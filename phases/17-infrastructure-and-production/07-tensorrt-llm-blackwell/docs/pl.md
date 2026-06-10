# TensorRT-LLM na Blackwell z FP8 i NVFP4

> TensorRT-LLM jest przeznaczony tylko dla NVIDIA, ale wygrywa na Blackwell. Na GB200 NVL72 z orkiestracją Dynamo, narzędzie SemiAnalytic InferenceX zmierzyło $0.012 per million tokens on a 120B model in Q1-Q2 2026, against $0,09/M na H100 + vLLM — 7-krotność luki ekonomicznej. Stos składa się z trzech reżimów zmiennoprzecinkowych: 8PR pozostaje krytyczny dla jąder pamięci podręcznej KV i uwagi, ponieważ ma potrzebny zakres dynamiki; NVFP4 (4-bitowe mikroskalowanie) obsługuje wagi i aktywacje; przewidywanie wielu tokenów (MTP) i zdezagregowane wstępne wypełnianie/dekodowanie dodają kolejne 2-3x na górze. Obsługa modelu dnia 0 ładuje ciężary FP4 bezpośrednio, bez konwersji po treningu. Haczyk dla zespołów inżynieryjnych na rok 2026: TRT-LLM to zamknięty stos NVIDIA, więc jego przyjęcie wymaga kompromisu w zakresie przenośności na rzecz przepustowości. Przed zatwierdzeniem wykonaj obliczenia na zestawie modeli i sprzętu.

**Typ:** Ucz się
**Języki:** Python (stdlib, pamięć dla zabawek FP8/NVFP4 i kalkulator kosztów)
**Wymagania wstępne:** Faza 17 · 04 (wewnętrzne urządzenia obsługujące vLLM), Faza 10 · 13 (kwantyzacja)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego FP8 pozostaje krytyczny dla pamięci podręcznej KV i uwagi, nawet gdy wagi są w NVFP4.
- Oblicz ślad HBM dla modelu granicznego w ramach BF16, FP8 i NVFP4 i uzasadnij, skąd pochodzą oszczędności.
- Wymień funkcje specyficzne dla Blackwell, które wykorzystuje TRT-LLM (dzień 0, FP4, MTP, udostępnianie zdezagregowane, operacje podstawowe typu „wszystko do wszystkich”).
- Zdecyduj, kiedy blokada NVIDIA TRT-LLM jest warta 7-krotnej luki w kosztach w porównaniu z vLLM na Hopperze.

## Problem

Granica ekonomii wnioskowania w 2026 r. to „ile tokenów na dolara”. Odpowiedź zależy od czterech połączonych opcji: generacji sprzętu (Hopper H100/H200 vs Blackwell B200/GB200), precyzji (BF16 → FP8 → NVFP4), silnika obsługującego (vLLM vs SGLang vs TRT-LLM) i orkiestracji (zwykły vs zdezagregowany vs Dynamo).

Na Hopperze z vLLM MoE 120B działa przy ~$0.09 per million tokens. On Blackwell with TRT-LLM + Dynamo, the same model runs at ~$0,012 — 7 razy taniej. Część tej luki dotyczy sprzętu (przepustowość Blackwell na GPU LLM jest 11–15 razy większa w porównaniu z Hopperem). Niektóre z nich to stos: wagi 4PR, wersja robocza MTP, zdezagregowane wstępne wypełnianie/dekodowanie i NVLink 5 typu „wszystko do wszystkich” do komunikacji ekspertów MoE.

Nie można tego odtworzyć poza stosem NVIDIA. Na tym polega kompromis — przenośność w imię ekonomii. Celem tej lekcji jest zrozumienie, które wybory stosów dają jaką część luki.

## Koncepcja

### Dlaczego 8PR to nadal podstawa dla pamięci podręcznej KV

Częsty błąd w 2026 r.: założenie, że NVFP4 ma zastosowanie wszędzie. Tak nie jest. Pamięć podręczna KV wymaga FP8 (8-bitowego zmiennoprzecinkowego), ponieważ przechowuje klucze uwagi i wartości obejmujące szeroki zakres dynamiki. Kwantyzacja KV do FP4 powoduje katastrofalną utratę dokładności — ogon rozkładu spada, a wyniki uwagi załamują się. Bity wykładnicze FP8 zapewniają buforowi KV wymagany zakres.

