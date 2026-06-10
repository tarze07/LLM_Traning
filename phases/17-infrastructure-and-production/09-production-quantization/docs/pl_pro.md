# Kwantyzacja na produkcji — AWQ, GPTQ, GGUF K-quants, FP8, MXFP4/NVFP4

> Format kwantyzacji nie jest uniwersalnym wyborem – zależy on od używanego sprzętu, silnika serwującego oraz specyfiki obciążenia. GGUF w wariantach Q4_K_M lub Q5_K_M dominuje w scenariuszach wykorzystujących procesory (CPU) i urządzenia brzegowe (edge), obsługiwane przez llama.cpp i Ollama. GPTQ sprawdza się najlepiej w vLLM, gdy wymagane jest uruchomienie wielu adapterów LoRA na tym samym modelu bazowym. AWQ z kernelami Marlin-AWQ zapewnia ok. 741 tokenów/s dla modelu klasy 7B, osiągając najwyższą dokładność (Pass@1) w precyzji INT4 – jest to domyślny standard produkcyjny w centrach danych w 2026 roku. Format FP8 pozostaje złotym środkiem dla architektur Hopper, Ada oraz Blackwell – gwarantuje niemal bezstratną jakość i jest szeroko wspierany. NVFP4 i MXFP4 (mikroskalowanie na architekturze Blackwell) to formaty bardzo agresywne, które wymagają weryfikacji jakości dla każdej warstwy/bloku modelu. Zespoły często wpadają w dwie pułapki: po pierwsze, zbiór danych kalibracyjnych musi odpowiadać domenie wdrożenia; po drugie, pamięć podręczna KV nie podlega kwantyzacji wag – twórcy zachwycający się tym, że „model zajmuje teraz tylko 4 GB”, zapominają o dodatkowych 10–30 GB na pamięć podręczną KV przy produkcyjnych wsadach (batches).

**Typ:** Ucz się
**Języki:** Python (stdlib, porównanie pamięci i przepustowości w różnych formatach)
**Wymagania wstępne:** Faza 10 · 13 (Podstawy kwantyzacji), Faza 17 · 04 (Wewnętrzne mechanizmy vLLM)
**Czas:** ~75 minut

## Cele nauczania

- Wymień sześć formatów kwantyzacji stosowanych produkcyjnie i wskaż ich optymalne zastosowania w 2026 r.
- Dokonaj wyboru formatu w oparciu o sprzęt (CPU vs GPU, Hopper vs Blackwell), silnik serwujący (vLLM, TRT-LLM, llama.cpp) oraz rodzaj obciążenia (zwykły czat, wnioskowanie logiczne, środowiska multi-LoRA).
- Oblicz oszczędność pamięci dla wag modelu oraz wielkość nienaruszonej pamięci podręcznej KV dla wybranego formatu.
- Zidentyfikuj pułapkę związaną ze zbiorem danych kalibracyjnych, która pogarsza jakość skwantowanych modeli w zadaniach dziedzinowych.

## Problem

Kwantyzacja pozwala na zmniejszenie zapotrzebowania na przepustowość pamięci oraz HBM, co jest kluczowe w fazie dekodowania. Model 70B w precyzji FP16 zajmuje ok. 140 GB pamięci. Po skwantowaniu wag do precyzji INT4 (przy użyciu AWQ lub GPTQ) model zajmuje już tylko 35 GB – dzięki czemu mieści się w pamięci pojedynczego układu H100 (80 GB), pozostawiając wolną przestrzeń na pamięć podręczną KV. Jest to niezwykle istotne, ponieważ przy 128 współbieżnych sekwencjach z kontekstem o długości 2k tokenów, sama pamięć podręczna KV zajmuje od 20 do 30 GB.

Jednak kwantyzacja nie jest darmowa. Agresywne zmniejszanie precyzji pogarsza jakość generowanych odpowiedzi, szczególnie w zadaniach wymagających logicznego myślenia. Różne formaty współpracują z różnymi silnikami wnioskowania, a dany sprzęt natywnie obsługuje tylko określone precyzje obliczeń. Ekosystem formatów w 2026 r. jest mocno zróżnicowany i nie można bezkrytycznie kopiować cudzych rozwiązań – decyzję należy podjąć w oparciu o posiadany stos technologiczny.

## Koncepcja

### Sześć formatów

