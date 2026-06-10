# vLLM od wewnątrz: PagedAttention, ciągłe przetwarzanie wsadowe, dzielenie fazy prefill na fragmenty (chunked prefill)

> Dominacja vLLM w 2026 roku opiera się na trzech połączonych ze sobą mechanizmach, a nie na pojedynczej optymalizacji. PagedAttention jest włączone domyślnie. Ciągłe przetwarzanie wsadowe (continuous batching) dynamicznie wprowadza nowe żądania do aktywnego wsadu (batch) między kolejnymi iteracjami generowania tokenów. Dzielenie fazy prefill na fragmenty (chunked prefill) zapobiega blokowaniu tokenów generowanych w fazie decode przez długie prompty wejściowe. Po włączeniu wszystkich trzech funkcji model Llama 3.3 70B FP8 na jednym układzie H100 SXM5 osiąga wydajność na poziomie 2200–2400 tokenów na sekundę przy 128 współbieżnych zapytaniach – to o ok. 25% więcej niż domyślna konfiguracja vLLM i 3-4 razy szybciej niż w przypadku naiwnej pętli PyTorch. W tej lekcji analizujemy działanie harmonogramu (scheduler) oraz jądra operacji Attention na poziomie szczegółowości pozwalającym na samodzielne rozrysowanie ich schematu. Część praktyczna w pliku `code/main.py` zawiera prosty symulator ciągłego przetwarzania wsadowego, który planuje fazy prefill i decode w sposób zbliżony do rzeczywistego vLLM.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, prosty symulator harmonogramu ciągłego przetwarzania wsadowego)
**Wymagania wstępne:** Faza 17 · 01 (Udostępnianie modelu), Faza 11 (Inżynieria LLM)
**Czas:** ~75 minut

## Cele nauczania

- Zrozumienie mechanizmu PagedAttention jako wirtualnego alokatora pamięci podręcznej KV Cache: rola bloków logicznych i fizycznych oraz tabel bloków (block tables), a także wyjaśnienie, dlaczego fragmentacja pamięci w warunkach produkcyjnych utrzymuje się poniżej 4%.
- Rozrysowanie schematu ciągłego przetwarzania wsadowego (continuous batching) na poziomie iteracji: sposób, w jaki zakończone sekwencje opuszczają wsad, a nowe są do niego dołączane bez przerywania pracy GPU.
- Definicja chunked prefill i określenie, którą metrykę opóźnienia chroni ten mechanizm (wskazówka: chodzi o percentyle opóźnienia pierwszego tokena TTFT w rozkładzie długoogonowym, a nie o średnią przepustowość).
- Analiza problemu w wersji vLLM v0.18.0, który sprawia trudności zespołom próbującym wdrożyć wszystkie te optymalizacje jednocześnie.

## Problem

Naiwna pętla serwowania modelu w PyTorch przetwarza jedno żądanie na raz: tokenizacja, faza prefill, faza decode do momentu napotkania tokena EOS lub limitu długości, po czym następuje zwrot wyniku. Dla jednego użytkownika takie rozwiązanie działa bez zarzutu, jednak przy stu użytkownikach tworzy się długa kolejka. Oczywiste usprawnienie – przetwarzanie wsadowe o stałym rozmiarze (static batching) – wymusza dopasowanie każdego żądania w paczce do najdłuższego promptu wejściowego oraz do najdłuższego oczekiwanego wyniku, co wstrzymuje całą grupę zapytań do momentu zakończenia najwolniejszej generacji. W efekcie płaci się za niepotrzebne wypełnienie (padding), a krótkie zapytania czekają na ukończenie tych długich.

vLLM rozwiązuje te trzy problemy jednocześnie. PagedAttention zapobiega fragmentacji pamięci podręcznej KV Cache, która przy klasycznej ciągłej alokacji pamięci (contiguous allocation) potrafi pochłonąć od 60 do 80% pamięci GPU. Ciągłe przetwarzanie wsadowe umożliwia dodawanie i usuwanie zapytań z paczki (batch) pomiędzy poszczególnymi krokami generowania kolejnych tokenów (iteracjami dekodowania), dzięki czemu zasoby GPU są stale wysycone pracą. Z kolei chunked prefill dzieli długie prompty wejściowe (np. o długości 32k tokenów) na mniejsze fragmenty (np. po 512 tokenów) i przeplata ich przetwarzanie z generowaniem tokenów dla innych zapytań, dzięki czemu przetwarzanie długiego tekstu wejściowego nie blokuje generacji u pozostałych użytkowników.

W warunkach produkcyjnych w 2026 roku standardem jest włączenie wszystkich trzech opcji. Konieczne jest zrozumienie specyfiki każdego z tych mechanizmów, ponieważ najczęstsze błędy i awarie leżą po stronie harmonogramu zapytań (schedulera), a nie samego modelu.

