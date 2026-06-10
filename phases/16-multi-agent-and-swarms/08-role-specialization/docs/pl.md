# Specjalizacja roli — Planista, Krytyk, Wykonawca, Weryfikator

> Najczęstsza dekompozycja wieloagentowa w 2026 r.: jeden agent planuje, drugi realizuje, ktoś krytykuje lub weryfikuje. MetaGPT (arXiv:2308.00352) formalizuje to jako standardowe procedury operacyjne zakodowane w podpowiedziach ról — menedżer produktu, architekt, kierownik projektu, inżynier, inżynier ds. kontroli jakości — zgodnie z `Code = SOP(Team)`. ChatDev (arXiv:2307.07924) łączy projektanta, programistę, recenzenta, testera poprzez „łańcuch czatu” z „komunikacyjną dehalucynacją” (agenci wyraźnie żądają brakujących szczegółów). Weryfikator jest nośny: Cemri i in. (MAST, arXiv:2503.13657) pokazują, że każdą awarię wielu agentów można powiązać z brakującą lub uszkodzoną weryfikacją. PwC odnotowało 7-krotny wzrost dokładności (10% → 70%) w wyniku ustrukturyzowanych pętli walidacyjnych w CrewAI.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (Model pierwotny), Faza 16 · 05 (Supervisor)
**Czas:** ~60 minut

## Problem

Ogólne systemy wieloagentowe generują ogólne dane wyjściowe. Trzej programiści na czacie grupowym piszą trzy wersje tego samego przeciętnego kodu. Możesz dodać więcej agentów, dodać więcej rund i nadal nie przekroczyć progu jakości.

Poprawka nie polega na większej liczbie agentów — lecz na *innych* agentach. Przypisz odrębne role. Daj krytykowi narzędzia, których nie ma planista. Daj weryfikatorowi obiektywny zestaw testów. Teraz w systemie panuje wewnętrzna niezgoda co do ugruntowanej korekty, a nie tylko równoległego zgadywania.

## Koncepcja

### Cztery role kanoniczne

**Planista.** Odczytuje cel, tworzy listę kroków lub specyfikację. Narzędzia: wyszukiwanie wiedzy, dokumenty. Wynik: uporządkowany plan.

**Wykonawca.** Czyta krok po kroku planu i tworzy artefakt. Narzędzia: rzeczywiste narzędzia pracy (kompilator kodu, powłoka, klient API). Wyjście: artefakt.

**Krytyka.** Odczytuje wyniki wykonawcy zgodnie z zamierzeniami planisty. Narzędzia: dostęp do artefaktu w trybie tylko do odczytu, analiza statyczna. Wynik: zaakceptuj/odrzuć z podaniem powodów.

**Weryfikator.** Odczytuje artefakt i przeprowadza kontrolę deterministyczną. Narzędzia: uruchamiacz testów, sprawdzanie typów, walidator schematu. Wynik: pozytywny/negatywny z dowodami.

Krytyk jest subiektywny, uparty, często oparty na LLM. Weryfikator jest obiektywny, deterministyczny, często oparty na kodzie. To nie jest ta sama rola.

### Wzór SOP MetaGPT

MetaGPT (arXiv:2308.00352) koduje standardowe procedury operacyjne inżynierii oprogramowania jako podpowiedzi dotyczące ról:

- **Menedżer Produktu** pisze PRD.
- **Architekt** tworzy projekt systemu.
- **Kierownik Projektu** dzieli zadania.
- **Inżynier** wdraża.
- **Inżynier ds. kontroli jakości** przeprowadza testy.

Każda rola ma ścisły schemat wejścia/wyjścia. Podpowiedź dotycząca roli mówi, czym *jest* rola i co *musi generować*. Sformułowanie `Code = SOP(Team)` — deterministyczne SOP przekształcają zespół LLM w przewidywalny rurociąg.

### Komunikatywna dehalucynacja ChatDeva

