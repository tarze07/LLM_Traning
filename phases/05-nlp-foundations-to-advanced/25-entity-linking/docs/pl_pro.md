# Łączenie i ujednoznacznianie encji (Entity Linking & Disambiguation)

> Model NER wykrył słowo „Paryż”. O ujednoznacznieniu decyduje proces łączenia encji: Paryż we Francji? Paris Hilton? Paryż w Teksasie? A może Parys (książę trojański)? Bez poprawnego powiązania (linkowania), graf wiedzy będzie pełen niespójności.

**Typ:** Projekt
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 24 (Rozstrzyganie koreferencji)
**Czas:** ~60 minut

## Problem

Analizujesz zdanie: „Jordan pokonał prasę”. Model NER poprawnie klasyfikuje słowo „Jordan” jako osobę (PERSON). Ale *o którego* Jordana chodzi?

- Michaela Jordana (koszykarza)?
- Michaela B. Jordana (aktora)?
- Michaela I. Jordana (profesora uczenia maszynowego na UC Berkeley – tak, ta zbieżność nazwisk prowadzi do realnych błędów w publikacjach naukowych)?
- Państwo Jordania?
- Imię Jordan?

Łączenie encji (EL – Entity Linking) polega na powiązaniu każdej wzmianki z unikalnym obiektem w bazie wiedzy (KB – Knowledge Base), takiej jak Wikidata, Wikipedia, DBpedia czy wewnętrzny rejestr Twojej domeny. Proces ten składa się z dwóch etapów:

1. **Generowanie kandydatów (Candidate generation):** Które wpisy w bazie wiedzy mogą odpowiadać wzmiance „Jordan”?
2. **Ujednoznacznianie (Disambiguation):** Który z wytypowanych kandydatów jest poprawny w kontekście analizowanego zdania?

Oba te kroki można zoptymalizować za pomocą algorytmów uczenia maszynowego i poddać ewaluacji. Architektura całego potoku pozostaje stabilna od lat – modyfikacji i ciągłemu ulepszaniu ulegają jedynie metody ujednoznaczniania.

## Koncepcja

![Potok łączenia encji: wzmianka → generowanie kandydatów → ujednoznacznianie](../assets/entity-linking.svg)

**Generowanie kandydatów.** Na podstawie formy tekstowej wzmianki („Jordan”) wyszukuje się kandydatów w tzw. indeksie aliasów (alias index). Słowniki aliasów oparte na Wikipedii pokrywają większość znanych obiektów: np. „JFK” → John F. Kennedy, Jacqueline Kennedy, lotnisko JFK, film „JFK”. Typowy indeks zwraca od 10 do 30 potencjalnych kandydatów dla jednej wzmianki.

**Ujednoznacznianie: trzy podejścia:**

1. **Prawdopodobieństwo a priori + podobieństwo kontekstu (np. Milne & Witten, 2008):** Metoda obliczająca iloczyn `P(entity | mention) × context-similarity(entity, text)`. Działa szybko, stabilnie i nie wymaga trenowania modeli.
2. **Metody oparte na osadzeniach (np. BLINK, REL):** Wzmianka wraz z kontekstem jest kodowana do postaci wektora. Podobnie koduje się opisy poszczególnych kandydatów. Wybierany jest kandydat o najwyższym podobieństwie cosinusowym. Standardowe podejście w latach 2020–2024.
3. **Podejście generatywne (np. GENRE, 2021; modele LLM, od 2023 roku):** Autoregresywne generowanie kanonicznej nazwy encji, token po tokenie. Zastosowanie dekodowania z ograniczeniami (constrained decoding, patrz lekcja 20) gwarantuje, że model wygeneruje wyłącznie istniejący identyfikator z bazy wiedzy.

**Modele end-to-end vs potoki (pipelines).** Nowoczesne modele (np. ELQ, BLINK, ExtEnD, GENRE) wykonują kroki NER, generowania kandydatów oraz ujednoznaczniania w ramach jednego przebiegu sieci. W systemach produkcyjnych wciąż dominują jednak potoki modułowe (pipeline), ze względu na łatwość wymiany i optymalizacji poszczególnych komponentów.

