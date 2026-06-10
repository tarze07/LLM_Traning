# Stos produkcyjny vLLM z odciążaniem LMCache KV

> Stos produkcyjny vLLM to referencyjne wdrożenie Kubernetes — router, silniki i obserwowalność połączone ze sobą. LMCache to warstwa odciążająca KV, która wyodrębnia pamięć podręczną KV z pamięci GPU i wykorzystuje ją ponownie w zapytaniach i silnikach (DRAM procesora, następnie dysk/Ceph). Złącze odciążające vLLM 0.11.0 KV (styczeń 2026 r.) sprawia, że ​​jest to asynchroniczne i można je podłączyć za pośrednictwem interfejsu API złącza (wersja 0.9.0+). Opóźnienie odciążania nie jest widoczne dla użytkownika. LMCache jest cenny nawet bez współdzielonych prefiksów — gdy w GPU zabraknie slotów KV, wywłaszczone żądania można przywrócić z procesora zamiast ponownie obliczać wstępne wypełnienie. Opublikowane testy porównawcze na 16x H100 (80 GB HBM) na 4 a3-highgpu-4g: gdy pamięć podręczna KV przekracza HBM, zarówno natywne obciążenie procesora, jak i pamięć LMCache znacznie poprawiają przepustowość; przy niskim zużyciu KV wszystkie konfiguracje odpowiadają wartościom bazowym przy niewielkim narzucie.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator wycieku KV)
**Wymagania wstępne:** Faza 17 · 04 (wewnętrzne urządzenia obsługujące vLLM), faza 17 · 06 (SGLang/RadixAttention)
**Czas:** ~60 minut

## Cele nauczania

- Diagram warstw stosu produkcyjnego vLLM: router, silniki, obciążenie KV, obserwowalność.
— Wyjaśnij interfejs API łącznika odciążającego KV (wersja 0.9.0+) i sposób, w jaki ścieżka asynchroniczna w wersji 0.11.0 ukrywa opóźnienia w odciążaniu.
- Określ ilościowo, kiedy LMCache CPU-DRAM pomaga (KV > HBM), a kiedy zwiększa obciążenie (KV jest wystarczająco małe, aby zmieścić się w HBM).
— Wybierz pomiędzy natywnym odciążaniem procesora vLLM a złączem LMCache, biorąc pod uwagę ograniczenia wdrożenia.

## Problem

Twoja usługa vLLM wyświetla procesory graficzne przy 100% HBM ze zdarzeniami wywłaszczania za każdym razem, gdy wzrasta współbieżność. Żądania są eksmitowane, umieszczane ponownie w kolejce, a Ty ponownie wypełniasz ten sam monit o token 2K cztery razy na minutę. Obliczenia GPU są wydawane na nadmiarowe wstępne wypełnienia; goodput jest znacznie niższy niż surowa przepustowość.

Dodanie większej liczby procesorów graficznych kosztuje liniowo. Dodanie większej ilości HBM nie jest możliwe. Ale procesor DRAM jest tani — jedno gniazdo ma ponad 512 GB przy opóźnieniach o rzędy wielkości gorszych niż HBM, ale w porządku dla „tymczasowo ciepłej” pamięci podręcznej KV.

LMCache wyodrębnia pamięć podręczną KV do pamięci DRAM procesora, dzięki czemu wywłaszczone żądania szybko są odzyskiwane, a powtarzające się prefiksy w różnych silnikach współdzielą pamięć podręczną bez ponownego napełniania każdego silnika.

## Koncepcja

### Stos produkcyjny vLLM

`github.com/vllm-project/production-stack` to referencyjne wdrożenie Kubernetes:

- **Router** — obsługujący pamięć podręczną (faza 17 · 11). Zużywa zdarzenia KV.
- **Silniki** — pracownicy vLLM. Jeden na procesor graficzny lub na grupę TP/PP.
- **Odciążenie pamięci podręcznej KV** — wdrożenie LMCache lub natywny łącznik.
- **Obserwowalność** — zeskrobanie Prometheusa, pulpity nawigacyjne Grafana, ślady Otel.
- **Płaszczyzna kontroli** — wykrywanie usług, konfiguracja, aktualizacje ciągłe.

Dostarczane jako mapa steru + operator.

### Interfejs API złącza odciążającego KV (wersja 0.9.0+)

W wersji vLLM 0.9.0 wprowadzono interfejs API złącza dla podłączanych backendów pamięci podręcznej KV. Twój silnik przeładowuje bloki do złącza; złącze przechowuje je (RAM, dysk, pamięć obiektowa, LMCache). Żądanie wymaga bloku, łącznik ładuje go z powrotem.

Wersja vLLM 0.11.0 (styczeń 2026 r.) dodaje asynchroniczną ścieżkę odciążania — odciążanie może odbywać się w tle, więc w typowym przypadku silnik nie blokuje jej. Kompleksowe opóźnienia i przepustowość nadal zależą od kształtu obciążenia, współczynnika trafień w pamięci podręcznej KV i ciśnienia w systemie; Z własnych notatek vLLM wynika, że ​​niestandardowe odciążanie jądra może obniżyć przepustowość przy niskim współczynniku trafień oraz że w przypadku planowania asynchronicznego występują znane problemy z interakcją z dekodowaniem spekulatywnym.

### Natywne obciążenie procesora a LMCache

**Natywne odciążenie procesora vLLM**: lokalne dla silnika. Przechowuje bloki KV w pamięci RAM hosta. Szybkie wdrożenie, zero przeskoków w sieci. Nie krzyżuje się z silnikami.

**Złącze LMCache**: skala klastra. Przechowuje bloki na współdzielonym serwerze LMCache (CPU DRAM + warstwa Ceph/S3). Bloki są dostępne dla każdego silnika. Opublikowano 16 testów porównawczych H100.

Wybierz natywny, gdy pojedynczy silnik ma ciśnienie HBM. Wybierz LMCache, gdy wiele silników ma wspólne prefiksy (RAG ze wspólnymi monitami systemowymi, wielu dzierżawców ze udostępnionymi szablonami).

### Zachowanie wzorcowe

16x H100 (80 GB HBM) rozłożony na 4 testy a3-highgpu-4g:

- Niski rozmiar KV (krótkie podpowiedzi, niska współbieżność): wszystkie konfiguracje są zgodne z wartościami bazowymi, LMCache dodaje ~3-5% narzutu.
- Umiarkowany zasięg: LMCache zaczyna pomagać w ponownym użyciu prefiksów w różnych silnikach.
- KV przewyższa HBM: zarówno natywne obciążenie procesora, jak i LMCache znacznie poprawiają przepustowość; LMCache większy zysk dzięki współużytkowaniu między silnikami.

### Kiedy LMCache ma decydujące znaczenie

- Obsługa wielu dzierżawców, w przypadku której monity systemowe są współużytkowane przez dzierżawców.
- RAG, w którym fragmenty dokumentu powtarzają się w zapytaniach.
- Dopracowane warianty (LoRA) oparte na tej samej podstawie, w których ponowne wykorzystanie podstawowego modelu KV ogranicza zbędną pracę.
- Obciążenia wymagające dużego wywłaszczania: przywracanie z procesora tańsze niż ponowne wstępne wypełnianie.

### Kiedy NIE włączać

- Małe obciążenie HBM — płacisz koszty ogólne bez korzyści.
- Krótkie konteksty (<1 tys. tokenów) — czas transferu > ponowne wypełnienie.
— Obciążenie pracą z jednym monitem dla jednego dzierżawcy — bez konieczności ponownego użycia do przechwytywania.

### Integracja z udostępnianiem zdezagregowanym

