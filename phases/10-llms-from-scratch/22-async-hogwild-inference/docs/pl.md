# Async i Hogwild! Wnioskowanie

> Dekodowanie spekulatywne (faza 10 · 15) równoległe tokeny w ramach jednej sekwencji. Struktury wieloagentowe działają równolegle w całych sekwencjach, ale wymuszają wyraźną koordynację (głosowanie, dzielenie podzadań). Hogwild! Wnioskowanie (Rodionov i in., arXiv:2504.06261) robi coś innego: uruchamia równolegle N instancji tego samego LLM względem pamięci podręcznej SHARED. Każdy pracownik natychmiast widzi wygenerowane przez każdego innego pracownika żetony. Nowoczesne modele rozumowania — QwQ, DeepSeek-R1 — mogą samodzielnie koordynować działanie za pośrednictwem współdzielonej pamięci podręcznej bez konieczności dostrajania. Podejście to jest eksperymentalne, ale otwiera zupełnie nową oś równoległości wnioskowania, która jest prostopadła do dekodowania specyfikacji. Ta lekcja przedstawia dwuosobowego Hogwilda! symulator w stdlib Python i wyjaśnia, dlaczego współpraca współdzielonej pamięci podręcznej wyłania się z możliwości wnioskowania istniejącego modelu.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 10 · 12 (optymalizacja wnioskowania), Faza 10 · 15 (dekodowanie spekulatywne)
**Czas:** ~60 minut

## Cele nauczania

- Opisz trzy popularne topologie równoległego LLM (głosowanie, podzadanie, Hogwild!) i nazwij problemy, których dotyczy każda z nich.
- Podaj rdzeń Hogwild! konfiguracja: wielu pracowników, jedna współdzielona pamięć podręczna KV, wschodząca koordynacja poprzez automatyczne podpowiedzi.
- Oblicz przyspieszenie Hogwild w czasie ściany! jako funkcja liczby procesów roboczych `N`, równoległości na poziomie zadania `p` i narzutu na koordynację `c`.
- Zaimplementuj dwuosobowego Hogwilda! symulator problemu zabawki i obserwuj pojawiający się podział zadań.

## Problem

Nowoczesne LLM rozwiązują trudne problemy, tworząc długie łańcuchy rozumowań — 5000 tokenów logiki krok po kroku jest powszechne, dziesiątki tysięcy tokenów ma miejsce w przypadku głębokich problemów matematycznych. Przy dekodowaniu 35 tokenów/s w modelu 70B, 50 tys. tokenów to 24 minuty. Model interaktywny nie jest.

Dekodowanie spekulatywne (faza 10 · 15) zapewnia 3-5-krotne przyspieszenie poprzez równoległość w obrębie jednej sekwencji. Poza tym sekwencyjna zależność dekodowania autoregresyjnego to twardy sufit. Każdy nowy token zależy od każdego poprzedniego tokena.

Oczywiste pytanie: czy możemy łączyć sekwencje równolegle? Uruchom wiele kopii tego samego modelu przy tym samym problemie, pozwól im współpracować, czy podzielą się pracą?

Wcześniejsze prace: zespoły do ​​głosowania (uruchom N modeli, wybierz odpowiedź większości), drzewo myśli (rozgałęzione ścieżki rozumowania i rekombinacja) oraz struktury wieloagentowe (przydziel każdemu agentowi podzadanie, skorzystaj z koordynatora). Wszystko to pomaga w określonych obszarach zadań. Wszystkie wprowadzają także jawne mechanizmy koordynacji — zasady głosowania, logikę rozgałęziania i usuwania, protokoły przesyłania wiadomości między agentami.

Hogwild! Wnioskowanie przyjmuje inne podejście. N pracowników korzysta z jednej pamięci podręcznej KV. Każdy pracownik natychmiast widzi wygenerowane przez pozostałych pracowników tokeny, tak jakby stanowiły jego własny kontekst. Pracownicy – ​​bez żadnego szkolenia i doskonalenia – zastanawiają się, jak podzielić pracę. Nowoczesne modele wnioskowania (QwQ, DeepSeek-R1, tryb wnioskowania rodziny Claude) mogą czytać współdzieloną pamięć podręczną i mówić takie rzeczy, jak „Widzę, że pracownik 2 już poradził sobie z przypadkiem podstawowym, więc popracuję nad krokiem indukcyjnym”.

