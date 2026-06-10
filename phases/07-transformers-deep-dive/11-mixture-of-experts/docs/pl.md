# Mieszanka ekspertów (MoE)

> Gęsty transformator 70B aktywuje każdy parametr dla każdego tokena. 671B MoE aktywuje tylko 37B na token i pobija go w każdym benchmarku. Sparsity to najważniejsza koncepcja skalowania tej dekady.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

Wartość FLOP gęstego transformatora przy wnioskowaniu jest równa liczbie jego parametrów (razy 2 dla przejścia w przód). Skaluj gęsty model, a każdy token opłaci pełny rachunek. Do 2024 r. granica uderzyła w ścianę obliczeniową: aby być znacząco mądrzejszym, potrzeba wykładniczo większej liczby FLOPów na token.

Mieszanka Ekspertów przerywa to połączenie. Zastąp każdego FFN niezależnymi ekspertami `E` + routerem, który wybiera ekspertów `k` na token. Łączna liczba parametrów = `E × FFN_size`. Aktywne parametry na token = `k × FFN_size`. Typowa konfiguracja 2026: `E=256`, `k=8`. Skalowanie pamięci za pomocą `E`, skalowanie obliczeń za pomocą `k`.

Granica roku 2026 to prawie w całości MoE: DeepSeek-V3 (łącznie 671B / 37B aktywnych), Mixtral 8×22B, Qwen2.5-MoE, Llama 4, Kimi K2, gpt-oss. W niezależnej tabeli wyników sztucznej analizy wszystkie 10 najlepszych modeli open source to MoE.

## Koncepcja

![Warstwa MoE: router wybiera k ekspertów E na token](../assets/moe.svg)

### Zamiana FFN

Gęsty blok transformatora:

```
h = x + attn(norm(x))
h = h + FFN(norm(h))
```

Blok MO:

```
h = x + attn(norm(x))
scores = router(norm(h))              # (N_tokens, E)
top_k = argmax_k(scores)              # pick k of E per token
h = h + sum_{e in top_k}(
        gate(scores[e]) * Expert_e(norm(h))
    )
```

Każdy ekspert jest niezależnym FFN (zazwyczaj SwiGLU). Router jest pojedynczą warstwą liniową. Każdy token wybiera własnych `k` ekspertów i otrzymuje bramkowaną mieszankę ich wyników.

### Problem z równoważeniem obciążenia

Jeśli router przepuści 90% tokenów przez eksperta 3, pozostali eksperci umrą z głodu. Wypróbowano trzy poprawki:

1. **Utrata równoważenia obciążenia pomocniczego** (transformator przełączający, Mixtral). Dodaj karę proporcjonalną do zróżnicowania wykorzystania przez eksperta. Działa, ale dodaje hiperparametr i drugi sygnał gradientu.
2. **Pojemność eksperta + zrzucanie tokenów** (wczesna zmiana). Każdy ekspert przetwarza maksymalnie `C × N/E` tokenów; Żetony przepełnienia pomijają warstwę. Boli jakość.
3. **Pomocnicze równoważenie bez strat** (DeepSeek-V3). Dodaj wyuczone nastawienie na eksperta, które zmienia wybór górnego k routera. Odchylenie jest aktualizowane poza utratą treningu. Brak kary za główny cel. Największe odblokowanie roku 2024.

Podejście DeepSeek-V3: po każdym etapie szkolenia dla każdego eksperta sprawdź, czy jego użycie jest powyżej, czy poniżej wartości docelowej. Zmień stronniczość, stosując `±γ`. Wybór wykorzystuje `scores + bias`. Prawdopodobieństwa eksperckie stosowane do bramkowania pozostają `scores` niezmienione. Oddziela routing od wyrażenia.

### Wspólni eksperci

DeepSeek-V2/V3 również podzielił ekspertów na *współdzielonych* i *kierowanych*. Każdy token przechodzi przez wszystkich wspólnych ekspertów. Eksperci kierowani są wybierani przez górne-k. Wspólni eksperci zdobywają wspólną wiedzę; specjalizują się przenoszeni eksperci. V3 obsługuje 1 wspólnego eksperta oraz 8 najlepszych z 256 tras.

