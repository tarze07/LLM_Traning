# Wnioskowanie w języku naturalnym — ujęcie tekstowe

> „t pociąga za sobą h” oznacza, że ludzki odczyt t doszedłby do wniosku, że h jest prawdziwe. NLI to zadanie przewidywania konsekwencji/sprzeczności/neutralności. Nudne na powierzchni, nośne w produkcji.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 05 (Analiza nastrojów), Faza 5 · 13 (Odpowiadanie na pytania)
**Czas:** ~60 minut

## Problem

Stworzyłeś podsumowanie. Powstało podsumowanie. Skąd wiesz, że podsumowanie nie zawiera halucynacji?

Zbudowałeś chatbota. Odpowiedź brzmiała: „tak”. Skąd wiesz, że odpowiedź jest poparta pobranym fragmentem?

Musisz sklasyfikować 10 000 artykułów prasowych według tematu. Nie masz etykiet szkoleniowych. Czy możesz ponownie wykorzystać model?

Wszystkie trzy problemy sprowadzają się do wnioskowania w języku naturalnym. NLI pyta: czy biorąc pod uwagę przesłankę `t` i hipotezę `h`, `h` wynika z `t`, jest sprzeczny czy neutralny (niepowiązany)?

- **Kontrola halucynacji:** `t` = dokument źródłowy, `h` = roszczenie podsumowujące. Brak konsekwencji = halucynacja.
- **Ugruntowana kontrola jakości:** `t` = pobrany fragment, `h` = wygenerowana odpowiedź. Nie implikacja = fabrykacja.
- **Klasyfikacja zerowa:** `t` = dokument, `h` = etykieta zwerbalizowana („Tu chodzi o sport”). Zaangażowanie = przewidywana etykieta.

Jedno zadanie, trzy zastosowania produkcyjne. Właśnie dlatego w każdym systemie oceny RAG znajduje się model NLI.

## Koncepcja

![NLI: klasyfikacja trójczynnikowa, przesłanka vs hipoteza](../assets/nli.svg)

**Trzy etykiety.**

- **Zaangażowanie.** `t` → `h`. „Kot jest na macie” oznacza „Tam jest kot”.
- **Sprzeczność.** `t` → ¬`h`. „Kot jest na macie” zaprzecza „Nie ma kota”.
- **Neutralnie.** Żadnych wnioskowań. „Kot jest na macie” jest neutralny w stosunku do „Kot jest głodny”.

**Nie ma implikacji logicznej.** NLI to wnioskowanie w *naturalnym* języku — to, co wywnioskowałby typowy ludzki czytelnik, a nie ścisła logika. „Jan spacerował z psem” w NLI oznacza „Jan ma psa”, ale ścisła logika pierwszego rzędu dopuszczałaby to tylko wtedy, gdyby aksjomatyzował posiadanie.

**Zestawy danych.**

- **SNLI** (2015). 570 tys. par z adnotacjami ludzkimi, podpisy do zdjęć jako przesłanki. Wąska domena.
- **MultiNLI** (2017). 433 tys. par w 10 gatunkach. Standardowy korpus szkoleniowy w 2026 roku.
- **ANLI** (2019). Kontrahent NLI. Ludzie napisali przykłady specjalnie zaprojektowane, aby przełamać istniejące modele. Trudniej.
- **DocNLI, KONTROL** (2020–21). Założenia dotyczące długości dokumentu. Testuje wnioskowanie wieloskokowe i dalekiego zasięgu.

**Architektura.** Koder transformatora (BERT, RoBERTa, DeBERTa) odczytuje `[CLS] premise [SEP] hypothesis [SEP]`. Reprezentacja `[CLS]` zasila 3-kierunkowy softmax. Trenuj na MNLI, oceniaj na podstawie ustalonych testów porównawczych, uzyskaj ponad 90% dokładności w parach w dystrybucji.

** Zero-shot przez NLI.** Mając dokument i etykiety kandydatów, zamień każdą etykietę w hipotezę („Ten tekst dotyczy sportu”). Oblicz prawdopodobieństwo konsekwencji dla każdego. Wybierz maks. Na tym polega mechanizm `zero-shot-classification` Hugging Face.

## Zbuduj to

