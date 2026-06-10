# Ograniczanie zimnego startu dla bezserwerowych LLM

> Obraz modelu o pojemności 20 GB potrzebuje od 5–10 minut (7B) do ponad 20 minut (70B), zanim zostanie udostępniony. W prawdziwym świecie bezserwerowym nie jest to rozgrzewka — to przerwa. Ograniczenia działają na pięciu warstwach: wstępnie zaszczepione obrazy węzłów (Bottlerocket na AWS, łuk z dwoma wolumenami), przesyłanie strumieniowe modeli (NVIDIA Run:ai Model Streamer, natywne w vLLM), migawki pamięci GPU (modalne punkty kontrolne, do 10x szybszy restart), ciepłe pule (`min_workers=1`), ładowanie warstwowe (ServerlessLLM NVMe → DRAM → HBM potok, redukcja opóźnień 10–200x) oraz migracja na żywo, która przenosi tokeny wejściowe (KB), a nie pamięć podręczną KV (GB). Modal publikuje 2-4 s zimne rozruchy jako podłogę; Domyślnie Baseten 5–10 s, poniżej sekundy z wstępnym nagrzewaniem. Ta lekcja uczy, jak mierzyć, budżetować i układać pięć warstw.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator ścieżki zimnego startu)
**Wymagania wstępne:** Faza 17 · 02 (Ekonomia platformy wnioskowania), Faza 17 · 03 (Autoskalowanie GPU)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć warstw łagodzenia zimnego startu i nazwij jedno narzędzie lub wzór w każdej warstwie.
- Oblicz całkowity czas zimnego rozruchu jako sumę (zaopatrzenie węzła) + (pobranie ciężarów) + (załadowanie ciężarów do HBM) + (inicjacja silnika) dla modelu 70B.
- Wyjaśnij, dlaczego migracja na żywo przenosi tokeny wejściowe (KB), a nie pamięć podręczną KV (GB) i jaka jest kara (ponowne obliczenie).
- Podaj kompromis w zakresie ciepłej puli (zapłać za bezczynny procesor graficzny lub zaakceptuj koniec zimnego startu) i próg umowy SLA, przy którym `min_workers > 0` staje się obowiązkowy.

## Problem

Twój bezserwerowy punkt końcowy LLM skaluje się do zera w ciągu nocy. O godzinie 8:00 nastąpił gwałtowny wzrost ruchu. Pierwsze żądanie czeka, aż:

1. Karpenter zapewnia węzeł GPU: 45-60s.
2. Kontener pobiera obraz o wielkości 30 GB i wadze: 120-300s.
3. Silnik ładuje ciężary do HBM: 45-120 s w zależności od rozmiaru modelu i prędkości przechowywania.
4. vLLM lub TRT-LLM inicjuje wykresy CUDA, pulę pamięci podręcznej KV, tokenizer: 10-30 s.

Łącznie: 220–510 s (około 3–8 minut), zanim ponownie pojawi się jeden token. Twoja umowa SLA wynosi 2 s. Wysyłasz ciepłą pulę (`min_workers=1`) i problem wydaje się znikać — ale teraz płacisz za jeden bezczynny procesor graficzny 24x7. Jeśli Twoja usługa obejmuje 5 produktów, każdy z jedną ciepłą repliką, oznacza to 5 × 24 × 30 = 3600 godzin GPU/miesiąc, niezależnie od tego, czy zadzwonił pojedynczy użytkownik, czy nie.

Ograniczanie zimnego startu polega na utrzymaniu ekonomii bezserwerowej przy jednoczesnym zmniejszeniu opóźnień związanych z zawsze włączonym.

## Koncepcja

### Warstwa 1 — wstępnie umieszczone obrazy węzłów (Bottlerocket)

W AWS architektura Bottlerocket z dwoma wolumenami oddziela system operacyjny od danych. Zrób migawkę woluminu danych z pobranym obrazem kontenera; odwołaj się do identyfikatora migawki w swoim `EC2NodeClass`. Nowe węzły uruchamiają się z ciężarami znajdującymi się już na lokalnym NVMe — kroki 2 i część 3 znikają. Natywnie współpracuje z Karpenterem. Typowe oszczędności: 2-4 minuty na zimny start w przypadku dużych modeli.

Odpowiednik w GCP: niestandardowe obrazy maszyn wirtualnych z wstępnie przygotowanymi warstwami kontenerów. Na platformie Azure: migawki dysków zarządzanych z tym samym wzorcem.

### Warstwa 2 — przesyłanie strumieniowe modelu (Run:ai Model Streamer)

