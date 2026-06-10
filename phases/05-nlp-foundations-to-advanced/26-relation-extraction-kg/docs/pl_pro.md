# Ekstrakcja relacji i budowa grafów wiedzy (Relation Extraction & Knowledge Graphs)

> Model NER wykrywa encje. Łączenie encji (Entity Linking) kotwiczy je w bazie wiedzy. Ekstrakcja relacji pozwala zidentyfikować krawędzie (relacje) między nimi. Graf wiedzy to sieć węzłów i krawędzi wraz z informacją o ich pochodzeniu (provenance).

**Typ:** Projekt
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 25 (Łączenie encji)
**Czas:** ~60 minut

## Problem

Analizujesz zdanie: „Tim Cook został dyrektorem generalnym Apple w 2011 roku”. Na tej podstawie wyodrębnić można cztery fakty:

- `(Tim Cook, role, CEO)`
- `(Tim Cook, employer, Apple)`
- `(Tim Cook, start_date, 2011)`
- `(Apple, type, Organization)`

Ekstrakcja relacji (RE – Relation Extraction) pozwala przekształcić tekst wolny w ustrukturyzowane trójki postaci `(podmiot, relacja, dopełnienie)` – ang. `(subject, relation, object)`. Agregacja tych danych z całego korpusu tekstów pozwala zbudować graf wiedzy (Knowledge Graph). Taki graf stanowi solidny fundament semantyczny do wnioskowania w systemach RAG (GraphRAG), zaawansowanej analityki czy audytów zgodności.

Wyzwanie: modele LLM bardzo chętnie wyodrębniają relacje – niestety często zbyt chętnie. Generują zhalucynowane trójki, które nie mają żadnego potwierdzenia w tekście źródłowym. Bez jednoznacznej informacji o pochodzeniu (provenance) nie jesteśmy w stanie odróżnić faktów od wiarygodnie brzmiącej konfabulacji. Sprawdzonym standardem są potoki typu „kotwicz i weryfikuj” (anchor-and-verify) realizowane w architekturze AEVS.

## Koncepcja

![Tekst → trójki → graf wiedzy](../assets/relation-extraction.svg)

**Struktura trójki (Triple format).** `(subject_entity, relation_type, object_entity)`. Relacje mogą należeć do zamkniętej ontologii (np. właściwości bazy Wikidata, FIBO, UMLS) lub do zbioru otwartego (podejście OpenIE, gdzie relacją może być dowolna fraza).

**Trzy podejścia do ekstrakcji relacji:**

1. **Metody regułowe i szablonowe (Pattern-based).** Np. szablony Hearsta: „X, takie jak Y” → `(Y, isA, X)` połączone z ręcznie zdefiniowanymi wyrażeniami regularnymi. Podejście podatne na zmiany zapisu (kruche), lecz bardzo precyzyjne i łatwo interpretowalne.
2. **Klasyfikator nadzorowany (Supervised classifier).** Dla dwóch wykrytych w zdaniu encji model klasyfikuje relację między nimi ze zdefiniowanego zbioru. Modele tego typu trenowane są na zbiorach TACRED, ACE, KBP. Standard dominujący w latach 2015–2022.
3. **Generatywne modele LLM.** Model jest instruowany, aby bezpośrednio wygenerował trójki faktów. Działa świetnie bez wcześniejszego uczenia, lecz wymaga wdrożenia weryfikacji pochodzenia (provenance), aby zapobiec halucynacjom.

**Metodologia AEVS (Anchor-Extraction-Verification-Supplement).** Sprawdzony schemat ograniczania halucynacji:

- **Kotwiczenie (Anchor):** Identyfikacja dokładnych pozycji (indeksów znakowych) encji oraz relacji w tekście źródłowym.
- **Ekstrakcja (Extraction):** Generowanie trójek bezpośrednio powiązanych z zakotwiczonymi fragmentami tekstu.
- **Weryfikacja (Verification):** Walidacja każdej wygenerowanej trójki z tekstem źródłowym; odrzucenie relacji bez pokrycia w faktach.
- **Uzupełnianie (Supplement):** Dodatkowy przebieg weryfikujący, czy żadna z zakotwiczonych encji nie została pominięta.

