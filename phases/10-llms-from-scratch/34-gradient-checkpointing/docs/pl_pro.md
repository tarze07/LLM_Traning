# Gradientowy punkt kontrolny i ponowne obliczenie aktywacji

> Propagacja wsteczna przechowuje każdą pośrednią aktywację. Przy 70B parametrach i kontekście 128K daje to 3 TB aktywacji na rząd. Checkpointing wymienia FLOPy na pamięć: przeliczaj zamiast zapisywać. Pytanie brzmi, które segmenty porzucić — a odpowiedź nie jest prosta.

**Typ:** Kompilacja
**Języki:** Python (z numpy, opcjonalna latarka)
**Wymagania wstępne:** Faza 10, lekcja 04 (przedszkoleniowy Mini-GPT), faza 10, lekcja 05 (skalowanie i dystrybucja)
**Czas:** ~70 minut

## Problem

Uczenie transformatora wymaga przechowywania danych wejściowych do każdej operacji różniczkowanej wstecz: wejść uwagi, projekcji Q/K/V, wyjścia softmax, wejść FFN, wyjść normalizacji i strumienia resztkowego. Dla warstwy o ukrytym rozmiarze `d`, długości sekwencji `L` i rozmiarze partii `B` ilość danych wynosi rzędu `12 * B * L * d` wartości zmiennoprzecinkowych na warstwę.

Dla `d=8192, L=8192, B=1` oznacza to 800 MB na warstwę w BF16. Model 64-warstwowy to 51 GB aktywacji — zanim uwzględni się rozmiar mikropartii, pośrednie produkty softmax uwagi (`L^2` na głowicę) oraz częściowe kopie w równoległości tensorowej.

Sytuacja jest niejednoznaczna: wagi BF16 wraz ze stanem optymalizatora mogą zmieścić się w 80 GB, lecz aktywacje szybko wyczerpują dostępną pamięć. Gradientowy punkt kontrolny (czyli ponowne obliczanie aktywacji) to standardowe rozwiązanie tego problemu. Większość aktywacji jest odrzucana, a podczas przejścia wstecznego wykonywane jest ponowne przejście w przód, by je odtworzyć. Koszt to dodatkowe FLOPy; korzyść to spadek zużycia pamięci proporcjonalny do stosunku segmentów z punktami kontrolnymi do łącznej liczby warstw.

W naiwnym podejściu punkty kontrolne kosztują około 33% dodatkowych FLOPów przejścia w przód na krok. Zastosowane umiejętnie — zgodnie z selektywnym checkpointingiem opisanym przez Korthikantiego i in. — można osiągnąć pięciokrotną oszczędność pamięci przy narzucie poniżej 5% FLOPów. W połączeniu z matmuls FP8, odciążaniem FSDP i równoległością MoE na poziomie eksperckim ma to realne znaczenie: nie można sobie pozwolić na marnowanie ani pamięci, ani mocy obliczeniowej.

## Koncepcja

### Czego potrzebuje przejście wsteczne

`output = layer(input)`. Przejście wsteczne wyznacza `grad_input` oraz `grad_params`. Do tego celu niezbędne są:

- `input` (do obliczenia `grad_params = input.T @ grad_output` dla warstw liniowych)
- niektóre pośrednie wartości pochodnych aktywacji (pochodna ReLU/GELU/softmax zależy od wartości aktywacji)

Przejście w przód zapisuje je automatycznie na grafie automatycznego różniczkowania. Każda operacja `tensor.retain_grad()` i każda operacja wymagająca danych wejściowych zachowuje referencję.

### Naiwny pełny checkpointing

Sieć dzielona jest na `N` segmentów. Podczas przejścia w przód zachowywane jest wyłącznie *wejście* każdego segmentu. Gdy przejście wsteczne potrzebuje wartości pośrednich, segment jest przeliczany w przód w celu ich odtworzenia, a następnie różniczkowany.

