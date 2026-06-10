# Gradientowy punkt kontrolny i ponowne obliczenie aktywacji

> Backprop zatrzymuje każdą pośrednią aktywację. Przy parametrach 70B i kontekście 128K, czyli 3 TB aktywacji na rangę. Checkpointing zamienia FLOPy na pamięć: przeliczaj zamiast zapisywać. Pytanie brzmi, które segmenty porzucić, a odpowiedź nie brzmi „wszystkie”.

**Typ:** Kompilacja
**Języki:** Python (z numpy, opcjonalna latarka)
**Wymagania wstępne:** Faza 10, lekcja 04 (przedszkoleniowy Mini-GPT), faza 10, lekcja 05 (skalowanie i dystrybucja)
**Czas:** ~70 minut

## Problem

Uczenie transformatora przechowuje dla każdej warstwy dane wejściowe do każdej operacji różnicowanej wstecz: wejścia uwagi, projekcje Q/K/V, wyjście softmax, wejścia FFN, wyjścia norm i strumień resztkowy. W przypadku warstwy o ukrytym rozmiarze `d`, długości sekwencji `L`, partii `B`, jest to rząd `12 * B * L * d` pływających na warstwę.

Dla `d=8192, L=8192, B=1` oznacza to 800 MB/warstwę w BF16. Model 64-warstwowy to 51 GB aktywacji — i to zanim pomnożysz przez rozmiar mikropartii, zanim dodasz produkty pośrednie typu uwaga-softmax (`L^2` na głowicę) i zanim uwzględnisz częściowe kopie tensorowo-równoległe.

Rachunek dwustronny: wagi BF16 plus stan optymalizatora mogą zmieścić się w 80 GB, ale aktywacje popychają cię do przodu. Gradientowe punkty kontrolne (czyli ponowne obliczanie aktywacji) to standardowe rozwiązanie. Porzuć większość aktywacji; powtórz ruch do przodu podczas cofania, aby je odzyskać. Koszt: dodatkowe FLOPy. Korzyści: pamięć spada o stosunek segmentów punktów kontrolnych do całkowitej liczby warstw.

Wykonywane naiwnie, punkty kontrolne kosztują około 33% więcej FLOP-ów z przejściem do przodu na krok. Dobrze zrobione — selektywne punkty kontrolne zgodnie z „inteligentną selekcją” Korthikantiego i in. — oszczędzasz 5x pamięć przy nakładzie poniżej 5% FLOP. A dzięki matmuls 8PR, odciążaniu FSDP i równoległemu MoE na poziomie eksperckim to naprawdę ma znaczenie: nie możesz sobie pozwolić ani na pamięć, ani na zmarnowane moce obliczeniowe.

## Koncepcja

### Czego właściwie potrzebuje wstecz

`output = layer(input)`. Wstecz chce `grad_input` i `grad_params`. Do ich obliczenia potrzeba:

- `input` (do obliczenia `grad_params = input.T @ grad_output` dla warstw liniowych)
- niektóre półprodukty pochodne aktywacji (pochodna ReLU/GELU/softmax zależy od wartości aktywacji)

Przepustka do przodu zapisuje je automatycznie na wykresie autogradu. Każda `tensor.retain_grad()` i każda operacja wymagająca wprowadzenia danych zachowuje odniesienie.

### Naiwne pełne sprawdzanie

Podziel sieć na segmenty `N`. Podczas przesyłania dalej przechowuj tylko *wejście* dla każdego segmentu. Kiedy wstecz potrzebuje półproduktów, powtórz przejście segmentu do przodu, aby je zmaterializować, a następnie rozróżnij.

Przykład: transformator 32-warstwowy podzielony na 32 segmenty po 1 warstwie każdy.