| Format | Bity | Optymalne zastosowanie (Sweet spot) | Silniki |
|------------|------|-----------|---------|
| GGUF Q4_K_M / Q5_K_M | 4-5 | Procesory (CPU), urządzenia brzegowe, laptopy | llama.cpp, Ollama |
| GPTQ | 4-8 | Infrastruktura multi-LoRA na vLLM | vLLM, TGI |
| AWQ | 4 | Produkcja na GPU w centrach danych | vLLM (Marlin-AWQ), TGI |
| FP8 | 8 | Centra danych z układami Hopper/Ada/Blackwell | vLLM, TRT-LLM, SGLang |
| MXFP4 | 4 | Środowiska wielodzierżawcowe na Blackwell | TRT-LLM |
| NVFP4 | 4 | Środowiska wielodzierżawcowe na Blackwell | TRT-LLM |

### GGUF — Standard dla CPU i urządzeń brzegowych

GGUF to format kontenera plików, a nie sam schemat kwantyzacji – łączy on różne warianty kwantyzacji K-quant (Q2_K, Q3_K_M, Q4_K_M, Q5_K_M, Q6_K, Q8_0) w jednym pliku. Wersje Q4_K_M oraz Q5_K_M stanowią standard produkcyjny, oferując jakość zbliżoną do BF16 przy zużyciu 4-5 bitów na wagę. Jest to najlepszy wybór do uruchamiania modeli na procesorach (CPU) lub urządzeniach brzegowych, ponieważ llama.cpp jest najszybszym silnikiem wnioskowania dla CPU.

Spadek wydajności w vLLM: na modelu 7B osiąga się ok. 93 tokeny/s – format ten nie jest zoptymalizowany pod kątem działania na GPU. Używaj formatu GGUF wyłącznie wtedy, gdy środowiskiem docelowym jest procesor (CPU) lub urządzenie brzegowe.

### GPTQ — Wielodzierżawczość multi-LoRA na vLLM

GPTQ to algorytm kwantyzacji post-trainingowej wykorzystujący etap kalibracji. Dedykowane kernele Marlin znacząco przyspieszają działanie modeli na procesorach graficznych (2,6-krotny wzrost wydajności w porównaniu z GPTQ bez Marlin) – osiągając ok. 712 tokenów/s dla modeli klasy 7B.

Kluczowa zaleta: format GPTQ-Int4 obsługuje adaptery LoRA w vLLM. Jeśli hostujesz jeden model bazowy i 10–50 wariantów dostrojonych (fine-tuned) za pomocą LoRA, GPTQ jest jedyną słuszną drogą. Format NVFP4 na początku 2026 r. nie oferuje jeszcze wsparcia dla LoRA.

### AWQ — Domyślny format GPU w centrach danych

Metoda kwantyzacji wag uwzględniająca profil aktywacji. Pozwala na zachowanie pełnej precyzji dla ok. 1% najbardziej krytycznych wag modelu. Zastosowanie kerneli Marlin-AWQ zapewnia 10,9-krotne przyspieszenie w porównaniu z podejściem naiwnym, osiągając ok. 741 tokenów/s dla modelu klasy 7B przy zachowaniu najwyższej dokładności (Pass@1) wśród wszystkich formatów INT4.

Wybierz AWQ do obsługi modeli na nowoczesnych procesorach graficznych, o ile nie potrzebujesz obsługi wielu adapterów LoRA (wtedy wybierz GPTQ) lub agresywnego formatu FP4 na architekturze Blackwell (wtedy NVFP4).

### FP8 — Złoty środek

Format 8-bitowy zmiennoprzecinkowy. Gwarantuje niemal bezstratną jakość i posiada szerokie wsparcie w branży. Rdzenie Tensor w architekturze Hopper natywnie przyspieszają obliczenia FP8, a architektura Blackwell dziedziczy tę cechę. Format FP8 to bezpieczny wybór domyślny w 2026 r., zwłaszcza gdy kryterium jakości jest bezkompromisowe (np. w systemach wnioskowania logicznego, medycynie czy generowaniu kodu). Oszczędność pamięci jest o połowę mniejsza niż w przypadku INT4, jednak ryzyko degradacji modelu jest minimalne.

### MXFP4 / NVFP4 — Agresywny format dla Blackwell