NVFP4 (2025-2026) dotyczy ciężarów i aktywacji. Mikroskalowanie: każdy blok wag ma swój własny współczynnik skali, więc małe bloki mogą obejmować różne zakresy dynamiczne bez utraty skali na tensor. W przypadku aktywacji FP4 wytrzymuje, ponieważ aktywacje mają niewielki zasięg w obrębie warstwy.

Typowa konfiguracja Blackwell:

- Wagi: NVFP4 (mikroskalowanie 4-bitowe).
- Aktywacje: NVFP4.
- Pamięć podręczna KV: FP8.
- Uwaga akumulator: FP32 (stabilność softmax).

### Prymitywy specyficzne dla Blackwell, których używa TRT-LLM

- **Wagi 4PR z dnia 0**: dostawcy modeli bezpośrednio wysyłają wagi 4PR; Obciążenia TRT-LLM bez konwersji potreningowej. Brak kroku AWQ/GPTQ dla FP4.
- **Przewidywanie wielu tokenów (MTP)**: ten sam pomysł co EAGLE (faza 17 · 05), ale zintegrowany z kompilacją TRT-LLM.
- **Udostępnianie zdezagregowane**: wstępne wypełnianie i dekodowanie w oddzielnych pulach GPU, pamięć podręczna KV przesyłana przez NVLink lub InfiniBand. Ten sam pomysł co Dynamo (faza 17 · 20).
- **Prymitywy komunikacji typu „wszystko do wszystkich”**: NVLink 5 zmniejsza opóźnienie komunikacji ekspertów MoE 3 razy w porównaniu z Hopperem. Jądra MoE TRT-LLM są do tego dostrojone.
- **Mikroskalowanie NVFP4 + MXFP8**: przyspieszana sprzętowo obsługa współczynnika skalowania w rdzeniach Blackwell Tensor.

### Liczby, które powinieneś zapamiętać

- HGX B200 z tokenami 0,02 USD/M na GPT-OSS-120B przez TRT-LLM.
- GB200 NVL72 po 0,012 USD/M tokenów za pośrednictwem Dynamo (organizacja TRT-LLM).
- Tokeny H100 + vLLM ≈ 0,09 USD/M przy porównywalnym obciążeniu pracą.
- 2,8-krotny wzrost przepustowości w ciągu trzech miesięcy aktualizacji TRT-LLM (2026).
- 11-15x przepustowość LLM na GPU, Blackwell vs Hopper.
- MLPerf Inference v6.0 (kwiecień 2026 r.): Firma Blackwell dominuje w każdym przesłanym zadaniu.

### Ile faktycznie kosztuje 4. PR pod względem jakości

NVFP4 jest agresywny. W przypadku obciążeń wymagających dużego rozumowania (łańcuch myślenia, matematyka, generowanie kodu w długim kontekście) wagi 4PR wyraźnie spadają. Kalibracja poszczególnych bloków łagodzi, ale nie eliminuje. Zespoły dostarczające modele rozumowania często wykorzystują wagi 8PR + aktywacje 4PR jako kompromis lub trzymają się H200 z 8PR przez cały czas.

Zasada: zawsze sprawdzaj jakość zadania w zestawie ewaluacyjnym przed zatwierdzeniem wag NVFP4.

### Dlaczego jest to decyzja blokująca firmę NVIDIA

TRT-LLM to jądra C++ + CUDA + o zamkniętym kodzie źródłowym. Modele należy skompilować dla określonej jednostki SKU procesora GPU. Żadnego AMD, żadnego Intela, żadnego ARM. Jeśli Twoja strategia infrastruktury obejmuje wielu dostawców, TRT-LLM nie jest rozwiązaniem dla warstwy obsługiwanej przez TRT-LLM — nadal możesz obsługiwać z vLLM na mieszanym sprzęcie. Jeśli korzystasz tylko z NVIDIA, 7-krotna luka opłaca blokadę.

### Praktyczny przepis 2026

W przypadku rocznego rachunku wnioskowanego o wartości ponad 100 milionów dolarów, uruchomienie na Hopperze + vLLM pozostawia 7-10x na stole. Przeprowadź migrację zadań, w których dominują koszty, do Blackwell + TRT-LLM + Dynamo. Zachowaj poziom eksperymentów na H100 + vLLM, aby uzyskać szybkość iteracji modelu. Przed rozpoczęciem produkcji sprawdzaj jakość każdego modelu po konwersji w formacie NVFP4.

### Premia za dezagregację

