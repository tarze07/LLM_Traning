# Kwantyzacja produkcji — AWQ, GPTQ, GGUF K-kwanty, FP8, MXFP4/NVFP4

> Format kwantyzacji nie jest wyborem uniwersalnym — jest funkcją sprzętu, silnika obsługującego i obciążenia. GGUF Q4_K_M lub Q5_K_M jest właścicielem procesora i krawędzi, dostarczanych przez llama.cpp i Ollama. GPTQ wygrywa w vLLM, gdy potrzebujesz wielu LoRA na tej samej bazie. AWQ z jądrami Marlin-AWQ zapewnia ~741 tok/s w modelu klasy 7B z najlepszą przepustką@1 na poziomie INT4 — wartość domyślna na rok 2026 dla produkcji w centrach danych. 8PR pozostaje środkiem w przypadku Hoppera, Ady i Blackwella — niemal bezstratnie i szeroko wspierany. NVFP4 i MXFP4 (mikroskalowanie Blackwella) są agresywne i wymagają sprawdzania poprawności każdego bloku. Zespoły gryzły dwie pułapki: zestaw danych kalibracyjnych musi pasować do domeny wdrożenia, a pamięć podręczna KV jest oddzielona od kwantyzacji wagi — lekcja AWQ „mój model ma teraz 4 GB” zapomina o pamięci podręcznej KV o wielkości 10–30 GB w przypadku partii produkcyjnych.

**Typ:** Ucz się
**Języki:** Python (stdlib, porównanie pamięci zabawek i przepustowości w różnych formatach)
**Wymagania wstępne:** Faza 10 · 13 (podstawy kwantyzacji), faza 17 · 04 (wewnętrzne elementy obsługujące vLLM)
**Czas:** ~75 minut

## Cele nauczania

- Wymień sześć formatów kwantyzacji produkcji i ich najlepsze punkty w 2026 r.
- Wybierz format, biorąc pod uwagę sprzęt (CPU vs GPU, Hopper vs Blackwell), silnik (vLLM, TRT-LLM, llama.cpp) i obciążenie (rutynowy czat, wnioskowanie, multi-LoRA).
- Oblicz zapisaną pamięć wagi i pamięć podręczną KV pozostawioną nietkniętą dla wybranego formatu.
- Podaj nazwę pułapki związanej ze zbiorem danych kalibracyjnych, która pogarsza skwantowane modele w ruchu domenowym.

## Problem

Kwantyzacja zmniejsza przepustowość pamięci i HBM, czyli dokładnie to, czego potrzebuje dekodowanie. Model FP16 70B to 140 GB obciążników. Kwantyzuj wagi do INT4 (AWQ lub GPTQ), a model ma 35 GB — mieści się w jednym H100 z miejscem na pamięć podręczną KV, co ma znaczenie, ponieważ przy 128 współbieżnych sekwencjach z kontekstem 2 kB, sama pamięć podręczna KV wynosi 20–30 GB.

Ale kwantyzacja nie jest darmowa. Agresywna kwantyzacja pogarsza jakość, szczególnie w przypadku zadań wymagających intensywnego rozumowania. Różne formaty współpracują z różnymi silnikami. Różny sprzęt obsługuje natywnie różne precyzje. Zoo w formacie 2026 jest prawdziwe i nie możesz skopiować czyjegoś wyboru – musisz wybierać na podstawie swojego stosu.

## Koncepcja

### Sześć formatów

| Formatuj | Bity | Słodkie miejsce | Silniki |
|------------|------|-----------|---------|
| GGUF Q4_K_M / Q5_K_M | 4-5 | Procesor, brzeg, laptopy | llama.cpp, Ollama |
| GPTQ | 4-8 | Multi-LoRA na vLLM | vLLM, TGI |
| AWQ | 4 | Produkcja procesorów graficznych dla centrów danych | vLLM (Marlin-AWQ), TGI |
| 8PR | 8 | Centrum danych Hopper/Ada/Blackwell | vLLM, TRT-LLM, SGLang |
| MXFP4 | 4 | Blackwell dla wielu użytkowników | TRT-LLM |
| NVFP4 | 4 | Blackwell dla wielu użytkowników | TRT-LLM |

### GGUF — ustawienie domyślne procesora/krawędzi

GGUF to format pliku, a nie schemat kwantyzacji jako taki — łączy warianty K-kwantowe (Q2_K, Q3_K_M, Q4_K_M, Q5_K_M, Q6_K, Q8_0) w jednym kontenerze. Q4_K_M i Q5_K_M to domyślne ustawienia produkcyjne — jakość bliska BF16 przy 4-5 bitach. Najlepszy wybór do obsługi procesora lub brzegu, ponieważ lama.cpp jest zdecydowanie najszybszym silnikiem wnioskowania o procesorze.

