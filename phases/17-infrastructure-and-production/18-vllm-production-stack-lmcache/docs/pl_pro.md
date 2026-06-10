# Stos produkcyjny vLLM z odciążaniem LMCache KV

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Produkcyjny stos vLLM (vLLM Production Stack) to referencyjna architektura wdrożeniowa na Kubernetes, integrująca router, silniki wnioskowania oraz warstwę monitorowania (observability). LMCache to system odciążania KV-cache, który pozwala wyeksportować pamięć podręczną KV z pamięci GPU i wykorzystywać ją ponownie w kolejnych zapytaniach i między różnymi instancjami modeli (przechowując dane w pamięci DRAM procesora, a następnie na dysku lub w Ceph). Wprowadzony w wersji vLLM 0.11.0 (styczeń 2026 r.) konektor odciążający pamięć KV (KV offloading connector) realizuje ten proces asynchronicznie i pozwala na wpinanie niestandardowych backendów za pomocą API konektora (dostępnego od wersji 0.9.0+). Dzięki temu opóźnienia związane z transferem danych są ukrywane przed użytkownikiem końcowym. LMCache przynosi korzyści nawet bez współdzielenia prefiksów promptów – kiedy w pamięci GPU zaczyna brakować miejsca na bloki KV (cache pressure), wywłaszczone żądania (evicted requests) można przywrócić bezpośrednio z pamięci RAM procesora, zamiast ponownie wykonywać kosztowną fazę prefill. Oficjalne benchmarki na klastrze 16x H100 (80 GB HBM) pokazują, że w scenariuszach, gdzie wolumen pamięci podręcznej KV przekracza pojemność pamięci HBM, zarówno natywne odciążanie do pamięci procesora, jak i LMCache drastycznie zwiększają przepustowość systemu. Przy niskim obciążeniu pamięci KV narzut obu rozwiązań jest minimalny.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator wywłaszczania bloków KV)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzna architektura vLLM), faza 17 · 06 (SGLang/RadixAttention)
**Czas:** ~60 minut

## Cele naukowe

- Zrozumienie warstw produkcyjnego stosu vLLM: routera, silników wnioskowania, systemów odciążania KV-cache oraz monitorowania.
- Omówienie działania API konektora odciążającego KV (od wersji vLLM 0.9.0+) i sposobu, w jaki asynchroniczny zapis wprowadzony w wersji 0.11.0 maskuje opóźnienia transferu.
- Analiza przypadków użycia: kiedy LMCache (odciążanie do CPU-DRAM) poprawia wydajność (rozmiar cache KV > pojemność HBM), a kiedy generuje niepotrzebny narzut (cały cache KV mieści się w pamięci GPU HBM).
- Wybór pomiędzy natywnym mechanizmem CPU offloading w vLLM a zewnętrznym konektorem LMCache w zależności od specyfiki wdrożenia.

## Problem

Twoja usługa vLLM wyświetla procesory graficzne przy 100% HBM ze zdarzeniami wywłaszczania za każdym razem, gdy wzrasta współbieżność. Żądania są eksmitowane, umieszczane ponownie w kolejce, a Ty ponownie wypełniasz ten sam monit o token 2K cztery razy na minutę. Obliczenia GPU są wydawane na nadmiarowe wstępne wypełnienia; goodput jest znacznie niższy niż surowa przepustowość.

Dodanie większej liczby procesorów graficznych kosztuje liniowo. Dodanie większej ilości HBM nie jest możliwe. Ale procesor DRAM jest tani — jedno gniazdo ma ponad 512 GB przy opóźnieniach o rzędy wielkości gorszych niż HBM, ale w porządku dla „tymczasowo ciepłej” pamięci podręcznej KV.

LMCache wyodrębnia pamięć podręczną KV do pamięci DRAM procesora, dzięki czemu wywłaszczone żądania szybko są odzyskiwane, a powtarzające się prefiksy w różnych silnikach współdzielą pamięć podręczną bez ponownego napełniania każdego silnika.

## Koncepcja

### Produkcyjny stos vLLM (vLLM Production Stack)

Repozytorium `github.com/vllm-project/production-stack` zawiera referencyjną konfigurację dla Kubernetes:

- **Router**: inteligentny router świadomy istnienia cache (cache-aware router – omówiony w fazie 17 · 11), analizujący dystrybucję KV.
- **Silniki (Engines)**: instancje wykonawcze vLLM (worker pods) – zazwyczaj jedna na GPU lub na grupę TP/PP (Tensor Parallel / Pipeline Parallel).
- **Odciążanie KV-cache (KV Offloading)**: integracja z LMCache lub wbudowany, natywny konektor vLLM.
- **Monitorowanie (Observability)**: eksport metryk do Prometheus, wizualizacja w Grafana oraz śledzenie rozproszone OpenTelemetry (OTel).
- **Control Plane**: automatyczne wykrywanie usług (service discovery), dystrybucja konfiguracji oraz bezprzerwowe aktualizacje (rolling updates).

