# Strategie podziału tekstu na fragmenty (Chunking Strategies) w systemach RAG

> Strategia podziału tekstu (chunking) wpływa na jakość wyszukiwania w stopniu nie mniejszym niż wybór samego modelu osadzeń (Vectara, NAACL 2025). Błędny podział sprawi, że nawet najlepszy reranker nie uratuje wyników wyszukiwania.

**Typ:** Projekt
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 14 (Wyszukiwanie informacji), Faza 5 · 22 (Modele osadzeń)
**Czas:** ~60 minut

## Problem

Wczytujesz 50-stronicową umowę do systemu RAG. Użytkownik pyta: „Jaki jest okres wypowiedzenia umowy?”. Moduł wyszukiwania (retriever) zwraca stronę tytułową dokumentu. Dlaczego? Ponieważ model osadzeń został przeszkolony na fragmentach o długości 512 tokenów, podczas gdy interesująca nas klauzula znajduje się na 20. stronie, została podzielona znakiem końca strony i nie zawiera lokalnych słów kluczowych łączących ją bezpośrednio z zapytaniem.

Rozwiązaniem tego problemu nie jest zakup droższego modelu osadzeń. Klucz tkwi w poprawnej strategii podziału tekstu (chunking). Jak duże powinny być fragmenty? Jaki zastosować margines zakładki (overlap)? Gdzie dokonać podziału? Jak zachować otaczający kontekst?

Wyniki benchmarków z początku 2026 roku przynoszą zaskakujące wnioski:

- **Badanie firmy Vectara (2026):** Rekursywny podział na fragmenty o rozmiarze 512 tokenów poprawia celność semantyczną wyszukiwania z 54% do 69%.
- **Analiza SPLADE + Mistral-8B na zbiorze Natural Questions:** Stosowanie marginesu zakładki (overlap) nie przynosi żadnych mierzalnych korzyści.
- **Klif kontekstowy (Context cliff):** Jakość odpowiedzi generowanych przez LLM gwałtownie spada, gdy przekazany kontekst przekracza około 2500 tokenów.

Powszechnie rekomendowane podejście (podział semantyczny, zakładka 20%, rozmiar 1000 tokenów) często okazuje się suboptymalne. W tej lekcji przeanalizujemy sześć głównych strategii podziału i wyjaśnimy, jak dopasować je do Twojego systemu.

## Koncepcja

![Wizualizacja sześciu strategii podziału tekstu na tym samym dokumencie](../assets/chunking.svg)

**Podział stałoznakowy (Fixed-size chunking).** Podział tekstu sztywno co `N` znaków lub tokenów. Najprostsze podejście (baseline). Powoduje jednak ucinanie zdań w połowie, co niszczy spójność semantyczną.

**Podział rekursywny (Recursive chunking).** Odpowiednik klasy `RecursiveCharacterTextSplitter` z biblioteki LangChain. Algorytm próbuje dzielić tekst kolejno na znakach nowego akapitu (`\n\n`), nowej linii (`\n`), kropkach ze spacją (`. `) oraz spacjach, starając się utrzymać pożądany rozmiar fragmentu. Zapewnia naturalne granice bloków tekstu; standard domyślny w 2026 roku.

**Podział semantyczny (Semantic chunking).** Tekst jest dzielony na zdania. Oblicza się podobieństwo cosinusowe osadzeń sąsiadujących zdań, a podział następuje w miejscach, w których podobieństwo spada poniżej zadanego progu. Świetnie zachowuje spójność tematyczną, lecz jest kosztowny obliczeniowo i bywa niestabilny (generuje zbyt krótkie, np. 40-tokenowe fragmenty, które są trudne do poprawnego wyszukania).

**Podział zdaniowy (Sentence-based chunking).** Podział tekstu ściśle na granicach zdań (pojedyncze zdania lub ruchome okno o szerokości `N` zdań). Zapewnia jakość zbliżoną do podziału semantycznego przy niemal zerowym koszcie obliczeniowym.

**Struktura rodzic-dziecko (Parent-document retrieval).** Przechowywanie małych fragmentów („dzieci”) na potrzeby wyszukiwania wektorowego oraz większych bloków tekstu („rodziców”) jako kontekstu przekazywanego do modelu LLM. Wyszukiwanie odbywa się na bazie wektorów dzieci, lecz do generowania odpowiedzi pobierana jest pełna treść rodzica. Rozwiązanie bardzo stabilne i odporne na błędy lokalne.

