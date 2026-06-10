# Zdezagregowane wstępne wypełnianie/dekodowanie — NVIDIA Dynamo i llm-d

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Faza wstępnego wypełniania (prefill) jest ograniczona mocą obliczeniową procesora (compute-bound), podczas gdy faza dekodowania (decode) zależy od przepustowości pamięci (memory-bound). Uruchamianie obu tych procesów na tym samym układzie GPU prowadzi do marnowania zasobów. Dezagregacja (disaggregation) polega na rozdzieleniu ich na dedykowane pule maszyn i przesyłaniu pamięci podręcznej KV-cache za pośrednictwem sieci o wysokiej przepustowości (np. NVIDIA NIXL wykorzystującej RDMA/InfiniBand lub TCP jako fallback). Oprogramowanie NVIDIA Dynamo (zaprezentowane na GTC 2025, wersja 1.0 GA) działa jako warstwa orkiestracji ponad vLLM/SGLang/TRT-LLM. Jego moduły Planner Profiler oraz SLA Planner automatycznie dostosowują proporcje instancji prefill do decode, aby spełnić zdefiniowane cele SLO. Według oficjalnych danych NVIDIA (developer.nvidia.com, czerwiec 2025), rozwiązanie to pozwala na ~6-krotny wzrost przepustowości dla modelu DeepSeek-R1 MoE na platformie GB200 NVL72 z Dynamo w scenariuszach o średnim opóźnieniu. Z kolei strona produktowa Dynamo reklamuje przepustowość wyższą nawet do 50x dla modeli MoE na architekturze GB300 NVL72 z Dynamo w porównaniu z Hopperem. Wartość „30x” pojawiająca się w doniesieniach społecznościowych dotyczy kompletnego stosu Blackwell + Dynamo + DeepSeek-R1 i ma charakter szacunkowy. Projekt llm-d (tworzony przez Red Hat i AWS) to z kolei rozwiązanie natywne dla platformy Kubernetes: prefill, decode oraz router działają jako niezależne usługi z autorskim skalowaniem HPA dla każdej roli. Wersja llm-d 0.5 wprowadza hierarchiczne odciążanie KV-cache, routing LoRA uwzględniający stan pamięci podręcznej, sieć UCCL oraz skalowanie do zera (scale-to-zero). W ujęciu ekonomicznym, wdrożenie dezagregacji z Dynamo pozwala zaoszczędzić około 30–40% rocznego budżetu na inferencję (co przy wydatkach rzędu 2 mln USD rocznie daje oszczędności na poziomie 600–800 tys. USD) przy zachowaniu tego samego SLA. Krótkie zapytania wejściowe (<512 tokenów) generujące krótkie odpowiedzi nie uzasadniają kosztów sieciowych transferu KV-cache.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator porównujący architekturę kolokowaną i zdezagregowaną)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzna architektura vLLM), faza 17 · 08 (Metryki inferencji)
**Czas:** ~75 minut

## Cele naukowe

- Wyjaśnienie, dlaczego prefill (wstępne wypełnianie) i decode (dekodowanie) napotykają na inne wąskie gardła sprzętowe oraz oszacowanie strat wynikających z ich kolokacji na jednym GPU.
- Zrozumienie schematu architektury zdezagregowanej: pula prefill, pula decode, transfer KV-cache przez NIXL oraz rola routera.
- Identyfikacja warunków, w których dezagregacja jest nieopłacalna (krótkie prompty, krótkie odpowiedzi).
- Porównanie technologii NVIDIA Dynamo (warstwa orkiestracji infrastruktury) oraz llm-d (rozwiązanie natywne dla Kubernetes) pod kątem zastosowania w projektach.

## Problem

Uruchamiasz model Llama 3.3 70B na klastrze 8 procesorów H100. Przy ruchu mieszanym (długie prompty systemowe i krótkie odpowiedzi) układy GPU marnują potencjał podczas dekodowania, ponieważ ich moc obliczeniowa była zoptymalizowana pod kątem prefillu. Przy odwrotnej charakterystyce ruchu (krótkie pytania i długie odpowiedzi) dochodzi do sytuacji odwrotnej. Tradycyjna kolokacja prefillu i decode na tej samej maszynie zmusza do przewymiarowania (overprovisioning) zasobów dla obu faz.