Zdezagregowane udostępnianie TRT-LLM (oddzielne pule wstępnego wypełniania i dekodowania) zostało szczegółowo omówione w fazie 17 · 20. W przypadku Blackwell mnożniki stosują się: wagi FP4 × przyspieszenie MTP × zdezagregowane rozmieszczenie × routing uwzględniający pamięć podręczną. Liczba 7x zakłada pełny stos.

## Użyj tego

`code/main.py` oblicza ślad HBM, przepustowość dekodowania (reżim związany z pamięcią) i tokeny $/M dla modelu na trzech stosach: H100 + BF16 + vLLM, H100 + FP8 + vLLM, B200 + NVFP4/FP8 + TRT-LLM. Uruchom go, aby zobaczyć efekt łączenia i udział luki wnoszonej przez każdą zmianę.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-trtllm-blackwell-advisor.md`. Biorąc pod uwagę obciążenie pracą, rozmiar modelu i roczny wolumen tokenów, decyduje, czy stos Blackwell + TRT-LLM jest wart blokady NVIDIA.

## Ćwiczenia

1. Uruchom `code/main.py`. W przypadku 120B MoE z 30% aktywnych parametrów oblicz przepustowość dekodowania ograniczoną przepustowością pamięci na H100 BF16, H100 FP8 i B200 NVFP4/FP8. Skąd bierze się największy skok?
2. Klient wydaje 2 miliony dolarów rocznie na H100 + vLLM. Jaki jest próg rentowności procesorów graficznych Blackwell, które muszą kupić, aby zamortyzować migrację do TRT-LLM w ciągu 12 miesięcy, biorąc pod uwagę 7-krotną lukę ekonomiczną?
3. Po konwersji masy NVFP4 dokładność spada o 3 punkty w MATH. Wymień dwie ścieżki odzyskiwania: jedna skupiająca się na jakości (zachowaj wagi z 8PR), druga skupiająca się na kosztach (kalibracja przy użyciu danych w domenie).
4. Przeczytaj wyniki wnioskowania MLPerf v6.0. Które zadanie ma najmniejszą różnicę między Blackwellem a Hopperem i dlaczego?
5. Oblicz HBM potrzebny dla modelu 405B przy wagach NVFP4 + pamięci podręcznej KV FP8 w kontekście 128k. Czy pasuje do pojedynczego węzła GB200 NVL72?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| 8PR | „ośmibitowy float” | 8-bitowy zmiennoprzecinkowy; używany do pamięci podręcznej KV i uwagi ze względu na zakres dynamiczny |
| NVFP4 | „czterobitowy mikro” | 4-bitowy format FP z mikroskalowaniem firmy NVIDIA; wagi i aktywacje na Blackwell |
| MXFP8 | „MX osiem” | Wariant FP8 z mikroskalowaniem; przyspieszany sprzętowo na rdzeniach Blackwell Tensor |
| Dzień 0 FP4 | „wagi statku 4PR” | Dostawcy modeli udostępniają wagi już w 4PR; brak etapu konwersji po pociągu |
| MTP | „przewidywanie wielu tokenów” | Zintegrowany projekt dekodowania spekulatywnego TRT-LLM (faza 17 · 05) |
| Zdezagregowana porcja | „podzielone wstępne wypełnianie/dekodowanie” | Wstępnie wypełniaj i dekoduj w oddzielnych pulach GPU; KV przesłane przez NVLink/IB |
| Wszystko dla wszystkich | „Komunikacja eksperta Ministerstwa Środowiska” | Tokeny routingu wzorców komunikacji do specjalistycznych procesorów graficznych; NVLink 5 cięć 3x |
| WnioskowanieX | „Ławka wnioskowania półanalizy” | Zaakceptowany w branży benchmark kosztu tokena na rok 2026 |

## Dalsze czytanie

— [NVIDIA — Blackwell Ultra MLPerf Inference v6.0](https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut/) — wyniki MLPerf z kwietnia 2026 r.
- [NVIDIA — Wnioskowanie MoE na Blackwell](https://developer.nvidia.com/blog/delivering-massive- Performance-leaps-for-mixture-of-experts-inference-on-nvidia-blackwell/) — Jądra NVLink 5 all-to-all i MoE.
- [Omówienie TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/overview.html) — oficjalna dokumentacja silnika.
— [NVIDIA — Przedstawiamy Dynamo](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/) — zdezagregowana orkiestracja powyżej TRT-LLM.
- [MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) — zestaw testów porównawczych, który publikuje liczby Blackwella.