# Handoffy i procedury — orkiestracja bezstanowa

> OpenAI Swarm (październik 2024 r.) uprościł orkiestrację wieloagentową do dwóch podstawowych elementów: **procedur** (instrukcji i narzędzi w promptu systemowym) oraz **handoffów** (przekazań sterowania, realizowanych jako wywołanie narzędzia zwracającego innego agenta). Brak tu maszyn stanów czy skomplikowanych języków DSL — LLM kieruje przepływem poprzez wywoływanie odpowiednich narzędzi przekazania. Pakiet SDK OpenAI Agents (marzec 2025 r.) to produkcyjny następca tej idei. Sam projekt Swarm pozostaje najczystszym punktem odniesienia — cały jego kod źródłowy mieści się w zaledwie kilkuset liniach. Wzorzec ten zyskał ogromną popularność (stał się wiralowy), ponieważ jego API jest banalnie proste: `agent = prompt + narzędzia`, a `handoff = funkcja zwracająca innego agenta`. Ograniczenie: architektura ta jest bezstanowa, więc zarządzanie pamięcią leży po stronie aplikacji wywołującej.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~60 minut

## Problem

Większość platform wieloagentowych wymaga nauki własnych języków DSL: węzłów i krawędzi w LangGraph, zespołów (crews) i zadań w CrewAI, czy menedżerów w AutoGen GroupChat. Języki DSL oferują przydatne abstrakcje, ale sprawiają, że system staje się bardziej skomplikowany, niż jest to konieczne.

Swarm idzie w przeciwnym kierunku: wykorzystuje wbudowaną w model funkcję wywoływania narzędzi (tool calling). Handoffy stają się zwykłymi wywołaniami funkcji. Koordynatorem staje się ten agent, który w danej chwili prowadzi rozmowę, a logika przejść (maszyna stanów) jest zaszyta bezpośrednio w ich promptach systemowych.

## Koncepcja

### Dwa podstawowe elementy

**Procedura (Routine).** Prompt systemowy definiujący rolę agenta oraz zestaw dostępnych dla niego narzędzi. Pomyśl o tym jak o instrukcji postępowania: „jesteś agentem segregującym (triage); jeśli użytkownik pyta o zwrot środków, przekaż sprawę do agenta ds. zwrotów”.

**Handoff (Przekazanie sterowania).** Narzędzie, które agent może wywołać i które zwraca obiekt innego agenta. Silnik wykonawczy Swarm wykrywa, że zwrócony został obiekt klasy `Agent`, i przełącza aktywnego rozmówcę w kolejnej turze.

To cała abstrakcja, jakiej potrzebujesz.

```python
def transfer_to_refunds():
    return refund_agent  # Swarm wykrywa zwrot obiektu Agent i przełącza aktywnego agenta
triage_agent = Agent(
    name="triage",
    instructions="Kieruj użytkownika do odpowiedniego specjalisty.",
    functions=[transfer_to_refunds, transfer_to_sales, transfer_to_support],
)
```

Prompt systemowy agenta triage sprawia, że wybiera on właściwy handoff na podstawie wiadomości użytkownika. Routing realizowany jest bezpośrednio przez mechanizm wywoływania narzędzi (tool calling) w LLM.

### Dlaczego ten wzorzec stał się tak popularny

- **Minimalistyczne API.** Tylko dwa pojęcia do opanowania.
- **Wykorzystanie istniejących możliwości modelu.** Wywoływanie narzędzi (tool calling) jest dojrzałą technologią u większości wiodących dostawców LLM.
- **Brak narzutu związanego z maszyną stanów.** Nie definiujesz jawnie grafu — to prompty agentów opisują zasady przekazywania sterowania.

### Bezstanowość i jej konsekwencje

Swarm jest całkowicie bezstanowy między kolejnymi uruchomieniami. W trakcie jednego wykonania silnik przechowuje historię wiadomości, ale nie zapisuje jej na stałe. Zarządzanie pamięcią, stanem sesji i długotrwałymi zadaniami leży po stronie aplikacji wywołującej.

