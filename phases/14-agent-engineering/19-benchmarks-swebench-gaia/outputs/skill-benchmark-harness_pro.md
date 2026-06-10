---

name: benchmark-harness
description: Zbuduj środowisko testowe w stylu SWE-bench dla bazy kodu z automatyczną weryfikacją FAIL_TO_PASS / PASS_TO_PASS, wykrywaniem zanieczyszczenia danych oraz metrykami liczby kroków.
version: 1.0.0
phase: 14
lesson: 19
tags: [swe-bench, gaia, agentbench, harness, evaluation]

---

Na podstawie bazy kodu oraz listy par (błąd, poprawka) utwórz framework benchmarkowy, który wykorzystuje rzeczywiste testy jednostkowe i mierzy kluczowe metryki operacyjne.

Wyprodukuj:

1. Definicję zadań zawierającą: identyfikator (`tid`), opis, stan początkowy (`state_before`), testy typu `fail_to_pass_tests`, testy typu `pass_to_pass_tests` oraz poprawne rozwiązanie (`solution`).
2. Moduł uruchomieniowy (runner), który w izolowanym środowisku (piaskownicy) aplikuje wygenerowaną przez agenta poprawkę, wykonuje testy i rejestruje: liczbę zaliczonych testów FTP (`FAIL_TO_PASS`), liczbę zaliczonych testów PTP (`PASS_TO_PASS`), liczbę kroków agenta, zużycie tokenów, czas rzeczywisty (wall-clock time) oraz łączny koszt.
3. Mechanizm wykrywania zanieczyszczenia danych (contamination check) – porównanie tekstu opisu błędu z wygenerowaną poprawką i oznaczanie flagą przypadków, gdzie stopień pokrycia wynosi >= 30%.
4. Moduł raportowania (reporter) eksportujący szczegółowe wyniki dla pojedynczych zadań oraz zagregowane podsumowanie w formacie JSON, w tym rozkład percentylowy (P50/P75/P95) dla liczby kroków i kosztów.
5. Krok w potoku CI (Continuous Integration) uruchamiający testy porównawcze przy każdym Pull Requeście (PR) i przerywający proces przy regresji wyników o >= 5%.

Kategoryczne odrzucenia (Twarde kryteria):

- Raportowanie wyników wyłącznie w postaci jednej, zbiorczej liczby. Wymagane jest przedstawienie szczegółowych rezultatów i rozkładów statystycznych dla każdego zadania z osobna.
- Uruchamianie kodu testowego bezpośrednio na maszynie hosta bez izolacji (piaskownicy). Wygenerowany przez agenta kod należy traktować jako kod niezaufany.
- Brak wdrożenia weryfikacji testów z grupy PASS_TO_PASS. Poprawki, które naprawiają dany błąd, ale psują inne funkcjonalności, powodują po cichu regresję całego systemu.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli użytkownik żąda weryfikacji wyłącznie za pomocą testów FAIL_TO_PASS, odmów. Zaimplementuj testy PASS_TO_PASS – uszkodzenie działających dotychczas funkcji (regresja) jest poważniejszym problemem niż brak wdrożenia nowej poprawki.
- Jeśli wersje testów nie są powiązane z konkretnym commitem (SHA) w repozytorium, odmów. Zmiany w kodzie testowym na przestrzeni czasu sprawiają, że wyniki poszczególnych uruchomień stają się nieporównywalne.
- Jeśli opis zadań testowych pokrywa się z danymi treningowymi, z których korzystał model, wyraźnie oznacz to w raporcie jako potencjalne zanieczyszczenie danych.

Pliki wynikowe: `tasks.py`, `harness.py`, `contamination.py`, `report.py`, `README.md` wyjaśniające działanie piaskownicy, mechanizmy weryfikacji (bramki) oraz zasady detekcji zanieczyszczenia danych. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 30 (rozwój oparty na ewaluacjach - Evaluation-driven development).
