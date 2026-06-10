# Wybór silnika wnioskowania na własnej infrastrukturze (Self-Hosted) — llama.cpp, Ollama, TGI, vLLM, SGLang

> W obszarze wnioskowania na własnej infrastrukturze dominują cztery silniki. Wybór odpowiedniego rozwiązania zależy od posiadanego sprzętu, skali wdrożenia oraz ekosystemu. **llama.cpp** to najszybszy silnik dla procesorów (CPU) – oferuje najszersze wsparcie dla modeli oraz pełną kontrolę nad kwantyzacją i wielowątkowością. **Ollama** pozwala na instalację na komputerze lokalnym za pomocą jednego polecenia, jednak jest o 15-30% wolniejsza od czystego llama.cpp (z powodu narzutu serializacji Go/CGo i warstwy HTTP), wykazując nawet 3-krotnie niższą przepustowość pod obciążeniem produkcyjnym. **TGI (Text Generation Inference) weszło w tryb konserwacji (maintenance mode) 11 grudnia 2025 roku** – od tej pory publikowane są wyłącznie poprawki błędów; silnik oferuje o ok. 10% niższą przepustowość niż vLLM, ale wyróżnia się historycznie najlepszą obserwowalnością i integracją z ekosystemem Hugging Face. Ze względu na wstrzymanie rozwoju, wybór TGI dla nowych projektów jest ryzykowny – standardem stają się SGLang oraz vLLM. **vLLM** to podstawowy silnik produkcyjny ogólnego przeznaczenia – wersja v0.15.1 (luty 2026) wprowadza optymalizacje dla PyTorch 2.10, układów RTX Blackwell SM120 oraz H200. **SGLang** to silnik zoptymalizowany pod kątem zadań agentowych, konwersacji wieloetapowych (multi-turn) oraz intensywnego współdzielenia prefiksów promptów – napędza już ponad 400 000 układów GPU w instalacjach produkcyjnych (np. w xAI, LinkedIn, Cursor, Oracle, GCP, Azure, AWS). Ograniczenia sprzętowe: środowisko tylko z procesorem (CPU-only) wymusza użycie llama.cpp; platformy AMD lub inne niż NVIDIA ograniczają wybór do vLLM/SGLang (ponieważ TensorRT-LLM od NVIDIA jest zablokowany na innym sprzęcie). Rekomendowany schemat przepływu (pipeline): środowisko lokalne (dev) = Ollama, staging = llama.cpp, produkcja (prod) = vLLM lub SGLang, z zachowaniem tych samych wag modeli (GGUF/HF) na każdym etapie.

**Typ:** Teoria / Nauka
**Języki:** Python (stdlib, spacer po drzewie decyzyjnym silnika)
**Wymagania wstępne:** Wszystkie lekcje fazy 17 dotyczące silników (04, 06, 07, 09, 18)
**Czas:** ~45 minut

## Cele nauczania

- Dobierz silnik wnioskowania na podstawie dostępnego sprzętu (CPU / AMD / NVIDIA Hopper / Blackwell), skali (1 / 100 / 10 000 użytkowników) oraz charakterystyki obciążenia (czat ogólny / scenariusze agentowe / długi kontekst).
- Wyjaśnij konsekwencje przejścia TGI w tryb konserwacji (11 grudnia 2025 r.) i uzasadnij migrację nowych wdrożeń w stronę vLLM lub SGLang.
- Opisz proces promocji kodu i modeli (dev/staging/prod) przy zachowaniu tych samych wag modeli (GGUF lub HF).
- Wyjaśnij, dlaczego architektura CPU-only wymaga użycia llama.cpp, a karty graficzne AMD uniemożliwiają skorzystanie z TensorRT-LLM (TRT-LLM).

## Problem

Twój zespół rozpoczyna prace nad nowym wdrożeniem modelu LLM na własnej infrastrukturze. Jeden inżynier rekomenduje Ollamę, drugi vLLM, a trzeci pyta, czy gotowe kontenery TGI nie będą najprostszym rozwiązaniem. Każda z tych propozycji ma swoje uzasadnienie w określonych warunkach, ale żadna nie jest uniwersalna.

Wybór silnika opiera się na prostym schemacie decyzyjnym: najpierw analizujemy sprzęt, następnie skalę ruchu, a na końcu charakterystykę zapytań. Wstrzymanie aktywnego rozwoju TGI (przejście w tryb konserwacji 11 grudnia 2025 r.) znacząco zmieniło domyślne zalecenia projektowe.

## Koncepcja

### Pięć silników

| Silnik wnioskowania | Zastosowanie | Uwagi |
|--------|----------|-------|
| **llama.cpp** | Urządzenia brzegowe (edge) / środowiska CPU / pełna kontrola nad zasobami | Najwyższa wydajność na procesorach, precyzyjne sterowanie parametrami |
| **Ollama** | Praca lokalna na komputerach programistów (jeden użytkownik) | Szybka instalacja; do 30% wolniejszy od czystego llama.cpp; duży narzut pod obciążeniem |
| **TGI** | Integracja z ekosystemem Hugging Face | Wstrzymany rozwój (tylko poprawki błędów od 11 grudnia 2025 r.) |
| **vLLM** | Środowiska produkcyjne ogólnego przeznaczenia pod dużym obciążeniem | Standard dla wdrożeń produkcyjnych; wersja v0.15.1 (luty 2026 r.) |
| **SGLang** | Systemy agentowe, konwersacje wieloetapowe, współdzielenie cache KV | Wyjątkowa wydajność dzięki RadixAttention; szerokie wdrożenia produkcyjne |

