# Agenci przeglądarki i długoterminowe zadania sieciowe

> ChatGPT Agent (lipiec 2025 r.) połączył funkcje Operatora i zaawansowanych badań (Deep Research) w jednym agencie przeglądarki i terminala, podnosząc wynik SOTA na benchmarku BrowseComp do 68,9%. OpenAI zamknęło projekt autonomicznego Operatora 31 sierpnia 2025 r. w ramach konsolidacji oferty produktowej. Przejęcie firmy Vercept przez Anthropic pozwoliło podnieść wynik modelu Claude Sonnet w benchmarku OSWorld z poziomu poniżej 15% do 72,5%. Projekt WebArena-Verified (ServiceNow, ICLR 2026) wyeliminował błędy w oryginalnej WebArenie, zmniejszając odsetek fałszywie negatywnych wyników o 11,3 punktu procentowego, i wprowadził trudny podzbiór (Hard subset) zawierający 258 zadań. Wyniki te są namacalne. Podobnie jak zagrożenia: szef ds. przygotowania (Preparedness) w OpenAI otwarcie przyznał, że pośrednie wstrzykiwanie instrukcji (indirect prompt injection) w agentach przeglądarkowych „nie jest podatnością, którą można w pełni załatać”. Do udokumentowanych ataków z lat 2025–2026 należą m.in. Tainted Memories (wykorzystujący Atlas CSRF), HashJack (wykryty przez Cato Networks) oraz przejęcia sesji jednym kliknięciem w Perplexity Comet.

**Typ:** Ucz się
**Języki:** Python (stdlib, model powierzchni ataku z pośrednim wtryskiem)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~45 minut

## Problem

Agent przeglądarkowy to system działający w długim horyzoncie czasowym, który analizuje niezweryfikowane treści i podejmuje na ich podstawie decyzje. Każda strona odwiedzana przez agenta stanowi dane wejściowe (input), których nie napisał użytkownik, a każdy formularz na stronie jest potencjalnym kanałem do przesyłania złośliwych poleceń. Przypadki ataków z lat 2025–2026 pokazują, że nie są to zagrożenia czysto teoretyczne: Tainted Memories pozwala napastnikowi na trwałe zapisanie złośliwych instrukcji w pamięci agenta za pomocą odpowiednio przygotowanej strony; HashJack ukrywa złośliwe komendy we fragmentach adresów URL odwiedzanych przez agenta; z kolei Perplexity Comet umożliwia przejęcie kontroli nad agentem za pomocą jednego kliknięcia.

Perspektywa obrony przed tymi zagrożeniami jest trudna. Szef ds. przygotowania w OpenAI otwarcie wypowiedział to, co wielu wolało milczeć: pośrednie wstrzykiwanie instrukcji „nie jest podatnością, którą można w pełni wyeliminować”. Wynika to z faktu, że atak ma miejsce na granicy między przetwarzaniem danych a działaniem agenta, która jest architektonicznie rozmyta – każdy token odczytany przez model językowy może w zasadzie zostać potraktowany jako instrukcja do wykonania.

W tej lekcji omówimy powierzchnię ataku, zaprezentujemy benchmarki (BrowseComp, OSWorld, WebArena-Verified) oraz przedstawimy uproszczony model scenariusza pośredniego wstrzykiwania instrukcji, co pozwoli na zaprojektowanie skutecznych mechanizmów obronnych omawianych w Lekcjach 14 i 18.

## Koncepcja

### Krajobraz technologiczny w 2026 roku (systemy w pigułce)

**ChatGPT Agent (OpenAI):** Uruchomiony w lipcu 2025 roku, łączy funkcje Operatora (przeglądanie sieci) i Deep Research (wielogodzinne, pogłębione analizy). Samodzielny projekt Operatora został zamknięty 31 sierpnia 2025 roku w celu konsolidacji produktu. Osiągnął status SOTA w benchmarku BrowseComp z wynikiem 68,9%, wykazując też świetną skuteczność w OSWorld oraz WebArena-Verified.

