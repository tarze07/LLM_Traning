# Async i Hogwild! Wnioskowanie

> Dekodowanie spekulatywne (faza 10 · 15) zrównolegluje tokeny w obrębie jednej sekwencji. Struktury wieloagentowe działają równolegle na poziomie całych sekwencji, lecz wymagają jawnej koordynacji — głosowania lub podziału podzadań. Hogwild! Inference (Rodionov i in., arXiv:2504.06261) idzie inną drogą: uruchamia N instancji tego samego LLM współdzielących jedną pamięć podręczną KV. Każdy pracownik natychmiast widzi tokeny wygenerowane przez pozostałych. Nowoczesne modele rozumowania — QwQ, DeepSeek-R1 — potrafią samodzielnie koordynować pracę poprzez wspólną pamięć podręczną, bez żadnego dodatkowego dostrajania. Podejście jest eksperymentalne, ale otwiera zupełnie nową oś równoległości wnioskowania, prostopadłą do dekodowania spekulatywnego. Niniejsza lekcja przedstawia dwuagentowy symulator Hogwild! zbudowany w stdlib Pythona i wyjaśnia, dlaczego współpraca za pośrednictwem wspólnej pamięci podręcznej wyłania się z istniejących zdolności modelu.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 10 · 12 (optymalizacja wnioskowania), Faza 10 · 15 (dekodowanie spekulatywne)
**Czas:** ~60 minut

## Cele nauczania

- Opisać trzy popularne topologie równoległego LLM (głosowanie, podział podzadań, Hogwild!) oraz wskazać problemy, do których rozwiązania każda z nich służy.
- Przedstawić rdzeń konfiguracji Hogwild!: wielu pracowników, jedna wspólna pamięć podręczna KV i koordynacja wyłaniająca się z automatycznych podpowiedzi.
- Obliczyć przyspieszenie Hogwild! w czasie rzeczywistym jako funkcję liczby pracowników `N`, równoległości na poziomie zadania `p` i kosztu koordynacji `c`.
- Zaimplementować dwuagentowy symulator na przykładowym problemie i zaobserwować wyłaniający się podział zadań.

## Problem

Nowoczesne LLM rozwiązują trudne problemy, budując długie łańcuchy rozumowań — 5000 tokenów krok po kroku to norma, a dziesiątki tysięcy tokenów zdarzają się przy głębokich problemach matematycznych. Przy prędkości dekodowania 35 tokenów/s w modelu 70B, 50 tys. tokenów to 24 minuty oczekiwania. Trudno mówić o interaktywności.

Dekodowanie spekulatywne (faza 10 · 15) zapewnia 3–5-krotne przyspieszenie dzięki zrównolegleniu wewnątrz jednej sekwencji. Za tym progiem napotykamy twardy sufit: każdy nowy token zależy od wszystkich poprzednich, co jest nieodłączną cechą dekodowania autoregresyjnego.

Nasuwa się pytanie: czy można zrównoleglić pracę na poziomie wielu sekwencji? Uruchomić kilka kopii tego samego modelu na tym samym problemie i pozwolić im współpracować — czy podzielą między sobą pracę?

Wcześniejsze podejścia to: zespoły głosujące (uruchom N modeli, wybierz odpowiedź większości), drzewo myśli (rozgałęzianie ścieżek rozumowania i przycinanie) oraz struktury wieloagentowe (każdy agent dostaje podzadanie, koordynator zarządza całością). Każde z nich sprawdza się w określonych zastosowaniach, ale wszystkie wymagają jawnych mechanizmów koordynacji — reguł głosowania, logiki rozgałęziania i przycinania lub protokołów komunikacji między agentami.

Hogwild! Inference przyjmuje inne podejście. N pracowników korzysta z jednej pamięci podręcznej KV. Każdy z nich natychmiast widzi tokeny wygenerowane przez pozostałych — tak jakby stanowiły część jego własnego kontekstu. Pracownicy, bez żadnego dodatkowego treningu ani dostrajania, sami ustalają podział pracy. Modele rozumowania (QwQ, DeepSeek-R1, tryb rozumowania rodziny Claude) potrafią odczytywać wspólną pamięć podręczną i wnioskować: „Widzę, że pracownik 2 już zajął się przypadkiem podstawowym — zajmę się krokiem indukcyjnym".

