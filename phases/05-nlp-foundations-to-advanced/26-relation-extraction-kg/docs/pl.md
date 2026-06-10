# Ekstrakcja relacji i konstrukcja wykresu wiedzy

> NER znalazł podmioty. Łączenie jednostek zakotwiczyło je. Ekstrakcja relacji pozwala znaleźć krawędzie pomiędzy nimi. Wykres wiedzy to suma węzłów, krawędzi i ich pochodzenia.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 25 (łączenie jednostek)
**Czas:** ~60 minut

## Problem

Analityk czyta: „Tim Cook został dyrektorem generalnym Apple w 2011 roku”. Cztery fakty:

- `(Tim Cook, role, CEO)`
- `(Tim Cook, employer, Apple)`
- `(Tim Cook, start_date, 2011)`
- `(Apple, type, Organization)`

Ekstrakcja relacji (RE) przekształca dowolny tekst w ustrukturyzowane trójki `(subject, relation, object)`. Agregując dane w całym korpusie, otrzymasz wykres wiedzy. Agreguj i wysyłaj zapytania, a otrzymasz podłoże do rozumowania dla RAG, analiz lub audytów zgodności.

Problem 2026: LLM entuzjastycznie wykorzystują relacje. Zbyt entuzjastycznie. Mają halucynacje potrójne, których tekst źródłowy nie potwierdza. Bez pochodzenia nie można odróżnić prawdziwych trójek od wiarygodnej fikcji. Odpowiedzią na rok 2026 są rurociągi typu „kotwicz i weryfikuj” w stylu AEVS.

## Koncepcja

![Tekst → trójki → wykres wiedzy](../assets/relation-extraction.svg)

**Forma potrójna.** `(subject_entity, relation_type, object_entity)`. Relacje pochodzą z zamkniętej ontologii (właściwości Wikidanych, FIBO, UMLS) lub zbioru otwartego (w stylu OpenIE, wszystko jest dozwolone).

**Trzy podejścia do ekstrakcji.**

1. **Oparte na regułach/wzorcach.** Wzorce Hearsta: „X takie jak Y” → `(Y, isA, X)`. Plus ręcznie wykonane wyrażenie regularne. Kruchy, precyzyjny, łatwy do wytłumaczenia.
2. **Klasyfikator nadzorowany.** Biorąc pod uwagę dwie wzmianki o podmiotach w zdaniu, przewiduj relację na podstawie ustalonego zbioru. Szkolony na TACRED, ACE, KBP. Norma 2015–2022.
3. **Generatywny LLM.** Poproś model o wyemitowanie potrójnych wartości. Działa od razu po wyjęciu z pudełka. Potrzebuje pochodzenia lub ma halucynacje przypominające wiarygodnie wyglądające śmieci.

**AEVS (Anchor-Extraction-Verification-Suplement, 2026).** Aktualne ramy łagodzenia halucynacji:

- **Kotwica.** Zidentyfikuj każdy zakres encji i zakres relacji z dokładnymi pozycjami.
- **Wyciąg.** Generuj trójki połączone z rozpiętościami kotwic.
- **Sprawdź.** Dopasuj każdy potrójny element do tekstu źródłowego; odrzuć wszystko, co nie jest obsługiwane.
- **Uzupełnienie.** Przepustka zabezpieczająca gwarantuje, że żadne zakotwiczone przęsło nie zostanie upuszczone.

Halucynacje gwałtownie spadają. Wymaga większej liczby obliczeń, ale można go kontrolować.

**Kompromis otwarty i zamknięty.**

- **Zamknięta ontologia.** Stała lista właściwości (np. ponad 11 000 właściwości Wikidanych). Możliwy do przewidzenia. Możliwość zapytania. Trudno wymyślić.
- **Otwórz IE.** Każde zdanie słowne staje się relacją. Wysoka pamięć. Niska precyzja. Brudne pytanie.

Produkcyjne KG zwykle mieszają: otwierają IE do odkrycia, następnie kanonizują relacje w zamkniętej ontologii przed połączeniem z głównym wykresem.

## Zbuduj to

### Krok 1: ekstrakcja oparta na wzorcach

