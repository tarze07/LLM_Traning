# Ocena LLM — RAGAS, DeepEval, G-Eval

> Dokładne dopasowanie i F1 tracą równoważność semantyczną. Przegląd ręczny nie podlega skali. Rozwiązaniem w zakresie produkcji jest LLM-as-sędzia — z wystarczającą kalibracją, aby ufać liczbom.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (odpowiadanie na pytania), faza 5 · 14 (wyszukiwanie informacji)
**Czas:** ~75 minut

## Problem

Twój system RAG odpowiada: „29 czerwca 2007”.
Złote odniesienie to: „29 czerwca 2007”.
Wynik Dokładnego Dopasowania wynosi 0. Wynik F1 wynosi ~75%. Człowiek uzyskałby 100%.

Teraz pomnóż przez 10 000 przypadków testowych. Pomnóż ponownie przez każdą zmianę w aporterze, porcjowaniu, podpowiedzi lub modelu. Potrzebujesz osoby oceniającej, która rozumie znaczenie, działa tanio i na dużą skalę, nie kłamie na temat regresji i wskazuje odpowiednie tryby awarii.

Rok 2026 ma trzy ramy, w których występuje ten problem.

- **RAGAS.** Ocena generacji rozszerzonej z wyszukiwaniem. Cztery wskaźniki RAG (wierność, trafność odpowiedzi, precyzja kontekstu, przypomnienie kontekstu) z zapleczem NLI + LLM-sędzia. Potwierdzone badaniami, lekkie.
- **DeepEval.** Pytest dla LLM. G-Eval, wykonanie zadania, halucynacje, wskaźniki uprzedzeń. Natywny dla CI/CD.
- **G-Eval.** Metoda (i metryka DeepEval): LLM-jako-sędzia z niestandardowymi kryteriami na podstawie łańcucha myślowego, wynik 0-1.

Cała trójka opiera się na LLM jako sędzia. Ta lekcja buduje intuicję dotyczącą metody i warstwy zaufania wokół niej.

## Koncepcja

![Cztery wymiary oceny, architektura LLM-as-judge](../assets/llm-evaluation.svg)

**LLM-jako-sędzia.** Zastąp metrykę statyczną LLM, która ocenia wyniki w danej rubryce. Biorąc pod uwagę `(query, context, answer)`, powiedz sędziemu LLM: „Ocena 0-1 za wierność”. Zwróć wynik.

Dlaczego to działa: LLM przybliżają ludzką ocenę za niewielki ułamek kosztów. GPT-4o-mini w ~$0.003 per scored case enables 1000-sample regression eval runs for under $5.

Dlaczego po cichu kończy się niepowodzeniem:

1. **Uprzedzenie sędziego.** Sędziowie wolą dłuższe odpowiedzi, odpowiedzi z własnej rodziny modeli, odpowiedzi pasujące do stylu podpowiedzi.
2. **Błędy analizowania JSON.** Zły JSON → Wynik NaN → dyskretnie wykluczony z agregatu. Użytkownicy RAGAS znają ten ból. Brama z try/except + jawnym trybem awarii.
3. **Pomiń wersje modeli.** Aktualizacja sędziego zmienia każdą metrykę. Zablokuj model oceny + wersję.

**Czwórka RAG.**

| Metryczne | Pytanie | Zaplecze |
|--------|----------|--------|
| Wierność | Czy każde twierdzenie w odpowiedzi pochodzi z odzyskanego kontekstu? | Pociąganie w oparciu o NLI |
| Znaczenie odpowiedzi | Czy odpowiedź dotyczy pytania? | Generuj hipotetyczne pytania na podstawie odpowiedzi; porównaj z prawdziwym pytaniem |
| Dokładność kontekstu | Jaka część z odzyskanych fragmentów była istotna? | Sędzia LLM |
| Przypomnienie kontekstu | Czy pobranie zwróciło wszystko, co było potrzebne? | Sędzia LLM przeciwko złotej odpowiedzi |

**G-Eval.** Zdefiniuj niestandardowe kryterium: „Czy w odpowiedzi podano właściwe źródło?” Struktura automatycznie rozszerza się na etapy oceny oparte na łańcuchu myśli, a następnie uzyskuje wynik 0-1. Dobre w przypadku wymiarów jakości specyficznych dla domeny, których nie obejmuje RAGAS.

**Kalibracja.** Nigdy nie ufaj surowym wynikom sędziego, dopóki nie uzyskasz korelacji z ludzkimi etykietami. Uruchom 100 ręcznie oznakowanych przykładów. Sędzia fabuły kontra człowiek. Oblicz rho Spearmana. Jeśli rho < 0,7, rubryka sędziowska wymaga dopracowania.

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

Rozłóż odpowiedź na twierdzenia atomowe. NLI sprawdza każde roszczenie pod kątem pobranego kontekstu. Wierność = ułamek obsługiwany.

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

Jeśli odpowiedź sugeruje inne pytania niż zadane, trafność spada.