Przykład: transformator 32-warstwowy podzielony na 32 segmenty, po jednej warstwie każdy.

- Pamięć: 32 wejścia warstw (małe) zamiast 32 * (objętość aktywacji na warstwę) (ogromne).
- Dodatkowe obliczenia: jedno dodatkowe przejście w przód na segment, co daje ~33% więcej łącznych FLOPów przejścia w przód (przejście wsteczne to 2x przejście w przód, więc pełny krok wynosi 1 + 1 + 2 = 4 jednostki zamiast 1 + 2 = 3).

Jest to oryginalna metoda Chen i in. z 2016 roku: jeden punkt kontrolny na `sqrt(L)` warstw, co zapewnia równowagę między pamięcią a obliczeniami. Dla L=64 daje to 8 punktów kontrolnych.

### Selektywny checkpointing (Korthikanti 2022)

Nie wszystkie aktywacje mają jednakowy koszt przechowywania. Wynik softmax uwagi zajmuje `B*L*L*heads` i rośnie *kwadratowo* wraz z długością sekwencji. Ukryta aktywacja FFN to `B*L*4d` i rośnie liniowo. Dla długich sekwencji dominuje softmax.

Selektywny checkpointing zachowuje aktywacje tanie w przechowywaniu (projekcje liniowe, połączenia resztkowe) i przelicza wyłącznie te kosztowniejsze (uwaga). Płaci się minimalne FLOPy za ponowne obliczenie, a oszczędzana jest pamięć rzędu O(L^2).

Megatron-Core implementuje tę metodę jako „selektywne" ponowne obliczanie aktywacji. Jest ona powszechnie stosowana w czołowych procesach szkoleniowych od 2024 roku.

### Odciążanie

Alternatywą dla ponownego obliczania jest przesyłanie aktywacji do pamięci RAM procesora między przejściami w przód i wstecz. Wymaga to przepustowości PCIe i jest opłacalne, gdy dostępna przepustowość przekracza koszt ponownego obliczenia. Stosowane są też strategie mieszane: część warstw podlega checkpointingowi, część jest odciążana.

FSDP2 obsługuje odciążanie jako opcję pierwszej klasy. Jest ono skuteczne, gdy procesor graficzny stanowi wąskie gardło pamięciowe, a transfer CPU-GPU dysponuje zapasem przepustowości.

### Model kosztów ponownego obliczania

FLOPy na krok przy naiwnym checkpointingu co `k` warstw z `L` warstw łącznie:

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

Przy selektywnym checkpointingu przeliczane jest jedynie jądro uwagi, a nie cała warstwa:

```
flops_recompute_selective = L * f_attention ~= L * f_layer * 0.15
overhead_selective = (3 + 0.15) / 3 - 1 = 0.05 = 5%
```

### Model oszczędności pamięci

Oznaczmy liczbę aktywacji na warstwę jako `A`. Dla `L` warstw łączna pamięć aktywacji wynosi `L * A`.

Pełny checkpointing (rozmiar segmentu 1): przechowywane jest jedynie `L * input_volume` (~`L * 1/10 A` dla standardowego transformatora), co daje oszczędność rzędu `9 * L * A * 1/10`.

Checkpoint co `k` warstw: przechowywane są wartości `L/k * A` plus `k-1` warstw aktywnego segmentu.

Przy `k = sqrt(L)` zarówno koszt pamięci, jak i koszt ponownego obliczania skalują się z `sqrt(L)` — to optymalny kompromis dla warstw o jednolitym koszcie.

### Kiedy nie stosować checkpointingu

- Najbardziej wewnętrzne warstwy etapu potoku, które są już w trakcie przetwarzania — i tak muszą zostać ukończone.
- Pierwsza i ostatnia warstwa, jeśli dominują w obliczeniach etapu (rzadko spotykane w transformatorach).
- Jądra uwagi korzystające już z FlashAttention — Flash przelicza softmax wewnętrznie, więc dodatkowy checkpointing na poziomie warstwy wnosi niewiele.

