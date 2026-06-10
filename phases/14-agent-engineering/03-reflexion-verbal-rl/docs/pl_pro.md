# Refleksja: Uczenie się ze wzmocnieniem werbalnym (Verbal Reinforcement Learning)

> Klasyczne uczenie ze wzmocnieniem (RL) oparte na gradientach wymaga tysięcy prób i klastrów GPU, aby wyeliminować pojedynczy błąd w działaniu. Metoda Reflexion (Shinn i in., NeurIPS 2023) realizuje to w języku naturalnym: po każdej nieudanej próbie agent formułuje refleksję (wnioski), zapisuje ją w pamięci epizodycznej i na jej podstawie podejmuje kolejną próbę. Wzorzec ten stanowi podstawę dla mechanizmów obliczeń w czasie bezczynności (Sleep-time compute) w Letta, instrukcji `CLAUDE.md` w Claude Code oraz reguł uczenia się w zaawansowanych przepływach pracy (pro-workflows).

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 02 (ReWOO)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy składowe architektury Reflexion (Actor, Evaluator, Self-Reflector) oraz opisz rolę pamięci epizodycznej.
- Zaimplementuj pętlę Reflexion przy użyciu biblioteki standardowej (stdlib), uwzględniając binarny moduł oceny (Evaluator), bufor refleksji oraz logikę ponawiania prób.
- Dokonaj wyboru pomiędzy skalarnym, heurystycznym i opartym na samoocenie źródłem informacji zwrotnej dla konkretnego zadania.
- Wyjaśnij, dlaczego wzmocnienie werbalne pozwala skorygować błędy, których usunięcie za pomocą klasycznego RL opartego na gradientach wymagałoby tysięcy iteracji treningowych.

## Problem

Agent nie radzi sobie z powierzonym zadaniem. W tradycyjnym uczeniu ze wzmocnieniem (RL) musielibyśmy przeprowadzić tysiące prób, obliczyć gradienty i zaktualizować wagi modelu. Jest to kosztowne, powolne, a większość produkcyjnych wdrożeń agentów nie posiada budżetu treningowego na obsługę każdego rodzaju awarii.

Metoda Reflexion (Shinn i in., arXiv:2303.11366) proponuje inne podejście: co by było, gdyby agent przeanalizował przyczyny niepowodzenia i podjął kolejną próbę, mając te wnioski zapisane bezpośrednio w prompcie? Nie ma tu aktualizacji wag ani obliczania gradientów – jedynie wnioski sformułowane w języku naturalnym, przekazywane między kolejnymi próbami.

Efekt: w środowisku ALFWorld rozwiązanie to deklasuje ReAct oraz inne modele bazowe bez dostrajania wag. W teście HotpotQA również przynosi poprawę w stosunku do standardowej pętli ReAct. W zadaniach generowania kodu (HumanEval/MBPP) wyznaczyło ono ówczesny stan wiedzy (SOTA) – a wszystko to bez wykonania ani jednego kroku optymalizacji gradientowej.

## Koncepcja

### Trzy komponenty

```
Actor         : generates a trajectory (ReAct-style loop)
Evaluator     : scores the trajectory — binary, heuristic, or self-eval
Self-Reflector: writes a natural-language reflection on the failure
```

Oraz jedna dodatkowa struktura danych:

```
Episodic memory: list of prior reflections, prepended to the next trial's prompt
```

Każda próba rozpoczyna się od uruchomienia Aktora. Następnie Evaluator ocenia wykonane działania. Jeśli ocena jest niska, Self-Reflector generuje wnioski w języku naturalnym (np. „Wybrałem niewłaściwe narzędzie, ponieważ błędnie zinterpretowałem pytanie i szukałem informacji o X, zamiast o Y”). Te wnioski trafiają do pamięci epizodycznej. Kolejna próba rozpoczyna się od początku, lecz w prompcie uwzględniane są już dotychczasowe refleksje.

### Trzy typy ewaluatorów

1. **Ewaluator skalarny** – zewnętrzny sygnał binarny. Przykładem jest sukces lub porażka w środowisku ALFWorld lub zaliczenie/niezaliczenie testów jednostkowych w HumanEval. To najprostsza metoda dostarczająca najbardziej jednoznacznego sygnału zwrotnego.
2. **Ewaluator heurystyczny** – reguły wykrywające określone anomalie. Przykłady: „Jeśli agent powtórzył to samo działanie dwa razy z rzędu, oznacz go jako zablokowanego”; „Jeśli ścieżka wykonania przekracza 50 kroków, oznacz jako nieefektywną”.
3. **Samoocena (Self-evaluation)** – model LLM samodzielnie ocenia swoją ścieżkę postępowania. Jest stosowana, gdy nie dysponujemy danymi referencyjnymi (ground truth). Daje słabszy sygnał, ale dobrze współgra z walidacją opartą na narzędziach (Lekcja 05 – Krytyk).

