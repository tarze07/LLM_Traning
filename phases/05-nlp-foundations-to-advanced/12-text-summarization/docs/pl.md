# Podsumowanie tekstu

> Systemy ekstrakcyjne przekazują informacje zawarte w dokumencie. Systemy abstrakcyjne mówią, co autor miał na myśli. Różne zadania, różne pułapki.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 11 (tłumaczenie maszynowe)
**Czas:** ~75 minut

## Problem

Artykuł informacyjny zawierający 2000 słów ląduje w Twoim kanale. Potrzebujesz 120 słów, które to oddają. Możesz wybrać trzy najważniejsze zdania z artykułu (wyciąg) lub przepisać treść własnymi słowami (wyciąg). Obydwa nazywane są podsumowaniem. To zupełnie różne problemy.

Ekstrakcyjne podsumowanie jest problemem rankingowym. Oceń każde zdanie, zwróć górny-`k`. Wynik jest zawsze gramatyczny, ponieważ jest podnoszony dosłownie. Istnieje ryzyko braku treści rozproszonych po całym artykule.

Abstrakcyjne podsumowanie jest problemem pokoleniowym. Transformator wytwarza nowy tekst uzależniony od sygnału wejściowego. Materiał wyjściowy jest płynny i skompresowany, ale może przywodzić na myśl fakty, których nie było w źródle. Ryzyko polega na pewnym sfabrykowaniu.

Ta lekcja buduje jedno i drugie, z trybem awarii, który każdy posiada.

## Koncepcja

![Ekstrakcyjny TextRank vs abstrakcyjny transformator](../assets/summarization.svg)

**Wyciąg.** Potraktuj artykuł jak wykres, którego węzły to zdania, a krawędzie to podobieństwa. Przeprowadź PageRank (lub coś w tym stylu) na wykresie, aby ocenić zdania na podstawie ich powiązania ze wszystkim innym. Zdania z najwyższą liczbą punktów stanowią podsumowanie. Kanoniczną implementacją jest **TextRank** (Mihalcea i Tarau, 2004).

**Streszczenie.** Dostrojenie kodera-dekodera transformatorowego (BART, T5, Pegasus) w parach dokument-podsumowanie. Podczas wnioskowania model odczytuje dokument i generuje podsumowanie token po tokenie za pomocą wzajemnej uwagi. W szczególności Pegasus wykorzystuje cel wstępnego szkolenia z przerwami, co czyni go doskonałym narzędziem do podsumowań bez większego dostrajania.

Ocena za pomocą **ROUGE** (badania zorientowanego na wycofanie w zakresie oceny istotności). ROUGE-1 i ROUGE-2 nakładają się na unigram i bigram. ROUGE-L wyznacza najdłuższy wspólny podciąg. Wyższa jest lepsza, ale 40 ROUGE-L jest „dobre”, a 50 jest „wyjątkowe”. Każda gazeta opisuje wszystkie trzy. Użyj pakietu `rouge-score`.

## Zbuduj to

### Krok 1: TextRank (wyodrębniający)

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

Dwie rzeczy warte nazwania. Funkcja podobieństwa wykorzystuje znormalizowane logarytmicznie nakładanie się słów, co jest oryginalnym wariantem TextRank. Cosinus wektorów TF-IDF również działa. Domyślnymi ustawieniami PageRank są współczynnik tłumienia 0,85 i liczba iteracji.

### Krok 2: abstrakcja z BARTEM

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """(long news article text)"""

summary = summarizer(article, max_length=120, min_length=60, do_sample=False)
print(summary[0]["summary_text"])
```

BART-large-CNN jest dostosowany do korpusu CNN/DailyMail. Tworzy gotowe podsumowania w stylu wiadomości. W przypadku innych domen (artykuły naukowe, dialogi, kwestie prawne) użyj odpowiedniego punktu kontrolnego Pegasus lub dostosuj dane docelowe.

### Krok 3: Ocena ROUGE

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
scores = scorer.score(reference_summary, generated_summary)
print({k: round(v.fmeasure, 3) for k, v in scores.items()})
```