Zmniejszenie przepustowości w vLLM: ~93 tok/s na 7B — format nie jest zoptymalizowany pod kątem jąder GPU. Użyj GGUF, gdy celem wdrożenia jest procesor/krawędź. Nie inaczej.

### GPTQ — multi-LoRA w vLLM

GPTQ to algorytm kwantyzacji po treningu z przejściem kalibracji. Jądra Marlin sprawiają, że jest szybki na GPU (przyspieszenie 2,6x w porównaniu z GPTQ innym niż Marlin). ~712 tok/s na 7B.

Wyjątkowa wygrana: GPTQ-Int4 obsługuje adaptery LoRA w vLLM. Jeśli obsługujesz model podstawowy i 10–50 dopracowanych wariantów (każdy jako LoRA), GPTQ jest Twoją ścieżką. NVFP4 nie obsługuje jeszcze LoRA od początku 2026 roku.

### AWQ — domyślny procesor graficzny centrum danych

Kwantyzacja wagowa uwzględniająca aktywację. Chroni ~1% najważniejszych wag podczas kwantyzacji. Jądra Marlin-AWQ: przyspieszenie 10,9x w porównaniu do wersji naiwnej. ~741 tok/s na 7B, najlepszy Pass@1 wśród formatów INT4.

Wybierz AWQ do obsługi nowych procesorów graficznych, chyba że potrzebujesz multi-LoRA (GPTQ) lub agresywnego Blackwell FP4 (NVFP4).

### 8PR — niezawodny środek

8-bitowy zmiennoprzecinkowy. Prawie bezstratny. Szeroko wspierane. Rdzenie Hopper Tensor natywnie przyspieszają FP8. Blackwell dziedziczy. 8PR to bezpieczny domyślny program na rok 2026, gdy jakość nie podlega negocjacjom (rozumowanie, medycyna, generowanie kodu). Oszczędność pamięci wynosi połowę wartości INT4, ale ryzyko jakości jest znacznie niższe.

### MXFP4 / NVFP4 — Blackwell agresywny

Mikroskalowanie FP4. Każdy blok odważników ma swój własny współczynnik skali. Agresywny, ale przyspieszany sprzętowo na rdzeniach Blackwell Tensor. Zmniejsz o połowę liczbę bajtów na token w porównaniu z 8PR — zwycięstwo ekonomiczne w fazie 17 · 07.

Zastrzeżenia:
- Brak jeszcze obsługi LoRA (początek 2026 r.).
- Spadek jakości widoczny w przypadku obciążeń wymagających dużego obciążenia rozumowaniem.
- Sprawdź swój zestaw ewaluacyjny dla każdego modelu.

### Pułapka kalibracyjna

AWQ i GPTQ wymagają zestawu danych kalibracyjnych — zazwyczaj C4 lub WikiText. W przypadku modeli domen (kodowych, medycznych, prawnych) kalibracja na ogólnym tekście internetowym pozwala algorytmowi podejmować błędne decyzje dotyczące wag, które należy chronić. Pass@1 na HumanEval może spowodować utratę kilku punktów.

Poprawka: kalibracja na danych w domenie. Zwykle wystarczą setki próbek domen. Przed wysyłką przetestuj zestaw eval.

### Pułapka pamięci podręcznej KV

AWQ zmniejsza wagę do 4 bitów. Pamięć podręczna KV jest oddzielna i pozostaje na poziomie FP16/FP8. Dla modelu 70B z AWQ:

- Waga: ~35 GB (INT4 od 140 GB).
- Pamięć podręczna KV przy 128 jednoczesnych kontekstach × 2 tys.: ~20 GB.
- Aktywacje: ~5 GB.
- Łącznie: ~60 GB - pasuje do H100 80 GB.

Naiwnie „skwantowałem swój model do 4 GB” zapomina o pozostałych 30-50 GB. Budżet HBM całościowo.

Osobno kwantyzacja pamięci podręcznej KV (FP8 KV lub INT8 KV) to inny wybór, mający swoje własne kompromisy — wpływa bezpośrednio na dokładność uwagi i nie jest darmową wygraną.

### AWQ INT4 jest niebezpieczne dla rozumowania

Łańcuch myślowy, matematyka, generowanie kodu z długim kontekstem – te elementy wyraźnie cierpią z powodu agresywnej kwantyzacji. AWQ INT4 traci ~3-5 punktów na MATH. W przypadku zadań wymagających dużego rozumowania użyj FP8 lub BF16; zaakceptować koszt pamięci.

