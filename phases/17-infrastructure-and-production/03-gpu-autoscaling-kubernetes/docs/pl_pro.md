# Autoskalowanie GPU na Kubernetesie — Karpenter, KAI Scheduler, Gang Scheduling

> Właściwe podejście do autoskalowania wymaga koordynacji trzech niezależnych warstw. Pierwszą z nich jest Karpenter, który dynamicznie udostępnia nowe węzły w chmurze (w czasie poniżej jednej minuty, czyli o 40% szybciej niż klasyczny Cluster Autoscaler). Drugą warstwę stanowi KAI Scheduler, który odpowiada za planowanie grupowe (gang scheduling), świadomość topologii sieciowej (topology awareness) oraz kolejkowanie hierarchiczne. Rozwiązanie to zapobiega m.in. pułapce częściowej alokacji zasobów (np. sytuacji, gdy 7 z 8 podów czeka bezużytecznie na uruchomienie ostatniego brakującego procesora GPU, generując wysokie koszty). Trzecią warstwą jest autoskalowanie na poziomie aplikacji (z użyciem narzędzi takich jak NVIDIA Dynamo Planner lub llm-d Workload Variant Autoscaler). Działa ono w oparciu o parametry specyficzne dla wnioskowania LLM — takie jak głębokość kolejki zapytań czy stopień zajętości pamięci podręcznej KV Cache — zamiast polegać na tradycyjnych metrykach zużycia procesora (CPU) lub ogólnego obciążenia kart graficznych z poziomu biblioteki DCGM. Klasyczna pułapka HPA polega na tym, że metryka `DCGM_FI_DEV_GPU_UTIL` mierzy wyłącznie cykle pracy: 100% obciążenia może oznaczać przetwarzanie zarówno 10, jak i 100 żądań. Co więcej, silniki takie jak vLLM wstępnie alokują całą dostępną pamięć dla KV Cache, przez co tradycyjne autoskalery oparte na zużyciu pamięci RAM/VRAM nigdy nie zdecydują się na zmniejszenie liczby replik. Ta lekcja uczy, jak prawidłowo skonfigurować te trzy warstwy i dlaczego należy unikać domyślnej polityki Karpentera `WhenEmptyOrUnderutilized`, która potrafi nagle usunąć węzeł GPU w trakcie generowania odpowiedzi dla użytkownika.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, prosty symulator autoskalowania na podstawie głębokości kolejki)
**Wymagania wstępne:** Faza 17 · 02 (Ekonomika platformy wnioskowania), faza 17 · 04 (Wewnętrzne mechanizmy serwowania vLLM)
**Czas:** ~75 minut

## Cele nauczania

- Poznaj i narysuj schemat trzech warstw automatycznego skalowania (udostępnianie węzłów, planowanie grup podów, autoskalowanie na poziomie aplikacji) oraz przyporządkuj odpowiednie narzędzia do każdej z nich.
- Wyjaśnij, dlaczego metryka `DCGM_FI_DEV_GPU_UTIL` jest nieprawidłowym sygnałem HPA dla vLLM i wskaż dwa właściwe parametry (głębokość kolejki zapytań, stopień zajętości pamięci podręcznej KV Cache).
- Zrozum mechanizm planowania grupowego (gang scheduling) i opisz problem częściowej alokacji zasobów (gdy 7 z 8 procesorów GPU pozostaje bezczynnych), któremu zapobiega KAI Scheduler.
- Dowiedz się, dlaczego polityka konsolidacji Karpentera (`WhenEmptyOrUnderutilized`) może nagle przerywać trwające zadania na GPU i wskaż bezpieczne alternatywne konfiguracje.

## Problem

Twój zespół wdraża usługę serwowania modeli LLM na platformie Kubernetes. Skonfigurowaliście HPA (Horizontal Pod Autoscaler) w oparciu o metrykę obciążenia procesorów GPU `DCGM_FI_DEV_GPU_UTIL`. W godzinach szczytu wskaźnik ten stale utrzymuje się na poziomie 100%. Mimo to HPA nie skaluje klastra w górę – system uznaje, że zasoby są optymalnie wysycone. Dodajecie nową replikę ręcznie i opóźnienie TTFT natychmiast spada, jednak autoskaler wciąż pozostaje bezczynny. Metryka GPU wprowadza Was w błąd.

Innym razem korzystacie z tradycyjnego Cluster Autoscalera do zarządzania węzłami. O 2:00 w nocy użytkownik przesyła duże zapytanie wymagające okna kontekstowego rzędu 1M tokenów. Cluster Autoscaler potrzebuje aż 3 minut na uruchomienie nowego węzła z GPU, co powoduje przekroczenie limitu czasu żądania (timeout) i błąd u użytkownika.

