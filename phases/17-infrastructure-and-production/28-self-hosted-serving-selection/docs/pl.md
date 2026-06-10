# Wybór serwowania na własnym serwerze — llama.cpp, Ollama, TGI, vLLM, SGLang

> W 2026 r. w wnioskowaniu na własnym serwerze dominują cztery silniki. Wybierz na podstawie sprzętu, skali i ekosystemu. **llama.cpp** jest najszybszy na procesorze — najszersza obsługa modeli, pełna kontrola nad kwantyzacją i wątkowością. **Ollama** to instalacja na laptopie deweloperskim za pomocą jednego polecenia, ~15-30% wolniejsza niż llama.cpp (serializacja Go + CGo + HTTP), 3-krotna luka w przepustowości przy obciążeniu podobnym do produktu. **TGI weszło w tryb konserwacji 11 grudnia 2025 r.** — tylko poprawki błędów, ~10% wolniejsza przepustowość w porównaniu do vLLM, ale historycznie najwyższa obserwowalność i integracja z ekosystemem HF. Ze względu na status konserwacji jest to ryzykowne rozwiązanie w dłuższej perspektywie — SGLang lub vLLM są bezpieczniejszymi ustawieniami domyślnymi dla nowych projektów. **vLLM** to domyślna wersja produkcyjna ogólnego przeznaczenia — wersja 0.15.1 (luty 2026) dodaje optymalizację PyTorch 2.10, RTX Blackwell SM120 i H200. **SGLang** to agentyczny specjalista w zakresie wieloobrotowości / dużej liczby prefiksów — ponad 400 000 procesorów graficznych w produkcji (xAI, LinkedIn, Cursor, Oracle, GCP, Azure, AWS). Ograniczenia sprzętowe: tylko procesor → tylko llama.cpp. AMD / inne niż NVIDIA → tylko vLLM (TRT-LLM jest zablokowany przez NVIDIA). Wzór potoku 2026: dev = Ollama, staging = llama.cpp, prod = vLLM lub SGLang. Te same wagi GGUF/HF w całym tekście.

**Typ:** Ucz się
**Języki:** Python (stdlib, spacer po drzewie decyzyjnym silnika)
**Wymagania wstępne:** Wszystkie lekcje fazy 17 dotyczące silników (04, 06, 07, 09, 18)
**Czas:** ~45 minut

## Cele nauczania

- Wybierz silnik, biorąc pod uwagę sprzęt (CPU / AMD / NVIDIA Hopper / Blackwell), skalę (1 użytkownik / 100 / 10 000) i obciążenie (czat ogólny / agent / długi kontekst).
- Podaj status trybu konserwacji TGI 2026 (11 grudnia 2025) i dlaczego skłania on nowe projekty w stronę vLLM lub SGLang.
- Opisz potok deweloperski/staging/prod, używając w całym tekście tych samych wag GGUF lub HF.
- Wyjaśnij, dlaczego „tylko procesor” wymusza llama.cpp, a „AMD” wyklucza TRT-LLM.

## Problem

Twój zespół rozpoczyna nowy, własny projekt LLM. Jeden inżynier mówi Ollama, inny mówi vLLM, trzeci mówi: „Czy TGI nie działa po prostu od razu po wyjęciu z pudełka?” Wszystkie trzy sprawdzają się w różnych kontekstach. Żaden nie jest odpowiedni dla wszystkich.

W 2026 r. liczy się drzewo wyboru: po pierwsze sprzęt, po drugie skala, po trzecie obciążenie pracą. Jedno konkretne wydarzenie w roku 2025 — wejście TGI w tryb konserwacji 11 grudnia — powoduje zmianę ustawień domyślnych dla nowych projektów.

## Koncepcja

### Pięć silników

