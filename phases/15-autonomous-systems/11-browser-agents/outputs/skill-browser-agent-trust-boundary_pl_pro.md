---

name: browser-agent-trust-boundary
description: Określ zakres proponowanego wdrożenia agenta przeglądarkowego – strefy zaufania, autoryzowane operacje zapisu, wymagane zabezpieczenia – zanim agent wejdzie w interakcję z rzeczywistą witryną.
version: 1.0.0
phase: 15
lesson: 11
tags: [browser-agents, prompt-injection, trust-boundary, osworld, webarena]

---

Na podstawie proponowanego przepływu pracy (workflow) agenta przeglądarkowego przygotuj dokument definiujący granice zaufania (trust boundaries), który wylicza każdą operację odczytu, zapisu oraz określa minimalny zestaw zabezpieczeń wymaganych przed pierwszym uruchomieniem.

Przygotuj:

1. **Powierzchnia odczytu (Read Surface).** Wskaż wszystkie źródła danych, które agent będzie pobierał. Sklasyfikuj każde z nich jako zaufane (np. wewnętrzne systemy firmy) lub niezaufane (strony trzecie, treści generowane przez użytkowników, wyniki wyszukiwania). Wszystkie odczyty z niezaufanych źródeł należy traktować jako potencjalne kanały wstrzykiwania złośliwych instrukcji (prompt injection).
2. **Powierzchnia zapisu (Write Surface).** Wypisz wszystkie operacje modyfikacji lub wysyłania danych, do których agent jest upoważniony (wysyłanie formularzy, publikowanie treści, wywoływanie API backendu, zapis do pamięci). Dla każdego działania określ potencjalny zakres szkód (blast radius) oraz czy jest ono odwracalne.
3. **Wymagane zabezpieczenia.** Zdefiniuj minimalny zestaw warstw ochronnych: sanityzacja zawartości HTML, granica odczytu/zapisu (zapisy wymagają ponownej autoryzacji, gdy źródło danych `content_origin` jest niezaufane), dedykowana biała lista narzędzi dla zadania, izolacja sesji z uprawnieniami o ograniczonym zakresie, tokeny kanarkowe w pamięci trwałej oraz udział człowieka (HITL) przy operacjach nieodwracalnych.
4. **Reprezentatywność benchmarku.** Jeśli skuteczność agenta opiera się na wynikach testów BrowseComp, OSWorld lub WebArena, określ poziom pokrycia (nakładania się) zadań testowych z rzeczywistym zastosowaniem produkcyjnym. Przykładowo, wysoki wynik w BrowseComp nie pozwala przewidzieć niezawodności agenta w procesie rezerwacji biletów.
5. **Lista kontrolna znanych ataków.** Zweryfikuj odporność wdrożenia na: (a) wstrzykiwanie instrukcji w widocznym tekście strony, (b) wstrzykiwanie instrukcji w adresach URL/parametrach zapytania, (c) zatruwanie pamięci (Tainted Memories), (d) ataki typu CSRF na zalogowane sesje, (e) przejęcia jednym kliknięciem. Dla każdego zagrożenia określ zastosowany mechanizm obronny oraz punkt jego aktywacji.

Kryteria odrzucenia (Hard Rejections):
- Agenci przeglądarkowi z dostępem do danych produkcyjnych działający bez izolacji sesji.
- Dowolne wdrożenie, w którym operacja zapisu inicjowana na bazie niezaufanych danych nie wymaga każdorazowej autoryzacji człowieka (HITL).
- Wdrożenia opierające się wyłącznie na sanityzacji treści (filtry HTML eliminują tylko proste ataki, zaawansowane ładunki wciąż mogą przejść).
- Korzystanie z pamięci trwałej bez zaimplementowanych tokenów kanarkowych.
- Procesy obsługujące transakcje finansowe lub dane osobowe klientów bez weryfikacji HITL przy operacjach zapisu.

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie potrafi określić potencjalnego zakresu szkód (blast radius) wstrzyknięcia instrukcji, należy odmówić wykonania zadania i zażądać jednoznacznego określenia najgorszego scenariusza.
- Jeśli użytkownik proponuje wdrożenie agenta przeglądarkowego w środowisku pozbawionym możliwości ograniczenia zakresu danych uwierzytelniających, należy odmówić i zażądać najpierw wydzielenia osobnej tożsamości cyfrowej (identyfikatora).
- Jeśli użytkownik powołuje się na wyniki publicznych benchmarków (BrowseComp, OSWorld, WebArena) jako dowód, że agent bezproblemowo poradzi sobie z zadaniem produkcyjnym, należy odmówić i zażądać przeprowadzenia wewnętrznych testów na rzeczywistych danych.

Format danych wyjściowych:

Przedstaw raport z audytu границ zaufania zawierający:
- **Tabelę powierzchni odczytu** (źródło danych, status zaufania)
- **Tabelę powierzchni zapisu** (akcja, zakres szkód, odwracalność [tak/nie])
- **Zestaw zabezpieczeń** (wypunktowana lista wdrożonych warstw ochronnych)
- **Analizę reprezentatywności benchmarku** (jeśli dotyczy)
- **Listę kontrolną znanych ataków** (tabela z pięcioma wierszami opisującymi metodę obrony dla każdego zagrożenia)
- **Rekomendację wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
