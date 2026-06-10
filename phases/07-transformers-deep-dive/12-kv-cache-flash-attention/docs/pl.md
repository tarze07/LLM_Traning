# Pamięć podręczna KV, uwaga Flash i optymalizacja wnioskowania

> Trening jest równoległy i związany z FLOP. Wnioskowanie ma charakter szeregowy i jest powiązane z pamięcią. Różne wąskie gardła, różne sztuczki.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~75 minut

## Problem

Naiwny dekoder autoregresyjny `O(N²)` generuje tokeny `N`: na każdym kroku ponownie oblicza uwagę na podstawie pełnego przedrostka. W przypadku odpowiedzi na token 4K, która obejmuje 16 milionów operacji uwagi, większość z nich jest zbędna. Każdy ukryty stan tokenu prefiksu jest deterministyczny po obliczeniu — wystarczy uruchomić zapytanie nowego tokenu względem buforowanych kluczy i wartości wszystkiego wcześniej.

Co więcej, sama uwaga przenosi wiele danych. Standardowa uwaga materializuje macierz wyników N×N, wynik softmax N×d, wynik końcowy N×d — zbyt wiele odczytów i zapisów w HBM. Dla N≥2K uwaga zostaje powiązana z pamięcią, zanim zostanie powiązana z FLOP. Klasyczne jądra uwagi nie wykorzystują nowoczesnych procesorów graficznych 4–10×.

Dwie optymalizacje, obie opracowane przez Dao i in., przesunęły wnioskowanie graniczne z „wolnego” na „szybkie”:

1. **Pamięć podręczna KV.** Przechowuj wektory K i V każdego tokenu prefiksu. Uwaga każdego nowego tokena to jedno zapytanie dotyczące kluczy w pamięci podręcznej. Wnioskowanie zmniejsza się z `O(N²)` do `O(N)` na krok generowania.
2. **Uwaga Flash.** Obliczenia uwagi podziel tak, aby pełna macierz N×N nigdy nie osiągnęła HBM. Wszystko softmax + matmul dzieje się w SRAM. 2–4× przyspieszenie zegara ściennego na A100; 5–10× na H100 z FP8.

Do 2026 roku oba będą uniwersalne. Każdy stos wnioskowania produkcyjnego (vLLM, TensorRT-LLM, SGLang, llama.cpp) je zakłada. Każdy model Frontier jest dostarczany z włączoną funkcją Flash Attention.

## Koncepcja

![Wzrost pamięci podręcznej KV i kafelkowanie uwagi Flash](../assets/kv-cache-flash-attn.svg)

### Matematyka pamięci podręcznej KV

Na warstwę dekodera, na token, na głowicę:

```
bytes_per_token_per_layer = 2 * d_head * dtype_size
                          ^
                          K and V
```

Dla modelu 7B z 32 warstwami, 32 głowami, d_head=128, fp16:

```
per token per layer = 2 * 128 * 2 = 512 bytes
per token (32 layers) = 16 KB
per 32K context = 512 MB
```

Dla Lamy 3 70B (80 warstw, d_head=128, GQA z 8 głowicami KV):

```
per token per layer = 2 * 8 * 128 * 2 = 4096 bytes (4 KB)
per 32K context = 10.4 GB
```

Z tych 10 GB wynika, że Llama 3 70B w kontekście 128 KB potrzebuje większości z 40 GB A100 tylko na pamięć podręczną KV w partii o rozmiarze 1.

**GQA to zwycięska pamięć podręczna KV.** MHA z 64 głowicami będzie wynosić 32 GB. MLA kompresuje jeszcze bardziej.

### Uwaga Flash — sztuczka z układaniem płytek

Standardowa uwaga:

```
S = Q @ K^T          (HBM read, N×N, HBM write)
P = softmax(S)       (HBM read, HBM write)
O = P @ V            (HBM read, HBM write)
```

