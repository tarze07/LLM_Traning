# Wnioskowanie na brzegu sieci — Apple Neural Engine, Qualcomm Hexagon, WebGPU/WebLLM, Jetson

> Podstawowym ograniczeniem przy wnioskowaniu na brzegu sieci (edge inference) jest przepustowość pamięci, a nie moc obliczeniowa procesora. Mobilna pamięć DRAM oferuje przepustowość na poziomie 50–90 GB/s, podczas gdy pamięć HBM3 w centrach danych zapewnia 2–3 TB/s. Oznacza to 30–50-krotną różnicę. Faza dekodowania (decoding) jest ograniczona przepustowością pamięci (memory-bound), dlatego ta różnica ma kluczowe znaczenie. W 2026 roku rynek rozwiązań brzegowych dzieli się na cztery główne obszary. Apple Neural Engine (ANE) w układach M4/A18 osiąga wydajność do 38 TOPS przy wykorzystaniu pamięci zunifikowanej (co eliminuje narzut na kopiowanie danych między CPU a NPU). NPU Qualcomm Hexagon w układach Snapdragon X Elite / 8 Gen 4 osiąga wydajność do 45 TOPS. Technologia WebGPU + WebLLM pozwala na uruchomienie modelu Llama-3.1-8B (w wersji Q4) z prędkością ok. 41 tokenów/s na procesorze M3 Max (osiągając ok. 70-80% wydajności aplikacji natywnej). Projekt ten ma 17,6 tys. gwiazdek na GitHubie, oferuje API zgodne z OpenAI i obejmuje zasięgiem ok. 70-75% urządzeń mobilnych. Z kolei NVIDIA Jetson Orin Nano Super (8 GB) sprawdza się przy obsłudze modeli Llama-3.2-3B lub Phi-3; wersja AGX Orin uruchamia model gpt-oss-20b za pośrednictwem vLLM z prędkością ok. 40 tokenów/s; model Jetson T4000 (działający pod kontrolą JetPack 7.1) oferuje dwukrotność wydajności AGX Orin. Ponadto platforma TensorRT Edge-LLM obsługuje dekodowanie spekulatywne EAGLE-3, format NVFP4 oraz mechanizm chunked prefill – rozwiązania zaprezentowane na targach CES 2026 przez firmy Bosch, ThunderSoft i MediaTek.

**Typ:** Ucz się
**Języki:** Python (stdlib, uproszczona symulacja dekodowania ograniczona przepustowością pamięci)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy vLLM), Faza 17 · 09 (Kwantyzacja produkcyjna)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego wnioskowanie z użyciem modeli LLM na urządzeniach mobilnych jest ograniczone przepustowością pamięci, a moc obliczeniowa procesora ma znaczenie drugorzędne.
- Charakteryzuj cztery docelowe platformy brzegowe (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) i przypisz każdą z nich do optymalnego scenariusza wdrożenia.
- Zidentyfikuj ograniczenia w zasięgu technologii WebGPU w 2026 r. (brak pełnego wsparcia w wersji Firefox na Androida, stabilna obsługa w Safari na iOS 26).
- Dobierz odpowiedni format kwantyzacji dla każdej z platform docelowych (Core ML INT4 + FP16 dla Apple ANE, QNN INT8/INT4 dla Qualcomm Hexagon, MLC Q4 dla rozwiązań przeglądarkowych, NVFP4 dla platformy Jetson Thor).

## Problem

Klient oczekuje wdrożenia chatbota działającego lokalnie na urządzeniu końcowym – z interfejsem głosowym, pełną prywatnością i możliwością pracy w trybie offline. Na laptopie MacBook Pro z procesorem M3 Max model Llama-3.1-8B w wersji Q4 generuje ok. 55 tokenów/s, co stanowi zadowalający wynik. Jednak na smartfonie iPhone 16 Pro ten sam model osiąga zaledwie 3 tokeny/s. Na średniej klasy telefonie z systemem Android i układem Snapdragon 8 Gen 3 wydajność wynosi 7 tokenów/s. W środowisku przeglądarkowym (poprzez WebGPU w Chrome na Androidzie v121+) szybkość waha się w przedziale 4-8 tokenów/s w zależności od urządzenia.

Te rozbieżności w wydajności nie wynikają ze złego przeniesienia kodu. Są one bezpośrednią konsekwencją różnic w przepustowości magistrali pamięci, zastosowanego formatu kwantyzacji oraz tego, czy system operacyjny pozwala aplikacji na bezpośredni dostęp do procesora NPU. Wnioskowanie na urządzeniach brzegowych w 2026 r. to w rzeczywistości cztery odrębne wyzwania technologiczne wymagające dedykowanych rozwiązań.

