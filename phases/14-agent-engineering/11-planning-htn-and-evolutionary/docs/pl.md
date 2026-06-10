# Planowanie za pomocą HTN i wyszukiwania ewolucyjnego

> Planowanie symboliczne obsługuje przypadki, w których można udowodnić, że plan jest poprawny. Wyszukiwanie kodu ewolucyjnego obsługuje przypadki, w których funkcję dopasowania można sprawdzić maszynowo. ChatHTN (2025) i AlphaEvolve (2025) pokazują, co każdy z nich odblokowuje w połączeniu z LLM.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 02 (ReWOO i Plan-and-Execute)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij hierarchiczne sieci zadań: zadania, metody, operatory, warunki wstępne, efekty.
- Opisz pętlę hybrydową ChatHTN — wyszukiwanie symboliczne z rozkładem awaryjnym LLM.
- Wyjaśnij pętlę ewolucyjną AlphaEvolve i dlaczego działa ona tylko z programowym ewaluatorem.
- Zaimplementuj narzędzie do planowania zabawek HTN oraz ewolucyjne wyszukiwanie zabawek w stdlib.

## Problem

ReWOO (lekcja 02), Plan-and-Execute i ReAct obejmują większość planowania agentów. Dwa przypadki, które nie obejmują dobrze:

1. **Plany z możliwą do udowodnienia poprawnością.** Planowanie, wyznaczanie trasy lotu, przepływy pracy zgodne z przepisami — plan musi być solidny od strony konstrukcyjnej. Płynny plan LLM, który czasami halucynuje krok, jest nie do przyjęcia.
2. **Optymalizacje z funkcją zgodności sprawdzaną maszynowo.** Mnożenie macierzy, heurystyka planowania, przebiegi kompilatora — celem nie jest „właściwy plan”, ale „najlepszy plan”.

Planowanie HTN i AlphaEvolve rozwiązują dwa różne problemy. Oba wykorzystują LLM jako wzmacniacze, a nie zamienniki.

## Koncepcja

### Hierarchiczne sieci zadań

HTN to:

- **Zadania** — złożone (do rozłożenia) i pierwotne (bezpośrednio wykonywalne).
- **Metody** — sposoby rozkładania zadania złożonego na podzadania wraz z warunkami wstępnymi.
- **Operatory** — prymitywne działania z warunkami wstępnymi i efektami.
- **Stan** — zbiór faktów.

Planowanie: mając cel i stan początkowy, znajdź rozkład na operatory pierwotne, których warunki są kolejno spełnione.

HTN jest starszy niż LLM i nadal stanowi punkt odniesienia dla planów, które można udowodnić, że są prawidłowe.

### ChatHTN (Gopalakrishnan i in., 2025)

ChatHTN (arXiv:2505.11814) przeplata symboliczny HTN z zapytaniami LLM:

1. Spróbuj rozłożyć bieżące zadanie złożone na istniejące metody.
2. Jeśli żadna metoda nie ma zastosowania, zapytaj LLM: „w jaki sposób rozłożyłbyś `task` na stan `s`?”
3. Przetłumacz odpowiedź LLM na kandydujące podzadania.
4. Sprawdź w oparciu o schemat operatora; odrzucić nieprawidłowe rozkłady.
5. Powtórzenie.

Główne twierdzenie artykułu: każdy opracowany plan jest słuszny w sposób możliwy do udowodnienia, ponieważ sugestie LLM pojawiają się jedynie jako potencjalne rozkłady, a nie jako bezpośrednie zmiany planu. Warstwa symboliczna posiada poprawność; LLM rozszerza bibliotekę metod.

Nauka metodą online (OpenReview `gwYEDY9j2x`, kontynuacja z 2025 r.) dodaje osobę uczącą się, która uogólnia dekompozycje utworzone przez LLM poprzez regresję — zmniejszając częstotliwość zapytań LLM do 75%.

### AlphaEvolve (Novikov i in., 2025)

AlphaEvolve (arXiv:2506.13131, DeepMind, czerwiec 2025) to inna bestia: ewolucyjne wyszukiwanie kodu zorganizowane przez zespół Gemini 2.0 Flash/Pro.

Pętla:

1. Zacznij od programu początkowego + ewaluatora programowego (zwraca wynik sprawności).
2. Zespół LLM proponuje mutacje.
3. Przepuść mutacje przez ewaluator.
4. Zachowaj to, co najlepsze; ponownie mutować.

Opublikowane zwycięstwa:

- Pierwsza poprawa w stosunku do Strassena w zakresie mnożenia macierzy zespolonych 4x4 od 56 lat (48 mnożeń skalarnych).
- 0,7% odzyskało obliczenia Google za pomocą heurystyki planowania Borg.
- 32% przyspieszenia FlashAttention przy obciążeniu granicznym.

Twarde ograniczenie: funkcja przystosowania musi być sprawdzalna maszynowo. Ewolucyjne poszukiwania odpowiedzi prozą nie są zbieżne.

### Kiedy używać którego

