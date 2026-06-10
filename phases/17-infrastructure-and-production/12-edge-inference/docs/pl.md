# Wnioskowanie o krawędzi — Apple Neural Engine, Qualcomm Hexagon, WebGPU/WebLLM, Jetson

> Podstawowym ograniczeniem krawędziowym jest przepustowość pamięci, a nie moc obliczeniowa. Mobilna pamięć DRAM ma prędkość 50–90 GB/s; centrum danych HBM3 zapewnia przepustowość 2–3 TB/s — luka 30–50-krotna. Dekodowanie jest związane z pamięcią, więc różnica jest decydująca. W 2026 roku krajobraz rozdziela się na cztery strony. Silnik neuronowy Apple M4/A18 osiąga szczytową prędkość 38 TOPS przy zunifikowanej pamięci (bez kopii CPU↔NPU). Qualcomm Snapdragon X Elite / 8 Gen 4 Hexagon osiąga 45 TOPÓW. WebGPU + WebLLM obsługuje Llamę 3.1 8B (Q4) przy ~41 tok/s na M3 Max (około 70-80% wersji natywnej); 17,6 tys. gwiazdek na GitHubie, API zgodne z OpenAI, zasięg urządzeń mobilnych ~70-75%. NVIDIA Jetson Orin Nano Super (8 GB) pasuje do Lamy 3.2 3B / Phi-3; AGX Orin uruchamia gpt-oss-20b przez vLLM z szybkością ~40 tok/s; Jetson T4000 (JetPack 7.1) to 2x AGX Orin. TensorRT Edge-LLM obsługuje EAGLE-3, NVFP4, wstępne wypełnianie fragmentami — pokazane na targach CES 2026 przez firmy Bosch, ThunderSoft, MediaTek.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator dekodowania związany z przepustowością)
**Wymagania wstępne:** Faza 17 · 04 (vLLM obsługująca elementy wewnętrzne), Faza 17 · 09 (kwantyzacja produkcji)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego wnioskowanie mobilnego LLM jest ograniczone przepustowością pamięci, a obliczenia są drugorzędne.
- Wylicz cztery cele brzegowe (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) i dopasuj każdy do przypadku użycia.
- Wymień lukę w zasięgu WebGPU w roku 2026 (nadrabianie zaległości w przeglądarce Firefox Android) i lądowanie w przeglądarce Safari iOS 26.
- Wybierz format kwantyzacji dla każdego celu (Core ML INT4 + FP16 dla ANE, QNN INT8/INT4 dla Hexagon, WebGPU Q4 dla przeglądarki, NVFP4 dla Jetson Thor).

## Problem

Klient chce chatbota na urządzeniu: najpierw głosowego, domyślnie prywatnego, działającego offline. Na MacBooku Pro M3 Max Llama 3.1 8B Q4 działa z prędkością ~55 tok/s — w porządku. Na iPhonie 16 Pro ten sam model działa z szybkością 3 tok/s – nie jest dobrze. Na Androidzie średniej klasy ze Snapdragonem 8 Gen 3, 7 tok/s. W przeglądarce poprzez WebGPU na Chrome Android v121+, 4-8 tok/s w zależności od urządzenia.

Różnice w przepustowości nie są problemem przenoszenia. Jest to różnica w przepustowości razy format kwantyzacji razy to, czy jednostka NPU jest dostępna z przestrzeni użytkownika. Wnioskowanie o krawędziach w roku 2026 to cztery różne problemy z czterema różnymi rozwiązaniami.

## Koncepcja

### Przepustowość to prawdziwy pułap

Dekodowanie odczytuje pełny zestaw wag dla każdego tokena. Jeden model 7B w czwartym kwartale ma 3,5 GB. Odczyt 3,5 GB przy 50 GB/s zajmuje 70 ms — teoretyczny pułap ~14 tok/s. Przy 90 GB/s (wysokiej klasy mobilna pamięć DRAM) pułap wzrasta do ~25 tok/s. Żadna ilość obliczeń nie pomoże poniżej tej liczby.

Datacenter HBM3 przy 3 TB/s oczyszcza te same 3,5 GB w 1,2 ms — maksymalna prędkość wynosi 830 tok/s. Ten sam model, ta sama waga. Inny podsystem pamięci.

### Silnik neuronowy Apple (M4 / A18)

