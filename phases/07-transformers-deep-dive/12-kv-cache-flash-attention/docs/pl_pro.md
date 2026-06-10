# Pamięć podręczna KV, Flash Attention i optymalizacja wnioskowania

> Trening jest równoległy i ograniczony przez operacje zmiennoprzecinkowe. Wnioskowanie ma charakter sekwencyjny i jest ograniczone przez pamięć. Inne wąskie gardła, inne techniki.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~75 minut

## Problem

Naiwny dekoder autoregresyjny o złożoności `O(N²)` generuje `N` tokenów, przy czym na każdym kroku od nowa oblicza uwagę dla całego prefiksu. Przy generowaniu odpowiedzi o długości 4K tokenów daje to 16 milionów operacji uwagi, z czego większość jest zbędna. Ukryte stany tokenów prefiksu są deterministyczne po pierwszym obliczeniu — wystarczy uruchomić zapytanie nowego tokenu względem buforowanych kluczy i wartości wszystkich poprzednich tokenów.

Co więcej, sama operacja uwagi wymaga transferu dużych ilości danych. Standardowa uwaga materializuje macierz wyników N×N, wynik softmax N×d oraz wynik końcowy N×d, co pociąga za sobą nadmiarowe odczyty i zapisy w HBM. Dla N≥2K uwaga staje się wąskim gardłem po stronie pamięci, zanim zdąży nim zostać po stronie operacji zmiennoprzecinkowych. Klasyczne jądra uwagi nie wykorzystują w pełni możliwości nowoczesnych procesorów graficznych, osiągając zaledwie 10–25% teoretycznej przepustowości.

Dwie optymalizacje, opracowane przez Dao i in., przesunęły wnioskowanie z kategorii „wolne" do „szybkie":

1. **Pamięć podręczna KV.** Wektory K i V każdego tokenu prefiksu są przechowywane w pamięci. Uwaga dla każdego nowego tokenu sprowadza się do jednego zapytania względem zbuforowanych kluczy. Złożoność wnioskowania spada z `O(N²)` do `O(N)` na krok generowania.
2. **Flash Attention.** Obliczenia uwagi są podzielone na bloki tak, aby pełna macierz N×N nigdy nie trafiła do HBM. Całość operacji softmax i mnożenia macierzy odbywa się w SRAM. Daje to przyspieszenie 2–4× na A100 i 5–10× na H100 z FP8.

Do 2026 roku obie techniki są powszechnie stosowane. Każdy produkcyjny stos wnioskowania (vLLM, TensorRT-LLM, SGLang, llama.cpp) zakłada ich obecność. Każdy model z czołówki jest dostarczany z włączonym Flash Attention.

## Koncepcja

![Wzrost pamięci podręcznej KV i kafelkowanie Flash Attention](../assets/kv-cache-flash-attn.svg)

### Matematyka pamięci podręcznej KV

Na warstwę dekodera, na token, na głowicę:

```
bytes_per_token_per_layer = 2 * d_head * dtype_size
                          ^
                          K and V
```

Dla modelu 7B z 32 warstwami, 32 głowicami, d_head=128, fp16:

```
per token per layer = 2 * 128 * 2 = 512 bytes
per token (32 layers) = 16 KB
per 32K context = 512 MB
```

Dla Llamy 3 70B (80 warstw, d_head=128, GQA z 8 głowicami KV):

```
per token per layer = 2 * 8 * 128 * 2 = 4096 bytes (4 KB)
per 32K context = 10.4 GB
```

Te 10 GB oznacza, że Llama 3 70B w kontekście 128K tokenów potrzebuje większości z 40 GB pamięci A100 wyłącznie na pamięć podręczną KV — przy rozmiarze partii równym 1.

**GQA jest optymalnym rozwiązaniem dla pamięci podręcznej KV.** MHA z 64 głowicami zajmuje 32 GB. MLA kompresuje dane jeszcze bardziej.

### Flash Attention — technika kafelkowania

Standardowa uwaga:

```
S = Q @ K^T          (HBM read, N×N, HBM write)
P = softmax(S)       (HBM read, HBM write)
O = P @ V            (HBM read, HBM write)
```

Trzy pełne transfery danych przez HBM. W H100 przepustowość HBM wynosi 3 TB/s, a pamięci SRAM — 30 TB/s. Każdy transfer przez HBM oznacza dziesięciokrotne spowolnienie w porównaniu z obliczeniami wyłącznie na chipie.

Flash Attention:

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

Jeden transfer przez HBM na kafelek. Całkowite zużycie pamięci spada z `O(N²)` do `O(N)`. Przejście wsteczne ponownie oblicza część wartości z przebiegu wprzód zamiast je przechowywać — to kolejna oszczędność pamięci.

