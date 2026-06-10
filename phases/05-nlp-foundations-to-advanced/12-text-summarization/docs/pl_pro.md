# Podsumowanie tekstu

> Systemy ekstrakcyjne przekazują informacje zawarte w dokumencie. Systemy abstrakcyjne oddają to, co autor miał na myśli. Różne zadania, różne pułapki.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 11 (tłumaczenie maszynowe)
**Czas:** ~75 minut

## Problem

Artykuł informacyjny liczący 2000 słów trafia do Twojego kanału. Potrzebujesz 120 słów, które uchwycą jego treść. Możesz wybrać trzy najważniejsze zdania z artykułu (ekstrakcja) lub przepisać treść własnymi słowami (abstrakcja). Oba podejścia nazywa się podsumowaniem, lecz są to zupełnie różne problemy.

Podsumowanie ekstrakcyjne to problem rankingowy. Oceń każde zdanie i zwróć `k` najlepszych. Wynik jest zawsze poprawny gramatycznie, ponieważ pochodzi dosłownie ze źródła. Istnieje jednak ryzyko pominięcia treści rozproszonych po całym artykule.

Podsumowanie abstrakcyjne to problem generatywny. Model transformatorowy wytwarza nowy tekst na podstawie danych wejściowych. Wynik jest płynny i skompresowany, ale może zawierać fakty nieobecne w źródle — ryzyko polega na możliwości sfabrykowania informacji.

Ta lekcja buduje oba podejścia i omawia charakterystyczne dla każdego z nich tryby awarii.

## Koncepcja

![Ekstrakcyjny TextRank vs abstrakcyjny transformator](../assets/summarization.svg)

**Ekstrakcja.** Potraktuj artykuł jak graf, w którym węzły to zdania, a krawędzie reprezentują podobieństwo między nimi. Zastosuj PageRank (lub podobny algorytm) na grafie, aby ocenić zdania według ich powiązania z pozostałymi. Zdania z najwyższą punktacją tworzą podsumowanie. Kanoniczną implementacją jest **TextRank** (Mihalcea i Tarau, 2004).

**Abstrakcja.** Dostrojenie kodera-dekodera transformatorowego (BART, T5, Pegasus) na parach dokument-podsumowanie. Podczas wnioskowania model odczytuje dokument i generuje podsumowanie token po tokenie z wykorzystaniem mechanizmu wzajemnej uwagi. Warto zaznaczyć, że Pegasus stosuje cel wstępnego trenowania oparty na zdaniach z lukami, co czyni go szczególnie skutecznym w zadaniach streszczania bez dodatkowego dostrajania.

Ocena za pomocą **ROUGE** (Recall-Oriented Understudy for Gisting Evaluation). ROUGE-1 i ROUGE-2 mierzą pokrycie unigramów i bigramów. ROUGE-L wyznacza najdłuższy wspólny podciąg. Wyższy wynik jest lepszy — 40 ROUGE-L uznaje się za „dobre", a 50 za „wyjątkowe". Większość publikacji naukowych podaje wszystkie trzy wartości. Używaj pakietu `rouge-score`.

## Zbuduj to

### Krok 1: TextRank (ekstrakcyjny)

```python
import math
import re
from collections import Counter

def sentence_split(text):
    return re.split(r"(?<=[.!?])\s+", text.strip())

def similarity(s1, s2):
    w1 = Counter(s1.lower().split())
    w2 = Counter(s2.lower().split())
    intersection = sum((w1 & w2).values())
    denom = math.log(len(w1) + 1) + math.log(len(w2) + 1)
    if denom == 0:
        return 0.0
    return intersection / denom

def textrank(text, top_k=3, damping=0.85, iterations=50, epsilon=1e-4):
    sentences = sentence_split(text)
    n = len(sentences)
    if n <= top_k:
        return sentences

    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                sim[i][j] = similarity(sentences[i], sentences[j])

    scores = [1.0] * n
    for _ in range(iterations):
        new_scores = [1 - damping] * n
        for i in range(n):
            total_out = sum(sim[i]) or 1e-9
            for j in range(n):
                if sim[i][j] > 0:
                    new_scores[j] += damping * sim[i][j] / total_out * scores[i]
        if max(abs(s - ns) for s, ns in zip(scores, new_scores)) < epsilon:
            scores = new_scores
            break
        scores = new_scores

    ranked = sorted(range(n), key=lambda k: scores[k], reverse=True)[:top_k]
    ranked.sort()
    return [sentences[i] for i in ranked]
```

Dwie kwestie warte omówienia. Funkcja podobieństwa używa logarytmicznie znormalizowanego pokrycia słów — jest to oryginalny wariant TextRank. Alternatywnie można zastosować cosinus wektorów TF-IDF. Domyślne parametry PageRank to współczynnik tłumienia 0,85 i określona liczba iteracji.

