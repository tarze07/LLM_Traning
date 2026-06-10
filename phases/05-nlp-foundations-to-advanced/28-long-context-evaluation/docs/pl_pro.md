# Ocena długokontekstowa — NIAH, RULER, LongBench, MRCR

> Gemini 3 Pro reklamuje 10 milionów tokenów kontekstu. Przy 1M tokenów ośmioigłowy MRCR spada do 26,3%. Reklamowane ≠ użyteczne. Ocena długokontekstowa pokazuje rzeczywistą pojemność modelu, z którego korzystasz.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (odpowiadanie na pytania), faza 5 · 23 (strategie podziału tekstu na fragmenty)
**Czas:** ~60 minut

## Problem

Masz 200-stronicową umowę. Model deklaruje okno kontekstu wynoszące 1M tokenów. Wklejasz umowę i pytasz: „Jaka jest klauzula wypowiedzenia?" Model odpowiada — ale odpowiedź pochodzi ze strony tytułowej, bo klauzula zakończenia leży na głębokości 120 tys. tokenów, poza zasięgiem faktycznej uwagi modelu.

To jest luka między deklarowanymi a rzeczywistymi możliwościami kontekstowymi w roku 2026. Specyfikacje podają 1M lub 10M. W praktyce 60–70% tej wartości nadaje się do użytku, a „użyteczność" zależy od rodzaju zadania.

- **Wyszukiwanie (pojedyncza igła w stogu siana):** niemal idealne aż do deklarowanego maksimum w modelach czołowych.
- **Wnioskowanie wieloskokowe i agregacja:** gwałtownie spada w większości modeli powyżej ~128 tys. tokenów.
- **Rozumowanie na podstawie rozproszonych faktów:** pierwsze zadanie, które zawodzi.

Ocena długokontekstowa mierzy te wymiary. W tej lekcji omówiono benchmarki, co każdy z nich faktycznie mierzy oraz jak zbudować własny test igłowy dostosowany do konkretnej dziedziny.

## Koncepcja

![NIAH, wielozadaniowy RULER, całościowy LongBench](../assets/long-context-eval.svg)

