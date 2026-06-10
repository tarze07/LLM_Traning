# Autoskalowanie GPU na Kubernetesie — Karpenter, KAI Scheduler, Gang Scheduling

> Trzy warstwy, a nie jedna. Karpenter dynamicznie udostępnia węzły (poniżej jednej minuty, 40% szybciej niż Cluster Autoscaler). KAI Scheduler obsługuje planowanie gangów, świadomość topologii i kolejki hierarchiczne — zapobiega pułapce częściowej alokacji 7 z 8, w której siedem węzłów czeka i spala się na jednym brakującym procesorze graficznym. Automatyczne skalowanie na poziomie aplikacji (NVIDIA Dynamo Planner, llm-d Workload Variant Autoscaler) skalują się na podstawie sygnałów specyficznych dla wnioskowania — głębokości kolejki, wykorzystania pamięci podręcznej KV — a nie cyklu pracy procesora/DCGM. Klasyczna pułapka HPA polega na tym, że `DCGM_FI_DEV_GPU_UTIL` jest miarą cyklu pracy: 100% może wynosić 10 lub 100 żądań. vLLM wstępnie przydziela pamięć podręczną KV, więc pamięć nigdy nie wyzwala skalowania w dół. Ta lekcja uczy, jak komponować trzy warstwy i unikać domyślnej polityki Karpentera `WhenEmptyOrUnderutilized`, która przerywa działające zadania GPU w połowie wnioskowania.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator automatycznego skalowania głębokości kolejki zabawek)
**Wymagania wstępne:** Faza 17 · 02 (ekonomika platformy wnioskowania), faza 17 · 04 (wewnętrzne jednostki obsługujące vLLM)
**Czas:** ~75 minut

## Cele nauczania

- Narysuj diagram trzech warstw automatycznego skalowania (wyposażanie węzłów, planowanie grup, poziom aplikacji) i nazwij narzędzie używane w każdej warstwie.
- Wyjaśnij, dlaczego `DCGM_FI_DEV_GPU_UTIL` jest nieprawidłowym sygnałem HPA dla vLLM i podaj dwa zamienniki (głębokość kolejki, wykorzystanie pamięci podręcznej KV).
- Opisz planowanie gangów i tryb awarii częściowej alokacji, któremu zapobiega KAI Scheduler (7 z 8 procesorów graficznych jest bezczynne).
- Podaj nazwę polityki konsolidacji firmy Karpenter (`WhenEmptyOrUnderutilized`), która kończy działające zadania GPU i podaj bezpieczną alternatywę na rok 2026.

## Problem

Twój zespół dostarcza usługę obsługi LLM na platformie Kubernetes. Ustawiasz HPA z `DCGM_FI_DEV_GPU_UTIL` jako sygnałem. W godzinach pracy piny serwisowe są wykorzystywane w 100%. HPA nigdy się nie skaluje — już myśli, że jesteś pełny. Dodajesz replikę ręcznie; TTFT spada. HPA nadal się nie skaluje. Sygnał cię okłamuje.

Oddzielnie używasz automatycznego skalowania klastrów dla węzłów. O godzinie 2 w nocy pojawia się monit z tokenem 1M; klaster spędza 3 minuty na udostępnianiu węzła i upłynął limit czasu żądania.

Ponownie wdrażasz model 70B wymagający 8 procesorów graficznych w 2 węzłach. Klaster ma 7 wolnych procesorów graficznych i 1 rozłożony na 3 węzły. Funkcja automatycznego skalowania klastra udostępnia węzeł dla 1 brakującego procesora GPU. Siedem węzłów czeka 4 minuty na spalanie pieniędzy, podczas gdy Kubernetes uruchamia ostatni procesor graficzny.

Trzy warstwy, trzy różne tryby awarii. Automatyczne skalowanie uwzględniające procesor graficzny w roku 2026 nie polega na „włączaniu HPA”. Obejmuje udostępnianie węzłów komponowania, planowanie grup i automatyczne skalowanie sygnału aplikacji.

## Koncepcja

### Warstwa 1 — udostępnianie węzłów (Karpenter)

Karpenter obserwuje oczekujące pody i udostępnia węzły w ciągu ~45–60 sekund (automatyczne skalowanie klastra zwykle zajmuje 90–120 sekund w przypadku węzłów GPU). Wybiera typy instancji dynamicznie zgodnie z ograniczeniem `NodePool` — jeśli Twój pod potrzebuje 8 H100, a klaster nie ma pasującego węzła, Karpenter udostępnia jeden bezpośrednio, zamiast skalować istniejącą grupę.

**Pułapka konsolidacji**: Domyślna wartość `consolidationPolicy: WhenEmptyOrUnderutilized` Karpentera jest niebezpieczna dla pul GPU. Zakończy działający węzeł GPU w celu migracji podów do tańszej instancji o odpowiedniej wielkości. W przypadku obciążeń wnioskowania oznacza to wykluczenie uruchomionych żądań i ponowne załadowanie modelu 70B w nowym węźle. Strata to minuty pojemności i niepowodzenia żądań.