## Koncepcja

### PagedAttention jako system pamięci wirtualnej

Rozmiar pamięci KV Cache na jedną sekwencję wyraża się wzorem: `num_layers × 2 × num_heads × head_dim × seq_len × bytes_per_element`. Dla modelu Llama 3.3 70B przy oknie 8192 tokenów wymaga to około 1,25 GB pamięci na sekwencję w formacie BF16. Jeśli zarezerwujemy statycznie 8192 sloty na każde żądanie, podczas gdy średnie zapytanie zużywa jedynie 1500 tokenów, zmarnujemy ok. 82% przydzielonej pamięci HBM (High Bandwidth Memory). Klasyczne przetwarzanie wsadowe generuje ogromne straty pamięci.

PagedAttention czerpie z rozwiązań stosowanych w pamięci wirtualnej systemów operacyjnych. Pamięć podręczna KV Cache nie jest alokowana jako spójny, ciągły obszar dla sekwencji. Zamiast tego dzieli się ją na bloki o stałym rozmiarze (domyślnie 16 tokenów). Każda sekwencja posiada tabelę bloków (block table), która mapuje pozycje tokenów logicznych na identyfikatory fizycznych bloków w pamięci GPU. Gdy sekwencja przekracza rozmiar aktualnie przydzielonych zasobów, alokowany jest kolejny blok, a po zakończeniu przetwarzania bloki są zwracane do wspólnej puli.

Dzięki temu fragmentacja pamięci spada z 60–80% do poziomu poniżej 4%. PagedAttention jest integralną częścią vLLM i nie wymaga dodatkowej aktywacji. Głównym parametrem konfiguracyjnym jest `--gpu-memory-utilization` (domyślnie 0.9), który określa, jaki odsetek pamięci HBM po załadowaniu wag modelu i aktywacji ma zostać przeznaczony na bloki KV Cache.

### Ciągłe przetwarzanie wsadowe na poziomie iteracji

Tradycyjne dynamiczne przetwarzanie wsadowe (dynamic batching) grupowało zapytania w określonym oknie czasowym (np. 10 ms), a następnie uruchamiało fazy prefill oraz decode, przetwarzając je współbieżnie do momentu zakończenia wszystkich sekwencji w paczce. Szybkie zapytania, które zakończyły generację wcześniej, pozostawały bezczynne do czasu, aż GPU przetworzy najdłuższe zadania.

Ciągłe przetwarzanie wsadowe (continuous batching) podejmuje decyzje o alokacji przed każdym krokiem generowania tokenów. W każdej iteracji harmonogram realizuje następujące kroki dla listy aktywnych sekwencji `RUNNING`:

1. Sekwencje, które wygenerowały token EOS lub osiągnęły limit `max_tokens`, są usuwane z listy `RUNNING`.
2. Harmonogram sprawdza kolejkę zapytań oczekujących (`WAITING`). Jeśli dostępne są wolne bloki KV Cache, dodaje nowe zadania (faza prefill lub wznowienie wstrzymanego dekodowania).
3. Wykonywany jest krok propagacji w przód (forward pass) na całej grupie `RUNNING`, generując po jednym tokenie dla każdej sekwencji.

Rozmiar aktywnej paczki (batch) dynamicznie zmienia się w czasie. Zapytania na różnym etapie generowania są łączone w jedno wspólne wywołanie GPU. W architekturze vLLM z 2026 roku odpowiada za to harmonogram `V1 scheduler`. Kluczowa zasada: harmonogram podejmuje decyzje raz na każdą iterację generowania tokenów, a nie raz na całe zapytanie.

### Chunked prefill w obronie percentyli TTFT

Faza prefill jest operacją silnie obciążającą jednostki obliczeniowe GPU. Przetworzenie promptu o długości 32k tokenów dla modelu Llama 3.3 70B wymaga ok. 800 ms ciągłej pracy jednego układu H100. W tym czasie wszystkie aktywne generacje (faza decode) dla innych użytkowników są wstrzymywane. W tradycyjnych pętlach obsługi długa faza prefill jednego zapytania dramatycznie zwiększa opóźnienie między tokenami (Inter-Token Latency - ITL) u dziesiątek pozostałych użytkowników.

Mechanizm chunked prefill dzieli fazę przetwarzania promptu wejściowego na mniejsze części o stałym rozmiarze (domyślnie 512 tokenów) i planuje każdą z nich jako osobną jednostkę obliczeniową. Pomiędzy przetwarzaniem kolejnych fragmentów harmonogram może wstawić wygenerowanie tokenów (decode) dla innych aktywnych zapytań. W ten sposób minimalne wydłużenie czasu prefill pojedynczego żądania (kilka milisekund na fragment) drastycznie zmniejsza wahania i skrajne opóźnienia w generowaniu odpowiedzi u pozostałych użytkowników. Wskaźnik P99 ITL przy mieszanym ruchu spada w testach porównawczych z ok. 50 ms do ok. 15 ms.