4-bitowy format zmiennoprzecinkowy z mikroskalowaniem. Każdy blok wag ma przypisany własny współczynnik skali. Jest to format agresywny, ale sprzętowo przyspieszany przez rdzenie Tensor architektury Blackwell. Pozwala na skrócenie zapotrzebowania na pamięć o połowę w porównaniu z FP8 (zgodnie z opisem w Fazie 17 · 07).

Ograniczenia:
- Brak wsparcia dla adapterów LoRA (stan na początek 2026 r.).
- Zauważalny spadek jakości w zadaniach wymagających logicznego myślenia.
- Wymaga każdorazowej weryfikacji na własnym zbiorze testowym.

### Pułapka kalibracyjna

Metody AWQ oraz GPTQ wymagają użycia zbioru danych kalibracyjnych – najczęściej stosuje się C4 lub WikiText. W przypadku modeli wyspecjalizowanych (np. programistycznych, medycznych, prawnych) kalibracja na ogólnych tekstach z internetu powoduje, że algorytm chroni niewłaściwe wagi. Może to prowadzić do spadku metryki Pass@1 w teście HumanEval o kilka punktów procentowych.

Rozwiązanie: Przeprowadzaj kalibrację na danych z domeny docelowej. Zazwyczaj wystarczy przygotować kilkaset reprezentatywnych próbek dziedzinowych. Przed wdrożeniem produkcyjnym zawsze przetestuj model na zbiorze walidacyjnym (eval set).

### Pułapka pamięci podręcznej KV

AWQ zmniejsza rozmiar wag modelu do 4 bitów. Pamięć podręczna KV jest alokowana osobno i pozostaje w precyzji FP16 lub FP8. Dla modelu 70B skwantowanego za pomocą AWQ:

- Wagi: ok. 35 GB (spadek ze 140 GB w INT4).
- Pamięć podręczna KV (dla 128 jednoczesnych zapytań o długości kontekstu 2k): ok. 20 GB.
- Aktywacje: ok. 5 GB.
- Łącznie: ok. 60 GB – co pozwala na zmieszczenie się w pamięci układu H100 (80 GB).

Naiwne stwierdzenie: „skwantowałem model do 4 GB” ignoruje fakt, że pozostałe 30-50 GB pamięci zajmują struktury dynamiczne. Budżet pamięci HBM należy zawsze planować całościowo.

Osobna kwantyzacja pamięci podręcznej KV (np. FP8 KV lub INT8 KV) to niezależna decyzja projektowa, która wiąże się z własnymi kompromisami – wpływa bezpośrednio na dokładność obliczeń mechanizmu uwagi i nie stanowi darmowego zysku wydajnościowego.

### Format AWQ INT4 a zadania logiczne (Reasoning)

Zadania wymagające logicznego myślenia (łańcuch myśli, matematyka, generowanie kodu z długim kontekstem) wyraźnie tracą na jakości przy zastosowaniu agresywnej kwantyzacji. Format AWQ INT4 powoduje spadek o ok. 3-5 punktów procentowych w teście benchmarkowym MATH. W takich zastosowaniach należy pozostać przy precyzji FP8 lub BF16, akceptując wyższe zapotrzebowanie na pamięć.

### Poradnik wyboru na rok 2026

- Wnioskowanie na CPU lub urządzeniach brzegowych: format GGUF Q4_K_M.
- Wnioskowanie na GPU, typowe zadania konwersacyjne (brak LoRA): format AWQ.
- Wnioskowanie na GPU z obsługą wielu adapterów LoRA: format GPTQ z kernelami Marlin.
- Wnioskowanie oparte na logice (Reasoning): format FP8.
- Centra danych Blackwell, po weryfikacji jakości: format NVFP4 + FP8 KV.
- Scenariusze niejednoznaczne: przeprowadź ewaluację na próbie 1000 zapytań dla każdego formatu.

## Użycie

Skrypt `code/main.py` oblicza zapotrzebowanie na pamięć (wagi + KV + aktywacje) oraz relatywną przepustowość dla sześciu formatów przy różnych rozmiarach modeli. Pokazuje, w których scenariuszach dominuje pamięć podręczna KV, kiedy kompresja wag przynosi największe zyski, a kiedy format FP8 stanowi najbezpieczniejszy wybór.

## Efekt końcowy

