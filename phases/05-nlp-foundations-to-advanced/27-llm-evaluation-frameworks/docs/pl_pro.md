# Ocena LLM — RAGAS, DeepEval, G-Eval

> Dokładne dopasowanie i miara F1 pomijają równoważność semantyczną. Ręczna weryfikacja nie skaluje się. Rozwiązaniem na poziomie produkcyjnym jest LLM-as-judge — odpowiednio skalibrowany, by ufać uzyskiwanym wynikom.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (odpowiadanie na pytania), faza 5 · 14 (wyszukiwanie informacji)
**Czas:** ~75 minut

## Problem

Twój system RAG odpowiada: „29 czerwca 2007".
Złoty wzorzec to: „29 czerwca 2007".
Wynik Dokładnego Dopasowania wynosi 0. Wynik F1 wynosi ~75%. Człowiek przyznałby 100%.

Teraz pomnóż to przez 10 000 przypadków testowych. Pomnóż ponownie przez każdą zmianę w module pobierającym, metodzie podziału na fragmenty, szablonie podpowiedzi lub modelu. Potrzebujesz narzędzia oceniającego, które rozumie znaczenie, działa tanio i na dużą skalę, rzetelnie wykrywa regresje i wskazuje właściwe tryby awarii.

W 2026 roku dostępne są trzy frameworki rozwiązujące ten problem.

- **RAGAS.** Ewaluacja generacji wspomaganej wyszukiwaniem. Cztery metryki RAG (wierność, trafność odpowiedzi, precyzja kontekstu, kompletność kontekstu) oparte na NLI i LLM-as-judge. Potwierdzone badaniami, lekkie w użyciu.
- **DeepEval.** Pytest dla LLM. Oferuje G-Eval, ocenę wykonania zadań, wykrywanie halucynacji i miary stronniczości. Natywnie zintegrowany z CI/CD.
- **G-Eval.** Metoda (i metryka DeepEval): LLM jako sędzia z niestandardowymi kryteriami opartymi na łańcuchu myślenia, zwracający wynik w skali 0–1.

Wszystkie trzy opierają się na LLM jako sędzi. Ta lekcja buduje intuicję dotyczącą tej metody oraz warstwy zaufania wokół niej.

## Koncepcja

![Cztery wymiary oceny, architektura LLM-as-judge](../assets/llm-evaluation.svg)

**LLM jako sędzia.** Zastąp metrykę statyczną modelem LLM, który ocenia wyniki według zadanej rubryki. Mając dane `(query, context, answer)`, polecamy sędziemu: „Oceń wierność w skali 0–1". Metoda zwraca wynik.

Dlaczego to działa: modele LLM przybliżają ludzką ocenę za ułamek jej kosztu. GPT-4o-mini w ~$0.003 per scored case enables 1000-sample regression eval runs for under $5.

Dlaczego może zawodzić po cichu:

1. **Stronniczość sędziego.** Sędziowie preferują dłuższe odpowiedzi, odpowiedzi z tej samej rodziny modeli i odpowiedzi dopasowane stylistycznie do szablonu podpowiedzi.
2. **Błędy parsowania JSON.** Niepoprawny JSON → wynik NaN → dyskretnie wykluczony z agregatu. Użytkownicy RAGAS dobrze znają ten problem. Stosuj bramę z `try/except` i jawnym trybem awarii.
3. **Pomijanie wersji modeli.** Aktualizacja modelu-sędziego zmienia każdą metrykę. Zablokuj wersję modelu oceniającego.

**Czwórka RAG.**

| Metryka | Pytanie | Mechanizm |
|--------|----------|--------|
| Wierność | Czy każde twierdzenie w odpowiedzi pochodzi z pobranego kontekstu? | NLI wspomagane LLM |
| Trafność odpowiedzi | Czy odpowiedź odnosi się do zadanego pytania? | Generuj hipotetyczne pytania na podstawie odpowiedzi; porównaj z oryginalnym pytaniem |
| Precyzja kontekstu | Jaka część pobranych fragmentów była istotna? | LLM jako sędzia |
| Kompletność kontekstu | Czy wyszukiwanie zwróciło wszystkie potrzebne informacje? | LLM jako sędzia względem złotej odpowiedzi |

**G-Eval.** Zdefiniuj niestandardowe kryterium, np.: „Czy odpowiedź podaje właściwe źródło?". Framework automatycznie rozbudowuje je o etapy oceny oparte na łańcuchu myślenia, a następnie zwraca wynik 0–1. Sprawdza się w przypadku wymiarów jakości specyficznych dla danej domeny, których RAGAS nie obejmuje.

**Kalibracja.** Nigdy nie ufaj surowym wynikom sędziego bez weryfikacji ich korelacji z ludzkimi ocenami. Uruchom 100 ręcznie oznaczonych przykładów. Porównaj wyniki sędziego z ocenami człowieka. Oblicz współczynnik rho Spearmana. Jeśli rho < 0,7, rubryka sędziego wymaga dopracowania.