Całość jest dostarczana w postaci szablonów Helm Chart oraz dedykowanego operatora Kubernetes.

### API konektora odciążającego KV (KV Offloading Connector API - od vLLM 0.9.0+)

W wersji vLLM 0.9.0 wprowadzono ujednolicone API konektora dla wtyczek zewnętrznych systemów przechowywania KV-cache. Silnik wnioskowania eksportuje nieużywane bloki KV do konektora, który zapisuje je w zdefiniowanym backendzie (pamięć RAM hosta, dysk lokalny, chmura obiektowa S3 lub serwer LMCache). Gdy zapytanie ponownie potrzebuje tych danych, konektor ładuje je z powrotem do pamięci GPU.

Wersja vLLM 0.11.0 (styczeń 2026 r.) wprowadza w pełni asynchroniczną ścieżkę zapisu. Transfer KV-cache odbywa się w tle, dzięki czemu wątek główny silnika nie jest blokowany. Należy jednak pamiętać, że rzeczywisty wpływ na opóźnienia zależy od charakteru ruchu, współczynnika trafień w cache oraz obciążenia sieci. Twórcy vLLM wskazują w dokumentacji, że przy niskim współczynniku trafień (hit rate) narzut transferu może nieznacznie obniżyć ogólną przepustowość, a asynchroniczne odciążanie może wchodzić w konflikty z mechanizmami dekodowania spekulatywnego (speculative decoding).

### Natywne odciążanie do CPU (vLLM Native) vs LMCache

- **Natywne odciążanie w vLLM (Native Offloading)**: działa w obrębie pojedynczego hosta. Przechowuje bloki KV w pamięci RAM przypisanej do konkretnego kontenera z silnikiem. Jest proste w konfiguracji i nie generuje narzutu sieciowego, ale dane nie mogą być współdzielone z innymi instancjami vLLM.
- **Konektor LMCache**: działa w skali klastra. Zapisuje bloki na wydzielonym serwerze LMCache (łączącym pamięć DRAM maszyn z trwałą warstwą typu Ceph/S3). Zapisane bloki KV-cache są dostępne dla dowolnej instancji vLLM w klastrze.

Wybierz rozwiązanie natywne (vLLM Native), jeśli problem z brakiem HBM dotyczy pojedynczej, odizolowanej instancji modelu. Wybierz LMCache, jeśli w klastrze działa wiele replik modeli współdzielących te same prefiksy (np. duże bazy RAG, systemy typu multi-tenant ze wspólnymi szablonami promptów).

### Wyniki benchmarków (Klaster 16x H100 80GB)

Testy przeprowadzone na instancjach Google Cloud typu `a3-highgpu-4g`:

- **Niskie zapotrzebowanie na pamięć KV** (krótkie prompty, mała współbieżność): wydajność wszystkich konfiguracji jest zbliżona do linii bazowej, wdrożenie LMCache generuje jedynie ~3-5% stałego narzutu.
- **Średnie zapotrzebowanie**: LMCache zaczyna przynosić zyski dzięki współdzieleniu wygenerowanych prefiksów między różnymi instancjami modeli.
- **Wysokie zapotrzebowanie (rozmiar cache KV przekracza pojemność HBM)**: zarówno natywne odciążanie do RAM, jak i LMCache drastycznie poprawiają przepustowość systemu. LMCache wykazuje przewagę w scenariuszach wieloinstancyjnych.

### Kiedy LMCache jest kluczowy

- Systemy typu multi-tenant ze wspólnymi instrukcjami systemowymi dla różnych klientów.
- Aplikacje RAG, w których te same dokumenty są wielokrotnie przeszukiwane w różnych zapytaniach.
- Równoległe wdrażanie modeli z adapterami LoRA opartymi na tym samym modelu bazowym.
- Systemy poddane dużemu obciążeniu konkurencyjnemu (częste wywłaszczanie zadań – preemption).

### Kiedy NIE należy wdrażać LMCache

- Niskie zużycie pamięci HBM (brak zysków, płacisz narzut wydajnościowy).
- Praca na krótkich kontekstach (<1K tokenów) – transfer danych trwa dłużej niż ponowne wykonanie fazy prefill na GPU.
- Systemy z jednym klientem i brakiem powtarzalności zapytań.

### Integracja z architekturą zdezagregowaną (Prefill-Decode Disaggregation)