Podejściem domyślnym jest model hybrydowy: ewaluator skalarny (jeśli jest dostępny), samoocena (gdy brak danych referencyjnych) oraz heurystyki pełniące rolę zabezpieczeń.

### Dlaczego to uogólnia

Reflexion to nie tyle nowy algorytm, co nazwany wzorzec projektowy. Niemal każdy wdrożony produkcyjnie agent posiadający mechanizm samonaprawy (self-repairing) wykorzystuje jakąś jego wersję:

- Obliczenia w czasie bezczynności Letty (Lekcja 08): pomocniczy proces analizuje historię interakcji i zapisuje kluczowe wnioski w blokach pamięci.
- Wzorzec pliku `CLAUDE.md` w Claude Code / mechanizm trwałości pamięci: wyciągnięte wnioski są utrwalane i dołączane do kolejnych sesji.
- Polecenie `/learn-rule` w profesjonalnych narzędziach workflow: korekty są zapisywane jako formalne reguły działania.
- Węzły refleksyjne w LangGraph: specjalny węzeł oceniający wyniki i w razie potrzeby kierujący przepływ do ścieżki korekcyjnej.

Wszystkie te techniki opierają się na jednej obserwacji: język naturalny jest wystarczająco ekspresyjny, by skutecznie przenosić wiedzę o błędach i wyciągniętych wnioskach pomiędzy kolejnymi uruchomieniami systemu.

### Kiedy to działa, a kiedy nie

Reflexion sprawdza się, gdy:

- Dysponujemy jednoznacznym sygnałem o błędzie (niezaliczony test, awaria narzędzia, błędna odpowiedź).
- Klasa zadań ma charakter powtarzalny (agent wykonuje podobne operacje w kolejnych krokach).
- Wyciągnięte wnioski mogą realnie poprawić kolejną próbę (mamy wystarczający budżet na wykonanie dodatkowych akcji).

Reflexion nie przynosi korzyści, gdy:

- Agent bez problemu realizuje zadanie przy pierwszej próbie.
- Błąd ma charakter zewnętrzny (np. awaria sieci, uszkodzenie zewnętrznego API) – wniosek o treści „błąd sieci” nie przełoży się na poprawę logiki działania w przyszłości.
- Wnioskowanie staje się nadmiernie specyficzne (overfitting) – agent próbuje uogólniać wnioski na podstawie pojedynczych, losowych fluktuacji w wykonaniu.

Pułapka: degradacja (zgnilizna) pamięci. Refleksje nawarstwiają się, a część z nich staje się nieaktualna lub błędna. Wszaz z rozrostem bufora pamięci epizodycznej wnioskowanie staje się coraz wolniejsze. Rozwiązanie: okresowa konsolidacja (kompaktowanie) pamięci (Lekcja 06), stosowanie mechanizmu TTL dla wpisów lub uruchamianie niezależnego procesu czyszczącego w czasie bezczynności (np. Letta).

## Zbuduj to

Plik `code/main.py` implementuje mechanizm Reflexion na przykładzie prostej łamigłówki polegającej na utworzeniu 3-elementowej listy liczb, których suma daje określoną wartość docelową. Aktor generuje kolejne propozycje list, Evaluator weryfikuje ich sumę, a Self-Reflector opisuje w jednej linijce przyczynę ewentualnego błędu. Wygenerowany wniosek zapisywany jest w pamięci epizodycznej przed przystąpieniem do kolejnej próby.

Komponenty:

- `Actor` – moduł wykonawczy, który modyfikuje swoje podejście po zapoznaniu się z zapisanymi wnioskami.
- `Evaluator.binary()` – binarny wskaźnik (sukces/porażka) poprawności sumy.
- `SelfReflector` – generuje krótką, jednozdaniową diagnozę błędu.
- `EpisodicMemory` – bufor o ograniczonej pojemności z mechanizmem TTL (czasu życia wpisów).

Uruchomienie:

```
python3 code/main.py
```

Logi wykonania pokazują trzy podejścia. Pierwsza próba kończy się niepowodzeniem i zapisaniem refleksji. W drugiej próbie model uwzględnia wyciągnięte wnioski i koryguje swoje działanie, ale wciąż nie osiąga celu. Trzecie podejście kończy się pełnym sukcesem. Porównaj to z wykonaniem bazowym (bez mechanizmu Reflexion), w którym model powtarza ten sam błąd, co w pierwszej próbie.

