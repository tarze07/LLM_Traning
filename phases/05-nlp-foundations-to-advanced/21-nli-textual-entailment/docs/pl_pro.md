# Wnioskowanie w języku naturalnym (NLI) – implikacja tekstowa (Textual Entailment)

> „Tekst T implikuje hipotezę H” (T entails H) oznacza, że człowiek czytający tekst T wyciągnąłby wniosek, że H jest prawdziwe. Zadanie NLI polega na klasyfikacji relacji między nimi jako: implikacja (entailment), sprzeczność (contradiction) lub neutralność (neutral). Choć brzmi to abstrakcyjnie, ma kolosalne znaczenie w systemach produkcyjnych.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 05 (Analiza wydźwięku), Faza 5 · 13 (Odpowiadanie na pytania)
**Czas:** ~60 minut

## Problem

Wygenerowałeś podsumowanie artykułu. Skąd masz pewność, że nie zawiera ono zhalucynowanych informacji?

Wdrożyłeś chatbota. Na pytanie użytkownika odpowiedział: „Tak”. Skąd wiesz, czy ta odpowiedź znajduje potwierdzenie w pobranym kontekście?

Musisz przypisać 10 000 artykułów prasowych do odpowiednich kategorii tematycznych. Nie masz oznaczonych danych treningowych. Czy możesz do tego celu wykorzystać gotowy model?

Każdy z tych trzech problemów można sprowadzić do zadania wnioskowania w języku naturalnym (NLI – Natural Language Inference). W NLI analizujemy relację między przesłanką (premise, oznaczoną jako `T`) a hipotezą (hypothesis, oznaczoną jako `H`). Badamy, czy zachodzi między nimi implikacja (wynikanie), sprzeczność (wykluczanie), czy też relacja jest neutralna.

- **Wykrywanie halucynacji:** `T` = dokument źródłowy, `H` = zdanie z podsumowania. Brak implikacji = halucynacja.
- **Weryfikacja ugruntowania odpowiedzi (grounding):** `T` = pobrany kontekst (passage), `H` = wygenerowana odpowiedź. Brak implikacji = konfabulacja/fabrykacja.
- **Klasyfikacja zero-shot:** `T` = dokument wejściowy, `H` = etykieta przekształcona w zdanie („Ten tekst dotyczy sportu”). Wykrycie implikacji oznacza przypisanie danej etykiety.

Jedno zadanie, a rozwiązuje trzy kluczowe problemy biznesowe. Właśnie dlatego model NLI jest nieodzownym elementem każdego nowoczesnego systemu oceny RAG (RAG evaluation).

## Koncepcja

![NLI: trójklasowa klasyfikacja relacji między przesłanką a hipotezą](../assets/nli.svg)

**Trzy klasy relacji:**

- **Implikacja / Wynikanie (Entailment):** `T` → `H`. Przykład: „Kot śpi na macie” implikuje „W pokoju znajduje się kot”.
- **Sprzeczność (Contradiction):** `T` → ¬`H`. Przykład: „Kot śpi na macie” zaprzecza zdaniu „W pokoju nie ma żadnego kota”.
- **Neutralność (Neutral):** Brak relacji wynikania ani wykluczenia. Przykład: „Kot śpi na macie” jest neutralne wobec zdania „Kot jest głodny”.

**Niewynikanie ściśle logiczne.** NLI to wnioskowanie w języku *naturalnym* – opiera się na tym, jak tekst zinterpretowałby przeciętny człowiek, a nie na zasadach formalnej logiki matematycznej. Przykładowo, zdanie „Jan spacerował ze swoim psem” w zadaniu NLI implikuje zdanie „Jan ma psa”, mimo że z punktu widzenia logiki pierwszego rzędu wynikanie to nie zachodzi bez jawnego zdefiniowania aksjomatu posiadania.

**Zbiory danych:**