Przyspieszenie zależy od rodzaju zadania i od kwietnia 2026 r. pozostaje w fazie eksperymentalnej. Warto jednak poznać ten pomysł, ponieważ otwiera nową oś równoległości wnioskowania.

## Koncepcja

### Konfiguracja

Uruchamiamy N procesów roboczych działających na tym samym LLM. Zamiast oddzielnej pamięci podręcznej KV dla każdego pracownika, utrzymywana jest JEDNA wspólna pamięć podręczna. Gdy pracownik `i` generuje token `t_j`, token ten trafia do wspólnej pamięci podręcznej na kolejnej pozycji. Gdy pracownik `k` wykonuje następny krok, odczytuje bieżący stan pamięci podręcznej — a więc wszystko, co do tej pory wygenerowali wszyscy N pracownicy.

Pracownicy jednocześnie zapisują tokeny, ścigając się o kolejne pozycje. Nie ma przypisanych pozycji dla poszczególnych pracowników — pamięć podręczna to jedna rosnąca sekwencja, a kolejność wpisów wyznacza czas ich dotarcia.

### Dlaczego wyłania się koordynacja

Wszyscy pracownicy współdzielą tę samą podpowiedź, zazwyczaj w stylu: „Jesteś jedną z N instancji pracujących wspólnie nad tym problemem. Każda instancja odczytuje wspólną pamięć i widzi, co napisały pozostałe. Unikaj zbędnej pracy". Taka zachęta w połączeniu ze wspólną pamięcią podręczną wystarczy. Modele rozumowania odczytują pamięć podręczną, dostrzegają, które części problemu zostały już podjęte, i — często, choć nie zawsze — kierują się ku niezbadanym fragmentom.

Hogwild! (Rodionov i in., 2025) opisuje między innymi następujące obserwacje:

- Pracownicy formułują plany i przekazują je sobie nawzajem za pośrednictwem pamięci podręcznej.
- Pracownicy wykrywają błędy w rozumowaniu innych i zwracają na nie uwagę.
- Pracownicy dostosowują się, gdy plan zawodzi, i proponują alternatywy.
- Gdy w podpowiedzi pojawi się prośba o sprawdzenie nadmiarowości, pracownicy ją wykrywają i zmieniają kierunek.

Żadne z tych zachowań nie wymaga dostrajania. Wyłaniają się wyłącznie z istniejących zdolności rozumowania modelu.

### Nazewnictwo

Nazwa nawiązuje do Hogwild! SGD (Recht i in., 2011) — optymalizatora działającego na asynchronicznych aktualizacjach. Analogia jest prosta: w Hogwild! SGD wszyscy pracownicy asynchronicznie zapisują do wspólnego wektora parametrów; w Hogwild! Inference wszyscy pracownicy zapisują do wspólnej pamięci podręcznej KV. Obydwa podejścia opierają się na empirycznej zbieżności, a nie na gwarancjach synchronizacji.

### Dlaczego RoPE to umożliwia

Rotary Position Embeddings (RoPE, Su i in. 2021) kodują informację o pozycji jako obrót wektorów Q i K. Ponieważ pozycja jest reprezentowana przez obrót, a nie przez wbudowane przesunięcie, można ją zmienić bez ponownego obliczania wpisu w pamięci podręcznej KV. Gdy pracownik `i` zapisuje token na pozycji `p` we wspólnej pamięci podręcznej, pozostali pracownicy mogą bezpośrednio korzystać z tego wpisu — bez konieczności ponownego przeliczania.

W modelach z wyuczonymi pozycjami lub pozycjami absolutnymi Hogwild! wymagałoby unieważnienia pamięci podręcznej przy każdym współbieżnym zapisie. Dzięki RoPE pamięć podręczna pozostaje stabilna.

### Matematyka czasu rzeczywistego

Niech `T_serial` oznacza czas, w którym jeden pracownik samodzielnie rozwiązuje problem. Niech `p` będzie ułamkiem zadania możliwym do zrównoleglenia. Niech `c` oznacza koszt koordynacji na krok (odczyt rozszerzonej pamięci podręcznej i podjęcie decyzji o kolejnym tokenie).

Czas jednego pracownika: `T_serial`.
Czas N pracowników w Hogwild! bez kosztu koordynacji: `T_serial * ((1 - p) + p / N)`. To klasyczne prawo Amdahla.
Z kosztem koordynacji: `T_serial * ((1 - p) + p / N) + c * steps_per_worker`.