### Drobni eksperci

Klasyczny MoE (GShard, Switch): każdy ekspert jest tak szeroki jak pełny FFN. `E` jest mały (8–64), `k` jest mały (1–2).

Nowoczesne drobnoziarniste MoE (DeepSeek-V3, Qwen-MoE): każdy ekspert jest węższy (rozmiar 1/8 FFN). `E` jest duży (256+), `k` jest większy (8+). Te same parametry całkowite, ale kombinacje skalują się znacznie szybciej. `C(256, 8) = 400 trillion` możliwych „ekspertów” na token. Jakość wzrasta, opóźnienia pozostają niezmienne.

### Profil kosztów

Na token, na warstwę:

| Konfiguracja | Aktywne parametry / token | Razem parametry |
|------------|----------------------|------------|
| Mieszany 8×22B | ~39B | 141B |
| Lama 3 70B (gęsta) | 70B | 70B |
| DeepSeek-V3 | 37B | 671B |
| Kimi K2 (MoE) | ~32B | 1T |

DeepSeek-V3 pokonuje Llamę 3 70B (gęsty) w prawie każdym benchmarku, wykonując **mniej aktywnych FLOPów na token**. Więcej parametrów = więcej wiedzy. Więcej aktywnych FLOPów = więcej obliczeń na token. Ministerstwo Środowiska je oddziela.

### Haczyk: pamięć

Wszyscy eksperci żyją na GPU, niezależnie od tego, który z nich odpala. Model 671B potrzebuje ~1,3 TB pamięci VRAM dla ciężarów fp16. Wdrożenie Frontier MoE wymaga specjalistycznej równoległości — ekspertów od fragmentów na różnych procesorach graficznych, trasowania tokenów w sieci. Opóźnienie jest zdominowane przez komunikację „wszyscy do wszystkich”, a nie matmul.

## Zbuduj to

Zobacz `code/main.py`. Kompaktowa warstwa MoE w czystej bibliotece stdlib z:

- `n_experts=8` Eksperci w stylu SwiGLU (dla ilustracji po jednym liniowym)
- routing top-k=2
- znormalizowane wagi bramkowe typu softmax
- pomocnicze równoważenie bezstratne poprzez nastawienie per-ekspert

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

Odchylenie wpływa na wybór, a nie na wagę bramki. Na tym polega sztuczka DeepSeek-V3 — błąd koryguje nierównowagę obciążenia bez sterowania przewidywaniami modelu.

### Krok 2: uruchom 100 tokenów przez router

Śledź, którzy eksperci zwalniają, jak często. Bez uprzedzeń użycie jest wypaczone. Dzięki pętli aktualizacji odchyleń (`-γ` w przypadku nadmiernie wykorzystywanych ekspertów, `+γ` w przypadku niedostatecznie wykorzystywanych) użycie zbiega się do równomiernego rozkładu w ciągu kilku iteracji.

### Krok 3: porównanie liczby parametrów

Wydrukuj „gęsty odpowiednik” konfiguracji MoE. W kształcie DeepSeek-V3: 256 trasowanych + 1 współdzielonych, 8 aktywnych, d_model=7168. Całkowita liczba parametrów jest oszałamiająca. Aktywna liczba to siódma część gęstej Lamy 3 70B.

## Użyj tego