| Silnik | Najlepsze dla | Notatki |
|--------|----------|-------|
| **llama.cpp** | Procesor / krawędź / minimalna głębokość / najszersza obsługa modeli | Najszybszy na procesorze, pełna kontrola |
| **Ollama** | Laptopy deweloperskie, pojedynczy użytkownik, instalacja za pomocą jednego polecenia | 15-30% wolniejszy niż llama.cpp; 3x luka w przepustowości produktu |
| **TGI** | Ekosystem HF, branże regulowane | **Tryb konserwacji 11 grudnia 2025** |
| **vLLM** | Produkcja ogólnego przeznaczenia, ponad 100 użytkowników | Szeroka domyślność produkcji; v0.15.1 luty 2026 r. |
| **SGLang** | Agentyczne obciążenia wieloobrotowe, wymagające dużych prefiksów | Ponad 400 000 procesorów graficznych w produkcji |

### Decyzja dotycząca sprzętu

**Tylko procesor** → llama.cpp. Ollama też działa, ale jest wolniejsza. Żaden inny silnik nie jest konkurencyjny pod względem procesora.

**AMD GPU** → vLLM (obsługa AMD ROCm). SGLang również działa. TRT-LLM jest zablokowany przez firmę NVIDIA, więc odpada.

**NVIDIA Hopper (H100 / H200)** → vLLM lub SGLang lub TRT-LLM. Cała trójka z najwyższej półki.

**NVIDIA Blackwell (B200 / GB200)** → TRT-LLM jest liderem przepustowości (faza 17 · 07). vLLM i SGLang tuż za nimi.

**Apple Silicon (seria M)** → llama.cpp (metal). Ollama to podsumowuje.

### Decyzja podejmowana w skali sekundy

**1 użytkownik / lokalny programista** → Ollama. Jedno polecenie, pierwszy żeton w kilka sekund.

**10-100 użytkowników / mały zespół** → vLLM z pojedynczą kartą graficzną.

**100-10 tys. użytkowników/produkcja** → stos produkcyjny vLLM (faza 17 · 18) lub SGLang.

**ponad 10 tys. użytkowników na przedsiębiorstwo** → stos produkcyjny vLLM + zdezagregowany (faza 17 · 17) + LMCache (faza 17 · 18).

### Trzecia decyzja dotycząca obciążenia pracą

**Czat ogólny / Pytania i odpowiedzi** → vLLM wygrywa przy szerokim zakresie domyślnym.

**Agentyczny wieloobrotowy (narzędzia, planowanie, pamięć)** → Dominuje RadixAttention firmy SGLang (faza 17 · 06).

**RAG z częstym ponownym użyciem przedrostków** → SGLang.

**Generowanie kodu** → vLLM w porządku; SGLang nieco lepszy w pamięci podręcznej.

**Długi kontekst (128 KB+)** → vLLM + wstępne wypełnienie fragmentaryczne; SGLang + wielopoziomowy KV.

### Pułapka konserwacyjna TGI

Hugging Face TGI weszło w tryb konserwacji 11 grudnia 2025 r. — w przyszłości zostaną poprawione tylko błędy. Historycznie: najwyższa obserwowalność, najlepsza w swojej klasie integracja ekosystemu HF (karty modeli, narzędzia zabezpieczające), nieco w tyle za vLLM pod względem surowej przepustowości.

Dla nowych projektów w 2026 r.: domyślnie poza TGI. Istniejące wdrożenia TGI mogą być kontynuowane, ale ostatecznie powinny zostać poddane migracji. SGLang i vLLM to bezpieczniejsze ustawienia domyślne.

### Wzór potoku

Dev (Ollama) → inscenizacja (llama.cpp) → prod (vLLM). W całym tekście te same wagi GGUF lub HF. Inżynierowie szybko wykonują iteracje na laptopach; inscenizacja odzwierciedla kwantyzację produkcji; prod jest celem wyświetlania.

### Ostrzeżenie Ollama

Ollama jest świetna dla programistów. Nie nadaje się to do współdzielonej produkcji: serializacja Go HTTP zwiększa obciążenie, zarządzanie współbieżnością jest prostsze niż vLLM, opóźnienia w obsłudze OpenTelemetry. Korzystaj z Ollama tam, gdzie najlepiej — jeden użytkownik, jedno polecenie — i przełącz się na vLLM w celu udostępniania.