### Kluczowe metryki

- **Współczynnik pokrycia kandydatów (Mention Recall):** Odsetek przypadków, w których poprawny obiekt z bazy wiedzy znajduje się na wygenerowanej liście kandydatów. Stanowi to matematyczną górną granicę dokładności całego potoku.
- **Dokładność ujednoznaczniania (Disambiguation Accuracy / F1):** Odsetek przypadków, w których poprawny kandydat zostaje sklasyfikowany na 1. miejscu.

Należy zawsze monitorować obie te wartości. System osiągający 99% dokładności ujednoznaczniania przy 80% pokrycia kandydatów daje w efekcie zaledwie 80% skuteczności całego potoku.

## Zbuduj to

### Krok 1: Budowa indeksu aliasów na bazie przekierowań Wikipedii

```python
alias_to_entities = {
    "jordan": ["Q41421 (Michael Jordan)", "Q810 (Jordan, country)", "Q254110 (Michael B. Jordan)"],
    "paris":  ["Q90 (Paris, France)", "Q663094 (Paris, Texas)", "Q55411 (Paris Hilton)"],
    "apple":  ["Q312 (Apple Inc.)", "Q89 (apple, fruit)"],
}
```

Dane te można pobrać z publicznych zrzutów Wikidanych (Wikidata dumps) i zapisać w postaci indeksu odwróconego.

### Krok 2: Ujednoznacznianie na bazie podobieństwa kontekstu

```python
def disambiguate(mention, context, alias_index, entity_desc):
    candidates = alias_index.get(mention.lower(), [])
    if not candidates:
        return None, 0.0
    context_words = set(tokenize(context))
    best, best_score = None, -1
    for entity_id in candidates:
        desc_words = set(tokenize(entity_desc[entity_id]))
        union = len(context_words | desc_words)
        score = len(context_words & desc_words) / union if union else 0.0
        if score > best_score:
            best, best_score = entity_id, score
    return best, best_score
```

Wykorzystanie współczynnika Jaccarda ma charakter wyłącznie demonstracyjny. W rzeczywistych systemach zastępuje się je podobieństwem cosinusowym na bazie osadzeń (patrz krok 2 w pliku `code/main.py`).

### Krok 3: Ujednoznacznianie oparte na osadzeniach (styl BLINK)

```python
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_mention(text, mention_span):
    start, end = mention_span
    marked = f"{text[:start]} [MENTION] {text[start:end]} [/MENTION] {text[end:]}"
    return encoder.encode([marked], normalize_embeddings=True)[0]

def embed_entity(entity_id, description):
    return encoder.encode([f"{entity_id}: {description}"], normalize_embeddings=True)[0]
```

Podczas indeksowania bazy wiedzy obliczamy i zapisujemy osadzenia dla każdego obiektu (jednokrotnie). Przy zapytaniu użytkownika generujemy wektor dla wzmianki wraz z jej kontekstem, obliczamy iloczyn skalarny (dot product) z wektorami kandydatów i wybieramy obiekt o najwyższej wartości.

### Krok 4: Generatywne łączenie encji (przykład koncepcyjny)

Model GENRE (lub jego współczesne rozwinięcia) dekoduje tytuł docelowego artykułu w Wikipedii znak po znaku. Zastosowanie dekodowania z ograniczeniami (constrained decoding, patrz lekcja 20) gwarantuje generowanie wyłącznie poprawnych nazw jednostek.

```python
prompt = f"""Text: {text}
Mention: {mention}
List the best Wikipedia title for this mention.
Respond with JSON: {{"title": "..."}}"""
```

Połączenie tej metody z listą dozwolonych wartości (np. funkcją `choice` w bibliotece Outlines) to najprostszy i bardzo stabilny potok EL do wdrożenia w 2026 roku.

### Krok 5: Ewaluacja na zbiorze AIDA-CoNLL