### Synergia optymalizacji

Wszystkie trzy mechanizmy ściśle ze sobą współpracują. PagedAttention dostarcza harmonogramowi elastyczne zasoby pamięci KV, którymi można zarządzać. Ciągłe przetwarzanie wsadowe wymaga precyzyjnej alokacji, aby dołączanie nowych zapytań nie wymuszało ponownego układania danych w pamięci. Z kolei chunked prefill jest bezpośrednio obsługiwany przez harmonogram w ramach jednej, wspólnej listy zadań `RUNNING`.

Głównym zadaniem harmonogramu jest maksymalizacja przepustowości w ramach dostępnego limitu bloków KV Cache przy jednoczesnym uwzględnieniu dzielenia fazy prefill na fragmenty.

### Problem kompatybilności w wersji v0.18.0

W wersji vLLM v0.18.0 nie jest możliwe jednoczesne włączenie flagi `--enable-chunked-prefill` oraz stosowanie spekulatywnego dekodowania z zewnętrznym modelem pomocniczym (`--speculative-model`). Wyjątkiem udokumentowanym w harmonogramie V1 jest jedynie spekulatywne dekodowanie z użyciem wewnętrznego mechanizmu N-gram na GPU. Zespoły, które włączają wszystkie flagi optymalizacyjne jednocześnie bez analizy dokumentacji wydania (release notes), napotkają krytyczny błąd wykonania (runtime error) przy starcie usługi. Jeśli zyski z wdrożenia spekulatywnego dekodowania przewyższają korzyści z chunked prefill, należy dokonać wyboru – w 2026 roku optymalnym rozwiązaniem jest często wdrożenie EAGLE-3 bez mechanizmu chunked prefill, zamiast próby łączenia niekompatybilnych flag w modelu roboczym (draft model).

### Liczby warte zapamiętania

- Przepustowość Llama 3.3 70B FP8 na H100 SXM5 (128 współbieżnych zapytań, pełna optymalizacja): 2200–2400 tokenów/s.
- Ten sam model w domyślnej konfiguracji vLLM (bez chunked prefill): ~1800 tokenów/s.
- Ten sam model w naiwnej pętli PyTorch: ~600 tokenów/s.
- Straty z fragmentacji pamięci KV w PagedAttention: <4%.
- Wskaźnik P99 ITL przy mieszanym obciążeniu: ~15 ms (z chunked prefill) vs ~50 ms (bez chunked prefill).

### Schemat działania harmonogramu

```python
while True:
    finished = [s for s in RUNNING if s.is_done()]
    for s in finished: 
        release_blocks(s)
        RUNNING.remove(s)

    while WAITING and have_free_blocks_for(WAITING[0]):
        s = WAITING.pop(0)
        allocate_initial_blocks(s)
        RUNNING.append(s)

    # planowanie fragmentów prefill oraz decode w jednej paczce (batch)
    batch = []
    for s in RUNNING:
        if s.in_prefill:
            batch.append(next_prefill_chunk(s))   # np. 512 tokenów
        else:
            batch.append(decode_one_token(s))     # 1 token

    run_forward(batch)                            # jedno wspólne wywołanie GPU
```

Skrypt `code/main.py` implementuje powyższą pętlę w czystym Pythonie przy użyciu symulowanych czasów przetwarzania i długości tokenów. Uruchomienie go pozwala zobaczyć, w jaki sposób chunked prefill podtrzymuje generowanie tokenów w fazie decode podczas długich operacji przetwarzania promptów wejściowych.

## Użyj tego

Skrypt `code/main.py` symuluje działanie harmonogramu w stylu vLLM z możliwością włączania poszczególnych funkcji:

- Tryb `NAIVE`: Przetwarzanie sekwencyjne (jedno zapytanie na raz), brak przetwarzania wsadowego.
- Tryb `STATIC`: Klasyczne przetwarzanie wsadowe (oczekiwanie na zebranie paczki i wspólne przetwarzanie do końca).
- Tryb `CONTINUOUS`: Dynamiczne dodawanie i usuwanie zapytań na poziomie pojedynczych iteracji.
- Tryb `CONTINUOUS + CHUNKED`: Dodatkowo przeplatanie fragmentów prefill z generowaniem tokenów (decode).

