# Wzorce przepływu pracy Anthropic: proste ponad złożone

> Schluntz i Zhang (Anthropic, grudzień 2024) odróżniają przepływy pracy (workflow - predefiniowane ścieżki) od agentów (dynamiczne korzystanie z narzędzi). Większość wdrożeń można opisać za pomocą pięciu podstawowych wzorców. Zaleca się rozpoczynanie od bezpośrednich wywołań API i wprowadzanie agentów dopiero wtedy, gdy kolejnych kroków nie da się przewidzieć.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć wzorców przepływu pracy (workflows) według Anthropic: łączenie w łańcuchy (prompt chaining), routing, równoległość (parallelization), koordynator-pracownicy (orchestrator-workers) oraz ewaluator-optymalizator (evaluator-optimizer).
- Wyjaśnij różnice pomiędzy agentem a predefiniowanym przepływem pracy oraz koszty inżynieryjne związane z każdym z tych podejść.
- Określ, kiedy wybrać przepływ pracy zamiast agenta (i odwrotnie).
- Zaimplementuj wszystkie pięć wzorców w czystym Pythonie (stdlib) przy użyciu mockowanego/skryptowego LLM.

## Problem

Zespoły często sięgają po złożone frameworki wieloagentowe nawet do stosunkowo prostych problemów. Niesie to ze sobą realne koszty: frameworki dodają warstwy abstrakcji, które zaciemniają prompty, ukrywają przepływ sterowania i prowadzą do przedwczesnej złożoności (overengineering). Publikacja Schluntza i Zhanga z grudnia 2024 r. to jedna z najważniejszych krytyk takiego podejścia w branży: należy zaczynać od prostych rozwiązań i wprowadzać złożoność tylko wtedy, gdy przynosi ona realne korzyści.

## Koncepcja

### Przepływy pracy a agenci

- **Przepływ pracy (Workflow).** LLM i narzędzia połączone z góry zdefiniowanymi ścieżkami w kodzie. To programista (inżynier) kontroluje graf przepływu.
- **Agent.** LLM dynamicznie decyduje o doborze narzędzi i kolejnych krokach działania. To model zarządza grafem przepływu.

Oba podejścia mają swoje zastosowanie. Przepływy pracy są tańsze, szybsze i łatwiejsze w debugowaniu. Agenci sprawdzają się w zadaniach o charakterze otwartym (open-ended), jednak znacznie trudniej jest analizować przyczyny ich błędów.

### Rozszerzony LLM (Augmented LLM)

Podstawa wszystkich pięciu wzorców: pojedynczy LLM rozbudowany o trzy podstawowe możliwości – pobieranie danych (retrieval), narzędzia (actions) oraz pamięć (persistence). Każde wywołanie API może korzystać z tych funkcji.

### Pięć wzorców

1. **Łączenie w łańcuchy (Prompt Chaining).** Dane wyjściowe z pierwszego wywołania stanowią wejście do kolejnego. Stosowane, gdy zadanie można podzielić na liniowe etapy. Pomiędzy krokami można wdrożyć opcjonalną walidację programistyczną.

2. **Routing.** Klasyfikator oparty na LLM decyduje, który model lub narzędzie wywołać w następnej kolejności. Stosowany, gdy zróżnicowane dane wejściowe wymagają zupełnie innej obsługi (np. wsparcie techniczne vs zwrot kosztów vs zgłoszenie błędu vs sprzedaż).

3. **Równoległość (Parallelization).** Równoległe uruchomienie N zapytań do LLM i agregacja ich wyników. Występuje w dwóch wariantach: podział zadania (różne podzadania wykonywane jednocześnie) oraz głosowanie (ten sam prompt uruchomiony N-krotnie w celu uzyskania konsensusu lub syntezy).

4. **Orkiestrator-pracownicy (Orchestrator-Workers).** LLM pełniący rolę koordynatora decyduje o uruchomieniu wyspecjalizowanych modeli (pracowników) i syntetyzuje ich wyniki. Działa podobnie do pętli agentowej, ale orkiestrator ma jasno określone warunki zakończenia i nie działa w nieskończoność.

5. **Ewaluator-optymalizator (Evaluator-Optimizer).** Jeden model (optymalizator) generuje propozycję rozwiązania, a drugi (ewaluator) ją ocenia. Iteracja trwa do momentu pozytywnej oceny. Jest to uogólniony wzorzec samodoskonalenia (Lekcja 05).

### Gdzie przepływ pracy przewyższa agentów

- **Przewidywalne zadania.** Jeśli potrafisz z góry zdefiniować kolejne kroki, powinieneś to zrobić w kodzie.
- **Kontrola kosztów.** Przepływy pracy mają z góry ograniczoną liczbę kroków, podczas gdy agenci mogą wpaść w nieskończone pętle generujące wysokie koszty.
- **Wymogi zgodności (compliance).** Audytorzy wolą analizować predefiniowany graf przepływu w kodzie niż rekonstruować zachowanie agenta na podstawie jego logów (trajektorii).

### Gdzie agenci pokonują przepływy pracy

- **Zadania otwarte (open-ended).** Kiedy wybór kolejnego kroku zależy bezpośrednio od nieprzewidywalnych wyników poprzedniego.
- **Zmienna liczba kroków.** Procesy trwające od minut do godzin, w których liczba kroków jest z góry nieznana.
- **Nowe domeny.** Kiedy optymalny przepływ pracy nie jest jeszcze znany – w takich przypadkach najpierw stosuje się eksplorację agentową, a dopiero później kodyfikuje się ją w sztywny przepływ.

