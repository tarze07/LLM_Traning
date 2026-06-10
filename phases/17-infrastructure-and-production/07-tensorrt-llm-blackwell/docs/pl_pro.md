# TensorRT-LLM na Blackwell z FP8 i NVFP4

> TensorRT-LLM to rozwiązanie dedykowane wyłącznie dla procesorów graficznych NVIDIA, ale na architekturze Blackwell osiąga bezkonkurencyjne wyniki. W przypadku GB200 NVL72 z orkiestracją Dynamo, narzędzie SemiAnalytic InferenceX w pierwszej połowie 2026 r. wykazało koszt na poziomie 0,012 USD za milion tokenów dla modelu 120B, w porównaniu do 0,09 USD/M na układach H100 z vLLM. Oznacza to ponad 7-krotną redukcję kosztów. Stos wykorzystuje trzy formaty zmiennoprzecinkowe: FP8 pozostaje kluczowy dla kerneli pamięci podręcznej KV i mechanizmu uwagi (attention), ponieważ zapewnia wymagany zakres dynamiczny; NVFP4 (4-bitowe mikroskalowanie) obsługuje wagi i aktywacje; natomiast przewidywanie wielu tokenów (MTP) oraz zdezagregowane fazy prefill/decode dają dodatkowe 2-3-krotne przyspieszenie. Obsługa modeli od pierwszego dnia (Day 0) umożliwia bezpośrednie ładowanie wag FP4 bez konieczności przeprowadzania konwersji po treningu. Haczyk dla zespołów inżynieryjnych w 2026 roku: TRT-LLM to zamknięty stos NVIDIA, co oznacza, że jego wdrożenie wymaga rezygnacji z przenośności kodu na rzecz maksymalnej przepustowości. Przed podjęciem ostatecznej decyzji należy dokładnie przeanalizować koszty dla konkretnych modeli i konfiguracji sprzętowych.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulacja pamięci FP8/NVFP4 i kalkulator kosztów)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy vLLM), Faza 10 · 13 (Kwantyzacja)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego FP8 pozostaje kluczowy dla pamięci podręcznej KV i mechanizmu uwagi, nawet gdy wagi są zapisane w formacie NVFP4.
- Oblicz zapotrzebowanie na pamięć HBM dla modeli granicznych w formatach BF16, FP8 oraz NVFP4 i uzasadnij źródło oszczędności.
- Wymień funkcje specyficzne dla architektury Blackwell wykorzystywane przez TRT-LLM (Day 0, FP4, MTP, zdezagregowane wnioskowanie, operacje komunikacyjne all-to-all).
- Zdecyduj, kiedy uzależnienie technologiczne (lock-in) od NVIDIA TRT-LLM jest warte 7-krotnej redukcji kosztów w porównaniu z vLLM na architekturze Hopper.

## Problem

Granica opłacalności wnioskowania w 2026 r. sprowadza się do pytania: „ile tokenów można wygenerować za jednego dolara”. Odpowiedź zależy od czterech powiązanych ze sobą decyzji projektowych: generacji sprzętu (Hopper H100/H200 vs Blackwell B200/GB200), precyzji obliczeń (BF16 → FP8 → NVFP4), silnika serwującego (vLLM vs SGLang vs TRT-LLM) oraz orkiestracji (standardowa vs zdezagregowana vs Dynamo).

Na architekturze Hopper z silnikiem vLLM model MoE 120B działa przy koszcie ok. 0,09 USD za milion tokenów. Na Blackwell z TRT-LLM + Dynamo ten sam model osiąga koszt ok. 0,012 USD – czyli jest 7 razy tańszy. Część tej różnicy wynika ze sprzętu (przepustowość Blackwell na GPU w zadaniach LLM jest 11–15 razy większa w porównaniu z Hopperem). Pozostała część to zasługa stosu technologicznego: wagi FP4, model pomocniczy MTP (draft model), zdezagregowane fazy prefill/decode oraz sieć NVLink 5 realizująca komunikację all-to-all dla ekspertów MoE.