**Szczegół numeryczny.** Przyrostowy softmax śledzi parę `(max, sum)` po wszystkich kafelkach, dzięki czemu końcowa normalizacja jest dokładna. Nie jest to przybliżenie — Flash Attention daje wyniki identyczne bitowo ze standardową uwagą (abstrahując od nieasocjatywności fp16).

**Ewolucja wersji:**

| Wersja | Rok | Kluczowa zmiana | Przyspieszenie na sprzęcie referencyjnym |
|--------|------|-----------|-------------------------|
| Flash 1 | 2022 | Kafelkowe jądro SRAM | 2× na A100 |
| Flash 2 | 2023 | Lepsza równoległość, porządek przyczynowy | 3× na A100 |
| Flash 3 | 2024 | Asynchroniczne potokowanie, FP8 | 1,5–2× na H100 (~740 TFLOPS FP16) |
| Flash 4 | 2026 | Pięciostopniowy potok Blackwell, software exp2 | Priorytet wnioskowania (początkowo tylko przejście wprzód) |

Flash 4 obsługuje wyłącznie przejście wprzód na etapie uruchamiania. Trening nadal korzysta z Flash 3. Wsparcie dla GQA i varlen w Flash 4 jest oczekiwane w połowie 2026 roku.

### Dekodowanie spekulatywne — zmniejszanie opóźnień

Tani model pomocniczy proponuje N tokenów. Duży model weryfikuje wszystkie N równolegle. Jeśli weryfikacja akceptuje k tokenów, koszt jednego przebiegu przez duży model przynosi k wygenerowanych tokenów. Typowe k wynosi 3–5 w przypadku kodu i prozy.

Standardowe rozwiązania na rok 2026:
- **EAGLE 2 / Medusa.** Zintegrowane głowice pomocnicze współdzielące ukryte stany weryfikatora. Przyspieszenie 2–3× bez utraty jakości.
- **Dekodowanie spekulatywne z modelem roboczym.** Przyspieszenie 2–4× na sprzęcie konsumenckim.
- **Dekodowanie z wyprzedzeniem.** Iteracja Jacobiego — nie wymaga żadnych zmian w architekturze modelu. Rozwiązanie niszowe, ale bezkosztowe.

### Ciągłe przetwarzanie wsadowe

Klasyczne wnioskowanie wsadowe polega na oczekiwaniu na zakończenie najwolniejszej sekwencji, a dopiero potem na uruchomieniu nowej partii. Powoduje to marnotrawstwo zasobów GPU, gdy krótkie odpowiedzi kończą się znacznie wcześniej.

Ciągłe przetwarzanie wsadowe (wprowadzone w Orca, obecnie stosowane w vLLM, TensorRT-LLM i SGLang) zastępuje zakończone żądania nowymi bez opróżniania partii. Dla typowych obciążeń czatowych przekłada się to na 5–10-krotny wzrost przepustowości.

### PagedAttention — pamięć podręczna KV jako pamięć wirtualna

Kluczowa innowacja vLLM. Pamięć podręczna KV jest przydzielana w blokach po 16 tokenów, a tablica stron odwzorowuje pozycje logiczne na bloki fizyczne. Rozwiązanie to umożliwia współdzielenie wartości KV między równoległymi próbkami (przeszukiwanie wiązką, równoległe próbkowanie), podmianę prefiksów w celu szybkiego buforowania oraz defragmentację pamięci. Daje to czterokrotną poprawę przepustowości w porównaniu z naiwną, ciągłą alokacją.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy:

1. Naiwny dekoder przyrostowy `O(N²)`.
2. Dekoder `O(N)` z pamięcią podręczną KV.
3. Kafelkowy softmax symulujący algorytm Flash Attention w wersji uproszczonej.

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

Zasada jest prosta: wektory K i V każdego tokenu są stopniowo dopisywane do list indeksowanych warstwą i głowicą.

### Krok 2: Kafelkowy softmax

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

Wynik jest identyczny bitowo z `softmax(qK) V` obliczonym jednorazowo, lecz w każdej chwili zestaw roboczy zajmuje jedynie blok `tile × d_head`, a nie pełne `N × d_head`.

### Krok 3: Porównanie dekodera naiwnego i buforowanego przy generacji 100 tokenów

Policz operacje uwagi. Naiwny: `O(N²)` = 5050. Buforowany: `O(N)` = 100. Program wyświetla obie wartości.

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

Buforowanie prefiksów żądań jest w 2026 roku znaczącą korzyścią — ten sam monit systemowy, kilka przykładów lub długi dokument kontekstowy jest ponownie wykorzystywany między wywołaniami. Dla obciążeń agentowych z powtarzającymi się monitami dotyczącymi narzędzi buforowanie prefiksów rutynowo zapewnia pięciokrotny wzrost przepustowości.

