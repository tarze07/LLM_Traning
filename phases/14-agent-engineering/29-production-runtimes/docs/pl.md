# Środowiska uruchomieniowe (Production Runtimes): Kolejki, Zdarzenia, Cron

> Agenty na produkcji działają w sześciu formach środowisk uruchomieniowych: żądanie-odpowiedź (request-response), przesyłanie strumieniowe (streaming), trwałe wykonywanie (durable execution), operacje w tle oparte na kolejkach (queue-based background), sterowane zdarzeniami (event-driven) i cykliczne (scheduled/cron). Wybierz formę, zanim wybierzesz framework. Obserwowalność jest kluczowa w każdej z nich.

**Typ:** Nauka
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 13 (LangGraph), Faza 14 · 22 (Głos)
**Czas:** ~60 minut

## Cele kształcenia

- Wymienienie sześciu form środowisk uruchomieniowych i dopasowanie każdej z nich do frameworka / wzorca produktu.
- Wyjaśnienie, dlaczego trwałe wykonywanie (LangGraph) ma znaczenie dla zadań długoterminowych.
- Opisanie środowiska uruchomieniowego sterowanego zdarzeniami oraz kiedy sprawdza się Claude Managed Agents.
- Wyjaśnienie tezy "obserwowalność jest kluczowa (load-bearing)" w odniesieniu do wieloetapowych agentów.

## Problem

Agenty na produkcji zawodzą w sposób, jakiego notatnik Jupyter nie ukazuje: przekroczenia limitu czasu w sieci przy 37. kroku, użytkownik rozłącza się w połowie połączenia głosowego, zadanie cron zostaje przerwane po restarcie maszyny, pracownik w tle wyczerpuje dostępną pamięć. Forma środowiska uruchomieniowego decyduje o tym, które z tych awarii można przetrwać.

## Koncepcja

### Żądanie-odpowiedź (Request-response)

- Synchroniczne zapytania HTTP. Użytkownik czeka na zakończenie zadania.
- Wykonalne tylko w przypadku krótkich zadań (<30s).
- Technologie: Agno (Python + FastAPI), Mastra (TypeScript + Express/Hono/Fastify/Koa).
- Obserwowalność: standardowe logi dostępu HTTP + ślady OTel (OTel spans).

### Przesyłanie strumieniowe (Streaming)

- SSE (Server-Sent Events) lub WebSocket do progresywnego dostarczania danych wyjściowych.
- LiveKit rozszerza to o standard WebRTC na potrzeby głosu i wideo (Lekcja 22).
- Technologie: dowolny framework z obsługą streamingu + frontend obsługujący SSE/WS.
- Obserwowalność: czas trwania poszczególnych fragmentów, opóźnienie wygenerowania pierwszego tokena, opóźnienie z długim ogonem (tail latency).

### Trwałe wykonywanie (Durable execution)

- Stan jest zapisywany w punktach kontrolnych (checkpointing) po każdym kroku; system wznawia pracę po wystąpieniu awarii.
- Model aktorowy AutoGen v0.4 izoluje awarie do poziomu jednego agenta (Lekcja 14).
- Główny wyróżnik LangGraph (Lekcja 13).
- Niezbędne, gdy liczba kroków jest nieznana, a koszt odzyskiwania sprawności jest wysoki.

### Oparte na kolejce / praca w tle (Queue-based / background)

- Zadanie trafia do kolejki, workerzy je podejmują, a wyniki wracają przez webhooki lub pub/sub.
- Niezbędne dla długoterminowych agentów (od kilkudziesięciu do setek kroków na zadanie, zgodnie z zapowiedziami funkcji obsługi komputera przez Anthropic).
- Technologie: Celery (Python), BullMQ (Node), SQS + Lambda (AWS), systemy niestandardowe (custom).
- Obserwowalność: wielkość kolejki, dystrybucja czasu wykonania danego zadania, rozmiar kolejki wiadomości niedoręczonych (DLQ).

### Sterowane zdarzeniami (Event-driven)

- Agenci subskrybują wyzwalacze (triggers): nowy e-mail, otwarcie PR (Pull Request), uruchomienie zaplanowanego zadania (cron).
- Rozwiązanie Claude Managed Agents zapewnia to od razu (Lekcja 17).
- CrewAI Flows (Lekcja 15) strukturyzuje oparte na zdarzeniach i deterministyczne przepływy pracy.
- Obserwowalność: źródło zdarzenia, opóźnienie między wystąpieniem zdarzenia a startem (event-to-start latency), opóźnienie pracy agenta (agent latency).