## Zbuduj to

### Krok 1: wierność NLI (w stylu RAGAS)

```python
from typing import Callable
from transformers import pipeline

nli = pipeline("text-classification",
               model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
               top_k=None)

# `llm` is any callable: prompt str -> generated str.
# Example: llm = lambda p: client.messages.create(model="claude-haiku-4-5", ...).content[0].text
LLM = Callable[[str], str]

def atomic_claims(answer: str, llm: LLM) -> list[str]:
    prompt = f"""Break this answer into simple factual claims (one per line):
{answer}
"""
    return llm(prompt).splitlines()

def faithfulness(answer: str, context: str, llm: LLM) -> float:
    claims = atomic_claims(answer, llm)
    if not claims:
        return 0.0
    supported = 0
    for claim in claims:
        result = nli({"text": context, "text_pair": claim})[0]
        entail = next((s for s in result if s["label"] == "entailment"), None)
        if entail and entail["score"] > 0.5:
            supported += 1
    return supported / len(claims)
```

Odpowiedź jest rozkładana na atomowe twierdzenia. NLI sprawdza każde z nich względem pobranego kontekstu. Wierność to odsetek twierdzeń, które znalazły potwierdzenie.

### Krok 2: trafność odpowiedzi

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# encoder: any model implementing .encode(texts, normalize_embeddings=True) -> ndarray
# e.g., encoder = SentenceTransformer("BAAI/bge-small-en-v1.5")

def answer_relevance(question: str, answer: str, encoder, llm: LLM, n: int = 3) -> float:
    prompt = f"Write {n} questions this answer could be the answer to:\n{answer}"
    generated = [line for line in llm(prompt).splitlines() if line.strip()][:n]
    if not generated:
        return 0.0
    q_emb = np.asarray(encoder.encode([question], normalize_embeddings=True)[0])
    g_embs = np.asarray(encoder.encode(generated, normalize_embeddings=True))
    sims = [float(q_emb @ g_emb) for g_emb in g_embs]
    return sum(sims) / len(sims)
```

Jeśli odpowiedź sugeruje inne pytania niż to, które zadano, trafność maleje.

### Krok 3: niestandardowe metryki G-Eval

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams, LLMTestCase

metric = GEval(
    name="Correctness",
    criteria="The answer should be factually accurate and match the expected output.",
    evaluation_steps=[
        "Read the expected output.",
        "Read the actual output.",
        "List factual claims in the actual output.",
        "For each claim, mark supported or unsupported by the expected output.",
        "Return score = fraction supported.",
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
)

test = LLMTestCase(input="When was the first iPhone released?",
                   actual_output="June 29th, 2007.",
                   expected_output="June 29, 2007.")
metric.measure(test)
print(metric.score, metric.reason)
```

Etapy oceny tworzą rubrykę. Jawnie zdefiniowane kroki są bardziej stabilne niż ukryte podpowiedzi z poleceniem „zwróć wynik 0–1".

### Krok 4: brama CI

```python
import deepeval
from deepeval.metrics import FaithfulnessMetric, ContextualRelevancyMetric

def test_rag_system():
    cases = load_regression_cases()
    faith = FaithfulnessMetric(threshold=0.85)
    rel = ContextualRelevancyMetric(threshold=0.7)
    for case in cases:
        faith.measure(case)
        assert faith.score >= 0.85, f"faithfulness regression on {case.id}"
        rel.measure(case)
        assert rel.score >= 0.7, f"relevancy regression on {case.id}"
```

Zapisz jako plik pytest. Uruchamiaj przy każdym pull requeście. Brama blokuje scalenie w razie wykrycia regresji.

### Krok 5: uproszczona ocena od zera

Patrz `code/main.py`. Przybliżenia oparte wyłącznie na bibliotece standardowej: wierność (pokrycie twierdzeń odpowiedzi przez kontekst) i trafność (pokrycie tokenów odpowiedzi przez tokeny pytania). Nie nadaje się do produkcji — ilustruje jedynie ogólną strukturę.

## Pułapki

- **Brak kalibracji.** Ocena z korelacją 0,3 względem ludzkich etykiet to czysty szum. Kalibracja musi poprzedzać wdrożenie.
- **Samoocena.** Używanie tego samego LLM do generowania i oceniania zawyża wyniki o 10–20%. Do roli sędziego wybierz model z innej rodziny.
- **Stronniczość pozycyjna przy ocenianiu parami.** Sędziowie preferują opcję przedstawioną jako pierwsza. Zawsze losuj kolejność i uruchamiaj oba warianty.
- **Agregat maskuje awarie.** Średni wynik 0,85 często ukrywa 5% katastrofalnych błędów. Zawsze analizuj dolny kwantyl rozkładu.
- **Złoty zbiór danych.** Niewersjowane zbiory ewaluacyjne, które zmieniają się w czasie, uniemożliwiają porównania podłużne. Oznaczaj zbiór danych przy każdej modyfikacji.
- **Koszt LLM.** W dużej skali koszty oceny mogą dominować nad innymi wydatkami. Używaj najtańszego modelu spełniającego próg kalibracji: GPT-4o-mini, Claude Haiku, Mistral Small.