- Pamięć: 32 wejścia warstwowe (małe) vs 32 * (objętość aktywacji na warstwę) (ogromne).
- Dodatkowe obliczenia: 1 dodatkowy ruch do przodu na segment, tj. ~33% więcej łącznie FLOPów do przodu (ponieważ wstecz oznacza 2x do przodu, pełny krok wynosi 1 + 1 + 2 = 4 jednostki zamiast 1 + 2 = 3).

To jest oryginał Chen i in. Przepis na rok 2016: jeden punkt kontrolny na każdą warstwę `sqrt(L)` w celu zrównoważenia pamięci i obliczeń. Dla L=64 jest to 8 punktów kontrolnych.

### Selektywne punkty kontrolne (Korthikanti 2022)

Nie wszystkie aktywacje kosztują tyle samo. Wynik softmax uwagi wynosi `B*L*L*heads` i rośnie *kwadratowo* wraz z długością sekwencji. Ukryta aktywacja FFN to `B*L*4d` i rośnie liniowo. W przypadku długich sekwencji dominuje softmax.

Selektywne punkty kontrolne utrzymują aktywacje tanie w sklepie (projekcje liniowe, reszty) i przeliczają tylko te droższe (uwaga). Płacisz minimalne FLOPy za ponowne obliczenie, ale oszczędzasz pamięć O(L^2).

Megatron-Core implementuje to jako „selektywne” ponowne obliczenie aktywacji. Używany w większości granicznych biegów szkoleniowych w latach 2024+.

### Rozładuj

Alternatywa dla ponownego obliczenia: przesyłaj aktywacje do pamięci RAM procesora między przesyłaniem do przodu i do tyłu. Wymaga przepustowości PCIe; korzystne, gdy niewykorzystana przepustowość przekracza koszt rematerializacji. Powszechne są strategie mieszane: zaznacz niektóre warstwy, odciąż inne.

FSDP2 dostarcza odciążenie jako opcję najwyższej klasy. Odciążenie działa, gdy procesor graficzny jest wąskim gardłem w pamięci, ale transfer CPU-GPU ma zapas.

### Ponownie oblicz model kosztów

FLOPy krokowe z naiwnym punktem kontrolnym co `k` warstwy z `L`:

```
flops_fwd_normal = L * f_layer
flops_bwd_normal = 2 * L * f_layer
flops_total_normal = 3 * L * f_layer

flops_fwd_ckpt = L * f_layer
flops_recompute = L * f_layer  # one extra forward per layer in the segment
flops_bwd_ckpt = 2 * L * f_layer
flops_total_ckpt = 4 * L * f_layer
overhead = 4 / 3 - 1 = 0.33 = 33%
```

Dzięki selektywnemu punktowi kontrolnemu przeliczasz tylko jądro uwagi, a nie całą warstwę:

```
flops_recompute_selective = L * f_attention ~= L * f_layer * 0.15
overhead_selective = (3 + 0.15) / 3 - 1 = 0.05 = 5%
```

### Model oszczędzania pamięci

Liczba aktywacji na warstwę: `A`. Dla warstw `L` całkowita pamięć aktywacyjna: `L * A`.

Pełny punkt kontrolny (rozmiar segmentu 1): przechowuj tylko `L * input_volume` (~`L * 1/10 A` dla standardowego transformatora). Zapisuje ~`9 * L * A * 1/10`.

Punkt kontrolny dla każdej warstwy `k`: przechowuj wartości `L/k * A` plus `k-1` warstw w aktywnym segmencie.

Przy `k = sqrt(L)` zarówno koszty pamięci, jak i ponownego obliczenia skalują się z `sqrt(L)` — optymalnym kompromisem dla warstw o ​​jednolitym koszcie.

### Kiedy nie należy odwiedzać punktu kontrolnego

- Najbardziej wewnętrzne warstwy etapu rurociągu, które są już w trakcie realizacji. I tak muszą dokończyć.
- Pierwsza i ostatnia warstwa, jeśli dominują w obliczeniach sceny (rzadko w transformatorach).
- Jądra Attention już korzystają z FlashAttention — Flash już szybko przelicza softmax, więc dodatkowe punkty kontrolne na poziomie warstwy niewiele wnoszą do góry.