## Wyślij to

Zobacz `outputs/skill-inference-optimizer.md`. Umiejętność dobiera implementację uwagi, strategię pamięci podręcznej KV, kwantyzację i dekodowanie spekulatywne dla nowego wdrożenia wnioskowania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Sprawdź, czy dekodery naiwny i buforowany dają ten sam wynik, i odnotuj różnicę w liczbie operacji.
2. **Średnie.** Zaimplementuj buforowanie prefiksów: po otrzymaniu monitu P i kilku uzupełnień wykonaj jedno przejście wprzód przez P, aby wypełnić pamięć podręczną KV, a następnie rozgałęziaj się od tego punktu. Zmierz przyspieszenie w porównaniu z ponownym kodowaniem P dla każdego uzupełnienia.
3. **Trudne.** Zaimplementuj uproszczoną wersję PagedAttention: pamięć podręczna KV w stałych blokach 16-tokenowych z listą wolnych bloków. Po zakończeniu sekwencji zwróć jej bloki do puli. Zasymuluj 1000 zakończeń rozmów o zróżnicowanej długości. Porównaj fragmentację pamięci z alokacją ciągłą.

## Kluczowe terminy

| Termin | Co się o tym mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Pamięć podręczna KV | „Sztuczka przyspieszająca dekodowanie" | Przechowywane wektory K i V każdego tokenu prefiksu; nowe zapytania korzystają z nich zamiast ponownie je obliczać. |
| HBM | „Główna pamięć GPU" | Pamięć o wysokiej przepustowości; 80 GB w H100, 192 GB w B200. Przepustowość ~3 TB/s. |
| SRAM | „Pamięć na chipie" | Szybka pamięć wieloprocesora strumieniowego, ~256 KB na SM w H100. Przepustowość ~30 TB/s. |
| Flash Attention | „Kafelkowe jądro uwagi" | Oblicza uwagę bez materializowania macierzy N×N w HBM. |
| Ciągłe przetwarzanie wsadowe | „Wsadowanie bez oczekiwania" | Zakończone sekwencje są zastępowane nowymi bez opróżniania całej partii. |
| PagedAttention | „Nagłówek vLLM" | Pamięć podręczna KV przydzielana w stałych blokach z tablicą stron; eliminuje fragmentację. |
| Buforowanie prefiksów | „Ponowne użycie długich podpowiedzi" | Wartości KV wspólnego prefiksu są buforowane między żądaniami; znaczące oszczędności w zastosowaniach agentowych. |
| Dekodowanie spekulatywne | „Szkic i weryfikacja" | Tani model pomocniczy proponuje tokeny; duży model weryfikuje k z nich w jednym przebiegu. |

## Dalsze czytanie

- [Dao i in. (2022). FlashAttention: szybka i oszczędzająca pamięć funkcja dokładnej uwagi z funkcją IO-Awareness](https://arxiv.org/abs/2205.14135) — Flash 1.
- [Dao (2023). FlashAttention-2: szybsza uwaga dzięki lepszej równoległości i podziałowi pracy](https://arxiv.org/abs/2307.08691) — Flash 2.
- [Shah i in. (2024). FlashAttention-3: szybka i dokładna uwaga z asynchronią i niską precyzją](https://arxiv.org/abs/2407.08608) — Flash 3.
- [Informacje o wydaniu FlashAttention-4 (Dao-AILab, 2026)](https://github.com/Dao-AILab/flash-attention) — pięciostopniowy potok Blackwell i technika software-exp2; README repozytorium zawiera zastrzeżenia dotyczące trybu tylko wprzód, o których mowa w tej lekcji.
- [Kwon i in. (2023). Efektywne zarządzanie pamięcią dla dużych modeli językowych za pomocą PagedAttention](https://arxiv.org/abs/2309.06180) — artykuł vLLM.
- [Leviathan i in. (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — dekodowanie spekulatywne.
- [Li i in. (2024). EAGLE: Próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności cech](https://arxiv.org/abs/2401.15077) — artykuł EAGLE-1/2 dotyczący podejścia zintegrowanego omawianego w lekcji.
- [Cai i in. (2024). Medusa: prosta architektura przyspieszania wnioskowania LLM z wieloma głowicami dekodującymi](https://arxiv.org/abs/2401.10774) — podejście Medusa, do którego nawiązuje EAGLE.
- [Dokumentacja vLLM — PagedAttention](https://docs.vllm.ai/en/latest/design/kernel/paged_attention.html) — szczegółowe omówienie bloku 16-tokenowego i projektu tablicy stron.