### Krok 1: Weryfikacja sprzętu

**Tylko procesor (CPU-only)**: llama.cpp. Ollama również jest obsługiwana, lecz wykazuje niższą wydajność. Inne silniki nie oferują konkurencyjnej optymalizacji dla CPU.

**Układy GPU AMD**: vLLM (ze wsparciem dla AMD ROCm) lub SGLang. TensorRT-LLM (TRT-LLM) nie wchodzi w grę, ponieważ działa wyłącznie na sprzęcie NVIDIA.

**NVIDIA Hopper (H100 / H200)**: vLLM, SGLang lub TRT-LLM. Wszystkie trzy silniki oferują najwyższą, zbliżoną wydajność.

**NVIDIA Blackwell (B200 / GB200)**: TRT-LLM zapewnia maksymalną przepustowość (Faza 17 · Lekcja 07), natomiast vLLM i SGLang szybko nadrabiają dystans.

**Apple Silicon (seria M)**: llama.cpp (optymalizacja Metal). Ollama działa jako nakładka na ten silnik.

### Krok 2: Skala wdrożenia

**Pojedynczy użytkownik / środowisko deweloperskie**: Ollama. Błyskawiczne uruchomienie za pomocą jednego polecenia.

**10-100 jednoczesnych użytkowników**: pojedyncza instancja vLLM na dedykowanej karcie GPU.

**100-10 000 jednoczesnych użytkowników**: rozproszony stos produkcyjny vLLM (Faza 17 · Lekcja 18) lub SGLang.

**Ponad 10 000 jednoczesnych użytkowników (skala enterprise)**: vLLM ze zdezagregowaną architekturą prefill/decode (Faza 17 · Lekcja 17) oraz mechanizmem LMCache (Faza 17 · Lekcja 18).

### Krok 3: Charakterystyka obciążenia (Workload)

**Standardowy czat / sesje pytań i odpowiedzi (Q&A)**: vLLM stanowi najlepszy i najbardziej wszechstronny wybór domyślny.

**Scenariusze agentowe i konwersacje wieloetapowe**: SGLang z technologią RadixAttention (Faza 17 · Lekcja 06) deklasuje konkurencję.

**Systemy RAG z powtarzalnymi prefiksami w zapytaniach**: SGLang ze względu na zaawansowane współdzielenie cache.

**Autouzupełnianie i generowanie kodu**: vLLM sprawdza się dobrze, natomiast SGLang oferuje lepszą wydajność cache przy powtarzalnym kontekście.

**Obsługa bardzo długiego kontekstu (128 KB+)**: vLLM (z funkcją chunked prefill) lub SGLang (z wielopoziomowym zarządzaniem pamięcią podręczną KV).

### Status TGI (Maintenance Mode)

Silnik TGI od Hugging Face wszedł w fazę konserwacji 11 grudnia 2025 roku. Od tego czasu wprowadzane są wyłącznie krytyczne poprawki błędów. Historycznie silnik ten wyróżniał się doskonałą obserwowalnością i natywną integracją z repozytorium Hugging Face, jednak wydajnościowo ustępuje vLLM.

W przypadku nowych wdrożeń zaleca się rezygnację z TGI na rzecz stabilniejszych i rozwijanych alternatyw, takich jak vLLM czy SGLang. Istniejące środowiska oparte na TGI powinny zaplanować migrację.

### Promocja środowisk i wag modeli

Standardowy przepływ: deweloperskie (Ollama) -> stagingowe (llama.cpp) -> produkcyjne (vLLM), przy użyciu dokładnie tych samych wag modeli (GGUF lub HF) na każdym z tych etapów. Pozwala to na szybką pracę lokalną i dokładne odwzorowanie parametrów kwantyzacji przed wdrożeniem produkcyjnym.

### Ograniczenia silnika Ollama

Ollama jest doskonałym narzędziem deweloperskim, ale nie nadaje się do współdzielonych środowisk produkcyjnych. Narzut serializacji Go/CGo i warstwy HTTP, uproszczona obsługa żądań współbieżnych oraz braki w integracji z OpenTelemetry dyskwalifikują ją w zastosowaniach wielodostępnych. Ollama powinna być stosowana lokalnie; w produkcji jej miejsce zajmuje vLLM.

### Hosting własny (Self-Hosted) a usługi zarządzane