- Do 38 TOPÓW. Ujednolicona pamięć (CPU i ANE korzystają z tej samej puli) — brak narzutu na kopiowanie.
- Dostęp poprzez Core ML + `.mlmodel` skompilowane modele lub poprzez Metal Performance Shaders (MPS) poprzez PyTorch.
- Backend Llama.cpp Metal używa MPS, a nie bezpośrednio ANE; natywny ANE wymaga konwersji Core ML.
- Najlepsza praktyczna ścieżka dla aplikacji na iOS w 2026 r.: Core ML z wagami INT4 + aktywacje FP16.

### Qualcomm Hexagon (Snapdragon X Elite / 8 Gen 4)

- Do 45 TOPÓW. Zintegrowany z procesorem i procesorem graficznym w SoC, ale oddzielna domena pamięci.
- QNN (Qualcomm Neural Network) SDK i AI Hub zapewniają konwersję z PyTorch/ONNX.
- Szablony czatu, Lama 3.2, Phi-3 są dostarczane jako artefakty najwyższej klasy w AI Hub.

### Jednostki NPU Intel/AMD (Lunar Lake, Ryzen AI 300)

- 40-50 TOPÓW. Oprogramowanie pozostaje w tyle za Apple/Qualcomm; OpenVINO się poprawia, ale jest niszowy.
- Najlepsze dla aplikacji pilota Windows ARM; natywnie na komputerach stacjonarnych AMD/Intel w trybie lokalnym.

### WebGPU + WebLLM

- Uruchamiaj modele w przeglądarce za pomocą shaderów obliczeniowych WebGPU; bez instalacji.
- Lama 3.1 8B Q4 przy ~41 tok/s na M3 Max — około 70-80% wersji natywnej za pośrednictwem tego samego backendu.
- 17,6 tys. gwiazd GitHuba w WebLLM; API JS kompatybilne z OpenAI; Apache 2.0.
- Zasięg na rok 2026: Chrome Android v121+, Safari iOS 26 GA, Firefox Android wciąż nadrabiają zaległości. Ogółem ~70-75% zasięgu sieci komórkowej.

### Rodzina NVIDIA Jetson

- Orin Nano Super (8 GB): pasuje do Llama 3.2 3B, Phi-3 przy dobrym tok/s.
- AGX Orin: uruchamia gpt-oss-20b przez vLLM z szybkością ~40 tok/s.
- Thor / T4000 (JetPack 7.1): wydajność 2x AGX Orin, obsługa EAGLE-3 i NVFP4.
— TensorRT Edge-LLM (2026) obsługuje dekodowanie spekulatywne EAGLE-3, wagi NVFP4, wstępne wypełnianie fragmentami — optymalizacje centrum danych przeniesione na brzeg.

### Wybór kwantyzacji na cel

| Cel | Formatuj | Notatki |
|--------|--------|-------|
| Jabłko ANE | Wagi INT4 + aktywacje FP16 | Podstawowa ścieżka konwersji ML |
| Sześciokąt Qualcomma | QNN INT8 / INT4 | Konwertery AI Hub |
| WebGPU / WebLLM | Q4 MLC (q4f16_1) | Użyj `mlc_llm convert_weight` + skompilowanego `.wasm`; GGUF nie jest obsługiwany |
| Jetson Orin Nano | Q4 GGUF lub TRT-LLM INT4 | Związany z pamięcią |
| Jetson AGX / Thor | NVFP4 + FP8 KV | Ścieżka Edge-LLM |

### Pułapka długokontekstowa na krawędzi

Kontekst 128 KB w Lamie 3.1 to funkcja centrum danych. Na telefonie z 8 GB RAM, model 4 GB + 2 GB pamięci podręcznej KV na 32 tys. tokenów + obciążenie systemu operacyjnego = OOM. Wdrożenia brzegowe utrzymują kontekst w rozdzielczości 4K–8K, chyba że zostanie zaakceptowana agresywna kwantyzacja KV (Q4 KV).

### Głos to zabójcza aplikacja

Agenci głosowi są wrażliwi na opóźnienia (pierwszy token < 500 ms). Lokalne wnioskowanie całkowicie eliminuje opóźnienia sieci. W połączeniu z zamianą mowy na tekst (warianty Whisper Turbo działają na krawędzi) i wnioskowanie brzegowe staje się pętlą głosową o jakości produkcyjnej.

### Liczby, które powinieneś zapamiętać