ChatDev dodaje kluczowy ruch: kiedy wykonawca potrzebuje konkretnego szczegółu, którego nie było w planie, wyraźnie pyta projektanta przed kontynuowaniem. Zapobiega to klasycznemu niepowodzeniu LLM polegającemu na wiarygodnym wymyśleniu szczegółów.

Implementacja: zachęta dotycząca roli obejmuje „jeśli potrzebujesz konkretnych informacji, których nie otrzymałeś, przed utworzeniem wyników zapytaj odpowiednią rolę z imienia i nazwiska”.

### Dlaczego weryfikator ma największe znaczenie

Cemri i in. (MAST) wyśledził 1642 niepowodzeń wykonywania wielu agentów. 21,3% stanowiły luki weryfikacyjne – system wysłał odpowiedź, której nikt nie sprawdził. Pozostałe 79% często wynika z tego, że „wystąpiła kontrola, która zakończyła się niepowodzeniem po cichu lub nigdy nie została przeprowadzona”. Weryfikacja jest rolą nośną.

PwC podało (wdrożenia CrewAI, 2025), że dodanie ustrukturyzowanej pętli walidacyjnej zwiększyło dokładność z 10% do 70%. 7× zysk z jednej roli.

### Krytyk kontra weryfikator

- Krytyk to LLM recenzujący artefakt pod kątem jakości. Subiektywny. Da się zwieść wiarygodną prozą.
- Weryfikator to deterministyczny program działający na artefakcie. Cel. Daje wynik pozytywny/negatywny wraz z dowodami.

Użyj obu. Krytyk wyłapuje problemy smakowe, których weryfikator nie jest w stanie wyrazić. Weryfikator wychwytuje błędy, których krytyk nie może zobaczyć, ponieważ pojawiają się one dopiero w czasie wykonywania.

### Antywzorzec

Każda rola w twoim systemie to LLM, a wynik każdej roli jest „wygląda dobrze”. Klasyczny tryb awarii MAST. Dodaj co najmniej jeden weryfikator, którego pozytywny/negatywny wynik jest ustalany na podstawie kodu, a nie LLM.

### Mapowania frameworka

- **CrewAI** — `Agent(role, goal, backstory)` to powierzchnia specjalizacji podręcznika.
- **LangGraph** — węzły mogą mieć specjalne podpowiedzi; krawędzie wzmacniają rurociąg.
- **AutoGen** — ConversableAgents specyficzni dla roli z nazwami składającymi się z jednego słowa w GroupChat.
- **OpenAI Agents SDK** — narzędzia do przekazywania informacji pomiędzy agentami wyspecjalizowanymi w danej roli.

## Zbuduj to

`code/main.py` implementuje 4-rolowy potok budujący prostą funkcję Pythona:

- **Planista** tworzy specyfikację.
- **Executor** generuje ciąg kodu.
- **Krytyk** (symulacja LLM) sygnalizuje oczywiste problemy.
- **Weryfikator** uruchamia wygenerowany kod w piaskownicy (`exec`) w odniesieniu do przypadku testowego.

Demo uruchamia się dwa razy: raz, gdy wykonawca wygeneruje poprawny kod (oba krytyczne i weryfikator przechodzą pomyślnie), drugi raz, gdy wykonawca wygeneruje kod niezgodny ze specyfikacją (krytyk przeocza błąd, ponieważ wygląda wiarygodnie, weryfikator wyłapuje go, ponieważ test się nie powiedzie).

Uruchom:

```
python3 code/main.py
```

## Użyj tego

`outputs/skill-role-designer.md` podejmuje zadanie i tworzy listę ról (3–5 ról), schemat wejścia/wyjścia dla każdej roli oraz kontrolę weryfikatora. Użyj tego przed podłączeniem agentów do struktury.

## Wyślij to

Lista kontrolna:

- **Przynajmniej jeden weryfikator deterministyczny.** Nigdy all-LLM.
- **Jawny schemat we/wy dla każdej roli.** Planista zwraca specyfikację, a nie prozę; wykonawca czyta ten schemat.
- **Dehalucynacja komunikacyjna.** Wykonawca musi zapytać planistę, gdy brakuje informacji; nigdy tego nie wymyślaj.
- **Kolejność krytyka/weryfikatora.** Najpierw uruchom krytyka (tanie, wychwytuje problemy projektowe), następnie weryfikator (powolny, wyłapuje błędy).
- **Budżet pętli.** Maks. 2 rundy przeglądu przez krytyka-wykonawcę przed eskalacją do człowieka.

## Ćwiczenia

1. Uruchom `code/main.py` i obserwuj, jak weryfikator wychwytuje błąd, który przeoczył krytyk. Dodaj kontrolę analizy statycznej (zlicz wystąpienia `return`) jako dodatkowy weryfikator. Co wyłapuje, czego brakuje w teście wykonawczym?
2. Dodaj piątą rolę: „analityk wymagań”, która przekłada życzenia użytkownika na specyfikację gotową dla planisty. Jakie komunikatywne prośby o dehalucynację powinny do niego płynąć?
3. Przeczytaj sekcję 3 MetaGPT („Agenci”). Wymień schemat wejścia/wyjścia każdej z 5 ról MetaGPT.
4. Przeczytaj diagram łańcucha czatu ChatDev (arXiv:2307.07924 Rysunek 3). Zidentyfikuj, gdzie dehalucynacja komunikacyjna przerywa pętlę, która w innym przypadku byłaby nieskończona.
5. 7-krotny wzrost dokładności PwC pochodzi z pętli weryfikacyjnych. Postaw hipotezę o trzech zadaniach, w przypadku których dodanie weryfikatora nie byłoby pomocne – w przypadku gdy deterministyczne sprawdzenie poprawności jest niemożliwe lub zbyt kosztowne.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Specjalizacja roli | „Różni agenci, różne prace” | Odrębne podpowiedzi systemowe dostosowane do ról planisty/wykonawcy/krytyka/weryfikatora. |
| Wzór SOP | „Zakodowana standardowa procedura operacyjna” | Ramy MetaGPT: ścisłe schematy we/wy dla każdej roli zamieniają zespół w potok. |
| Odhalucynacja komunikacyjna | „Zapytaj zanim wymyślisz” | Wzorzec ChatDev: wykonawca pyta planistę, gdy brakuje jakiegoś szczegółu, zamiast go wymyślać. |
| Krytyk | „Recenzent LLM” | Subiektywny, uparty recenzent. Łapie problemy smakowe. Da się zwieść wiarygodną prozą. |
| Weryfikator | „Kontrola deterministyczna” | Wynik pozytywny/nieudany w oparciu o kod. Osoba przeprowadzająca testy, sprawdzająca typ, walidator schematu. Nie da się oszukać. |
| Luka weryfikacyjna | „Nikt nie sprawdzał” | 21,3% awarii MAST. Odpowiedź wysłana bez czeku, który wyłapałby błąd. |
| Pętla rewizyjna | „Krytyk odsyła” | Odrzucenie krytyka powoduje ponowne uruchomienie wykonawcy z informacją zwrotną. Potrzebuje budżetu. |
| Antywzorzec All-LLM | „Wygląda mi to dobrze” | Każda rola to LLM, bez kontroli deterministycznej. Klasyczna awaria MAST. |

## Dalsze czytanie

- [Hong i in. — MetaGPT: Meta Programming for Multi-Agent Collaboration](https://arxiv.org/abs/2308.00352) — dokument referencyjny SOP-as-role-prompt
- [Qian i in. — Agenci komunikatywni do tworzenia oprogramowania (ChatDev)](https://arxiv.org/abs/2307.07924) — łańcuch czatów + dehalucynacja komunikacyjna
- [Cemri i in. — Dlaczego wieloagentowe systemy LLM zawodzą?](https://arxiv.org/abs/2503.13657) — taksonomia MAST; luki weryfikacyjne stanowią 21,3% niepowodzeń
- [Dokumentacja CrewAI — Role agentów](https://docs.crewai.com/en/introduction) — powierzchnia specyfikacji roli produkcyjnej