### Krok 3: Niestandardowe dane G-Eval

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

Etapy oceny stanowią rubrykę. Jawne kroki są bardziej stabilne niż ukryte podpowiedzi „wynik 0-1”.

### Krok 4: Brama CI

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

Wyślij jako plik pytest. Działaj na każdym PR. Blok łączy się podczas regresji.

### Krok 5: ocena zabawki od zera

Zobacz `code/main.py`. Przybliżenia tylko Stdlib dotyczące wierności (nakładanie się roszczeń odpowiedzi z kontekstem) i trafności (nakładanie się tokenów odpowiedzi na tokeny pytań). Nie produkcja. Pokazuje kształt.

## Pułapki

- **Brak kalibracji.** Ocena z korelacją 0,3 z ludzkimi etykietami to szum. Wymagaj przeprowadzenia kalibracji przed wysyłką.
- **Samoocena.** Korzystanie z tego samego LLM do generowania i oceniania zawyża wyniki o 10-20%. Użyj innej rodziny modeli dla sędziego.
- **Stronniczość pozycyjna przy ocenianiu w parach.** Sędziowie preferują pierwszą przedstawioną opcję. Zawsze losuj kolejność i uruchamiaj oba.
- **Surowy agregat ukrywa awarie.** Średni wynik 0,85 często kryje 5% katastrofalnych awarii. Zawsze sprawdzaj dolny kwantyl.
- **Złoty zbiór danych.** Niewersjonowane zbiory ewaluacyjne, które dryfują w czasie, przerywają porównanie podłużne. Oznacz zbiór danych przy każdej zmianie.
- **Koszt LLM.** W skali koszty dominują oceny. Użyj najtańszego modelu spełniającego próg kalibracji. GPT-4o-mini, Claude Haiku, Mistral-mały.

## Użyj tego

Stos na rok 2026:

| Przypadek użycia | Ramy |
|--------|-----------|
| Monitorowanie jakości RAG | RAGAS (4 metryki) |
| Bramki regresji CI/CD | DeepEval + pytest |
| Niestandardowe kryteria domeny | G-Eval w DeepEval |
| Monitorowanie ruchu online na żywo | RAGAS z trybem bez referencji |
| Kontrole na miejscu z udziałem człowieka w pętli | LangSmith lub Phoenix z interfejsem adnotacji |
| Zespół czerwonych / ocena bezpieczeństwa | Promptfoo + DeepEval |

Typowy stos: RAGAS do monitorowania, DeepEval dla CI, G-Eval dla nowatorskich wymiarów. Uruchom wszystkie trzy; pożytecznie się nie zgadzają.

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

1. **Łatwe.** Użyj RAGAS na 10 przykładach RAG ze znanymi halucynacjami. Sprawdź, czy metryka wierności łapie każdy z nich.
2. **Średni.** Etykieta ręczna 50 odpowiedzi QA 0-1 dla poprawności. Zdobądź punkty dzięki G-Eval. Zmierz Spearmana rho pomiędzy sędzią a człowiekiem.
3. **Trudne.** Zbuduj bramkę CI za pomocą narzędzia DeepEval. Celowo cofnij retrievera. Sprawdź, czy brama nie działa. Dodaj alerty dotyczące dolnego kwantylu poprzez kontrolę progu dla najniższych 10%.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| LLM jako sędzia | Punktacja z LLM | Poproś model sędziego o ocenę wyników 0-1 w danej rubryce. |
| RAGA | Biblioteka metryk RAG | Platforma ewaluacyjna typu open source z 4 wskaźnikami RAG bez referencji. |
| Wierność | Czy odpowiedź jest uzasadniona? | Część żądań odpowiedzi wynikających z odzyskanego kontekstu. |
| Dokładność kontekstu | Czy odzyskane fragmenty były istotne? | Część fragmentów z najwyższej półki, które faktycznie miały znaczenie. |
| Przypomnienie kontekstu | Czy funkcja pobierania znalazła wszystko? | Część roszczeń ze złotą odpowiedzią potwierdzona przez odzyskane fragmenty. |
| G-Eval | Niestandardowy sędzia LLM | Rubryka + etapy oceny łańcucha myślowego + wynik 0-1. |
| Kalibracja | Ufaj, ale sprawdzaj | Korelacja Spearmana między oceną sędziego a oceną człowieka. |

## Dalsze czytanie

- [Es i in. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — artykuł RAGAS.
- [Liu i in. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634) — artykuł G-Eval.
- [Dokumentacja DeepEval](https://deepeval.com/docs/metrics-introduction) — otwarty stos produkcyjny.
- [Zheng i in. (2023). Sędziowanie LLM-as-a-Judge za pomocą MT-Bench i Chatbot Arena](https://arxiv.org/abs/2306.05685) — błędy systematyczne, kalibracja, limity.
- [MLflow GenAI Scorer](https://mlflow.org/blog/ Third-party-scorers) — ujednolicający framework integrujący RAGAS, DeepEval, Phoenix.