## Koncepcja

### Przepustowość pamięci jako rzeczywiste wąskie gardło

Podczas dekodowania procesor musi odczytać komplet wag modelu dla każdego generowanego tokena. Model klasy 7B skwantowany do formatu 4-bitowego zajmuje ok. 3,5 GB pamięci. Przy przepustowości pamięci na poziomie 50 GB/s, sam odczyt wag z RAM zajmuje 70 ms – co nakłada fizyczny limit generowania na poziomie ok. 14 tokenów/s. Zwiększenie przepustowości do 90 GB/s (wysokiej klasy pamięci DRAM w smartfonach) przesuwa tę granicę do ok. 25 tokenów/s. Żadne zwiększanie mocy obliczeniowej nie pozwoli na przekroczenie tych wartości.

Dla porównania, pamięć HBM3 w centrach danych o przepustowości 3 TB/s pozwala na odczyt tych samych 3,5 GB danych w zaledwie 1,2 ms – co umożliwia generowanie z prędkością teoretyczną do 830 tokenów/s. Dokładnie ten sam model, te same wagi – jedyną różnicą jest architektura podsystemu pamięci.

### Apple Neural Engine (ANE w układach M4 / A18)

- Wydajność do 38 TOPS. Architektura pamięci zunifikowanej (Unified Memory) oznacza, że CPU i NPU współdzielą tę samą fizyczną pamięć RAM, co eliminuje konieczność kopiowania danych.
- Dostęp realizowany jest poprzez framework Core ML (modele skompilowane do formatu `.mlmodel`) lub Metal Performance Shaders (MPS) pod kontrolą PyTorch.
- Backend Metal w bibliotece Llama.cpp wykorzystuje interfejs MPS, nie odwołując się bezpośrednio do ANE. Wykorzystanie pełnego potencjału ANE wymaga konwersji modelu do formatu Core ML.
- Rekomendowane podejście dla aplikacji iOS w 2026 r.: konwersja Core ML z wagami w formacie INT4 oraz aktywacjami w FP16.

### Qualcomm Hexagon (Snapdragon X Elite / 8 Gen 4)

- Wydajność do 45 TOPS. Układ NPU jest zintegrowany w strukturze SoC (wraz z CPU i GPU), lecz posiada wydzieloną domenę pamięci.
- Narzędzia QNN (Qualcomm Neural Network) SDK oraz platforma AI Hub zapewniają mechanizmy konwersji z formatów PyTorch/ONNX.
- Gotowe szablony konwersji dla modeli Llama 3.2 oraz Phi-3 są udostępniane jako oficjalne pakiety w AI Hub.

### Procesory NPU Intel/AMD (Lunar Lake, Ryzen AI 300)

- Wydajność na poziomie 40-50 TOPS. Wsparcie programistyczne ustępuje rozwiązaniom firm Apple i Qualcomm. Narzędzie OpenVINO jest stale rozwijane, ale pozostaje technologią niszową.
- Rozwiązanie optymalne dla aplikacji integrujących się z systemem Windows na architekturze ARM lub lokalnych wdrożeń na komputerach stacjonarnych z układami AMD/Intel.

### WebGPU + WebLLM

- Uruchamianie modeli bezpośrednio w oknie przeglądarki z użyciem shaderów obliczeniowych WebGPU – niewymagające instalacji dodatkowego oprogramowania.
- Wydajność na poziomie ok. 41 tokenów/s dla modelu Llama-3.1-8B Q4 na procesorze M3 Max – co stanowi ok. 70-80% szybkości aplikacji natywnej korzystającej z tego samego backendu.
- Ponad 17,6 tys. gwiazdek na GitHubie dla projektu WebLLM; udostępnia on API kompatybilne ze standardem OpenAI w języku JavaScript na licencji Apache 2.0.
- Stan wsparcia w 2026 r.: Chrome na Androidzie v121+, Safari na iOS 26 GA; trwają prace nad wdrożeniem w przeglądarce Firefox na systemie Android. Łączny zasięg na rynku urządzeń mobilnych wynosi ok. 70-75%.

### Rodzina NVIDIA Jetson