Trzy wycieczki w obie strony HBM. W H100 przepustowość HBM wynosi 3 TB/s; Pamięć SRAM wynosi 30 TB/s. Każda podróż HBM to 10-krotne spowolnienie w porównaniu z utrzymaniem wszystkiego na chipie.

Błysk Uwaga:

```
for each block of Q (tile size ~128 × 128):
    load Q_tile into SRAM
    for each block of K, V:
        load K_tile, V_tile into SRAM
        compute S_tile = Q_tile @ K_tile^T     (SRAM)
        running softmax aggregation             (SRAM)
        accumulate into O_tile                  (SRAM)
    write O_tile to HBM
```

Jedna podróż HBM na kafelek. Całkowite wykorzystanie pamięci spada z `O(N²)` do `O(N)`. Przejście wsteczne ponownie oblicza niektóre wartości z przebiegu w przód, zamiast je przechowywać – kolejna wygrana pamięci.

**Sztuczka numeryczna.** Uruchamianie softmaxu utrzymuje `(max, sum)` na wszystkich kafelkach, więc ostateczna normalizacja jest dokładna. To nie jest przybliżenie — Flash Attention oblicza bitowo identyczne dane wyjściowe ze standardową uwagą (brak asocjatywności modulo fp16).

**Ewolucja wersji:**

| Wersja | Rok | Kluczowa zmiana | Przyspieszenie na sprzęcie referencyjnym |
|--------|------|-----------|-------------------------|
| Flash 1 | 2022 | Kafelkowe jądro SRAM | 2× na A100 |
| Flash 2 | 2023 | Lepsza równoległość, porządek przyczynowy | 3× na A100 |
| Flash 3 | 2024 | Asynchronia leja, FP8 | 1,5–2× na H100 (~740 TFLOPS FP16) |
| Flash 4 | 2026 | Blackwell 5-stopniowy potok, oprogramowanie exp2 | Najpierw wnioskowanie (początkowo tylko do przodu) |

Flash 4 jest przesyłany w przód tylko podczas uruchamiania. Szkolenie nadal wykorzystuje Flash 3. Oczekuje się na obsługę Flash 4 przez GQA i varlen (połowa 2026 r.).

### Dekodowanie spekulatywne — wygrywa druga latencja

Tani model proponuje N żetonów. Duży model sprawdza wszystkie N równolegle. Jeśli weryfikacja akceptuje k tokenów, zapłaciłeś 1 karnet na duży model na k pokoleń. Typowe k=3–5 w kodzie i prozie.

Wartości domyślne na rok 2026:
- **EAGLE 2 / Medusa.** Zintegrowane głowice przeciągowe, które współdzielą ukryte stany weryfikatora. Przyspieszenie 2–3× bez utraty jakości.
- **Dekodowanie spekulacyjne w modelu roboczym.** Przyspieszenie 2–4× na sprzęcie konsumenckim.
- **Dekodowanie z wyprzedzeniem.** Iteracja Jacobiego; nie jest potrzebny żaden projekt modelu. Niszowe, ale darmowe.

### Ciągłe dozowanie

Klasyczne wnioskowanie wsadowe: poczekaj na zakończenie najwolniejszej sekwencji, a następnie rozpocznij nową partię. Marnuje procesor graficzny, gdy krótkie odpowiedzi kończą się wcześniej.

Ciągłe przetwarzanie wsadowe (najpierw wysłane w Orca, teraz w vLLM, TensorRT-LLM, SGLang): zamień nowe żądania do partii, gdy tylko stare się zakończą. 5–10-krotny wzrost przepustowości w przypadku typowych obciążeń związanych z czatem.

### PagedAttention — pamięć podręczna KV jako pamięć wirtualna