**Claude Sonnet + Vercept (Anthropic):** Przejęcie startupu Vercept przez Anthropic pozwoliło mocno rozwinąć funkcje obsługi komputera (computer use). Wynik modelu Claude Sonnet w benchmarku OSWorld wzrósł z poziomu poniżej 15% do 72,5%. Funkcjonalność Claude Computer Use jest udostępniana deweloperom jako jedno z narzędzi API.

**Gemini 3 Pro z integracją przeglądarkową (DeepMind):** Bezpośrednia integracja z przeglądarką pozwala na sprawne kontrolowanie systemu. Benchmark FSF v3 (kwiecień 2026 r., patrz Lekcja 20) szczegółowo monitoruje autonomię modeli, zwłaszcza w zadaniach z zakresu automatyzacji prac badawczo-rozwojowych (R&D) w obszarze uczenia maszynowego.

**WebArena-Verified (ServiceNow, ICLR 2026):** Rozwiązuje znany problem oryginalnej WebAreny, w której około 11,3% wyników stanowiły fałszywe negatywy (zadania oznaczone jako niezaliczone, mimo że agent rozwiązał je prawidłowo). Zweryfikowana wersja ocenia pracę agentów na podstawie zweryfikowanych przez człowieka kryteriów i wprowadza podzbiór zadań trudnych (Hard subset) zawierający 258 przypadków testowych (publikacja ICLR 2026, patrz: openreview.net/forum?id=94tlGxmqkN).

### Porównanie benchmarków: BrowseComp vs OSWorld vs WebArena

| benchmark | Co mierzy | Horyzont |
|---|---|---|
| BrowseComp | Wyszukiwanie faktów w otwartym internecie pod presją czasu | minuty |
| OSWorld | Kontrola nad pełnym pulpitem systemu operacyjnego (mysz, klawiatura, powłoka) | dziesiątki minut |
| WebArena-Verified | Zadania transakcyjne w symulowanym środowisku webowym | minuty |
| Hard subset | Złożone zadania z wielostronicowymi zmianami stanu w WebArena-Verified | dziesiątki minut |

Są to różne wymiary oceny. Wysoki wynik w BrowseComp oznacza jedynie, że agent sprawnie wyszukuje informacje, a nie że potrafi np. samodzielnie zarezerwować bilet lotniczy. Wynik w OSWorld pokazuje, jak dobrze model radzi sobie z obsługą rzeczywistego systemu operacyjnego. Z kolei WebArena-Verified mierzy zdolność do realizowania kompletnych procesów biznesowych i przepływów zadań. Decyzja o wdrożeniu produkcyjnym powinna opierać się na benchmarku, który najlepiej odzwierciedla realny charakter zadań.

### Główne wektory ataków

1. **Pośrednie wstrzykiwanie instrukcji (Indirect Prompt Injection).** Zawartość zewnętrznej, niezaufanej strony zawiera ukryte polecenia dla agenta. Gdy agent odczyta tekst, zaczyna wykonywać wstrzyknięte instrukcje. Przykłady obejmują badania Kaia Greshake i in. (2024), publikację Tainted Memories (2025) oraz HashJack od Cato Networks (2026).
2. **Wstrzykiwanie w parametrach i fragmentach URL.** Komendy są ukrywane w sekcji `#fragment` lub w parametrach zapytania (query string) odwiedzanego adresu URL. Nie są one bezpośrednio renderowane na stronie, lecz trafiają do kontekstu agenta.
3. **Zatruwanie pamięci agenta (Memory Poisoning).** Strona instruuje agenta, aby zapisał określone informacje w pamięci podręcznej lub trwalą (zarządzanie stanem opisano w Lekcji 12). Przy kolejnej sesji pobrane dane uruchamiają złośliwy ładunek (payload) bez widocznej przyczyny.
4. **Ataki klasy CSRF na sesje uwierzytelnione.** Wykorzystanie podatności typu Tainted Memories – gdy agent jest zalogowany w jakimś serwisie, złośliwa strona może skłonić go do wykonania operacji zmieniających stan konta przy użyciu aktywnych ciasteczek (cookies) użytkownika.
5. **Przejęcia jednym kliknięciem (One-click hijacking).** Pozornie niegroźne przyciski lub linki na stronie wywołują akcje przenoszące złośliwe komendy, które agent automatycznie wykonuje (klasa ataków Comet).
6. **Podatności w politykach bezpieczeństwa (CSP) środowiska agenta.** Silnik przeglądarki oraz warstwa narzędzi agenta mogą same w sobie stanowić wektor ataku; środowisko uruchomieniowe przeglądarki agenta ma bardzo szeroki zakres uprawnień.