**Igła w stogu siana (NIAH, 2023).** Umieść fakt („magiczne słowo to ananas") na określonej głębokości w długim kontekście. Poproś model o jego odtworzenie. Pomiar odbywa się przez przeszukiwanie głębokości i długości. To oryginalny benchmark długokontekstowy. Czołowe modele osiągają w nim nasycenie — jest warunkiem koniecznym, ale niewystarczającym.

**RULER (Nvidia, 2024).** 13 typów zadań w 4 kategoriach: pobieranie (jeden klucz / wiele kluczy / wiele wartości), śledzenie wieloskokowe (śledzenie zmiennych), agregacja (częstotliwość wspólnych słów), kontrola jakości. Konfigurowalna długość kontekstu (od 4k do 128k+). Ujawnia modele, które nasycają NIAH, lecz zawodzą przy wieloskokowym wnioskowaniu. W edycji z 2024 r. tylko połowa spośród 17 modeli deklarujących kontekst powyżej 32 tys. tokenów utrzymała jakość na tym poziomie.

**LongBench v2 (2024).** 503 pytania wielokrotnego wyboru, konteksty od 8 tys. do 2 mln słów, sześć kategorii: pytania do pojedynczego dokumentu, pytania do wielu dokumentów, uczenie się z długiego kontekstu, długie dialogi, repozytorium kodu, długie dane strukturalne. Benchmark dla rzeczywistych zachowań modeli w długim kontekście.

**MRCR (rozdzielczość wielorundowych odniesień).** Koreferencja w dużej skali. Warianty z 8, 24 i 100 igłami. Pokazuje, ile faktów model potrafi skoordynować, zanim uwaga zacznie się degradować.

**NoLiMa.** „Nieleksykalna igła". Igła i zapytanie nie pokrywają się dosłownie — wyszukiwanie wymaga jednego kroku rozumowania semantycznego. Trudniejsze niż NIAH.

**HELMET.** Łączy wiele dokumentów i zadaje pytanie dotyczące dowolnego z nich. Testuje selektywną uwagę.

**BABIlong.** Osadza łańcuchy wnioskowania bAbI w nieistotnym materiale wypełniającym. Testuje rozumowanie w stogu siana, a nie samo wyszukiwanie.

### Co raportować

- **Deklarowane okno kontekstu.** Liczba z karty specyfikacji.
- **Efektywna długość wyszukiwania.** Próg, przy którym NIAH osiąga zadany poziom (np. 90%).
- **Efektywna długość wnioskowania.** Próg, przy którym wieloskokowe wnioskowanie lub agregacja osiągają zadany poziom.
- **Krzywa degradacji.** Dokładność w funkcji długości kontekstu, wykreślona osobno dla każdego typu zadania.

Dwie kluczowe liczby w karcie specyfikacji: skuteczność wyszukiwania i skuteczność wnioskowania. Efektywne okno wnioskowania wynosi zwykle 25–50% deklarowanej wartości.

## Zbuduj to

### Krok 1: własny NIAH dla Twojej dziedziny

Zobacz `code/main.py`. Szkielet:

```python
def build_haystack(filler_text, needle, depth_ratio, total_tokens):
    if not (0.0 <= depth_ratio <= 1.0):
        raise ValueError(f"depth_ratio must be in [0, 1], got {depth_ratio}")
    if total_tokens <= 0:
        raise ValueError(f"total_tokens must be positive, got {total_tokens}")

    filler_tokens = tokenize(filler_text)
    needle_tokens = tokenize(needle)
    if not filler_tokens:
        raise ValueError("filler_text produced no tokens")

    # Repeat filler until long enough to fill the haystack body.
    body_len = max(total_tokens - len(needle_tokens), 0)
    while len(filler_tokens) < body_len:
        filler_tokens = filler_tokens + filler_tokens
    filler_tokens = filler_tokens[:body_len]

    insert_at = min(int(body_len * depth_ratio), body_len)
    haystack = filler_tokens[:insert_at] + needle_tokens + filler_tokens[insert_at:]
    return " ".join(haystack)

def score_niah(model, haystack, question, expected):
    answer = model.complete(f"Context: {haystack}\nQ: {question}\nA:", max_tokens=50)
    return 1 if expected.lower() in answer.lower() else 0
```

Przeszukuj `depth_ratio` ∈ {0, 0,25, 0,5, 0,75, 1,0} × `total_tokens` ∈ {1k, 4k, 16k, 64k}. Narysuj mapę cieplną. To jest karta NIAH dla docelowego modelu.

### Krok 2: wariant wieloigłowy

```python
def build_multi_needle(filler, needles, total_tokens):
    depths = [0.1, 0.4, 0.7]
    chunks = [filler[:int(total_tokens * 0.1)]]
    for depth, needle in zip(depths, needles):
        chunks.append(needle)
        next_chunk = filler[int(total_tokens * depth): int(total_tokens * (depth + 0.3))]
        chunks.append(next_chunk)
    return " ".join(chunks)
```

Pytania w stylu „Jakie są trzy magiczne słowa?" wymagają odnalezienia wszystkich trzech igieł. Powodzenie przy jednej igle nie gwarantuje powodzenia przy wielu.

### Krok 3: śledzenie zmiennych wieloskokowych (w stylu RULER)

```python
haystack = """X1 = 42. ... (filler) ... X2 = X1 + 10. ... (filler) ... X3 = X2 * 2."""
question = "What is X3?"
```

Odpowiedź wymaga połączenia trzech kroków. Czołowe modele przy 128 tys. tokenów często osiągają tu zaledwie 50–70% dokładności.

### Krok 4: LongBench v2 na własnym stosie

```python
from datasets import load_dataset
longbench = load_dataset("THUDM/LongBench-v2")

def eval_model_on_longbench(model, subset="single-doc-qa"):
    tasks = [x for x in longbench["test"] if x["task"] == subset]
    correct = 0
    for x in tasks:
        answer = model.complete(x["context"] + "\n\nQ: " + x["question"], max_tokens=20)
        if normalize(answer) == normalize(x["answer"]):
            correct += 1
    return correct / len(tasks)
```

Raportuj dokładność według kategorii. Wyniki łączne maskują duże różnice między typami zadań.

## Pułapki

- **Ocena wyłącznie przez NIAH.** Zaliczenie NIAH przy 1M tokenów nic nie mówi o wieloskokowym wnioskowaniu. Zawsze uruchamiaj RULER lub własny test wieloskokowy.
- **Jednolita głębokość próbkowania.** Wiele implementacji testuje tylko głębokość 0,5. Testuj głębokości 0, 0,25, 0,5, 0,75 i 1,0 — efekt „zagubienia w środku" jest realny.
- **Leksykalne nakładanie się z materiałem wypełniającym.** Jeśli igła dzieli słowa kluczowe z wypełniaczem, wyszukiwanie staje się trywialne. Stosuj niepokrywające się igły w stylu NoLiMa.
- **Pomijanie opóźnień.** Wstępne wypełnienie kontekstu o długości 1M tokenów zajmuje 30–120 sekund. Mierz czas do pierwszego tokenu oraz dokładność.
- **Wyniki raportowane przez dostawców.** OpenAI, Google i Anthropic publikują własne benchmarki. Zawsze przeprowadzaj niezależne testy dostosowane do swojego przypadku użycia.

## Zastosuj to

Rekomendowany zestaw narzędzi na rok 2026:

| Sytuacja | Benchmark |
|----------|-----------|
| Szybka weryfikacja poprawności | Własny NIAH: 3 głębokości × 3 długości |
| Wybór modelu do produkcji | RULER (13 zadań) na docelowej długości |
| Jakość QA w rzeczywistych warunkach | Podzbiór pytań do pojedynczego dokumentu z LongBench v2 |
| Wieloskokowe wnioskowanie | BABIlong lub własne śledzenie zmiennych |
| Rozmowa i dialog | MRCR 8-igłowy na docelowej długości |
| Regresja przy aktualizacji modelu | Stały zestaw NIAH + RULER uruchamiany przy każdej nowej wersji |

Praktyczna zasada dla produkcji: nie ufaj deklarowanemu oknu kontekstu, dopóki nie przeprowadzisz NIAH oraz co najmniej jednego testu wnioskowania przy docelowej długości.

## Wyślij to

Zapisz jako `outputs/skill-long-context-eval.md`:

```markdown
---
name: long-context-eval
description: Design a long-context evaluation battery for a given model and use case.
version: 1.0.0
phase: 5
lesson: 28
tags: [nlp, long-context, evaluation]
---

Given a target model, target context length, and use case, output:

1. Tests. NIAH depth × length grid; RULER multi-hop; custom domain task.
2. Sampling. Depths 0, 0.25, 0.5, 0.75, 1.0 at each length.
3. Metrics. Retrieval pass rate; reasoning pass rate; time-to-first-token; cost-per-query.
4. Cutoff. Effective retrieval length (90% pass) and effective reasoning length (70% pass). Report both.
5. Regression. Fixed harness, rerun on every model upgrade, surface deltas.

Refuse to trust a context window from the model card alone. Refuse NIAH-only evaluation for any multi-hop workload. Refuse vendor self-reported long-context scores as independent evidence.
```

## Ćwiczenia

1. **Łatwe.** Zbuduj NIAH z 3 głębokościami (0,25, 0,5, 0,75) × 3 długościami (1k, 4k, 16k). Uruchom na dowolnym modelu. Wykreśl współczynnik trafień jako mapę cieplną 3×3.
2. **Średnie.** Dodaj wariant z 3 igłami. Zmierz skuteczność odtworzenia wszystkich trzech na każdej długości. Porównaj z wynikami dla pojedynczej igły przy tych samych długościach.
3. **Trudne.** Zbuduj zadanie śledzenia zmiennych (X1 → X2 → X3, trzy skoki) osadzone w 64 tys. tokenów materiału wypełniającego. Zmierz dokładność na trzech czołowych modelach. Podaj efektywną długość wnioskowania dla każdego z nich.

## Kluczowe terminy

| Termin | Potoczne określenie | Znaczenie |
|------|-----------------|----------------------|
| NIAH | Igła w stogu siana | Umieść fakt w materiale wypełniającym i poproś model o jego odtworzenie. |
| RULER | NIAH na sterydach | 13 typów zadań: pobieranie / wieloskokowe wnioskowanie / agregacja / kontrola jakości. |
| Efektywny kontekst | Rzeczywista pojemność | Długość, przy której dokładność utrzymuje się powyżej zadanego progu. |
| Zagubiony w środku | Odchylenie głębokości | Modele ignorują treść znajdującą się w środku długich danych wejściowych. |
| Wieloigłowy | Wiele faktów naraz | Wiele igieł; testuje zarządzanie uwagą, a nie samo wyszukiwanie. |
| MRCR | Wielorundowa koreferencja | Koreferencja 8, 24 lub 100 igieł; ujawnia nasycenie uwagi. |
| NoLiMa | Nieleksykalna igła | Igła i zapytanie nie mają wspólnych tokenów; wymagane jest wnioskowanie semantyczne. |

## Dalsze czytanie

- [Kamradt (2023). Analiza igły w stogu siana](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — oryginalne repozytorium NIAH.
- [Hsieh i in. (2024). RULER: Jaki jest rzeczywisty rozmiar kontekstu Twoich długokontekstowych modeli językowych?](https://arxiv.org/abs/2404.06654) — wielozadaniowy benchmark.
- [Bai i in. (2024). LongBench v2](https://arxiv.org/abs/2412.15204) — ocena długiego kontekstu w rzeczywistych warunkach.
- [Modarressi i in. (2024). NoLiMa: Nieleksykalne igły](https://arxiv.org/abs/2404.06666) — trudniejsze igły.
- [Kuratov i in. (2024). BABIlong](https://arxiv.org/abs/2406.10149) — wnioskowanie w stogu siana.
- [Liu i in. (2024). Zagubiony w środku: jak modele językowe korzystają z długich kontekstów](https://arxiv.org/abs/2307.03172) — artykuł o efekcie głębokości.