Tego efektu nie da się odtworzyć poza ekosystemem NVIDIA. Na tym polega kompromis – rezygnujemy z przenośności na rzecz ekonomii. Celem tej lekcji jest zrozumienie, które elementy stosu odpowiadają za poszczególne części tej przewagi kosztowej.

## Koncepcja

### Dlaczego FP8 to nadal podstawa dla pamięci podręcznej KV

Częsty błąd w 2026 r. polega na zakładaniu, że format NVFP4 można zastosować wszędzie. Tak nie jest. Pamięć podręczna KV wymaga formatu FP8 (8-bitowy zmiennoprzecinkowy), ponieważ przechowuje klucze i wartości uwagi (attention keys/values) charakteryzujące się szerokim zakresem dynamiki. Kwantyzacja KV do FP4 powoduje drastyczny spadek dokładności – wartości skrajne (ogon rozkładu) zostają odcięte, co prowadzi do załamania wyników mechanizmu uwagi. Bity wykładnika w formacie FP8 zapewniają buforowi KV niezbędny zakres wartości.

Format NVFP4 (w latach 2025-2026) jest stosowany do wag i aktywacji. Mikroskalowanie polega na tym, że każdy blok wag posiada własny współczynnik skali, dzięki czemu małe bloki mogą reprezentować różne zakresy dynamiczne bez utraty dokładności skalowania na poziomie całego tensora. W przypadku aktywacji format FP4 sprawdza się, ponieważ mają one ograniczony zakres w obrębie pojedynczej warstwy.

Typowa konfiguracja na architekturze Blackwell:

- Wagi: NVFP4 (4-bitowe mikroskalowanie).
- Aktywacje: NVFP4.
- Pamięć podręczna KV: FP8.
- Akumulator uwagi (attention accumulator): FP32 (dla stabilności operacji softmax).

### Prymitywy specyficzne dla Blackwell, których używa TRT-LLM

- **Wagi FP4 od pierwszego dnia (Day 0)**: Dostawcy modeli udostępniają wagi bezpośrednio w formacie FP4; TRT-LLM uruchamia je bez konieczności konwersji post-trainingowej. Pominięty zostaje etap AWQ/GPTQ dla FP4.
- **Przewidywanie wielu tokenów (MTP)**: Rozwiązanie oparte na tej samej idei co EAGLE (Faza 17 · 05), ale zintegrowane bezpośrednio z procesem kompilacji TRT-LLM.
- **Zdezagregowane wnioskowanie (Disaggregated Serving)**: Realizacja faz prefill i decode na osobnych pulach GPU, przy czym pamięć podręczna KV jest przesyłana za pośrednictwem NVLink lub InfiniBand. Koncepcja tożsama z Dynamo (Faza 17 · 20).
- **Prymitywy komunikacji all-to-all**: Sieć NVLink 5 zmniejsza opóźnienia w komunikacji między ekspertami MoE 3-krotnie w porównaniu z Hopperem. Jądra MoE w TRT-LLM są zoptymalizowane pod tym kątem.
- **Mikroskalowanie NVFP4 + MXFP8**: Sprzętowo przyspieszana obsługa współczynników skalowania w rdzeniach Tensor architektury Blackwell.

### Liczby, które powinieneś zapamiętać

- Koszt 0,02 USD/M tokenów dla GPT-OSS-120B na HGX B200 przy użyciu TRT-LLM.
- Koszt 0,012 USD/M tokenów na GB200 NVL72 przy użyciu orkiestracji Dynamo (pod kontrolą TRT-LLM).
- Koszt ok. 0,09 USD/M tokenów na H100 + vLLM przy analogicznym obciążeniu.
- 2,8-krotny wzrost przepustowości w ciągu trzech miesięcy dzięki aktualizacjom TRT-LLM (2026).
- 11-15x większa przepustowość LLM na procesor graficzny Blackwell w porównaniu z Hopperem.
- Dominacja architektury Blackwell we wszystkich zadaniach w testach MLPerf Inference v6.0 (kwiecień 2026 r.).

