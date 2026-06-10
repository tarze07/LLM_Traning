# Architektury równoległe, rojowe i sieciowe

> W przeciwieństwie do wzorca nadzorcy, w architekturach rojowych brak jest centralnego koordynatora. Agenci odczytują zdarzenia ze wspólnej szyny (event bus), asynchronicznie pobierają zadania do realizacji i zapisują wyniki z powrotem. LangGraph wprost wspiera tzw. architekturę roju (swarm architecture) na potrzeby zdecentralizowanych i dynamicznych środowisk. Projekt Matrix (arXiv:2511.21686) reprezentuje przepływ sterowania oraz przepływ danych w postaci serializowanych komunikatów przesyłanych przez rozproszone kolejki w celu wyeliminowania wąskiego gardła, jakim bywa centralny orkiestrator. Kompromis jest wyraźny: poświęcamy determinizm i łatwość śledzenia (traceability) na rzecz wybitnej skalowalności. Architektura rojowa sprawdza się w zadaniach składających się z wielu niezależnych podproblemów; nie nadaje się do procesów wymagających jednego, spójnego planu globalnego.

**Typ:** Ucz się + Buduj  
**Języki:** Python (stdlib, `threading`, `queue`)  
**Wymagania wstępne:** Faza 16 · 05 (Wzorzec nadzorcy), Faza 16 · 04 (Model prymitywny)  
**Czas:** ~75 minut  

## Problem

Wzorzec nadzorcy ogranicza skalowalność systemu do najwyżej kilku pracowników. Przy setkach agentów centralny planista sam staje się wąskim gardłem: każda decyzja o podziale i przydziale zadań przechodzi przez jeden model LLM, a pojedyncze, opóźnione wywołanie blokuje działanie całego potoku.

Architektury rojowe wywracają tradycyjne podejście do projektowania do góry nogami. Zamiast przydzielać zadania z poziomu centralnego orkiestratora, pozwalamy pracownikom (Workers) samodzielnie pobierać zadania ze wspólnej kolejki. Koordynacja jest tutaj wbudowana bezpośrednio w semantykę szyny zdarzeń. Brak centralnego planisty sprawia, że system skaluje się tak daleko, jak pozwala na to sama przepustowość kolejki.

## Koncepcja

### Struktura roju

```
                 ┌─── współdzielona kolejka ───┐
                 │                              │
        ┌────────┼────────┐           ◄─────┬───┘
        ▼        ▼        ▼                 │
     Worker   Worker   Worker            Worker
       A        B        C                 D
        │        │        │                 │
        └────────┴────────┴─────────────────┘
                 │
                 ▼
          pula rezultatów
```

W systemie nie ma orkiestratora. Każdy pracownik działa w pętli: pobiera zadanie z kolejki, przetwarza je, zapisuje wynik (i opcjonalnie wrzuca kolejne podzadania do kolejki).

### Kiedy architektura rojowa się sprawdza

- **Wiele niezależnych zadań.** Procesy takie jak skrobanie stron (scraping), transformacja danych czy klasyfikacja tekstów. Zadania te nie zależą od siebie nawzajem.
- **Zróżnicowany czas wykonania (variable duration).** Jeśli część zadań zajmuje 100 ms, a część 10 s, rój automatycznie bilansuje obciążenie (load balancing) — szybcy pracownicy sprawnie rozładowują kolejkę, podczas gdy inni przetwarzają wolniejsze wątki. Nadzorca miałby ogromne trudności z przewidzeniem tych czasów.
- **Priorytet przepustowości nad determinizmem.** Liczy się całkowity czas przetworzenia zbioru zadań, a nie sztywna kolejność ich wykonywania.

### Kiedy rój się nie sprawdza

- **Przepływy o ścisłej sekwencyjności.** Jeśli krok 3 bezwzględnie wymaga danych z kroku 2, w roju istnieje ryzyko uruchomienia kroku 3 przed zakończeniem kroku 2.
- **Zadania wymagające planu globalnego.** Złożone procesy badawcze potrzebują planisty. Rój niezależnych badaczy wygeneruje zbiór luźnych faktów, a nie spójny raport końcowy.
- **Trudność debugowania.** Przy braku centralnego rejestru zdarzeń i w pełni asynchronicznej pracy odtworzenie i zdiagnozowanie konkretnego błędu jest bardzo kosztowne.