### Krok 2: abstrakcja z BARTEM

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """(long news article text)"""

summary = summarizer(article, max_length=120, min_length=60, do_sample=False)
print(summary[0]["summary_text"])
```

BART-large-CNN jest dostrojony na korpusie CNN/DailyMail. Generuje gotowe podsumowania w stylu dziennikarskim. W przypadku innych dziedzin (artykuły naukowe, dialogi, teksty prawne) należy użyć odpowiedniego punktu kontrolnego Pegasus lub dostroić model na danych docelowych.

### Krok 3: Ocena ROUGE

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
scores = scorer.score(reference_summary, generated_summary)
print({k: round(v.fmeasure, 3) for k, v in scores.items()})
```

Zawsze używaj stemmingu. Bez niego wyrazy „bieganie" i „biegnąć" są traktowane jako różne słowa, co zaniża wyniki ROUGE.

### Beyond ROUGE (ocena podsumowania w 2026 roku)

ROUGE przez dwadzieścia lat dominował jako główna metryka ewaluacji podsumowań, jednak w 2026 roku sam w sobie już nie wystarcza. Zakrojona na szeroką skalę metaanaliza artykułów z dziedziny NLG wykazała, że:

- **BERTScore** (podobieństwo oparte na osadzeniach kontekstowych) zyskał na popularności w 2023 roku i jest obecnie podawany obok ROUGE w większości prac dotyczących podsumowań.
- **BARTScore** traktuje ocenę jako zadanie generatywne: podsumowanie jest oceniane na podstawie prawdopodobieństwa przypisanego mu przez wytrenowany BART z uwzględnieniem źródła.
- **MoverScore** (odległość Earth Mover w przestrzeni osadzeń kontekstowych) osiągnął najlepsze wyniki w testach porównawczych z 2025 roku, ponieważ lepiej oddaje semantyczne pokrycie treści niż ROUGE.
- **FactCC** i metody wierności oparte na pytaniach kontrolnych były powszechne w latach 2021–2023. Dziś często zastępuje je **G-Eval** — podejście oparte na łańcuchu podpowiedzi GPT-4, które ocenia spójność, zgodność ze źródłem, płynność i trafność z wykorzystaniem rozumowania krok po kroku.
- **G-Eval** i podobne metody oparte na sędziach LLM osiągają zgodność z oceną ludzką na poziomie ~80%, gdy rubryki oceny są dobrze zaprojektowane.

Zalecenie produkcyjne: raportuj ROUGE-L dla porównania z wcześniejszymi wersjami, BERTScore dla pokrycia semantycznego oraz G-Eval dla spójności i rzetelności faktograficznej. Kalibruj metryki na 50–100 podsumowaniach opatrzonych etykietami ludzkimi.

### Krok 4: problem z faktami

Abstrakcyjne streszczenia są podatne na halucynacje. Streszczenia ekstrakcyjne niosą znacznie mniejsze ryzyko, ponieważ wynik pochodzi dosłownie ze źródła — choć mogą wprowadzać w błąd, gdy zdania są wyrwane z kontekstu, nieaktualne lub przytoczone w niewłaściwej kolejności. To główny powód, dla którego systemy produkcyjne w obszarach regulowanych nadal preferują podejście ekstrakcyjne.

Typowe rodzaje halucynacji:

- **Zamiana podmiotów.** Źródło podaje „John Smith". Podsumowanie zawiera „John Brown".
- **Błąd liczbowy.** Źródło podaje „25 000". Podsumowanie mówi „25 milionów".
- **Odwrócenie znaczenia.** Źródło stwierdza, że „odrzucono ofertę". Podsumowanie twierdzi, że „ofertę przyjęto".
- **Zmyślony fakt.** Źródło nie wspomina o dyrektorze generalnym. Podsumowanie przypisuje mu zatwierdzenie decyzji.

Metody ewaluacji wierności faktograficznej:

- **FactCC.** Binarny klasyfikator wytrenowany na relacjach między zdaniami źródłowymi a zdaniami podsumowania. Przewiduje, czy dane zdanie jest zgodne z faktami.
- **Wierność oparta na pytaniach kontrolnych.** Model pytań i odpowiedzi jest pytany o informacje obecne w źródle. Jeśli podsumowanie zawiera inne odpowiedzi, zdanie jest flagowane.
- **F1 na poziomie jednostek nazwanych.** Porównuje jednostki nazwane w źródle i podsumowaniu. Podmioty obecne wyłącznie w podsumowaniu są podejrzane.

We wszystkich zastosowaniach skierowanych do użytkowników, gdzie liczy się rzetelność faktograficzna (wiadomości, medycyna, prawo, finanse), ekstrakcja jest bezpieczniejszym rozwiązaniem domyślnym. Abstrakcja wymaga weryfikacji faktów w pętli.

## Użyj tego