- Orin Nano Super (8 GB): Doskonale radzi sobie z obsługą modeli Llama-3.2-3B oraz Phi-3, oferując satysfakcjonującą przepustowość.
- AGX Orin: Pozwala na uruchomienie modelu gpt-oss-20b za pomocą vLLM z wydajnością ok. 40 tokenów/s.
- Thor / T4000 (działające z JetPack 7.1): Oferują 2-krotny wzrost wydajności w porównaniu z AGX Orin oraz pełne wsparcie dla dekodowania spekulatywnego EAGLE-3 i formatu NVFP4.
- Zastosowanie TensorRT Edge-LLM (2026 r.) przenosi zaawansowane optymalizacje znane z centrów danych (np. speculatywne generowanie EAGLE-3, wagi NVFP4, chunked prefill) na urządzenia brzegowe.

### Rekomendowane formaty kwantyzacji dla poszczególnych platform

| Platforma | Format | Uwagi |
|--------|--------|-------|
| Apple ANE | Wagi INT4 + aktywacje FP16 | Rekomendowana ścieżka konwersji Core ML |
| Qualcomm Hexagon | QNN INT8 / INT4 | Konwersja za pomocą narzędzi z AI Hub |
| WebGPU / WebLLM | Q4 MLC (q4f16_1) | Wymaga użycia polecenia `mlc_llm convert_weight` oraz kompilacji do `.wasm` (format GGUF nie jest wspierany) |
| Jetson Orin Nano | Q4 GGUF lub TRT-LLM INT4 | Scenariusz ściśle ograniczony przepustowością pamięci |
| Jetson AGX / Thor | NVFP4 + FP8 KV | Dedykowana ścieżka Edge-LLM |

### Wyzwanie długiego kontekstu na urządzeniach brzegowych

Kontekst o długości 128k tokenów w modelach Llama 3.1 to rozwiązanie projektowane z myślą o centrach danych. Na urządzeniu mobilnym wyposażonym w 8 GB pamięci RAM, uruchomienie skwantowanego modelu (ok. 4 GB) przy kontekście 32k tokenów wymaga zaalokowania dodatkowych 2 GB na pamięć podręczną KV, co w połączeniu z narzutem systemu operacyjnego prowadzi do natychmiastowego błędu braku pamięci (OOM). Wdrożenia brzegowe zazwyczaj ograniczają długość kontekstu do przedziału 4k–8k tokenów, chyba że zastosowana zostanie agresywna kwantyzacja pamięci podręcznej (np. Q4 KV).

### Zastosowania głosowe jako główny motor wdrożeń brzegowych

Interfejsy głosowe są niezwykle wrażliwe na opóźnienia – czas do wygenerowania pierwszego dźwięku powinien wynosić < 500 ms. Lokalne uruchomienie modelu eliminuje opóźnienia transmisji sieciowej. W połączeniu ze zoptymalizowanymi modelami rozpoznawania mowy (np. warianty Whisper Turbo działające lokalnie), wnioskowanie na brzegu sieci umożliwia budowę responsywnych asystentów głosowych o jakości produkcyjnej.

### Liczby, które powinieneś zapamiętać

- Wydajność Apple M4 / A18 ANE: 38 TOPS.
- Wydajność Qualcomm Hexagon w Snapdragon X Elite: 45 TOPS.
- Przepustowość WebLLM na M3 Max: ok. 41 tokenów/s dla Llama-3.1-8B Q4.
- Wydajność AGX Orin: ok. 40 tokenów/s dla modelu gpt-oss-20b pod kontrolą vLLM.
- Różnica w przepustowości pamięci (urządzenie brzegowe vs centrum danych): 30-50x.
- Zasięg WebGPU na rynku mobilnym: ok. 70-75% (głównym ograniczeniem jest brak pełnego wsparcia w mobilnej przeglądarce Firefox).

## Użycie

Skrypt `code/main.py` wylicza teoretyczne limity przepustowości dekodowania na podstawie parametrów sprzętowych magistrali pamięci dla poszczególnych platform brzegowych. Porównuje uzyskane wyniki z rzeczywistymi testami wydajnościowymi i wskazuje, w których miejscach to przepustowość pamięci, a nie moc obliczeniowa, stanowi wąskie gardło systemu.

## Efekt końcowy