Aby pracownicy odnosili korzyść z równoległości, `c` musi być małe w stosunku do czasu dekodowania jednego kroku. W modelach rozumowania generujących ponad 5 tys. tokenów można sobie pozwolić na setki tokenów narzutu koordynacyjnego i nadal uzyskiwać zysk. W przypadku krótkich rozmów chatbotowych koszt koordynacji dominuje i Hogwild! wypada gorzej niż podejście szeregowe.

### Przykład liczbowy

Weźmy zadanie rozumowania o łańcuchu myślowym długości 10 tys. tokenów. Przyjmijmy `p = 0.7` (70% zadania da się zrównoleglić — różne strategie dowodowe, różne analizy przypadków) i `c = 200` tokenów narzutu koordynacyjnego na pracownika. Dla `N = 4` pracowników:

- Czas szeregowy: 10 000 kroków dekodowania.
- Czas Hogwild!: 10 000 * (0,3 + 0,7 / 4) + 200 * 4 = 10 000 * 0,475 + 800 = 5 550 kroków dekodowania.
- Przyspieszenie: 10 000 / 5 550 = 1,8x.

To skromny wynik. Jednak przy dłuższych zadaniach (50 tys. tokenów) koszt koordynacji amortyzuje się, a przyspieszenie rośnie do 2,5–3x. Hogwild! jest dla wnioskowania tym, czym równoległość wątkowa dla języków obsługujących wielowątkowość — naturalnym sposobem skalowania.

### Kiedy sięgać po Hogwild!

- Długie zadania rozumowania (tysiące tokenów), które dają się podzielić na niezależne podcele.
- Modele rozumowania przeszkolone do myślenia krok po kroku. Modele bez zdolności rozumowania koordynują się słabo.
- Środowiska jednowęzłowe z wystarczającą ilością pamięci VRAM na wspólną pamięć podręczną i N pracowników. Pamięć podręczna jest współdzielona, ale każdy pracownik ma własną pamięć aktywacji.

### Kiedy nie stosować Hogwild!

- Krótkie, interaktywne rozmowy — koszt koordynacji dominuje.
- Zadania sekwencyjne z natury (pojedynczy dowód liniowy, pojedyncza kompilacja) — N=1 to optimum.
- Modele bez zdolności rozumowania — koordynacja nie wyłoni się.
- Środowiska wielowęzłowe — wspólna pamięć podręczna wymaga bardzo szybkiej synchronizacji między węzłami; wewnątrz węzła to nie problem, ale synchronizacja między węzłami generuje katastrofalne opóźnienia.

### Stan eksperymentalny

Od kwietnia 2026 r. Hogwild! pozostaje metodą badawczą z otwartą implementacją w PyTorch. Nie trafił jeszcze do produkcji. Trzy główne przeszkody:

1. Zarządzanie wspólną pamięcią podręczną KV w środowisku współbieżnych procesów jest nietrywialnym wyzwaniem inżynieryjnym.
2. Wyłaniająca się koordynacja zależy od rodzaju zadania, a testy porównawcze są wciąż opracowywane.
3. Przyspieszenie jest skromne w zestawieniu z tym, co już oferuje dekodowanie spekulatywne; można je łączyć, ale połączone wdrożenie to osobna warstwa złożoności.

Warto wiedzieć, warto eksperymentować. Na wdrożenie produkcyjne jest jednak za wcześnie.

## Zbuduj to

`code/main.py` implementuje zabawkowy symulator Hogwild!:

- Dwóch pracowników — każdy to deterministyczny „LLM" generujący tokeny z jednej z kilku kategorii (token pracy, token obserwacji, token koordynacji) z określonym prawdopodobieństwem.
- Wspólna pamięć podręczna (prosta lista tokenów), którą obaj pracownicy odczytują i uzupełniają.
- Prosta logika koordynacji: gdy pracownik zauważy, że drugi wygenerował już wystarczającą liczbę tokenów w danej kategorii, przełącza się na inną.

Symulator działa w ramach stałego budżetu kroków i raportuje:

- Łączną liczbę wygenerowanych tokenów pracy.
- Całkowity czas wykonania (liczba kroków pracownika).
- Efektywne przyspieszenie względem jednego pracownika.
- Ślad pokazujący, który pracownik napisał który token.

