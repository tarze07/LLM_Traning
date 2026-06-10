# Specjalizacja ról — Planista, Krytyk, Wykonawca, Weryfikator

> Najpopularniejsza struktura dekompozycji zadań w 2026 roku opiera się na podziale: jeden agent planuje proces, drugi go realizuje, a kolejny krytykuje lub weryfikuje wyniki. Publikacja MetaGPT (arXiv:2308.00352) sformalizowała to podejście jako standardowe procedury operacyjne (SOP) zakodowane w instrukcjach ról — np. menedżer produktu, architekt, kierownik projektu, inżynier oraz specjalista QA — zgodnie z formułą `Code = SOP(Team)`. ChatDev (arXiv:2307.07924) łączy te role (projektanta, programistę, recenzenta i testera) za pomocą potoków komunikacyjnych z mechanizmem tzw. odhalucynowania komunikacyjnego (communicative de-hallucination), w którym agenci wprost dopytują o brakujące szczegóły. Rola weryfikatora jest tutaj kluczowa: Cemri i in. (taksonomia MAST, arXiv:2503.13657) wykazali, że zdecydowaną większość błędów w systemach wieloagentowych można powiązać z brakiem lub wadliwym działaniem warstwy weryfikacji. Z kolei PwC zaraportowało aż 7-krotny wzrost dokładności (z 10% do 70%) po wdrożeniu ustrukturyzowanych pętli walidacyjnych w CrewAI.

**Typ:** Ucz się + Buduj  
**Języki:** Python (stdlib)  
**Wymagania wstępne:** Faza 16 · 04 (Model prymitywny), Faza 16 · 05 (Wzorzec nadzorcy)  
**Czas:** ~60 minut  

## Problem

Niewyspecjalizowane systemy wieloagentowe generują przeciętne wyniki. Trzej programiści w jednym ogólnym czacie grupowym wygenerują po prostu trzy warianty tego samego, średniej jakości kodu. Zwiększanie liczby agentów czy rund debaty nie przyniesie poprawy, jeśli wszyscy wykonują to samo zadanie.

Rozwiązaniem nie jest dodawanie kolejnych agentów, lecz zróżnicowanie ich ról. Przypisz im odrębne zadania. Daj krytykowi narzędzia, których nie posiada planista. Daj weryfikatorowi obiektywne środowisko testowe. Dzięki temu w systemie zaistnieje konstruktywny proces korekty oparty na faktach, a nie tylko losowe próby generowania odpowiedzi.

## Koncepcja

### Cztery role kanoniczne

**Planista (Planner).** Analizuje cel główny, tworzy listę kroków lub specyfikację techniczną. Narzędzia: wyszukiwarki wiedzy, dokumentacja. Wynik: ustrukturyzowany plan działania.

**Wykonawca (Executor).** Realizuje kolejne punkty planu i tworzy docelowy artefakt. Narzędzia: rzeczywiste środowisko pracy (kompilator kodu, powłoka shell, klienty API). Wynik: gotowy artefakt.

**Krytyk (Critic).** Analizuje wyniki pracy wykonawcy pod kątem założeń planu. Narzędzia: dostęp do odczytu artefaktu, analizatory statyczne. Wynik: decyzja o akceptacji lub odrzuceniu z uzasadnieniem.

**Weryfikator (Verifier).** Poddaje artefakt deterministycznym testom walidacyjnym. Narzędzia: narzędzia testowe (test runners), sprawdzanie typów, walidatory schematów. Wynik: status zaliczony/niezaliczony wraz z logami błędów.

Krytyk ocenia subiektywnie, opierając się zazwyczaj na modelu LLM. Weryfikator działa w sposób obiektywny i deterministyczny, bazując na kodzie programistycznym. Są to dwie zupełnie różne role.

### Wzorzec SOP w MetaGPT

MetaGPT (arXiv:2308.00352) przenosi standardowe procedury operacyjne (SOP) z inżynierii oprogramowania wprost do instrukcji systemowych agentów:

- **Menedżer Produktu (Product Manager)** opracowuje dokument PRD (Product Requirements Document).
- **Architekt (Architect)** tworzy projekt systemu.
- **Kierownik Projektu (Project Manager)** dekomponuje i przydziela zadania.
- **Inżynier (Engineer)** wdraża kod.
- **Inżynier ds. Kontroli Jakości (QA Engineer)** opracowuje i uruchamia testy.

Każda rola posiada sztywno określone schematy wejścia i wyjścia. Formuła `Code = SOP(Team)` sprawia, że deterministyczne procedury SOP przekształcają dynamiczny zespół LLM w przewidywalny potok produkcyjny.