Zawsze używaj stemplowania. Bez tego „bieganie” i „bieganie” liczą się jako różne słowa, a ROUGE jest zaniżone.

### Beyond ROUGE (ocena podsumowująca rok 2026)

ROUGE jest dominującym miernikiem podsumowującym od dwudziestu lat i sam w sobie nie wystarczy w roku 2026. Zakrojona na szeroką skalę metaanaliza artykułów NLG wykazała:

- **BERTScore** (podobieństwo osadzania kontekstowego) zyskało na popularności w 2023 r. i obecnie jest podawane obok ROUGE w większości artykułów podsumowujących.
- **BARTScore** traktuje ocenę jako generowanie: oceniaj podsumowanie na podstawie prawdopodobieństwa przypisania go przez przeszkolony BART, biorąc pod uwagę źródło.
- **MoverScore** (odległość Earth Mover w osadzaniu kontekstowym) osiągnął pierwsze miejsce w testach porównawczych podsumowań za rok 2025, ponieważ lepiej oddaje nakładanie się semantyki niż ROUGE.
- **FactCC** i **wierność oparta na kontroli jakości** były powszechne w latach 2021–2023, obecnie często zastępowane przez **G-Eval** (łańcuch podpowiedzi GPT-4, który ocenia spójność, zgodność, płynność i trafność z rozumowaniem opartym na łańcuchu myślowym).
- **G-Eval** i podobne podejścia oparte na sędziach LLM odpowiadają ludzkiej ocenie w ~80% przypadków, gdy rubryki są dobrze zaprojektowane.

Zalecenie produkcyjne: raport ROUGE-L dla porównania starszej wersji, BERTScore dla nakładania się semantyki, G-Eval dla spójności i rzeczowości. Kalibracja na podstawie 50–100 podsumowań opatrzonych etykietami ludzi.

### Krok 4: problem z faktami

Abstrakcyjne streszczenia są podatne na halucynacje. Ekstrakcyjne streszczenia niosą ze sobą znacznie mniejsze ryzyko halucynacji, ponieważ wynik jest dosłownie pobierany ze źródła, chociaż nadal mogą wprowadzać w błąd, jeśli zdania źródłowe zostaną wyrwane z kontekstu, nieaktualne lub cytowane w niewłaściwej kolejności. Jest to najważniejszy powód, dla którego systemy produkcyjne nadal preferują metody wyodrębniania treści zgodnych z przepisami.

Rodzaje halucynacji, aby wymienić:

- **Zamiana jednostek.** Źródło podaje „John Smith”. Podsumowanie brzmi: „John Brown”.
- **Odchylenie liczbowe.** Źródło podaje „25 000”. Podsumowanie mówi „25 milionów”.
- **Odwrócenie polaryzacji.** Źródło twierdzi, że „odrzuciło ofertę”. Podsumowanie mówi „zaakceptowałem ofertę”.
- **Fakt zmyślony.** Źródło nie wspomina o dyrektorze generalnym. Podsumowanie mówi, że dyrektor generalny wyraził zgodę.

Podejścia do ewaluacji, które działają:

- **FactCC.** Klasyfikator binarny przeszkolony w zakresie powiązań między zdaniem źródłowym a zdaniem podsumowującym. Przewiduje fakty/nie fakty.
- **Fakty oparte na kontroli jakości.** Zadawaj pytania w ramach modelu kontroli jakości, na które odpowiedzi znajdują się w źródle. Jeżeli w podsumowaniu znajdują się różne odpowiedzi, zaznacz.
- **Poziom jednostki F1.** Porównaj nazwane jednostki w źródle i podsumowaniu. Podmioty obecne jedynie w podsumowaniu są podejrzane.