### Krok 1: wspólna pamięć podręczna

Lista, do której dołączają obaj pracownicy. W rzeczywistej implementacji wymagałaby blokowania (Python `threading.Lock`); w symulatorze korzystamy ze zwykłego licznika.

### Krok 2: pętla pracownika

Na każdym kroku pracownik:

- Odczytuje bieżący stan wspólnej pamięci podręcznej.
- Decyduje, jaką kategorię tokenu zapisać, na podstawie tego, co już się w niej znajduje.
- Zapisuje jeden token.

### Krok 3: heurystyka koordynacji

Jeśli kategoria X ma już K tokenów w pamięci podręcznej, a pracownik planuje zapisać token kategorii X, przełącza się na kategorię Y. To zabawkowe odwzorowanie zachowania modelu rozumowania: „widzę, że to już zostało omówione — zajmę się czymś innym".

### Krok 4: mierzenie przyspieszenia

Uruchom symulator z N=1 i N=2 pracownikami przy tym samym łącznym budżecie kroków. Policz wygenerowane tokeny pracy. Konfiguracja N=2 powinna wyprodukować około 1,5–1,8 razy więcej tokenów pracy dzięki koordynowanemu podziałowi zadań.

### Krok 5: zaburzenie koordynacji

Zmniejsz czułość heurystyki koordynacji. Uruchom ponownie. Bez sprawnej koordynacji N=2 generuje te same tokeny co N=1, a przyspieszenie spada poniżej 1. Jest to zgodne z obserwacjami z artykułu: metoda działa tylko wtedy, gdy pracownicy mają wystarczające zdolności rozumowania do samodzielnej koordynacji.

## Użyj tego

Integracja Hogwild! z produkcją pozostaje od kwietnia 2026 r. w fazie badawczej. Referencyjna implementacja Yandex/HSE/IST jest oparta na PyTorch i przeznaczona do konfiguracji jednowęzłowych, wieloprocesowych na modelach DeepSeek-R1 i QwQ.

Pragmatyczna ścieżka wdrożenia:

1. Sprofiluj obciążenie związane z rozumowaniem. Zmierz udział tokenów eksploracyjnych (wiele strategii, analizy przypadków, przeszukiwanie) względem tokenów sekwencyjnych.
2. Jeśli eksploracja dominuje, przeprowadź eksperyment z dwoma pracownikami Hogwild!. Zmierz poprawę czasu wykonania.
3. Jeśli poprawa jest mniejsza niż 1,3x, jesteś w reżimie zdominowanym przez koszty koordynacji. Wróć do jednego pracownika.
4. Jeśli poprawa przekracza 1,5x, wypróbuj N=4 i zmierz ponownie. Malejące zyski pojawiają się zwykle w okolicach N=4–8.

Połącz z dekodowaniem spekulatywnym: każdy pracownik Hogwild! może niezależnie korzystać z dekodowania spekulatywnego. Oba przyspieszenia mnożą się w przybliżeniu — przykładowo 3x ze spekulatywnego dekodowania i 1,8x z Hogwild! dają łącznie około 5,4x w porównaniu z naiwnym dekodowaniem jednego pracownika.

## Wyślij to

Ta lekcja wprowadza `outputs/skill-parallel-inference-router.md`. Na podstawie profilu obciążenia rozumowaniem (budżet tokenów, profil równoległości zadania, rodzina modeli, cel wdrożenia) kieruje wyborem spośród strategii: głosowanie, drzewo myśli, wiele agentów, Hogwild! i dekodowanie spekulatywne.

## Ćwiczenia

1. Uruchom `code/main.py` z domyślnymi ustawieniami. Potwierdź, że konfiguracja N=2 Hogwild! generuje więcej tokenów pracy niż linia bazowa N=1 w tym samym czasie wykonania.

2. Zmniejsz siłę heurystyki koordynacji (ustaw `coordination_weight=0.1`). Uruchom ponownie. Pokaż, że przyspieszenie zanika. Wyjaśnij dlaczego: pracownicy powielają wysiłki, gdy nie potrafią się koordynować.

3. Oblicz oczekiwane przyspieszenie Hogwild! dla zadania rozumowania o długości 50 tys. tokenów z `p=0.8, c=500` i N=4 pracownikami. Następnie powtórz obliczenie dla krótkotrwałego zadania chatbotowego o długości 1 tys. tokenów z `p=0.3, c=200` i N=4. Dlaczego jedno przynosi zysk, a drugie stratę?