Zarządzane usługi chmurowe zostały szczegółowo omówione w Fazie 17 (Lekcje 01 oraz 02). Ta lekcja koncentruje się na scenariuszu, w którym świadomie decydujesz się na własną infrastrukturę (self-hosted). Główne powody takiego kroku to restrykcyjne wymogi dotyczące suwerenności danych, konieczność głębokiej personalizacji modeli, korzyści kosztowe (TCO) przy bardzo dużej skali operacji oraz wykorzystanie niszowych modeli niedostępnych u zewnętrznych dostawców API.

### Kluczowe dane do zapamiętania

- Przejście TGI w tryb konserwacji: 11 grudnia 2025 roku.
- Silnik vLLM v0.15.1 (luty 2026 r.): wsparcie dla PyTorch 2.10 oraz architektury Blackwell SM120.
- Skala produkcyjna SGLang: ponad 400 000 aktywnych instancji GPU.
- Różnica wydajności Ollama vs llama.cpp: 15-30% wolniej lokalnie; do 3x niższa przepustowość pod obciążeniem.

## Kod demonstracyjny

Skrypt `code/main.py` realizuje drzewo decyzyjne wyboru silnika: na podstawie dostępnego sprzętu, skali zapytań i typu zadań rekomenduje optymalne rozwiązanie wraz ze szczegółowym uzasadnieniem.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-engine-picker.md`. Na podstawie zdefiniowanych ograniczeń infrastrukturalnych i wymagań dobiera on właściwy silnik wnioskowania oraz opisuje plan ewentualnej migracji.

## Ćwiczenia

1. Uruchom skrypt `code/main.py` dla parametrów swojej infrastruktury. Czy wygenerowana rekomendacja pokrywa się z Twoją oceną projektową?
2. Dysponujesz klastrem złożonym z 12 układów H100 (NVIDIA) oraz 8 układów MI300X (AMD). Jaki silnik wnioskowania powinieneś wdrożyć i dlaczego TensorRT-LLM jest wykluczony w tym scenariuszu?
3. Zespół inżynierów nalega na użycie TGI w nowych wdrożeniach, argumentując to wcześniejszym doświadczeniem. Sformułuj argumenty techniczne i biznesowe uzasadniające migrację do nowszego silnika.
4. Planujesz przejście z lokalnego środowiska deweloperskiego opartego na Ollamie do produkcyjnego vLLM. Jakie zmiany należy wprowadzić w kwantyzacji modeli, konfiguracji serwerów oraz systemach obserwowalności?
5. Projektujesz system RAG charakteryzujący się długim, powtarzalnym prefiksem zapytań (P99 = 8K tokenów) o wysokim stopniu współdzielenia przez użytkowników. Wybierz silnik i powiąż go z mechanizmami opisanymi w Fazie 17 (Lekcje 11 oraz 18).

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| llama.cpp | „silnik CPU” | Wysoce zoptymalizowane pod procesory (CPU) narzędzie obsługujące formaty kwantyzacji |
| Ollama | „Ollama na laptopa” | Proste w instalacji narzędzie deweloperskie do lokalnych testów zapytań |
| TGI | „silnik Hugging Face” | Rozwiązanie od Hugging Face; w trybie konserwacji (brak nowych funkcji) od końca 2025 r. |
| vLLM | „produkcyjny standard” | Podstawowy silnik produkcyjny ogólnego przeznaczenia z zaawansowaną pamięcią podręczną |
| SGLang | „silnik dla agentów” | Silnik zoptymalizowany pod kątem częstego współdzielenia cache KV (RadixAttention) i scenariuszy agentowych |
| TensorRT-LLM | „zamknięty silnik NVIDIA” | Najszybszy silnik dedykowany wyłącznie kartom graficznym NVIDIA, kluczowy przy architekturze Blackwell |
| GGUF | „pliki GGUF” | Format plików modeli zoptymalizowany pod kątem uruchamiania na procesorach i kartach konsumenckich |
| Stos produkcyjny | „vLLM na Kubernetes” | Referencyjna architektura produkcyjna opisana w Lekcji 18 Fazy 17 |
| Ścieżka promocji | „dev -> staging -> prod” | Spójny przepływ wdrożeniowy (Ollama -> llama.cpp -> vLLM) przy zachowaniu tych samych wag modelu |

## Materiały uzupełniające

- [Narzędzia stworzone przez sztuczną inteligencję – vLLM vs Ollama vs llama.cpp vs TGI 2026](https://www.aimadetools.com/blog/vllm-vs-ollama-vs-llamacpp-vs-tgi/)
- [Morph — llama.cpp kontra Ollama 2026](https://www.morphllm.com/comparisons/llama-cpp-vs-ollama)
- [n1n.ai — kompleksowe porównanie silnika wnioskowania LLM](https://explore.n1n.ai/blog/llm-inference-engine-comparison-vllm-tgi-tensorrt-sglang-2026-03-13)
- [PremAI — 10 najlepszych alternatyw vLLM 2026](https://blog.premai.io/10-best-vllm-alternatives-for-llm-inference-in-production-2026/)
- [Ogłoszenie o konserwacji TGI](https://github.com/huggingface/text-generation-inference) — informacje o wersji.
- [Informacje o wersji vLLM v0.15.1](https://github.com/vllm-project/vllm/releases)