Zamiast ładować pełny plik przed udzieleniem odpowiedzi na pierwsze żądanie, przesyłaj strumieniowo wagi do pamięci GPU warstwa po warstwie i rozpocznij przetwarzanie, gdy tylko pierwszy blok transformatora się pojawi. NVIDIA Run:ai Model Streamer jest dostarczany z natywną wersją vLLM 2026. Współpracuje z S3, GCS i lokalnym NVMe. Skraca czas ładowania obciążenia mniej więcej o połowę w przypadku dużych modeli, nakładając operacje we/wy na konfigurację obliczeniową.

### Warstwa 3 — migawki pamięci GPU (modalne)

Modal pobiera punkt kontrolny stanu GPU (wagi, wykresy CUDA, obszar pamięci podręcznej KV) po pierwszym załadowaniu. Kolejne restarty deserializują bezpośrednio do HBM — 10 razy szybciej niż ponowna inicjalizacja. Jest to najbardziej zbliżone do „uruchomienia ciepłego procesora graficznego w 2 sekundy”. Kompromis: migawki są zależne od topologii GPU, więc jeśli Karpenter przeniesie Cię do innej jednostki SKU, ponownie przejdziesz do punktu kontrolnego.

### Warstwa 4 — ciepłe baseny (min_workers=1)

Najprostsze rozwiązanie: jedna replika powinna być zawsze gotowa. Koszt to stawka godzinowa jednego procesora graficznego 24x7. Arytmetyka jest brutalna w przypadku małych modeli (płacisz $0.85-$1,50/h, aby uniknąć zimnego startu w ciągu 30 s) i życzliwa w przypadku dużych (płacisz 4 $/h, aby uniknąć 5-minutowego zimnego startu). Próg SLA, przy którym ciepłe baseny stają się obowiązkowe: zazwyczaj TTFT P99 < 60 s w modelu 70B+.

### Warstwa 5 — ładowanie warstwowe (ServerlessLLM)

ServerlessLLM traktuje pamięć masową jako hierarchię: NVMe (szybki, ale duży), DRAM (średni, ale wielowarstwowy), HBM (mały, ale natychmiastowy). Odważniki są wstępnie załadowane do pamięci DRAM; ładowanie na żądanie do HBM. W artykule podano 10–200-krotną redukcję opóźnień przy zimnym ładowaniu w porównaniu z naiwnym dyskiem do HBM. Wdrożenie produkcyjne jest wcześnie, ale istnieją integracje z vLLM.

### Warstwa 6 — migracja na żywo (wzór bonusowy)

Kiedy węzeł staje się niedostępny (wyrzucenie punktowe, opróżnienie węzła), tradycyjnym wzorcem jest zimny start innej repliki i opróżnienie kolejki żądań. Migracja na żywo przenosi tokeny wejściowe (kilobajty) do miejsca docelowego, w którym załadowany jest model, i ponownie oblicza pamięć podręczną KV w miejscu docelowym. Ponowne obliczenia są tańsze niż przesyłanie GB pamięci podręcznej KV przez sieć. Ma zastosowanie do zdezagregowanych wdrożeń.

### Matematyka dotycząca ciepłego basenu

W przypadku usługi z umową SLA P99 TTFT na czas 2 s pytanie nie brzmi „ciepły basen tak/nie”, ale „ile ciepłych replik i którymi ścieżkami je uzyskać”.

- Wartościowe ścieżki interaktywne (czat na żywo, agent głosowy): `min_workers=1-2`.
- Ścieżki wsadowe w tle (klasyfikacja nocna): akceptowana skala do zera, tolerowany 5-10 minut zimny start.
- Warstwa Premium: `min_workers` na dzierżawcę z dedykowaną pojemnością.

### Zmierz przed optymalizacją

Anatomia zimnego startu dla modelu 70B na świeżym węźle (ilustracja):

| Faza | Czas | Łagodzenie |
|-------|------|---------------|
| Zapewnienie węzła | lata 50. | Bottlerocket + wstępnie zaszczepiony obraz, ciepły basen |
| Pociągnięcie obrazu | lata 180-te | Wstępnie zaszczepiona ilość danych (wyeliminuj) |
| Wagi do HBM | lata 75. | Model streamera (połowa); Migawka GPU (wyeliminuj) |
| Uruchomienie silnika | lata 20. | Trwała pamięć podręczna wykresów CUDA |
| Pierwszy napastnik | 3s | Min. nieodłączne opóźnienie |
| **Całkowite zimno** | **328s** | |
| **Razem z uwzględnieniem łagodzeń** | **~15 lat** | 22x redukcja |