Ładowanie twarzy:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x22B-v0.1")
```

Wnioskowanie produkcyjne na rok 2026: vLLM obsługuje natywnie routing MoE. SGLang ma najszybszą ścieżkę ekspercko-równoległą. Obydwa automatycznie obsługują wybór górnego k i ekspercką równoległość.

**Kiedy wybrać MoE:**
- Chcesz granicznej jakości przy niższym koszcie wnioskowania na token.
- Masz infrastrukturę VRAM / ekspercko-równoległą.
- Twoje obciążenie pracą wymaga dużej ilości symboli (czat, kod), a nie kontekstu (długie dokumenty).

**Kiedy NIE wybierać MoE:**
- Wdrożenie brzegowe — płacisz pełne miejsce za każdy aktywny FLOP.
— Obsługa pojedynczego użytkownika z krytycznym opóźnieniem — routing ekspercki zwiększa obciążenie.
- Małe modele (<7B) — przewaga jakościowa MoE pojawia się jedynie powyżej progu obliczeniowego (~6B aktywnych parametrów).

## Wyślij to

Zobacz `outputs/skill-moe-configurator.md`. Umiejętność wybiera E, k i układ współdzielonego eksperta dla nowego MoE, biorąc pod uwagę budżet parametrów, tokeny szkoleniowe i cel wdrożenia.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Zobacz, jak pomocnicza, pozbawiona strat aktualizacja odchylenia wyrównuje wykorzystanie przez ekspertów w ciągu 50 iteracji.
2. **Średni.** Wymień wyuczony router na router oparty na mieszaniu (deterministyczny, bez uczenia). Porównaj jakość i równowagę. Dlaczego wyuczony router jest lepszy?
3. **Trudne.** Zaimplementuj „routing dopasowany do wdrożenia” w stylu GRPO (sztuczka DeepSeek-V3.2): log, który eksperci uruchamiają podczas wnioskowania, wymusza ten sam routing podczas obliczania gradientu. Zmierz wpływ na konfigurację gradientu zasad zabawek.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Ekspert | „Jeden FFN spośród wielu” | Niezależna sieć wyprzedzająca; parametry przeznaczone dla rzadkiego wycinka obliczeń FFN. |
| routera | „Brama” | Mała warstwa liniowa, która ocenia każdy żeton względem każdego eksperta; wybór górnego k. |
| Routing górny-k | „k aktywnych ekspertów na token” | Obliczenie FFN każdego tokena przechodzi przez dokładnie k ekspertów, ważonych według bramki. |
| Strata pomocnicza | „Kara za równowagę obciążenia” | Termin dodatkowej straty, który karze za niewłaściwe użycie przez ekspertów. |
| Pomocniczy bezstratny | „Sztuczka DeepSeek-V3” | Zrównoważenie poprzez nastawienie eksperta wyłącznie na temat wyboru routera; bez dodatkowego gradientu. |
| Wspólny ekspert | „Zawsze włączone” | Dodatkowy ekspert, przez który przechodzi każdy token; chwyta powszechną wiedzę. |
| Równoległość ekspercka | „Odłamek eksperta” | Przydziel różnych ekspertów do różnych procesorów graficznych; tokeny trasy w sieci. |
| Rzadkość | „Aktywne parametry < całkowite parametry” | Stosunek `k × expert_size / (E × expert_size)`; 37/671 ≈ 5,5% dla DeepSeek-V3. |

## Dalsze czytanie

- [Shazeer i in. (2017). Skandalicznie duże sieci neuronowe: słabo bramkowana warstwa mieszanki ekspertów](https://arxiv.org/abs/1701.06538) — pomysł.
- [Fedus, Zoph, Shazeer (2022). Transformator przełączający: skalowanie do modeli o bilionach parametrów przy użyciu prostej i wydajnej rzadkości](https://arxiv.org/abs/2101.03961) — Switch, klasyczny MoE.
- [Jiang i in. (2024). Mixtral Ekspertów](https://arxiv.org/abs/2401.04088) — Mixtral 8×7B.
- [DeepSeek-AI (2024). Raport techniczny DeepSeek-V3](https://arxiv.org/abs/2412.19437) — MLA + pomocnicze MoE bez strat + MTP.
- [Wang i in. (2024). Pomocnicza strategia równoważenia obciążenia bez strat dla mieszanki ekspertów](https://arxiv.org/abs/2408.15664) — dokument równoważący oparty na uprzedzeniach.
- [Dai i in. (2024). DeepSeekMoE: Ku ostatecznej specjalizacji eksperckiej w modelach językowych składających się z mieszanki ekspertów](https://arxiv.org/abs/2401.06066) — drobnoziarnisty i współdzielony podział ekspercki, z którego korzysta router w tej lekcji.
- [Kim i in. (2022). DeepSpeed-MoE: Advancing Mixture-of-Experts Inference and Training](https://arxiv.org/abs/2201.05596) — oryginalny artykuł udostępniony przez ekspertów.