W wersji produkcyjnej (OpenAI Agents SDK, marzec 2025 r.) była to jedna z kluczowych zmian: pakiet SDK dodaje wbudowane zarządzanie sesjami, mechanizmy zabezpieczające (guardrails) oraz śledzenie wykonania (tracing), zachowując przy tym prostotę mechanizmu przekazywania.

### Kiedy warto stosować model Swarm / handoffy

- **Wzorce klasyfikacji (triage).** Agent pierwszej linii kieruje użytkownika do odpowiedniego specjalisty.
- **Przekazywanie na podstawie kompetencji.** „Jeśli zadanie wymaga pisania kodu, wywołaj programistę; jeśli potrzebny jest research, wywołaj badacza”.
- **Krótkie, zamknięte scenariusze.** Obsługa klienta, przekształcanie FAQ w zgłoszenia, proste procesy biznesowe.

### Gdzie model Swarm się nie sprawdza

- **Długie sesje ze współdzieleniem pamięci.** Handoff przełącza kontekst na nowego agenta i jego prompt systemowy wraz z całą historią. Bez zewnętrznego zarządzania pamięcią nie ma możliwości utrzymywania trwałego stanu specyficznego dla poszczególnych agentów.
- **Równoległe wykonywanie zadań.** Handoffy są sekwencyjne — w danym momencie aktywny jest tylko jeden agent. Wykonywanie zadań równolegle wymaga, aby aplikacja wywołująca uruchomiła wiele instancji Swarm jednocześnie.
- **Audytowalność i powtarzalność.** Bezstanowe uruchomienia są trudne do dokładnego zreplikowania, ponieważ wybór handoffu przez LLM nie jest w pełni deterministyczny.

### OpenAI Agents SDK (marzec 2025 r.)

Produkcyjny następca dodaje:

- **Utrzymywanie stanu sesji.** Trwały wątek konwersacji między wywołaniami.
- **Mechanizmy zabezpieczające (Guardrails).** Metody przechwytujące wejście/wyjście (hooks) w celu walidacji danych.
- **Śledzenie (Tracing).** Każde wywołanie narzędzia i każdy handoff są logowane.
- **Filtry handoffów.** Kontrola nad tym, jaki zakres kontekstu jest przekazywany nowemu agentowi.

Podstawowa mechanika przekazywania sterowania została zachowana, ale wzbogacono ją o funkcjonalności niezbędne w środowisku produkcyjnym.

### Model Swarm a GroupChat

Oba wzorce opierają się na routingu sterowanym przez LLM, ale różnią się tym, **kto decyduje o kolejnym kroku**:

- GroupChat: zewnętrzny selektor (funkcja lub LLM) wybiera kolejnego rozmówcę.
- Swarm: to aktualny agent wskazuje swojego następcę poprzez wywołanie narzędzia handoffu.

Swarm realizuje podejście „agent decyduje o kolejnym kroku”, podczas gdy GroupChat działa na zasadzie „menedżer decyduje o kolejnym kroku”. W Swarm decyzja jest wynikiem wywołania narzędzia przez aktywnego agenta; w GroupChat logika ta leży w `GroupChatManager`.

## Zbuduj to

Plik `code/main.py` implementuje Swarm od podstaw: klasę danych `Agent`, mechanizm handoffu (funkcję narzędziową zwracającą obiekt `Agent`) oraz pętlę uruchomieniową, która obsługuje przełączanie agentów.

Demonstracja: agent triage kieruje użytkownika do specjalistów ds. zwrotów, sprzedaży lub wsparcia technicznego. Każdy z nich ma przypisane dedykowane narzędzia. Pętla uruchomieniowa wypisuje w konsoli informacje o każdym handoffie.

Uruchomienie:

```bash
python3 code/main.py
```

## Zastosowanie

Plik `outputs/skill-handoff-designer.md` projektuje topologię handoffów dla wybranego zadania: określa strukturę agentów, dostępne dla nich przekazania sterowania oraz zakres przekazywanego kontekstu.

## Wdrożenie produkcyjne

Lista kontrolna:

- **Logowanie handoffów.** Każde przekazanie sterowania powinno zapisywać zdarzenie śledzenia wraz z migawką kontekstu przesyłanego między agentami.
- **Zasady przekazywania kontekstu.** Zdefiniuj politykę zarządzania historią przy handoffie: pełna historia (kosztowna), ostatnie N wiadomości czy skompresowane podsumowanie.
- **Uwierzytelnianie na granicach handoffu.** Przejście do agenta specjalistycznego dysponującego wrażliwymi narzędziami powinno być dodatkowo weryfikowane — w przeciwnym razie ataki typu prompt injection mogą wymusić nieautoryzowane przekazanie sterowania.
- **Wykonywanie pętli (Loop detection).** Sytuacja, w której dwóch agentów przekazuje sobie zadanie w nieskończoność (ping-pong), to częsty błąd. Wykrywaj go, analizując historię ostatnich K kroków.
- **Agent rezerwowy (Fallback).** Jeśli cel handoffu nie jest dostępny, skieruj przepływ do bezpiecznego agenta domyślnego.

## Ćwiczenia

1. Uruchom `code/main.py` i zasymuluj proces zwrotu kosztów. Upewnij się, że w drugiej turze aktywnym agentem staje się agent ds. zwrotów.
2. Zaimplementuj mechanizm wykrywania pętli: jeśli tych samych dwóch agentów przekazuje sobie sterowanie 3 razy z rzędu, wymuś przerwanie procesu i wywołaj procedurę rezerwową.
3. Zapoznaj się z dokumentacją OpenAI Agents SDK w sekcji dotyczącej filtrów handoffu. Zaimplementuj wersję z podsumowaniem kontekstu: agent przekazujący sterowanie streszcza dotychczasową dyskusję do listy punktowanej, zanim kontrolę przejmie kolejny agent.
4. Porównaj handoff w Swarm z selektorem w `GroupChatManager`. Który z tych wzorców jest bardziej podatny na ataki typu prompt injection i dlaczego?
5. Przeanalizuj oficjalne materiały i przykłady dla Swarm (https://developers.openai.com/cookbook/examples/orchestrating_agents). Wskaż jedną kluczową decyzję projektową ze Swarm, która uległa zmianie lub została zachowana w nowym OpenAI Agents SDK.

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Procedura (Routine) | „Prompt agenta” | Prompt systemowy + lista narzędzi. Definiuje rolę i możliwe kierunki przekazania sterowania. |
| Handoff | „Przekazanie do innego agenta” | Funkcja narzędziowa wywoływana przez aktywnego agenta, która zwraca obiekt nowego agenta. Silnik wykonawczy przełącza aktywnego rozmówcę. |
| Bezstanowość | „Brak pamięci między uruchomieniami” | Swarm nie utrzymuje stanu na stałe; zarządzanie historią leży po stronie aplikacji wywołującej. |
| Aktywny agent | „Kto aktualnie mówi” | Agent, który w danym momencie przetwarza zapytanie użytkownika. Handoff zmienia tego agenta. |
| Przekazywanie kontekstu | „Co jest przesyłane przy handoffie” | Polityka dotycząca historii wiadomości dostępnej dla kolejnego agenta: pełna, ostatnie N wiadomości lub podsumowana. |
| Pętla handoffów | „Ping-pong agentów” | Błąd (antywzorzec), w którym dwóch agentów bez końca przekazuje sobie nawzajem sterowanie. |
| OpenAI Agents SDK | „Produkcyjny Swarm” | Następca projektu Swarm z marca 2025 r.; dodaje wbudowane sesje, mechanizmy zabezpieczające i śledzenie. |
| Filtr handoffu | „Brama kontrolna” | Funkcja w SDK służąca do weryfikacji i modyfikacji kontekstu na granicy przekazywania sterowania. |

## Literatura uzupełniająca

- [Książka kucharska OpenAI — Agenci orkiestrujący: procedury i przekazywanie](https://developers.openai.com/cookbook/examples/orchestrating_agents) — artykuł referencyjny
- [Repozytorium OpenAI Swarm](https://github.com/openai/swarm) — oryginalna implementacja, zachowana jako odniesienie koncepcyjne
- [Dokumentacja OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — następca produkcyjny z sesjami i śledzeniem
- [Antropiczne notatki dotyczące przekazania w Claude](https://docs.anthropic.com/en/docs/claude-code) — jak podagenci Claude Code wykorzystują wzorzec podobny do przekazania za pośrednictwem `Task`