Połączenie zapytań i mechanizmów z fazy 17 · 17 oraz LMCache: nieużywany cache KV z puli prefill może być eksportowany bezpośrednio do LMCache. Przy kolejnych zapytaniach dane są pobierane bezpośrednio stamtąd. Router z fazy 17 · 11 decyduje o skierowaniu zadania do węzła, który posiada lokalne dane lub najszybszy dostęp do klastra LMCache.

### Kluczowe statystyki do zapamiętania

- Wdrożenie API konektora: od wersji vLLM 0.9.0.
- Asynchroniczne odciążanie (vLLM 0.11.0, styczeń 2026 r.): asynchroniczny transfer minimalizuje blokowanie wątku głównego, lecz ostateczny zysk zależy od specyfiki ruchu.
- Wydajność na 16x H100: LMCache przynosi korzyści przede wszystkim, gdy rozmiar pamięci podręcznej KV przekracza wolumen dostępnej pamięci HBM.
- Narzut przy braku optymalizacji: stałe ~3-5% straty na wydajności w scenariuszach z krótkimi kontekstami.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje obciążenie klastra vLLM wywołujące wywłaszczanie zadań (eviction) w wersjach z LMCache oraz bez niego. Raportuje współczynnik unikniętych operacji prefill, wzrost przepustowości oraz próg opłacalności w odniesieniu do zajętości pamięci HBM.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano szablon decyzyjny `outputs/skill-vllm-stack-decider.md`. Narzędzie to analizuje profil obciążenia i parametry wdrożenia vLLM, sugerując wybór natywnego odciążania, wdrożenie LMCache lub rezygnację z optymalizacji.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakim poziomie zajętości pamięci HBM wdrożenie LMCache staje się opłacalne?
2. Klient współdzieli prompt systemowy o rozmiarze 6K tokenów w ramach 200 zapytań na godzinę. Oblicz szacowane oszczędności mocy obliczeniowej dzięki zastosowaniu LMCache.
3. Centralny serwer LMCache stanowi pojedynczy punkt awarii (SPOF). Zaprojektuj architekturę wysokiej dostępności (HA) z replikacją i mechanizmem fallback do pamięci natywnej.
4. LMCache przechowuje dane na wolniejszej pamięci masowej (np. Ceph HDD). Porównaj czas odczytu 500 MB danych KV-cache (odpowiadających promptowi 4K dla modelu 70B FP8) z tym samym czasem ponownego przetworzenia tej fazy prefill bezpośrednio na procesorze GPU.
5. Przeanalizuj asynchroniczną ścieżkę zapisu we vLLM 0.11.0. Gdzie kryją się ukryte koszty i narzut wydajnościowy tej operacji?

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| vLLM Production Stack | „stos produkcyjny vLLM” | Dedykowane szablony Helm Chart i operator vLLM dla Kubernetes |
| Connector API | „API konektora KV” | Wtykowy interfejs wprowadzony we vLLM 0.9.0+ do integracji z zewnętrznym magazynem KV-cache |
| Native CPU Offloading | „lokalne odciążanie do RAM” | Zapisywanie nieużywanych bloków KV bezpośrednio w pamięci RAM hosta przypisanego do danej instancji |
| LMCache | „klastrowy cache KV” | Centralny serwer pamięci podręcznej KV-cache dla wielu instancji silnika, zapisujący dane w RAM i na dysku |
| Asynchroniczne odciążanie | „nieblokujący zapis” | Przesyłanie bloków KV-cache realizowane w tle, bez blokowania głównego wątku inferencji we vLLM 0.11.0 |
| Wywłaszczanie (Preemption) | „zwalnianie pamięci GPU” | Usuwanie bloków KV-cache z pamięci HBM karty w celu obsłużenia nowych zapytań przy braku miejsca |
| Ponowne użycie prefiksów | „współdzielony prefix” | Sytuacja, w której wiele zapytań zaczyna się od tych samych tokenów (np. instrukcji systemowych) |
| Warstwa Ceph/S3 | „trwały cache” | Trwała warstwa pamięci masowej w hierarchii cache, zapobiegająca utracie danych po przepełnieniu pamięci RAM |

## Materiały uzupełniające

- [vLLM Blog – KV Offloading Connector (styczeń 2026 r.)](https://blog.vllm.ai/2026/01/08/kv-offloading-connector.html)
- [vLLM Production Stack GitHub](https://github.com/vllm-project/production-stack) – szablony Helm i kod operatora Kubernetes.
- [LMCache for Enterprise-Scale LLM Inference (arXiv:2510.09665)](https://arxiv.org/html/2510.09665v2)
- [LMCache GitHub](https://github.com/LMCache/LMCache) – kod źródłowy konektora.
- [vLLM 0.11.0 Release Notes](https://github.com/vllm-project/vllm/releases) – szczegóły asynchronicznej ścieżki zapisu.