Kolejny problem pojawia się podczas wdrażania modelu 70B, który wymaga podziału na 8 procesorów GPU (tensor parallelism) rozproszonych na 2 węzłach. Klaster ma wolne 7 procesorów GPU na różnych maszynach oraz 1 procesor GPU rozproszony na jeszcze innych 3 węzłach. Autoskaler klastra uruchamia nowy węzeł, aby udostępnić ten jeden brakujący GPU. W tym czasie pozostałe 7 węzłów czeka bezczynnie przez 4 minuty, generując ogromne koszty, podczas gdy Kubernetes dopiero inicjuje ostatni wymagany procesor graficzny.

Rozwiązaniem tych problemów jest właściwa kompozycja trzech warstw autoskalowania: szybkiego udostępniania maszyn, atomowego planowania grup oraz skalowania w oparciu o faktyczne metryki aplikacji.

## Koncepcja

### Warstwa 1 — udostępnianie węzłów (Karpenter)

Karpenter stale monitoruje pody oczekujące w kolejce (Pending pods) i potrafi uruchomić nowy węzeł w chmurze w czasie ok. 45–60 sekund (tradycyjny Cluster Autoscaler potrzebuje na to zwykle 90–120 sekund w przypadku maszyn z GPU). Karpenter dobiera typy instancji dynamicznie na podstawie reguł określonych w konfiguracji `NodePool` – jeśli Twój pod wymaga do uruchomienia 8 kart H100, a klaster nie dysponuje wolną maszyną o takich parametrach, Karpenter utworzy ją bezpośrednio, zamiast próbować skalować istniejące, niedopasowane grupy instancji.

**Ryzyko konsolidacji**: Domyślna polityka Karpentera `consolidationPolicy: WhenEmptyOrUnderutilized` jest bardzo niebezpieczna dla klastrów z GPU. Pozwala ona na usunięcie aktywnego węzła GPU w celu przeniesienia uruchomionych na nim podów na tańszą, mniejszą maszynę. W przypadku serwowania modeli LLM oznacza to nagłe przerwanie obsługi aktywnych zapytań użytkowników i konieczność ponownego załadowania wielogigabajtowego modelu (np. Llama 70B) do pamięci GPU na nowym węźle, co paraliżuje system na wiele minut.

Bezpieczne ustawienia dla puli węzłów z GPU:

```yaml
disruption:
  consolidationPolicy: WhenEmpty
  consolidateAfter: 1h
```

Konfiguracja ta pozwala Karpenterowi na usuwanie wyłącznie całkowicie pustych węzłów po upływie godziny bezczynności, zabezpieczając aktywne procesy przed nagłym przerwaniem.

### Warstwa 2 — planowanie grupowe (KAI Scheduler)

KAI Scheduler (rozwijany wcześniej pod nazwą Karp) realizuje funkcje, których nie obsługuje domyślny system kube-scheduler:

**Planowanie grupowe (gang scheduling)** — zasada „wszystko albo nic”. Jeśli rozproszone wnioskowanie wymaga do pracy klastra 8 procesorów GPU, KAI Scheduler dba o to, aby albo wszystkie 8 podów zostało uruchomionych współbieżnie, albo żadne z nich. Zapobiega to sytuacji częściowej alokacji, w której uruchomienie np. 7 podów powoduje ich bezczynne oczekiwanie w nieskończoność i marnowanie budżetu.

**Świadomość topologii (topology awareness)** — system analizuje, które procesory GPU są połączone szybkimi mostkami NVLink, które znajdują się w tej samej szafie rack, a które komunikują się za pomocą interfejsu InfiniBand. Pody są rozmieszczane tak, aby zminimalizować opóźnienia sieciowe. Jest to kluczowe w przypadku modeli takich jak DeepSeek-V3 67B, gdzie obliczenia tensorowe muszą bezwzględnie mieścić się w jednej domenie NVLink.

**Kolejki hierarchiczne** — umożliwiają współdzielenie tej samej puli drogich procesorów GPU przez różne zespoły deweloperskie z zachowaniem priorytetów i limitów zasobów. Dzięki temu nagły wzrost ruchu produkcyjnego dla Zespołu A może automatycznie zawiesić mniej pilne zadania szkoleniowe Zespołu B, o ile pozwalają na to reguły priorytetów.

KAI Scheduler działa obok standardowego kube-scheduler jako dodatkowy mechanizm planowania (multi-scheduler); aktywuje się go poprzez dodanie odpowiednich adnotacji (annotations) w definicji wdrożenia. Współpracuje on bezpośrednio zarówno z vLLM, jak i z klastrami Ray.

### Warstwa 3 — sygnały na poziomie aplikacji

