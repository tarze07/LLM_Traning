# Ocena długokontekstowa — NIAH, RULER, LongBench, MRCR

> Gemini 3 Pro reklamuje 10 milionów tokenów kontekstu. Przy żetonach 1M 8-igłowy MRCR spada do 26,3%. Reklamowane ≠ nadające się do użytku. Ocena długokontekstowa informuje o rzeczywistej pojemności modelu, na którym wysyłasz.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (odpowiadanie na pytania), faza 5 · 23 (strategie dzielenia na części)
**Czas:** ~60 minut

## Problem

Masz 200-stronicową umowę. Model twierdzi, że kontekst tokenu 1M. Wklejasz umowę i pytasz: „Jaka jest klauzula wypowiedzenia?” Model odpowiada — ale odpowiada ze strony tytułowej, ponieważ klauzula zakończenia znajduje się na głębokości 120 tys. tokenów, poza miejscem, w którym faktycznie uczestniczy model.

Jest to luka w zakresie możliwości kontekstowych w roku 2026. W specyfikacjach podano 1M lub 10M. Rzeczywistość mówi, że 60-70% z tego nadaje się do użytku, a „użyteczność” zależy od zadania.

- **Odzyskiwanie (pojedyncza igła w stogu siana):** prawie idealne aż do reklamowanego maksimum w modelach pionierskich.
- **Multi-hop / agregacja:** w większości modeli gwałtownie spada powyżej ~128 tys.
- **Rozumowanie na podstawie rozproszonych faktów:** pierwsze zadanie, które się nie powiodło.

Ocena długokontekstowa mierzy te osie. W tej lekcji wymieniono testy porównawcze, co faktycznie mierzy każdy z nich i jak zbudować niestandardowy test igłowy dla Twojej domeny.

## Koncepcja

![NIAH, wielozadaniowy RULER, całościowy LongBench](../assets/long-context-eval.svg)

**Igła w stogu siana (NIAH, 2023).** Umieść fakt („magiczne słowo to ananas”) na kontrolowanej głębokości w długim kontekście. Poproś modelkę o jego odzyskanie. Głębokość przemiatania × długość. Oryginalny benchmark o długim kontekście. Modele graniczne teraz to nasycają; jest to konieczny, ale niewystarczający punkt odniesienia.

**RULER (Nvidia, 2024).** 13 typów zadań w 4 kategoriach: pobieranie (pojedynczy / wiele kluczy / wiele wartości), śledzenie wielu przeskoków (śledzenie zmiennych), agregacja (częstotliwość słów wspólnych), kontrola jakości. Konfigurowalna długość kontekstu (4k do 128k+). Ujawnia modele, które nasycają NIAH, ale zawodzą w trybie multi-hop. W wersji z 2024 r. tylko połowa z 17 modeli twierdzących, że kontekst przekracza 32 tys., zachowała jakość na poziomie 32 tys.

**LongBench v2 (2024).** 503 pytania wielokrotnego wyboru, konteksty słów od 8 tys. do 2 mln słów, sześć kategorii zadań: kontrola jakości w jednym dokumencie, kontrola jakości w wielu dokumentach, długie uczenie się w kontekście, długie dialogi, repozytorium kodu, długie dane strukturalne. Tester porównawczy dla zachowań w długim kontekście w świecie rzeczywistym.

**MRCR (rozdzielczość wielorundowego odniesienia).** Wieloobrotowa korelacja w dużej skali. Warianty 8-igłowe, 24-igłowe i 100-igłowe. Pokazuje, ile faktów model może pogodzić, zanim uwaga ulegnie pogorszeniu.

**NoLiMa.** „Igła nieleksykalna”. Igła i zapytanie nie pokrywają się dosłownie; wyszukiwanie wymaga jednego kroku rozumowania semantycznego. Trudniejsze niż NIAH.

**HELMET.** Łączy wiele dokumentów, zadaje pytanie któremukolwiek z nich. Testuje uwagę selektywną.

**BABIlong.** Osadza łańcuchy rozumowania bAbI w nieistotnych stogach siana. Testuje rozumowanie w stogu siana, a nie tylko wyszukiwanie.

### Co właściwie zgłosić

- **Okno kontekstowe reklamowane.** Numer arkusza specyfikacji.
- **Efektywna długość wyszukiwania.** NIAH przechodzi przy pewnym progu (np. 90%).
- **Efektywna długość wnioskowania.** Przeskok wielokrotny lub agregacja przy tym progu.
- **Krzywa degradacji.** Dokładność w funkcji długości kontekstu, wykreślona według typu zadania.

Dwie liczby w arkuszu specyfikacji: skuteczność wyszukiwania i skuteczność rozumowania. Zwykle rozumowanie efektywne wynosi 25-50% reklamowanego okna.

## Zbuduj to

### Krok 1: niestandardowy NIAH dla Twojej domeny

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

Przeciągnięcie `depth_ratio` ∈ {0, 0,25, 0,5, 0,75, 1,0} × `total_tokens` ∈ {1k, 4k, 16k, 64k}. Narysuj mapę cieplną. To jest karta NIAH dla Twojego docelowego modelu.

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

Pytania typu „Jakie są trzy magiczne słowa?” wymagają pobrania wszystkich trzech. Sukces przy użyciu jednej igły nie oznacza sukcesu przy użyciu wielu igieł.

