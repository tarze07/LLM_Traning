---

name: agent-budget-audit
description: Przed uruchomieniem nienadzorowanej sesji agenta przeprowadź audyt mechanizmów kontroli kosztów (stos zarządzania kosztami) i wskaż brakujące warstwy zabezpieczeń.
version: 1.0.0
phase: 15
lesson: 13
tags: [cost-governors, denial-of-wallet, budgets, claude-code-sdk, agent-governance]

---

Dla proponowanego wdrożenia agenta przeprowadź audyt mechanizmów kontroli kosztów w odniesieniu do dwunastu referencyjnych warstw zabezpieczeń. Wskaż warstwy brakujące, niedostatecznie skonfigurowane (niedostrojone) lub zbyt restrykcyjne (przestrojone).

Przygotuj:

1. **Rejestr warstw zabezpieczeń.** Dla każdej z dwunastu referencyjnych warstw (limit na zapytanie, limit tokenów na zadanie, limit budżetu na zadanie, limity dla poszczególnych narzędzi, limit iteracji, limity czasowe: minutowe/godzinowe/dobowe/miesięczne, limit dynamiki kosztów, warstwowy routing modeli, buforowanie promptów, zarządzanie oknem kontekstowym, punkty kontrolne HITL, wyłącznik awaryjny) określ status wdrożenia oraz przypisaną wartość.
2. **Mapowanie scenariuszy awarii.** Dla każdego typu awarii (nagłe zapętlenie, powolny wyciek środków, błędy wdrożeniowe, skok obciążenia) wskaż konkretną warstwę zabezpieczeń, która ma go wykryć, oraz szacowany czas reakcji.
3. **Limity dla narzędzi.** Przygotuj listę wszystkich narzędzi dostępnych dla agenta. Dla każdego z nich określ limit wywołań na sesję wraz z uzasadnieniem. Brak limitu dla konkretnego narzędzia tworzy otwartą pętlę podatności na koszty.
4. **Progi alertów (Alert Thresholds).** Niezależnie od sztywnych limitów: przy jakim tempie wzrostu kosztów uruchamiane jest powiadomienie dla człowieka? Opisywany przypadek e-commerce (wzrost z 1200 do 4800 USD) wynikał z braku reakcji na skok wydatków w ujęciu tygodniowym, a nie z przekroczenia limitu miesięcznego.
5. **Architektura wyłącznika awaryjnego (Kill Switch).** Co się dzieje w momencie aktywacji limitu? Zdefiniuj mechanizmy: bezpieczne przerwanie sesji, wycofanie zmian, powiadomienia oraz procedurę ponownego włączenia. Potwierdź, czy wyłącznik awaryjny znajduje się poza środowiskiem uruchomieniowym agenta (agent nie może mieć uprawnień do modyfikacji własnych limitów budżetowych).

Kryteria odrzucenia (Hard Rejections):
- Dowolne autonomiczne wdrożenie bez nałożonego limitu budżetu finansowego na zadanie.
- Uruchamianie nienadzorowanych zadań w długim horyzoncie bez limitu dynamiki kosztów (velocity limit).
- Udostępnianie nowych narzędzi (wdrożonych w ciągu ostatnich 30 dni) bez określonych limitów wywołań.
- Wyłączniki awaryjne (kill switches), które mogą być modyfikowane przez samego agenta.
- Stosowanie limitu miesięcznego jako jedynego zabezpieczenia budżetowego (brak kontroli w krótszych oknach czasowych).

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie potrafi oszacować kosztów najgorszego scenariusza na bazie aktualnych cenników modeli, należy odmówić i zażądać kalkulacji kosztów.
- Jeśli proponowany budżet przekracza poziom akceptowalnych strat finansowych dla organizacji z tytułu jednego incydentu, należy odmówić i zażądać obniżenia limitu.
- Jeśli użytkownik traktuje klasyfikator bezpieczeństwa trybu automatycznego (patrz Lekcja 10) jako alternatywę dla limitów budżetowych, należy odmówić. Klasyfikator nie monitoruje kosztów zapytań; wymagane jest jednoczesne wdrożenie obu tych warstw.

Format danych wyjściowych:

Przedstaw raport z audytu kontroli kosztów zawierający:
- **Tabelę warstw** (nazwa warstwy, status konfiguracji [tak/nie], przypisana wartość)
- **Analizę pokrycia scenariuszy awarii** (cztery wiersze: zapętlenie, wyciek, błędy wdrożeniowe, skok obciążenia)
- **Limity wywołań narzędzi** (narzędzie, limit, uzasadnienie)
- **Progi powiadomień i alertów** (częstotliwość, osoba odpowiedzialna, kanał komunikacji)
- **Architekturę wyłącznika awaryjnego** (wyzwalacz, akcja, procedura ponownego uruchomienia)
- **Rekomendacją wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