### Przewodnik kompletacji na rok 2026

- Serwer procesora/kraju: GGUF Q4_K_M. Zrobione.
- Obsługa GPU, rutynowy czat, brak LoRA: AWQ.
- Obsługa GPU, multi-LoRA: GPTQ z Marlinem.
- Nakład pracy związany z rozumowaniem: 8PR.
- Centrum danych Blackwell, sprawdzona jakość: NVFP4 + FP8 KV.
- Niejednoznaczne: przeprowadzić ocenę 1000 próbek dla każdego formatu kandydata.

## Użyj tego

`code/main.py` oblicza wielkość pamięci (wagi + KV + aktywacje) i względną przepustowość w sześciu formatach dla różnych rozmiarów modeli. Pokazuje, gdzie dominuje pamięć podręczna KV, gdzie opłaca się kompresja ciężaru i gdzie FP8 jest bezpiecznym wyborem.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-quantization-picker.md`. Biorąc pod uwagę sprzęt, rozmiar modelu, rodzaj obciążenia i tolerancję jakości, wybiera format i tworzy plan kalibracji/walidacji.

## Ćwiczenia

1. Uruchom `code/main.py`. Dla modelu 70B przy 128 jednocześnie z kontekstem 2k oblicz całkowity HBM dla każdego formatu. Jaki format pozwala zmieścić się na jednym urządzeniu H100 80 GB?
2. Masz model kodowania 7B. Wybierz format i uzasadnij. Jeśli mylisz się co do tolerancji jakości, jaka jest ścieżka odzyskiwania?
3. Oblicz rozmiar zbioru danych kalibracyjnych potrzebny do kalibracji AWQ dla modelu dziedziny medycznej. Dlaczego więcej danych nie zawsze oznacza lepiej?
4. Przeczytaj dokument jądra Marlin-AWQ lub uwagi do wydania. Wyjaśnij w trzech zdaniach, dlaczego AWQ osiąga 741 tok/s na 7B, podczas gdy surowy GPTQ osiąga ~712.
5. Kiedy ma sens łączenie wag AWQ z pamięcią podręczną KV FP8 zamiast utrzymywania KV na poziomie BF16?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| GGUF | „Format lamy.cpp” | Format pliku obejmujący warianty K-kwantowe; Domyślny procesor/krawędź |
| Q4_K_M | „Q4 K M” | 4-bitowy nośnik kwantowy K; produkcja domyślna GGUF |
| GPTQ | „Ojej, tee q” | Po pociągu INT4 z kalibracją; obsługuje LoRA w vLLM |
| AWQ | "a w q" | INT4 obsługujący aktywację; jądra marlina; najlepsza przepustka@1 w INT4 |
| Jądra Marlina | „szybkie jądra INT4” | Niestandardowe jądra CUDA dla INT4 na Hopperze; 10-krotne przyspieszenie |
| 8PR | „ośmibitowy float” | Bezpieczna precyzja domyślna w Hopper/Ada/Blackwell |
| MXFP4 / NVFP4 | „mikroskalowa czwórka” | Blackwell 4-bitowy FP ze współczynnikami skali na blok |
| Zbiór danych kalibracyjnych | „dane kal.” | Tekst wejściowy używany do wybierania parametrów kwantyzacji; musi pasować do domeny |
| Kwantyzacja pamięci podręcznej KV | „KV INT8” | Oddzielny wybór od ciężarków; wpływa na dokładność uwagi |

## Dalsze czytanie

- [VRLA Tech — LLM Quantization 2026](https://vrlatech.com/llm-quantization-explained-int4-int8-fp8-awq-and-gptq-in-2026/) — testy porównawcze.
- [Jarvis Labs — kompletny przewodnik po kwantyzacji vLLM](https://jarvislabs.ai/blog/vllm-quantization-complete-guide-benchmarks) — liczby przepustowości według formatu.
- [PremAI — GGUF vs AWQ vs GPTQ vs bitsandbytes 2026](https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/) — wybieranie format po formacie.
- [dokumentacja vLLM — Kwantyzacja](https://docs.vllm.ai/en/latest/features/quantization/index.html) — obsługiwane formaty i flagi.
- [Artykuł AWQ (arXiv:2306.00978)](https://arxiv.org/abs/2306.00978) — oryginalne sformułowanie AWQ.
- [Dokument GPTQ (arXiv:2210.17323)](https://arxiv.org/abs/2210.17323) — oryginalne sformułowanie GPTQ.