Konsekwencje budżetowe: od 20% do 40% mocy obliczeniowej GPU marnuje się z powodu niedopasowania profilu zadania do architektury sprzętu. Płacisz za zaawansowane rdzenie obliczeniowe H100 przy operacji decode (ograniczonej pamięcią HBM) lub przepłacasz za pamięć HBM przy operacji prefill (ograniczonej mocą obliczeniową).

Rozwiązaniem jest dezagregacja: rozdzielenie zadań prefill i decode do osobnych pul maszyn o konfiguracji sprzętowej dopasowanej do ich wąskich gardeł, z jednoczesnym przesyłaniem danych KV-cache z puli prefill do decode za pomocą dedykowanych łączy sieciowych o wysokiej przepustowości.

## Koncepcja

### Charakterystyka wąskich gardeł (Prefill vs Decode)

- **Prefill (wstępne wypełnianie)**: polega na jednorazowym przetworzeniu całego promptu wejściowego przez sieć neuronową. Dominują tu operacje mnożenia macierzy (GEMM), co czyni ten proces zależnym od mocy obliczeniowej (compute-bound). Układ H100 oferuje w formacie FP8 wydajność rzędu ~2000 TFLOPS. Przetwarzanie wsadowe (batching) działa tu bardzo efektywnie.
- **Decode (dekodowanie)**: polega na sekwencyjnym generowaniu kolejnych tokenów (po jednym na krok), co wymaga odczytywania wszystkich wag modelu z pamięci przy każdym kroku. Proces ten jest ograniczony przepustowością pamięci (memory-bound). Pamięć HBM3 oferuje przepustowość na poziomie ~3 TB/s. Przetwarzanie wsadowe jest efektywne jedynie przy bardzo wysokim stopniu współbieżności, który pozwala zamortyzować koszt odczytu wag.

Kolokacja zmusza do zakupu uniwersalnych kart GPU. H100 sprawdza się w obu rolach, ale jest inwestycją kosztowną. W architekturze zdezagregowanej pulę prefill można oprzeć na kartach o potężnej mocy obliczeniowej (np. H100), natomiast pulę decode na kartach z większą ilością pamięci (np. H200) lub wdrożyć agresywną kwantyzację wag.

### Architektura systemu

```
            ┌──────────────┐
   Request → │    Router    │ ───────────────────────┐
            └──────┬───────┘                        │
                   │                                │
                   ▼ (prompt only)                  │
            ┌──────────────┐    KV cache    ┌───────▼──────┐
            │ Prefill pool │ ─── NIXL ────► │ Decode pool  │
            │  (compute)   │                │  (memory)    │
            └──────────────┘                └──────┬───────┘
                                                   │ tokens
                                                   ▼
                                                 Client
```

NIXL (NVIDIA Inter-Node Express Link) to dedykowany protokół transportu danych KV-cache między węzłami. Wykorzystuje technologię RDMA/InfiniBand, a w przypadku jej braku przełącza się na standardowy protokół TCP. Opóźnienie transferu sieciowego jest zauważalne – wynosi zazwyczaj od 20 do 80 ms dla KV-cache wygenerowanego z promptu o długości 4K tokenów dla modelu 70B w formacie FP8. Z tego powodu krótkie prompty wejściowe nie uzasadniają stosowania dezagregacji, gdyż czas potrzebny na transfer sieciowy przewyższa oszczędności na inferencji.

### NVIDIA Dynamo vs llm-d

**NVIDIA Dynamo** (premiera na GTC 2025, wersja 1.0 GA):
- Działa jako nadrzędny orkiestrator nad silnikami vLLM, SGLang oraz TRT-LLM.
- Komponent Planner Profiler na bieżąco analizuje obciążenie, a SLA Planner automatycznie dobiera odpowiednie proporcje puli prefill do decode.
- Rdzeń napisany w Rust z możliwością rozszerzania w języku Python.
- Wydajność: NVIDIA deklaruje 6-krotny wzrost przepustowości dla DeepSeek-R1 MoE na architekturze GB200 NVL72 z Dynamo przy średnich opóźnieniach (developer.nvidia.com, czerwiec 2025). Raportowane przez społeczność wyniki rzędu „30x” dla stosu Blackwell + Dynamo + DeepSeek-R1 mają charakter szacunkowy.
- GB300 NVL72 + Dynamo: do 50-krotnego wzrostu przepustowości dla modeli MoE w porównaniu do architektury Hopper (według strony produktowej NVIDIA Dynamo).