Nagłówek funkcji vLLM. Pamięć podręczna KV jest przydzielana w 16-tokenowych blokach; tabela stron odwzorowuje pozycje logiczne na bloki fizyczne. Umożliwia współdzielenie wartości KV pomiędzy równoległymi próbkami (wyszukiwanie wiązki, próbkowanie równoległe), przedrostki typu hot-swap w celu szybkiego buforowania i pamięć defragmentacyjną. 4-krotna poprawa przepustowości w porównaniu z naiwną alokacją ciągłą.

## Zbuduj to

Zobacz `code/main.py`. Wdrażamy:

1. Naiwny dekoder przyrostowy `O(N²)`.
2. Dekoder `O(N)` z pamięcią podręczną KV.
3. Kafelkowy softmax symulujący algorytm Flash Attention działający maksymalnie.

### Krok 1: Pamięć podręczna KV

```python
class KVCache:
    def __init__(self, n_layers, n_heads, d_head):
        self.K = [[[] for _ in range(n_heads)] for _ in range(n_layers)]
        self.V = [[[] for _ in range(n_heads)] for _ in range(n_layers)]

    def append(self, layer, head, k, v):
        self.K[layer][head].append(k)
        self.V[layer][head].append(v)

    def read(self, layer, head):
        return self.K[layer][head], self.V[layer][head]
```

Proste: stale powiększaj wektory K, V na token w listach na warstwę i na głowę.

### Krok 2: kafelkowy softmax

```python
def tiled_softmax_dot(q, K, V, tile=4):
    """Flash-attention-style softmax(qK^T)V with running max/sum."""
    m = float("-inf")
    s = 0.0
    out = [0.0] * len(V[0])
    for start in range(0, len(K), tile):
        k_block = K[start:start + tile]
        v_block = V[start:start + tile]
        scores = [sum(qi * ki for qi, ki in zip(q, k)) for k in k_block]
        new_m = max(m, *scores)
        exp_old = math.exp(m - new_m) if m != float("-inf") else 0.0
        exp_new = [math.exp(sc - new_m) for sc in scores]
        s = s * exp_old + sum(exp_new)
        for j in range(len(out)):
            out[j] = out[j] * exp_old + sum(e * v[j] for e, v in zip(exp_new, v_block))
        m = new_m
    return [o / s for o in out]
```

Bitowo identyczne wyjście do `softmax(qK) V` za jednym razem, ale w dowolnym momencie zestawem roboczym jest blok `tile × d_head`, a nie pełny `N × d_head`.

### Krok 3: porównaj dekodowanie naiwne z dekodowaniem buforowanym przy generacji 100 tokenów

Policz operacje uwagi. Naiwny: `O(N²)` = 5050. Buforowany: `O(N)` = 100. Kod wyświetla oba.

## Użyj tego

```python
# HuggingFace transformers auto-enables KV cache on decoder-only generate().
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B",
    attn_implementation="flash_attention_2",  # use FA3 if Hopper
    torch_dtype="bfloat16",
)
# generate() uses KV cache automatically
```

Produkcja vLLM:

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 32768 \
    --enable-prefix-caching \
    --kv-cache-dtype fp8