### Krok 1: uruchom wstępnie wytrenowany model NLI

```python
from transformers import pipeline

nli = pipeline("text-classification",
               model="facebook/bart-large-mnli",
               top_k=None)  # return all labels; replaces deprecated return_all_scores=True

premise = "The cat is sleeping on the couch."
hypothesis = "There is a cat in the room."

result = nli({"text": premise, "text_pair": hypothesis})[0]
print(result)
# [{'label': 'entailment', 'score': 0.97},
#  {'label': 'neutral', 'score': 0.02},
#  {'label': 'contradiction', 'score': 0.01}]
```

W przypadku produkcyjnego NLI otwartymi wartościami domyślnymi są `facebook/bart-large-mnli` i `microsoft/deberta-v3-large-mnli`. DeBERTa-v3 na szczycie rankingów.

### Krok 2: klasyfikacja zero-shot

```python
zs = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "The stock market rallied after the central bank cut interest rates."
labels = ["finance", "sports", "politics", "technology"]

result = zs(text, candidate_labels=labels)
print(result)
# {'labels': ['finance', 'politics', 'technology', 'sports'],
#  'scores': [0.92, 0.05, 0.02, 0.01]}
```

Szablon to „Ten przykład dotyczy {label}”. domyślnie. Dostosuj za pomocą `hypothesis_template`. Nie są wymagane żadne dane szkoleniowe. Żadnego dostrajania. Działa od razu po wyjęciu z pudełka.

### Krok 3: sprawdzenie wierności RAG

```python
def is_faithful(answer, context, threshold=0.5):
    result = nli({"text": context, "text_pair": answer})[0]
    entail = next(s for s in result if s["label"] == "entailment")
    return entail["score"] > threshold
```

To jest rdzeń wierności RAGAS. Podziel wygenerowaną odpowiedź na niepodzielne oświadczenia. Sprawdź każde roszczenie pod kątem pobranego kontekstu. Podaj ułamek, który z tego wynika.

### Krok 4: ręcznie walcowany klasyfikator NLI (koncepcyjny)

Zobacz `code/main.py`, aby zapoznać się z zabawką obsługującą tylko standardową bibliotekę stdlib: przesłanki i hipotezy są porównywane poprzez wykrywanie nakładania się leksykalnego + negacji. Nie jest konkurencyjny w stosunku do modeli transformatorów — ale pokazuje kształt zadania: dwa teksty, 3-kierunkowa etykieta, strata = entropia krzyżowa powyżej `{entail, contradict, neutral}`.

## Pułapki

- **Skróty dotyczące tylko hipotez.** Modele mogą przewidzieć etykietę na podstawie samej hipotezy na poziomie ~60% w przypadku SNLI, ponieważ „nie”, „nikt”, „nigdy” korelują ze sprzecznością. Solidna podstawa do wykrywania wycieków etykiet.
- **Heurystyka nakładania się leksykalnego.** Heurystyka podciągów („z każdego podciągu wynika”) spełnia wymagania SNLI, ale nie spełnia wymagań HANS/ANLI. Użyj kontradyktoryjnych testów porównawczych.
- **Spadek długości dokumentu.** Jednozdaniowe modele NLI zmniejszają 20+ F1 w oparciu o długość dokumentu. Używaj modeli wyszkolonych w DocNLI dla długiego kontekstu.
- **Czułość szablonu zerowego.** „Ten przykład dotyczy {label}” w porównaniu z „{label}” w porównaniu z „Tematem jest {label}” może zwiększyć dokładność o ponad 10 punktów. Dostosuj szablon.
- **Niezgodność domeny.** MNLI szkoli się z ogólnego języka angielskiego. Teksty prawne, medyczne i naukowe wymagają modeli NLI specyficznych dla danej dziedziny (np. SciNLI, MedNLI).

## Użyj tego

Stos na rok 2026:

