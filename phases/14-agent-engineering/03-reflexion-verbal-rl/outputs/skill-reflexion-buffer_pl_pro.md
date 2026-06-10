---

name: reflexion-buffer
description: Zarządzaj buforem wniosków w pamięci epizodycznej na potrzeby wzmocnienia werbalnego (Verbal RL), obsługując mechanizmy TTL, deduplikację oraz zakresy ważności.
version: 1.0.0
phase: 14
lesson: 03
tags: [reflexion, episodic-memory, self-healing, verbal-rl, sleep-time]

---

Dla danej klasy zadań (czyli powtarzalnego typu operacji realizowanych przez agenta, np. „refaktoryzacja funkcji”, „zamykanie zgłoszeń wsparcia technicznego”) utrzymuj bufor refleksji (wniosków) w pamięci epizodycznej. Każda refleksja powinna opisywać rodzaj napotkanego błędu oraz wskazówki korygujące sformułowane w języku naturalnym. Zawartość bufora jest dołączana do promptu przy kolejnej próbie realizacji zadania z tej samej klasy.

Przygotuj:

1. Rejestrowanie wniosków (refleksji): Gdy próba zakończy się wynikiem poniżej określonego progu, wygeneruj jednozdaniowy wniosek o strukturze: „Nie udało mi się wykonać X, ponieważ Y; następnym razem należy zrobić Z”. Ignoruj błędy wynikające z czynników zewnętrznych (np. awaria sieci, błąd serwera 500 upstream), chyba że mają one charakter powtarzalny.
2. Czas życia (TTL) i deduplikacja: Domyślnie wpisy wygasają po N próbach (sugerowana wartość to 10). Identyczne wpisy są odrzucane. W przypadku wpisów niemal identycznych (podobieństwo cosinusowe > 0,9 w mniejszym modelu embeddingów lub wspólny podciąg na poziomie >= 80%) zachowywany jest wyłącznie najnowszy wpis.
3. Definiowanie zakresu (Scope): Obsługuj trzy poziomy zakresu: klasa zadania (dla konkretnego typu zadania), użytkownik (pomiędzy zadaniami tego samego użytkownika) oraz agent (globalnie dla wszystkich użytkowników). Domyślnym ustawieniem jest klasa zadania. Rozszerzaj zakres do poziomu użytkownika tylko wtedy, gdy wniosek dotyczy jego indywidualnych preferencji; pod żadnym pozorem nie eskaluj zakresu automatycznie do poziomu agenta.
4. Kompaktowanie (konsolidacja): Gdy bufor przekroczy limit rozmiaru, uruchom proces kompaktowania w tle (w czasie bezczynności): pogrupuj podobne wpisy, podsumuj je i scal. Kompaktowanie musi odbywać się poza główną ścieżką wykonania, aby nie powodować opóźnień w działaniu agenta.
5. Wstrzykiwanie do promptu: Wygeneruj dedykowaną sekcję zatytułowaną „Wnioski z poprzednich prób” w formie listy punktowanej. Ogranicz jej zawartość do maksymalnie 6 wpisów w monicie; pozostałe wpisy powinny zostać zagregowane w formie krótkiej adnotacji (np. „... oraz 4 starsze wnioski dotyczące limitów czasu”).

Kryteria odrzucenia:
- Zapisywanie ogólnych wniosków w rodzaju „następnym razem muszę być bardziej ostrożny” (brak wartości wdrożeniowej). W takim przypadku należy ponownie uruchomić moduł refleksji z promptem wymuszającym sformułowanie konkretnych instrukcji działania.
- Określanie czasu życia (TTL) wpisów na podstawie czasu rzeczywistego zamiast liczby wykonanych prób. W środowiskach testowych (offline) TTL musi bazować na liczbie prób, a nie na upływie czasu.
- Zapisywanie wniosków zawierających dane wrażliwe (klucze API, tokeny, dane osobowe - PII). Tego typu wpisy muszą zostać zablokowane i odrzucone z błędem klasy „zawiera dane wrażliwe” przed zapisaniem ich w buforze.

Zasady odmowy wykonania zadania:
- Jeśli do zadania nie przypisano modułu oceniającego (Evaluator), odmów wykonania i rekomenduj Lekcję 05 (Samodoskonalenie/Krytyk) – refleksja wymaga jasnego sygnału zwrotnego, a nie domysłów.
- Jeśli dane zadanie jest unikalne (jednorazowe i nigdy się nie powtórzy), odmów wykonania; pamięć epizodyczna nie przynosi żadnych korzyści w przypadku niepowtarzalnych operacji.

Oczekiwany rezultat: Ustrukturyzowany plik bufora (JSON zawierający obiekty wniosków: id próby, klasa zadania, zakres, treść, data utworzenia, pozostały TTL), sekcja promptu do wstrzyknięcia przy kolejnej próbie oraz raport o wpisach przeznaczonych do wygaszenia.

Na końcu dodaj sekcję „Sugerowane lektury” odsyłającą do Lekcji 06 (kompresja kontekstu) – jeśli bufor stale przekracza limity rozmiaru – lub do Lekcji 08 (Obliczenia w czasie bezczynności Letta) – w celu przeniesienia procesu kompaktowania poza główny przepływ wykonania.
