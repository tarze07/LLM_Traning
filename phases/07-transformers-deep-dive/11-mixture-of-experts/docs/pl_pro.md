# Mieszanka ekspertów (MoE)

> Gęsty transformator 70B aktywuje każdy parametr dla każdego tokena. Model 671B oparty na MoE aktywuje tylko 37B parametrów na token i przewyższa go w każdym teście porównawczym. Rzadkość obliczeniowa to najważniejsza koncepcja skalowania tej dekady.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

Koszt obliczeniowy gęstego transformatora podczas wnioskowania jest wprost proporcjonalny do liczby jego parametrów (razy 2 dla przejścia w przód). Przy skalowaniu gęstego modelu każdy token ponosi pełny koszt obliczeniowy. Do 2024 roku podejście to natrafiło na ścianę: aby model był istotnie lepszy, potrzeba wykładniczo więcej operacji zmiennoprzecinkowych na token.

Mieszanka Ekspertów przerywa tę zależność. Każdą warstwę FFN zastępuje się `E` niezależnymi ekspertami oraz routerem, który wybiera `k` ekspertów na token. Łączna liczba parametrów wynosi `E × FFN_size`, natomiast liczba aktywnych parametrów na token to `k × FFN_size`. Typowa konfiguracja z 2026 roku: `E=256`, `k=8`. Pamięć skaluje się przez `E`, obliczenia przez `k`.

W 2026 roku czołówkę modeli językowych stanowią niemal wyłącznie architektury MoE: DeepSeek-V3 (671B parametrów łącznie, 37B aktywnych), Mixtral 8×22B, Qwen2.5-MoE, Llama 4, Kimi K2 oraz gpt-oss. W niezależnych rankingach wszystkie 10 najlepszych modeli open source to modele MoE.

## Koncepcja

![Warstwa MoE: router wybiera k ekspertów E na token](../assets/moe.svg)

### Zamiana FFN

Gęsty blok transformatora:

```
h = x + attn(norm(x))
h = h + FFN(norm(h))
```

Blok MoE:

```
h = x + attn(norm(x))
scores = router(norm(h))              # (N_tokens, E)
top_k = argmax_k(scores)              # pick k of E per token
h = h + sum_{e in top_k}(
        gate(scores[e]) * Expert_e(norm(h))
    )
```

Każdy ekspert jest niezależną warstwą FFN (zazwyczaj SwiGLU). Router to pojedyncza warstwa liniowa. Każdy token wybiera własnych `k` ekspertów i otrzymuje ważoną sumę ich odpowiedzi.

### Problem z równomiernym rozłożeniem obciążenia

Jeśli router kieruje 90% tokenów do eksperta nr 3, pozostali eksperci są pomijani. Opracowano trzy rozwiązania tego problemu:

1. **Pomocnicza strata równoważenia obciążenia** (Switch Transformer, Mixtral). Do funkcji straty dodaje się człon kary proporcjonalny do nierównomierności użycia ekspertów. Podejście skuteczne, lecz wprowadza dodatkowy hiperparametr i drugi sygnał gradientu.
2. **Pojemność eksperta z pomijaniem tokenów** (wczesne warianty Switch). Każdy ekspert przetwarza co najwyżej `C × N/E` tokenów; nadmiarowe tokeny omijają warstwę. Rozwiązanie to obniża jakość.
3. **Pomocnicze równoważenie bez dodatkowej straty** (DeepSeek-V3). Do każdego eksperta dodaje się wyuczony parametr odchylenia, który wpływa na wybór top-k w routerze. Odchylenie jest aktualizowane poza główną funkcją straty, nie zaburzając treningu. To najważniejszy przełom roku 2024.

Mechanizm DeepSeek-V3: po każdym kroku treningowym sprawdzane jest, czy użycie każdego eksperta jest powyżej czy poniżej wartości docelowej. Odchylenie jest korygowane o ±γ. Routing używa wartości `scores + bias`, natomiast wagi bramkowe do agregacji wyników ekspertów obliczane są na podstawie oryginalnych wartości `scores`. Dzięki temu routing i wyrażenie modelu są od siebie oddzielone.

### Eksperci współdzieleni

W modelach DeepSeek-V2 i V3 eksperci zostali podzieleni na *współdzielonych* i *kierowanych*. Każdy token przechodzi przez wszystkich ekspertów współdzielonych bez względu na routing. Eksperci kierowani są wybierani przez mechanizm top-k. Eksperci współdzieleni gromadzą wiedzę ogólną, eksperci kierowani — specjalizują się. Model V3 wykorzystuje 1 eksperta współdzielonego oraz 8 najlepszych spośród 256 ekspertów kierowanych.

