# Capstone 06 — Agent rozwiązywania problemów DevOps dla Kubernetes

> Agent DevOps AWS przeszedł na wersję GA, Resolve AI opublikowało swoje podręczniki K8, NeuBird zademonstrował monitorowanie semantyczne, a Metoro powiązał AI SRE z SLO na usługę. Kształt produkcji jest ustalony: uruchamia się webhook z alertami, agent odczytuje dane telemetryczne, przegląda wykres obiektów K8, klasyfikuje hipotezy dotyczące głównych przyczyn i publikuje brief w Slacku z przyciskami zatwierdzania. Domyślnie tylko do odczytu. Każde leczenie kontrolowane przez człowieka. Podstawą jest ten agent, oceniony na podstawie 20 syntetycznych incydentów i porównany z agentem AWS w trzech wspólnych przypadkach.

**Typ:** Zwieńczenie
**Języki:** Python (agent), TypeScript (integracja ze Slackiem)
**Wymagania wstępne:** Faza 11 (inżynieria LLM), Faza 13 (narzędzia i MCP), Faza 14 (agenci), Faza 15 (autonomia), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P11 · P13 · P14 · P15 · P17 · P18
**Czas:** 30 godzin

## Problem

Narracja SRE na lata 2025–2026 brzmiała: „Agenci AI segregują incydenty, ludzie zatwierdzają środki zaradcze”. AWS DevOps Agent, Resolve AI, NeuBird, Metoro, PagerDuty AIOps dostarczają ten kształt w produkcji. Agent odczytuje metryki Prometheusa, logi Lokiego, ślady Tempo, metryki stanu kube i wykres wiedzy obiektów K8s. W mniej niż pięć minut generuje rankingową hipotezę dotyczącą przyczyny źródłowej wraz z cytatami telemetrycznymi. Nigdy nie wykonuje destrukcyjnych poleceń bez wyraźnej zgody człowieka za pośrednictwem Slacka.

Większość ciężkiej pracy to określanie zakresu i bezpieczeństwo, a nie rozumowanie. Agent potrzebuje domyślnej powierzchni RBAC tylko do odczytu, wzmocnionego serwera narzędzi MCP i dzienników audytu każdego rozważanego i wykonanego polecenia. Musi wiedzieć, kiedy wychodzi poza swoją głębokość i eskalować. Musi też działać na tyle tanio, aby kaskady zabijania OOM nie generowały rachunku agenta w wysokości 5 tys. dolarów.

## Koncepcja

Agent działa na grafie wiedzy. Węzły to obiekty K8 (pody, wdrożenia, usługi, węzły, HPA, PVC) oraz źródła telemetrii (seria Prometheus, strumienie Loki, ślady Tempo). Edges koduje własność (Pod -> Zestaw replik -> Wdrożenie), planowanie (Pod -> Węzeł) i obserwację (Pod -> Seria Prometheus). Wykres jest aktualizowany dzięki synchronizacji metryk stanu Kube i jest ponownie próbkowany przy każdym alercie.

Po uruchomieniu alertu agent wywołuje przyczyny główne z obiektu, którego dotyczy problem. Przechodzi przez krawędzie, pobiera odpowiednie wycinki telemetrii (ostatnie 15 minut) i formułuje hipotezę. Hipoteza jest uszeregowana według dowodów: ile cytatów z telemetrii ją potwierdza, jak niedawna, jak konkretna. Trzy najlepsze hipotezy trafiają do Slacka wraz z wizualizacjami ścieżek graficznych i przyciskami zatwierdzającymi działania naprawcze.

Remediacja jest zamknięta. Dozwolone akcje domyślne są tylko do odczytu. Destrukcyjne działania (zmniejszanie, wycofywanie, usuwanie Podów) wymagają zgody Slacka; Haki wycofywania ArgoCD wymagają tokenu uwierzytelniania, którego agent nigdy nie posiada. Dziennik audytu rejestruje każde polecenie *rozważone* przez agenta — a nie tylko wykonane — więc proces przeglądu wychwytuje przypadki, w których mogło dojść do chybienia.

## Architektura

```
PagerDuty / Alertmanager webhook
           |
           v
     FastAPI receiver
           |
           v
   LangGraph root-cause agent
           |
           +---- read-only MCP tools ----+
           |                             |
           v                             v
   K8s knowledge graph              telemetry slices
     (Neo4j / kuzu)              Prometheus, Loki, Tempo
   ownership + scheduling          last 15m, scoped
           |
           v
   hypothesis ranking (evidence weight)
           |
           v
   Slack brief + approval buttons
           |
           v (approved)
   ArgoCD rollback hook / PagerDuty escalate
           |
           v
   audit log: considered vs executed, every command
```