### Ile faktycznie kosztuje FP4 pod względem jakości

NVFP4 to format bardzo agresywny. W zadaniach wymagających zaawansowanego wnioskowania (łańcuch myśli, matematyka, generowanie kodu o długim kontekście) stosowanie wag FP4 prowadzi do zauważalnego spadku jakości odpowiedzi. Kalibracja poszczególnych bloków zmniejsza ten problem, ale go nie eliminuje. Zespoły wdrażające modele wnioskujące często wybierają kompromis w postaci wag FP8 + aktywacji FP4 lub decydują się na pozostanie przy architekturze H200 i pełnym FP8.

Zasada: Przed wdrożeniem wag NVFP4 na produkcji zawsze sprawdź jakość działania modelu na reprezentatywnym zbiorze testowym.

### Dlaczego jest to decyzja wiążąca (vendor lock-in) z firmą NVIDIA

TRT-LLM opiera się na zamkniętym kodzie źródłowym napisanym w C++ i CUDA. Modele muszą być kompilowane pod konkretną wersję (SKU) procesora graficznego. Brak tu obsługi układów AMD, Intel czy ARM. Jeśli Twoja strategia infrastrukturalna zakłada współpracę z wieloma dostawcami sprzętu, TRT-LLM nie sprawdzi się jako jednolita warstwa serwująca – w takim scenariuszu lepszym wyborem na mieszanym sprzęcie pozostaje vLLM. Jeśli jednak opierasz się wyłącznie na technologii NVIDIA, 7-krotna redukcja kosztów w pełni uzasadnia to uzależnienie technologiczne.

### Praktyczny przepis na rok 2026

Przy rocznych kosztach wnioskowania przekraczających 100 milionów dolarów, pozostanie przy architekturze Hopper + vLLM oznacza stratę rzędu 7-10x. Należy przenieść najbardziej kosztowne zadania na Blackwell + TRT-LLM + Dynamo. Środowiska eksperymentalne warto utrzymać na H100 + vLLM w celu zachowania szybkiego tempa iteracji modeli. Przed wdrożeniem produkcyjnym należy każdorazowo zweryfikować jakość modelu po konwersji do formatu NVFP4.

### Dodatkowe korzyści ze zdezagregowanego wnioskowania

Zdezagregowane wnioskowanie w TRT-LLM (rozdzielenie pul prefill i decode) zostało szczegółowo opisane w Fazie 17 · 20. Na architekturze Blackwell poszczególne zyski wydajnościowe nakładają się na siebie: wagi FP4 × przyspieszenie MTP × zdezagregowane wdrożenie × routing uwzględniający lokalność cache. Prezentowany 7-krotny zysk zakłada wykorzystanie pełnego stosu tych technologii.

## Użycie

Skrypt `code/main.py` oblicza zapotrzebowanie na pamięć HBM, przepustowość generowania tokenów w fazie dekodowania (scenariusz ograniczony przepustowością pamięci) oraz koszt $/M tokenów dla modelu na trzech stosach: H100 + BF16 + vLLM, H100 + FP8 + vLLM oraz B200 + NVFP4/FP8 + TRT-LLM. Uruchom go, aby zaobserwować skumulowany efekt tych technologii i wkład poszczególnych czynników w ogólną redukcję kosztów.

## Efekt końcowy