Przyspieszenie jest zależne od obciążenia i ma charakter eksperymentalny od kwietnia 2026 r. Warto jednak poznać ten pomysł, ponieważ otwiera nową oś równoległości wnioskowania.

## Koncepcja

### Konfiguracja

Zainicjuj N procesów roboczych, wszystkie działające na tym samym LLM. Zamiast pamięci podręcznej KV na pracownika, utrzymuj JEDNĄ współdzieloną pamięć podręczną. Kiedy proces roboczy `i` generuje token `t_j`, token jest zapisywany we współdzielonej pamięci podręcznej na następnej pozycji. Kiedy proces roboczy `k` wykonuje kolejny krok, odczytuje bieżący stan pamięci podręcznej (który obejmuje wszystko, co do tej pory wygenerowało wszystkich N pracowników).

W odpowiednim momencie pracownicy ścigają się, aby zapisywać tokeny. Nie ma indeksu pozycji przypadającego na pracownika — pamięć podręczna to pojedyncza rosnąca sekwencja. Zamówienie jest ustalane na podstawie czasu przybycia zapisu.

### Dlaczego pojawia się koordynacja

Pracownicy dzielą się podpowiedzią. Zwykle coś w stylu: „Jesteś jedną z N instancji pracujących razem nad tym problemem. Każda instancja odczytuje pamięć współdzieloną i może zobaczyć, co napisały inne instancje. Unikaj zbędnej pracy”. Wystarczy zachęta i współdzielona pamięć podręczna. Modele rozumowania odczytują pamięć podręczną, zauważają, które części problemu już próbowano i (często, ale nie zawsze) zwracają się do niezbadanych części.

Hogwild! w artykule (Rodionov i in., 2025) przedstawiono obserwacje takie jak:

- Pracownicy formułują plany i przekazują je innym pracownikom za pośrednictwem pamięci podręcznej.
- Pracownicy zauważają błędy w rozumowaniu innych pracowników i je wytykają.
- Pracownicy dostosowują się, gdy plan się nie powiedzie, i proponują alternatywy.
- Gdy pojawi się monit o sprawdzenie nadmiarowości, pracownicy wykrywają to i odwracają się.

Nic z tego nie wymaga dostrojenia. Pojawiające się zachowanie wynika z możliwości rozumowania, które model już posiada.

### Nazewnictwo

Nazwa gazety riffuje na temat Hogwild! SGD (Recht i in., 2011), optymalizator aktualizacji asynchronicznej. Analogia: wszyscy asynchroniczni pracownicy SGD zapisują do wspólnego wektora parametrów; Hogwild! Wszyscy pracownicy Inference zapisują we współdzielonej pamięci podręcznej KV. Obydwa opierają się na empirycznej zbieżności, a nie na gwarancjach synchronizacji.

### Dzięki RoPE jest to wykonalne

Rotary Position Embeddings (RoPE, Su i in. 2021) kodują informacje o pozycji poprzez rotację wektorów Q i K. Ponieważ pozycje są obrotami, a nie wbudowanymi przesunięciami, pozycja tokena może się zmienić bez ponownego obliczania wpisu pamięci podręcznej KV. Gdy pracownik `i` zapisuje we współdzielonej pamięci podręcznej na pozycji `p`, inni pracownicy czytający tę pozycję mogą bezpośrednio korzystać z wpisu w pamięci podręcznej — bez konieczności ponownej rotacji.

W modelu pozycji wyuczonej lub pozycji absolutnej, Hogwild! wymagałoby unieważnienia pamięci podręcznej przy każdym współbieżnym zapisie. Dzięki RoPE pamięć podręczna pozostaje stabilna.

### Matematyka na ścianie

Niech `T_serial` będzie czasem, w którym jeden pracownik samodzielnie rozwiąże problem. Niech `p` będzie ułamkiem możliwym do zrównoleglenia na poziomie zadania. Niech `c` będzie kosztem koordynacji poszczególnych kroków (czytanie rozszerzonej pamięci podręcznej, decydowanie, co zapisać).

Czas pojedynczego pracownika: `T_serial`.
N-pracownik Hogwild! czas, jeśli koordynacja jest bezpłatna: `T_serial * ((1 - p) + p / N)`. Klasyczny Amdahl.
Z narzutem na koordynację: `T_serial * ((1 - p) + p / N) + c * steps_per_worker`.