4. Przeczytaj sekcję 4 artykułu Hogwild! (wstępna ocena). Wskaż dwa tryby awarii opisane przez autorów. Opisz, jak lepsza podpowiedź koordynacyjna mogłaby każdy z nich złagodzić.

5. Połącz Hogwild! z dekodowaniem spekulatywnym w symulatorze: każdy pracownik wewnętrznie stosuje 2-tokenowe dekodowanie spekulatywne. Wyznacz mnożnikowe przyspieszenie. Jaki problem z zarządzaniem stanem pojawia się, gdy dwóch pracowników chce jednocześnie rozszerzyć ten sam prefiks wspólnej pamięci podręcznej?

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|----------------|--------------------------------------|
| Hogwild! | „Równolegli pracownicy, wspólna pamięć podręczna" | N instancji tego samego LLM działających jednocześnie z jedną wspólną pamięcią podręczną KV; koordynacja wyłania się z automatycznych podpowiedzi |
| Wspólna pamięć podręczna KV | „Centrum koordynacji" | Jeden rosnący bufor KV, który wszyscy pracownicy odczytują i zapisują; umożliwia natychmiastową widoczność tokenów między pracownikami |
| Wyłaniająca się koordynacja | „Bez dodatkowego treningu" | LLM zdolne do rozumowania mogą odczytywać wspólną pamięć podręczną i dzielić pracę bez dostrajania ani jawnego protokołu |
| Koszt koordynacji (c) | „Tokeny wydane na orientację" | Koszt odczytu rozszerzonej pamięci podręcznej i podjęcia decyzji o kolejnym tokenie; musi być mały względem całkowitego czasu dekodowania |
| Ułamek równoległy (p) | „Co może działać równolegle" | Równoległość na poziomie zadania: część całkowitej pracy, która nie jest z natury sekwencyjna |
| RoPE umożliwia Hogwild! | „Pozycje obrotowe są niezmienne przy przesunięciu" | Ponieważ pozycje są obrotami, zapis we wspólnej pamięci podręcznej nie wymaga ponownego obliczania wcześniejszych tokenów |
| Zespół głosujący | „Uruchom N, wybierz większość" | Najprostsza topologia wnioskowania równoległego; przydatna przy klasyfikacji, mniej przy długim rozumowaniu |
| Drzewo myśli | „Rozgałęziaj i przycinaj" | Strategia rozumowania eksplorująca wiele gałęzi i przycinająca słabsze; wymaga jawnej logiki koordynacji |
| Framework wieloagentowy | „Przydziel podzadania" | Każdy agent otrzymuje rolę, koordynator zarządza całością; duże obciążenie protokołu komunikacyjnego |

## Dalsze czytanie

- [Rodionow i in. — Hogwild! Inference: Asynchronous Large Language Model Inference with Dynamic Speculative Decoding (arXiv:2504.06261)](https://arxiv.org/abs/2504.06261) — artykuł Hogwild!, wstępna ocena na QwQ i DeepSeek-R1
- [Recht, Re, Wright, Niu — Hogwild!: A Lock-Free Approach to Parallelizing Stochastic Gradient Descent (arXiv:1106.5730, NeurIPS 2011)](https://arxiv.org/abs/1106.5730) — oryginalny Hogwild!, źródło nazwy
- [Su i in. — RoFormer: Enhanced Transformer with Rotary Position Embedding (arXiv:2104.09864)](https://arxiv.org/abs/2104.09864) — RoPE, własność umożliwiająca wnioskowanie ze wspólną pamięcią podręczną
- [Yao i in. — Tree of Thoughts: Deliberate Problem Solving with Large Language Models (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) — strategia drzewa myśli, prostopadła do Hogwild!
- [Lewiatan i in. — Fast Inference from Transformers via Speculative Decoding (arXiv:2211.17192)](https://arxiv.org/abs/2211.17192) — dekodowanie spekulatywne, równoległość wewnątrz sekwencji, którą Hogwild! uzupełnia
- [Hogwild! referencyjna implementacja PyTorch](https://github.com/eqimp/hogwild_llm) — jedyne źródło prawdy o eksperymentach z artykułu
