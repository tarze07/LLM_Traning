# Wzorce przepływu pracy Anthropic: proste ponad złożone

> Schluntz i Zhang (Anthropic, grudzień 2024) odróżniają przepływy pracy (predefiniowane ścieżki) od agentów (dynamiczne użycie narzędzi). Większość przypadków obejmuje pięć wzorców przepływu pracy. Zacznij od bezpośrednich wywołań API. Dodawaj agentów tylko wtedy, gdy nie można przewidzieć kroków.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć wzorców przepływu pracy firmy Anthropic: szybkie łączenie w łańcuch, routing, równoległość, koordynator-pracownicy, oceniający-optymalizator.
- Wyjaśnij rozróżnienie między agentem a przepływem pracy oraz koszty inżynieryjne każdego z nich.
- Określ, kiedy wybrać przepływ pracy zamiast agenta (i odwrotnie).
- Zaimplementuj wszystkie pięć wzorców w stdlib względem skryptowego LLM.

## Problem

W przypadku problemów wymagających pojedynczego wywołania funkcji zespoły sięgają po frameworki wieloagentowe. Koszt jest realny: frameworki dodają warstwy, które zasłaniają monity, ukrywają przepływ kontroli i powodują przedwczesną złożoność. Post Schluntza i Zhanga z grudnia 2024 r. jest najczęściej cytowaną krytyką branży: zacznij od prostych rozwiązań, dodawaj złożoność tylko wtedy, gdy będzie to opłacalne.

## Koncepcja

### Przepływy pracy a agenci

- **Przepływ pracy.** LLM i narzędzia zorganizowane za pomocą predefiniowanych ścieżek kodu. Inżynierowie są właścicielami wykresu.
- **Agent.** LLM dynamicznie kierują własnymi narzędziami i podejmują własne kroki. Model jest właścicielem wykresu.

Obydwa mają swoje miejsce. Przepływy pracy są tańsze, szybsze i łatwiejsze do debugowania. Agenci odblokowują otwarte problemy, ale utrudniają zrozumienie przyczyn awarii.

### Rozszerzony LLM

Podstawa wszystkich pięciu wzorców: jeden LLM z trzema wbudowanymi możliwościami — wyszukiwanie (odzyskiwanie), narzędzia (działania), pamięć (trwałość). Każde wywołanie API może z nich korzystać.

### Pięć wzorów

1. **Szybkie łączenie.** Dane wyjściowe wywołania 1 są wprowadzane do wywołania 2. Użyj, gdy zadanie ma czysty rozkład liniowy. Opcjonalne bramy programowe pomiędzy krokami.

2. **Routing.** Klasyfikator LLM wybiera dalszy LLM lub narzędzie, które ma wywołać. Używaj, gdy kategorycznie różne dane wejściowe wymagają innej obsługi (wsparcie poziomu 1 vs zwrot pieniędzy vs błąd vs sprzedaż).

3. **Równoległość.** Uruchom jednocześnie N wywołań LLM, zagreguj wyniki. Dwa kształty: dzielenie (różne fragmenty) i głosowanie (ten sam monit, N przebiegów, większość/synteza).

4. **Orkiestrator-pracownicy.** Orkiestrator LLM dynamicznie decyduje, których pracowników (także LLM) uruchomić i syntezuje ich wyniki. Podobnie jak pętle agentów, ale program Orchestrator nie wykonuje pętli w nieskończoność.

5. **Ewaluator-optymalizator.** Jeden LLM proponuje odpowiedź, inny LLM ją ocenia. Iteruj, aż osoba oceniająca przejdzie. Jest to uogólnione samodoskonalenie (lekcja 05).

### Tam, gdzie przepływ pracy przewyższa agentów

- **Przewidywalne zadania.** Jeśli potrafisz wyliczyć kroki, powinieneś to zrobić.
- **Zadania związane z kosztami.** Przepływy pracy mają ograniczoną liczbę kroków; agenci mogą się nakręcać.
- **Zadania związane ze zgodnością.** Audytorzy chcą czytać wykres, a nie wnioskować o nim na podstawie trajektorii.

### Gdzie agenci pokonują przepływy pracy

- **Badania otwarte.** Kiedy następny krok zależy od tego, co zwrócił ostatni krok.
- **Zadania o różnej długości.** Minuty lub godziny pracy, gdy liczba kroków jest nieznana.
- **Nowe domeny.** Jeśli nie znasz jeszcze odpowiedniego przepływu pracy — najpierw eksploracja, później kodyfikacja.

### Towarzysz inżynierii kontekstowej