Aby pracownik był produktywny, `c` musi być mały w stosunku do czasu dekodowania na krok. W modelach rozumowania produkujących tokeny o wartości ponad 5 tys. pracowników można sobie pozwolić na setki tokenów kosztów ogólnych i nadal wychodzą na prowadzenie. W przypadku krótkich zadań na czacie dominuje koordynacja i Hogwild! jest gorszy od serialu.

### Konkretny przykład

Problem z rozumowaniem: 10 tysięcy znaków łańcucha myślowego. Załóżmy, że problem ma `p = 0.7` treść, którą można zrównoleglić (różne strategie dowodowe, różne analizy przypadków) i `c = 200` tokeny narzutu koordynacji na pracownika. Z pracownikami `N = 4`:

- Czas szeregowy: 10000 kroków dekodowania.
- Dziki! czas: 10000 * (0,3 + 0,7 / 4) + 200 * 4 = 10000 * 0,475 + 800 = 5550 kroków dekodowania.
- Przyspieszenie: 10000 / 5550 = 1,8x.

To skromne. Ale w przypadku dłuższych problemów z rozumowaniem (50 tys. Tokenów) narzut koordynacyjny amortyzuje się, a przyspieszenie wzrasta 2,5-3x. Hogwild! jest odpowiednikiem wnioskowania równoległości na poziomie wątku w języku, który umożliwia naturalne pisanie kodu wielowątkowego.

### Kiedy sięgnąć po Hogwild!

- Długie problemy z rozumowaniem (tysiące tokenów), w przypadku których zadanie można zrównoleglić w ramach niezależnych celów cząstkowych.
- Modele rozumowania, które zostały przeszkolone do myślenia krok po kroku. Modele nierozumne nie koordynują się dobrze.
- Wdrożenia jednowęzłowe z wystarczającą ilością pamięci VRAM do przechowywania współdzielonej pamięci podręcznej oraz N procesów roboczych. Pamięć podręczna jest współdzielona, ​​ale każdy pracownik ma własną pamięć aktywacji.

### Kiedy tego nie robić

- Krótki interaktywny czat. Dominuje obciążenie koordynacyjne.
- Zadania, które nie są zrównoleglone (pojedynczy dowód liniowy, pojedyncza kompilacja). N=1 to maksimum.
- Modele nierozumne. Nie pojawia się żadna koordynacja.
- Wdrożenia wielowęzłowe. Udostępniona pamięć podręczna wymaga bardzo szybkiej synchronizacji między procesami roboczymi. Wewnątrz węzła jest w porządku; cross-node to katastrofa związana z opóźnieniami.

### Stan eksperymentalny

Od kwietnia 2026 r. Hogwild! to metoda badawcza z implementacją PyTorch typu open source. Nie doszło do przyjęcia produkcyjnego. Trzy blokery:

1. Zarządzanie współdzieloną pamięcią podręczną KV w ramach współbieżnych procesów nie jest trywialne.
2. Wschodząca koordynacja zależy od zadania; benchmarki są wciąż opracowywane.
3. Przyspieszenie jest niewielkie w porównaniu z tym, co już zapewnia dekodowanie spekulatywne, i można je połączyć, ale połączona inżynieria to inna warstwa.

Warto wiedzieć. Warto poeksperymentować. Nie warto jeszcze stawiać na produkt.

## Zbuduj to

`code/main.py` implementuje zabawkę Hogwild! symulator:

- Dwa procesy robocze, każdy deterministyczny „LLM”, który generuje jedną z kilku kategorii tokenów (token pracy, token obserwacji, token współrzędnych) ze znanym prawdopodobieństwem.
- Wspólna pamięć podręczna (tylko lista tokenów), którą obaj pracownicy czytają i zapisują.
- Prosta logika koordynacji: kiedy pracownik widzi, że drugi pracownik wyprodukował już wystarczającą liczbę żetonów pracy w danej kategorii, wybiera inną kategorię.

Symulator działa ze stałym budżetem krokowym i raportuje:

- Całkowita liczba wyprodukowanych żetonów pracy.
- Całkowity czas ściany (liczba kroków pracownika).
- Efektywne przyspieszenie w stosunku do pojedynczego pracownika.
- Ślad, który pracownik napisał który token.