Zbiór AIDA-CoNLL to standard referencyjny w zadaniach EL: zawiera 1393 artykuły agencji Reuters, 34 tysiące oznaczonych wzmianek oraz powiązania z Wikipedią. Podczas ewaluacji należy raportować precyzję dopasowania do bazy (`P@1`) oraz skuteczność identyfikacji przypadków spoza bazy (NIL detection).

## Typowe pułapki

- **Obsługa obiektów spoza bazy (NIL classification):** Wiele wzmianek w tekście nie posiada swoich odpowiedników w bazie wiedzy (np. nowe firmy, lokalne wydarzenia). System musi umieć zwrócić wartość `NIL` (brak dopasowania) zamiast przypisywać błędną encję na siłę. Skuteczność tej klasyfikacji należy mierzyć osobnym wskaźnikiem.
- **Błędy granic wzmianek:** Jeśli model NER w początkowej fazie błędnie wyznaczy granice frazy (np. oznaczy „Bank of America” jako po prostu „Bank”), pełność (Recall) modułu EL drastycznie spadnie.
- **Błąd popularności (Popularity bias):** Modele mają tendencję do faworyzowania najczęstszych obiektów w bazie. Przykładowo, wzmianka o profesorze „Michaelu I. Jordanie” w artykule o sztucznej inteligencji może zostać błędnie powiązana z koszykarzem Michaelem Jordanem.
- **Międzyjęzykowe łączenie encji (Cross-lingual EL):** Mapowanie wzmianek w języku np. polskim na encje w angielskiej bazie Wikidata. Wymaga to stosowania modeli wielojęzycznych lub dodatkowego kroku translacji.
- **Dezaktualizacja bazy wiedzy (KB staleness):** Nowo powstałe podmioty gospodarcze czy osoby publiczne nie będą widoczne w historycznym zrzucie Wikidanych. Produkcyjne wdrożenia wymagają wdrożenia mechanizmów regularnej aktualizacji bazy wiedzy.

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Język angielski (ogólne zastosowania, Wikipedia) | Moduły mGENRE lub REL |
| Wielojęzyczność (bazowana na Wikipedii) | mGENRE |
| Niski wolumen zapytań, integracja z LLM | GPT-4 / Claude z listą kandydatów i walidacją formatu JSON (Constrained JSON) |
| Bazy specjalistyczne (medycyna, prawo) | Dedykowany model BERT z wyszukiwaniem wektorowym w bazie wiedzy + dostrojenie na zbiorze walidacyjnym dostosowanym do dziedziny |
| Krytycznie niskie opóźnienia | Podejście Milne-Witten (klasyczne wyszukiwanie dopasowań) |
| Zaawansowane systemy badawcze SOTA | GENRE / ExtEnD / generatywne modele LLM-EL |

Standard wdrożeniowy w 2026 roku: potok w kolejności NER → koreferencja → łączenie encji (EL) na bazie klastrów. Wszystkie wzmianki z danego klastra są sprowadzane do jednej encji kanonicznej. Wyjściem systemu jest jeden unikalny identyfikator KB dla każdego obiektu w dokumencie, a nie dla każdej pojedynczej wzmianki.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-entity-linker.md`:

```markdown
---
name: entity-linker
description: Zaprojektuj potok łączenia encji: określ bazę wiedzy, generator kandydatów, moduł ujednoznaczniania oraz plan ewaluacji.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]
---

Na podstawie wymagań scenariusza użycia (dziedzinowa baza wiedzy, język, wolumen zapytań, limit opóźnień) wygeneruj:

1. Baza wiedzy: Wikidata / Wikipedia / rejestr wewnętrzny, data wersji oraz częstotliwość aktualizacji.
2. Generator kandydatów: Indeks aliasów, wyszukiwanie wektorowe lub metoda hybrydowa wraz z docelową wartością Recall@K.
3. Ujednoznaczniacz: Prawdopodobieństwo a priori + kontekst, oparte na osadzeniach, generatywne lub oparte na LLM.
4. Strategia obsługi NIL: Próg odcięcia wyniku, dodatkowy klasyfikator lub jawny kandydat NIL.
5. Plan ewaluacji: Wskaźnik Recall@30 dla kandydatów, dokładność TOP-1 oraz miara F1 dla detekcji NIL na wydzielonym zbiorze testowym.