## Stos

- Źródła obserwowalności: Prometeusz, Loki, Tempo, kube-state-metrics
- Wykres wiedzy: Neo4j (zarządzany) lub kuzu (wbudowany) obiektów K8s + krawędzie telemetryczne
- Agent: LangGraph z listą dozwolonych dla poszczególnych narzędzi, domyślnie tylko do odczytu
- Transport narzędzi: FastMCP poprzez StreamableHTTP; oddzielny serwer dla destrukcyjnych narzędzi za bramą zatwierdzającą
- Modele: Claude Sonnet 4.7 do wnioskowania o przyczynach źródłowych, Gemini 2.5 Flash do podsumowania logów
- Naprawa: webhook przywracania ArgoCD, eskalacja PagerDuty, karta zatwierdzająca Slack
- Audyt: uporządkowany dziennik z możliwością dołączenia (rozpatrzony, wykonany, zatwierdzony, wynik)
- Wdrożenie: wdrożenie K8 z własną wąską rolą RBAC; osobna przestrzeń nazw

## Zbuduj to

1. **Przetwarzanie wykresów.** Synchronizuj metryki stanu kube z Neo4j/kuzu co 30 sekund. Węzły: Pod, wdrożenie, węzeł, usługa, PVC, HPA. Krawędzie: OWNED_BY, SCHEDULED_ON, EXPOSES, MOUNTS, SCALE. Krawędzie nakładki telemetrii: OBSERVED_BY (Pod jest obserwowany przez serię Prometheus).

2. **Odbiornik alertów.** Punkt końcowy FastAPI akceptujący webhooki PagerDuty lub Alertmanager. Wyodrębnij dotknięte obiekty i naruszenie SLO.

3. **Powierzchnia narzędzia tylko do odczytu.** Zawijaj kubectl, zapytanie Prometheus, Loki logql, Tempo traciql przez FastMCP. Każde narzędzie ma wąski czasownik RBAC („pobierz”, „lista”, „opisz”). Brak „delete”, „exec”, „scale” na domyślnym serwerze.

4. **Agent przyczyny pierwotnej.** LangGraph z trzema węzłami: `sample` pobiera wycinek telemetrii z ostatnich 15 minut, `walk` wysyła zapytania do wykresu pod kątem sąsiednich obiektów, `hypothesize` tworzy wersję roboczą rankingowych kandydatów będących przyczyną źródłową z cytatami telemetrycznymi.

5. **Ocena dowodów.** Każda hipoteza ma punktację = aktualność * specyficzność * odwrotność długości ścieżki wykresu * liczba cytowań. Wróć do góry-3.

6. **Krótka informacja o Slack.** Opublikuj załącznik zawierający hipotezę, wizualizację ścieżki wykresu (obraz podgrafu renderowany po stronie serwera) i przyciski zatwierdzania maksymalnie jednego działania zaradczego.

7. **Brama naprawcza.** Narzędzia destrukcyjne (zmniejszanie, przywracanie, usuwanie) znajdują się na drugim serwerze MCP za tokenem zatwierdzającym. Agent może do nich zadzwonić dopiero po zatwierdzeniu karty Slack przez człowieka.

8. **Dziennik audytu.** JSONL z możliwością dołączenia: dla każdego polecenia kandydującego zapisz, czy zostało ono uwzględnione, czy zostało wykonane i kto je zatwierdził. Wysyłka do S3 codziennie.

9. **Syntetyczny pakiet incydentów.** Zbuduj 20 scenariuszy: kaskada OOMKill, klapa DNS, thrash HPA, wypełnienie PVC, hałaśliwy sąsiad, wadliwy wózek boczny, złe wdrożenie ConfigMap, rotacja certyfikatów, wycofywanie obrazów itp. Oceń agenta pod względem dokładności przyczyny źródłowej i czasu oczekiwania na hipotezę.

## Użyj tego