### Krok 1: współdzielona pamięć podręczna

Lista, do której dołączają obaj pracownicy. Proste blokowanie (Python `threading.Lock`) w rzeczywistej implementacji; symulujemy za pomocą licznika.

### Krok 2: pętla procesu roboczego

Każdy pracownik na każdym etapie:

- Odczytuje bieżącą udostępnioną pamięć podręczną.
- Decyduje, jaką kategorię tokena zapisać w oparciu o to, co już tam jest.
- Zapisuje jeden token.

### Krok 3: heurystyka koordynacji

Jeśli kategoria X ma już K tokenów w pamięci podręcznej, a docelową kategorią pracownika jest X, pracownik przełącza się do kategorii Y. Jest to zabawka zastępująca zachowanie w modelu rozumowania: „zauważ, że to już zostało omówione, zamiast tego zrób coś innego”.

### Krok 4: zmierzone przyspieszenie

Uruchom symulator z N=1 pracownikiem i N=2 pracownikami, przy takim samym całkowitym budżecie kroków. Policz wyprodukowane żetony pracy. N=2 powinno wygenerować około 1,5-1,8 razy więcej żetonów pracy ze względu na podział zadań oparty na koordynacji.

### Krok 5: podkreśl koordynację

Zmniejsz czułość heurystyki koordynacji. Uruchom ponownie. Zauważ, że bez dobrej koordynacji N=2 generuje te same żetony, a przyspieszenie spada poniżej 1. Zgadza się to z obserwacjami artykułu: sztuczka działa tylko wtedy, gdy pracownicy mają zdolność rozumowania do samokoordynacji.

## Użyj tego

Hogwild! integracja z produkcją od kwietnia 2026 r. ma charakter badawczy. Referencyjna implementacja firmy Yandex/HSE/IST jest oparta na PyTorch i jest przeznaczona dla jednowęzłowych, wieloprocesowych konfiguracji w modelach DeepSeek-R1 i QwQ.

Pragmatyczna ścieżka adopcji:

1. Sprofiluj obciążenie pracą związaną z rozumowaniem. Zmierz część tokenów eksploracyjnych (wiele strategii, analizy przypadków, wyszukiwanie) w porównaniu z liniowymi.
2. Jeśli dominuje eksploracja, stwórz dwuosobowego Hogwilda! eksperyment. Zmierz poprawę czasu na ścianie.
3. Jeśli poprawa jest mniejsza niż 1,3x, znajdujesz się w reżimie zdominowanym przez koordynację. Wróć do pracy jednoosobowej.
4. Jeśli poprawa przekracza 1,5x, naciśnij N=4 i zmierz ponownie. Malejące zyski zwykle osiągają okolice N=4-8.