### Wzorce implementacji

1. **Opakowanie funkcji:** zawiń segment w `torch.utils.checkpoint.checkpoint(fn, input)`. PyTorch przechowuje tylko `input`, wszystko inne przelicza wstecz.

2. **Oparte na dekoratorze:** warstwy etykiet jako punkty kontrolne; trener decyduje w czasie konfiguracji, które segmenty zostaną zapakowane.

3. **Ręczne jawne ponowne obliczenie:** samodzielnie napisz przebieg wsteczny, wywołując niestandardową funkcję `recompute_forward`, która powiela przekaz do przodu z przechowywanymi danymi wejściowymi.

Wszystkie trzy dają ten sam wynik funkcjonalny. Wrappery to standardowy idiom.

### Interakcja z TP/PP/8PR

- **Tensor równoległy:** dane wejściowe z punktu kontrolnego muszą zostać zebrane lub ponownie rozproszone podczas ponownego obliczania; pokryć koszty komunikacji.
- **Potok równoległy:** typowy wzorzec polega na punkcie kontrolnym każdego etapu potoku, aby mikropartie w odwrotnej kolejności mogły ponownie wykorzystać pamięć aktywacyjną.
- **Ponowne obliczenie FP8:** historie amax zaktualizowane podczas ponownego obliczenia muszą odpowiadać oryginalnym przeliczeniom lub dryfom skali FP8. Większość frameworków tworzy migawkę skali.

## Zbuduj to

### Krok 1: Model zabawkowy z segmentami

```python
import numpy as np

def linear_forward(x, w, b):
    return x @ w + b

def relu(x):
    return np.maximum(x, 0)

def layer_forward(x, w1, b1, w2, b2):
    h = relu(linear_forward(x, w1, b1))
    return linear_forward(h, w2, b2)

def model_forward(x, params):
    activations = [x]
    h = x
    for w1, b1, w2, b2 in params:
        h = layer_forward(h, w1, b1, w2, b2)
        activations.append(h)
    return h, activations
```

### Krok 2: Naiwne wsteczne wymaganie wszystkich aktywacji

```python
def model_backward(grad_output, activations, params):
    grads = [None] * len(params)
    g = grad_output
    for i in range(len(params) - 1, -1, -1):
        w1, b1, w2, b2 = params[i]
        x_in = activations[i]
        h_pre = linear_forward(x_in, w1, b1)
        h = relu(h_pre)
        gh = g @ w2.T
        gw2 = h.T @ g
        gb2 = g.sum(axis=0)
        g_pre = gh * (h_pre > 0)
        gx = g_pre @ w1.T
        gw1 = x_in.T @ g_pre
        gb1 = g_pre.sum(axis=0)
        grads[i] = (gw1, gb1, gw2, gb2)
        g = gx
    return g, grads
```

### Krok 3: Punkt kontrolny – co k pamięci

```python
def model_forward_checkpointed(x, params, k=4):
    saved_inputs = [x]
    h = x
    for i, (w1, b1, w2, b2) in enumerate(params):
        h = layer_forward(h, w1, b1, w2, b2)
        if (i + 1) % k == 0:
            saved_inputs.append(h)
    return h, saved_inputs

def model_backward_checkpointed(grad_output, saved_inputs, params, k=4):
    grads = [None] * len(params)
    g = grad_output
    segments = [(j * k, min((j + 1) * k, len(params))) for j in range(len(saved_inputs))]
    for seg_idx in range(len(saved_inputs) - 1, -1, -1):
        start, end = segments[seg_idx]
        if start >= end:
            continue
        x_in = saved_inputs[seg_idx]
        _, seg_acts = model_forward(x_in, params[start:end])
        g, seg_grads = model_backward(g, seg_acts, params[start:end])
        for j, gr in enumerate(seg_grads):
            grads[start + j] = gr
    return g, grads
```