Zestawienie na 2026 rok:

| Przypadek użycia | Polecane |
|--------|------------|
| Wiadomości, podsumowanie 3-5 zdań, angielski | `facebook/bart-large-cnn` |
| Artykuły naukowe | `google/pegasus-pubmed` lub dostrojony T5 |
| Wielodokumentowe, długie | Dowolny LLM z oknem kontekstowym powyżej 32 tys. tokenów, podawany przez prompt |
| Podsumowanie dialogu | `philschmid/bart-large-cnn-samsum` |
| Ekstrakcyjne, niskie ryzyko halucynacji ze względu na konstrukcję | TextRank lub LSA / LexRank `sumy` |

W 2026 roku modele LLM z długim kontekstem często przewyższają wyspecjalizowane modele, gdy moc obliczeniowa nie jest ograniczeniem. Kompromisem są koszty i powtarzalność — wyspecjalizowane modele dają bardziej spójne wyniki.

## Wyślij to

Zapisz jako `outputs/skill-summary-picker.md`:

```markdown
---
name: summary-picker
description: Pick extractive or abstractive, named library, factuality check.
version: 1.0.0
phase: 5
lesson: 12
tags: [nlp, summarization]
---

Given a task (document type, compliance requirement, length, compute budget), output:

1. Approach. Extractive or abstractive. Explain in one sentence why.
2. Starting model / library. Name it. `sumy.TextRankSummarizer`, `facebook/bart-large-cnn`, `google/pegasus-pubmed`, or an LLM prompt.
3. Evaluation plan. ROUGE-1, ROUGE-2, ROUGE-L (use rouge-score with stemming). Plus factuality check if abstractive.
4. One failure mode to probe. Entity swap is the most common in abstractive news summarization; flag samples where source entities do not appear in summary.

Refuse abstractive summarization for medical, legal, financial, or regulated content without a factuality gate. Flag input over the model's context window as needing chunked map-reduce summarization (not just truncation).
```

## Ćwiczenia

1. **Łatwe.** Uruchom TextRank na 5 artykułach prasowych. Porównaj 3 najwyżej ocenione zdania z podsumowaniem referencyjnym. Zmierz ROUGE-L. W artykułach w stylu CNN/DailyMail powinieneś uzyskać wartości z zakresu 30–45 ROUGE-L.
2. **Średni.** Zaimplementuj ocenę wierności na poziomie jednostek nazwanych: wyodrębnij podmioty ze źródła i podsumowania (spaCy), oblicz recall podmiotów źródłowych w podsumowaniu oraz precyzję podmiotów podsumowania względem źródła. Wysoka precyzja przy niskim recall oznacza bezpieczeństwo kosztem zwięzłości; niska precyzja sygnalizuje halucynowane podmioty.
3. **Trudne.** Porównaj BART-large-CNN z wybranym LLM (Claude lub GPT-4) na 50 artykułach CNN/DailyMail. Zgłoś ROUGE-L, wierność faktograficzną (według F1 podmiotów) oraz koszt jednostkowy podsumowania. Udokumentuj przypadki, w których każde podejście wypada lepiej.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Ekstrakcyjne | Wybierz zdania | Zwróć zdania dosłownie ze źródła. Halucynacje wykluczone. |
| Abstrakcyjne | Przepisz | Wygeneruj nowy tekst na podstawie źródła. Możliwe halucynacje. |
| ROUGE | Metryka podsumowania | Pokrycie N-gramów/NWP między wyjściem systemu a wartością referencyjną. |
| TextRank | Ekstrakcja oparta na grafie | PageRank na grafie podobieństwa zdań. |
| Wierność faktograficzna | Czy to prawda | Czy twierdzenia w podsumowaniu są poparte przez źródło. |
| Halucynacja | Zmyślona treść | Treść podsumowania nieobecna w źródle ani przez nie nieuzasadniona. |

## Dalsze czytanie

- [Mihalcea i Tarau (2004). TextRank: Uporządkowanie tekstów](https://aclanthology.org/W04-3252/) — kanoniczna praca o ekstrakcji.
- [Lewis i in. (2019). BART: Denoising Sequence-to-Sequence Pre-training](https://arxiv.org/abs/1910.13461) — artykuł opisujący BART.
- [Zhang i in. (2019). PEGASUS: Trening wstępny z wyodrębnionymi zdaniami z lukami](https://arxiv.org/abs/1912.08777) — Pegasus i cel uczenia oparty na zdaniach z lukami.
- [Lin (2004). ROUGE: Pakiet do automatycznej oceny podsumowań](https://aclanthology.org/W04-1013/) — artykuł opisujący ROUGE.
- [Maynez i in. (2020). O wierności i faktyczności w podsumowaniach abstrakcyjnych](https://arxiv.org/abs/2005.00661) — przegląd metod oceny wierności faktograficznej.