Połącz z dekodowaniem spekulatywnym: każdy Hogwild! pracownik może samodzielnie korzystać z dekodowania specyfikacji. Obydwa przyspieszenia mnożą się (w przybliżeniu), dając dekodowanie specyfikacji 3x i Hogwild 1,8x! do efektywnego dekodowania 5,4x w porównaniu z naiwnym dekodowaniem jednego pracownika.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-parallel-inference-router.md`. Biorąc pod uwagę profil obciążenia rozumowaniem (budżet tokena, profil równoległości zadań, rodzina modeli, cel wdrożenia), wyznacza trasy pomiędzy strategiami głosowania, drzewa myśli, wielu agentów, Hogwild! i spekulatywnego dekodowania.

## Ćwiczenia

1. Uruchom `code/main.py` z ustawieniami domyślnymi. Potwierdź N=2 Hogwild! konfiguracja generuje więcej żetonów pracy niż linia bazowa N=1 w tym samym czasie ściany.

2. Zmniejsz siłę heurystyki koordynacji (ustaw `coordination_weight=0.1`). Ponowne odtworzenie. Pokaż, że przyspieszenie zanika. Wyjaśnij dlaczego: pracownicy dublują wysiłki, gdy nie mogą koordynować swoich działań.

3. Oblicz oczekiwaną Hogwild! przyspieszenie zadania wnioskowania zawierającego 50 tys. tokenów z `p=0.8, c=500` i N=4 pracownikami. Zrób to samo dla zadania czatu z tokenem 1 tys. z `p=0.3, c=200` i N=4. Dlaczego jeden jest zwycięstwem, a drugi porażką?

4. Przeczytaj Hogwild! Sekcja 4 artykułu (ocena wstępna). Zidentyfikuj dwa tryby awarii zgłaszane przez autorów. Opisz, w jaki sposób lepsza podpowiedź koordynacyjna może złagodzić każde z nich.

5. Połącz Hogwild! z dekodowaniem spekulatywnym w zabawce: każdy pracownik używa wewnętrznie 2-tokenowego dekodowania spec. Zgłoś multiplikatywne przyspieszenie. Jaki problem z księgowością pojawia się, gdy dwóch pracowników chce rozszerzyć ten sam prefiks współdzielonej pamięci podręcznej?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Hogwild! | „Pracownicy równoległi, współdzielona pamięć podręczna” | N instancji tego samego LLM działających jednocześnie z jedną współdzieloną pamięcią podręczną KV; wschodząca koordynacja poprzez samopodpowiadanie |
| Wspólna pamięć podręczna KV | „Ośrodek koordynacyjny” | Pojedynczy rosnący bufor KV, który wszyscy pracownicy czytają i zapisują; umożliwia natychmiastową widoczność tokenów wśród pracowników |
| Wschodząca koordynacja | „Nie jest potrzebne żadne szkolenie” | LLM zdolne do rozumowania mogą odczytywać współdzieloną pamięć podręczną i dzielić pracę bez żadnego dostrajania lub jawnego protokołu |
| Koszty koordynacji (c) | „Żetony wydane na orientację” | Koszt odczytu rozszerzonej pamięci podręcznej na pracownika i podjęcia decyzji, co zrobić; musi pozostać mały w porównaniu do całkowitego czasu dekodowania |
| Ułamek równoległy (p) | „Co może działać równolegle” | Równoległość na poziomie zadań: część całkowitej pracy, która nie jest wewnętrznie sekwencyjna |
| RoPE umożliwia Hogwild! | „Pozycje obrotowe są niezmienne przy przesunięciu” | Ponieważ pozycje są rotacjami, zapisywanie we współdzielonej pamięci podręcznej nie wymaga ponownego obliczania wcześniejszych tokenów |
| Zespół do głosowania | „Uruchom N, wybierz większość” | Najprostsza topologia wnioskowania równoległego; przydatne do klasyfikacji, mniej do długiego rozumowania |
| Drzewo myśli | „Gałąź i przycinanie” | Strategia rozumowania, która bada wiele gałęzi i suszonych śliwek; wyraźna logika koordynacji |
| Framework wieloagentowy | „Przypisz podzadania” | Każdy agent otrzymuje rolę; koordynator koordynuje; duże obciążenie protokołu |

## Dalsze czytanie

- [Rodionow i in. — Dziki! Wnioskowanie: równoległe generowanie LLM poprzez współbieżną uwagę (arXiv:2504.06261)](https://arxiv.org/abs/2504.06261) — Hogwild! artykuł, wstępna ocena QwQ i DeepSeek-R1
- [Recht, Re, Wright, Niu — Hogwild!: A Lock-Free Approach to Parallelizing Stochastic Gradient Descent (arXiv:1106.5730, NeurIPS 2011)](https://arxiv.org/abs/1106.5730) — oryginalny Hogwild!, początek nazewnictwa
- [Su i in. — RoFormer: ulepszony transformator z osadzaniem pozycji obrotowej (arXiv:2104.09864)](https://arxiv.org/abs/2104.09864) — RoPE, właściwość umożliwiająca wnioskowanie o współdzielonej pamięci podręcznej
- [Yao i in. — Drzewo myśli: celowe rozwiązywanie problemów za pomocą modeli wielkojęzykowych (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) — strategia rozumowania oparta na drzewie myśli Hogwild! leży prostopadle do
- [Lewiatan i in. — Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne (arXiv:2211.17192)](https://arxiv.org/abs/2211.17192) — dekodowanie spekulatywne, paralelizm wewnątrz sekwencji Hogwild! komponuje z
- [Hogwild! referencyjna implementacja PyTorch](https://github.com/eqimp/hogwild_llm) — jedyne źródło prawdy o eksperymentach artykułu