### Krok 4: Model kosztów

```python
def checkpoint_cost(n_layers, segment_size, flops_per_layer=1.0):
    fwd = n_layers * flops_per_layer
    recompute = n_layers * flops_per_layer
    bwd = 2 * n_layers * flops_per_layer
    return {
        "fwd": fwd,
        "recompute": recompute,
        "bwd": bwd,
        "total": fwd + recompute + bwd,
        "overhead_vs_no_ckpt": (fwd + recompute + bwd) / (fwd + bwd) - 1.0,
    }

def selective_checkpoint_cost(n_layers, attention_fraction=0.15,
                              flops_per_layer=1.0):
    fwd = n_layers * flops_per_layer
    recompute = n_layers * attention_fraction * flops_per_layer
    bwd = 2 * n_layers * flops_per_layer
    return {
        "fwd": fwd,
        "recompute": recompute,
        "bwd": bwd,
        "total": fwd + recompute + bwd,
        "overhead_vs_no_ckpt": (fwd + recompute + bwd) / (fwd + bwd) - 1.0,
    }
```

### Krok 5: Estymator pamięci

```python
def activation_memory_mb(n_layers, hidden=8192, seq=8192,
                        batch=1, bytes_per_value=2):
    per_layer = 12 * batch * seq * hidden * bytes_per_value
    return n_layers * per_layer / 1e6

def memory_after_checkpoint(n_layers, segment_size, hidden=8192,
                           seq=8192, batch=1, bytes_per_value=2):
    n_seg = max(1, n_layers // segment_size)
    saved = (n_seg + segment_size) * 1 * batch * seq * hidden * bytes_per_value
    return saved / 1e6
```

### Krok 6: Optymalny rozmiar segmentu

```python
def optimal_segment(n_layers):
    return int(round(np.sqrt(n_layers)))
```

### Krok 7: Wybiórcza decyzja dotycząca punktu kontrolnego

```python
def should_recompute(layer_type, activation_bytes, recompute_flops_ratio):
    if layer_type == "attention" and activation_bytes > 100 * 1e6:
        return True
    if layer_type == "ffn" and activation_bytes > 500 * 1e6:
        return recompute_flops_ratio < 0.1
    return False
```

## Użyj tego

- **torch.utils.checkpoint**: `from torch.utils.checkpoint import checkpoint` — kanoniczne opakowanie w PyTorch. Zawija funkcję; przechowuje tylko dane wejściowe, przelicza wstecz.
- **Ponowne obliczenie aktywacji Megatron-Core**: obsługuje tryby `selective`, `full` i `block`. Standard w szkoleniu pionierskim 2024+.
- **Odciążenie FSDP2**: `module.to_empty(device="cpu")` z `offload_policy` w FSDP2 powoduje aktywację fragmentów do procesora zamiast ponownego obliczania.
- **DeepSpeed ​​ZeRO-Offload**: odciążanie procesora dla stanów i aktywacji optymalizatora, uzupełnienie punktów kontrolnych.

## Wyślij to

Ta lekcja generuje `outputs/prompt-activation-recompute-policy.md` — monit, który pobiera konfigurację modelu (warstwy, ukryte, sekwencyjne, wsadowe) i dostępną pamięć GPU oraz emituje zasady ponownego obliczania dla każdej warstwy (brak / selektywne / pełne / odciążenie).

## Ćwiczenia

1. Sprawdź poprawność. Uruchom `model_forward` + `model_backward` (pełne aktywacje) vs `model_forward_checkpointed` + `model_backward_checkpointed` (segmenty). Gradienty parametrów muszą być identyczne z precyzją maszyny.

2. Rozmiar segmentu przemiatania `k` od 1 do `L`. Wykreśl obciążenie FLOP i pamięć. Znajdź kolano krzywej.

