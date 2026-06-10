# Długo działający agenci w tle: trwałe wykonanie

> Wdrożeni produkcyjnie, długo działający agenci nie opierają się na zwykłych pętlach `while True`. Każde wywołanie LLM staje się rejestrowanym krokiem (działaniem/aktywnością) z punktem kontrolnym (checkpoint), obsługą ponownych prób oraz mechanizmem odtwarzania (replay). Integracja OpenAI Agents SDK z platformą Temporal (marzec 2026 r.) oraz Claude Code Routines (Anthropic) umożliwiają uruchamianie zaplanowanych zadań Claude Code bez konieczności utrzymywania stałego procesu lokalnego. Sesje są wstrzymywane, gdy wymagana jest decyzja człowieka, potrafią przetrwać restarty środowiska i wznawiają działanie od ostatniego punktu kontrolnego powiązanego z `thread_id`. Za tą nowoczesną ergonomią kryje się klasyczny wzorzec – orkiestracja przepływów pracy (workflow orchestration) – wzbogacona o jeden nowy element: traktowanie wywołań LLM jako operacji niedeterministycznych, które muszą być deterministycznie odtworzone po awarii.

**Typ:** Ucz się
**Języki:** Python (stdlib, minimalna maszyna stanowa o trwałym wykonaniu)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~60 minut

## Problem

Wyobraźmy sobie agenta realizującego zadanie przez cztery godziny. W tym czasie wywołuje on trzy narzędzia zewnętrzne, dwukrotnie prosi użytkownika o decyzję i wykonuje czterdzieści zapytań do LLM. W połowie pracy serwer, na którym uruchomiono agenta, zostaje zrestartowany. Co się wówczas dzieje?

- **W przypadku naiwnej pętli `while True`:** cały stan zostaje utracony. Zadanie startuje od zera. Trzy wywołania narzędzi (wywołujące realne efekty uboczne) są uruchamiane ponownie. Użytkownik musi powtórnie zatwierdzać te same decyzje, a koszty czterdziestu zapytań do LLM są naliczane od nowa.
- **W przypadku trwałego wykonania (durable execution):** proces wznawia działanie dokładnie od ostatniego punktu kontrolnego. Zakończone pomyślnie kroki nie są uruchamiane powtórnie – ich wyniki są odtwarzane z trwałego dziennika (event log). Użytkownik nie jest ponownie pytany o zatwierdzone już decyzje, a koszty wykonanych wcześniej zapytań LLM nie są generowane powtórnie.

Jest to ten sam wzorzec, który od lat oferują silniki przepływów pracy (takie jak Temporal, Cadence czy Cherami od Ubera). Nowością jest to, że wywołania LLM są tu traktowane jako specyficzny rodzaj aktywności (activity) – niedeterministyczny, kosztowny i obarczony ryzykiem błędów – który idealnie wpisuje się w tę architekturę.

Kluczowy temat tej lekcji to spadek niezawodności agentów w długim horyzoncie czasowym (organizacja METR zaobserwowała tzw. „35-minutową degradację” – wskaźnik sukcesu zadań spada niemal kwadratowo wraz z wydłużaniem czasu pracy). Trwałe wykonanie umożliwia realizację zadań trwających dłużej niż pozwala na to podstawowy profil niezawodności agenta. Stanowi to nową metodę bezpiecznej obsługi awarii (graceful degradation) przy prawidłowo zaprojektowanym systemie, ale może być źródłem zagrożeń w przypadku błędów projektowych.

## Koncepcja

### Aktywności, przepływy pracy i powtórki

- **Przepływ pracy (Workflow):** Deterministyczny kod odpowiedzialny za orkiestrację. Definiuje sekwencję kroków, rozgałęzienia logiki oraz warunki oczekiwania. Musi być całkowicie deterministyczny, aby można go było wiernie odtworzyć z dziennika zdarzeń bez rozbieżności w stanie aplikacji.
- **Aktywność (Activity):** Niedeterministyczna, podatna na błędy jednostka pracy. Może to być zapytanie LLM, wywołanie zewnętrznego narzędzia, zapis pliku lub żądanie HTTP. Każda aktywność jest rejestrowana w logach wraz ze swoimi parametrami wejściowymi oraz (po zakończeniu) zwróconym wynikiem.
- **Dziennik zdarzeń (Event Log):** Trwały magazyn danych (storage). Rejestruje każde uruchomienie, zakończenie, błąd, ponowną próbę oraz każdą decyzję podjętą w ramach przepływu pracy.
- **Odtwarzanie (Replay):** Po odzyskaniu stanu po awarii kod przepływu pracy jest uruchamiany ponownie od początku. Każda aktywność, która została już pomyślnie zakończona, zwraca swój uprzednio zarejestrowany wynik bez ponownego wykonywania kodu. W efekcie fizycznie uruchamiane są tylko te kroki, które nie zostały sfinalizowane przed awarią.

