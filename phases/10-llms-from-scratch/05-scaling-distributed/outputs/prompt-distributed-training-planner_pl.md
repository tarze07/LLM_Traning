---

name: prompt-distributed-training-planner
description: Zaplanuj rozproszone szkolenie, biorąc pod uwagę rozmiar modelu i dostępny sprzęt
version: 1.0.0
phase: 10
lesson: 5
tags: [distributed-training, fsdp, deepspeed, tensor-parallelism, pipeline-parallelism, scaling]

---

# Rozproszony planista szkoleń

Planując przebieg szkolenia rozproszonego dla dużego modelu języka, użyj tej struktury, aby określić strategię równoległości, budżet pamięci, obciążenie komunikacyjne i oczekiwaną przepływność.

## Wymagania wejściowe

Zapewnij:
- **Rozmiar modelu** (parametry w miliardach)
- **Docelowe żetony szkoleniowe** (w bilionach)
- **Dostępne procesory graficzne** (typ: A100/H100/H200, liczba, połączenie: NVLink/InfiniBand)
- **Pamięć GPU** (80 GB dla A100/H100, 141 GB dla H200)
- **Węzły** (procesory graficzne na węzeł, liczba węzłów)
- **Ograniczenia budżetowe** (maksymalny koszt w dolarach, maksymalny czas zegara ściennego)

## Krok 1: Budżet pamięci

Oblicz pamięć na GPU dla każdego komponentu:

| Składnik | Formuła | FP16 | FP32 |
|----------|---------|------|------|
| Ciężary | parametry x bajty_na_param | parametry x 2 | parametry x 4 |
| Optymalizator Adama (m + v) | parametry x 4 x 2 | 8 bajtów/parametr zawsze | 8 bajtów/parametr |
| Gradienty | parametry x bajty_na_param | parametry x 2 | parametry x 4 |
| Aktywacje (oszacowanie) | seq_len x partia x ukryta x warstwy x 2 | różni się | różni się |

Jeśli suma przekracza pamięć GPU, wymagane jest sharding. Spróbuj po kolei:
1. ZeRO-1 (tylko optymalizator shard) - najtańsza komunikacja
2. ZeRO-2 (+ gradienty) – komunikacja umiarkowana
3. FSDP/ZeRO-3 (+ wagi) - najwyższa komunikacja, ale maksymalna oszczędność pamięci
4. Dodaj punkt kontrolny aktywacji, jeśli aktywacje są nadal zbyt duże
5. Dodaj równoległość tensora, jeśli pojedyncza warstwa nie mieści się na jednym GPU

## Krok 2: Strategia równoległości

### Drzewo decyzyjne

1. **Czy jedna warstwa mieści się na jednym GPU?**
   - Nie: potrzebujesz równoległości tensorów. Ustaw TP = 2, 4 lub 8 (w węźle).
   - Tak: Pomiń równoległość tensora.

2. **Czy pełny model (z fragmentowaniem) mieści się na procesorach graficznych w jednym węźle?**
   - Nie: potrzebujesz równoległości rurociągu. Ustaw PP = liczba węzłów/grup.
   - Tak: Pomiń równoległość potoku.

3. **Ile pozostałych procesorów graficznych dla równoległości danych?**
   - DP = total_gpus / (TP x PP)

4. **Jaki poziom fragmentowania w grupie równoległej danych?**
   - Zacznij od FSDP (ZeRO-3). Jeśli komunikacja stanowi wąskie gardło, zredukuj do ZeRO-2 lub ZeRO-1.

### Typowe konfiguracje

| Rozmiar modelu | Całkowita liczba procesorów graficznych | TP | PP | DP | Odłamki |
|-----------|-----------|----|----|-----|----------|
| 7B | 8 | 1 | 1 | 8 | FSDP |
| 13B | 16 | 2 | 1 | 8 | FSDP |
| 70B | 64 | 8 | 1 | 8 | FSDP |
| 70B | 128 | 8 | 2 | 8 | FSDP |
| 405B | 16 384 | 8 | 16 | 128 | FSDP |

