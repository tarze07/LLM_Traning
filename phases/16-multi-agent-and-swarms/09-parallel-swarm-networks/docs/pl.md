# Architektury równoległe / rojowe / sieciowe

> W przeciwieństwie do przełożonego: brak centralnego decydora. Agenci czytają współdzieloną magistralę zdarzeń, podejmują pracę asynchronicznie i zapisują wyniki. LangGraph wyraźnie obsługuje „architekturę roju” dla zdecentralizowanych, dynamicznych środowisk. Matrix (arXiv:2511.21686) reprezentuje zarówno kontrolę, jak i przepływ danych w postaci serializowanych komunikatów przekazywanych przez rozproszone kolejki w celu wyeliminowania wąskiego gardła koordynatora. Kompromis jest wyraźny: determinizm i identyfikowalność w celu zapewnienia skalowalności. Rój dopasowuje zadania z wieloma niezależnymi podproblemami; nie pasuje do zadań wymagających jednego, spójnego planu.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `threading`, `queue`)
**Wymagania wstępne:** Faza 16 · 05 (Wzorzec Nadzorcy), Faza 16 · 04 (Model Prymitywny)
**Czas:** ~75 minut

## Problem

Przełożony ogranicza się do kilku pracowników. A co z setkami? Sam przełożony staje się wąskim gardłem: każda decyzja o tym, kto co robi, odbywa się za pośrednictwem jednego agenta. Jeden powolny krok planu blokuje cały system.

Architektury roju odwracają uwagę od projektu. Zamiast przydzielania pracy przez centralnego planistę, pracownicy wybierają zadania ze wspólnej kolejki. „Koordynacja” jest wbudowana w semantykę magistrali zdarzeń. Brak orkiestratora; system skaluje się, dopóki nie zrobi tego kolejka.

## Koncepcja

### Kształt

```
                ┌──── shared queue ────┐
                │                      │
       ┌────────┼────────┐  ◄──────┬───┘
       ▼        ▼        ▼         │
     Worker  Worker  Worker   Worker
      A       B       C        D
       │        │        │         │
       └────────┴────────┴─────────┘
                 │
                 ▼
            results pool
```

Żadnego orkiestratora. Każdy pracownik powtarza: wyciągnij zadanie, przeprowadź proces, zapisz wynik (i opcjonalnie kolejkuj dalsze działania).

### Kiedy rój się zmieści

- **Wiele niezależnych zadań.** Skrobanie, przekształcanie, klasyfikacja. Zadania nie są od siebie zależne.
- **Praca o zmiennym czasie trwania.** Jeśli niektóre zadania zajmują 100 ms, a inne 10 s, rój automatycznie równoważy obciążenie — szybcy pracownicy wykonują kolejne zadania. Przełożony musi przewidzieć czas trwania.
- **Przepustowość ponad determinizm.** Zależy Ci na całkowitym czasie realizacji, a nie na ścisłym zamawianiu.

### Gdy rój zawiedzie

- **Uporządkowane przepływy pracy.** Jeśli krok 3 wymaga wyników kroku 2, rój ryzykuje odpaleniem w kroku 3 przed wykonaniem kroku 2.
- **Zadania planu globalnego.** Złożone pytania badawcze korzystają z pomocy planisty. Rój badaczy tworzy niezależne fakty, a nie spójny raport.
- **Debugowanie.** Bez centralnego dziennika i pracy asynchronicznej odtworzenie błędu jest kosztowne.

### Matryca (arXiv:2511.21686)

Matrix to publikacja z 2025 r., która prowadzi rój do naturalnego wniosku: zarówno przepływ sterowania, jak i przepływ danych to serializowane komunikaty w rozproszonych kolejkach. Brak centralnego koordynatora. Tolerancja na błędy wynika z trwałości komunikatów. Skalowalność jest problemem brokera komunikatów, a nie systemu.

Wkład: model programowania, w którym koordynacja wielu agentów polega na tym, „jaki temat wiadomości subskrybuje ten agent?” zamiast „którego agenta następnie wybiera przełożony?” Dzięki temu system wygląda jak siatka zdarzeń pub/sub.

### Architektura roju LangGrapha

Dokumentacja LangGraph 2025 wyraźnie opisuje „architekturę roju” jako jeden ze wzorców wieloagentowych: agenci są węzłami, ale krawędzie tworzą ukierunkowany graf z cyklami, a dowolny węzeł można aktywować z puli. Pracownik wybiera spośród dostępnych prac według stanu, a nie przypisania przełożonego.

### Tryb awarii: głód i plamienie na gorąco

Jeśli wszyscy pracownicy wykonają najszybsze dostępne zadanie, długotrwałe zadania nigdy nie zostaną wybrane, dopóki nie pozostaną jedynymi. Klasyczny głód w kolejce.

Środki łagodzące:
- Kolejki priorytetowe z wyraźnym przedawnieniem (zwiększ priorytet wraz z czasem oczekiwania).
- Specjalizacja pracowników: niektórzy pracownicy podejmują się jedynie „długich” zadań.
- Przeciwciśnienie: ogranicz liczbę szybkich zadań umieszczanych w kolejce.

### Łącze routingu oparte na zawartości

Rój naturalnie łączy się w pary z routingiem opartym na treści (Lekcja 22). Zamiast kolejki ogólnej, dla każdego typu komunikatu należy utworzyć jedną kolejkę. Pracownicy wyspecjalizowani subskrybują tylko swój typ. Stanowi to podstawę architektur magistrali komunikatów, które można skalować do tysięcy agentów.

## Zbuduj to