### Odhalucynowanie komunikacyjne w ChatDev

ChatDev wprowadza bardzo ważny mechanizm: gdy wykonawca potrzebuje konkretnych parametrów lub szczegółów, których zabrakło w planie, wprost wysyła zapytanie do projektanta przed przystąpieniem do pracy. Zapobiega to powszechnemu błędowi modeli LLM, jakim jest zmyślanie brakujących danych w celu ukończenia zadania za wszelką cenę.

Wdrożenie: instrukcja systemowa wykonawcy zawiera zapis: „Jeśli potrzebujesz konkretnych informacji, których nie otrzymałeś w planie, zapytaj o nie wprost odpowiedniego agenta (wskazując go z nazwy), zanim wygenerujesz wynik”.

### Dlaczego weryfikator jest kluczowy

Cemri i in. (taksonomia MAST) przeanalizowali 1642 błędy w systemach wieloagentowych. Aż 21,3% z nich stanowiły tzw. luki weryfikacyjne (verification gaps) — sytuacje, w których system wysłał odpowiedź do użytkownika bez jakiejkolwiek wcześniejszej weryfikacji. Pozostałe 79% błędów często wynikało z weryfikatorów, które zakończyły się błędem po cichu lub w ogóle nie zostały uruchomione. Rola weryfikatora jest absolutnie krytyczna.

Raporty PwC dotyczące wdrożeń CrewAI wskazują, że dodanie ustrukturyzowanej pętli weryfikacyjnej zwiększa dokładność odpowiedzi z 10% do 70%. To 7-krotny zysk z wdrożenia tylko jednej roli.

### Krytyk a Weryfikator

- **Krytyk** to model LLM oceniający artefakt jakościowo. Działa subiektywnie. Może zostać zwiedziony przez wiarygodnie brzmiącą prozę wygenerowaną przez wykonawcę.
- **Weryfikator** to deterministyczny program analizujący artefakt. Działa obiektywnie. Zwraca jednoznaczny status zaliczony/niezaliczony w oparciu o twarde dane.

Zaleca się stosowanie obu tych ról. Krytyk wyłapuje błędy jakościowe i stylistyczne, których weryfikator nie jest w stanie opisać regułami. Weryfikator z kolei wykrywa usterki logiczne i wykonawcze, które dla krytyka LLM były niewidoczne w tekście źródłowym.

### Antywzorzec: Systemy All-LLM

Powszechnym błędem opisanym w MAST jest projektowanie systemów, w których każda rola jest modelem LLM, a weryfikacja sprowadza się do wygenerowania komunikatu „wygląda w porządku”. Wdrożenie produkcyjne wymaga co najmniej jednego deterministycznego weryfikatora opartego na kodzie.

### Mapowanie frameworków

- **CrewAI** — parametry `Agent(role, goal, backstory)` stanowią podręcznikowy przykład definiowania specjalizacji.
- **LangGraph** — pozwala na definiowanie węzłów o unikalnych podpowiedziach systemowych, a krawędzie wymuszają kolejność potoku.
- **AutoGen** — wspiera specjalizację poprzez konfigurację `ConversableAgent` w ramach czatu grupowego (GroupChat).
- **OpenAI Agents SDK** — realizuje ten wzorzec poprzez mechanizmy przekazywania zadań (handoffs) pomiędzy wyspecjalizowanymi agentami.

## Zbuduj to

W pliku `code/main.py` zaimplementowano 4-etapowy potok tworzący prostą funkcję w języku Python:
- **Planista** opracowuje specyfikację funkcji.
- **Wykonawca** generuje kod źródłowy.
- **Krytyk** (symulowany LLM) ocenia kod pod kątem czytelności.
- **Weryfikator** uruchamia kod w odizolowanym środowisku (`exec`) i testuje go dla zadanych parametrów.

Demo uruchamia się dwukrotnie:
1. W pierwszym przebiegu wykonawca generuje poprawny kod (krytyk i weryfikator zaliczają testy).
2. W drugim przebiegu wykonawca generuje kod niezgodny ze specyfikacją. Krytyk LLM przepuszcza błąd, ponieważ kod wygląda bardzo wiarygodnie. Weryfikator jednak natychmiast go wykrywa, ponieważ uruchomiony test jednostkowy kończy się niepowodzeniem.

Uruchomienie:

```
python3 code/main.py
```

## Użyj tego

W pliku `outputs/skill-role-designer.md` zdefiniowano umiejętność, która analizuje zadanie i projektuje dla niego strukturę ról (od 3 do 5 agentów), określając dokładne schematy wejścia/wyjścia oraz logikę działania weryfikatora. Użyj jej przed rozpoczęciem kodowania agentów.