Liczba halucynacji drastycznie spada. Metoda ta wymaga większych nakładów obliczeniowych, lecz gwarantuje pełną kontrolę nad procesem.

**Porównanie ontologii otwartych i zamkniętych:**

- **Ontologia zamknięta.** Stały, z góry zdefiniowany zbiór relacji (np. ponad 11 000 relacji w bazie Wikidata). Przewidywalna i łatwa do odpytywania (np. w SPARQL), lecz trudna w zaprojektowaniu i rozbudowie.
- **Ontologia otwarta (Open IE).** Dowolna fraza czasownikowa może stać się relacją. Zapewnia wysoką pełność (Recall), lecz charakteryzuje się niską precyzją i tworzy niespójny, trudny do odpytywania graf.

Produkcyjne grafy wiedzy (KG) zazwyczaj łączą oba podejścia: Open IE służy do wyszukiwania nowych relacji, które następnie są kanonizowane do zamkniętej ontologii przed scaleniem z głównym grafem.

## Zbuduj to

### Krok 1: Ekstrakcja relacji w oparciu na szablonach (Hearst Patterns)

```python
PATTERNS = [
    (r"(?P<s>[A-Z]\w+) (?:is|was) (?:a|an|the) (?P<o>[A-Z]?\w+)", "isA"),
    (r"(?P<s>[A-Z]\w+) (?:is|was) born in (?P<o>\w+)", "bornIn"),
    (r"(?P<s>[A-Z]\w+) works? (?:at|for) (?P<o>[A-Z]\w+)", "worksAt"),
    (r"(?P<s>[A-Z]\w+) founded (?P<o>[A-Z]\w+)", "founded"),
]
```

W pliku `code/main.py` znajdziesz kompletną implementację prostego ekstraktora. Szablony Hearsta wciąż są chętnie stosowane w potokach dziedzinowych ze względu na ich determinizm i łatwość debugowania.

### Krok 2: Nadzorowana klasyfikacja relacji (model REBEL)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tok = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSequenceClassification.from_pretrained("Babelscape/rebel-large")

text = "Tim Cook was born in Alabama. He later became CEO of Apple."
encoded = tok(text, return_tensors="pt", truncation=True)
output = model.generate(**encoded, max_length=200)
triples = tok.batch_decode(output, skip_special_tokens=False)
```

Model REBEL to ekstraktor typu seq2seq: przyjmuje na wejściu tekst, a generuje trójki faktów zmapowane bezpośrednio na identyfikatory właściwości bazy Wikidata. Model został dostrojony z wykorzystaniem techniki zdalnego nadzoru (distant supervision) i stanowi świetny otwartoźródłowy baseline.

### Krok 3: Ekstrakcja relacji za pomocą LLM z wdrożonym kotwiczeniem

```python
prompt = f"""Extract (subject, relation, object) triples from the text.
For each triple, include the exact character span in the source text.

Text: {text}

Output JSON:
[{{"subject": {{"text": "...", "span": [start, end]}},
   "relation": "...",
   "object": {{"text": "...", "span": [start, end]}}}}, ...]

Only include triples fully supported by the text. No inference beyond what is stated.
"""
```

Weryfikujemy każdy wygenerowany indeks znakowy z tekstem źródłowym i odrzucamy trójki, dla których fragment tekstu `text[start:end]` nie jest identyczny z wyekstrahowaną encją. To uproszczona wersja etapu weryfikacji (Verification) w AEVS.

### Krok 4: Kanonizacja relacji do zamkniętej ontologii

```python
RELATION_MAP = {
    "is the CEO of": "P169",       # "chief executive officer"
    "was born in":   "P19",         # "place of birth"
    "founded":        "P112",       # "founded by"
    "works at":       "P108",       # "employer"
}

def canonicalize(relation):
    rel_low = relation.lower().strip()
    if rel_low in RELATION_MAP:
        return RELATION_MAP[rel_low]
    return None   # odrzucenie relacji spoza ontologii lub przekazanie do ręcznej weryfikacji