**Pułapka HPA**: Wykorzystanie GPU raportowane przez DCGM (`DCGM_FI_DEV_GPU_UTIL`) to metryka typu duty-cycle — rejestruje ona jedynie fakt wykonywania jakichkolwiek obliczeń przez rdzenie GPU w danym oknie czasowym. Wskaźnik na poziomie 100% uzyskamy zarówno przy obsłudze 10 zapytań, jak i przy maksymalnym przeciążeniu 100 zapytaniami. Skalowanie na podstawie tej metryki jest nieefektywne.

Dodatkowo vLLM rezerwuje pamięć VRAM na potrzeby KV Cache (zgodnie z parametrem `--gpu-memory-utilization`) zaraz po starcie procesu. Przez to zużycie pamięci GPU stale wynosi blisko 90% nawet przy zerowym ruchu, co uniemożliwia tradycyjnemu HPA podjęcie decyzji o redukcji liczby replik.

**Metryki autoskalowania w 2026 roku**:

- **Głębokość kolejki (queue depth)** — liczba zapytań oczekujących na przetworzenie fazy prefill.
- **Stopień zajętości KV Cache** — odsetek bloków pamięci przydzielonych do obsługi aktywnych generacji.
- **Percentyl P99 TTFT na replikę** — bezpośrednia metryka jakości obsługi (SLA).
- **Goodput** — liczba zapytań na sekundę spełniających wszystkie warunki SLO.

Narzędzia takie jak NVIDIA Dynamo Planner oraz autoskaler llm-d monitorują te parametry bezpośrednio z silnika wnioskowania i sterują liczbą replik, całkowicie zastępując tradycyjne metryki systemowe HPA.

### Podsumowanie ról poszczególnych komponentów

| Zadanie skalowania | Rekomendowane narzędzie |
|----------------|------|
| Dodawanie i usuwanie węzłów w chmurze | Karpenter |
| Planowanie rozproszonych zadań multi-GPU | KAI Scheduler |
| Dodawanie i usuwanie replik podów | Dynamo Planner / llm-d Workload Variant Autoscaler |
| Dobór odpowiedniego typu maszyn GPU | Konfiguracja NodePool w Karpenterze |
| Obsługa priorytetów i wywłaszczania zadań | Hierarchiczne kolejki w KAI Schedulerze |

### Wpływ dezagregacji faz prefill i decoding

W przypadku wdrożenia architektury zdezagregowanej (disaggregated prefill/decode - faza 17 · 17), pody realizujące fazę prefill oraz pody realizujące fazę decoding wymagają zupełnie innych sygnałów do autoskalowania. Pody prefill skaluje się na podstawie głębokości kolejki zapytań, natomiast pody decoding – na podstawie obciążenia i stopnia zajętości pamięci podręcznej KV Cache. Narzędzia takie jak llm-d traktują je jako osobne usługi (Kubernetes Services) i zarządzają nimi za pomocą niezależnych obiektów HPA. Próba objęcia obu ról jednym wspólnym autoskalerem jest błędem projektowym.

### Wpływ czasu zimnego startu na SLA

Planując autoskalowanie, należy uwzględnić czas potrzebny na inicjalizację nowych instancji. 45–60 sekund pracy Karpentera, kolejne minuty na pobranie i załadowanie 20 GB wag modelu do pamięci GPU oraz czas rozruchu samego silnika wnioskowania sprawiają, że uruchomienie nowej repliki od zera może zająć od 2 do 5 minut. Dla krytycznych ścieżek użytkowników należy utrzymywać minimalną ciepłą pulę replik (`min_workers=1`) lub stosować szybkie przywracanie ze stanów przejściowych (checkpointing) na poziomie aplikacji.

### Liczby warte zapamiętania

- Czas uruchamiania węzła przez Karpentera: ~45–60 sekund (w porównaniu do 90–120 sekund dla Cluster Autoscalera).
- KAI Scheduler zapobiega blokowaniu zasobów GPU w scenariuszach częściowej alokacji.
- Metryka `DCGM_FI_DEV_GPU_UTIL` jako sygnał dla HPA jest nieefektywna – należy stosować głębokość kolejki lub zajętość KV Cache.
- Domyślna polityka konsolidacji Karpentera `WhenEmptyOrUnderutilized` potrafi przerwać aktywne generacje – do obsługi LLM należy stosować konfigurację `WhenEmpty` z opóźnieniem `consolidateAfter: 1h`.

## Użyj tego