### Dlaczego nie można w pełni wyeliminować tych podatności?

Wynika to z faktu, że wektory ataku są ściśle powiązane z kluczowymi możliwościami agenta. Aby realizować zadania, agent musi analizować zewnętrzne, niezaufane treści. Każda taka treść może zawierać złośliwe instrukcje, a ich wykonanie może stać w sprzeczności z intencjami użytkownika. Zastosowanie zabezpieczeń (np. granice zaufania, klasyfikatory pomocnicze, białe listy narzędzi czy weryfikacja człowieka HITL) znacznie zwiększa trudność ataku i ogranicza jego potencjalny zakres szkód (blast radius), lecz nie likwiduje problemu u podstaw.

Jest to analogiczne do twierdzenia Löba (omawianego w Lekcji 8): agent nie jest w stanie dowieść matematycznego bezpieczeństwa każdego kolejnego tokenu; może jedynie działać w systemie zaprojektowanym tak, by podejrzane tokeny były łatwiejsze do wykrycia i odizolowania.

### Rekomendowane mechanizmy obronne wdrożeń produkcyjnych

- **Granica odczytu/zapisu (Read/Write Boundary).** Operacje odczytu nie mogą powodować skutków ubocznych. Wszelkie operacje zapisu (wysyłanie formularzy, publikowanie postów, wywoływanie narzędzi modyfikujących dane) wymagają każdorazowego zatwierdzenia przez człowieka, jeśli przetworzone dane pochodzą spoza strefy zaufania.
- **Białe listy narzędzi dedykowane dla zadań (Task-specific Tool Whitelisting).** Agent może przeglądać internet, ale nie może np. realizować przelewów bankowych, o ile takie narzędzie nie zostało jawnie przypisane do danego zadania. Limity finansowe i budżety opisano w Lekcji 13.
- **Izolacja sesji (Session Isolation).** Agent przeglądarkowy powinien działać w oparciu o tymczasowe dane uwierzytelniające o ograniczonym zakresie. Niedopuszczalne jest podłączanie kont produkcyjnych czy osobistych skrzynek e-mail. Wszystkie zapytania HTTP powinny być logowane na potrzeby przyszłego audytu.
- **Sanityzacja danych wejściowych (Input Sanitization).** Pobrany kod HTML jest oczyszczany z podejrzanych elementów przed przekazaniem do kontekstu modelu. (Metoda ta eliminuje najprostsze ataki, lecz nie zatrzyma zaawansowanych zagrożeń).
- **Zatwierdzanie propozycji przez człowieka (Propose-then-Commit).** Architektura HITL (Human-in-the-Loop) szczegółowo opisana w Lekcji 15.
- **Tokeny kanarkowe w pamięci (Canary Tokens).** Jeśli złośliwe instrukcje zmodyfikują pamięć trwałą, użytkownik zostanie natychmiast o tym powiadomiony (patrz Lekcja 14).

## Przykład praktyczny

Skrypt `code/main.py` modeluje działanie prostego agenta przeglądarkowego na trzech syntetycznych stronach: bezpiecznej, zawierającej bezpośrednie wstrzyknięcie tekstu oraz zawierającej wstrzyknięcie we fragmencie adresu URL (niewidocznym wizualnie, lecz obecnym w kontekście agenta). Kod demonstruje: (a) zachowanie naiwnego agenta bez zabezpieczeń, (b) skuteczność granicy odczytu/zapisu, (c) skuteczność sanityzacji kodu HTML, (d) ograniczenia obu tych metod w zderzeniu z wyrafinowanymi atakami.