```

Proces kanonizacji i mapowania relacji stanowi często od 60% do 80% całego nakładu pracy inżynierskiej przy budowie grafów. Należy to uwzględnić w harmonogramie projektu.

### Krok 5: Budowa prostego grafu i odpytywanie

```python
triples = extract(text)
graph = {}
for s, r, o in triples:
    graph.setdefault(s, []).append((r, o))

def neighbors(node, relation=None):
    return [(r, o) for r, o in graph.get(node, []) if relation is None or r == relation]

print(neighbors("Tim Cook", relation="P108"))    # -> [(P108, Apple)]
```

To elementarny budulec systemów typu GraphRAG. Produkcyjne wdrożenia skaluje się za pomocą baz RDF (np. GraphDB, Blazegraph, Virtuoso), grafowych baz danych (np. Neo4j) lub baz wektorowych ze wsparciem dla struktur grafowych.

## Typowe pułapki

- **Koreferencja przed ekstrakcją relacji:** W zdaniu „On założył Apple” moduł RE musi wiedzieć, do kogo odnosi się zaimek „On”. Przed ekstrakcją relacji należy bezwzględnie wdrożyć rozstrzyganie koreferencji (patrz lekcja 24).
- **Kanonizacja encji:** Określenia „Apple Inc.” oraz „Apple” muszą wskazywać ten sam węzeł w grafie. Przed ekstrakcją relacji należy uruchomić łączenie encji (patrz lekcja 25).
- **Zhalucynowane relacje:** Modele LLM generują trójki faktów, które nie wynikają z tekstu. Należy wymusić weryfikację indeksów źródłowych (provenance).
- **Niespójność relacji w Open IE (Relation drift):** Różnorodne zapisy tej samej relacji (np. „urodził się w”, „miejsce urodzenia to”, „pochodzi z”) tworzą chaos w grafie. Należy je zmapować do identyfikatorów kanonicznych (np. P19), w przeciwnym razie graf będzie bezużyteczny.
- **Ignorowanie wymiaru czasowego relacji:** Zdanie „Tim Cook jest CEO Apple” jest prawdziwe obecnie, lecz było fałszywe w 2005 roku. Wiele relacji ma charakter dynamiczny. Należy stosować kwalifikatory czasowe (np. czas rozpoczęcia P580, czas zakończenia P582 w formacie Wikidanych).
- **Niezgodność dziedziny (Domain mismatch):** Model REBEL był trenowany na artykułach z Wikipedii. Analiza tekstów medycznych, prawnych czy technicznych wymaga modeli RE dostrojonych dziedzinowo.

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Szybkie wdrożenie, domena ogólna | Model REBEL lub dedykowane modele LLM z kanonizacją do bazy Wikidata |
| Analiza tekstów specjalistycznych (medycyna, prawo) | Modele dostrojone dziedzinowo (np. SciREX) + dedykowana ontologia |
| Generowanie za pomocą LLM z weryfikacją | Potok AEVS (kotwiczenie → ekstrakcja → weryfikacja → uzupełnianie) |
| Przetwarzanie wiadomości o dużym wolumenie | Hybryda metod regułowych oraz klasyfikatorów nadzorowanych |
| Budowa grafu wiedzy od zera | Metoda Open IE + etap półautomatycznej kanonizacji relacji |
| Modelowanie czasowe (Temporal KG) | Ekstrakcja relacji wraz z kwalifikatorami czasu |

Sprawdzony potok integracyjny: NER → koreferencja → łączenie encji → ekstrakcja relacji → mapowanie ontologii → zapis do bazy grafowej. Każdy z tych etapów stanowi kluczowy punkt kontroli jakości danych.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-re-designer.md`:

```markdown
---
name: re-designer
description: Zaprojektuj potok ekstrakcji relacji z weryfikacją pochodzenia danych (provenance) oraz kanonizacją.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]
---

Na podstawie charakterystyki korpusu (dziedzina, język, wolumen zapytań) oraz celu biznesowego (GraphRAG, analityka, audyt zgodności) wygeneruj:

1. Ekstraktor: Szablonowy (patterns), nadzorowany, LLM lub hybrydowy (AEVS) wraz z uzasadnieniem (balans precyzji i pełności).
2. Ontologia: Zamknięta lista właściwości (Wikidata / wewnętrzna) lub podejście Open IE z wdrożonym etapem kanonizacji relacji.
3. Pochodzenie danych (Provenance): Każda trójka musi być powiązana z indeksem znakowym w tekście źródłowym oraz identyfikatorem dokumentu (kluczowe dla audytowalności).
4. Strategia scalania: Kanoniczny identyfikator encji + identyfikator relacji + kwalifikatory czasowe oraz zasady deduplikacji.
5. Plan ewaluacji: Precyzja i pełność (precision/recall) na próbie przynajmniej 200 ręcznie oznaczonych trójek oraz wskaźnik halucynacji dla ekstrakcji LLM.

Zawsze odrzucaj projekty potoków RE opartych o LLM, które nie posiadają weryfikacji indeksów znakowych (provenance). Nigdy nie zezwalaj na zapis danych z Open IE do grafu produkcyjnego bez wdrożonego etapu kanonizacji relacji. Oznaczaj jako błędne potoki, które nie obsługują kwalifikatorów czasowych dla relacji zmiennych w czasie (takich jak zatrudnienie, stanowisko czy małżeństwo).
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Uruchom prosty model regułowy z pliku `code/main.py` na 5 zdaniach z artykułów prasowych. Ręcznie zweryfikuj poprawność (precyzję) wyekstrahowanych trójek.
2. **Poziom średni:** Użyj modelu REBEL (lub modelu LLM) na tych samych zdaniach. Porównaj wygenerowane trójki. Który ekstraktor cechuje się wyższą precyzją, a który wyższą pełnością (Recall)?
3. **Poziom trudny:** Zaimplementuj potok zgodny z metodologią AEVS: zrealizuj ekstrakcję za pomocą LLM i weryfikuj poprawność wygenerowanych indeksów znakowych (spans) z tekstem źródłowym. Oblicz wskaźnik halucynacji przed i po nałożeniu filtrów weryfikacyjnych na próbie 50 zdań.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Trójka (Triple) | S-R-O | Krotka `(s, r, o)` będąca podstawowym, atomowym rekordem w grafie wiedzy. |
| Open IE | Wyodrębnij wszystko | Ekstrakcja relacji na bazie wolnego słownictwa języka naturalnego; wysoka pełność (Recall), niska precyzja. |
| Ontologia zamknięta | Sztywny schemat | Ściśle zdefiniowany, skończony słownik dopuszczalnych relacji (np. Wikidata, UMLS, FIBO). |
| Kanonizacja relacji | Normalizacja relacji | Mapowanie synonimów i wariantów zapisu relacji do jednego unikalnego identyfikatora kanonicznego. |
| AEVS | AEVS | Standard Anchor-Extraction-Verification-Supplement gwarantujący ugruntowanie faktów w tekście źródłowym. |
| Pochodzenie danych (Provenance) | Ugruntowanie faktu | Powiązanie każdej trójki z identyfikatorem dokumentu oraz indeksami znakowymi tekstu źródłowego. |
| Zdalny nadzór (Distant Supervision) | Tanie dane uczące | Automatyczne generowanie zbiorów treningowych poprzez mapowanie istniejącego grafu wiedzy na teksty wolne. |

## Literatura uzupełniająca

- [Mintz et al. (2009). Distant supervision for relation extraction without labeled data](https://www.aclweb.org/anthology/P09-1113.pdf) — klasyczna publikacja dotycząca zdalnego nadzoru.
- [Huguet Cabot & Navigli (2021). REBEL: Relation Extraction By End-to-end Language generation](https://aclanthology.org/2021.findings-emnlp.204.pdf) — seq2seq RE.
- [Wadden et al. (2019). Entity, Relation, and Event Extraction with Contextualized Span Representations](https://arxiv.org/abs/1909.03546) — opis biblioteki DyGIE++.
- [AEVS Design (2026): A Framework for Hallucination Mitigation in LLM-based Knowledge Graph Construction](https://www.mdpi.com/2073-431X/15/3/178) — projekt łagodzenia halucynacji w konstrukcjach grafów wiedzy.
- [Oficjalny podręcznik odpytywania baz Wikidata za pomocą języka SPARQL](https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial) — zapytania dotyczące grafów kanonicznych.
