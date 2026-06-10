# Długo działający agenci w tle: trwałe wykonanie

> Agenci produkcyjni długoterminowi nie działają w `while True`. Każde połączenie LLM staje się działaniem z punktem kontrolnym, ponowną próbą i powtórką. Integracja pakietu SDK dla agentów OpenAI w firmie Temporal została wdrożona w marcu 2026 r. Claude Code Routines (Anthropic) uruchamia zaplanowane wywołania Claude Code bez trwałego procesu lokalnego. Sesje wstrzymują się po wejściu człowieka, przeżywają wdrożenie i wznawiają od ostatniego punktu kontrolnego wpisanego przez `thread_id`. Za nową ergonomią kryje się stary wzorzec — orkiestracja przepływu pracy — z jednym nowym wkładem: wywołania LLM jako działania niedeterministyczne, które należy deterministycznie odtworzyć po powrocie do zdrowia.

**Typ:** Ucz się
**Języki:** Python (stdlib, minimalna maszyna stanowa o trwałym wykonaniu)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~60 minut

## Problem

Rozważmy agenta działającego przez cztery godziny. Wywołuje trzy narzędzia, dwukrotnie pyta użytkownika i wykonuje czterdzieści wywołań LLM. W połowie host, na którym działa, uruchamia się ponownie. Co się dzieje?

- W naiwnej pętli `while True`: wszystko stracone. Bieg rozpoczyna się od zera. Trzy wywołania narzędzi (z rzeczywistymi efektami ubocznymi) są wykonywane ponownie. Użytkownik jest ponownie pytany o rzeczy, które już zatwierdził. Czterdzieści połączeń LLM jest ponownie rozliczanych.
- W przypadku trwałego wykonania: bieg zostaje wznowiony od ostatniego punktu kontrolnego. Czynności już zakończone nie są powtarzane; ich wyniki są odtwarzane z trwałego dziennika. Użytkownik nie zatwierdza ponownie rzeczy, które już zatwierdził. Już wykonane połączenia LLM nie są ponownie rozliczane.

Jest to ten sam wzór, który silniki przepływu pracy dostarczają od dziesięciu lat (Temporal, Cadence, Cherami firmy Uber). Nowością jest to, że wywołania LLM są obecnie rodzajem działania – niedeterministycznym, kosztownym, niosącym ze sobą skutki uboczne – i doskonale wpasowują się w ten schemat.

Temat przewodni lekcji: spadek niezawodności w długim horyzoncie czasowym (METR obserwuje „35-minutową degradację” — wskaźnik sukcesu spada mniej więcej kwadratowo wraz z horyzontem). Trwałe wykonanie umożliwia przebiegi dłuższe niż obsługuje profil niezawodności, co stanowi nowy sposób na bezpieczną awarię, jeśli projekt jest dobry, i niebezpieczny, jeśli projekt jest błędny.

## Koncepcja

### Aktywności, przepływy pracy i powtórki

- **Przepływ pracy**: deterministyczny kod orkiestracji. Definiuje sekwencję działań, rozgałęzienia, oczekiwania. Musi być deterministyczny, aby można go było odtworzyć z dziennika zdarzeń bez zaskakujących rozbieżności.
- **Działanie**: niedeterministyczna, potencjalnie wadliwa jednostka pracy. Wywołanie LLM, wywołanie narzędzia, zapis pliku, żądanie HTTP. Każde działanie jest rejestrowane wraz z danymi wejściowymi i (po zakończeniu) wynikami.
- **Dziennik zdarzeń**: trwały magazyn zapasowy. Rejestrowane jest każde rozpoczęcie, zakończenie, niepowodzenie, ponowna próba i każda decyzja dotycząca przepływu pracy.
- **Powtórka**: po odzyskaniu kod przepływu pracy jest uruchamiany ponownie od początku; każde działanie, które zostało już zakończone, zwraca zarejestrowany wynik bez ponownego wykonywania. W rzeczywistości uruchamiane są tylko działania, które nie zostały zakończone.

