# Strategie dzielenia dla RAG

> Konfiguracja fragmentacji wpływa na jakość wyszukiwania w takim samym stopniu, jak wybór modelu osadzania (Vectara NAACL 2025). Jeśli pomylisz się w dzieleniu, żadna zmiana rankingu Cię nie uratuje.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 14 (wyszukiwanie informacji), faza 5 · 22 (Osadzanie modeli)
**Czas:** ~60 minut

## Problem

Umieszczasz 50-stronicową umowę w systemie RAG. Użytkownik pyta: „Jaka jest klauzula wypowiedzenia?” Retriever zwraca stronę tytułową. Dlaczego? Ponieważ model został przeszkolony na fragmentach zawierających 512 tokenów, a klauzula zakończenia znajduje się na 20 stronach, podzielona na podział strony, bez lokalnych słów kluczowych wiążących ją z zapytaniem.

Rozwiązaniem nie jest „kup lepszy model do osadzania”. Poprawka polega na fragmentowaniu. Jak duży? Zachodzić na siebie? Gdzie się podzielić? Z otaczającym kontekstem?

Testy porównawcze z lutego 2026 r. wykazały zaskakujące wyniki:

- Badanie Vectary z 2026 r.: rekursywne fragmentowanie 512 tokenów przewyższa dokładność semantyczną 69% → 54%.
- SPLADE + Mistral-8B w kwestiach naturalnych: nakładanie się zapewnia zerową wymierną korzyść.
- Klif kontekstowy: jakość odpowiedzi gwałtownie spada w okolicach 2500 tokenów kontekstu.

„Oczywista” odpowiedź (podział semantyczny, nakładanie się 20%, 1000 tokenów) jest często błędna. Ta lekcja rozwija intuicję dotyczącą sześciu strategii i podpowiada, kiedy po którą sięgnąć.

## Koncepcja

![Sześć strategii dzielenia wizualizowanych w jednym fragmencie](../assets/chunking.svg)

**Naprawiono fragmentację.** Podziel co N znaków lub tokenów. Najprostsza podstawa. Przerywa w połowie zdania. Dobra kompresja, zła spójność.

**Rekurencyjne.** `RecursiveCharacterTextSplitter` LangChaina. Spróbuj najpierw podzielić na `\n\n`, następnie `\n`, następnie `.`, a następnie spację. Wraca czysto. Wartość domyślna z 2026 r.

**Semantyczne.** Umieść każde zdanie. Oblicz cosinus podobieństwa między sąsiednimi zdaniami. Podziel, gdy podobieństwo spadnie poniżej progu. Zachowuje spójność tematu. Wolniej; czasami tworzy maleńkie fragmenty zawierające 40 żetonów, które utrudniają odzyskanie.

**Zdanie.** Podzielone na granicach zdań. Jedno zdanie na fragment lub okno N zdań. Dopasowuje fragmentację semantyczną do ~ 5 tys. tokenów za ułamek ceny.

**Dokument-rodzic.** Przechowuj małe fragmenty podrzędne w celu odzyskania *i* większe fragmenty nadrzędne w celu uzyskania kontekstu. Odzyskanie przez dziecko; powrót rodzica. Degraduje z wdziękiem: złe kawałki dziecka nadal zwracają rozsądnych rodziców.

**Późne fragmentowanie (2024 r.).** Najpierw osadź cały dokument na poziomie tokenu, a następnie połącz osadzanie tokenów w osadzanie fragmentów. Zachowuje kontekst między fragmentami. Współpracuje z osadzaczami o długim kontekście (BGE-M3, Jina v3). Wyższe obliczenia.

**Wyszukiwanie kontekstowe (Anthropic, 2024).** Dołącz do każdego fragmentu wygenerowane przez LLM podsumowanie jego pozycji w dokumencie („Ten fragment stanowi część 3.2 klauzul dotyczących rozwiązania umowy…”). Poprawa wyszukiwania o 35–50% w porównaniu z własnym benchmarkiem Anthropic. Drogie w indeksowaniu.

### Zasada, która pokonuje każdą wartość domyślną

Dopasuj rozmiar porcji do typu zapytania:

| Typ zapytania | Rozmiar kawałka |
|------------|-----------|
| Factoid („Jak nazywa się dyrektor generalny?”) | 256-512 tokenów |
| Analityczne / multi-hop | 512-1024 tokenów |
| Rozumienie całej sekcji | 1024-2048 tokenów |

Benchmark firmy NVIDIA na rok 2026. Kawałek powinien być wystarczająco duży, aby pomieścić odpowiedź plus kontekst lokalny, na tyle mały, aby górne K aportera skupiało się na odpowiedzi, a nie na szumie kontekstu.

## Zbuduj to

### Krok 1: fragmentacja stała i rekurencyjna

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

### Krok 2: fragmentacja semantyczna

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

Dostrój `threshold` w swojej domenie. Za wysokie → fragmenty. Za niski → jeden wielki kawał.

### Krok 3: dokument nadrzędny

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

Kluczowy spostrzeżenie: oszukani rodzice. Wiele dzieci może być przypisanych do tego samego rodzica; zwrócenie wszystkiego zmarnowałoby kontekst.

### Krok 4: wyszukiwanie kontekstowe (wzorzec antropiczny)

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

Indeksuj kontekstowe fragmenty. W czasie zapytania pobieranie korzysta z dodatkowego sygnału otoczenia.

### Krok 5: oceń

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

Zawsze porównuj. „Najlepsza” strategia dla Twojego korpusu może nie pasować do żadnego wpisu na blogu.

## Pułapki