Zasada ta jest analogiczna do ponownego renderowania w React na podstawie Virtual DOM lub odtwarzania stanu drzewa roboczego w Git na podstawie historii commitów. Determinizm kodu orkiestrującego sprawia, że utrzymanie trwałości stanu jest wyjątkowo efektywne.

### Dlaczego połączenia LLM pasują do wzorca

Połączenia LLM to:
- Niedeterministyczny (temperatura > 0; nawet temperatura 0 zmienia się w zależności od wersji modelu).
- Drogie (pieniądze i opóźnienia).
- Potencjalna awaria (limity szybkości, przekroczenia limitu czasu).
- Efekt uboczny (jeśli wywołują narzędzia).

To jest dokładnie profil działalności. Zawijanie każdego wywołania LLM jako działania umożliwia ponowną próbę z wykładniczym wycofywaniem, punktami kontrolnymi przy ponownym uruchomieniu i odtwarzalnym śladem na potrzeby debugowania.

### Punkty kontrolne powiązane z `thread_id`

Frameworki takie jak LangGraph, Microsoft Agent Framework, Cloudflare Durable Objects czy Claude Code Routines korzystają z ujednoliconego wzorca API: parametr `thread_id` (lub jego odpowiednik) identyfikuje konkretną sesję. Każda zmiana stanu jest zapisywana w bazie danych (domyślnie PostgreSQL, SQLite w środowiskach deweloperskich lub Redis jako pamięć podręczna). Po awarii system automatycznie odczytuje stan z ostatniego zapisanego punktu kontrolnego (checkpoint).

Wybór bazy danych ma kluczowe znaczenie:

- **PostgreSQL:** Trwały, obsługujący zapytania SQL, odporny na restarty i wdrożenia nowej wersji aplikacji. Jest to domyślne rozwiązanie dla LangGraph.
- **SQLite:** Przeznaczony głównie do celów deweloperskich; nie zapewnia synchronizacji danych przy pracy wielohostowej.
- **Redis:** Bardzo szybki, ale z natury ulotny (in-memory), chyba że skonfigurowano mechanizmy AOF/RDB (migawki).
- **Cloudflare Durable Objects:** Wygodny, rozproszony magazyn danych powiązany z unikalnym kluczem, zdolny do przechowywania stanu sesji przez wiele godzin lub tygodni.

### Udział człowieka jako element pierwszego stopnia (First-class Citizen)

Wzorzec „zaproponuj, a następnie zatwierdź” (omawiany w Lekcji 15) wymaga wdrożenia trwałego stanu „oczekiwania na decyzję człowieka”. Przepływ pracy jest wówczas wstrzymywany, zewnętrzne kolejki przechowują oczekujące zgłoszenia, a po autoryzacji proces rusza dalej dokładnie od momentu zatrzymania. Bez trwałego wykonania realizacja takich pauz opiera się jedynie na próbach utrzymania procesu w tle (best-effort); z nim – zatwierdzenie może nastąpić nawet po wielu godzinach bez ryzyka utraty kontekstu.

### Zjawisko 35-minutowej degradacji

Badania organizacji METR wskazują, że niezawodność niemal każdej klasy agentów spada drastycznie po około 35 minutach ciągłej pracy. Dwukrotne wydłużenie czasu trwania zadania wiąże się z około czterokrotnym wzrostem liczby błędów. Trwałe wykonanie nie eliminuje samych błędów modeli, lecz pozwala procesowi trwać dłużej niż wynikałoby to z podstawowych limitów stabilności. Bezpieczne podejście wymaga łączenia trwałego wykonania z wymogiem ponownej autoryzacji człowieka (HITL) po wznowieniu procesu oraz z limitami budżetowymi (patrz Lekcja 13), które kontrolują zużycie zasobów niezależnie od czasu rzeczywistego.

### Kiedy trwałe wykonanie NIE jest zalecane?

- Krótkie zadania (trwające poniżej kilku minut) niewymagające udziału człowieka. Narzut architektoniczny przewyższa tu potencjalne korzyści.
- Operacje pobierania danych (retrieval) przeznaczone wyłącznie do odczytu.
- Zadania, w których poprawność wyniku zależy od przetworzenia całości problemu w ramach jednego okna kontekstowego (np. niektóre zadania logiczne lub generowanie treści za jednym podejściem).

## Uruchomienie kodu

