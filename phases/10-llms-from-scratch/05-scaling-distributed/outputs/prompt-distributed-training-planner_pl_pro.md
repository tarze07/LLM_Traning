---

name: prompt-distributed-training-planner
description: Zaplanuj rozproszone szkolenie, biorąc pod uwagę rozmiar modelu i dostępny sprzęt
version: 1.0.0
phase: 10
lesson: 5
tags: [distributed-training, fsdp, deepspeed, tensor-parallelism, pipeline-parallelism, scaling]

---

# Planowanie rozproszonego treningu LLM

Planując rozproszony trening dużego modelu językowego (LLM), użyj poniższego schematu, aby określić strategię równoległości, budżet pamięci, obciążenie komunikacyjne oraz oczekiwaną przepustowość.

## Wymagania wejściowe

Podaj:
- **Rozmiar modelu** (liczba parametrów w miliardach – B)
- **Docelowa liczba tokenów treningowych** (w bilionach – T)
- **Dostępne układy GPU** (typ: A100/H100/H200, liczba, rodzaj połączenia: NVLink/InfiniBand)
- **Pamięć VRAM GPU** (np. 80 GB dla A100/H100, 141 GB dla H200)
- **Węzły (Nodes)** (liczba układów GPU na węzeł, całkowita liczba węzłów)
- **Ograniczenia projektowe** (maksymalny budżet finansowy, maksymalny czas rzeczywisty – wall-clock time)

## Krok 1: Budżet pamięci (VRAM)

Oblicz zapotrzebowanie na pamięć jednego układu GPU dla każdego komponentu:

| Komponent | Wzór | FP16 | FP32 |
|----------|---------|------|------|
| Wagi | parametry x bajty_na_parametr | parametry x 2 | parametry x 4 |
| Optymalizator Adam (m + v) | parametry x 4 x 2 | Zawsze 8 bajtów/parametr | Zawsze 8 bajtów/parametr |
| Gradienty | parametry x bajty_na_parametr | parametry x 2 | parametry x 4 |
| Aktywacje (szacunkowo) | seq_len x batch_size x hidden_dim x layers x 2 | Zmienne | Zmienne |

Jeśli suma przekracza pamięć GPU, konieczne jest zastosowanie shardingu (podziału danych). Wypróbuj kolejno następujące metody:
1. ZeRO-1 (tylko sharding stanów optymalizatora) – najniższy narzut komunikacyjny
2. ZeRO-2 (+ sharding gradientów) – umiarkowany narzut komunikacyjny
3. FSDP/ZeRO-3 (+ sharding wag) – najwyższy narzut komunikacyjny, ale maksymalna oszczędność pamięci
4. Aktywacja checkpointingu (activation checkpointing), jeśli aktywacje wciąż zajmują zbyt dużo miejsca
5. Równoległość tensorowa (Tensor Parallelism), jeśli pojedyncza warstwa nie mieści się na jednym GPU

## Krok 2: Strategia równoległości

### Drzewo decyzyjne

1. **Czy pojedyncza warstwa mieści się na jednym GPU?**
   - Nie: wymagana jest równoległość tensorowa (Tensor Parallelism). Ustaw TP = 2, 4 lub 8 (w obrębie jednego węzła).
   - Tak: pomiń równoległość tensorową.

2. **Czy cały model (po zastosowaniu shardingu) mieści się w pamięci GPU pojedynczego węzła?**
   - Nie: wymagana jest równoległość potokowa (Pipeline Parallelism). Ustaw PP = liczba węzłów/grup.
   - Tak: pomiń równoległość potokową.

3. **Ile GPU pozostaje dla równoległości danych (Data Parallelism)?**
   - DP = total_gpus / (TP x PP)

4. **Jaki poziom shardingu zastosować w grupie równoległości danych?**
   - Zacznij od FSDP (ZeRO-3). Jeśli komunikacja stanie się wąskim gardłem, przejdź na ZeRO-2 lub ZeRO-1.

### Typowe konfiguracje

| Rozmiar modelu | Całkowita liczba GPU | TP | PP | DP | Sharding |
|-----------|-----------|----|----|-----|----------|
| 7B | 8 | 1 | 1 | 8 | FSDP |
| 13B | 16 | 2 | 1 | 8 | FSDP |
| 70B | 64 | 8 | 1 | 8 | FSDP |
| 70B | 128 | 8 | 2 | 8 | FSDP |
| 405B | 16 384 | 8 | 16 | 128 | FSDP |

## Krok 3: Analiza narzutu komunikacyjnego

Oszacuj wolumen przesyłanych danych na jeden krok treningowy:

- **Równoległość danych (Data Parallel - all-reduce)**: `2 x gradient_size x (N-1)/N` na krok
- **FSDP (all-gather + reduce-scatter)**: `~3 x rozmiar_wag x (N-1)/N` na krok (wartość wyższa niż przy standardowym DP)
- **Równoległość tensorowa (all-reduce na warstwę)**: `2 x rozmiar_aktywacji x liczba_warstw` na krok (wymaga szybkiego łącza NVLink)
- **Równoległość potokowa (point-to-point)**: `rozmiar_aktywacji` na granicach etapów potoku (minimalny wolumen)

Jeśli czas komunikacji przekracza 20% czasu obliczeń, potok jest ograniczony przez komunikację (communication-bound). Sugerowane rozwiązania:
- Akumulacja gradientów (zmniejszenie częstotliwości operacji all-reduce)
- Nakładanie na siebie komunikacji i obliczeń (FSDP wykonuje to domyślnie)
- Zwiększenie rozmiaru mikro-batcha (poprawia stosunek obliczeń do komunikacji)
- Przejście na wariant shardingu o niższym narzut komunikacyjnym

## Krok 4: Szacowanie przepustowości i kosztów

**Liczba operacji FLOP na krok treningu:**
- Przejście w przód (forward pass): `~2 x parametry x tokens_per_batch`
- Przejście wsteczne (backward pass): `~4 x parametry x tokens_per_batch` (dwukrotność przejścia w przód)
- Razem: `~6 x parametry x tokens_per_batch`

**Czas treningu:**
- `total_flops = 6 x parametry x total_tokens`
- `time_seconds = total_flops / (num_gpus x gpu_tflops x 1e12 x MFU)`
- Typowe MFU (Model FLOPs Utilization): 35-45% (uwzględnia narzut komunikacyjny, bąble potoku – pipeline bubbles oraz narzut pamięciowy)

**Koszt:**
- `total_gpu_hours = num_gpus x time_seconds / 3600`
- `koszt = total_gpu_hours x koszt_gpu_na_godzine`

## Krok 5: Lista kontrolna walidacji

Przed uruchomieniem:

1. Zapotrzebowanie na pamięć VRAM na pojedynczym GPU mieści się w limicie sprzętowym (z zachowaniem 10% marginesu bezpieczeństwa).
2. Globalny rozmiar batcha (global batch size) jest zgodny z założeniami (`per_gpu_batch x DP x gradient_accumulation_steps`).
3. Narzut komunikacyjny w stosunku do mocy obliczeniowej nie przekracza 20%.
4. Udział bąbli potoku (pipeline bubble fraction) wynosi poniżej 15% (wymaga odpowiedniej liczby mikro-batchy).
5. Współczynnik uczenia (learning rate) jest odpowiednio skalowany do efektywnego, globalnego rozmiaru batcha.
6. Częstotliwość zapisu checkpointów uwzględnia średni czas bezawaryjnej pracy sprzętu (dla dużych procesów zaleca się zapis co 1-2 godziny).
7. Skonfigurowano obcinanie gradientów (gradient clipping, zazwyczaj próg ustawiony na 1.0 dla dużych modeli).
8. Liczba kroków rozgrzewki (warmup steps) jest proporcjonalna do całkowitej liczby kroków (zazwyczaj 0,1–1% całości).

## Sygnały ostrzegawcze (czerwone flagi)

- **TP > 8**: Stosowanie równoległości tensorowej (Tensor Parallelism) między węzłami (za pomocą InfiniBand) jest prawie zawsze wolniejsze niż równoległość potokowa (Pipeline Parallelism).
- **PP stages > 32 (liczba etapów potoku)**: Narzut bąbli potoku staje się znaczący, nawet przy dużej liczbie mikro-batchy.
- **Efektywny, globalny rozmiar batcha > 10 mln tokenów**: Pojawia się problem malejących przychodów (diminishing returns); może to również negatywnie wpłynąć na konwergencję modelu.
- **MFU poniżej 30%**: Trening jest silnie ograniczony komunikacją – należy ponownie przeanalizować i zoptymalizować strategię równoległości.
- **Brak checkpointingu aktywacji (activation checkpointing) dla modeli powyżej 13B**: Istnieje ogromne ryzyko wystąpienia błędu Out of Memory (OOM) podczas przejścia wstecznego (backward pass).
- **Brak akumulacji gradientów przy małym rozmiarze batcha na pojedynczy GPU**: Prowadzi to do zbyt wysokiego szumu gradientu. Należy akumulować gradienty, aby uzyskać globalny rozmiar batcha odpowiadający co najmniej 256 próbkom.