| Przypadek użycia | Modelka |
|--------|-------|
| NLI ogólnego przeznaczenia | `microsoft/deberta-v3-large-mnli` |
| Szybki / krawędziowy | `cross-encoder/nli-deberta-v3-base` |
| Klasyfikacja zerowego strzału (lekka) | `facebook/bart-large-mnli` |
| NLI na poziomie dokumentu | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` |
| Wielojęzyczny | `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` |
| Wykrywanie halucynacji w RAG | Warstwa NLI wewnątrz RAGAS / DeepEval |

Meta-wzorzec 2026: NLI to taśma klejąca rozumienia tekstu. Kiedykolwiek potrzebujesz pytania: „Czy A wspiera B?” lub „czy A zaprzecza B?” — sięgnij po NLI, zanim sięgniesz po kolejne połączenie LLM.

## Wyślij to

Zapisz jako `outputs/skill-nli-picker.md`:

```markdown
---
name: nli-picker
description: Pick an NLI model, label template, and evaluation setup for a classification / faithfulness / zero-shot task.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]
---

Given a use case (faithfulness check, zero-shot classification, document-level inference), output:

1. Model. Named NLI checkpoint. Reason tied to domain, length, language.
2. Template (if zero-shot). Verbalization pattern. Example.
3. Threshold. Entailment cutoff for the decision rule. Reason based on calibration.
4. Evaluation. Accuracy on held-out labeled set, hypothesis-only baseline, adversarial subset.

Refuse to ship zero-shot classification without a 100-example labeled sanity check. Refuse to use a sentence-level NLI model on document-length premises. Flag any claim that NLI solves hallucination — it reduces it; it does not eliminate it.
```

## Ćwiczenia

1. **Łatwe.** Uruchom `facebook/bart-large-mnli` na 20 ręcznie wykonanych trójkach (przesłanka, hipoteza, etykieta) obejmujących wszystkie trzy klasy. Zmierz dokładność. Dodaj kontradyktoryjne pułapki „heurystyczne podsekwencji” („nie zjadłem ciasta” vs „zjadłem ciasto”) i zobacz, czy się zepsuje.
2. **Średni.** Porównaj szablon zerowy `"This text is about {label}"` z `"The topic is {label}"` i `"{label}"` w nagłówkach 100 AG News. Raportuj wahania dokładności.
3. **Trudne.** Zbuduj narzędzie do sprawdzania wierności RAG: rozkład roszczeń atomowych + NLI na roszczenie. Oceń 50 odpowiedzi wygenerowanych przez RAG ze złotym kontekstem. Zmierz odsetek wyników fałszywie dodatnich i fałszywie ujemnych w porównaniu z etykietami ręcznymi.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| NLI | Wnioskowanie w języku naturalnym | Trójczynnikowa klasyfikacja zależności przesłanka-hipoteza. |
| RTE | Rozpoznawanie treści tekstowych | Starsza nazwa NLI; to samo zadanie. |
| Zaangażowanie | „t implikuje h” | Typowy czytelnik doszedłby do wniosku, że h jest prawdziwe, biorąc pod uwagę t. |
| Sprzeczność | „t wyklucza h” | Typowy czytelnik doszedłby do wniosku, że h jest fałszywe, biorąc pod uwagę t. |
| Neutralny | „niezdecydowany” | W obu przypadkach nie ma żadnego wnioskowania od t do h. |
| Klasyfikacja zerowego strzału | NLI jako klasyfikator | Werbalizuj etykiety jako hipotezy, wybieraj maksymalne wnioski. |
| Wierność | Czy odpowiedź jest obsługiwana? | Koniec NLI (pobrany kontekst, wygenerowana odpowiedź). |

## Dalsze czytanie

- [Bowman i in. (2015). Duży korpus z adnotacjami do nauki wnioskowania w języku naturalnym](https://arxiv.org/abs/1508.05326) — SNLI.
- [Williams, Nangia, Bowman (2017). Korpus wyzwań o szerokim zasięgu dotyczący rozumienia zdań poprzez wnioskowanie](https://arxiv.org/abs/1704.05426) — MultiNLI.
- [Nie i in. (2019). Adversarial NLI](https://arxiv.org/abs/1910.14599) — punkt odniesienia ANLI.
- [Yin, Hay, Roth (2019). Benchmarkingowa klasyfikacja tekstu typu zero-shot](https://arxiv.org/abs/1909.00161) — NLI-as-classifier.
- [On i in. (2021). DeBERTa: BERT ze wzmocnionym dekodowaniem i rozplątaną uwagą](https://arxiv.org/abs/2006.03654) – koń pociągowy NLI 2026.