```python
PATTERNS = [
    (r"(?P<s>[A-Z]\w+) (?:is|was) (?:a|an|the) (?P<o>[A-Z]?\w+)", "isA"),
    (r"(?P<s>[A-Z]\w+) (?:is|was) born in (?P<o>\w+)", "bornIn"),
    (r"(?P<s>[A-Z]\w+) works? (?:at|for) (?P<o>[A-Z]\w+)", "worksAt"),
    (r"(?P<s>[A-Z]\w+) founded (?P<o>[A-Z]\w+)", "founded"),
]
```

Zobacz `code/main.py`, aby zapoznać się z pełnym ekstraktorem zabawek. Wzorce Hearsta nadal są dostarczane w potokach specyficznych dla domeny, ponieważ można je debugować.

### Krok 2: klasyfikacja relacji nadzorowanej

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tok = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSequenceClassification.from_pretrained("Babelscape/rebel-large")

text = "Tim Cook was born in Alabama. He later became CEO of Apple."
encoded = tok(text, return_tensors="pt", truncation=True)
output = model.generate(**encoded, max_length=200)
triples = tok.batch_decode(output, skip_special_tokens=False)
```

REBEL jest ekstraktorem relacji seq2seq: wejście tekstu, potrojenie, już w identyfikatorach właściwości Wikidanych. Dostrojone na podstawie danych pochodzących z zdalnego nadzoru. Standardowa linia bazowa z otwartymi ciężarami.

### Krok 3: Ekstrakcja pod wpływem LLM z zakotwiczeniem

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

Sprawdź każdy zwrócony zakres względem źródła. Odrzuć wszystko, gdzie `text[start:end] != triple_entity`. Jest to etap „weryfikacji” AEVS w jego minimalnej formie.

### Krok 4: kanonizacja do zamkniętej ontologii

```python
RELATION_MAP = {
    "is the CEO of": "P169",       # "chief executive officer"
    "was born in":   "P19",         # "place of birth"
    "founded":        "P112",       # "founded by" (inverted subject/object)
    "works at":       "P108",       # "employer"
}

def canonicalize(relation):
    rel_low = relation.lower().strip()
    if rel_low in RELATION_MAP:
        return RELATION_MAP[rel_low]
    return None   # drop unmapped open relations or route to manual review
```

Kanonizacja to często 60-80% pracy inżynierskiej. Budżet na to.

### Krok 5: zbuduj mały wykres i zapytanie

```python
triples = extract(text)
graph = {}
for s, r, o in triples:
    graph.setdefault(s, []).append((r, o))

def neighbors(node, relation=None):
    return [(r, o) for r, o in graph.get(node, []) if relation is None or r == relation]

print(neighbors("Tim Cook", relation="P108"))    # -> [(P108, Apple)]
```

To jest atom każdego systemu RAG-over-KG. Skaluj go za pomocą potrójnych magazynów RDF (Blazegraph, Virtuoso), wykresów właściwości (Neo4j) lub magazynów grafów powiększanych wektorowo.

## Pułapki

- **Korespondencja przed RE.** „Założył Apple” — RE musi wiedzieć, kim „on” jest. Najpierw uruchom coref (lekcja 24).
- **Kanonizacja jednostki.** „Apple Inc” i „Apple” muszą być rozpoznawane w tym samym węźle. Najpierw łączenie encji (lekcja 25).
- **Halucynowane trójki.** LLM emitują trójki, których tekst nie obsługuje. Wymuś weryfikację zakresu.
- **Dryf kanonizacji relacji.** Otwarte relacje IE są niespójne („urodził się w”, „pochodził z”, „pochodzi z”). Zwiń do identyfikatorów kanonicznych, w przeciwnym razie wykresu nie można sprawdzić.
- **Błędy czasowe.** „Tim Cook jest dyrektorem generalnym Apple” — obecnie prawda, w 2005 r. fałsz. Wiele relacji jest ograniczonych w czasie. Użyj kwalifikatorów (`P580` czas rozpoczęcia, `P582` czas zakończenia w Wikidanych).
- **Niezgodność domeny.** REBEL przeszkolony na Wikipedii. Teksty prawne, medyczne i naukowe często wymagają modeli RE dostosowanych do danej dziedziny.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Szybka produkcja, domena ogólna | REBEL lub LlamaPred z kanonizacją Wikidanych |
| Specyficzne dla domeny (biomed, legalne) | Dostosowanie domeny w stylu SciREX + niestandardowa ontologia |
| Podpowiedzi LLM, skontrolowane wyniki | Rurociąg AEVS: zakotwiczenie → wyodrębnienie → zweryfikowanie → uzupełnienie |
| Wiadomości o dużej objętości IE | Hybryda oparta na wzorcach + nadzorowana |
| Budowa KG od podstaw | Otwarty IE + przepustka do ręcznej kanonizacji |
| Tymczasowy KG | Wyciąg z kwalifikatorami (czas rozpoczęcia/zakończenia, punkt w czasie) |

Wzorzec integracji: NER → coref → łączenie encji → ekstrakcja relacji → mapowanie ontologii → ładowanie grafu. Każdy etap jest potencjalną bramą jakości.

## Wyślij to

Zapisz jako `outputs/skill-re-designer.md`:

```markdown
---
name: re-designer
description: Design a relation extraction pipeline with provenance and canonicalization.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]
---