### Liczby, które powinieneś zapamiętać

- Modalny zimny start: 2-4 s (z migawkami GPU).
- Domyślny zimny start Baseten: 5-10 s; poniżej sekundy przy wstępnym podgrzewaniu.
- Zimny ​​start surowego 70B: 3-8 minut.
- Run:ai Model Streamer: ~2x przyspieszenie obciążenia.
- Warstwowe ładowanie bez serwera LLM: redukcja opóźnień 10-200x (liczba dokumentów).

## Użyj tego

`code/main.py` modeluje ścieżkę zimnego startu z każdymi środkami zaradczymi i bez nich. Podaje całkowity czas zimnego startu, koszt podgrzewania basenu i próg rentowności, powyżej którego ciepły basen się zwraca.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-cold-start-planner.md`. Biorąc pod uwagę umowę SLA, rozmiar modelu i kształt ruchu, wybiera, które środki zaradcze mają być stosowane.

## Ćwiczenia

1. Uruchom `code/main.py`. Oblicz próg rentowności, powyżej którego ciepła replika jest tańsza niż płacenie podatku zimnego rozruchu poprzez dodatkowe spadki żądań w SLO.
2. Wdrażasz model 13B z umową SLA P99 TTFT na 3 s. Wybierz minimalny stos łagodzący (najmniej warstw), który to osiąga.
3. Wstępne wysiewanie Bottlerocket eliminuje ściąganie obrazu, ale ciężary nadal są ładowane od migawki do HBM. Oblicz zegar ścienny dla modelu 70B, jeśli pamięć NVMe oparta na migawkach odczytuje prędkość 7 GB/s.
4. Twój dostawca usług bezserwerowych oferuje migawki GPU (modalne), a Twój zespół odmawia, ponieważ „migawki powodują wyciek informacji umożliwiających identyfikację”. Spierajcie się obie strony – jakie jest realistyczne ryzyko i jakie jest jego ograniczenie (efemeryczne migawki, szyfrowanie, izolacja przestrzeni nazw)?
5. Zaprojektuj wielopoziomową politykę ciepłej puli: ile ciepłych replik dla użytkowników płatnych, użytkowników próbnych i obciążeń wsadowych? Pokaż matematykę.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zimny ​​start | „wielka pauza” | Czas od żądania do pierwszego tokena na świeżej replice |
| Ciepły basen | „zawsze włączone minimum” | `min_workers >= 1`, aby przynajmniej jedna replika była gotowa |
| Wstępnie zaszczepiony obraz | „pieczone AMI” | Obraz węzła z wstępnie rezydentnymi wagami kontenerów |
| Rakieta butelkowa | „System operacyjny węzła AWS” | System operacyjny zoptymalizowany pod kątem kontenera AWS z obsługą migawek na dwóch woluminach |
| Model streamera | „obciążenie strumieniowe” | Nakładanie się wag we/wy z konfiguracją obliczeń |
| Migawka GPU | „punkt kontrolny do HBM” | Serializuj stan procesora graficznego po załadowaniu; deserializować przy ponownym uruchomieniu |
| Ładowanie warstwowe | „NVMe + DRAM + HBM” | Hierarchia poziomów przechowywania; ładunek na żądanie |
| Migracja na żywo | "przesuń żetony" | Przesyłanie danych wejściowych (KB), ponowne obliczenie KV w miejscu docelowym |
| `min_workers` | „ciepłe repliki” | Minimalna liczba podtrzymania bez serwera |
| Skala do zera | „pełny bezserwerowy” | Brak kosztów w stanie bezczynności; zaakceptować pełny podatek od zimnego startu |

## Dalsze czytanie

- [Modal — Wydajność zimnego startu] (https://modal.com/docs/guide/cold-start) — opublikowane testy porównawcze Modal i architektura punktów kontrolnych.
- [AWS Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) — wzór migawki woluminu danych wstępnie zaszczepiony.
- [NVIDIA Run:ai Model Streamer](https://github.com/run-ai/runai-model-streamer) — ładowanie nakładających się ciężarów podczas konfiguracji obliczeń.
- [Baseten — łagodzenie skutków zimnego rozruchu](https://www.baseten.co/blog/cold-start-mitigation/) — podręcznik dotyczący przygotowania do rozgrzania.
- [Dokument ServerlessLLM (USENIX OSDI'24)](https://www.usenix.org/conference/osdi24/presentation/fu) — wielopoziomowy projekt ładowania.
— [NVIDIA — Disaggregated LLM Inference on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — migracja na żywo dla zdezagregowanych wdrożeń.