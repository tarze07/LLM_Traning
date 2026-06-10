---

name: devops-agent
description: Zbuduj agenta rozwiązywania problemów Kubernetes, który przegląda wykres wiedzy o klastrze, ocenia główne przyczyny i bramkuje każde rozwiązanie za pośrednictwem Slacka.
version: 1.0.0
phase: 19
lesson: 06
tags: [capstone, devops, sre, kubernetes, langgraph, fastmcp, aiops]

---

Mając klaster K8s i źródło alertów (PagerDuty lub Alertmanager), zbuduj agenta, który generuje rankingowe hipotezy dotyczące przyczyn źródłowych w czasie krótszym niż pięć minut i zatwierdza każde rozwiązanie za pomocą karty zatwierdzającej Slack.

Plan budowy:

1. Pobieraj kube-state-metrics do Neo4j lub kuzu co 30 sekund. Utwórz wykres podów, wdrożeń, usług, węzłów, PVC, HPA oraz krawędzi nakładki telemetrii do źródeł Prometheus, Loki i Tempo.
2. Przygotuj odbiornik webhooka FastAPI dla PagerDuty i Alertmanager.
3. Udostępnij narzędzia tylko do odczytu poprzez FastMCP z transportem StreamableHTTP: kubectl get/describe, promql, logql, traciql.
4. Zbuduj agenta przyczyny źródłowej LangGraph z trzema węzłami: `sample` (telemetria ściągania 15 m), `walk` (sąsiedzi grafu przechodzącego), `hypothesize` (uszereguj kandydatów według aktualności × specyficzności × liczby cytowań).
5. Opublikuj 3 najwyżej ocenione hipotezy z wizualizacją ścieżki graficznej w serwisie Slack za pomocą przycisków zatwierdzania.
6. Umieść destrukcyjne narzędzia (skalowanie, wycofywanie zmian, usuwanie) na oddzielnym serwerze FastMCP za tokenem zatwierdzającym, który agent uzyskuje dopiero po podpisaniu Slack.
7. Prowadź dziennik audytu przeznaczony tylko do dodawania: każde *rozważone* polecenie, czy zostało zatwierdzone, czy zostało wykonane, kto zatwierdził.
8. Stwórz 20 syntetycznych scenariuszy incydentów (OOMKill, klapa DNS, thrash HPA, wypełnienie PVC, hałaśliwy sąsiad, uszkodzony wózek boczny, złe wdrożenie ConfigMap, rotacja certyfikatów, wycofanie pobrania obrazu, awaria sondy i 10 innych). Agent oceniający dokładność RCA i czas do postawienia hipotezy.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Dokładność RCA w zestawie scenariuszy | Co najmniej 80% prawidłowej pierwotnej przyczyny w 20 syntetycznych incydentach |
| 20 | Bezpieczeństwo | Strażnik akcji niszczącej nigdy nie uruchamia się bez zgody Slacka w dzienniku audytu |
| 20 | Czas do postawienia hipotezy | p50 poniżej 5 minut od alertu do komunikatu Slack |
| 20 | Wyjaśnialność | Każda hipoteza ma ścieżki wykresów i cytaty telemetryczne |
| 15 | Kompletność integracji | PagerDuty, Slack, ArgoCD, Prometheus - kompleksowa praca |

Twarde odrzucenia:

- Agenci z pojedynczym serwerem MCP, który łączy w sobie narzędzia tylko do odczytu i narzędzia destrukcyjne.
- Dowolne RCA wyprodukowane bez cytatów telemetrycznych. Niecytowane hipotezy należy odrzucić.
- Dzienniki audytu, które rejestrują tylko wykonania. Muszą rejestrować każde rozważane polecenie.
- Twierdzenia dotyczące dokładności bez uruchamiania agenta w zestawie 20 scenariuszy z nasionami.

Zasady odmowy:

- Odmów podjęcia działań naprawczych bez zgody Slacka od osoby dzwoniącej. Nawet jeśli hipoteza jest oczywista.
- Odmawiaj ujawniania `kubectl exec`, `kubectl port-forward` lub jakiegokolwiek narzędzia interaktywnego za pośrednictwem MCP tylko do odczytu. Działają destrukcyjnie.
- Odmawiaj zbiorczego stosowania środków zaradczych w wielu wdrożeniach bez kart zatwierdzających dla każdego wdrożenia.

Dane wyjściowe: repozytorium zawierające odbiornik FastAPI, agenta LangGraph, serwery MCP tylko do odczytu i destrukcyjne, integrację ze Slack, zestaw testów obejmujących 20 scenariuszy, bezpośrednie porównanie z agentem AWS DevOps w przypadku trzech wspólnych incydentów oraz zapis poleceń, które mogły się nie udać (co agent *rozważał*, ale nie wykonał) w ciągu tygodniowego okna obserwacji.