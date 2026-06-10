# Zdezagregowane wstępne wypełnianie/dekodowanie — NVIDIA Dynamo i llm-d

> Wstępne wypełnienie jest powiązane z obliczeniami; dekodowanie jest powiązane z pamięcią. Uruchamianie obu na tym samym procesorze graficznym marnuje jeden zasób. Dezagregacja dzieli je na oddzielne pule i przesyła między nimi pamięć podręczną KV za pośrednictwem NIXL (RDMA/InfiniBand lub rezerwa TCP). NVIDIA Dynamo (ogłoszenie GTC 2025, 1.0 GA) plasuje się powyżej vLLM/SGLang/TRT-LLM — jej Planner Profiler + SLA Planner automatycznie dopasowują współczynniki wstępnego wypełnienia do dekodowania, aby spełnić SLO. NVIDIA publikuje wzrosty przepustowości w tym zakresie — developer.nvidia.com (2025-06) pokazuje ~6x poprawę DeepSeek-R1 MoE na GB200 NVL72 + Dynamo w trybie średniego opóźnienia, a strona produktu Dynamo (developer.nvidia.com, bez daty) reklamuje przepustowość do 50x MoE na GB300 NVL72 + Dynamo w porównaniu z Hopperem. Liczba „30x” to suma raportów społeczności z pełnych raportów Blackwell + Dynamo + DeepSeek-R1; nie znaleźliśmy ani jednego głównego źródła podającego dokładnie 30x, więc potraktuj to jako twierdzenie kierunkowe. llm-d (Red Hat + AWS) jest natywny dla Kubernetes: wstępne wypełnianie/dekodowanie/router jako niezależne usługi z HPA dla poszczególnych ról. llm-d 0.5 dodaje hierarchiczne odciążanie KV, routing LoRA uwzględniający pamięć podręczną, sieć UCCL, skalowanie do zera. Ekonomia: wewnętrzne zestawienie wielu ujawnień klientów sugeruje 30–40% oszczędności w zakresie $2M-class inference spend (i.e., $600–800 tys./rok) w przypadku przejścia z udostępniania kolokowanego na zdezagregowane z Dynamo przy stałej umowie SLA; konkretna liczba $2M→$600–800 tys. to wewnętrzne zestawienie, a nie pojedyncze opublikowane studium przypadku — użyj jej jako kotwicy rzędu wielkości, a nie cytatu referencyjnego. Krótkie podpowiedzi (<512 tokenów, krótki wynik) nie uzasadniają kosztu transferu.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator zabawek zdezagregowanych i kolokowanych)
**Wymagania wstępne:** Faza 17 · 04 (wewnętrzne elementy obsługujące vLLM), faza 17 · 08 (metryki wnioskowania)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego wstępne wypełnianie i dekodowanie mają różną optymalną alokację procesora graficznego, i opisz ilościowo straty wynikające z kolokacji.
- Diagram zdezagregowanej architektury: pula wstępnego wypełnienia, pula dekodowania, transfer KV przez NIXL, router.
- Wymień warunek, w którym dezagregacja NIE się opłaca (krótkie podpowiedzi, krótkie wyniki).
- Odróżnij NVIDIA Dynamo (stos powyżej) od llm-d (natywny dla Kubernetes) i dopasuj każdy do kontekstu operacyjnego.

## Problem

Uruchamiasz Lamę 3.3 70B na 8 H100. Przy mieszanym obciążeniu (długie monity + krótkie dane wyjściowe) procesory graficzne są bezczynne podczas dekodowania, ponieważ większość obliczeń została wydana na wstępne wypełnienie. Przy różnym obciążeniu pracą (krótkie podpowiedzi + długie wyniki) dzieje się odwrotnie. Kolokowane wstępne wypełnianie i dekodowanie oznacza, że ​​obydwa te elementy są nadmiernie udostępniane.

Wpływ na budżet: 20–40% czasu procesora graficznego jest marnowane na niewłaściwy zasób. Kupujesz moc obliczeniową H100 w celu dekodowania związanego z pamięcią lub kupujesz przepustowość H100 HBM w celu wstępnego wypełniania związanego z obliczeniami. Jedno i drugie jest kosztownym odpadem.

Dezagregacja dzieli wstępne wypełnienie i dekodowanie na osobne pule o rozmiarze dostosowanym do wąskiego gardła każdego z nich. Transfery pamięci podręcznej KV z puli wstępnego wypełnienia do puli dekodowania za pośrednictwem połączenia międzysieciowego o dużej przepustowości.

## Koncepcja

### Dlaczego wąskie gardła są różne

**Wstępne napełnianie** – uruchom transformator po pojawieniu się monitu o pełne wejście w jednym kroku. Dominują mnożenia macierzy; związany z obliczeniami. H100 FP8 zapewnia ~2000 TFLOPS użytecznej przepustowości. Wydajność wsadowa jest dobra — jeden forwarder przetwarza wiele tokenów.