**llm-d** (projekt Red Hat i AWS, natywny dla Kubernetes):
- Fazy prefill i decode oraz router działają jako niezależne mikrousługi w klastrze Kubernetes.
- Niezależne skalowanie HPA dla każdej z ról na podstawie metryk takich jak długość kolejki zadań (dla prefill) oraz poziom użycia KV-cache (dla decode).
- Konfiguracja `topologyConstraint packDomain: rack` dba o to, by instancje prefill i decode były uruchamiane w obrębie tego samego racka (szafy serwerowej), co minimalizuje opóźnienia sieciowe przy transferze KV.
- Wersja llm-d 0.5 (2026): wprowadza hierarchiczne odciążanie (offloading) cache KV, routing LoRA uwzględniający lokalizację cache, obsługę sieci UCCL oraz mechanizm skalowania do zera (scale-to-zero).

Wybierz NVIDIA Dynamo, jeśli potrzebujesz gotowej, wydajnej warstwy orkiestracji integrującej się bezpośrednio z silnikami inferencyjnymi. Wybierz llm-d, jeśli Twoja infrastruktura opiera się w pełni na Kubernetes i chcesz zarządzać wdrożeniem za pomocą natywnych zasobów chmurowych CNCF.

### Analiza kosztów i zysków (ROI)

Szacunki oparte na agregacji danych wdrożeniowych u wielu klientów (rząd wielkości):

- Wyjściowy budżet: 2 000 000 USD rocznie na serwerach kolokowanych.
- Wdrożenie: przejście na architekturę zdezagregowaną z NVIDIA Dynamo.
- Efekt: identyczny wolumen ruchu, zachowanie dotychczasowego SLA dla opóźnień P99.
- Oszczędności: 600 000 – 800 000 USD rocznie (obniżenie kosztów o 30–40%) bez zakupu nowego sprzętu.

Wartości te stanowią uśredniony obraz rynkowy. Najbliższe oficjalne dane pochodzą z raportu Baseten (baseten.co, październik 2025): 2-krotne skrócenie czasu TTFT i o 61% wyższa przepustowość przy użyciu routingu Dynamo KV, a także analizy VAST + CoreWeave (vastdata.com, grudzień 2025): wzrost wydajności o 60–130% (tokeny/USD) przy współczynniku trafień cache KV na poziomie 40–60%. Największe korzyści odnoszą systemy przetwarzające długie dokumenty (np. RAG z prefiksami powyżej 8K tokenów).

### Kiedy DEZAGREGACJA SIĘ NIE OPŁACA

- Krótkie zapytania (<512 tokenów) i krótkie odpowiedzi (<200 tokenów) – czas transferu KV-cache przewyższa zyski z optymalizacji.
- Małe klastry sprzętowe (<4 układy GPU) – brak możliwości efektywnego wydzielenia pul maszyn.
- Brak kompetencji zespołu do zarządzania dwiema niezależnie skalowanymi pulami GPU.
- Brak infrastruktury sieciowej opartej na RDMA – narzut związany z transferem po TCP jest zbyt wysoki.

### Integracja z routerem zorientowanym na cache (Faza 17 · 11)

Routery w architekturze zdezagregowanej muszą być świadome lokalizacji KV-cache. Zapytanie powinno trafić bezpośrednio do węzła decode, który posiada już wygenerowany wcześniej prefiks. Jeśli nie ma dopasowania w cache, proces przechodzi przez pełną ścieżkę prefill → decode.

### Wydajność MoE na architekturze Blackwell

Połączenie architektury GB300 NVL72 z Dynamo pozwala osiągnąć do 50x wyższą przepustowość dla modeli MoE w porównaniu do generacji Hopper. Routing ekspertów w architekturach MoE obciąża moc obliczeniową w fazie prefill, ale stawia wysokie wymagania pamięciowe w fazie decode (ze względu na konieczność przechowywania wag wielu ekspertów). Dezagregacja rozwiązuje oba problemy jednocześnie. Jest to kluczowe przy wdrażaniu nowoczesnych modeli MoE, takich jak DeepSeek-V3 czy przyszłe warianty GPT-5.

### Kluczowe statystyki do zapamiętania

Benchmarki wydajnościowe ulegają częstym zmianom wraz z aktualizacjami oprogramowania. Zawsze weryfikuj je z aktualną dokumentacją przed podjęciem decyzji projektowych.