### Projekt Matrix (arXiv:2511.21686)

Matrix to publikacja z 2025 roku, która rozwija architekturę rojową do logicznego końca: zarówno dane, jak i sterowanie są przesyłane jako serializowane komunikaty w rozproszonych kolejkach. Odporność na awarie (fault tolerance) wynika z trwałości wiadomości w kolejce. Skalowanie staje się problemem warstwy transportowej (brokera komunikatów), a nie logiki aplikacyjnej agentów.

Kluczowy wniosek: koordynacja w systemie wieloagentowym sprowadza się do pytania: „Jakie tematy (topics) subskrybuje ten agent?”, zamiast: „Którego agenta orkiestrator powinien wywołać jako następnego?”. System zaczyna przypominać klasyczną szynę zdarzeń w architekturze pub/sub.

### Architektura roju w LangGraph

Dokumentacja LangGraph z 2025 roku klasyfikuje architekturę roju jako jeden z fundamentalnych wzorców wieloagentowych: agenci są węzłami, ale krawędzie tworzą skierowany graf z cyklami, a dowolny węzeł może być aktywowany bezpośrednio z puli zadań. Pracownicy pobierają zadania na podstawie stanu systemu, a nie decyzji nadzorcy.

### Tryby awarii: głód zadań (starvation) oraz punkty przeciążenia (hot-spotting)

Jeśli wszyscy pracownicy będą wybierać najszybsze i najprostsze zadania z kolejki, długotrwałe i trudne wątki mogą nigdy nie zostać zrealizowane (zjawisko głodu w kolejkach).

Metody łagodzenia:
- Kolejki priorytetowe z mechanizmem starzenia zadań (zwiększanie priorytetu w miarę upływu czasu oczekiwania).
- Specjalizacja pracowników: dedykowanie części agentów wyłącznie do obsługi długich zadań.
- Mechanizmy pushbacku (backpressure) ograniczające liczbę zadań szybkich w kolejce.

### Routing oparty na treści (Content-Based Routing)

Rój doskonale współgra z routingiem opartym na treści (lekcja 22). Zamiast jednej ogólnej kolejki, tworzy się osobne kolejki dla konkretnych typów komunikatów. Wyspecjalizowani agenci subskrybują wyłącznie te kolejki, które odpowiadają ich kompetencjom. To fundament szyn komunikatów skalowalnych do tysięcy agentów.

## Zbuduj to

W pliku `code/main.py` zaimplementowano rój składający się z 4 wątków roboczych pobierających dane ze współdzielonej kolejki `queue.Queue`. Zadania mają zróżnicowany czas wykonania. Demo porównuje:
- **Potok sekwencyjny:** jeden pracownik przetwarza wszystkie zadania po kolei.
- **Sztywny przydział:** każde zadanie jest z góry przypisane do konkretnego agenta (styl nadzorcy).
- **Rój:** pracownicy dynamicznie pobierają zadania z jednej wspólnej kolejki.

Rój automatycznie bilansuje obciążenie, podczas gdy sztywny przydział sprawia, że szybcy pracownicy czekają bezczynnie, gdy przypisane im zadanie okazuje się powolne.

Uruchomienie:

```
python3 code/main.py
```

W logach wyświetli się statystyka wykonanych zadań per wątek (rój rozkłada obciążenie optymalnie, choć nierównomiernie) oraz całkowity czas wykonania dla każdego z trzech wariantów.

## Użyj tego

W pliku `outputs/skill-swarm-fit.md` zdefiniowano umiejętność służącą do oceny, czy dla danego typu zadania należy wdrożyć architekturę rojową, czy wzorzec nadzorcy. Narzędzie bada stopień niezależności zadań, zmienność czasu wykonania, wymogi dotyczące kolejności procesów oraz potrzeby debugowania.

## Wyślij to

Lista kontrolna przed wdrożeniem architektury rojowej:

- **Kolejka priorytetowa ze starzeniem zadań (aging).** Zapobiega blokowaniu i głodzeniu trudnych zadań.
- **Idempotentność pracowników.** Agent musi działać w sposób idempotentny — jeśli ulegnie awarii w trakcie pracy, zadanie zostanie pobrane przez innego wykonawcę i przetworzone ponownie, co nie może uszkodzić stanu systemu.
- **Trwałość kolejki (Persistence).** W środowisku produkcyjnym korzystaj z systemów takich jak Kafka, strumienie Redis czy RabbitMQ. Biblioteka `queue.Queue` działa wyłącznie w pamięci operacyjnej (in-memory) i nie chroni danych przed restartem.
- **Śledzenie zadań (Tracing).** Każde zadanie musi posiadać unikalny identyfikator korelacji (correlation ID) przenoszony w logach każdego agenta.
- **Kontrola przeciążenia (Backpressure).** Jeśli kolejka rośnie zbyt szybko, wdróż mechanizmy spowalniające producentów zadań.

## Ćwiczenia

1. Uruchom `code/main.py`. O ile szybszy okazał się rój w porównaniu do potoku sekwencyjnego? O ile szybszy w porównaniu do sztywnego przydziału zadań?
2. Zmodyfikuj kod, wprowadzając kolejkę priorytetową (`queue.PriorityQueue`). Przypisz zadaniom priorytety i zaobserwuj, czy pod stałym obciążeniem zadania o niskim priorytecie nie ulegają zjawisku głodu.
3. Zaimplementuj detektor punktów przeciążenia (hot-spots): wygeneruj alert, gdy jeden z pracowników wykona 3-krotnie więcej zadań niż najwolniejszy agent. O czym to świadczy w kontekście rozkładu zadań?
4. Przeczytaj sekcję 3 publikacji Matrix (arXiv:2511.21686). Wskaż kompromisy tego rozwiązania: co zyskano (skalowalność), a z czego zrezygnowano (determinizm, śledzenie stanu).
5. Przekształć demo roju tak, aby kolejka przesyłała krotki `(task_type, payload)`, a agenci subskrybowali wyłącznie określone typy zadań. Zaprojektuj reguły routingu dla tak zróżnicowanego środowiska.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Architektura roju | „Zdecentralizowani agenci” | Wzorzec, w którym pracownicy samodzielnie pobierają zadania ze wspólnej kolejki bez udziału centralnego koordynatora. |
| Szyna zdarzeń (Event Bus) | „Broker wiadomości” | Warstwa pośrednicząca, która kieruje zadania do agentów na podstawie typu wiadomości lub jej treści. |
| Głód zadań (Starvation) | „Zadanie wisi” | Sytuacja, w której zadania o niskim priorytecie oczekują w nieskończoność, wypierane przez nowe zadania o wyższym priorytecie. |
| Punkty przeciążenia | „Hot-spotting” | Nierównomierne obciążenie systemu, w którym jeden agent przejmuje większość zadań, stając się wąskim gardłem. |
| Kontrola przeciążenia | „Backpressure” | Sygnalizowanie systemom nadzorującym konieczności spowolnienia generowania zadań, gdy kolejka jest pełna. |
| Idempotentność | „Bezpieczne ponowne próby” | Właściwość gwarantująca, że wielokrotne wykonanie tego samego zadania przez agenta da tożsamy wynik. |
| Trwała kolejka | „Kolejka dyskowa” | System przechowywania zadań (np. Kafka), który chroni dane przed utratą w przypadku awarii węzła. |
| Wzorzec Matrix | „Rój pub/sub” | Architektura, w której całe sterowanie oraz przepływ danych są realizowane asynchronicznie przez szynę wiadomości. |

## Dalsze czytanie

- [LangGraph: Swarm Architecture](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — oficjalne wsparcie dla architektury roju.
- [Matrix: A Decentralized Framework for Multi-Agent Systems](https://arxiv.org/abs/2511.21686) — opis zdecentralizowanej komunikacji asynchronicznej.
- [Anthropic Engineering: Multi-Agent Systems](https://www.anthropic.com/engineering/multi-agent-research-system) — uzasadnienie wyboru nadzorcy zamiast roju w systemach badawczych.
- [AutoGen: Actor Model](https://microsoft.github.io/autogen/stable/) — opis modelu aktorskiego sterowanego zdarzeniami w wersji v0.4.