W ramach tej lekcji tworzony jest dokument `outputs/skill-quantization-picker.md`. Na podstawie typu sprzętu, rozmiaru modelu, charakteru obciążenia oraz tolerancji na spadki jakości dokonuje on wyboru optymalnego formatu i generuje plan kalibracji oraz walidacji modelu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Dla modelu 70B obsługującego 128 jednoczesnych zapytań z kontekstem o długości 2k tokenów, oblicz zapotrzebowanie na pamięć HBM dla każdego z formatów. Które formaty pozwalają na uruchomienie modelu na pojedynczym procesorze graficznym H100 80 GB?
2. Posiadasz model programistyczny klasy 7B. Wybierz odpowiedni format kwantyzacji i uzasadnij swoją decyzję. Jeśli błędnie ocenisz tolerancję na spadki jakości, jaka będzie Twoja strategia wyjścia?
3. Oblicz rozmiar zbioru danych kalibracyjnych niezbędny do przeprowadzenia kalibracji AWQ dla modelu z domeny medycznej. Dlaczego większa liczba danych kalibracyjnych nie zawsze przekłada się na lepszą jakość modelu?
4. Zapoznaj się z dokumentacją techniczną kerneli Marlin-AWQ. Wyjaśnij w trzech zdaniach, dlaczego format AWQ osiąga przepustowość 741 tokenów/s dla modelu 7B, podczas gdy standardowy GPTQ uzyskuje ok. 712 tokenów/s.
5. W jakich przypadkach uzasadnione jest łączenie wag w formacie AWQ z pamięcią podręczną KV w formacie FP8, zamiast pozostawiania KV w precyzji BF16?

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| GGUF | „format llama.cpp” | Format zapisu modeli obsługujący warianty K-quant; standard dla CPU i urządzeń brzegowych |
| Q4_K_M | „Q4 K M” | Wariant kwantyzacji 4-bitowej w formacie GGUF; domyślny standard produkcyjny |
| GPTQ | „dżi-pi-ti-kju” | Algorytm kwantyzacji post-trainingowej INT4 z etapem kalibracji; wspiera obsługę LoRA w vLLM |
| AWQ | „ej-dubleju-kju” | Format kwantyzacji INT4 uwzględniający profil aktywacji; wykorzystuje kernele Marlin; najwyższa dokładność Pass@1 w INT4 |
| Kernele Marlin | „szybkie jądra INT4” | Zoptymalizowane jądra CUDA dla obliczeń INT4 na procesorach graficznych Hopper; zapewniają ok. 10-krotne przyspieszenie |
| FP8 | „ośmiobitowy float” | 8-bitowy format zmiennoprzecinkowy; bezpieczny standard dla układów Hopper/Ada/Blackwell |
| MXFP4 / NVFP4 | „czterobitowe mikroskalowanie” | 4-bitowe formaty zmiennoprzecinkowe z mikroskalowaniem (współczynniki skali przypisane do bloków wag) na architekturze Blackwell |
| Zbiór danych kalibracyjnych | „dane kalibracyjne” | Zbiór tekstów wejściowych używany przez algorytmy kwantyzacji do optymalizacji parametrów; musi odpowiadać domenie docelowej |
| Kwantyzacja cache KV | „KV INT8 / FP8” | Zmniejszenie precyzji zapisu pamięci podręcznej KV (niezależne od kwantyzacji wag); wpływa na dokładność obliczeń uwagi |

## Dalsze czytanie

- [VRLA Tech — LLM Quantization 2026](https://vrlatech.com/llm-quantization-explained-int4-int8-fp8-awq-and-gptq-in-2026/) — Wyniki testów porównawczych.
- [Jarvis Labs — Complete Guide to vLLM Quantization](https://jarvislabs.ai/blog/vllm-quantization-complete-guide-benchmarks) — Zestawienie przepustowości w zależności od formatu.
- [PremAI — GGUF vs AWQ vs GPTQ vs bitsandbytes 2026](https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/) — Szczegółowe porównanie formatów.
- [Dokumentacja vLLM — Quantization](https://docs.vllm.ai/en/latest/features/quantization/index.html) — Obsługiwane formaty oraz flagi konfiguracyjne.
- [Publikacja AWQ (arXiv:2306.00978)](https://arxiv.org/abs/2306.00978) — Oryginalna praca naukowa opisująca metodę AWQ.
- [Publikacja GPTQ (arXiv:2210.17323)](https://arxiv.org/abs/2210.17323) — Oryginalna praca naukowa opisująca metodę GPTQ.