| Klasa problemowa | Użyj | Dlaczego |
|----------|-----|-----|
| Planowanie z twardymi ograniczeniami | HTN + CzatHTN | Udowodniona solidność |
| Optymalizacja kompilatora | AlphaEvolve | Sprawność sprawdzana maszynowo |
| Wieloetapowa realizacja zadania | Reaguj / ReWOO | LLM w pętli, brak formalnych gwarancji |
| Ulepszanie kodu za pomocą testów | AlphaEvolve | Testy są oceniającym |
| Automatyzacja związana z polityką | HTN | Warunki wstępne kodują politykę |

### Gdzie ten wzorzec jest błędny

- **HTN bez operatorów.** Bez schematów warunków wstępnych/efektów twierdzenie o solidności upada. „LLM sugeruje rozkład” ChatHTN wymaga, aby schemat odrzucał nieprawidłowe ruchy.
- **AlphaEvolve bez prawdziwego oceniającego.** „Zapytaj LLM, czy kod jest lepszy” nie jest funkcją fitness. Ewaluator musi być deterministyczny i szybki.
- **Nadmierna inżynieria.** Większość zadań agenta też nie jest potrzebna. Sięgnij najpierw po ReAct lub ReWOO.

## Zbuduj to

`code/main.py` implementuje dwie zabawki:

- Planista HTN stdlib z operatorami, metodami, warunkami wstępnymi, efektami i `LLMFallback`, który uruchamia się, gdy żadna metoda nie pasuje do zadania złożonego. „LLM” to skryptowy dekompozytor, dzięki czemu planista działa w trybie offline.
- Przeszukiwanie ewolucyjne stdlib w programach arytmetycznych: powiększanie wyrażeń, których dane wyjściowe minimalizują `|f(x) - target|` w zestawie testowym. Ewaluator jest deterministyczny.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje, jak planista HTN rozkłada złożone zadanie (z rezerwowym LLM w połowie planu) i pętlę ewolucyjną zbiegającą się do wyrażenia docelowego.

## Użyj tego

- **Planiści HTML** — `pyhop`, `SHOP3` lub utwórz własny, aby egzekwować zasady specyficzne dla domeny.
- **ChatHTN** — kod badawczy; wzorzec (symboliczny + rezerwowy LLM) można łatwo przenieść do dowolnego planisty HTN.
- **AlphaEvolve** — artykuł DeepMind; wzór (zespół + oceniający) jest powtarzalny. Pojawiają się OpenEvolve i podobne rozwidlenia open source.
- **Struktura agentów** — żadna nie oferuje jeszcze najwyższej klasy HTN ani AlphaEvolve. Zbuduj go jako subagent lub pracownik w tle.

## Wyślij to

`outputs/skill-hybrid-planner.md` generuje hybrydowe rusztowanie planisty (HTN lub ewolucyjne) z wyraźnie określonym zakresem roli LLM.

## Ćwiczenia

1. Rozszerz planer HTN o funkcję cofania: gdy warunek końcowy operatora nie powiedzie się w czasie wykonywania, wycofaj się i wypróbuj następną metodę.
2. Dodaj pamięć podręczną metody LLM do ChatHTN: gdy LLM rozkłada zadanie `T` we wzorcu stanu `P`, zapisz wynik. Przy następnym wywołaniu sprawdź ponownie bibliotekę metod.
3. Zamień ewaluator wyszukiwania ewolucyjnego na prawdziwy zestaw testów. Opracuj funkcję sortowania, która przejdzie 20 przypadków testowych; zgłosić pokolenia do konwergencji.
4. Przeczytaj uwagi do projektu ewaluatora AlphaEvolve. Zaprojektuj ewaluator dla domeny, na której Ci zależy (optymalizacja zapytań SQL, minimalizacja zestawu testów, wdrożenie YAML).
5. Połącz: użyj HTN, aby rozłożyć zadanie złożone na podzadania, a następnie użyj wyszukiwania ewolucyjnego dla pierwotnego operatora każdego podzadania. Gdzie błyszczy, gdzie przepracowuje?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| HTN | „Planista hierarchiczny” | Dekompozycja zadań z operatorami, warunkami wstępnymi, efektami |
| Metoda | „Reguła rozkładu” | Sposób podziału zadania złożonego na podzadania |
| Operator | „Działanie prymitywne” | Stopień betonowy z warunkiem i skutkiem |
| CzatHTN | „LLM + HTN” | Planista symboliczny pyta LLM, gdy żadna metoda nie pasuje |
| AlphaEvolve | „Poszukiwanie kodu ewolucyjnego” | Zespoły LLM mutują kod; deterministyczny oceniający wybiera |
| Funkcja fitness | „Ewaluator” | Deterministyczny, sprawdzalny maszynowo wynik na podstawie wyników |
| Nauka metodą online | „Rozkład LLM w pamięci podręcznej” | Przechowuj + uogólniaj plany LLM, aby obniżyć koszty zapytań |

## Dalsze czytanie

- [Gopalakrishnan i in., ChatHTN (arXiv:2505.11814)](https://arxiv.org/abs/2505.11814) — planista symboliczny + hybrydowy LLM
- [Novikov et al., AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — przeszukiwanie kodu ewolucyjnego z mutacjami LLM
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — kiedy sięgnąć po planistę, a kiedy po prostą pętlę