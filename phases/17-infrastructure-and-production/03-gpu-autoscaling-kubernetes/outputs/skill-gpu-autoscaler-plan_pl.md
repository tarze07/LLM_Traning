---

name: gpu-autoscaler-plan
description: Zaprojektuj trójwarstwowy plan automatycznego skalowania procesora graficznego (Karpenter + KAI Scheduler + sygnały aplikacji) dla klastra obsługującego LLM opartego na Kubernetes. Diagnozuj pułapki DCGM_FI_DEV_GPU_UTIL i błędy częściowej alokacji.
version: 1.0.0
phase: 17
lesson: 03
tags: [kubernetes, gpu, autoscaling, karpenter, kai-scheduler, hpa, dynamo-planner, llm-d]

---

Biorąc pod uwagę topologię klastra (węzły, typy procesorów graficznych, domeny NVLink), kształt obciążenia (konfiguracja TP/PP, średnia współbieżność, współczynnik transmisji) i SLO (TTFT P99, goodput), utwórz trójwarstwowy plan automatycznego skalowania.

Wyprodukuj:

1. Warstwa 1 — Karpenter NodePool. Określ `instance-type`, `capacity-type` (na żądanie / miejsce / zarezerwowane), `consolidationPolicy` (musi to być `WhenEmpty` z `consolidateAfter: 1h` dla pul GPU), zmiany wykluczające obciążenia inne niż GPU oraz etykiety wyboru harmonogramu KAI.
2. Warstwa 2 — polityka harmonogramu KAI. Określ, czy wymagane jest planowanie grupowe (tak dla TP/PP > 1). Zdefiniuj ograniczenia topologiczne (domena NVLink, szafa, strefa). Określ hierarchię kolejek i reguły wywłaszczania dla dzierżaw produkcyjnych i szkoleniowych.
3. Warstwa 3 — Autoskaler aplikacji. Wybierz sygnał: głębokość kolejki dla obciążeń związanych ze wstępnym wypełnieniem, wykorzystanie pamięci podręcznej KV dla obciążeń dekodowanych, dobra wydajność złożona dla zadań mieszanych. Zabroń `DCGM_FI_DEV_GPU_UTIL` i wyjaśnij dlaczego.
4. Podział zdezagregowany. Jeśli używasz rozdrobnionego wstępnego wypełniania/dekodowania fazy 17 · 17, określ oddzielne HPA — sygnał głębokości kolejki dla puli wstępnego wypełnienia, sygnał wykorzystania KV dla puli dekodowania.
5. Rozmiar ciepłego basenu. Minimalna liczba gotowych replik dla ścieżek krytycznych SLO w oparciu o ograniczenie P99 TTFT i zaobserwowany czas zimnego startu (zapewnienie węzła + obciążenie modelu).
6. Monitorowanie. Metryki na pulpicie nawigacyjnym: głębokość kolejki na replikę, wykorzystanie KV na replikę, czas oczekiwania na udostępnienie węzła, liczba odroczeń w harmonogramie grupy, zdarzenia konsolidacji Karpenter.

Twarde odrzucenia:
- Polecanie HPA na `DCGM_FI_DEV_GPU_UTIL`. Odrzuć i podaj głębokość kolejki + wykorzystanie KV jako prawidłowe sygnały.
- Pozostawienie `consolidationPolicy: WhenEmptyOrUnderutilized` dla puli GPU. Odmów i podaj ryzyko eksmisji związanej z pracą.
- Ignorowanie planowania grupowego dla obciążenia TP/PP. Odmów — częściowa alokacja to antywzorzec spalający $.

Zasady odmowy:
- Jeśli klaster ma tylko jeden typ procesora graficznego i jeden węzeł, odrzuć propozycję firmy Karpenter — klient potrzebuje najpierw zarządzanej wersji bezserwerowej (faza 17 · 02).
- Jeśli operator poprosi o „skalowanie pamięci GPU”, odmów — vLLM wstępnie przydziela `--gpu-memory-utilization`; pamięć pozostaje w pobliżu 90% nawet przy jednym żądaniu.
— Jeśli harmonogram grupowy zostanie odrzucony ze względu na obciążenie TP-8, powołując się na złożoność, odmów certyfikacji planu — umieszczenie pojedynczego modułu na 8 rozproszonych procesorach graficznych kończy się niepowodzeniem atomowo.

Dane wyjściowe: jednostronicowy plan z fragmentem kodu YAML firmy Karpenter, fragmentem konfiguracji harmonogramu KAI, wyborem sygnału HPA/niestandardowego autoskalera, numerem ciepłej puli i pięcioma metrykami pulpitu nawigacyjnego. Zakończ pojedynczym wyłącznikiem awaryjnym: jeśli P99 TTFT naruszy, wróć do ostatniego znanego stanu automatycznego skalowania.