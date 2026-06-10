---

name: benchmark-harness
description: Zbuduj wiązkę w stylu SWE dla bazy kodu z bramkowaniem FAIL_TO_PASS / PASS_TO_PASS, kontrolą zanieczyszczeń i metrykami liczby kroków.
version: 1.0.0
phase: 14
lesson: 19
tags: [swe-bench, gaia, agentbench, harness, evaluation]

---

Mając bazę kodu i listę par (błąd, poprawka), utwórz zestaw testów porównawczych, który opiera się na rzeczywistych testach jednostkowych i rejestruje metryki operacyjne.

Wyprodukuj:

1. Definicja zadania: `(tid, description, state_before, fail_to_pass_tests, pass_to_pass_tests, solution)`.
2. Biegacz, który instaluje łatkę agenta, uruchamia zestaw testów repo w piaskownicy i rejestruje: liczbę przejść FTP, liczbę przejść PTP, liczbę kroków, tokeny, zegar ścienny, koszt.
3. Kontrola skażenia: dopasowanie tekstu wydania do wyprodukowanej łatki; flaga >= 30% nakładania się.
4. Reporter, który emituje wyniki dla poszczególnych zadań i wyniki zbiorcze w formacie JSON, plus krok i koszt P50/P75/P95.
5. Zadanie CI, które uruchamia wiązkę przy każdym PR i kończy się niepowodzeniem przy >=5% regresji.

Twarde odrzucenia:

- Uprząż, która zgłasza tylko jedną liczbę zbiorczą. Wymagaj wyników i rozkładów dla poszczególnych zadań.
- Uprząż, która uruchamia testy bez piaskownicy. Poprawki dostarczane przez agenta to niezaufany kod.
- Uprząż bez bramki PASS_TO_PASS. Poprawki, które przerywają inne testy, po cichu powodują regresję produktu.

Zasady odmowy:

- Jeśli użytkownik poprosi o „tylko wynik FAIL_TO_PASS”, odmów. Dodaj PASS_TO_PASS; złamanie istniejących testów jest gorszą regresją niż przegapienie poprawki.
- Jeśli testy nie są przypięte do konkretnego zatwierdzenia, odmów. Dryf w testach sprawia, że ​​wyniki w różnych seriach są nieporównywalne.
- Jeśli zadania pokrywają się z tekstem problemu widocznym podczas szkolenia, zaznacz to wyraźnie.

Dane wyjściowe: `tasks.py`, `harness.py`, `contamination.py`, `report.py`, `README.md` wyjaśniające piaskownicę, bramy i politykę dotyczącą skażenia. Zakończ słowami „Co dalej czytać”, wskazując na lekcję 30 dotyczącą rozwoju opartego na ewaluacji na górze uprzęży.