Given a corpus (domain, language, volume) and downstream use (KG-RAG, analytics, compliance), output:

1. Extractor. Pattern-based / supervised / LLM / AEVS hybrid. Reason tied to precision vs recall target.
2. Ontology. Closed property list (Wikidata / domain) or open IE with canonicalization pass.
3. Provenance. Every triple carries source char-span + doc id. Non-negotiable for audit.
4. Merge strategy. Canonical entity id + relation id + temporal qualifiers; dedup policy.
5. Evaluation. Precision / recall on 200 hand-labelled triples + hallucination-rate on LLM-extracted sample.

Refuse any LLM-based RE pipeline without span verification (source provenance). Refuse open-IE output flowing into a production graph without canonicalization. Flag pipelines with no temporal qualifier on time-bounded relations (employer, spouse, position).
```

## Ćwiczenia

1. **Łatwe.** Uruchom ekstraktor wzorców w `code/main.py` na 5 zdaniach z artykułów prasowych. Sprawdź precyzję ręcznie.
2. **Średni.** Użyj REBEL (lub małego LLM) w tych samych zdaniach. Porównaj trójki. Który ekstraktor ma większą precyzję? Wyższa pamięć?
3. **Trudne.** Zbuduj potok AEVS: wyodrębnij za pomocą LLM + sprawdź zakresy względem źródła. Zmierz współczynnik halucynacji przed i po etapie weryfikacji na 50 zdaniach w stylu Wikipedii.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Potrójne | Podmiot-relacja-przedmiot | `(s, r, o)` krotka będąca jednostką atomową KG. |
| Otwórz IE | Wyodrębnij wszystko | Zwroty relacyjne o otwartym słownictwie; wysoka pamięć, niska precyzja. |
| Zamknięta ontologia | Naprawiono schemat | Ograniczony zbiór typów relacji (Wikidata, UMLS, FIBO). |
| Kanonizacja | Normalizuj wszystko | Mapuj nazwy powierzchni/relacje do identyfikatorów kanonicznych. |
| AEV | Ekstrakcja uziemiona | Rurociąg „Kotwica-Wydobycie-Weryfikacja-Suplementacja” (2026). |
| Pochodzenie | Link do źródła prawdy | Każda trójka przenosi do źródła identyfikator dokumentu + zakres znaków. |
| Zdalny nadzór | Tanie etykiety | Dopasuj tekst do istniejącego KG, aby utworzyć dane szkoleniowe. |

## Dalsze czytanie

- [Mintz i in. (2009). Nadzór zdalny w zakresie ekstrakcji relacji bez oznaczonych danych](https://www.aclweb.org/anthology/P09-1113.pdf) — dokument dotyczący zdalnego nadzoru.
- [Huguet Cabot, Navigli (2021). REBEL: Ekstrakcja relacji przez kompleksowe generowanie języka](https://aclanthology.org/2021.findings-emnlp.204.pdf) — seq2seq RE.
- [Wadden i in. (2019). Ekstrakcja encji, relacji i zdarzeń za pomocą kontekstowych reprezentacji rozpiętości (DyGIE++)](https://arxiv.org/abs/1909.03546) — wspólne IE.
- [AEVS — Struktura Anchor-Extraction-Verification-Supplement](https://www.mdpi.com/2073-431X/15/3/178) — Projekt łagodzenia halucynacji na rok 2026.
- [Poradnik Wikidata SPARQL](https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial) — zapytania dotyczące grafów kanonicznych.