W ramach tej lekcji powstaje dokument `outputs/skill-trtllm-blackwell-advisor.md`. Na podstawie profilu obciążenia, rozmiaru modelu i rocznego wolumenu tokenów ocenia on, czy wdrożenie stosu Blackwell + TRT-LLM jest warte wejścia w zamknięty ekosystem NVIDIA.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Dla modelu MoE 120B z 30% aktywnych parametrów oblicz przepustowość dekodowania (ograniczoną przepustowością pamięci) na konfiguracjach H100 BF16, H100 FP8 oraz B200 NVFP4/FP8. Z którego przejścia wynika największy wzrost wydajności?
2. Klient wydaje rocznie 2 miliony dolarów na utrzymanie infrastruktury H100 + vLLM. Ile procesorów graficznych Blackwell musi zakupić, aby koszt migracji na TRT-LLM zamortyzował się w ciągu 12 miesięcy, biorąc pod uwagę 7-krotną różnicę w kosztach eksploatacji?
3. Po konwersji wag do formatu NVFP4 dokładność modelu w teście benchmarkowym MATH spada o 3 punkty procentowe. Wskaż dwie ścieżki zaradcze: jedną skupiającą się na zachowaniu jakości (pozostawienie wag w formacie FP8), drugą zorientowaną na optymalizację kosztów (kalibracja z użyciem danych z domeny docelowej).
4. Zapoznaj się z wynikami testów MLPerf Inference v6.0. W którym zadaniu różnica wydajnościowa między architekturami Blackwell i Hopper jest najmniejsza i z czego to wynika?
5. Oblicz zapotrzebowanie na pamięć HBM dla modelu 405B przy wagach w formacie NVFP4 oraz pamięci podręcznej KV w formacie FP8 dla kontekstu o długości 128k. Czy taki model zmieści się w pamięci pojedynczego węzła GB200 NVL72?

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| FP8 | „ośmiobitowy float” | 8-bitowy format zmiennoprzecinkowy; stosowany dla pamięci podręcznej KV oraz mechanizmu uwagi ze względu na odpowiedni zakres dynamiczny |
| NVFP4 | „czterobitowy micro” | 4-bitowy format zmiennoprzecinkowy z mikroskalowaniem od NVIDIA; stosowany do zapisu wag i aktywacji na architekturze Blackwell |
| MXFP8 | „MX osiem” | Odmiana formatu FP8 z mikroskalowaniem; sprzętowo przyspieszana w rdzeniach Tensor architektury Blackwell |
| Day 0 FP4 | „wagi fabryczne FP4” | Udostępnianie wag modelu przez twórców bezpośrednio w formacie FP4; pozwala uniknąć etapu konwersji post-trainingowej |
| MTP | „przewidywanie wielu tokenów” | Zintegrowany w TRT-LLM mechanizm dekodowania spekulatywnego (Faza 17 · 05) |
| Zdezagregowane wnioskowanie | „podział prefill/decode” | Wykonywanie faz prefill i decode na osobnych pulach GPU; dane KV są przesyłane przez NVLink/IB |
| All-to-all | „komunikacja MoE” | Wzorzec komunikacji kierujący tokeny do wyspecjalizowanych procesorów graficznych (ekspertów); NVLink 5 skraca ten czas 3-krotnie |
| InferenceX | „benchmark SemiAnalysis” | Przyjęty w branży standard porównywania rzeczywistych kosztów generowania tokenów na rok 2026 |

## Dalsze czytanie

- [NVIDIA — Blackwell Ultra MLPerf Inference v6.0](https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut/) — Wyniki MLPerf z kwietnia 2026 r.
- [NVIDIA — Wnioskowanie MoE na Blackwell](https://developer.nvidia.com/blog/delivering-massive-performance-leaps-for-mixture-of-experts-inference-on-nvidia-blackwell/) — Szczegóły dotyczące NVLink 5 all-to-all oraz kerneli MoE.
- [Dokumentacja TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/overview.html) — Oficjalny przewodnik po silniku wnioskowania.
- [NVIDIA — Przedstawiamy Dynamo](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/) — Orkiestracja zdezagregowana działająca ponad TRT-LLM.
- [MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) — Oficjalny zestaw testów porównawczych, w którym publikowane są wyniki dla architektury Blackwell.
