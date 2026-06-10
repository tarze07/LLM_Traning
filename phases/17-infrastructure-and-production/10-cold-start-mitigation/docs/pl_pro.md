# Ograniczanie zimnego startu dla bezserwerowych LLM

> Uruchomienie obrazu modelu o rozmiarze 20 GB zajmuje od 5–10 minut (dla modelu 7B) do ponad 20 minut (dla 70B), zanim zacznie on obsługiwać zapytania. W rzeczywistych systemach bezserwerowych (serverless) nie jest to tylko faza rozgrzewania – to krytyczna przerwa w działaniu (downtime). Metody optymalizacji działają na pięciu poziomach (warstwach): wstępnie przygotowane obrazy węzłów (np. Bottlerocket na AWS z architekturą dwuwolumenową), przesyłanie strumieniowe wag modelu (NVIDIA Run:ai Model Streamer, natywnie wspierany w vLLM), migawki pamięci GPU (punkty kontrolne stanu pamięci, pozwalające na 10-krotnie szybsze uruchomienie), utrzymywanie ciepłych pul instancji (`min_workers=1`), wielopoziomowe ładowanie (potok ServerlessLLM: NVMe → DRAM → HBM, redukujący opóźnienia 10–200x) oraz migracja na żywo, która przesyła tokeny wejściowe (w kilobajtach), zamiast całej pamięci podręcznej KV (w gigabajtach). Platforma Modal podaje czas 2-4 sekund jako dolną granicę zimnego startu; Baseten domyślnie potrzebuje 5-10 sekund (poniżej sekundy przy zastosowaniu wstępnego podgrzewania). Z tej lekcji dowiesz się, jak mierzyć opóźnienia, planować budżet pamięci i efektywnie łączyć te pięć warstw optymalizacji.

**Typ:** Ucz się
**Języki:** Python (stdlib, uproszczona symulacja ścieżki zimnego startu)
**Wymagania wstępne:** Faza 17 · 02 (Ekonomia platformy wnioskowania), Faza 17 · 03 (Autoskalowanie GPU)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć warstw ograniczania skutków zimnego startu i wskaż jedno narzędzie lub wzorzec projektowy dla każdej z nich.
- Oblicz całkowity czas zimnego startu dla modelu 70B jako sumę czasów: (inicjalizacja węzła) + (pobranie wag) + (ładowanie wag do pamięci HBM) + (inicjalizacja silnika).
- Wyjaśnij, dlaczego migracja na żywo (live migration) przesyła tokeny wejściowe (kilobajty), a nie pamięć podręczną KV (gigabajty) oraz z jaką karą obliczeniową (ponowne wyliczenie) się to wiąże.
- Zdefiniuj kompromis związany z ciepłą pulą (koszt bezczynnego GPU vs akceptacja czasu zimnego startu) oraz określ próg umowy SLA, przy którym konfiguracja `min_workers > 0` staje się obowiązkowa.

## Problem

Twój bezserwerowy punkt końcowy (endpoint) LLM skaluje się do zera w nocy z powodu braku ruchu. O godzinie 8:00 następuje nagły gwałtowny wzrost liczby zapytań. Pierwsze zapytanie musi czekać, aż:

1. Narzędzie Karpenter przydzieli węzeł GPU: 45-60 s.
2. Pobrany zostanie obraz kontenera o rozmiarze 30 GB z wagami modelu: 120-300 s.
3. Silnik załaduje wagi do pamięci HBM: 45-120 s (w zależności od rozmiaru modelu i prędkości pamięci masowej).
4. Silnik vLLM lub TRT-LLM zainicjuje wykresy CUDA (CUDA graphs), pulę pamięci podręcznej KV oraz tokenizer: 10-30 s.

Łącznie: od 220 do 510 sekund (ok. 3–8 minut), zanim zostanie wygenerowany pierwszy token. Twoje SLA zakłada czas reakcji na poziomie 2 s. Wdrażasz ciepłą pulę (`min_workers=1`) i problem pozornie znika – jednak od teraz płacisz za utrzymanie bezczynnego procesora graficznego przez 24 godziny na dobę, 7 dni w tygodniu. Jeśli Twoja usługa obejmuje 5 produktów, z których każdy posiada jedną ciepłą replikę, generuje to koszt 5 × 24 × 30 = 3600 godzin pracy GPU w miesiącu, niezależnie od tego, czy ktokolwiek skorzystał z aplikacji.