„Efektywna inżynieria kontekstu dla agentów AI” (Anthropic 2025) formalizuje sąsiadującą dyscyplinę: okno 200 tys. to budżet, a nie kontener. Co uwzględnić, kiedy zagęścić, kiedy pozwolić na rozwój kontekstu. Omówiono szczegółowo w lekcji fazy 14 dotyczącej kompresji kontekstu (faza 14, wcześniejsza lekcja 06 w tym programie nauczania przed zmianą numeracji).

## Zbuduj to

`code/main.py` implementuje wszystkie pięć wzorców przepływu pracy w oparciu o `ScriptedLLM`:

- `prompt_chain(input, steps)` — sekwencyjne.
- `route(input, classifier, handlers)` — klasyfikacja + wysyłka.
- `parallel_vote(prompt, n, aggregator)` — N przebiegów, suma.
- `orchestrator_workers(task, workers)` — koordynator wybiera pracowników.
- `evaluator_optimizer(task, proposer, evaluator, max_iter)` — pętla aż do zaliczenia.

Uruchom to:

```
python3 code/main.py
```

Każdy wzór drukuje swój ślad. Całkowita liczba linii kodu na wzór wynosi ~10-15; koszt ramy mierzony jest w tysiącach.

## Użyj tego

- Bezpośrednie wywołania API dla większości zadań.
- Framework tylko wtedy, gdy wzorzec rzeczywiście wymaga trwałego stanu (LangGraph), współbieżności aktor-model (AutoGen v0.4) lub szablonów ról (CrewAI).
- Sięgnij po pakiet SDK Claude Agent, jeśli chcesz uzyskać kształt uprzęży Claude Code bez jej przebudowywania.

## Wyślij to

`outputs/skill-workflow-picker.md` wybiera odpowiedni wzorzec dla danego opisu zadania, łącznie z uzasadnieniem decyzji i ścieżką refaktoryzacji do agenta, jeśli przepływy pracy okażą się niewystarczające.

## Ćwiczenia

1. Zaimplementuj routing z progiem ufności. Poniżej progu -> eskaluj do człowieka. Gdzie znajduje się próg dla przypadku użycia pomocy technicznej poziomu 1?
2. Dodaj limit czasu do `parallel_vote`. Co się stanie, gdy jedno połączenie zostanie zawieszone? Jak agregować brakujące głosy?
3. Zmień `evaluator_optimizer` w bandytę: przechowuj 2 pierwsze wyniki w iteracjach, aby późny dobry wynik nie został nadpisany przez późnie zły.
4. Połącz szybkie tworzenie łańcuchów z routingiem: router wybiera jeden z trzech łańcuchów. Zmierz koszt tokena w porównaniu z pojedynczą alternatywą, która wymaga dużej podpowiedzi.
5. Wybierz jedną ze swoich funkcji produkcyjnych. Narysuj wykres przepływu pracy. Policz kroki. Czy agent rzeczywiście byłby tu lepszy?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Przepływ pracy | „Predefiniowany przepływ” | Własny przez inżyniera wykres LLM i wywołań narzędzi |
| Agent | „Autonomiczna sztuczna inteligencja” | Wykres będący własnością modelu; dynamiczny kierunek narzędzia |
| Rozszerzony LLM | „LLM z narzędziami” | LLM + wyszukiwanie + narzędzia + pamięć; jednostka atomowa |
| Szybkie łączenie | „Połączenia sekwencyjne” | Wyjście wywołania N jest wejściem wywołania N+1 |
| Trasowanie | „Wysłanie klasyfikatora” | Wybierz, który łańcuch/model obsługuje dane wejściowe |
| Równoległość | „Wachlować” | N równoczesnych połączeń; agreguj poprzez dzielenie lub głosowanie |
| Orkiestratorzy-pracownicy | „Agent dyspozytor” | Orchestrator LLM dynamicznie wybiera specjalistyczne LLM |
| Ewaluator-optymalizator | „Wnioskodawca + sędzia” | Iteruj, aż ewaluator przejdzie; Samodoskonalenie uogólnione |

## Dalsze czytanie

– [Anthropic, Building Effective Agents (grudzień 2024 r.)](https://www.anthropic.com/research/building-efektywne-agents) – pięć wzorców przepływu pracy
- [Antropiczna, efektywna inżynieria kontekstu dla agentów AI](https://www.anthropic.com/engineering/efektywna-context-engineering-for-ai-agents) — dyscyplina towarzysząca
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — gdy wykresy stanowe zarabiają
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — stworzony wzorzec Orchestrator-Workers