**Dekoduj** — generuj jeden token na raz, odczytując pełne wagi w każdej iteracji. Ograniczona przepustowość pamięci. HBM3 daje ~3 TB/s. Wydajność wsadowa jest dobra tylko przy dużej współbieżności — odczytane wagi amortyzują się w całej partii.

Kolokowanie ich: kupujesz procesory graficzne zoptymalizowane pod kątem obu. H100 jest dobry w obu przypadkach, ale kosztuje tyle samo w obu przypadkach. Na dużą skalę chcesz wstępnie wypełnić pulę na H100/dużo mocy obliczeniowej; Pula dekodowania na H200 / z dużym obciążeniem pamięci lub z agresywną kwantyzacją.

### Architektura

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

NIXL to transport międzywęzłowy firmy NVIDIA. Używa RDMA/InfiniBand, jeśli jest dostępny, w przeciwnym razie zastępczy protokół TCP. Opóźnienie transferu jest rzeczywiste — zazwyczaj 20–80 ms dla pamięci podręcznej KV monitu o 4K tokena w 70B FP8. Dlatego krótkie podpowiedzi nie uzasadniają dezagregacji: podatek transferowy przewyższa oszczędności.

### Dynamo kontra llm-d

**NVIDIA Dynamo** (ogłoszenie GTC 2025, 1.0 GA):
- Zasiada nad vLLM, SGLang, TRT-LLM jako orkiestrator.
- Planner Profiler mierzy obciążenie pracą, SLA Planner automatycznie konfiguruje współczynniki wstępnego wypełnienia: dekodowania.
- Rdzeń Rust, rozszerzalność Pythona.
- Wzrost przepustowości: NVIDIA raportuje 6x dla DeepSeek-R1 MoE na GB200 NVL72 + Dynamo w trybie średniego opóźnienia (developer.nvidia.com, 2025-06); raporty społeczności dotyczące „do 30x” pełnych stosów Blackwell + Dynamo + DeepSeek-R1 nie mają jednego głównego źródła i należy je traktować jako kierunkowe.
- GB300 NVL72 + Dynamo: do 50x przepustowość MoE w porównaniu do Hoppera, zgodnie ze stroną produktu Dynamo (developer.nvidia.com, bez daty).

**llm-d** (Red Hat + AWS, natywnie Kubernetes):
- Wstępne wypełnienie / dekodowanie / router jako niezależne usługi Kubernetes.
- HPA dla poszczególnych ról z sygnałami głębokości kolejki (wstępne wypełnienie) / wykorzystania KV (dekodowanie).
- `topologyConstraint packDomain: rack` pakuje kliki wstępnego wypełniania i dekodowania na tym samym stojaku w celu zapewnienia transferu KV o dużej przepustowości.
- llm-d 0,5 (2026): hierarchiczne odciążanie KV, routing LoRA uwzględniający pamięć podręczną, sieć UCCL, skalowanie do zera.

Użyj dodatku Dynamo, jeśli chcesz zarządzanego orkiestratora znajdującego się nad stosem. Użyj llm-d, jeśli chcesz prymitywów natywnych dla Kubernetes i jesteś zaangażowany w ekosystem CNCF.

### Ekonomia

Wewnętrzny kompozyt (ani jedno opublikowane studium przypadku — kotwica rzędu wielkości):

- Wydatki rzędu 2 mln USD rocznie na udostępnianie w kolokacji.
— Przełączono na zdezagregowane za pomocą Dynamo.
— Ta sama liczba żądań, ta sama umowa SLA dotycząca opóźnienia P99.
- Zgłoszone oszczędności: $600K–$800 tys./rok (obniżka o 30–40%).
- Brak nowego sprzętu.

Syntetyzujemy tę liczbę na podstawie informacji ujawnionych przez wielu klientów, a nie z jednego, możliwego do cytowania studium przypadku; Najbliższe opublikowane dane to 2x szybszy TTFT firmy Baseten / 61% wyższa przepustowość z routingiem Dynamo KV (baseten.co, 2025–10) oraz prognoza VAST + CoreWeave dotycząca 60–130% więcej tokenów/$ przy współczynniku trafień KV 40–60% (vastdata.com, 2025–12). Oszczędności wynikają z odpowiedniego doboru rozmiaru każdej puli; Obciążenia wymagające wstępnego wypełnienia (RAG z prefiksami ponad 8 000) przynoszą więcej korzyści niż obciążenia zrównoważone.

### Kiedy NIE należy dokonywać dezagregacji

- Podpowiada < 512 tokenów i wyświetla < 200 tokenów: podatek transferowy dominuje nad zyskiem.
- Mały klaster (< 4 procesory graficzne): niewystarczająca różnorodność puli.
- Zespół nie może obsługiwać dwóch pul GPU ze skalowaniem według ról: Dynamo pomaga, ale nie jest to trywialne.
- Brak tkaniny RDMA: podatek od transferu TCP jest wyższy.

### Router integruje się z fazą 17 · 11