Wyniki symulacji zawierają łączną przepustowość (tokeny na wirtualną sekundę), średnią wartość TTFT oraz percentyl P99 ITL. W warunkach mieszanego ruchu konfiguracja `CONTINUOUS + CHUNKED` powinna wykazać najwyższą efektywność.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-vllm-scheduler-reader.md`. Na podstawie parametrów Twojego wdrożenia (rozmiar wsadów, alokacja pamięci KV Cache, rozmiar fragmentów prefill, konfiguracja spekulatywna) wygeneruje ono analizę działania harmonogramu, wskazując potencjalne wąskie gardła i zalecane zmiany w konfiguracji.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj wyniki trybów `STATIC` oraz `CONTINUOUS` przy obciążeniu łączącym krótkie i długie zapytania. Z czego wynika różnica w przepustowości – z wydajności fazy prefill, fazy decode czy z opóźnień na końcowym etapie generowania?
2. Zaimplementuj w symulatorze parametr `--max-num-batched-tokens`. Jaka wartość będzie optymalna dla układu H100 obsługującego model Llama 3.3 70B FP8? (Wskazówka: wartość ta zależy od rozmiaru bloku KV Cache i liczby dostępnych bloków, a nie od całkowitej pamięci HBM).
3. Przeanalizuj dokumentację vLLM w wersji v0.18.0. Wskaż, które z flag konfiguracyjnych wykluczają się wzajemnie i opisz przyczyny tej niekompatybilności.
4. Oblicz straty pamięci wywołane fragmentacją KV Cache dla próby 1000 zapytań o średniej długości wyjściowej 1500 tokenów (odchylenie standardowe 600 tokenów) w przypadku: (a) ciągłej alokacji na żądanie przy limicie 8192 tokenów, (b) PagedAttention z blokami o rozmiarze 16 tokenów.
5. Wyjaśnij, dlaczego chunked prefill wydatnie poprawia wskaźnik P99 ITL, ale sam w sobie nie zwiększa surowej przepustowości przetwarzania (throughput). Z czego wynika rzeczywisty zysk wydajnościowy w praktyce produkcyjnej?

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| PagedAttention | „optymalizacja pamięci KV” | System alokacji pamięci dla KV Cache oparty na blokach o stałym rozmiarze; zmniejsza fragmentację pamięci do poziomu <4%. |
| Block table | „tabela bloków” | Struktura danych mapująca logiczne pozycje tokenów w sekwencji na fizyczne bloki KV Cache w pamięci GPU. |
| Continuous batching | „dynamiczne przetwarzanie wsadowe” | Mechanizm podejmujący decyzje o modyfikacji aktywnej paczki (batch) na poziomie pojedynczych kroków generowania tokenów. |
| Chunked prefill | „dzielenie prefill” | Podział długiego promptu wejściowego na mniejsze części (np. po 512 tokenów) i przeplatanie ich przetwarzania z aktywnym generowaniem odpowiedzi. |
| TTFT | „czas pierwszego tokena” | Czas od wysłania zapytania do wygenerowania pierwszego tokena; przy długich promptach kluczowy wpływ ma faza prefill. |
| ITL | „opóźnienie między tokenami” | Czas przetwarzania pojedynczego kroku generacji (decode) pomiędzy kolejnymi tokenami; zależy głównie od rozmiaru aktywnej paczki. |
| Goodput | „przepustowość z zachowaniem SLA” | Liczba tokenów na sekundę przetworzonych w ramach zdefiniowanych limitów parametrów TTFT i ITL. |
| V1 scheduler | „nowy harmonogram” | Zoptymalizowany harmonogram vLLM wprowadzony w 2026 roku, wspierający m.in. zintegrowane mechanizmy spekulatywne. |
| `--gpu-memory-utilization` | „alokacja pamięci” | Parametr określający odsetek pamięci HBM przeznaczony na KV Cache po załadowaniu wag i aktywacji modelu. |

## Dalsze czytanie

- [vLLM Documentation — Speculative Decoding](https://docs.vllm.ai/en/latest/features/spec_decode/) — oficjalne informacje o kompatybilności chunked prefill z dekodowaniem spekulatywnym.
- [NVIDIA vLLM Release Notes](https://docs.nvidia.com/deeplearning/frameworks/vllm-release-notes/index.html) — historia wersji i specyficzne zachowania wersji z 2026 roku.
- [vLLM Blog — PagedAttention](https://blog.vllm.ai/2023/06/20/vllm.html) — oryginalny wpis wprowadzający koncepcję wirtualnej alokacji pamięci.
- [PagedAttention Paper (arXiv:2309.06180)](https://arxiv.org/abs/2309.06180) — pełna analiza teoretyczna fragmentacji pamięci i projektowania harmonogramów.
- [Aleksa Gordic — Inside vLLM](https://www.aleksagordic.com/blog/vllm) — szczegółowa analiza działania harmonogramu V1 wraz z profilowaniem wydajności (flame graphs).