Jest to ten sam kształt, co ponowne renderowanie Reacta w wirtualnym DOM lub Git przebudowujący działające drzewo na podstawie zatwierdzeń. Determinizm w orkiestratorze sprawia, że ​​trwałość jest tania.

### Dlaczego połączenia LLM pasują do wzorca

Połączenia LLM to:
- Niedeterministyczny (temperatura > 0; nawet temperatura 0 zmienia się w zależności od wersji modelu).
- Drogie (pieniądze i opóźnienia).
- Potencjalna awaria (limity szybkości, przekroczenia limitu czasu).
- Efekt uboczny (jeśli wywołują narzędzia).

To jest dokładnie profil działalności. Zawijanie każdego wywołania LLM jako działania umożliwia ponowną próbę z wykładniczym wycofywaniem, punktami kontrolnymi przy ponownym uruchomieniu i odtwarzalnym śladem na potrzeby debugowania.

### Punkty kontrolne oznaczone przez `thread_id`

LangGraph, Microsoft Agent Framework, Cloudflare Durable Objects i Claude Code Routines są zbieżne w tym samym kształcie API: `thread_id` (lub odpowiednik) identyfikuje sesję; każde przejście stanu jest zachowywane w backendie (domyślnie PostgreSQL, SQLite dla deweloperów, Redis dla pamięci podręcznej); CV odczytuje najnowszy punkt kontrolny.

Wybór backendu ma znaczenie:

- **PostgreSQL**: trwały, z możliwością zapytań, przetrwa wdrożenie. Wartość domyślna dla LangGraph.
- **SQLite**: tylko dla programistów lokalnych; traci dane na wszystkich hostach.
- **Redis**: szybki, ale efemeryczny, chyba że skonfigurowano AOF/migawkę.
- **Obiekty trwałe Cloudflare**: dystrybuowane w sposób przejrzysty; objęty unikalnym kluczem; przetrwa wiele godzin lub tygodni.

### Wkład człowieka jako stan najwyższej klasy

Zaproponuj, a następnie zatwierdź (lekcja 15) wymaga trwałego stanu „oczekiwania na człowieka”. Przepływ pracy zostaje wstrzymany, kolejka zewnętrzna przechowuje oczekujące żądanie, a zatwierdzanie zostaje wznowione dokładnie od tego momentu. Bez trwałości jest to najlepszy wysiłek; dzięki niemu zatwierdzenie przychodzi z dnia na dzień, a przepływ pracy rozpoczyna się rano.

### 35-minutowa degradacja

METR zaobserwował, że każda zmierzona klasa agenta wykazuje spadek niezawodności powyżej ~35 minut ciągłej pracy. Podwojenie czasu trwania zadania zwiększa mniej więcej czterokrotnie wskaźnik niepowodzeń. Trwałe wykonanie tego nie rozwiązuje; pozwala pracować dłużej niż pozwala na to profil niezawodności. Bezpieczny wzorzec polega na połączeniu trwałości z punktami kontrolnymi, które wymagają świeżego HITL przy ponownym wejściu, oraz z przełącznikami budżetowymi (lekcja 13), które ograniczają całkowitą moc obliczeniową niezależnie od czasu zegara ściennego.

### Gdy trwałe wykonanie jest złą odpowiedzią

- Działa krócej niż kilka minut bez udziału człowieka. Koszty ogólne > korzyść.
- Pobieranie informacji wyłącznie do odczytu.
- Zadania, w których poprawność wymaga kompleksowego rozwiązania w jednym oknie kontekstowym (niektóre zadania związane z rozumowaniem; niektóre generowanie jednorazowe).

## Użyj tego

`code/main.py` implementuje minimalny silnik o trwałym wykonaniu w stdlib Python. Obsługuje:

- Dekorator `@activity`, który rejestruje wejścia i wyjścia w dzienniku zdarzeń JSON.
- Funkcja przepływu pracy, która sekwencjonuje działania.
- Funkcja `run_or_replay(workflow, event_log)`, która odtwarza zakończone działania bez ich ponownego wykonywania.

Sterownik symuluje przepływ pracy składający się z trzech czynności, ulega awarii w połowie i pokazuje (a) naiwną ponowną próbę ponownego wykonania wszystkiego w porównaniu z (b) powtórką uruchamiającą tylko brakującą czynność.

## Wyślij to

`outputs/skill-durable-execution-review.md` sprawdza proponowane długoterminowe wdrożenie agenta pod kątem prawidłowego kształtu trwałego wykonania: działań, determinizmu, zaplecza punktu kontrolnego, stanu wprowadzania danych przez człowieka i polityki HITL-on-resume.

## Ćwiczenia

1. Uruchom `code/main.py`. Obserwuj różnicę w liczbie wykonanych działań między naiwnymi ponawianiami i powtórkami. Zmień punkt awarii i pokaż odpowiednio zmiany liczby powtórek.

2. Przekonwertuj silnik zabawki, aby jawnie używał `thread_id`. Symuluj dwie równoczesne sesje korzystające z silnika i upewnij się, że ich dzienniki zdarzeń nie kolidują ze sobą.

3. Wykonaj jedno działanie w silniku zabawki. Wprowadź niedeterminizm (sygnał czasowy zegara ściennego w decyzji dotyczącej przepływu pracy). Zademonstruj rozbieżność w powtórce. Wyjaśnij, jak radzą sobie z tym rzeczywiste silniki (rejestracja efektów ubocznych, interfejsy API `Workflow.now()`).

4. Przeczytaj post LangChain „Środowisko wykonawcze za agentami produkcyjnymi”. Wypisz każdy stan, w którym utrzymuje się środowisko wykonawcze, i nazwij, który tryb awarii obejmuje każdy z nich.

5. Zaprojektuj politykę punktów kontrolnych dla 6-godzinnego zadania autonomicznego kodowania. Gdzie masz punkt kontrolny? Jak wygląda wznowienie po awarii? Co wymaga świeżego HITL-a?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Przepływ pracy | „Scenariusz agenta” | Deterministyczny kod orkiestracji; odtwarzalne z dziennika zdarzeń |
| Aktywność | „Krok” | Jednostka niedeterministyczna (wywołanie LLM, wywołanie narzędzia); zalogowany przed i po |
| Dziennik zdarzeń | „Sklep zapasowy” | Trwały zapis każdej zmiany stanu |
| Odtwórz ponownie | „Wznów” | Uruchom ponownie przepływ pracy; zakończone działania zwracają zarejestrowane wyniki bez ponownego wykonywania |
| Punkt kontrolny | "Zapisz punkt" | Stan utrwalony kluczowany przez thread_id; najnowsze wygrane w CV |
| identyfikator_wątku | „Klucz sesji” | Identyfikator obejmujący stan trwały |
| 35-minutowa degradacja | „Spadek niezawodności” | METR: wskaźnik sukcesu spada ~kwadratowo wraz z horyzontem |
| Niedeterminizm | „Drift podczas powtórki” | Zegar ścienny, losowy, wyjście LLM; musi być zarejestrowany jako skutek uboczny |

## Dalsze czytanie

- [Anthropic — Claude Code Agent SDK: pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — semantyka budżetu, obrotów i wznowienia.
- [Microsoft — Agent Framework: human-in-the-loop i punkty kontrolne](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — kształt RequestInfoEvent.
- [LangChain — The Runtime Behind Production Deep Agents](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) — konkretne wymagania dotyczące czasu działania.
- [OpenAI Agents SDK + integracja czasowa (ogłoszenie Trigger.dev)](https://trigger.dev) — kształt aktywności dla wywołań LLM.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — odniesienie do 35-minutowej degradacji.