```
webhook: alert.pagerduty.com -> checkout-api SLO breach, error rate 14%
[graph]   affected: Deployment checkout-api (3 Pods, Node ip-10-2-3-4)
[walk]    neighbors: ReplicaSet checkout-api-abc, Service checkout-api,
           recent rollout 14m ago
[sample]  prometheus error_rate 14%, up-trend; loki 500s on /api/v2/pay
[hypo]    #1 bad rollout: latest image checkout-api:v2.41 fails /healthz
          citations: deploy.yaml (rev 42), prometheus errorRate, loki 500 stack
[slack]   [ROLL BACK to v2.40]  [ESCALATE]  [IGNORE]
          (approval required; agent does not roll back unilaterally)
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-devops-agent.md`. Biorąc pod uwagę klaster K8 i źródło alertów, agent generuje rankingowe hipotezy dotyczące przyczyn źródłowych i przepływ środków zaradczych bramkowanych przez Slack.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Dokładność RCA w zestawie scenariuszy | ≥80% prawidłowej pierwotnej przyczyny w 20 syntetycznych incydentach |
| 20 | Bezpieczeństwo | Strażnik akcji niszczącej nigdy nie uruchamia się bez zgody Slacka w dzienniku audytu |
| 20 | Czas do postawienia hipotezy | p50 poniżej 5 minut od alertu do komunikatu Slack |
| 20 | Wyjaśnialność | Każda hipoteza ma ścieżki wykresów i cytaty telemetryczne |
| 15 | Kompletność integracji | PagerDuty, Slack, ArgoCD, Prometheus - kompleksowa praca |
| **100** | | |

## Ćwiczenia

1. Uruchom swojego agenta na tych samych trzech zdarzeniach, na których działa agent DevOps AWS. Opublikuj obok siebie. Zgłoś, gdzie agent się różni.

2. Dodaj audyt „prawie nietrafiony”, który oznacza każde polecenie *rozważone* przez agenta, które bez zatwierdzenia byłoby destrukcyjne. Zmierz wskaźnik sytuacji potencjalnie nietrafionych w ciągu jednego tygodnia.

3. Zamień model hipotezy z Claude Sonnet 4.7 na samodzielnie hostowaną Lamę 3.3 70B. Zmierz deltę dokładności RCA i dolara na incydent.

4. Zbuduj filtr przyczynowy: odróżnij skorelowane skoki telemetryczne od prawdziwej przyczyny źródłowej. Wytrenuj mały klasyfikator na podstawie etykiet zawierających 20 scenariuszy.

5. Dodaj próbę wycofywania zmian: wycofywanie ArgoCD względem klastra pomostowego z tym samym manifestem. Sprawdź plan wycofywania w aktywnym klastrze przed przyciskiem zatwierdzania Slack.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Wykres wiedzy K8 | „Wykres skupień” | Węzły = obiekty K8s + serie telemetryczne; krawędzie = własność, planowanie, obserwacja |
| Domyślnie tylko do odczytu | „RBAC o określonym zakresie” | Konto usługi agenta zawiera tylko czasowniki get/list/description; destrukcyjne czasowniki znajdują się na oddzielnym serwerze za zatwierdzeniem |
| Dziennik audytu | „Rozważone vs wykonane” | Dołącz tylko rekord każdego polecenia kandydującego, niezależnie od tego, czy zostało wykonane, kto zatwierdził |
| Ranking hipotez | „Wynik dowodów” | Aktualność × specyfika × odwrotność długości ścieżki wykresu × liczba cytowań |
| Karta zatwierdzenia luzu | „Brama HITL” | Interaktywny komunikat Slack z przyciskami korygującymi; agent nie może kontynuować, dopóki człowiek nie kliknie |
| Cytat z telemetrii | „Wskaźnik dowodowy” | Zapytanie Prometheusa, selektor Loki lub adres URL śledzenia Tempo, który obsługuje oświadczenie |
| MTTR | „Czas na rozwiązanie” | Zegar ścienny od alarmu pożarowego do odzyskiwania SLO |

## Dalsze czytanie

– [AWS DevOps Agent GA](https://aws.amazon.com/blogs/aws/aws-devops-agent-helps-you-accelerate-incident-response-and-improve-system-reliability-preview/) — kanoniczne odniesienie na rok 2026
— [Rozwiązywanie problemów z AI K8s](https://resolve.ai/blog/kubernetes-troubleshooting-in-resolve-ai) — odniesienie do konkurencji
- [Monitorowanie semantyczne NeuBird](https://www.neubird.ai) — podejście oparte na grafie semantycznym
- [Metoro AI SRE](https://metoro.io) — SLO – pierwsze kadrowanie produkcyjne
- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) — źródło stanu klastra
- [LangGraph](https://langchain-ai.github.io/langgraph/) — koordynator agenta referencyjnego
- [FastMCP](https://github.com/jlowin/fastmcp) — framework serwerowy Python MCP
- [Wycofanie ArgoCD](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_rollback/) — bramkowany cel zaradczy