- **Porcjowanie oceniane jest tylko w przypadku zapytań o faktoidy.** Zapytania z wieloma przeskokami ujawniają bardzo różnych zwycięzców. Użyj zestawu eval ze stratyfikacją typu zapytania.
- **Podział semantyczny bez minimalnego rozmiaru.** Tworzy 40-tokenowe fragmenty, które utrudniają odzyskanie. Zawsze egzekwuj `min_tokens`.
- **Nakładanie się jako kult cargo.** Badania z 2026 r. wykazały, że nakładanie się często zapewnia zerowe korzyści i podwaja koszt indeksu. Mierz, nie zakładaj.
- **Brak wymuszania minimalnej/maksymalnej wartości.** Kawałki 5 tokenów lub 5000 tokenów przerywają pobieranie. Zacisk.
- **Część dokumentów między dokumentami.** Nigdy nie pozwalaj, aby porcja obejmowała dwa dokumenty. Zawsze dziel się na poszczególne dokumenty, a następnie łącz je.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Strategia |
|----------|----------|
| Pierwsza kompilacja, nieznany korpus | Rekurencyjne, 512 tokenów, bez nakładania się |
| Kontrola jakości faktów | Rekurencyjne, 256-512 tokenów |
| Analityczne / multi-hop | Rekurencyjne, 512-1024 tokenów + dokument nadrzędny |
| Ciężkie odniesienia (umowy, dokumenty) | Późne fragmentowanie lub pobieranie kontekstowe |
| Korpus konwersacyjny / dialogowy | Fragmenty poziomu kolei + metadane głośników |
| Krótkie wypowiedzi (tweety, recenzje) | Jeden dokument = jedna porcja |

Zacznij od rekurencyjnego 512. Zmierz przywołanie @ 5 w zestawie ewaluacyjnym składającym się z 50 zapytań. Dostrój stamtąd.

## Wyślij to

Zapisz jako `outputs/skill-chunker.md`:

```markdown
---
name: chunker
description: Pick a chunking strategy, size, and overlap for a given corpus and query distribution.
version: 1.0.0
phase: 5
lesson: 23
tags: [nlp, rag, chunking]
---

Given a corpus (document types, avg length, domain) and query distribution (factoid / analytical / multi-hop), output:

1. Strategy. Recursive / sentence / semantic / parent-document / late / contextual. Reason.
2. Chunk size. Token count. Reason tied to query type.
3. Overlap. Default 0; justify if >0.
4. Min/max enforcement. `min_tokens`, `max_tokens` guards.
5. Evaluation plan. Recall@5 on 50-query stratified eval set (factoid, analytical, multi-hop).

Refuse any chunking strategy without min/max chunk size enforcement. Refuse overlap above 20% without an ablation showing it helps. Flag semantic chunking recommendations without a min-token floor.
```

## Ćwiczenia

1. **Łatwo.** Podziel jeden 20-stronicowy dokument na elementy stałe (512, 0), rekurencyjne (512, 0) i rekurencyjne (512, 100). Porównaj liczbę porcji i jakość granic.
2. **Średni.** Zbuduj zestaw ewaluacyjny składający się z 30 zapytań w 5 dokumentach. Zmierz przypomnienie @ 5 dla dokumentu rekurencyjnego, semantycznego i nadrzędnego. Które wygrywa? Czy zgadza się z wpisami na blogu?
3. **Trudne.** Zaimplementuj pobieranie kontekstowe. Zmierz poprawę MRR w porównaniu z bazową metodą rekurencyjną. Raportuj koszt indeksu (wywołania LLM) w porównaniu ze wzrostem dokładności.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Kawałek | Kawałek dokumentu | Jednostka dokumentu podrzędnego, która jest osadzana, indeksowana i pobierana. |
| Nakładanie się | Margines bezpieczeństwa | N żetonów współdzielonych pomiędzy sąsiednimi fragmentami; często bezużyteczne w benchmarkach na rok 2026. |
| Fragmentacja semantyczna | Inteligentne kawałkowanie | Podziel, gdy podobieństwo sąsiedniego zdania zawierającego osadzanie spada. |
| Dokument-rodzic | Wyszukiwanie dwupoziomowe | Odzyskaj małe dzieci, zwróć większych rodziców. |
| Późne kawałkowanie | Kawałek po osadzeniu | Osadź pełny dokument na poziomie tokena, połącz go z wektorami fragmentów. |
| Pobieranie kontekstowe | Sztuczka Anthropica | Podsumowanie wygenerowane przez LLM dołączane do każdej porcji przed indeksowaniem. |
| Klif kontekstowy | Ściana za 2500 żetonów | Spadek jakości zaobserwowany wokół 2,5 tys. tokenów kontekstu w RAG (styczeń 2026 r.). |

## Dalsze czytanie

- [Tak i in. / LangChain — dokumentacja dotycząca rekurencyjnego podziału znaków](https://python.langchain.com/docs/how_to/recursive_text_splitter/) — wartość domyślna w środowisku produkcyjnym.
- [Vectara (2024, NAACL 2025). Analiza konfiguracji fragmentacji](https://arxiv.org/abs/2410.13070) — podział na porcje ma takie samo znaczenie jak wybór osadzania.
– [Jina AI — Late Chunking in Long-Context Embedding Models (2024)](https://jina.ai/news/late-chunking-in-long-context-embedding-models/) — artykuł dotyczący późnego fragmentowania.
— [Anthropic — pobieranie kontekstowe](https://www.anthropic.com/news/contextual-retrieval) — poprawa wyszukiwania o 35–50% dzięki przedrostkom kontekstu generowanym przez LLM.
- [benchmark wielkości porcji NVIDIA 2026 — podsumowanie Premai](https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/) — wielkość porcji według typu zapytania.