## Wyślij to

Lista kontrolna wdrożenia ról:

- **Co najmniej jeden weryfikator deterministyczny.** Unikaj systemów opartych wyłącznie na LLM (antywzorzec All-LLM).
- **Jawne schematy wejścia/wyjścia (I/O Schemas).** Planista musi zwracać ustrukturyzowany dokument specyfikacji, który wykonawca może bezbłędnie sparsować.
- **Odhalucynowanie komunikacyjne.** Wykonawca musi mieć możliwość dopytania planisty w przypadku braku danych; nie może zgadywać parametrów.
- **Kolejność wywołań weryfikacji.** Najpierw uruchamiaj krytyka (jest to proces szybki i tani, który wyłapuje wczesne wady), a dopiero potem weryfikatora (jest wolniejszy, ale wykrywa błędy wykonania).
- **Budżet pętli poprawek (Revision Loop).** Określ limit iteracji wykonawca-krytyk (zalecany limit to 2) przed przekazaniem zadania do weryfikacji przez człowieka.

## Ćwiczenia

1. Uruchom `code/main.py` i zaobserwuj, jak weryfikator wykrywa błąd przepuszczony przez krytyka LLM. Dodaj analizator statyczny (np. sprawdzający obecność słowa kluczowego `return`) jako dodatkowy weryfikator.
2. Wprowadź piątą rolę: „analityka wymagań”, który tłumaczy zapytania użytkownika na specyfikację wejściową dla planisty. Jakie reguły odhalucynowania komunikacyjnego należy dla niego zaimplementować?
3. Przeanalizuj sekcję 3 (Agents) w publikacji MetaGPT. Wypisz schematy wejścia i wyjścia dla każdej z 5 zdefiniowanych tam ról.
4. Przeanalizuj rysunek 3 (Chat Chain) w publikacji ChatDev (arXiv:2307.07924). Wskaż, w którym miejscu mechanizm odhalucynowania przerywa potencjalnie nieskończoną pętlę.
5. Rozważ trzy procesy biznesowe, w których wdrożenie deterministycznego weryfikatora (nieopartego na LLM) jest niemożliwe lub zbyt kosztowne. Zaproponuj alternatywne metody kontroli jakości dla tych przypadków.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Specjalizacja ról | „Różni agenci do różnych prac” | Konfiguracja instrukcji systemowych agentów pod kątem ról planisty, wykonawcy, krytyka i weryfikatora. |
| Wzorzec SOP | „Procedury operacyjne w monitach” | Podejście z MetaGPT: zdefiniowanie sztywnych schematów wejścia/wyjścia dla ról w celu stabilizacji potoku. |
| Odhalucynowanie komunikacyjne | „Zapytaj, zanim zmyślisz” | Wzorzec z ChatDev: wykonawca wprost dopytuje planistę o parametry w przypadku ich braku. |
| Krytyk (Critic) | „Recenzent LLM” | Subiektywny agent oceniający jakość i styl. Może zostać oszukany przez poprawny syntaktycznie, ale błędny kod. |
| Weryfikator (Verifier) | „Test automatyczny” | Deterministyczny program weryfikujący artefakt (np. test runner, linter). Niemożliwy do oszukania prozą. |
| Luka weryfikacyjna | „Brak weryfikacji” | Błąd z taksonomii MAST stanowiący 21,3% awarii — wysłanie wyniku bez jakiejkolwiek wcześniejszej weryfikacji. |
| Pętla poprawek (Revision Loop) | „Proces poprawek” | Cykl, w którym krytyk odsyła artefakt do wykonawcy w celu naniesienia poprawek na podstawie uwag. |
| Antywzorzec All-LLM | „Sami krytycy LLM” | Błąd projektowy polegający na braku jakiejkolwiek deterministycznej weryfikacji na poziomie kodu. |

## Dalsze czytanie

- [Hong i in. — MetaGPT: Meta Programming for Multi-Agent Collaboration](https://arxiv.org/abs/2308.00352) — bazowa publikacja opisująca wzorzec SOP w systemach agentowych.
- [Qian i in. — Communicative Agents for Software Development (ChatDev)](https://arxiv.org/abs/2307.07924) — opis koncepcji łańcuchów komunikacji i odhalucynowania.
- [Cemri i in. — Why Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — analiza taksonomii MAST i statystyk luk weryfikacyjnych.
- [CrewAI: Agent Roles](https://docs.crewai.com/en/introduction) — dokumentacja definiowania roli i profilu agentów w środowisku CrewAI.