## Zastosowania

Zalecany stos na 2026 rok:

| Przypadek użycia | Framework |
|--------|-----------|
| Monitorowanie jakości RAG | RAGAS (4 metryki) |
| Bramy regresji CI/CD | DeepEval + pytest |
| Niestandardowe kryteria domenowe | G-Eval w DeepEval |
| Monitorowanie ruchu produkcyjnego na żywo | RAGAS w trybie bez referencji |
| Przeglądy z udziałem człowieka w pętli | LangSmith lub Phoenix z interfejsem adnotacji |
| Testy red-team i ocena bezpieczeństwa | Promptfoo + DeepEval |

Typowy stos: RAGAS do monitorowania, DeepEval dla CI, G-Eval dla nowych wymiarów oceny. Uruchamiaj wszystkie trzy — ich rozbieżności są informacyjnie wartościowe.

## Wyślij to

Zapisz jako `outputs/skill-eval-architect.md`:

```markdown
---
name: eval-architect
description: Design an LLM evaluation plan with calibrated judge and CI gates.
version: 1.0.0
phase: 5
lesson: 27
tags: [nlp, evaluation, rag]
---

Given a use case (RAG / agent / generative task), output:

1. Metrics. Faithfulness / relevance / context-precision / context-recall + any custom G-Eval metrics with criteria.
2. Judge model. Named model + version, rationale for cost vs accuracy.
3. Calibration. Hand-labeled set size, target Spearman rho vs human > 0.7.
4. Dataset versioning. Tag strategy, change log, stratification.
5. CI gate. Thresholds per metric, regression-window logic, bottom-quantile alert.

Refuse to rely on a judge untested against ≥50 human-labeled examples. Refuse self-evaluation (same model generates + judges). Refuse aggregate-only reporting without bottom-10% surfacing. Flag any pipeline where judge upgrade lands without parallel baseline eval.
```

## Ćwiczenia

1. **Łatwe.** Użyj RAGAS na 10 przykładach RAG ze znanymi halucynacjami. Sprawdź, czy metryka wierności wykrywa każdą z nich.
2. **Średnie.** Ręcznie oznacz 50 odpowiedzi QA wartościami 0–1 dla poprawności. Oceń je za pomocą G-Eval. Zmierz współczynnik rho Spearmana między sędzią a człowiekiem.
3. **Trudne.** Zbuduj bramę CI za pomocą DeepEval. Celowo zepsuj moduł pobierający. Sprawdź, czy brama zablokuje scalenie. Dodaj alerty dla dolnego kwantyla, kontrolując próg dla najsłabszych 10% wyników.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Właściwe znaczenie |
|------|-----------------|----------------------|
| LLM jako sędzia | Punktowanie przez model | Polecenie modelowi-sędzi oceny wyników 0–1 według zadanej rubryki. |
| RAGAS | Biblioteka metryk RAG | Platforma ewaluacyjna open source z 4 metrykami RAG niewymagającymi referencji. |
| Wierność | Czy odpowiedź jest uzasadniona? | Odsetek twierdzeń w odpowiedzi potwierdzonych przez pobrany kontekst. |
| Precyzja kontekstu | Czy pobrane fragmenty były trafne? | Odsetek fragmentów z górnej części rankingu, które faktycznie były istotne. |
| Kompletność kontekstu | Czy wyszukiwanie znalazło wszystko? | Odsetek twierdzeń ze złotej odpowiedzi potwierdzonych przez pobrane fragmenty. |
| G-Eval | Niestandardowy sędzia LLM | Rubryka + etapy oceny łańcucha myślenia + wynik 0–1. |
| Kalibracja | Ufaj, ale sprawdzaj | Korelacja Spearmana między oceną sędziego a oceną człowieka. |

## Dalsze czytanie

- [Es i in. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — artykuł RAGAS.
- [Liu i in. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634) — artykuł G-Eval.
- [Dokumentacja DeepEval](https://deepeval.com/docs/metrics-introduction) — otwarty stos produkcyjny.
- [Zheng i in. (2023). Sędziowanie LLM-as-a-Judge za pomocą MT-Bench i Chatbot Arena](https://arxiv.org/abs/2306.05685) — błędy systematyczne, kalibracja, ograniczenia.
- [MLflow GenAI Scorer](https://mlflow.org/blog/ Third-party-scorers) — ujednolicający framework integrujący RAGAS, DeepEval, Phoenix.