```

Buforowanie prefiksów w żądaniach to wielka korzyść w roku 2026 — ten sam monit systemowy, kilka przykładów lub dokument o długim kontekście ponownie wykorzystuje wartość KV w połączeniach. W przypadku obciążeń agentów z powtarzającymi się monitami o narzędzia buforowanie prefiksów rutynowo zapewnia 5-krotny wzrost przepustowości.

## Wyślij to

Zobacz `outputs/skill-inference-optimizer.md`. Umiejętność wybiera implementację uwagi, strategię pamięci podręcznej KV, kwantyzację i dekodowanie spekulatywne w celu nowego wdrożenia wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Potwierdź, że dekodery naiwne i buforowane dają ten sam wynik; zwróć uwagę na różnicę w liczbie operacji.
2. **Średni.** Zaimplementuj buforowanie prefiksów: po otrzymaniu monitu P i kilku uzupełnień, wykonaj jedno przejście w przód przez P, aby wypełnić pamięć podręczną KV, a następnie rozgałęziaj się po zakończeniu. Zmierz przyspieszenie w porównaniu z ponownym kodowaniem P dla każdego.
3. **Trudne.** Zaimplementuj zabawkę PagedUwaga: pamięć podręczna KV w stałych 16-tokenowych blokach z bezpłatną listą. Kiedy sekwencja się zakończy, należy zwrócić jej bloczki do puli. Symuluj 1000 zakończeniach czatów o różnej długości. Porównaj fragmentację pamięci z alokacją ciągłą.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Pamięć podręczna KV | „Sztuczka, która przyspiesza dekodowanie” | Przechowywane K i V z każdego żetonu prefiksu; nowe zapytania obsługują je, zamiast ponownie obliczać. |
| HBM | „Pamięć główna GPU” | Pamięć o dużej przepustowości; 80 GB na H100, 192 GB na B200. Przepustowość ~3 TB/s. |
| SRAM | „Pamięć na chipie” | Szybka pamięć na SM, ~256 KB na SM w H100. Przepustowość ~30 TB/s. |
| Błysk Uwaga | „Jądro uwagi kafelkowej” | Oblicza uwagę bez materializowania N×N w HBM. |
| Ciągłe dozowanie | „Przetwarzanie wsadowe bez oczekiwania” | Wymień gotowe sekwencje i włóż nowe, bez opróżniania partii. |
| PagedUwaga | „nagłówek vLLM” | Pamięć podręczna KV przydzielana w stałych blokach z tablicą stron; eliminuje fragmentację. |
| Buforowanie prefiksów | „Użyj ponownie długich podpowiedzi” | Buforuj KV dla wspólnego prefiksu dla żądań; poważne obniżki kosztów agentów. |
| Dekodowanie spekulatywne | „Szkic + weryfikacja” | Tani model draftu proponuje tokeny; duży model sprawdza k w jednym przebiegu. |

## Dalsze czytanie

- [Dao i in. (2022). FlashAttention: szybka i oszczędzająca pamięć funkcja dokładnej uwagi z funkcją IO-Awareness](https://arxiv.org/abs/2205.14135) — Flash 1.
- [Dao (2023). FlashAttention-2: szybsza uwaga dzięki lepszej równoległości i podziałowi pracy](https://arxiv.org/abs/2307.08691) — Flash 2.
- [Shah i in. (2024). FlashAttention-3: szybka i dokładna uwaga z asynchronią i niską precyzją](https://arxiv.org/abs/2407.08608) — Flash 3.
- [Informacje o wydaniu FlashAttention-4 (Dao-AILab, 2026)](https://github.com/Dao-AILab/flash-attention) — 5-etapowy potok Blackwell i sztuczka software-exp2; przeczytaj repozytorium README, aby zapoznać się z zastrzeżeniami dotyczącymi uruchamiania tylko do przodu, o których wspomina ta lekcja.
- [Kwon i in. (2023). Efektywne zarządzanie pamięcią w przypadku modelu wielkojęzycznego udostępnianego za pomocą PagedAttention](https://arxiv.org/abs/2309.06180) — artykuł vLLM.
- [Lewiatan i in. (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — dekodowanie specyfikacji.
- [Li i in. (2024). EAGLE: Próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności cech](https://arxiv.org/abs/2401.15077) — artykuł EAGLE-1/2 dotyczący podejścia zintegrowanego, o którym mowa w lekcji.
- [Cai i in. (2024). Medusa: prosta struktura przyspieszania wnioskowania LLM z wieloma głowicami dekodującymi](https://arxiv.org/abs/2401.10774) — podejście Medusa, do którego odwołuje się EAGLE.
- [dokumentacja vLLM — PagedAttention](https://docs.vllm.ai/en/latest/design/kernel/paged_attention.html) — kanoniczne szczegółowe omówienie 16-tokenowego bloku i projektu tablicy stron.