### Efektywne zarządzanie kontekstem

„Effective context engineering for AI agents” (Anthropic 2025) definiuje powiązaną dyscyplinę: okno kontekstowe o rozmiarze 200k to budżet, który należy optymalizować, a nie pojemnik do bezmyślnego zapełniania. Określa ono, jakie informacje włączyć, kiedy je kompresować, a kiedy pozwolić kontekstowi rosnąć (szczegółowo omówione w lekcji dotyczącej kompresji kontekstu w Fazie 14).

## Zbuduj to

Plik `code/main.py` implementuje wszystkie pięć wzorców przepływu pracy przy użyciu klasy `ScriptedLLM`:

- `prompt_chain(input, steps)` — sekwencyjne przetwarzanie.
- `route(input, classifier, handlers)` — klasyfikacja i przekierowanie.
- `parallel_vote(prompt, n, aggregator)` — równoległe zapytania i agregacja.
- `orchestrator_workers(task, workers)` — dynamiczny dobór i koordynacja zadań.
- `evaluator_optimizer(task, proposer, evaluator, max_iter)` — iteracyjna optymacja do momentu walidacji.

Uruchomienie:

```
python3 code/main.py
```

Uruchomienie każdego wzorca generuje logi wykonania. Napisanie każdego wzorca wymaga zaledwie ok. 10-15 linii kodu; narzut złożoności przy wprowadzaniu dużych frameworków jest nieporównywalnie wyższy.

## Użyj tego

- Stosuj bezpośrednie wywołania API w większości standardowych zadań.
- Sięgaj po frameworki tylko wtedy, gdy rozwiązanie wymaga trwałego zarządzania stanem (LangGraph), współbieżności w modelu aktora (AutoGen v0.4) lub gotowych szablonów ról (CrewAI).
- Skorzystaj z Claude Agent SDK, jeśli chcesz wdrożyć mechanizmy znane z Claude Code bez konieczności ich samodzielnego tworzenia od podstaw.

## Wyślij to

Plik `outputs/skill-workflow-picker.md` dobiera odpowiedni wzorzec na podstawie opisu zadania, dostarczając uzasadnienie decyzji oraz określając ścieżkę refaktoryzacji do pełnego agenta, jeśli statyczne przepływy pracy okażą się niewystarczające.

## Ćwiczenia

1. Zaimplementuj routing z progiem pewności (confidence threshold). Jeśli pewność klasyfikacji jest poniżej progu – skieruj sprawę do konsultanta. Jak ustaliłbyś ten próg dla automatycznej obsługi zgłoszeń pierwszej linii?
2. Dodaj limit czasu (timeout) do `parallel_vote`. Co powinno się stać, gdy jedno z zapytań ulegnie zawieszeniu? W jaki sposób agregować głosy w przypadku brakujących wyników?
3. Zmodyfikuj `evaluator_optimizer`, aby zapamiętywał najlepsze dotychczasowe wyniki (np. top-2 warianty). Zapobiegnie to sytuacji, w której późniejsza, słabsza iteracja nadpisze lepszy wypracowany wcześniej wynik.
4. Połącz routing z łączeniem w łańcuchy: router kieruje zapytanie do jednego z trzech wyspecjalizowanych łańcuchów. Porównaj koszt tokenów z pojedynczym, rozbudowanym promptem obsługującym wszystkie przypadki.
5. Wybierz jeden z rzeczywistych procesów w swoim projekcie. Rozrysuj jego graf przepływu i policz kroki. Czy zastosowanie pełnego agenta zamiast statycznego przepływu przyniosłoby tu realne korzyści?

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Przepływ pracy (Workflow) | „Predefiniowana ścieżka” | Zdefiniowany przez programistę graf wywołań LLM i narzędzi |
| Agent | „Autonomiczny asystent” | Graf przepływu kontrolowany dynamicznie przez sam model LLM |
| Rozszerzony LLM (Augmented LLM) | „LLM wyposażony w narzędzia” | Połączenie LLM z pobieraniem danych, narzędziami i pamięcią; podstawowa jednostka systemu |
| Łączenie w łańcuchy (Prompt Chaining) | „Sekwencyjne zapytania” | Dane wyjściowe z kroku N stają się danymi wejściowymi kroku N+1 |
| Routing | „Przekierowanie” | Wybór odpowiedniej ścieżki wykonania na podstawie klasyfikacji zapytania |
| Równoległość (Parallelization) | Współbieżność (fan-out) | N równoległych zapytań; agregacja przez podział zadań lub głosowanie |
| Orkiestrator-pracownicy | „Koordynator i wykonawcy” | Model orkiestratora dynamicznie przydziela podzadania wyspecjalizowanym modelom wykonawczym |
| Ewaluator-optymalizator | „Twórca i krytyk” | Iteracyjna poprawa rozwiązania do momentu uzyskania pozytywnej oceny od ewaluatora |

## Dalsze czytanie

- [Anthropic, Building Effective Agents (grudzień 2024)](https://www.anthropic.com/research/building-effective-agents) — opis pięciu podstawowych wzorców przepływu pracy
- [Anthropic, Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — najlepsze praktyki zarządzania oknem kontekstowym
- [Dokumentacja LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — tworzenie zaawansowanych grafów stanowych
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — oficjalna implementacja wzorca Orkiestrator-Pracownicy