- DeepSeek-R1 na GB200 NVL72 + Dynamo: ~6-krotny wzrost przepustowości przy średnich opóźnieniach (developer.nvidia.com, czerwiec 2025).
- GB300 NVL72 + Dynamo: do 50x wyższa przepustowość MoE w stosunku do kart Hopper (developer.nvidia.com).
- Szacowane oszczędności: redukcja kosztów o 600 000 – 800 000 USD rocznie przy budżecie wyjściowym 2 000 000 USD, przy zachowaniu SLA.
- Warunki progowe dla dezagregacji: prompty wejściowe >512 tokenów oraz generowane odpowiedzi >200 tokenów.
- Czas transferu KV przez NIXL: 20–80 ms dla promptu 4K i modelu 70B FP8.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje działanie architektury kolokowanej oraz zdezagregowanej. Wyświetla dane o przepustowości, kosztach pojedynczego zapytania oraz punkcie rentowności w zależności od długości promptu.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-disaggregation-decider.md`. Narzędzie to analizuje charakterystykę ruchu i konfigurację klastra GPU, pomagając w podjęciu decyzji o wdrożeniu dezagregacji.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakiej długości promptu architektura zdezagregowana zaczyna przewyższać kolokowaną?
2. Zaprojektuj podział klastra na pulę prefill i pulę decode dla systemu RAG, w którym 99. percentyl (P99) długości prefiksu wynosi 8K tokenów, a generowane odpowiedzi mają średnio 300 tokenów.
3. NVIDIA Dynamo vs llm-d: które z tych rozwiązań wybierzesz dla infrastruktury opartej wyłącznie na Kubernetes, jeśli zespół nie chce wprowadzać dodatkowych zależności pythonowych?
4. Oblicz czas transferu cache KV: faza prefill dla promptu 4K i modelu 70B FP8 generuje ~500 MB danych KV-cache. Przy użyciu sieci RDMA o przepustowości 100 GB/s transfer zajmie 5 ms. Przy standardowym połączeniu TCP 10 GB/s potrwa to 50 ms. Jak te wartości wpływają na Twoje wymagania SLA?
5. Modele MoE (np. DeepSeek) zmieniają sposób aktywacji wag w zależności od tokena. Jak zachowuje się architektura zdezagregowana w przypadku modeli MoE, które dynamicznie aktywują różnych ekspertów?

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Zdezagregowane serwowanie | „rozdzielenie prefill/decode” | Wydzielenie osobnych pul procesorów GPU dedykowanych odpowiednio do wstępnego wypełniania i dekodowania |
| NIXL | „transport Dynamo” | Standard komunikacyjny NVIDIA do szybkiego przesyłania KV-cache między węzłami (RDMA/TCP) |
| NVIDIA Dynamo | „orkiestrator Dynamo” | Oprogramowanie zarządzające klastrem wnioskowania ponad silnikami vLLM/SGLang/TRT-LLM |
| llm-d | „Kube-disaggregation” | Otwarty projekt AWS/Red Hat do obsługi dezagregacji w Kubernetes |
| Planner Profiler | „profiler Dynamo” | Komponent Dynamo analizujący charakterystykę ruchu i konfigurujący proporcje pul GPU |
| SLA Planner | „zarządca opóźnień” | Moduł Dynamo optymalizujący rozkład zadań w celu zachowania zdefiniowanych limitów opóźnień (SLO) |
| `packDomain: rack` | „topologia racka” | Dyrektywa llm-d wymuszająca uruchamianie powiązanych podów w tej samej szafie serwerowej dla skrócenia czasu transferu KV |
| UCCL | „sieć UCCL” | Zoptymalizowana warstwa komunikacji sieciowej wprowadzona w llm-d 0.5 |
| Routing ekspertów MoE | „routing MoE” | Specyficzny dla modeli Mixture-of-Experts mechanizm dynamicznego ładowania wag ekspertów na poziomie pojedynczego tokena |

## Materiały uzupełniające

- [NVIDIA – Introducing Dynamo](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/)
- [NVIDIA – Deploying Disaggregated LLM Inference Workloads on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/)
- [TensorRT-LLM – Disaggregated Serving](https://nvidia.github.io/TensorRT-LLM/blogs/tech_blog/blog5_Disaggregated_Serving_in_TensorRT-LLM.html)
- [llm-d GitHub](https://github.com/llm-d/llm-d)
- [llm-d 0.5 Release Notes](https://github.com/llm-d/llm-d/releases)