**Późne fragmentowanie (Late chunking).** Cały dokument jest najpierw przepuszczany przez model osadzeń (na poziomie pojedynczych tokenów), a dopiero wygenerowane wektory tokenów są agregowane w wektory docelowych fragmentów. Pozwala to zachować globalny kontekst dokumentu w każdym wektorze fragmentu. Wymaga modeli obsługujących długi kontekst (np. BGE-M3, Jina v3) i zwiększa koszty obliczeniowe.

**Wyszukiwanie kontekstowe (Contextual Retrieval – metoda Anthropic).** Do każdego fragmentu dołącza się krótkie (generowane przez model LLM) podsumowanie umiejscawiające go w kontekście całego dokumentu (np. „Ten fragment jest częścią rozdziału 3.2 opisującego warunki wypowiedzenia umowy…”). Pozwala to poprawić dokładność wyszukiwania o 35–50% kosztem wyższego kosztu i dłuższego czasu indeksowania.

### Dopasowanie rozmiaru fragmentu do typu zapytania (Query-to-Chunk Matching)

| Typ zapytania | Rozmiar fragmentu |
|------------|-----------|
| Pytania o proste fakty / konkretne szczegóły („Kto jest CEO?”) | 256-512 tokenów |
| Analiza porównawcza / Wnioskowanie wielokrokowe (multi-hop) | 512-1024 tokenów |
| Synteza i rozumienie całych rozdziałów/sekcji | 1024-2048 tokenów |

Według wytycznych benchmarku firmy NVIDIA, idealny fragment musi być na tyle duży, aby zawierał pełną odpowiedź wraz z niezbędnym kontekstem lokalnym, a jednocześnie na tyle mały, aby w TOP-K wyników wyszukiwania model LLM otrzymywał esencję informacji, a nie zbędny szum z otoczenia.

## Zbuduj to

### Krok 1: Podział stałoznakowy i rekursywny

```python
def chunk_fixed(text, size=512, overlap=0):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]

def chunk_recursive(text, size=512, seps=("\n\n", "\n", ". ", " ")):
    if len(text) <= size:
        return [text]
    for sep in seps:
        if sep not in text:
            continue
        parts = text.split(sep)
        chunks = []
        buf = ""
        for p in parts:
            if len(p) > size:
                if buf:
                    chunks.append(buf)
                    buf = ""
                chunks.extend(chunk_recursive(p, size=size, seps=seps[1:] or (" ",)))
                continue
            candidate = buf + sep + p if buf else p
            if len(candidate) <= size:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                buf = p
        if buf:
            chunks.append(buf)
        return [c for c in chunks if c.strip()]
    return chunk_fixed(text, size)
```

### Krok 2: Podział semantyczny

```python
def chunk_semantic(text, encoder, threshold=0.6, min_chars=200, max_chars=2048):
    sentences = split_sentences(text)
    if not sentences:
        return []
    embs = encoder.encode(sentences, normalize_embeddings=True)
    chunks = [[sentences[0]]]
    for i in range(1, len(sentences)):
        sim = float(embs[i] @ embs[i - 1])
        current_len = sum(len(s) for s in chunks[-1])
        if sim < threshold and current_len >= min_chars:
            chunks.append([sentences[i]])
        else:
            chunks[-1].append(sentences[i])

    result = []
    for group in chunks:
        text_group = " ".join(group)
        if len(text_group) > max_chars:
            result.extend(chunk_recursive(text_group, size=max_chars))
        else:
            result.append(text_group)
    return result
```

Parametr progu podobieństwa (`threshold`) należy dostosować empirycznie. Zbyt wysoka wartość wygeneruje mnóstwo małych fragmentów, zbyt niska – połączy tekst w jeden ogromny blok.

### Krok 3: Wyszukiwanie w strukturze rodzic-dziecko (Parent-document)

```python
def chunk_parent_child(text, parent_size=2048, child_size=256):
    parents = chunk_recursive(text, size=parent_size)
    mapping = []
    for p_idx, parent in enumerate(parents):
        children = chunk_recursive(parent, size=child_size)
        for child in children:
            mapping.append({"child": child, "parent_idx": p_idx, "parent": parent})
    return mapping

def retrieve_parent(child_query, mapping, encoder, top_k=3):
    child_embs = encoder.encode([m["child"] for m in mapping], normalize_embeddings=True)
    q_emb = encoder.encode([child_query], normalize_embeddings=True)[0]
    scores = child_embs @ q_emb
    top = np.argsort(-scores)[:top_k]
    seen, parents = set(), []
    for i in top:
        if mapping[i]["parent_idx"] not in seen:
            parents.append(mapping[i]["parent"])
            seen.add(mapping[i]["parent_idx"])
    return parents
```