### Krok 3: śledzenie zmiennych z wieloma przeskokami (w stylu RULER)

```python
haystack = """X1 = 42. ... (filler) ... X2 = X1 + 10. ... (filler) ... X3 = X2 * 2."""
question = "What is X3?"
```

Odpowiedź wymaga połączenia trzech zadań. Modele frontierowe przy rozdzielczości 128 tys. często spadają tutaj do 50–70% dokładności.

### Krok 4: LongBench v2 na stosie

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

Raportuj dokładność według kategorii. Łączne wyniki ukrywają duże różnice na poziomie zadań.

## Pułapki

- **Ewaluacja tylko NIAH.** Przekazanie NIAH przy 1 milionie tokenów nie mówi nic o multi-hopie. Zawsze uruchamiaj RULER lub niestandardowy test wielu przeskoków.
- **Jednolita głębokość próbkowania.** Wiele implementacji testuje tylko głębokość = 0,5. Głębokość testu=0, 0,25, 0,5, 0,75, 1,0 — efekt „zagubienia w środku” jest realny.
- **Leksykalne nakładanie się na wypełniacz.** Jeśli igła ma wspólne słowa kluczowe z wypełniaczem, wyszukiwanie staje się banalne. Używaj niezachodzących na siebie igieł typu NoLiMa.
- **Ignorowanie opóźnień.** Wstępne wypełnienie monitów o token 1M zajmuje 30–120 sekund. Mierz czas do pierwszego żetonu i dokładność.
- **Liczby zgłaszane przez dostawców.** OpenAI, Google i Anthropic publikują własne wyniki. Zawsze uruchamiaj ponownie niezależnie od przypadku użycia.

## Użyj tego

Stos na rok 2026:

| Sytuacja | punkt odniesienia |
|----------|-----------|
| Szybka kontrola zdrowego rozsądku | Niestandardowy NIAH na 3 głębokościach × 3 długościach |
| Wybór modelu do produkcji | LINIA (13 zadań) na docelowej długości |
| Jakość QA w świecie rzeczywistym | Podzbiór kontroli jakości pojedynczego dokumentu LongBench v2 |
| Rozumowanie wieloprzeskokowe | BABILong lub niestandardowe śledzenie zmiennych |
| Rozmowa / dialog | Igła MRCR 8 na docelowej długości |
| Regresja aktualizacji modelu | Naprawiono uprząż NIAH + RULER, działającą na każdym nowym modelu |

Praktyczna zasada dotycząca produkcji: nigdy nie ufaj oknu kontekstowemu, dopóki nie wykonasz zadania wnioskowania NIAH + 1 o zamierzonej długości.

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

1. **Łatwe.** Zbuduj NIAH z 3 głębokościami (0,25, 0,5, 0,75) × 3 długościami (1k, 4k, 16k). Uruchom na dowolnym modelu. Wykreśl współczynnik przepustowości jako mapę cieplną 3×3.
2. **Średni.** Dodaj wariant z 3 igłami. Zmierz pobieranie wszystkich 3 na każdej długości. Porównaj z szybkością przejścia pojedynczej igły przy tej samej długości.
3. **Trudne.** Skonstruuj zadanie polegające na śledzeniu zmiennych (X1 → X2 → X3, z 3 przeskokami) osadzone w 64 tys. wypełniacza. Zmierz dokładność w 3 pionierskich modelach. Zgłaszaj efektywną długość wnioskowania dla każdego modelu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| NIAH | Igła w stogu siana | Umieść fakt w wypełniaczu i poproś modelkę o jego odzyskanie. |
| WŁADCA | NIAH na sterydach | 13 typów zadań w zakresie pobierania / wielu przeskoków / agregacji / kontroli jakości. |
| Efektywny kontekst | Prawdziwa pojemność | Długość, przy której dokładność nadal utrzymuje się powyżej progu. |
| Zagubiony w środku | Odchylenie głębokości | Modele nie zwracają uwagi na treść w środku długich danych wejściowych. |
| Wieloigłowe | Wiele faktów na raz | Wiele roślin; testuje żonglowanie uwagą, a nie samo odzyskiwanie. |
| MRCR | Rdzeń wielorundowy | Koreferencja 8, 24 lub 100 igieł; eksponuje nasycenie uwagi. |
| NoLiMa | Igła nieleksykalna | Igła i zapytanie nie mają wspólnych tokenów dosłownych; wymaga rozumowania. |

## Dalsze czytanie

- [Kamradta (2023). Analiza igły w stogu siana](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — oryginalne repozytorium NIAH.
- [Hsieh i in. (2024). WŁADCA: Jaki jest rzeczywisty rozmiar kontekstu Twoich LM o długim kontekście?](https://arxiv.org/abs/2404.06654) — wielozadaniowy test porównawczy.
- [Bai i in. (2024). LongBench v2](https://arxiv.org/abs/2412.15204) — ewaluacja w długim kontekście w świecie rzeczywistym.
- [Modarressi i in. (2024). NoLiMa: Igły nieleksykalne](https://arxiv.org/abs/2404.06666) — igły twardsze.
- [Kuratov i in. (2024). BABILong](https://arxiv.org/abs/2406.10149) — rozumowanie-w-stóg siana.
- [Liu i in. (2024). Zagubiony w środku: jak modele językowe używają długich kontekstów](https://arxiv.org/abs/2307.03172) — artykuł na temat głębi.