Zdezagregowane routery obsługują pamięć podręczną KV (faza 17 · 11). Żądanie trafia do puli dekodowania zawierającej swój prefiks — jeśli nie ma dopasowania, następuje wstępne wypełnienie → dekodowanie. Współczynnik trafień i związek dezagregacji — router obsługujący pamięć podręczną określa, czy w ogóle potrzebne jest nowe wstępne wypełnienie.

### Ministerstwo Sprawiedliwości w sprawie Blackwell to prawdziwe liczby

GB300 NVL72 + Dynamo wykazuje 50-krotną przepustowość MoE w stosunku do wartości bazowych Hoppera. Routing ekspercki MoE wymaga dużej mocy obliczeniowej podczas wstępnego wypełniania, ale wymaga dużej ilości pamięci podczas dekodowania (eksperckie pamięci podręczne), więc dezagregacja to podwójne zwycięstwo. Obsługa modelu granicznego na rok 2026 dominuje w MoE (DeepSeek-V3, przyszłe warianty GPT-5).

### Liczby, które powinieneś zapamiętać

Dryf wyników testów porównawczych — NVIDIA i stos wnioskowań publikują aktualizowane wyniki co kwartał. Sprawdź ponownie zanim zacytujesz.

- DeepSeek-R1 na GB200 NVL72 + Dynamo: ~6x przepustowość w porównaniu z wartością bazową w trybie średniego opóźnienia (developer.nvidia.com, 2025-06); Roszczenia społeczności „do 30x” dotyczące pełnych stosów Blackwell + Dynamo to agregaty kierunkowe bez jednego głównego źródła.
- GB300 NVL72 + Dynamo: do 50x przepustowość MoE w porównaniu do Hoppera (developer.nvidia.com, bez daty).
- Kotwica oszczędności (zestaw wewnętrzny, a nie pojedyncze studium przypadku): $600-800K/year off a $2 mln rocznych wydatków przy stałej umowie SLA.
- Próg dezagregacji: monity > 512 tokenów + dane wyjściowe > 200 tokenów.
- Transfer KV przez NIXL: 20-80 ms dla KV z komunikatem 4K na 70B FP8.

## Użyj tego

`code/main.py` symuluje wyświetlanie kolokowane i zdezagregowane. Raportuje przepustowość, koszt żądania i skrzyżowanie długości podpowiedzi.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-disaggregation-decider.md`. Biorąc pod uwagę obciążenie pracą i klaster, decyduje, czy dokonać dezagregacji.

## Ćwiczenia

1. Uruchom `code/main.py`. W jakim czasie dezagregacja jest lepsza od kolokacji?
2. Zaprojektuj pulę wstępnego wypełnienia i pulę dekodowania dla usługi RAG z prefiksem P99 o długości 8K i wyjściem 300.
3. Dynamo vs llm-d: wybierz jeden dla sklepu wykorzystującego wyłącznie Kubernetes, bez preferencji dotyczących środowiska wykonawczego Pythona.
4. Oblicz koszt transferu KV: wstępne wypełnienie 4K na 70B FP8 = ~500 MB KV. Przy RDMA 100 GB/s transfer = 5 ms. Przy TCP 10 GB/s = 50 ms. Co ma znaczenie dla Twojej umowy SLA?
5. Routing ekspercki Ministerstwa Środowiska zmienia wzorce dostępu KV. Jak zachowuje się dezagregacja w przypadku MoE, które aktywuje różnych ekspertów na token?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Zdezagregowana porcja | „podzielone wstępne wypełnianie/dekodowanie” | Oddzielne pule GPU dla każdej fazy |
| NIXL | „Transport NVIDIA” | Międzywęzłowy transfer KV Dynamo (RDMA/TCP) |
| NVIDIA Dynamo | „Orkiestrator” | Koordynator stosu dla vLLM/SGLang/TRT-LLM |
| llm-d | „Natywny Kubernetes” | Dezagregowany stos Red Hat + AWS K8 |
| Planista Profiler | „Automatyczna konfiguracja Dynamo” | Mierzy obciążenie pracą, konfiguruje współczynniki puli |
| Planista SLA | „Polityka Dynama” | Automatyczne dopasowywanie stawek, wstępne wypełnianie: dekodowanie w celu spełnienia SLO |
| `packDomain: rack` | „topologia llm-d” | Spakuj wstępne wypełnienie i dekodowanie na tym samym stojaku, aby uzyskać szybkie KV |
| Uniwersytet Kalifornijski | „zjednoczony kolektyw” | llm-d 0,5 warstwa sieciowa dla skalowania do zera |
| Przekierowanie ekspertów Ministerstwa Środowiska | „ekspert na token” | Wzór DeepSeek-V3; dezagregacja pomaga |

## Dalsze czytanie

- [NVIDIA — Przedstawiamy Dynamo](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/)
— [NVIDIA — zdezagregowane wnioskowanie LLM na platformie Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/)
— [Blog dotyczący szczegółowego udostępniania TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/blogs/tech_blog/blog5_Disaggregated_Serving_in_TensorRT-LLM.html)
— [llm-d GitHub](https://github.com/llm-d/llm-d)
- [Informacje o wersji llm-d 0.5](https://github.com/llm-d/llm-d/releases)