### Wzorce implementacji

1. **Opakowanie funkcji:** owinięcie segmentu w `torch.utils.checkpoint.checkpoint(fn, input)`. PyTorch zachowuje wyłącznie `input`, a wszystko inne przelicza podczas przejścia wstecznego.

2. **Oparte na dekoratorze:** warstwy oznaczane są jako punkty kontrolne; trener decyduje podczas konfiguracji, które segmenty zostaną opakowane.

3. **Ręczne jawne ponowne obliczanie:** samodzielna implementacja przejścia wstecznego wywołująca niestandardową funkcję `recompute_forward`, która odtwarza przejście w przód na podstawie zachowanych danych wejściowych.

Wszystkie trzy podejścia dają taki sam wynik. Wrappery to standardowy idiom.

### Interakcja z TP/PP/FP8

- **Równoległość tensorowa:** dane wejściowe punktu kontrolnego muszą zostać zebrane lub ponownie rozproszone podczas przeliczania; należy uwzględnić koszty komunikacji.
- **Równoległość potokowa:** typowy wzorzec polega na checkpointingu każdego etapu potoku, dzięki czemu mikropartie przetwarzane w odwrotnej kolejności mogą ponownie wykorzystywać pamięć aktywacji.
- **Ponowne obliczanie FP8:** historia wartości amax aktualizowana podczas przeliczania musi być spójna z pierwotnymi obliczeniami, inaczej dochodzi do dryftu skali FP8. Większość frameworków tworzy migawkę skali.

## Zbuduj to

### Krok 1: Model przykładowy z segmentami

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

### Krok 2: Naiwne przejście wsteczne wymagające wszystkich aktywacji

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

### Krok 3: Checkpointing co k warstw

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

### Krok 7: Decyzja o selektywnym checkpointingu

```python
def should_recompute(layer_type, activation_bytes, recompute_flops_ratio):
    if layer_type == "attention" and activation_bytes > 100 * 1e6:
        return True
    if layer_type == "ffn" and activation_bytes > 500 * 1e6:
        return recompute_flops_ratio < 0.1
    return False
```

## Zastosowanie w praktyce

- **torch.utils.checkpoint**: `from torch.utils.checkpoint import checkpoint` — kanoniczne opakowanie w PyTorch. Opakowuje funkcję, zachowuje tylko dane wejściowe i przelicza je podczas przejścia wstecznego.
- **Ponowne obliczanie aktywacji w Megatron-Core**: obsługuje tryby `selective`, `full` i `block`. Standard w czołowych procesach szkoleniowych od 2024 roku.
- **Odciążanie FSDP2**: `module.to_empty(device="cpu")` z `offload_policy` w FSDP2 przenosi fragmenty aktywacji na procesor zamiast ponownego obliczania.
- **DeepSpeed ZeRO-Offload**: odciążanie procesora dla stanów optymalizatora i aktywacji, uzupełniające checkpointing.

## Dane wyjściowe lekcji

Lekcja generuje plik `outputs/prompt-activation-recompute-policy.md` — zapytanie, które przyjmuje konfigurację modelu (liczba warstw, rozmiar ukryty, długość sekwencji, rozmiar partii) oraz dostępną pamięć GPU i zwraca politykę ponownego obliczania dla każdej warstwy (brak / selektywne / pełne / odciążanie).

## Ćwiczenia

1. Sprawdź poprawność. Uruchom `model_forward` + `model_backward` (pełne aktywacje) oraz `model_forward_checkpointed` + `model_backward_checkpointed` (segmenty). Gradienty parametrów muszą być identyczne z dokładnością maszynową.

2. Przemiataj rozmiar segmentu `k` od 1 do `L`. Wykreśl narzut FLOPów i zużycie pamięci. Znajdź punkt przegięcia krzywej.