### Zaplanowane (Scheduled / Cron)

- Agenci w formie zadań typu cron, którzy uruchamiają się okresowo.
- Połącz z trwałym wykonywaniem (durable execution), tak aby niewykonany proces, odpalony w nocy został wznowiony przy następnym wyzwoleniu.
- Technologie: Kubernetes CronJob + trwały (durable) framework; wersje hostowane (Render cron, Vercel cron).

### Wzorce wdrażania z 2026 roku

- **CrewAI Flows** dla procesów sterowanych zdarzeniami na produkcji.
- **Agno** z bezstanowym FastAPI dla mikroserwisów w Pythonie.
- **Mastra** za pomocą adapterów serwerów (Express, Hono, Fastify, Koa) do osadzania w aplikacjach.
- **Pipecat Cloud / LiveKit Cloud** dla usług zarządzania głosem (Lekcja 22).
- **Claude Managed Agents** dla asynchronicznych operacji długoterminowych, hostowanych przez Anthropic.

### Obserwowalność jest kluczowa (load-bearing)

Bez funkcji OTel GenAI (OpenTelemetry w AI - Lekcja 23) oraz integracji z backendami Langfuse/Phoenix/Opik (Lekcja 24), nie jesteś w stanie skutecznie debugować wieloetapowego agenta, który uległ awarii w 40. kroku działania. Na produkcji takie mechanizmy nie są kwestią wyboru. To stanowi różnicę między "szybko diagnozujemy problemy" a "uruchamiamy i odtwarzamy zadanie od nowa z włączonym bardziej szczegółowym logowaniem".

### W czym upadają poszczególne rozwiązania uruchomieniowe

- **Błędny wybór formatu.** Wybór "żądanie-odpowiedź" dla zadania 5-minutowego. Użytkownicy w tym czasie kończą proces; procesy workerów się nawarstwiają; retransmisje się piętrzą.
- **Brak kolejki DLQ.** Uruchamianie agentów bez zapasowych mechanizmów wiadomości niedoręczonych (Dead-letter). W takiej sytuacji zgłoszenia ulegające niepowodzeniu zwyczajnie giną.
- **Niejawna praca w tle.** Agent działający w tle działa bez możliwości eksportowania śladów. Przez co, ewentualne awarie pozostają niewidoczne, dopóki użytkownicy nie zaczną ich zgłaszać.
- **Pominięcie zapisywania trwałego stanu (durable state).** Każde zadanie o czasie trwania > 30 sekund, gdzie nie możesz sobie pozwolić na restartowanie go od początku, z reguły wymaga trwałego wykonywania (durable execution).

## Zbuduj to

`code/main.py` jest wieloformatowym demo opartym na standardowej bibliotece:

- Punkt końcowy żądania-odpowiedzi (request-response) (zwykła funkcja).
- Handler odpowiadający za strumieniowanie (generator).
- Worker oparty na logice kolejkowej oraz mechanizmem DLQ.
- Rejestr wyzwalaczy wywoływanych przez zdarzenia (Event trigger registry).
- Harmonogram o budowie opartej na działaniu zadań chronologicznych (Cron-shaped scheduler).

Uruchom:

```bash
python3 code/main.py
```

Wynik: pięć śladów pokazujących zachowanie każdego środowiska podczas wykonywania dokładnie tego samego zadania. Kod i cała logika działania agenta jest ta sama w każdym przypadku, zmieniają się jedynie warunki zewnętrzne pracy. Wyjątkiem jest Trwałe Wykonywanie (durable execution), będące szóstym kształtem celowo zawartym i omawianym dokładniej w Lekcji 13 bazującej na checkpointowaniu systemu LangGraph.

## Użyj tego

- **Żądanie-odpowiedź (Request-response)** dla doświadczeń użytkownika w stylu komunikatora czatowego.
- **Przesyłanie strumieniowe (Streaming)** dla stopniowego wyświetlania zwrotnej odpowiedzi.
- **Trwałe (Durable)** dla zadań wieloetapowych i perspektywistycznych.
- **Kolejkowe (Queue)** przeznaczone do działań grupowych i asynchronicznych (bądź w perspektywie długoterminowej).
- **Zdarzenia (Event)** jako środek zapewnienia odpowiednich interakcji systemowych dla działania z agentem.
- **Harmonogram (Cron)** na rzecz mechanik pielęgnacyjnych typu rutynowego (konsolidacje wewnątrz pamięci, regularne zestawienia i przeglądy ogólne kosztów i inne operacje administracyjne).