Wskazówka: deduplikacja rodziców. Ponieważ wiele fragmentów-dzieci może należeć do tego samego dokumentu-rodzica, w kodzie wyszukiwania należy zastosować mechanizm deduplikacji, aby uniknąć przekazywania tej samej treści wielokrotnie.

### Krok 4: Wyszukiwanie kontekstowe (szablon Anthropic)

```python
def contextualize_chunks(document, chunks, llm):
    context_prompts = [
        f"""<document>{document}</document>
Here is the chunk to situate: <chunk>{c}</chunk>
Write 50-100 words placing this chunk in the document's context."""
        for c in chunks
    ]
    contexts = llm.batch(context_prompts)
    return [f"{ctx}\n\n{c}" for ctx, c in zip(contexts, chunks)]
```

Kontekstualizowane fragmenty są indeksowane w bazie. Podczas wyszukiwania model osadzeń korzysta z dodatkowej informacji semantycznej zawartej w nagłówku kontekstowym.

### Krok 5: Ewaluacja jakości podziału

```python
def recall_at_k(queries, corpus_chunks, encoder, k=5):
    chunk_embs = encoder.encode(corpus_chunks, normalize_embeddings=True)
    hits = 0
    for q_text, gold_idxs in queries:
        q_emb = encoder.encode([q_text], normalize_embeddings=True)[0]
        top = np.argsort(-(chunk_embs @ q_emb))[:k]
        if any(i in gold_idxs for i in top):
            hits += 1
    return hits / len(queries)
```

Zawsze weryfikuj wyniki empirycznie. Rozwiązanie optymalne dla Twojego korpusu danych może różnić się od ogólnych zaleceń.

## Typowe pułapki

- **Ewaluacja wyłącznie na bazie prostych pytań (factoids):** Ocena jakości podziału tylko na prostych zapytaniach jednokrokowych może prowadzić do mylnych wniosków. Zapytania wielokrokowe (multi-hop) wymagają zupełnie innych rozmiarów fragmentów. Zbiór testowy powinien być podzielony (warstwowany) pod kątem stopnia skomplikowania pytań.
- **Podział semantyczny bez limitu minimalnego rozmiaru:** Może generować bardzo krótkie fragmenty (np. jednowyrazowe lub kilkutokenowe), które nie niosą wystarczającej wartości semantycznej do poprawnego wyszukania. Zawsze stosuj próg minimalnej liczby tokenów (`min_tokens`).
- **Bezrefleksyjne stosowanie marginesu zakładki (overlap):** Badania pokazują, że stosowanie zakładek często nie przekłada się na lepsze wyniki wyszukiwania, a generuje dodatkowy koszt pamięciowy (podwaja rozmiar indeksu). Należy to zweryfikować pomiarami.
- **Brak kontroli wartości skrajnych (min/max):** Fragmenty o rozmiarze 5 tokenów lub 5000 tokenów zaburzają działanie algorytmu wyszukiwania wektorowego. Zawsze stosuj sztywne granice rozmiaru.
- **Fragmenty zawierające fragmenty różnych dokumentów:** Nigdy nie dopuszczaj do sytuacji, w której jeden fragment łączy w sobie końcówkę jednego dokumentu i początek innego. Podział must być realizowany w granicach pojedynczych dokumentów.

## Rekomendowane podejścia

| Sytuacja | Strategia |
|----------|----------|
| Pierwsza wersja wdrożenia (unknown corpus) | Podział rekursywny, 512 tokenów, brak zakładki (overlap=0) |
| Pytania o proste fakty (Factoid QA) | Podział rekursywny, 256-512 tokenów |
| Złożone wnioskowanie (multi-hop) | Podział rekursywny (512-1024 tokenów) + struktura rodzic-dziecko |
| Dokumentacja o gęstej strukturze (umowy, specyfikacje) | Late chunking lub Contextual Retrieval (Anthropic) |
| Dane konwersacyjne (dialogi, czaty) | Podział na tury konwersacyjne + metadane o mówcy |
| Bardzo krótkie dokumenty (tweety, recenzje) | Jeden dokument = jeden fragment |

Sprawdzony punkt startowy: zacznij od podziału rekursywnego na bloki po 512 tokenów. Zmierz wartość Recall@5 na zbiorze walidacyjnym z 50 zapytaniami i optymalizuj parametry w oparciu o uzyskane wyniki.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-chunker.md`:

```markdown
---
name: chunker
description: Wybierz strategię podziału tekstu na fragmenty, rozmiar bloku oraz margines zakładki (overlap) dla podanego korpusu i rozkładu zapytań.
version: 1.0.0
phase: 5
lesson: 23
tags: [nlp, rag, chunking]
---

Na podstawie charakterystyki korpusu (rodzaje dokumentów, średnia długość, dziedzina) oraz rozkładu zapytań (pytania o fakty / wnioskowanie / multi-hop) wygeneruj:

1. Strategia: Rekursywny, zdaniowy, semantyczny, rodzic-dziecko, late chunking lub wyszukiwanie kontekstowe (Contextual Retrieval) wraz z uzasadnieniem.
2. Rozmiar fragmentu: Liczba tokenów wraz z uzasadnieniem powiązanym z typem zapytań.
3. Margines zakładki (overlap): Domyślnie 0; podaj uzasadnienie w przypadku wyboru wartości wyższej niż 0.
4. Warunki skrajne (min/max): Wdrożenie zabezpieczeń `min_tokens` oraz `max_tokens`.
5. Plan ewaluacji: Wskaźnik Recall@5 na warstwowym zbiorze testowym składającym się z 50 zapytań (pytania o fakty, wnioskowanie, multi-hop).

Nigdy nie akceptuj strategii podziału tekstu bez zaimplementowanej weryfikacji wartości skrajnych (min/max). Zawsze odrzucaj propozycje stosowania zakładek powyżej 20% bez wyników testów wykazujących ich skuteczność. Oznaczaj rekomendacje podziału semantycznego, które nie posiadają zdefiniowanego dolnego limitu tokenów (min-token floor).
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Podziel 20-stronicowy dokument tekstowy za pomocą trzech metod: podział stałoznakowy (512, overlap=0), podział rekursywny (512, overlap=0) oraz podział rekursywny z zakładką (512, overlap=100). Porównaj liczbę wygenerowanych fragmentów oraz jakość podziału na granicach bloków.
2. **Poziom średni:** Przygotuj zbiór walidacyjny składający się z 30 zapytań do 5 dokumentów. Zmierz wartość Recall@5 dla podziału rekursywnego, semantycznego oraz struktury rodzic-dziecko. Porównaj wyniki z powszechnymi zaleceniami.
3. **Poziom trudny:** Zaimplementuj metodę wyszukiwania kontekstowego (Contextual Retrieval). Zmierz różnicę w metryce MRR w odniesieniu do bazowego podziału rekursywnego. Porównaj koszt indeksowania (wywołania modelu LLM) z rzeczywistym przyrostem jakości wyszukiwania.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Fragment (Chunk) | Kawałek dokumentu | Podzielona część dokumentu źródłowego podlegająca indeksowaniu wektorowemu i wyszukiwaniu. |
| Margines zakładki (Overlap) | Zakładka | Liczba tokenów współdzielonych przez sąsiednie fragmenty; badania z 2026 r. wskazują, że często nie przynosi to korzyści. |
| Podział semantyczny (Semantic chunking) | Inteligentne kawałkowanie | Dynamiczny podział w miejscach spadku podobieństwa semantycznego osadzeń kolejnych zdań. |
| Struktura rodzic-dziecko (Parent-document) | Wyszukiwanie dwupoziomowe | Wyszukiwanie oparte na małych fragmentach (dzieciach) i zwracanie powiązanych większych bloków tekstu (rodziców). |
| Późne fragmentowanie (Late chunking) | Kawałek po osadzeniu | Obliczanie wektorów osadzeń na poziomie tokenów dla całego dokumentu, a następnie agregowanie ich do wektorów fragmentów. |
| Wyszukiwanie kontekstowe (Contextual Retrieval) | Metoda Anthropic | Doklejanie generowanego przez model LLM kontekstu globalnego do każdego fragmentu przed indeksowaniem. |
| Klif kontekstowy (Context cliff) | Ściana kontekstu | Spadek sprawności generowania odpowiedzi przez model LLM, gdy przekazany kontekst przekracza próg ok. 2500 tokenów. |

## Literatura uzupełniająca

- [Oficjalna dokumentacja LangChain – RecursiveCharacterTextSplitter](https://python.langchain.com/docs/how_to/recursive_text_splitter/) — standard produkcyjny podziału tekstu.
- [Vectara (2024). How Chunking Configuration Affects Retrieval Performance](https://arxiv.org/abs/2410.13070) — badanie wykazujące wpływ podziału tekstu na jakość wyszukiwania.
- [Jina AI (2024). Late Chunking in Long-Context Embedding Models](https://jina.ai/news/late-chunking-in-long-context-embedding-models/) — wprowadzenie do techniki późnego fragmentowania.
- [Anthropic (2024). Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) — publikacja prezentująca metodę poprawy jakości wyszukiwania poprzez nagłówki kontekstowe.
- [NVIDIA (2026). RAG Chunking Strategies Benchmark Guide](https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/) — kompleksowy przewodnik po doborze rozmiaru fragmentów w zależności od typu zadań.