3. Wprowadź selektywny checkpointing: zachowaj dane wejściowe modułu uwagi, ale nie ich wartości pośrednie. Zmierz narzut FLOPów w porównaniu z checkpointingiem pełnej warstwy dla modelu 32-warstwowego przy seq=8192.

4. Dodaj odciążanie. Zapisz wejścia segmentu w symulowanym „buforze procesora" (osobna lista). Zmierz „przepustowość PCIe" jako bajty/czas i wyznacz próg opłacalności między odciążaniem a ponownym obliczaniem.

5. Wykonaj testy porównawcze prawdziwego transformatora PyTorch z `torch.utils.checkpoint` i bez niego. Zmierz zużycie pamięci (przez `torch.cuda.max_memory_allocated`) oraz czas kroku.

## Kluczowe terminy

| Termin | Co się mówi | Co to oznacza |
|------|----------------|----------------------|
| Gradientowy punkt kontrolny | „Zaoszczędź pamięć przez ponowne przejście w przód" | Przechowuj tylko wejścia segmentów; wartości pośrednie są przeliczane podczas przejścia wstecznego, by uzyskać tensory z gradientami |
| Ponowne obliczanie aktywacji | „To samo co punkt kontrolny" | Nazwa o rodowodzie HPC dla tej samej techniki |
| Rozmiar segmentu (k) | „Ile warstw na punkt kontrolny" | Liczba warstw, których wartości pośrednie są odrzucane i ponownie odtwarzane łącznie |
| Selektywny checkpointing | „Metoda Korthikantiego" | Ponowne obliczanie tylko kosztownych w przechowywaniu aktywacji (softmax uwagi) przy zachowaniu tanich |
| Pełny checkpointing | „Wersja naiwna" | Ponowne obliczanie wartości pośrednich każdej warstwy w każdym segmencie |
| Blokowy checkpointing | „Gruboziarnisty" | Checkpointing całych bloków transformatora; największa ziarnistość |
| Narzut FLOPów | „Podatek obliczeniowy" | Dodatkowe FLOPy na krok = (FLOPy przeliczania) / (FLOPy przód + wstecz); 33% dla metody naiwnej, 5% dla selektywnej |
| Odciążanie aktywacji | „Wysłanie do procesora" | Przeniesienie aktywacji do pamięci RAM procesora między przejściem w przód a wstecz; alternatywa dla ponownego obliczania |
| Reguła sqrt-L | „Klasyczne optimum" | Dla warstw o jednakowym koszcie optymalny odstęp między punktami kontrolnymi wynosi sqrt(L) warstw |
| Objętość softmax uwagi | „Problem O(L^2)" | L^2 * liczba głowic * rozmiar partii; dominuje pamięć aktywacji przy długich kontekstach |

## Dalsza lektura

- [Chen i in., 2016 – „Training Deep Nets with Sublinear Memory Cost"](https://arxiv.org/abs/1604.06174) – oryginalny artykuł formalizujący gradientowe punkty kontrolne
- [Korthikanti i in., 2022 – „Reducing Activation Recomputation in Large Transformer Models"](https://arxiv.org/abs/2205.05198) – selektywne ponowne obliczanie aktywacji i formalna analiza kosztów
- [Pudipeddi i in., 2020 – „Training Large Neural Networks with Constant Memory using a New Execution Algorithm"](https://arxiv.org/abs/2002.05645) – alternatywne podejście ze stałym zużyciem pamięci przez rematerializację w trybie wstecznym
- [Ren i in., 2021 – „ZeRO-Offload: Democratizing Billion-Scale Model Training"](https://arxiv.org/abs/2101.06840) – odciążanie aktywacji na dużą skalę
- [Dokumentacja PyTorch torch.utils.checkpoint](https://pytorch.org/docs/stable/checkpoint.html) – standardowe API
- [Dokumentacja ponownego obliczania aktywacji Megatron-Core](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/features/memory_optimizations.html) – tryby selektywny, pełny i blokowy