### Hosting własny czy zarządzany to osobna decyzja

Faza 17 · 01 (zarządzane hiperskalery), · 02 (platformy wnioskowania) zarządzane pokrycie. W tej lekcji założono, że podjąłeś już decyzję o samodzielnym gospodarzu. Powody samodzielnego hostowania: miejsce przechowywania danych, niestandardowe dostosowanie, całkowity koszt posiadania na dużą skalę, model domeny niedostępny na serwerze hostowanym.

### Liczby, które powinieneś zapamiętać

- Tryb konserwacji TGI: 11 grudnia 2025 r.
- vLLM v0.15.1: luty 2026; PyTorch 2.10; Obsługa Blackwell SM120.
- Powierzchnia produkcyjna SGLang: ponad 400 000 procesorów graficznych.
- Różnica w przepustowości Ollama vs llama.cpp: 15-30% wolniej; 3x pod obciążeniem prod.

## Użyj tego

`code/main.py` to narzędzie do przechodzenia przez drzewo decyzyjne: dany sprzęt + skala + obciążenie, wybiera silnik i wyjaśnia dlaczego.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-engine-picker.md`. Biorąc pod uwagę ograniczenia, wybiera silnik i pisze plan migracji.

## Ćwiczenia

1. Uruchom `code/main.py` ze swoim sprzętem/skalą/obciążeniem. Czy wynik jest zgodny z Twoją intuicją?
2. Twoja infrastruktura to 12 H100 i 8 MI300X AMD. Jaki silnik? Dlaczego TRT-LLM nie wchodzi w grę?
3. Zespół chce korzystać z TGI w 2026 roku, ponieważ „to jest to, co wiemy”. Dyskutuj na temat migracji.
4. Od dewelopera Ollama do prod vLLM: jakie zmiany w kwantyzacji, konfiguracji i obserwowalności?
5. Produkt RAG z prefiksem P99 o długości 8K i wysokim stopniem ponownego wykorzystania wśród najemców. Wybierz silnik i połącz go z Fazą 17 · 11 + 18.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| lama.cpp | „ten z procesorem” | Najszersza obsługa modeli, najszybszy procesor |
| Ollama | „ten laptop” | Instalacja za pomocą jednego polecenia, przepustowość na poziomie deweloperskim |
| TGI | „Serwacja HF” | Tryb konserwacji od grudnia 2025 r. |
| vLLM | „domyślny” | Szeroki poziom bazowy produkcji na 2026 r. |
| SGLang | „ten agent” | Duży przedrostek, RadixAttention |
| TRT-LLM | „Zablokowana karta NVIDIA” | Lider przepustowości Blackwell, tylko NVIDIA |
| GGUF | „Format lamy.cpp” | W pakiecie warianty ilościowe K |
| Stos produkcyjny | „vLLM K8” | Faza 17 · 18 wdrożenie odniesienia |
| Wzór rurociągu | „program → etap → produkt” | Ollama → llama.cpp → vLLM na tych samych ciężarach |

## Dalsze czytanie

– [Narzędzia stworzone przez sztuczną inteligencję – vLLM vs Ollama vs llama.cpp vs TGI 2026](https://www.aimadetools.com/blog/vllm-vs-ollama-vs-llamacpp-vs-tgi/)
– [Morph — llama.cpp kontra Ollama 2026](https://www.morphllm.com/comparisons/llama-cpp-vs-ollama)
- [n1n.ai — kompleksowe porównanie silnika wnioskowania LLM](https://explore.n1n.ai/blog/llm-inference-engine-comparison-vllm-tgi-tensorrt-sglang-2026-03-13)
- [PremAI — 10 najlepszych alternatyw vLLM 2026](https://blog.premai.io/10-best-vllm-alternatives-for-llm-inference-in-production-2026/)
– [Ogłoszenie o konserwacji TGI](https://github.com/huggingface/text-generation-inference) — informacje o wersji.
- [Informacje o wersji vLLM v0.15.1](https://github.com/vllm-project/vllm/releases)