## Wdróż to

`outputs/skill-runtime-shape.md` służy jako metoda wyboru optymalnej formy dla określonego zadania w zestawieniu z wdrożeniem i uaktywnieniem odpowiednich funkcji obserwacji.

## Ćwiczenia

1. Przeprowadź transformację swojej własnej wersji pętli ReAct (zobacz Lekcję 01) aby zastosować ją i sprawdzić każdy z wspomnianych tu sześciu sposobów w twoim środowisku pracy. Która forma pasuje do której funkcji aplikacji?
2. Zastosuj rozwiązanie typu wiadomości niedoręczonych, wdrażając DLQ we wbudowanym modelu w wersji kolejkowej. Następnie dokonaj i symuluj poziom opuszczanych zdarzeń jako obciążenie w skali 10 procent wskaźnika niepowodzeń i uwydatnij zjawisko przeładowywania i powiększania wielkości kolejki w ramach działania testowego.
3. Utwórz agenta bazującego na mechanice działania "cron", którego zadaniem operacyjnym będzie sprawdzanie, zestawianie danych na podstawie 20 najważniejszych działań podejmowanych podczas jednego dnia przez inne jednostki pracujące w środowisku sieciowym.
4. Załącz do procesu strumieniowania swoisty bufor ciśnienia zwrotnego (backpressure). Mechanizm ten ma dopuszczać do stanu polegającego na powstrzymaniu pracy agenta, jeżeli w określonym procesie zachodzą błędy typu nadmiernego spowolnienia na stacji klienta. W jaki sposób ten proces wchodzi w korelacje w konfrontacji z opóźnieniami w odniesieniu do przydzielanego na daną turę budżetu (turn budget)?
5. Zapoznaj się z zapisami dokumentacji odnoszącej się do modułu Claude Managed Agents. Zastanów się, w których fazach warto zrezygnować na jej rzecz z hostowania środowiska dedykowanego w przypadku korzystania z rozbudowanych i przedłużających w czasie operacyjnym podjęte zadania wieloetapowe.

## Kluczowe pojęcia

| Termin | Co mówią ludzie | Co to w rzeczywistości oznacza |
|------|----------------|------------------------|
| Żądanie-odpowiedź (Request-response) | "Synchroniczne" | Użytkownik czeka; zastosowanie tylko w przypadku krótkich zadań |
| Przesyłanie strumieniowe (Streaming) | "SSE / WS" | Odpowiedź przychodząca etapowo; zwiększenie wydajności (User Experience); możliwość weryfikacji i podglądu czasów dostarczenia, dla partii pakietowych |
| Trwałe wykonywanie (Durable execution) | "Wznawianie z błędów" | Środowisko dysponujące regularnym logowaniem zapisanego poziomu stanu kontrolnego; przy błędach można wznowić wykonanie zadania od momentu ostatniego bezpiecznego stanu jego zawartości |
| Oparte na kolejce (Queue-based) | "Zadania w tle" | Proces w którym biorą udział producent / zbiory serwerów pracowników (worker pool) / DLQ |
| Sterowane zdarzeniami (Event-driven) | "Oparte na wyzwalaczach" | Mechanika operacyjna agenta, opierająca się na uruchamianiu procesów wywołanych odrębnymi i zewnętrznymi zdarzeniami w czasie |
| DLQ | "Kolejka utraconych listów" | Baza awaryjna pełniąca rolę rezerwową na potrzeby zadań awaryjnych (Failed jobs) |
| Claude Managed Agents | "Hostowana uprząż" | Odnoszące się bezpośrednio do obsługi ze strony Anthropic, dedykowane opcje zarządzania opartymi z założenia w swym wymiarze, w głównej mierze rozbudowanymi wieloetapowymi zadaniami (z mechaniką cachowania, uwzględniając funkcje kompakcji ze strony serwera operacyjnego) |

## Dalsza lektura

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — informacje z zakresu funkcji wdrażania na podstawie koncepcji (Durable execution details)
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) — zestaw informacji o hostowanym trybie, do asynchronicznych i przedłużających się operacji czasowych
- [Anthropic, Introducing computer use](https://www.anthropic.com/news/3-5-models-and-computer-use) — "dozens-to-hundreds of steps per task"
- [AutoGen v0.4 (Microsoft Research)](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — wzorcowy model ukierunkowany na izolację uszkodzeń na poziomie samego agenta aktorowego