Skrypt `code/main.py` implementuje uproszczony silnik trwałego wykonania z użyciem biblioteki standardowej Pythona. Zawiera on:

- Dekorator `@activity`, który zapisuje parametry wejściowe i wyjściowe kroków w dzienniku zdarzeń w formacie JSON.
- Funkcję orkiestrującą przepływ pracy (workflow).
- Funkcję `run_or_replay(workflow, event_log)`, która odtwarza zakończone kroki bez ich ponownego uruchamiania.

Kod testowy symuluje proces składający się z trzech kroków, celowo wywołuje błąd w trakcie pracy i porównuje: (a) naiwne ponowne uruchomienie całego zadania od zera z (b) odtworzeniem stanu (replay), które wykonuje jedynie brakujący krok.

## Zadanie wdrożeniowe

Plik `outputs/skill-durable-execution-review.md` służy do weryfikacji proponowanego wdrożenia długo działającego agenta pod kątem poprawności architektury trwałego wykonania. Ocenie podlegają: podział na aktywności, determinizm przepływu, konfiguracja bazy danych dla punktów kontrolnych oraz zasady wznawiania sesji i autoryzacji przez człowieka (HITL).

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Zurtóć uwagę na różnicę w liczbie wykonanych kroków pomiędzy tradycyjnym uruchomieniem od zera a mechanizmem odtwarzania stanu. Zmień punkt wystąpienia awarii i zaobserwuj wpływ na proces odtwarzania.
2. Zmodyfikuj przykładowy silnik tak, aby jawnie wykorzystywał parametr `thread_id`. Symuluj dwie równoległe sesje i upewnij się, że ich dzienniki zdarzeń nie kolidują ze sobą.
3. Wprowadź czynnik niedeterministyczny (np. pobieranie aktualnego czasu systemowego wewnątrz funkcji przepływu pracy). Zademonstruj rozbieżność stanów podczas odtwarzania sesji. Wyjaśnij, jak profesjonalne silniki radzą sobie z tym wyzwaniem (rejestrowanie efektów ubocznych, używanie funkcji typu `Workflow.now()`).
4. Przeczytaj artykuł LangChain pt. „The Runtime Behind Production Deep Agents”. Wypisz wszystkie stany, które muszą być trwale zapisywane przez środowisko uruchomieniowe, i wskaż, jakie scenariusze awarii są dzięki temu zabezpieczane.
5. Zapoznaj się z zasadami tworzenia punktów kontrolnych dla zadania automatycznego kodowania zaplanowanego na 6 godzin. W których momentach należy zapisać stan? Jak powinien wyglądać powrót do pracy po awarii i które kroki bezwzględnie wymagają ponownej autoryzacji człowieka (HITL)?

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Przepływ pracy (Workflow) | „Scenariusz agenta” | Deterministyczny kod odpowiedzialny za orkiestrację; odtwarzalny na podstawie dziennika zdarzeń |
| Aktywność (Activity) | „Krok” | Niedeterministyczna jednostka pracy (np. zapytanie LLM, wywołanie API); logowana przed i po wykonaniu |
| Dziennik zdarzeń (Event Log) | „Baza stanów” | Trwały zapis każdej zmiany stanu i wywołania aktywności w systemie |
| Odtwarzanie (Replay) | „Wznowienie” | Ponowne uruchomienie przepływu pracy, w którym zakończone kroki zwracają zapamiętany wynik |
| Punkt kontrolny (Checkpoint) | „Punkt zapisu” | Trwały stan procesu przypisany do konkretnego thread_id; podstawa do wznowienia pracy |
| thread_id | „Klucz sesji” | Unikalny identyfikator pozwalający na jednoznaczne powiązanie trwałego stanu sesji |
| 35-minutowa degradacja | „Spadek niezawodności” | Zjawisko opisane przez METR: wskaźnik sukcesu zadań spada wraz z czasem ich trwania |
| Niedeterminizm | „Rozbieżność w powtórce” | Czynniki zmienne (czas, losowość, wyjście z LLM), które muszą być rejestrowane jako skutek uboczny |

## Dalsza lektura

- [Anthropic — Claude Code Agent SDK: pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — budżety, kroki i wznawianie sesji.
- [Microsoft — Agent Framework: human-in-the-loop i punkty kontrolne](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — struktura zdarzenia RequestInfoEvent.
- [LangChain — The Runtime Behind Production Deep Agents](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) — specyficzne wymagania dla środowisk uruchomieniowych agentów.
- [OpenAI Agents SDK + integracja z Temporal (Trigger.dev)](https://trigger.dev) — obsługa aktywności w wywołaniach LLM.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — analiza zjawiska 35-minutowej degradacji.