3. Wprowadź selektywne punkty kontrolne: przechowuj dane wejściowe modułu uwagi, ale nie ich produkty pośrednie. Zmierz narzut FLOP w porównaniu z punktami kontrolnymi pełnej warstwy dla modelu 32-warstwowego w seq=8192.

4. Dodaj odciążenie. Zapisz wejścia segmentu w symulowanym „buforze procesora” (osobna lista). Zmierz „przepustowość PCIe” jako bajty/czas i znajdź próg rentowności między odciążeniem a ponownym obliczeniem.

5. Zrób test porównawczy prawdziwego transformatora PyTorch z i bez `torch.utils.checkpoint`. Zmierz pamięć (przez `torch.cuda.max_memory_allocated`) i czas kroku.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| Gradientowe punkty kontrolne | „Zaoszczędź pamięć, wykonując ponawianie do przodu” | Przechowuj tylko wejścia segmentów; ponownie obliczyć półprodukty podczas odtwarzania wstecz, aby uzyskać tensory obsługujące gradienty |
| Ponowne obliczenie aktywacji | „To samo co punkt kontrolny” | Nazwa o smaku HPC dla tej samej techniki |
| Rozmiar segmentu (k) | „Ile warstw na punkt kontrolny” | Liczba warstw, których produkty pośrednie są odrzucane i ponownie materializowane razem |
| Selektywne punkty kontrolne | „Sztuczka Korthikantiego” | Oblicz ponownie tylko te aktywacje, które są drogie w sklepie (uwaga softmax); trzymaj tanie |
| Pełne punkty kontrolne | „Wersja naiwna” | Oblicz ponownie półprodukty każdej warstwy w każdym segmencie |
| Blokuj punkty kontrolne | „Gruboziarnisty” | Checkpoint całe bloki transformatorów; największa ziarnistość |
| FLOP nad głową | „Podatek obliczeniowy” | Dodatkowe FLOPy na krok = (przelicz FLOPy) / (fwd + bwd FLOP); 33% naiwny, 5% selektywny |
| Odciążenie aktywacji | „Wysłać do procesora” | Przenieś aktywacje do pamięci RAM procesora w przód->wstecz; alternatywa dla ponownego obliczenia |
| reguła sqrt-L | „Klasyczne optymalne” | W przypadku warstw o ​​jednakowych kosztach optymalnym odstępem między punktami kontrolnymi są warstwy sqrt(L) |
| Uwaga-softmax głośność | „Problem O(L^2)” | L^2 * głowice * pływaki wsadowe; dominuje pamięć aktywacji w długich kontekstach |

## Dalsze czytanie

– [Chen i in., 2016 – „Trening głębokich sieci za pomocą subliniowego kosztu pamięci”](https://arxiv.org/abs/1604.06174) – oryginalny artykuł, który sformalizował gradientowe punkty kontrolne
- [Korthikanti i in., 2022 - „Reducing Activation Recomputation in Large Transformer Models”](https://arxiv.org/abs/2205.05198) – selektywne ponowne obliczenie aktywacji i formalna analiza kosztów
- [Pudipeddi i in., 2020 – „Trening dużych sieci neuronowych za pomocą stałej pamięci przy użyciu nowego algorytmu wykonywania”](https://arxiv.org/abs/2002.05645) – alternatywne podejście ze stałą pamięcią poprzez rematerializację w trybie odwrotnym
– [Ren i in., 2021 – „ZeRO-Offload: Demokratyzacja szkolenia w zakresie modeli na skalę miliardową”](https://arxiv.org/abs/2101.06840) – odciążanie aktywacyjne na dużą skalę
- [Dokumentacja PyTorch torch.utils.checkpoint](https://pytorch.org/docs/stable/checkpoint.html) - standardowe API
- [Dokumentacja ponownego obliczenia aktywacji Megatron-Core](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/features/memory_optimizations.html) - tryby selektywne, pełne i blokowe