Efektywne ograniczanie zimnego startu polega na zachowaniu zalet ekonomicznych modelu bezserwerowego przy jednoczesnym uniknięciu opóźnień związanych z ciągłym utrzymywaniem aktywnych maszyn (always-on).

## Koncepcja

### Warstwa 1 — Wstępnie zaszczepione obrazy węzłów (Bottlerocket)

W chmurze AWS architektura Bottlerocket z dwoma woluminami pozwala na oddzielenie systemu operacyjnego od woluminu danych. Możesz utworzyć migawkę (snapshot) woluminu danych z pobranym już obrazem kontenera, a następnie odwołać się do identyfikatora tej migawki w konfiguracji `EC2NodeClass`. Nowe węzły uruchamiają się z wagami zapisanymi bezpośrednio na lokalnym dysku NVMe – dzięki czemu krok 2 oraz część kroku 3 zostają wyeliminowane. Rozwiązanie to natywnie współpracuje z narzędziem Karpenter. Typowa oszczędność: skrócenie zimnego startu o 2-4 minuty dla dużych modeli.

Odpowiednik w GCP: niestandardowe obrazy maszyn wirtualnych z wstępnie pobranymi warstwami kontenerów. Na platformie Azure: migawki dysków zarządzanych (managed disks) realizujące ten sam schemat.

### Warstwa 2 — Przesyłanie strumieniowe wag modelu (Run:ai Model Streamer)

Zamiast ładować cały plik z wagami modelu przed przetworzeniem pierwszego zapytania, wagi są przesyłane strumieniowo do pamięci GPU warstwa po warstwie. Przetwarzanie rozpoczyna się natychmiast po załadowaniu pierwszego bloku transformera. Narzędzie NVIDIA Run:ai Model Streamer w wersjach z 2026 r. jest natywnie zintegrowane z vLLM. Współpracuje z magazynami AWS S3, Google GCS oraz lokalnymi dyskami NVMe. Skraca czas ładowania modelu o około połowę w przypadku dużych sieci, nakładając operacje we/wy (I/O) na proces inicjalizacji środowiska obliczeniowego.

### Warstwa 3 — Migawki pamięci GPU (Modal)

Platforma Modal wykonuje zrzut stanu pamięci GPU (wagi, wykresy CUDA, obszar pamięci podręcznej KV) po pierwszym załadowaniu modelu. Kolejne uruchomienia deserializują dane bezpośrednio do pamięci HBM, co jest 10-krotnie szybsze niż ponowna inicjalizacja od zera. Jest to rozwiązanie najbliższe koncepcji „uruchomienia ciepłego procesora graficznego w 2 sekundy”. Kompromis: migawki są ściśle powiązane z topologią GPU, więc jeśli Karpenter przydzieli Ci inną wersję (SKU) procesora graficznego, konieczne będzie ponowne wygenerowanie punktu kontrolnego.

### Warstwa 4 — Ciepłe pule (min_workers=1)

Najprostsza metoda: co najmniej jedna replika modelu jest stale utrzymywana w stanie gotowości. Kosztem jest stawka godzinowa za pracę procesora graficznego 24/7. Rachunek ekonomiczny bywa bezwzględny dla mniejszych modeli (płacisz 0,85–1,50 USD/h, aby uniknąć 30-sekundowego zimnego startu), ale uzasadniony dla dużych systemów (płacisz 4 USD/h, aby uniknąć 5-minutowego oczekiwania). Próg SLA, przy którym ciepłe pule stają się niezbędne: zazwyczaj gdy wymagane opóźnienie P99 TTFT wynosi < 60 s dla modeli klasy 70B+.

### Warstwa 5 — Ładowanie wielopoziomowe (ServerlessLLM)