Bezpieczne ustawienie dla pul GPU:

```yaml
disruption:
  consolidationPolicy: WhenEmpty
  consolidateAfter: 1h
```

Pozwala Karpenterowi skonsolidować naprawdę puste węzły po godzinie, ale nigdy nie eksmitować działającego zadania.

### Warstwa 2 — planowanie grupowe (KAI Scheduler)

KAI Scheduler (projekt „Karp”, którego nazwa została następnie zmieniona) obsługuje to, czego nie robi domyślny program kube-scheduler:

**Planowanie grupowe** — planuj wszystko albo nic. Rozproszony moduł wnioskowania wymagający 8 procesorów graficznych albo wszystkie 8 zaczynają się razem, albo żaden. Bez tego wpadniesz w pułapkę częściowej alokacji: uruchamia się 7 z 8 podów, czekaj w nieskończoność, spalaj pieniądze.

**Świadomość topologii** — dowiedz się, które procesory graficzne współdzielą NVLink, które znajdują się w tej samej szafie, a które mają między sobą technologię InfiniBand. Umieść odpowiednio strąki. Równoległe obciążenie tensorowe DeepSeek-V3 67B musi pozostać w jednej domenie NVLink; KAI Scheduler to szanuje.

**Kolejki hierarchiczne** — wiele zespołów rywalizuje o tę samą pulę procesorów graficznych z zachowaniem priorytetu i limitu. Szczyt produkcyjny Zespołu A zostaje przesłonięty pracą szkoleniową Zespołu B tylko wtedy, gdy pozwalają na to zasady priorytetów.

KAI jest wdrażany razem z kube-scheduler jako dodatkowy program planujący; dodajesz adnotacje do obciążeń, aby z nich skorzystać. Zarówno stos produkcyjny Ray, jak i vLLM integrują się.

### Warstwa 3 — sygnały na poziomie aplikacji

**Pułapka HPA**: `DCGM_FI_DEV_GPU_UTIL` to metryka cyklu pracy — mierzy, czy procesor graficzny wykonywał pracę w każdym interwale próbkowania. 100% wykorzystania może oznaczać 10 lub 100 jednoczesnych żądań; GPU był zajęty tak czy inaczej. Skalowanie w cyklu pracy jest skalowaniem na ślepo.

Co gorsza, vLLM i podobne silniki wstępnie przydzielają pamięć podręczną KV (do `--gpu-memory-utilization`). Nawet przy jednym żądaniu zużycie pamięci utrzymuje się na poziomie blisko 90%. HPA oparte na pamięci nigdy nie jest skalowane w dół.

**Sygnały zastępcze 2026**:

- Głębokość kolejki (liczba żądań oczekujących na wstępne wypełnienie).
- Wykorzystanie pamięci podręcznej KV (jaka część bloków jest przydzielona do aktywnych sekwencji).
- Na replikę P99 TTFT (Twój sygnał SLA).
- Goodput (żądania spełnienia wszystkich SLO na sekundę).

Narzędzie NVIDIA Dynamo Planner i automatyczne skalowanie wariantów obciążenia llm-d wykorzystują te sygnały i skalują repliki. Całkowicie zastępują HPA do obsługi LLM.

### Kiedy czego używać

| Decyzja skali | Narzędzie |
|----------------|------|
| Dodaj/usuń węzły | Stolarz |
| Zaplanuj zadania z wieloma procesorami graficznymi | Harmonogram KAI |
| Dodaj/usuń repliki | Dynamo Planner / llm-d WVA (lub niestandardowy HPA na głębokość kolejki) |
| Wybierz typ procesora graficznego | Pula węzłów Karpentera |
| Wywłaszczaj o niskim priorytecie | Kolejki KAI Scheduler |

### Zdezagregowane wstępne wypełnianie/dekodowanie komplikuje wszystko

Jeśli uruchomisz zdezagregowane wstępne wypełnianie/dekodowanie (faza 17 · 17), masz dwie klasy podów z różnymi wyzwalaczami skalowania: wstępne wypełnianie podów skaluje się według głębokości kolejki, dekodowanie podów skaluje się według ciśnienia pamięci podręcznej KV. llm-d udostępnia je jako oddzielne `Services` z HPA dla poszczególnych ról. Nie próbuj umieszczać jednego HPA przed obydwoma.

### Zimny start też ma tutaj znaczenie

Łagodzenie zimnego startu (faza 17 · 10) polega na tym, że czas udostępniania węzła staje się widoczny dla użytkownika. Rozgrzewka Karpentera trwająca 45–60 sekund, obciążenie modelu 20 GB i uruchomienie silnika oznaczają, że żądanie od zera zajmuje 2–5 minut. Zachowaj ciepłą pulę (`min_workers=1`) dla ścieżek krytycznych dla SLO lub użyj punktów kontrolnych w stylu modalnym w warstwie aplikacji.