Zawsze odrzucaj projekty potoków EL, które nie posiadają zdefiniowanego baseline dla pokrycia kandydatów (wyszukiwania nie da się poprawnie ocenić bez pewności, że poprawny obiekt znalazł się na liście kandydatów). Nigdy nie akceptuj rozwiązań opartych o LLM, które nie stosują dekodowania z ograniczeniami (constrained decoding) do poprawnych identyfikatorów z bazy wiedzy. Oznaczaj jako wymagające dostrojenia systemy, w których błąd popularności (popularity bias) fałszuje wyniki dla rzadkich encji o zbieżnych nazwach.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Zaimplementuj klasyczny algorytm ujednoznaczniania oparty na prawdopodobieństwie a priori oraz podobieństwie kontekstu z pliku `code/main.py` na 10 niejednoznacznych przykładach (np. Paryż, Jordan, Apple). Oznacz ręcznie poprawne encje i oblicz dokładność modelu.
2. **Poziom średni:** Przygotuj zbiór 50 niejednoznacznych wzmianek. Zaimplementuj ujednoznacznianie oparte na osadzeniach wektorowych i porównaj jego poprawność z prostym dopasowaniem kontekstu metodą Jaccarda.
3. **Poziom trudny:** Zbuduj własną bazę wiedzy zawierającą 1000 specjalistycznych encji (np. struktura produktów i pracowników Twojej firmy). Wdróż kompletny potok NER + EL i przeprowadź ewaluację precyzji i pełności (precision/recall) na próbie 100 zdań testowych.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Łączenie encji (Entity Linking) | Linkowanie do KB | Powiązanie wzmianki w tekście z konkretnym, unikalnym rekordem w bazie wiedzy. |
| Generowanie kandydatów (Candidate Generation) | Wybór kandydatów | Pobranie z bazy wiedzy krótkiej listy obiektów, które mogą odpowiadać danej wzmiance. |
| Ujednoznacznianie (Disambiguation) | Ujednoznacznianie | Wybór poprawnego obiektu spośród wytypowanych kandydatów na podstawie kontekstu. |
| Indeks aliasów (Alias Index) | Tabela aliasów | Struktura mapująca formę tekstową wzmianki na listę potencjalnych obiektów z bazy wiedzy. |
| Klasa NIL | Wynik NIL | Decyzja klasyfikatora wskazująca, że dany obiekt nie występuje w posiadanej bazie wiedzy. |
| Baza wiedzy (Knowledge Base) | KB | Baza danych referencyjnych encji, np. Wikidata, Wikipedia, DBpedia lub baza wewnętrzna. |
| Zbiór AIDA-CoNLL | Benchmark AIDA | Standardowy benchmark zawierający 1393 artykuły agencji Reuters z ręcznie oznaczonymi powiązaniami encji. |

## Literatura uzupełniająca

- [Milne & Witten (2008). An Effective, Low-Cost Approach to Word Sense Disambiguation](https://www.cs.waikato.ac.nz/~ihw/papers/08-DM-IHW-LearningToLinkWithWikipedia.pdf) — klasyczna metoda ujednoznaczniania w oparciu o Wikipedię.
- [Wu et al. (2020). Zero-shot Entity Linking with Dense Entity Retrieval (BLINK)](https://arxiv.org/abs/1911.03814) — architektura oparta na wyszukiwaniu gęstym.
- [De Cao et al. (2020). Autoregressive Entity Retrieval (GENRE)](https://arxiv.org/abs/2010.00904) — generatywne podejście do łączenia encji z dekodowaniem z ograniczeniami.
- [Hoffart et al. (2011). Robust Disambiguation of Named Entities in Text](https://www.aclweb.org/anthology/D11-1072.pdf) — publikacja wprowadzająca zbiór AIDA-CoNLL.
- [van Hulst et al. (2020). REL: An Entity Linker Standing on the Shoulders of Giants](https://arxiv.org/abs/2006.01969) — opis otwartoźródłowej biblioteki produkcyjnej.