Skrypt `code/main.py` symuluje działanie trójwarstwowego autoskalera pod dużym obciążeniem GPU. Porównuje on zachowanie naiwnego HPA (opartego o ogólne wykorzystanie GPU), HPA monitorującego głębokość kolejki oraz planowania grupowego z użyciem KAI Schedulera. Zwraca raport dotyczący liczby odrzuconych zapytań, czasu bezczynności procesorów GPU oraz zbiorczy wskaźnik efektywności.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-gpu-autoscaler-plan.md`. Na podstawie parametrów Twojego klastra, profilu obciążenia oraz celów SLA wygeneruje ono kompletny plan konfiguracji autoskalowania dla wszystkich trzech warstw infrastruktury.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Jaką liczbę zapytań odrzuca tradycyjny autoskaler HPA (oparty na obciążeniu GPU) pod dużym ruchem w porównaniu do autoskalera bazującego na głębokości kolejki? Wyjaśnij źródło tej różnicy.
2. Zaprojektuj konfigurację Karpenter NodePool dla klastra serwującego model Llama 3.3 70B FP8 na instancjach z GPU H100 SXM5. Zdefiniuj parametry `capacity-type`, `disruption.consolidationPolicy`, `consolidateAfter` oraz reguły (tolerations/affinity) zabezpieczające te drogie węzły przed uruchamianiem na nich zadań niezwiązanych z GPU.
3. Pody wdrożeniowe w Twoim klastrze utknęły w stanie `Pending` z komunikatem wskazującym, że wolne procesory GPU są dostępne fizycznie w chmurze, ale harmonogram nie może przydzielić zadań. Zdiagnozuj przyczynę – czy problem leży po stronie Karpentera, standardowego kube-scheduler czy KAI Schedulera? Wskaż metryki potwierdzające Twoją diagnozę.
4. Wybierz i uzasadnij optymalną metrykę do autoskalowania podów prefill oraz inną metrykę dedykowaną dla podów decoding w architekturze zdezagregowanej.
5. Oblicz szacowane koszty operacyjne wywoływane przez domyślną politykę Karpentera `WhenEmptyOrUnderutilized` w systemie produkcyjnym działającym w trybie 24/7, zakładając, że powoduje ona średnio 60 przerwanych zapytań dziennie ze wskaźnikiem P99 TTFT > 10 sekund.

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Karpenter | „skaler węzłów” | Nowoczesny autoskaler Kubernetes; potrafi uruchomić węzły w chmurze w czasie poniżej minuty. |
| Cluster Autoscaler | „starszy skaler” | Tradycyjny mechanizm autoskalowania węzłów w Kubernetesie; wolniejszy i mniej elastyczny przy dynamicznym doborze maszyn z GPU. |
| KAI Scheduler | „harmonogram GPU” | Dodatkowy mechanizm planowania zadań w Kubernetesie, wspierający planowanie grupowe, topologię sieci i kolejki. |
| Gang scheduling | „wszystko albo nic” | Atomowe planowanie grupy podów; uruchamia wszystkie pody jednocześnie albo odkłada całą operację w czasie. |
| Topology awareness | „świadomość topologii” | Rozmieszczanie podów na węzłach z uwzględnieniem fizycznych połączeń (NVLink, InfiniBand, szafy rack). |
| `DCGM_FI_DEV_GPU_UTIL` | „zużycie GPU” | Metryka cykli pracy rdzeni GPU; nie nadaje się jako główny wyzwalacz dla autoskalowania systemów LLM. |
| Queue depth | „głębokość kolejki” | Liczba zapytań oczekujących na wykonanie fazy prefill; optymalna metryka dla skalowania podów prefill. |
| KV Cache usage | „zajętość KV Cache” | Stopień wykorzystania przydzielonych bloków pamięci podręcznej; optymalna metryka dla skalowania podów decoding. |
| Consolidation | „konsolidacja w Karpenterze” | Automatyczne usuwanie lub zastępowanie węzłów mniejszymi/tańszymi w celu optymalizacji kosztów chmury. |
| `WhenEmpty + 1h` | „bezpieczna konsolidacja” | Konfiguracja Karpentera zapobiegająca usuwaniu węzłów z aktywnymi podami realizującymi wnioskowanie. |

## Dalsze czytanie

- [KAI Scheduler GitHub](https://github.com/kai-scheduler/KAI-Scheduler) — specyfikacja techniczna, dokumentacja i przykłady wdrożeń.
- [Karpenter Disruption Controls](https://karpenter.sh/docs/concepts/disruption/) — szczegółowe informacje o konfiguracji polityki konsolidacji bezpiecznej dla maszyn z GPU.
- [NVIDIA — Zdezagregowane wnioskowanie LLM na Kubernetesie](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — analiza wdrożeń i wskaźników skalowania z użyciem Dynamo Plannera.
- [Dokumentacja Ray — KAI Scheduler dla RayClusters](https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kai-scheduler.html) — wzorce integracji klastrów Ray z harmonogramem KAI.
- [AWS EKS Best Practices Guide for AIML](https://docs.aws.amazon.com/eks/latest/best-practices/aiml-compute.html) — oficjalne zalecenia AWS dotyczące obliczeń wysokiej wydajności na Kubernetesie.
- [llm-d GitHub](https://github.com/llm-d/llm-d) — projekt dedykowanego autoskalera dla dynamicznych obciążeń wnioskowania LLM.