### Liczby, które powinieneś zapamiętać

— Udostępnianie węzła Karpenter: ~45–60 s w porównaniu do automatycznego skalowania klastra ~90–120 s (węzły GPU).
- KAI Scheduler zapobiega marnotrawieniu częściowej alokacji — pułapka 7 z 8.
- `DCGM_FI_DEV_GPU_UTIL` jako sygnał HPA: uszkodzony; użyj głębokości kolejki lub wykorzystania KV.
- Karpenter `WhenEmptyOrUnderutilized`: kończy uruchomione zadania GPU. Do wnioskowania użyj `WhenEmpty + consolidateAfter: 1h`.

## Użyj tego

`code/main.py` symuluje trójwarstwowy autoskaler przy dużym obciążeniu procesora graficznego. Porównuje naiwne HPA (cykl pracy), HPA głębokości kolejki i skalowanie zaplanowane według grupy KAI. Raportuje niezaspokojone żądania, minuty bezczynności GPU i wynik złożony.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-gpu-autoscaler-plan.md`. Biorąc pod uwagę topologię klastra, kształt obciążenia i poziom docelowego poziomu usług, projektuje trójwarstwowy plan automatycznego skalowania.

## Ćwiczenia

1. Uruchom `code/main.py`. Ile żądań przy dużym obciążeniu pracą naiwny moduł HPA w cyklu pracy odrzuca przechwytywane przez HPA głębokość kolejki? Skąd bierze się różnica?
2. Zaprojektuj Karpenter NodePool dla klastra obsługującego Llama 3.3 70B FP8 na H100 SXM5. Określ `capacity-type`, `disruption.consolidationPolicy`, `consolidateAfter` i zmianę, która utrzymuje obciążenia inne niż GPU poza tymi węzłami.
3. Twój zespół zgłasza, że ​​wdrożenia utknęły w stanie Oczekujące, ponieważ „Kompresory graficzne są dostępne, ale pod nie można zaplanować”. Diagnozuj — czy to Karpenter, kube-scheduler czy KAI Scheduler? Które wskaźniki potwierdzają?
4. Wybierz sygnał, aby automatycznie skalować zdezagregowane wstępnie wypełnione zasobniki i inny sygnał do dekodowania zasobników. Uzasadnij oba.
5. Oblicz koszt pułapki konsolidacyjnej `WhenEmptyOrUnderutilized` w usłudze produkcyjnej działającej 24 godziny na dobę, 7 dni w tygodniu, która średnio 60 zdarzeń powodujących porzucenie żądań dziennie przy P99 TTFT > 10 s.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Stolarz | „dostawca węzła” | Autoskaler węzła Kubernetes; rezerwa subminutowa |
| Automatyczne skalowanie klastrów | „stary skaler” | Poprzednik automatycznego skalowania węzła Kubernetes; wolniej, grupowo |
| Harmonogram KAI | „harmonogram GPU” | Dodatkowy harmonogram dla gangu + topologii + kolejek |
| Harmonogram gangów | „wszystko albo nic” | Zaplanuj N podów atomowo lub odłóż wszystkie |
| Świadomość topologii | „świadomy stojaka” | Umieść kapsuły w oparciu o rozmieszczenie NVLink/IB/rack |
| `DCGM_FI_DEV_GPU_UTIL` | „Wykorzystanie GPU” | Wskaźnik cyklu pracy; NIE sygnał skalujący dla LLM |
| Głębokość kolejki | „oczekujące żądania” | Poprawny sygnał HPA dla skalowania związanego ze wstępnym wypełnieniem |
| Wykorzystanie pamięci podręcznej KV | „ciśnienie pamięci” | Poprawny sygnał HPA dla skalowania związanego z dekodowaniem |
| Konsolidacja | „Konsolidacja stolarska” | Zakończenie węzła na tańszy typ instancji |
| `WhenEmpty + 1h` | „bezpieczna konsolidacja” | Polityka, która nie wyklucza uruchomionych zadań GPU |

## Dalsze czytanie

- [KAI Scheduler GitHub](https://github.com/kai-scheduler/KAI-Scheduler) — dokumentacja projektowa i przykłady konfiguracji.
- [Karpenter Disruption Controls](https://karpenter.sh/docs/concepts/disruption/) — semantyka zasad konsolidacji i ustawienia domyślne bezpieczne dla GPU.
— [NVIDIA — zdezagregowane wnioskowanie LLM na platformie Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — sygnały skalowania dodatku Dynamo Planner.
- [Ray docs — KAI Scheduler for RayClusters](https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kai-scheduler.html) — Wzorzec integracji Ray.
— [Najlepsze praktyki AWS EKS dotyczące obliczeń i automatycznego skalowania](https://docs.aws.amazon.com/eks/latest/best-practices/aiml-compute.html) — wskazówki dotyczące zarządzanego Kubernetesa.
— [llm-d GitHub](https://github.com/llm-d/llm-d) — Projekt automatycznego skalowania wariantu obciążenia.