## Użyj tego

LangGraph udostępnia wzorzec Reflexion w postaci odpowiedniego węzła grafu. Narzędzia takie jak Claude Code (polecenie `/memory`) czy zaawansowane środowiska workflow (polecenie `/learn-rule`) zapisują bufor epizodyczny w postaci plików Markdown. W Letta obliczenia w tle (sleep-time) uruchamiają moduł Self-Reflector podczas bezczynności agenta, dzięki czemu główny proces działa bez opóźnień. Pakiet SDK OpenAI nie wspiera bezpośrednio tego wzorca – można go jednak zaimplementować, tworząc moduł filtrujący (guardrail) odrzucający ścieżki o niskiej ocenie oraz wykorzystując trwałą pamięć sesji (Session), która utrzymuje stan pomiędzy kolejnymi uruchomieniami.

## Wyślij to

Plik `outputs/skill-reflexion-buffer.md` definiuje zasady tworzenia i utrzymywania bufora pamięci epizodycznej z obsługą logowania wniosków, mechanizmem TTL oraz deduplikacją. Na podstawie charakteru zadania i napotkanego błędu generuje on precyzyjne wskazówki ułatwiające kolejną próbę (unikając ogólnych sformułowań w stylu „bądź bardziej ostrożny”).

## Ćwiczenia

1. Zastąp binarny moduł oceny ewaluatorem skalarnym, który mierzy odległość od celu (np. różnicę sumy). Czy model szybciej osiąga zbieżność?
2. Wprowadź mechanizm TTL dla refleksji o długości 10 prób. Czy po przekroczeniu tej liczby starsze wpisy pomagają, czy utrudniają osiągnięcie celu?
3. Zaimplementuj ewaluator heurystyczny oznaczający próbę jako zablokowaną w pętli, jeśli agent dwukrotnie powtórzy to samo działanie. Jak to wpływa na pracę modułu Self-Reflector?
4. Przetestuj pętlę Reflexion z Aktorem, który ma tendencję do ignorowania wpisów z pamięci epizodycznej. Jak zmodyfikować prompt, aby zmusić Aktora do uwzględnienia tych wskazówek?
5. Przeczytaj sekcję 4 artykułu o Reflexion poświęconą środowisku ALFWorld. Wyjaśnij koncepcyjnie źródło wzrostu skuteczności o 130%: jaka kluczowa zmiana decyduje o tej różnicy w porównaniu do klasycznej pętli ReAct?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| Reflexion | „Samokorekta” | Wzorzec (Shinn i in., 2023) łączący role Aktora, Ewaluatora i Self-Reflectora ze strukturą pamięci epizodycznej. |
| Wzmocnienie werbalne (Verbal Reinforcement) | „Nauka bez modyfikacji wag” | Wykorzystanie wniosków w języku naturalnym, dołączanych do promptu przed kolejną próbą wykonania zadania. |
| Pamięć epizodyczna | „Historia błędów i wniosków” | Bufor przechowujący poprzednie refleksje dla danej klasy zadań. |
| Ewaluator skalarny | „Ocena liczbowa lub binarna” | Sukces/porażka lub ocena punktowa określana na podstawie obiektywnych kryteriów referencyjnych (ground truth). |
| Ewaluator heurystyczny | „Wyszukiwanie znanych wzorców błędów” | Analiza ścieżki pod kątem typowych problemów (np. zapętlenie, przekroczenie limitu kroków). |
| Samoocena | „Model jako sędzia własnych działań” | Metoda oceny stosowana w przypadku braku danych referencyjnych, często łączona z automatyczną weryfikacją wyników narzędzi. |
| Zgnilizna pamięci (Memory Rot) | „Przestarzałe lub sprzeczne wpisy” | Problem zapychania bufora pamięci epizodycznej nieaktualnymi informacjami; rozwiązaniem jest stosowanie TTL lub kompaktowanie. |
| Refleksja w czasie bezczynności (Sleep-time Reflection) | „Asynchroniczne wyciąganie wniosków” | Przeniesienie działania modułu Self-Reflector poza główną pętlę decyzyjną w celu uniknięcia opóźnień w interakcji z użytkownikiem. |

## Dalsze czytanie

- [Shinn i in., Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) — artykuł kanoniczny
- [Letta, Obliczanie czasu snu](https://www.letta.com/blog/sleep-time-compute) — asynchroniczne odbicie w produkcji
- [Anthropic, Efektywna inżynieria kontekstu dla agentów AI](https://www.anthropic.com/engineering/efektyw-context-engineering-for-ai-agents) — zarządzanie buforem epizodycznym jako częścią kontekstu
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — wzór węzła odbicia