W przypadku wszystkiego, co dotyczy użytkownika, gdzie liczy się fakty (wiadomości, medycyna, prawo, finanse), ekstrakcja jest bezpieczniejszym rozwiązaniem domyślnym. Streszczenie wymaga sprawdzenia faktów w pętli.

## Użyj tego

Stos na rok 2026:

| Przypadek użycia | Polecane |
|--------|------------|
| Wiadomości, podsumowanie 3-5 zdań, angielski | `facebook/bart-large-cnn` |
| Artykuły naukowe | `google/pegasus-pubmed` lub dostrojony T5 |
| Wielodokumentowe, długie | Dowolny LLM z kontekstem ponad 32 tys., wyświetli się monit |
| Podsumowanie dialogu | `philschmid/bart-large-cnn-samsum` |
| Ekstrakcyjne, niskie ryzyko halucynacji ze względu na konstrukcję | TextRank lub LSA / LexRank `sumy` |

LLM z długim kontekstem często pokonują wyspecjalizowane modele w 2026 r., gdy obliczenia nie stanowią ograniczenia. Kompromisem są koszty i powtarzalność; wyspecjalizowane modele dają bardziej spójne wyniki.

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

1. **Łatwe.** Uruchom TextRank dla 5 artykułów prasowych. Porównaj 3 najważniejsze zdania z podsumowaniem referencyjnym. Zmierz ROUGE-L. Powinieneś zobaczyć 30-45 ROUGE-L w artykułach w stylu CNN/DailyMail.
2. **Średni.** Wdrażaj faktyczność na poziomie jednostki: wyodrębniaj nazwane jednostki ze źródła i podsumowania (spaCy), obliczaj odwołanie jednostek źródłowych w podsumowaniu i precyzję jednostek podsumowujących w stosunku do źródła. Wysoka precyzja i niska pamięć oznaczają bezpieczeństwo, ale zwięzłość; niska precyzja oznacza istoty halucynacyjne.
3. **Trudne.** Porównaj BART-large-CNN z LLM (Claude lub GPT-4) w 50 artykułach CNN/DailyMail. Zgłoś ROUGE-L, stan faktyczny (według podmiotu F1) i koszt podsumowania. Dokumentuj, gdzie każdy wygrywa.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Ekstrakcyjne | Wybierz zdania | Zwróć zdania dosłownie ze źródła. Nigdy nie ma halucynacji. |
| Abstrakcyjne | Przepisz | Wygeneruj nowy tekst uzależniony od źródła. Może mieć halucynacje. |
| RÓŻ | Metryka podsumowująca | Nakładanie się N-gramów/LCS pomiędzy wyjściem systemu a wartością odniesienia. |
| TekstRank | Ekstrakcja oparta na wykresach | PageRank na wykresie podobieństwa zdań. |
| Rzeczywistość | Czy to prawda | Czy twierdzenia podsumowujące są poparte przez źródło. |
| Halucynacja | Zmyślona treść | Treść podsumowania, której źródło nie obsługuje. |

## Dalsze czytanie

- [Mihalcea i Tarau (2004). TextRank: Uporządkowanie tekstów](https://aclanthology.org/W04-3252/) — ekstraktywna praca kanoniczna.
- [Lewis i in. (2019). BART: Denoising Sequence-to-Sequence Pre-training](https://arxiv.org/abs/1910.13461) — artykuł BART.
- [Zhang i in. (2019). PEGASUS: Trening wstępny z wyodrębnionymi zdaniami z lukami](https://arxiv.org/abs/1912.08777) — Pegasus i cel dotyczący zdań z lukami.
- [Lin (2004). ROUGE: Pakiet do automatycznej oceny podsumowań](https://aclanthology.org/W04-1013/) — artykuł ROUGE.
- [Maynez i in. (2020). O wierności i faktyczności w podsumowaniach abstrakcyjnych] (https://arxiv.org/abs/2005.00661) — dokument przedstawiający przegląd faktów.