## Zadanie wdrożeniowe

Plik `outputs/skill-browser-agent-trust-boundary.md` określa ramy wdrożenia agenta przeglądarkowego: wskazuje strefy zaufania, z którymi wchodzi w interakcję, definiuje dozwolone operacje zapisu oraz opisuje zabezpieczenia, które muszą zostać skonfigurowane przed pierwszym uruchomieniem.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Zidentyfikuj, które ataki są wykrywane przez mechanizm sanityzacji, lecz pomijane przez granicę odczytu/zapisu, a które są blokowane wyłącznie przez tę granicę.
2. Rozbuduj moduł sanityzujący, aby wykrywał próby wstrzykiwania instrukcji we fragmentach URL w stylu HashJack. Przeanalizuj poziom fałszywych alarmów (false positives) dla bezpiecznych adresów URL zawierających standardowe fragmenty.
3. Wybierz konkretne zadanie realizowane przez agenta przeglądarkowego (np. „rezerwacja biletów lotniczych”). Wypisz wszystkie operacje odczytu oraz zapisu. Wskaż, które z nich bezwzględnie wymagają weryfikacji człowieka (HITL) i dlaczego.
4. Zapoznaj się z publikacją dotyczącą WebArena-Verified z ICLR 2026. Wskaż jedną kategorię zadań, dla której pierwotne wyniki w WebArena były niemiarodajne, i wyjaśnij, jak nowa metoda weryfikacji rozwiązuje ten problem.
5. Zaprojektuj mechanizm tokenów kanarkowych dla pamięci agenta przeglądarkowego. Określ, co powinno być zapisywane, w jakich lokalizacjach oraz co powinno wywołać alert bezpieczeństwa.

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Pośrednie wstrzykiwanie instrukcji (Indirect prompt injection) | „Zły tekst na stronie” | Złośliwe instrukcje umieszczone na niezaufanej stronie, które agent wykonuje po jej odczytaniu |
| Zatruwanie pamięci (Tainted Memories) | „Atak na pamięć agenta” | Zapisanie przez agenta złośliwych wytycznych w pamięci trwałej, wywoływanych przy kolejnych sesjach |
| HashJack | „Wstrzyknięcie w adres URL” | Złośliwy ładunek (payload) ukryty we fragmencie adresu URL lub parametrach zapytania, niewidoczny dla użytkownika |
| Przejęcie jednym kliknięciem (One-click hijacking) | „Zły przycisk” | Przejęcie sesji poprzez zmuszenie agenta do kliknięcia elementu wywołującego złośliwe akcje |
| BrowseComp | „Test wyszukiwania sieciowego” | Benchmark oceniający szybkość i dokładność wyszukiwania faktów w otwartym internecie |
| OSWorld | „Test obsługi pulpitu” | Benchmark oceniający sterowanie całym systemem operacyjnym poprzez interfejs graficzny i tekstowy |
| WebArena-Verified | „Poprawiony test zadań webowych” | Udoskonalona wersja WebAreny od ServiceNow, eliminująca fałszywe negatywy i zawierająca podzbiór zadań trudnych |
| Granica odczytu/zapisu | „Bramkowanie efektów ubocznych” | Zasada bezpieczeństwa: odczyt jest bezwarunkowy, lecz każda operacja zapisu wymaga autoryzacji |

## Dalsza lektura

- [OpenAI — Przedstawiamy agenta ChatGPT](https://openai.com/index/introducing-chatgpt-agent/) — połączenie Operatora i zaawansowanych badań; SOTA w BrowseComp.
- [OpenAI — Agent korzystający z komputera](https://openai.com/index/computer-using-agent/) — architektura i rodowód technologiczny.
- [Zhou i in. — WebArena](https://webarena.dev/) — oryginalny projekt benchmarku.
- [WebArena-Verified (OpenReview)](https://openreview.net/forum?id=94tlGxmqkN) — artykuł ICLR 2026 opisujący zweryfikowany podzbiór.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — analiza powierzchni ataku dla agentów computer-use.