### Drobnoziarniste MoE

Klasyczne MoE (GShard, Switch): każdy ekspert ma rozmiar równy pełnej warstwie FFN. `E` jest małe (8–64), `k` też małe (1–2).

Nowoczesne drobnoziarniste MoE (DeepSeek-V3, Qwen-MoE): każdy ekspert jest węższy (rozmiar 1/8 pełnego FFN). `E` jest duże (256 lub więcej), `k` większe (8 lub więcej). Przy tej samej łącznej liczbie parametrów liczba możliwych kombinacji ekspertów rośnie znacznie szybciej: `C(256, 8) = 400 bilionów` możliwych zestawów ekspertów na token. Jakość modelu rośnie, a opóźnienie pozostaje bez zmian.

### Profil kosztów

Na token, na warstwę:

| Konfiguracja | Aktywne parametry / token | Łącznie parametrów |
|------------|----------------------|------------|
| Mixtral 8×22B | ~39B | 141B |
| Llama 3 70B (gęsty) | 70B | 70B |
| DeepSeek-V3 | 37B | 671B |
| Kimi K2 (MoE) | ~32B | 1T |

DeepSeek-V3 przewyższa Llamę 3 70B w niemal każdym teście porównawczym, wykonując **mniej aktywnych operacji zmiennoprzecinkowych na token**. Większa liczba parametrów oznacza więcej zgromadzonej wiedzy, większa liczba aktywnych operacji — więcej obliczeń na token. Architektura MoE pozwala te dwa wymiary rozdzielić.

### Koszt: pamięć

Wszyscy eksperci muszą rezydować w pamięci GPU niezależnie od tego, którzy są aktywni. Model 671B wymaga około 1,3 TB pamięci VRAM dla wag w formacie fp16. Wdrożenie zaawansowanych modeli MoE wymaga specjalistycznej równoległości — poszczególnych ekspertów przypisanych do różnych kart graficznych z routingiem tokenów przez sieć. Opóźnienie jest zdominowane przez komunikację „wszyscy do wszystkich", a nie przez mnożenie macierzy.

## Zbuduj to

Zobacz `code/main.py`. Zwarta warstwa MoE zaimplementowana w czystym Pythonie (bez zewnętrznych bibliotek):

- `n_experts=8` ekspertów w stylu SwiGLU (dla uproszczenia — jeden liniowy na eksperta)
- routing top-k=2
- znormalizowane wagi bramkowe (softmax)
- pomocnicze równoważenie bez dodatkowej straty — przez odchylenie per-ekspert

### Krok 1: router

```python
def route(hidden, W_router, top_k, bias):
    scores = [sum(h * w for h, w in zip(hidden, W_router[e])) for e in range(len(W_router))]
    biased = [s + b for s, b in zip(scores, bias)]
    top_idx = sorted(range(len(biased)), key=lambda i: -biased[i])[:top_k]
    # softmax over ORIGINAL scores of the chosen experts
    chosen = [scores[i] for i in top_idx]
    m = max(chosen)
    exps = [math.exp(c - m) for c in chosen]
    s = sum(exps)
    gates = [e / s for e in exps]
    return top_idx, gates
```

Odchylenie wpływa na wybór eksperta, ale nie na wartość wagi bramkowej. Na tym polega mechanizm DeepSeek-V3 — odchylenie koryguje nierównomierność obciążenia bez wpływu na przewidywania modelu.

### Krok 2: uruchom 100 tokenów przez router

Śledź, którzy eksperci są wybierani i jak często. Bez odchyleń użycie jest nierównomierne. Po zastosowaniu pętli aktualizacji odchyleń (`-γ` dla ekspertów nadmiernie używanych, `+γ` dla pomijanych) rozkład obciążenia wyrównuje się w ciągu kilku iteracji.

### Krok 3: porównanie liczby parametrów

Wydrukuj „gęsty odpowiednik" danej konfiguracji MoE. Dla kształtu DeepSeek-V3 (256 ekspertów kierowanych + 1 współdzielony, 8 aktywnych, d_model=7168) łączna liczba parametrów jest imponująca, a liczba aktywnych stanowi jedną siódmą Llamy 3 70B.

## Użyj tego