Faza 17 · 17 zdezagregowanych porcji + związki LMCache: Transfery KV z puli wstępnej do dekodowania obszaru puli w LMCache, jeśli nie są używane; kolejne zapytania pobierane są z LMCache. Router obsługujący pamięć podręczną fazy 17 · 11 może kierować do silnika, którego lokalna pamięć podręczna współdzielona LUB LMCache pasuje.

### Liczby, które powinieneś zapamiętać

— vLLM 0.9.0: Dostarczono interfejs API oprogramowania sprzęgającego.
- vLLM 0.11.0 (styczeń 2026): asynchroniczna ścieżka odciążania; całkowity wpływ opóźnień zależy od obciążenia, współczynnika trafień KV i ciśnienia w systemie (nie jest to absolutna gwarancja).
- 16x test porównawczy H100: LMCache pomaga, gdy ślad KV przekracza HBM.
- Małe ciśnienie HBM: 3-5% narzutu bez korzyści.

## Użyj tego

`code/main.py` symuluje obciążenie wymagające wywłaszczania z i bez LMCache. Raportuje uniknięcie ponownego napełniania, wzrost przepustowości i wykorzystanie HBM na poziomie progu rentowności.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-vllm-stack-decider.md`. Biorąc pod uwagę kształt obciążenia i wdrożenie vLLM, decyduje się na natywny, LMCache czy żaden z nich.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakim wykorzystaniu HBM zaczyna płacić LMCache?
2. Dzierżawca udostępnia monit systemowy o wartości 6 tys. tokenów w ramach 200 zapytań na godzinę. Oblicz oczekiwane oszczędności LMCache na dzierżawcę.
3. Serwer LMCache jest pojedynczym punktem awarii. Zaprojektuj strategię HA (repliki, powrót do wersji natywnej).
4. LMCache przechowuje dane w Ceph na wirującym dysku. Jaki jest czas odczytu w przypadku tokena 4K KV przy 70B FP8 (500 MB) w porównaniu z ponownym wypełnieniem?
5. Przedyskutuj, czy ścieżka asynchroniczna vLLM 0.11.0 jest „wolna” – gdzie kryje się narzut?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Stos produkcyjny | „wdrożenie referencyjne” | Wykres vLLM Kubernetes Helm + operator |
| Interfejs API łącznika | „Interfejs zaplecza KV” | vLLM 0.9.0+ wtykowy interfejs magazynu KV |
| Natywne obciążenie procesora | „wyciek lokalny z silnika” | Przechowuj KV w pamięci RAM hosta tego samego silnika |
| Pamięć LMC | „pamięć podręczna klastra KV” | Międzysilnikowy serwer pamięci podręcznej KV na procesorze DRAM + dysk |
| 0.11.0 asynchroniczny | „odciążenie nieblokujące” | Odciążenie ukryte za strumieniem silnika |
| Wywłaszczenie | „eksmituj, żeby zrobić miejsce” | Tasowanie pamięci podręcznej KV, gdy HBM jest pełny |
| Ponowne użycie prefiksu | „ten sam monit systemowy” | Wiele zapytań ma wspólny początek; trafienie w pamięć podręczną |
| Poziom Cepha | „poziom dysku” | Trwała pamięć podręczna poniżej pamięci DRAM w hierarchii pamięci podręcznej |

## Dalsze czytanie

– [Blog vLLM — złącze odciążające KV (styczeń 2026 r.)](https://blog.vllm.ai/2026/01/08/kv-offloading-connector.html)
- [vLLM Production Stack GitHub](https://github.com/vllm-project/production-stack) — Wykres Helm + operator.
— [LMCache do wnioskowania LLM na skalę korporacyjną (arXiv:2510.09665)](https://arxiv.org/html/2510.09665v2)
- [LMCache GitHub](https://github.com/LMCache/LMCache) — Implementacja konektora.
- [Informacje o wydaniu vLLM 0.11.0](https://github.com/vllm-project/vllm/releases) — szczegóły ścieżki asynchronicznej.