W ramach tej lekcji tworzony jest dokument `outputs/skill-edge-target-picker.md`. Na podstawie wybranej platformy docelowej (iOS, Android, przeglądarka, Jetson), modelu oraz założeń budżetowych i wymagań dotyczących opóźnień, dokonuje on wyboru formatu kwantyzacji i generuje instrukcje dla potoku konwersji modelu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Dla modelu klasy 7B w formacie Q4 uruchomionego na układzie Snapdragon 8 Gen 3 (przepustowość pamięci ok. 77 GB/s) oblicz teoretyczny limit wydajności fazy dekodowania. Porównaj wynik z obserwowanymi w rzeczywistości 6-8 tokenami/s – czy silnik wnioskowania jest optymalnie wykorzystywany?
2. Technologia WebGPU na systemie Android wymaga przeglądarki Chrome w wersji v121+. Zaprojektuj mechanizm automatycznego przełączania (fallback) na wnioskowanie po stronie serwera z zachowaniem tego samego interfejsu API zgodnego ze standardem OpenAI dla starszych wersji przeglądarek.
3. Twoja aplikacja na iOS wymaga obsługi przesyłania strumieniowego kontekstu o długości 4k tokenów. Która kombinacja modelu i formatu kwantyzacji pozwoli na utrzymanie zużycia pamięci poniżej limitu 4 GB na smartfonie iPhone 16?
4. Platforma Jetson AGX Orin pozwala na uruchomienie modelu gpt-oss-20b z prędkością 40 tokenów/s, podczas gdy mniejsza wersja Jetson Nano mieści jedynie modele klasy 3B. Jeśli Twój produkt ma wspierać obie te platformy sprzętowe, jak ujednolicić stos technologiczny wnioskowania?
5. Przeanalizuj stwierdzenie: „Projekt WebLLM jest gotowy do wdrożenia produkcyjnego w 2026 roku”. Oceń stopień pokrycia rynku, wydajność oraz wpływ braku pełnego wsparcia w przeglądarce Firefox na systemie Android.

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| ANE | „Apple Neural Engine” | Koprocesor NPU wbudowany w układy Apple z serii M oraz A; wykorzystuje architekturę pamięci zunifikowanej |
| Hexagon | „NPU od Qualcomm” | Procesor NPU zintegrowany w układach Snapdragon; dostęp programistyczny realizowany jest za pomocą QNN SDK |
| WebGPU | „GPU w przeglądarce” | Standard API dla przeglądarek umożliwiający wykonywanie obliczeń na GPU; wspierany przez Chrome i Safari w 2026 r. |
| WebLLM | „silnik LLM w przeglądarce” | Projekt rozwijany w ramach MLC-LLM na licencji Apache 2.0; udostępnia API w JS zgodne z OpenAI |
| Jetson | „platforma brzegowa NVIDIA” | Rodzina komputerów jednopłytkowych do zadań AI (np. Orin Nano, AGX, Thor, T4000) |
| TRT Edge-LLM | „TensorRT dla brzegu” | Wersja silnika TensorRT-LLM zoptymalizowana dla urządzeń brzegowych, wspierająca m.in. EAGLE-3 i format NVFP4 |
| Pamięć zunifikowana | „unified memory” | Współdzielenie tej samej fizycznej pamięci RAM przez procesory CPU, GPU i NPU, co eliminuje opóźnienia przesyłu danych |
| Ograniczenie przepustowością | „memory-bound” | Stan, w którym prędkość działania algorytmu dekodowania jest ograniczona czasem odczytu wag modelu z pamięci RAM |
| Core ML | „framework Apple” | Natywna biblioteka i format modeli Apple, zoptymalizowana pod kątem uruchamiania na Apple Neural Engine |
| QNN | „Qualcomm Neural Network” | Zestaw narzędzi programistycznych (SDK) od firmy Qualcomm do optymalizacji i uruchamiania modeli na procesorach Hexagon NPU |

## Dalsze czytanie

- [Status Unii On-Device LLMs 2026](https://v-chandra.github.io/on-device-llms/) — Analiza rynku i wyniki testów porównawczych dla modeli lokalnych.
- [NVIDIA Jetson Edge AI](https://developer.nvidia.com/blog/getting-started-with-edge-ai-on-nvidia-jetson-llms-vlms-and-foundation-models-for-robotics/) — Wdrażanie modeli językowych i wizyjnych na platformie Jetson.
- [NVIDIA TensorRT Edge-LLM](https://developer.nvidia.com/blog/accelerating-llm-and-vlm-inference-for-automotive-and-robotics-with-nvidia-tensorrt-edge-llm/) — Zapowiedź nowej wersji silnika dla branży motoryzacyjnej i robotyki.
- [WebLLM (arXiv:2412.15803)](https://arxiv.org/html/2412.15803v2) — Praca naukowa opisująca architekturę i wydajność silnika WebLLM.
- [Apple Core ML Documentation](https://developer.apple.com/documentation/coreml) — Oficjalne materiały dotyczące integracji modeli w ekosystemie Apple.
- [Qualcomm AI Hub](https://aihub.qualcomm.com/) — Portal z gotowymi modelami zoptymalizowanymi pod kątem układów Snapdragon.