## Krok 3: Analiza komunikacji

Oszacuj wielkość komunikacji na etap szkolenia:

- **Dane równoległe (all-reduce)**: 2 x gradient_size x (N-1)/N na krok
- **FSDP (zebranie całościowe + redukcja rozproszenia)**: ~3 x rozmiar_wagi x (N-1)/N na krok (wyższy niż DP)
- **Tensor równoległy (all-reduce na warstwę)**: 2 x aktywacja_rozmiar x liczba_warstw na krok (wymaga NVLink)
- **Równoległy rurociąg (od punktu do punktu)**: rozmiar_aktywacji na granicę etapu (minimalny)

Jeśli czas komunikacji przekracza 20% czasu obliczeń, strategia jest powiązana z komunikacją. Rozwiązania:
- Akumulacja gradientu (zmniejsz wszystko-zmniejsz częstotliwość)
- Nakładanie się komunikacji z obliczeniami (FSDP robi to domyślnie)
— Zwiększenie rozmiaru mikropartii (lepszy stosunek mocy obliczeniowej do komunikacji)
— Przejdź na etap fragmentowania mniej obciążający komunikację

## Krok 4: Szacowanie przepustowości i kosztów

**FLOPS na krok treningu:**
- Do przodu: ~2 x parametry x tokens_per_batch
- Wstecz: ~4 x parametry x tokens_per_batch (2x do przodu)
- Razem: ~6 x parametry x tokens_per_batch

**Czas szkolenia:**
- total_flops = 6 x parametry x total_tokens
- time_sekundy = total_flops / (num_gpus x gpu_tflops x 1e12 x wykorzystanie)
- Typowe wykorzystanie: 35-45% (uwzględniając komunikację, pęcherzyki w rurociągach, obciążenie pamięci)

**Koszt:**
- total_gpu_hours = liczba_gpu x czas_sekund / 3600
- koszt = całkowita_godzina_gpu x koszt_godziny_gpu

## Krok 5: Lista kontrolna walidacji

Przed uruchomieniem:

1. Pamięć na procesor graficzny mieści się w limicie sprzętowym (z zapasem 10%)
2. Efektywny rozmiar partii jest zgodny z celem (per_gpu_batch x DP x gradient_accumulation_steps)
3. Stosunek komunikacji do mocy obliczeniowej jest poniżej 20%
4. Frakcja pęcherzyków w rurociągu jest poniżej 15% (wystarczająca ilość mikropartii)
5. Szybkość uczenia się jest skalowana dla efektywnej wielkości partii
6. Częstotliwość punktów kontrolnych uwzględnia prawdopodobieństwo awarii (w przypadku dużych serii zapisz co 1-2 godziny)
7. Ustawiono przycinanie gradientu (zwykle 1,0 dla dużych modeli)
8. Kroki rozgrzewki są proporcjonalne do całkowitej liczby kroków (zwykle 0,1-1% całości)

## Czerwone flagi

- **TP > 8**: Równoległość tensorów między węzłami (przez InfiniBand) jest prawie zawsze wolniejsza niż równoległość potoków
- **Etapy rurociągu > 32**: Narzut pęcherzyków staje się znaczący nawet w przypadku wielu mikropartii
- **Efektywna wielkość partii > 10 mln tokenów**: Malejące zyski; może zaszkodzić konwergencji
- **Wykorzystanie poniżej 30%**: Związane z komunikacją – ponownie oceń strategię równoległości
- **Brak punktów kontrolnych aktywacji powyżej 13B**: Podczas przejścia wstecz zabraknie Ci pamięci
- **Brak akumulacji gradientów przy małych partiach przypadających na procesor graficzny**: Zwiększa się szum gradientu; zgromadzić do efektywnej partii ponad 256 próbek