Projekt ServerlessLLM organizuje pamięć masową w hierarchię: NVMe (pojemna, ale wolniejsza), DRAM (średnia pojemność i szybkość), HBM (szybka, ale o ograniczonej pojemności). Wagi modeli są wstępnie ładowane do pamięci systemowej DRAM, a w razie zapotrzebowania przesyłane bezpośrednio do HBM karty graficznej. Autorzy projektu wykazali 10–200-krotne skrócenie opóźnień zimnego startu w porównaniu do tradycyjnego odczytu z dysku do HBM. Rozwiązanie to jest na wczesnym etapie wdrażania produkcyjnego, lecz posiada już integrację z vLLM.

### Warstwa 6 — Migracja na żywo (Wzorzec dodatkowy)

W przypadku utraty węzła (np. eksmisja instancji spot, czyszczenie węzła) tradycyjny wzorzec zakładał zimny start nowej repliki i skierowanie do niej kolejki zapytań. Migracja na żywo polega na przesłaniu samych tokenów wejściowych (zaledwie kilka kilobajtów) do sprawnego węzła z załadowanym modelem i ponownym obliczeniu pamięci podręcznej KV na miejscu. Ponowne obliczenie (recomputation) jest znacznie szybsze i tańsze niż przesyłanie gigabajtów danych pamięci podręcznej KV przez sieć. Metoda ta ma zastosowanie w architekturach zdezagregowanych.

### Kalkulacja dla ciepłych pul

W systemach z rygorystyczną umową SLA (np. P99 TTFT <= 2 s) kluczowe pytanie nie brzmi „czy stosować ciepłe pule”, lecz „ile ciepłych replik utrzymywać i które ścieżki krytyczne nimi obsłużyć”.

- Krytyczne ścieżki interaktywne (czat na żywo, asystent głosowy): `min_workers = 1-2`.
- Przetwarzanie wsadowe w tle (np. nocna klasyfikacja danych): dopuszczalne skalowanie do zera, tolerowany zimny start na poziomie 5-10 minut.
- Warstwa Premium: gwarantowana wartość `min_workers` dedykowana dla konkretnego dzierżawcy (tenant).

### Pomiar przed optymalizacją

Struktura opóźnień zimnego startu dla modelu 70B na nowo utworzonym węźle (przykład):

| Faza | Czas | Metoda optymalizacji |
|-------|------|---------------|
| Inicjalizacja węzła | 50 s | Bottlerocket + wstępnie pobrany obraz, ciepła pula |
| Pobieranie obrazu | 180 s | Wstępnie zainstalowany obraz na woluminie danych (eliminacja kroku) |
| Wagi do HBM | 75 s | Model streamer (skrócenie o połowę); migawka GPU (eliminacja kroku) |
| Inicjalizacja silnika | 20 s | Trwały zapis (caching) wykresów CUDA |
| Pierwsza faza forward | 3 s | Minimalne nieuniknione opóźnienie modelu |
| **Całkowity czas (zimny start)** | **328 s** | |
| **Czas po optymalizacjach** | **~15 s** | 22-krotne skrócenie czasu |

### Liczby, które powinieneś zapamiętać

- Zimny start na platformie Modal: 2-4 s (dzięki migawkom GPU).
- Domyślny zimny start na Baseten: 5-10 s (poniżej sekundy przy włączonym wstępnym nagrzewaniu).
- Zimny start nieoptymalizowanego modelu 70B: 3-8 minut.
- Run:ai Model Streamer: ok. 2-krotne skrócenie czasu ładowania wag.
- ServerlessLLM: 10-200x szybsze ładowanie modeli (dane z publikacji naukowej).

## Użycie

Skrypt `code/main.py` symuluje proces zimnego startu w scenariuszu z zastosowaniem metod optymalizacji oraz bez nich. Oblicza całkowity czas oczekiwania, koszt utrzymywania ciepłych pul oraz punkt rentowności, powyżej którego stosowanie ciepłych pul staje się ekonomicznie uzasadnione.

## Efekt końcowy