- **SNLI** (2015): 570 tysięcy ręcznie oznaczonych par, gdzie jako przesłanki posłużyły opisy obrazków. Wąska dziedzina tekstów.
- **MultiNLI** (2017): 433 tysięcy par z 10 różnych gatunków literackich i stylów. Standardowy zbiór treningowy.
- **ANLI** (2019): Zbiór stworzony wrogą metodą (adversarial NLI). Analitycy celowo pisali hipotezy tak, aby oszukać ówczesne modele. Znacznie trudniejszy benchmark.
- **DocNLI, CONTRACT** (2020–21): Zbiory oparte na długich dokumentach, testujące wnioskowanie wielokrokowe (multi-hop) na dużych odległościach.

**Architektura.** Encoder transformerowy (np. BERT, RoBERTa, DeBERTa) przyjmuje na wejściu sekwencję w formacie `[CLS] przesłanka [SEP] hipoteza [SEP]`. Reprezentacja wektora `[CLS]` z ostatniej warstwy jest przekazywana do klasyfikatora z trójklasową funkcją Softmax. Modele trenowane na zbiorze MNLI i testowane na standardowych benchmarkach osiągają obecnie ponad 90% dokładności (accuracy) dla danych z tej samej dystrybucji.

**Zero-shot classification za pomocą NLI.** Mając dokument i zestaw potencjalnych etykiet, każdą etykietę przekształcamy w hipotezę (np. „Ten tekst dotyczy sportu”). Obliczamy prawdopodobieństwo implikacji (entailment score) dla każdej pary i wybieramy tę o najwyższym wyniku. Dokładnie tak działa popularny rurociąg `zero-shot-classification` w bibliotece Hugging Face.

## Zbuduj to

### Krok 1: Uruchomienie pre-trenowanego modelu NLI

```python
from transformers import pipeline

nli = pipeline("text-classification",
               model="facebook/bart-large-mnli",
               top_k=None)  # zwraca wszystkie etykiety

premise = "The cat is sleeping on the couch."
hypothesis = "There is a cat in the room."

result = nli({"text": premise, "text_pair": hypothesis})[0]
print(result)
# [{'label': 'entailment', 'score': 0.97},
#  {'label': 'neutral', 'score': 0.02},
#  {'label': 'contradiction', 'score': 0.01}]
```

W zastosowaniach produkcyjnych standardem są modele `facebook/bart-large-mnli` oraz `microsoft/deberta-v3-large-mnli` (rodzina DeBERTa-v3 zajmuje obecnie czołowe miejsca w rankingach).

### Krok 2: Klasyfikacja Zero-shot

```python
zs = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "The stock market rallied after the central bank cut interest rates."
labels = ["finance", "sports", "politics", "technology"]

result = zs(text, candidate_labels=labels)
print(result)
# {'labels': ['finance', 'politics', 'technology', 'sports'],
#  'scores': [0.92, 0.05, 0.02, 0.01]}
```

Domyślny szablon hipotezy to: „This text is about {label}”. Możesz go dostosować za pomocą parametru `hypothesis_template`. Metoda ta nie wymaga żadnych danych treningowych ani dostrajania wag modelu.

### Krok 3: Weryfikacja spójności (faithfulness) w systemach RAG

```python
def is_faithful(answer, context, threshold=0.5):
    result = nli({"text": context, "text_pair": answer})[0]
    entail = next(s for s in result if s["label"] == "entailment")
    return entail["score"] > threshold
```

To kluczowy mechanizm ewaluacyjny (np. w bibliotece Ragas). Wygenerowana przez LLM odpowiedź jest dzielona na atomowe zdania twierdzące, a następnie każde z nich jest weryfikowane modelem NLI pod kątem zgodności z pobranym kontekstem. Wynik to odsetek zdań, dla których wykazano relację implikacji.

### Krok 4: Prosty, regułowy algorytm NLI (przykład koncepcyjny)

W pliku `code/main.py` znajdziesz uproszczony model oparty wyłącznie na bibliotece standardowej Pythona. Przesłanka i hipoteza są tam porównywane pod kątem nakładania się słów (lexical overlap) oraz obecności przeczeń. Kod ten ma charakter wyłącznie dydaktyczny i nie może konkurować z transformerami, lecz dobrze obrazuje strukturę zadania: wejście składa się z dwóch tekstów, wyjściem jest jedna z 3 klas, a funkcją straty – entropia krzyżowa (cross-entropy) dla etykiet `{entailment, contradiction, neutral}`.