- Apple M4 / A18 ANE: 38 TOPÓW.
- Qualcomm Hexagon SD X Elite: 45 TOPÓW.
- WebLLM M3 Max: ~41 tok/s na Lamie 3.1 8B Q4.
- AGX Orin: ~40 tok/s na gpt-oss-20b przez vLLM.
- Różnica w przepustowości na granicy centrum danych: 30-50x.
- Zasięg mobilny WebGPU: ~70-75% (opóźnienie przeglądarki Firefox w systemie Android).

## Użyj tego

`code/main.py` oblicza teoretyczne pułapy przepustowości dekodowania na podstawie matematyki związanej z przepustowością dla celów brzegowych. Porównuje się z obserwowanymi testami porównawczymi i podkreśla, gdzie wąskim gardłem jest przepustowość, a nie obliczenia.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-edge-target-picker.md`. Biorąc pod uwagę platformę (iOS/Android/przeglądarka/Jetson), model i budżet opóźnienia/pamięci, wybiera format kwantyzacji i potok konwersji.

## Ćwiczenia

1. Uruchom `code/main.py`. W przypadku modelu 7B w czwartym kwartale na procesorze Snapdragon 8 Gen 3 (przepustowość ~77 GB/s) oblicz pułap dekodowania. Porównaj z obserwowanymi 6-8 tok/s – czy czas działania jest efektywny?
2. WebGPU na Androidzie wymaga przeglądarki Chrome v121+. Zaprojektuj rezerwę dla starszych przeglądarek — po stronie serwera za pośrednictwem tego samego interfejsu API zgodnego z OpenAI.
3. Twoja aplikacja na iOS wymaga przesyłania strumieniowego w kontekście 4K. Która kombinacja modelu/formatu pozwala zachować mniej niż 4 GB aktywnej pamięci w telefonie iPhone 16?
4. Jetson AGX Orin uruchamia gpt-oss-20b z szybkością 40 tok/s. Jetson Nano pasuje tylko do 3B. Jeśli Twój produkt jest skierowany do obu, jak ujednolicić stos wnioskowań?
5. Przedyskutuj, czy „WebLLM będzie gotowy do produkcji w 2026 roku”. Podaj zasięg, wydajność i lukę w Firefoksie na Androida.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| ANE | „Silnik neuronowy Apple” | NPU na urządzeniu w serii M i A; zunifikowana pamięć |
| Sześciokąt | „Qualcomm NPU” | Snapdragon NPU; QNN SDK dla dostępu |
| WebGPU | „GPU przeglądarki” | API przeglądarki GPU zgodne ze standardem W3C; Chrome/Safari 2026 |
| WebLLM | „Środowisko wykonawcze LLM przeglądarki” | projekt MLC-LLM; Apache 2.0; JS zgodny z OpenAI |
| Jetson | „Krawędź NVIDIA” | Rodzina Orin Nano / AGX / Thor / T4000 |
| TRT Edge-LLM | „Tensor krawędziowyRT” | Port brzegowy 2026 TensorRT-LLM; EAGLE-3 + NVFP4 |
| Ujednolicona pamięć | „wspólny basen” | Procesor i NPU widzą tę samą pamięć RAM; brak narzutu na kopiowanie |
| Ograniczone pasmo | „ograniczona pamięć” | Dekodowanie bramkowane bajtami/s odczytu wag |
| Rdzeń ML | „Konwersja Apple” | Framework Apple dla modeli natywnych ANE |
| QNN | „Stos Qualcomma” | Zestaw SDK sieci neuronowej Qualcomm |

## Dalsze czytanie

– [Status Unii On-Device LLMs 2026](https://v-chandra.github.io/on-device-llms/) – krajobraz i testy porównawcze.
- [NVIDIA Jetson Edge AI](https://developer.nvidia.com/blog/getting-started-with-edge-ai-on-nvidia-jetson-llms-vlms-and-foundation-models-for-robotics/) — Orin / AGX / Thor.
— [NVIDIA TensorRT Edge-LLM](https://developer.nvidia.com/blog/accelerating-llm-and-vlm-inference-for-automotive-and-robotics-with-nvidia-tensorrt-edge-llm/) — ogłoszenie dotyczące portu brzegowego na rok 2026.
- [WebLLM (arXiv:2412.15803)](https://arxiv.org/html/2412.15803v2) — projekt i testy porównawcze.
- [Apple Core ML](https://developer.apple.com/documentation/coreml) — konwersja natywna ANE.
- [Qualcomm AI Hub](https://aihub.qualcomm.com/) — modele wstępnie przekonwertowane dla Hexagon.