Ładowanie z Hugging Face:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x22B-v0.1")
```

Wnioskowanie produkcyjne w 2026 roku: vLLM obsługuje routing MoE natywnie. SGLang oferuje najszybszą ścieżkę z równoległością ekspercką. Oba rozwiązania automatycznie obsługują wybór top-k i równoległość ekspercką.

**Kiedy wybrać MoE:**
- Zależy ci na najwyższej jakości przy niższym koszcie wnioskowania na token.
- Masz odpowiednią infrastrukturę (VRAM, równoległość ekspercka).
- Twoje zadania wymagają przetwarzania wielu tokenów (czat, kod), a nie długich kontekstów.

**Kiedy NIE wybierać MoE:**
- Wdrożenie brzegowe — płacisz za pamięć wszystkich parametrów niezależnie od aktywacji.
- Obsługa jednego użytkownika z rygorystycznym wymogiem niskich opóźnień — routing ekspercki zwiększa narzut.
- Małe modele (poniżej 7B) — przewaga jakościowa MoE ujawnia się dopiero powyżej pewnego progu obliczeniowego (około 6B aktywnych parametrów).

## Wyślij to

Zobacz `outputs/skill-moe-configurator.md`. Narzędzie dobiera wartości E, k oraz układ ekspertów współdzielonych dla nowego modelu MoE, uwzględniając budżet parametrów, liczbę tokenów treningowych i wymagania wdrożeniowe.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Obserwuj, jak pomocnicza aktualizacja odchylenia bez dodatkowej straty wyrównuje użycie ekspertów w ciągu 50 iteracji.
2. **Średnie.** Zastąp wyuczony router routerem opartym na haszowaniu (deterministycznym, bez uczenia). Porównaj jakość i równomierność obciążenia. Dlaczego wyuczony router daje lepsze wyniki?
3. **Trudne.** Zaimplementuj „routing dopasowany do wdrożenia" wzorowany na GRPO (technika DeepSeek-V3.2): rejestruj, którzy eksperci są aktywowani podczas wnioskowania, a następnie wymuszaj ten sam routing przy obliczaniu gradientu. Zmierz wpływ na gradient polityki w uproszczonej konfiguracji.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Ekspert | „Jeden FFN spośród wielu" | Niezależna sieć w przód; parametry przypisane do rzadko aktywowanego fragmentu obliczeń FFN. |
| Router | „Brama" | Mała warstwa liniowa oceniająca każdy token względem każdego eksperta i wybierająca top-k. |
| Routing top-k | „k aktywnych ekspertów na token" | Obliczenia FFN każdego tokena przechodzą przez dokładnie k ekspertów, ważonych wagami bramkowymi. |
| Strata pomocnicza | „Kara za nierównomierne obciążenie" | Dodatkowy człon funkcji straty, który karze za nierównomierne użycie ekspertów. |
| Pomocnicze bez straty | „Sztuczka DeepSeek-V3" | Równoważenie obciążenia przez odchylenie per-ekspert, wpływające wyłącznie na wybór w routerze, bez dodatkowego gradientu. |
| Ekspert współdzielony | „Zawsze aktywny" | Dodatkowy ekspert, przez który przechodzi każdy token; gromadzi wiedzę ogólną. |
| Równoległość ekspercka | „Fragmentacja ekspertów" | Przypisanie różnych ekspertów do różnych kart graficznych z routingiem tokenów przez sieć. |
| Rzadkość | „Aktywne parametry < łączne parametry" | Stosunek `k × expert_size / (E × expert_size)`; dla DeepSeek-V3 wynosi 37/671 ≈ 5,5%. |

## Dalsze czytanie

- [Shazeer i in. (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) — pierwotny pomysł.
- [Fedus, Zoph, Shazeer (2022). Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961) — Switch, klasyczny MoE.
- [Jiang i in. (2024). Mixtral of Experts](https://arxiv.org/abs/2401.04088) — Mixtral 8×7B.
- [DeepSeek-AI (2024). DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437) — MLA + pomocnicze MoE bez straty + MTP.
- [Wang i in. (2024). Auxiliary-Loss-Free Load Balancing Strategy for Mixture of Experts](https://arxiv.org/abs/2408.15664) — artykuł o równoważeniu opartym na odchyleniu.
- [Dai i in. (2024). DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models](https://arxiv.org/abs/2401.06066) — drobnoziarnisty podział ekspercki i eksperci współdzieleni, z których korzysta router omówiony w tej lekcji.
- [Kim i in. (2022). DeepSpeed-MoE: Advancing Mixture-of-Experts Inference and Training](https://arxiv.org/abs/2201.05596) — artykuł wprowadzający równoległość ekspercką.