## Typowe pułapki

- **Korelacje oparte wyłącznie na hipotezie (Hypothesis-only biases):** Modele potrafią poprawnie sklasyfikować relację w ~60% przypadków na podstawie samej hipotezy (bez czytania przesłanki!), ponieważ słowa takie jak „nie”, „nikt”, „nigdy” silnie korelują z klasą sprzeczności w zbiorze SNLI. To częsty problem wycieku etykiet w zbiorach danych.
- **Heurystyka nakładania się leksykalnego (Lexical overlap bias):** Modele mogą nauczyć się błędnej reguły, że jeśli hipoteza składa się ze słów występujących w przesłance, to zawsze zachodzi implikacja. Reguła ta sprawdza się na prostym zbiorze SNLI, lecz zawodzi na trudniejszych zbiorach HANS czy ANLI. Warto stosować wrogie testy porównawcze (adversarial benchmarks).
- **Spadek wydajności na długich tekstach:** Modele NLI trenowane na pojedynczych zdaniach notują spadek miary F1 o ponad 20 punktów, gdy przesłanką staje się długi dokument. W takich przypadkach należy stosować modele dedykowane, np. trenowane na zbiorze DocNLI.
- **Wpływ szablonu promptu (Template sensitivity):** Zmiana szablonu hipotezy (np. porównanie „Ten tekst dotyczy {label}” vs „Tematyka: {label}”) potrafi zmienić dokładność klasyfikacji zero-shot nawet o ponad 10 punktów procentowych. Szablony wymagają starannego doboru.
- **Niezgodność dziedziny (Domain mismatch):** Standardowy zbiór MNLI zawiera teksty o charakterze ogólnym. Analiza tekstów prawnych, medycznych czy naukowych wymaga modeli NLI dostrojonych dziedzinowo (np. SciNLI, MedNLI).

## Rekomendowane podejścia

| Przypadek użycia | Rekomendowany model |
|--------|-------|
| NLI ogólnego przeznaczenia | `microsoft/deberta-v3-large-mnli` |
| Wersje szybkie / urządzenia brzegowe | `cross-encoder/nli-deberta-v3-base` |
| Klasyfikacja zero-shot (lekka) | `facebook/bart-large-mnli` |
| NLI na poziomie całych dokumentów | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` |
| Modele wielojęzyczne | `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` |
| Wykrywanie halucynacji w RAG | Ewaluatory NLI w bibliotekach Ragas / DeepEval |

Złota zasada: Modele NLI to doskonałe, tanie narzędzie do weryfikacji faktów w tekście. Zawsze gdy musisz odpowiedzieć na pytanie „Czy tekst A potwierdza informację B?” lub „Czy zdanie A zaprzecza dokumentowi B?”, użyj dedykowanego modelu NLI zamiast generować kosztowne i wolne zapytania do modeli LLM.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-nli-picker.md`:

```markdown
---
name: nli-picker
description: Wybierz model NLI, szablon hipotezy oraz strukturę ewaluacji dla zadania klasyfikacji, weryfikacji spójności lub klasyfikacji zero-shot.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]
---

Na podstawie scenariusza użycia (weryfikacja ugruntowania/faithfulness, klasyfikacja zero-shot, wnioskowanie na poziomie dokumentu) wygeneruj:

1. Model: Dokładna nazwa punktu kontrolnego (checkpoint) modelu NLI wraz z uzasadnieniem (dziedzina, długość kontekstu, język).
2. Szablon (dla zero-shot): Konstrukcja szablonu hipotezy wraz z przykładem.
3. Próg odcięcia (Threshold): Wartość progowa prawdopodobieństwa implikacji dla reguły decyzyjnej wraz z uzasadnieniem (kalibracja).
4. Plan ewaluacji: Dokładność (accuracy) na wydzielonym zbiorze testowym, wynik bazowy dla samej hipotezy (hypothesis-only baseline) oraz wyniki na wrogim podzbiorze testowym.

Nigdy nie wdrażaj klasyfikacji zero-shot bez wcześniejszego testu poprawności (sanity check) na przynajmniej 100 oznaczonych przykładach. Nigdy nie stosuj modeli NLI trenowanych na zdaniach do analizy dokumentów o znacznej długości. Wyraźnie zaznaczaj, że NLI nie eliminuje całkowicie problemu halucynacji – pozwala go jedynie istotnie ograniczyć.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Przetestuj model `facebook/bart-large-mnli` na 20 przygotowanych samodzielnie trójkach (przesłanka, hipoteza, etykieta) reprezentujących wszystkie trzy klasy. Zmierz dokładność klasyfikacji. Dodaj trudniejsze przykłady oparte na nakładaniu się słów z przeczeniem (np. „Nie zjadłem ciasta” vs „Zjadłem ciasto”) i sprawdź, czy model da się oszukać.
2. **Poziom średni:** Porównaj skuteczność klasyfikacji zero-shot na zbiorze 100 artykułów z bazy AG News przy użyciu różnych szablonów: „This text is about {label}”, „The topic is {label}” oraz czystego „{label}”. Zgłoś zaobserwowane wahania metryki dokładności.
3. **Poziom trudny:** Zbuduj własny skrypt do oceny ugruntowania odpowiedzi (faithfulness check) dla systemu RAG: podziel odpowiedź na zdania atomowe i wykonaj klasyfikację NLI dla każdego z nich. Przeprowadź ewaluację na 50 wygenerowanych parach odpowiedź-kontekst. Oblicz odsetek wyników fałszywie dodatnich (false positives) i fałszywie ujemnych (false negatives) w odniesieniu do ręcznie oznaczonych danych referencyjnych.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| NLI | Wnioskowanie w języku naturalnym | Trójklasowa klasyfikacja relacji semantycznej między przesłanką a hipotezą. |
| RTE (Recognising Textual Entailment) | RTE | Starsze określenie na zadanie wnioskowania w języku naturalnym (NLI). |
| Implikacja / Wynikanie (Entailment) | „T implikuje H” | Relacja, w której czytelnik tekstu T naturalnie wywnioskuje, że hipoteza H jest prawdziwa. |
| Sprzeczność (Contradiction) | „T wyklucza H” | Relacja, w której czytelnik tekstu T naturalnie wywnioskuje, że hipoteza H jest fałszywa (H stoi w sprzeczności z T). |
| Neutralność (Neutral) | „niezdecydowany” | Brak podstaw do wywnioskowania prawdziwości lub fałszywości hipotezy H na podstawie tekstu T. |
| Klasyfikacja zero-shot za pomocą NLI | NLI jako klasyfikator | Przekształcenie etykiet klas w hipotezy i wybór klasy o najwyższym współczynniku implikacji. |
| Wierność / Ugruntowanie (Faithfulness) | Czy odpowiedź jest ugruntowana? | Ocena, czy wygenerowana odpowiedź systemu RAG jest w pełni poparta pobranym kontekstem źródłowym. |

## Literatura uzupełniająca

- [Bowman et al. (2015). A large annotated corpus for learning natural language inference](https://arxiv.org/abs/1508.05326) — publikacja wprowadzająca zbiór SNLI.
- [Williams, Nangia, Bowman (2017). A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference](https://arxiv.org/abs/1704.05426) — publikacja prezentująca zbiór MultiNLI.
- [Nie et al. (2019). Adversarial NLI: A New Benchmark for Natural Language Inference](https://arxiv.org/abs/1910.14599) — opis wrogiej metodologii tworzenia zbioru ANLI.
- [Yin, Hay, Roth (2019). Benchmarking Zero-Shot Text Classification: Systematic Investigation of Cross-Task Generalization](https://arxiv.org/abs/1909.00161) — zastosowanie modeli NLI do klasyfikacji tekstu.
- [He et al. (2020). DeBERTa: Decoding-enhanced BERT with Disentangled Attention](https://arxiv.org/abs/2006.03654) — oryginalna praca wprowadzająca wiodącą architekturę DeBERTa.