`code/main.py` implementuje rój 4 wątków roboczych pobierających ze współdzielonego `queue.Queue`. Zadania mają zmienny czas trwania (niektóre szybkie, inne wolne). Demo kontrastuje:

- **Sekwencyjny poziom bazowy:** jeden pracownik przetwarza wszystkie zadania szeregowo.
- **Stałe przypisanie:** każde zadanie przydzielone wcześniej konkretnemu pracownikowi (w stylu przełożonego).
- **Rój:** pracownicy pobierają się ze wspólnej kolejki.

Rój automatycznie równoważy obciążenie; stałe przypisanie pozostawia szybkich pracowników bezczynnych, gdy przydzielone im zadanie jest wolne.

Uruchom:

```
python3 code/main.py
```

Dane wyjściowe pokazują liczbę zadań na pracownika (rój rozkłada się nierównomiernie, ale optymalnie) i czasy zegara ściennego.

## Użyj tego

`outputs/skill-swarm-fit.md` ocenia, czy zadanie powinno używać roju czy nadzorcy. Dane wejściowe: niezależność zadań, wariancja czasu trwania, wymagania dotyczące kolejności, potrzeby w zakresie debugowalności.

## Wyślij to

Lista kontrolna:

- **Kolejka priorytetowa ze starzeniem się.** Zapobiegaj głodowi przy długich zadaniach.
- **Idempotencja procesu roboczego.** Zadanie może zostać pobrane więcej niż raz, jeśli proces roboczy ulegnie awarii w połowie jego działania. Pracownicy muszą być idempotentni.
- **Trwała kolejka.** Do produkcji używaj Kafki, strumieni Redis lub kolejki opartej na bazie danych. `queue.Queue` znajduje się tylko w pamięci.
- **Obserwowalność na zadanie.** Każde zadanie ma identyfikator śledzenia; każdy dziennik roboczy zaczyna się od niego/kończy.
- ** Przeciwciśnienie.** Jeśli kolejka rośnie szybciej, niż pracownicy ją wyczerpują, spowolnij producenta.

## Ćwiczenia

1. Uruchom `code/main.py`. O ile szybszy jest rój niż sekwencyjny przy obciążeniu o zmiennym czasie trwania? O ile szybciej niż stałe przypisanie?
2. Dodaj wariant kolejki priorytetowej (użyj `queue.PriorityQueue`). Przypisz priorytet według pola „ważność” zadania. Zaobserwuj, czy zadania o niskim priorytecie nie ulegają kiedykolwiek głodowi pod ciągłym obciążeniem.
3. Zastosuj detektor gorących punktów: zarejestruj, kiedy dowolny pracownik wykona 3 razy więcej zadań niż najwolniejszy pracownik. Co to oznacza w odniesieniu do rozkładu czasu trwania zadań?
4. Przeczytaj streszczenie artykułu Matrix (arXiv:2511.21686) i sekcję 3. Zidentyfikuj jeden konkretny kompromis, który Matrix akceptuje (wzrost skalowalności) i ten, z którego rezygnuje (możliwość śledzenia, determinizm).
5. Przekonwertuj demo roju, aby korzystało z `queue.Queue` krotek (task_type, payload), przy czym pracownicy subskrybują tylko określone typy. Jakie reguły routingu mają sens, gdy zadania są heterogeniczne?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Architektura roju | „Agenci zdecentralizowani” | Pracownicy wycofują się ze wspólnej kolejki; brak centralnego koordynatora. |
| Autobus eventowy | „Agenci subskrybują tematy” | Broker komunikatów, który kieruje zadania do procesów roboczych według typu lub treści. |
| Głód | „Zadanie nigdy nie jest uruchamiane” | Zadanie o niskim priorytecie nigdy nie jest wybierane, ponieważ zadania o wyższym priorytecie napływają w sposób ciągły. |
| Hot-spotting | „Jeden robotnik tonie” | Nierównowaga obciążenia, gdy jeden pracownik otrzymuje większość zadań. |
| Przeciwciśnienie | „Zwolnij producenta” | Mechanizm sygnalizujący podmiotowi nadrzędnemu zaprzestanie produkcji, gdy kolejka się zapełni. |
| Idempotentny pracownik | „Bezpieczne ponowne uruchomienie” | Zadanie przetworzone dwukrotnie daje ten sam wynik. Wymagane, ponieważ procesy robocze mogą ulec awarii w trakcie wykonywania. |
| Trwała kolejka | „Przetrwa awarie” | Kolejka obsługiwana przez dysk lub replikowaną pamięć masową; zadania nie są tracone w przypadku awarii pracownika. |
| Struktura macierzy | „Pełny rój przekazujący wiadomości” | Zarówno przepływ danych, jak i kontroli to serializowane komunikaty w rozproszonych kolejkach. |

## Dalsze czytanie

- [Przepływy pracy i agenci LangGraph — Architektura roju](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — jawna obsługa roju
- [Matrix — zdecentralizowana struktura dla systemów wieloagentowych] (https://arxiv.org/abs/2511.21686) — pełny rój przekazujący wiadomości
- [Inżynieria antropiczna — dlaczego nadzorca nie jest rojem w badaniach](https://www.anthropic.com/engineering/multi-agent-research-system) — dlaczego konkretny system produkcyjny wyraźnie wybrał nadzorcę zamiast roju
- [Dokumentacja modelu aktora AutoGen v0.4](https://microsoft.github.io/autogen/stable/) — przepisanie aktora sterowanego zdarzeniami, bliżej roju niż GroupChat w wersji 0.2