W ramach tej lekcji powstaje dokument `outputs/skill-cold-start-planner.md`. Na podstawie wymagań SLA, rozmiaru modelu i profilu ruchu dobiera on odpowiednie techniki optymalizacji zimnego startu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Wyznacz punkt rentowności, powyżej którego utrzymanie ciepłej repliki jest tańsze niż ponoszenie kosztów kar umownych (SLA) wynikających z odrzucania zapytań podczas zimnego startu.
2. Wdrażasz model klasy 13B z wymaganiem SLA P99 TTFT <= 3 s. Zaproponuj minimalny zestaw metod optymalizacji (najmniejszą liczbę warstw), który pozwoli na osiągnięcie tego celu.
3. Wdrożenie technologii Bottlerocket eliminuje czas pobierania obrazu, lecz wagi modelu wciąż muszą zostać odczytane i przesłane do HBM. Oblicz czas tego procesu dla modelu 70B, zakładając prędkość odczytu z lokalnego NVMe na poziomie 7 GB/s.
4. Twój dostawca usług serverless oferuje funkcję migawek GPU (jak Modal), lecz zespół ds. bezpieczeństwa odmawia jej wdrożenia, twierdząc, że „migawki pamięci mogą prowadzić do wycieku danych osobowych (PII)”. Przedstaw argumenty obu stron: jakie jest realne ryzyko bezpieczeństwa i jak można je ograniczyć (np. efemeryczne migawki, szyfrowanie, izolacja przestrzeni nazw)?
5. Zaprojektuj wielopoziomową politykę ciepłych pul: określ liczbę ciepłych replik dla użytkowników premium (płatnych), użytkowników wersji próbnej oraz dla zadań uruchamianych w tle. Przedstaw kalkulację kosztów.

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Zimny start | „wielkie opóźnienie” | Czas upływający od wysłania zapytania do wygenerowania pierwszego tokena na nowo utworzonej replice |
| Ciepła pula | „minimalna liczba instancji” | Konfiguracja `min_workers >= 1` zapewniająca stałą gotowość co najmniej jednej repliki |
| Wstępnie zaszczepiony obraz | „gotowe AMI / obraz” | Obraz węzła z zapisanymi lokalnie wagami modelu i kontenerem |
| Bottlerocket | „system operacyjny od AWS” | Zoptymalizowany pod kątem kontenerów system operacyjny od AWS, wspierający migawki na poziomie woluminów danych |
| Model streamer | „ładowanie strumieniowe wag” | Nakładanie czasu odczytu wag z dysku na fazę inicjalizacji środowiska obliczeniowego |
| Migawka GPU | „zrzut pamięci do HBM” | Zapis stanu pamięci karty graficznej po załadowaniu modelu; pozwala na szybkie odtworzenie stanu przy restarcie |
| Ładowanie warstwowe | „hierarchia NVMe/DRAM/HBM” | Wykorzystanie warstwowej architektury pamięci do przyspieszenia ładowania modelu na żądanie |
| Migracja na żywo | „przekazanie tokenów” | Przesłanie samych tokenów wejściowych (KB) i ponowne wyliczenie stanu cache KV na nowym węźle |
| `min_workers` | „ciepłe repliki” | Minimalna liczba aktywnych instancji w architekturze bezserwerowej |
| Skalowanie do zera | „czysty serverless” | Brak opłat w okresie bezczynności; wiąże się z koniecznością poniesienia pełnego kosztu czasowego zimnego startu |

## Dalsze czytanie

- [Modal — Wydajność zimnego startu](https://modal.com/docs/guide/cold-start) — Oficjalne wyniki testów i architektura punktów kontrolnych pamięci Modal.
- [AWS Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) — Instrukcja konfiguracji wstępnie zaszczepionych woluminów danych.
- [NVIDIA Run:ai Model Streamer](https://github.com/run-ai/runai-model-streamer) — Narzędzie do równoległego ładowania wag podczas inicjalizacji środowiska.
- [Baseten — Optymalizacja zimnego startu](https://www.baseten.co/blog/cold-start-mitigation/) — Praktyczny przewodnik po metodach rozgrzewania instancji.
- [Publikacja ServerlessLLM (USENIX OSDI'24)](https://www.usenix.org/conference/osdi24/presentation/fu) — Opis wielopoziomowego potoku ładowania.
- [NVIDIA — Disaggregated LLM Inference on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — Szczegóły migracji na żywo w środowiskach zdezagregowanych.
