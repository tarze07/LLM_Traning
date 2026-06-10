---

name: rsi-cycle-pause-spec
description: Określ warunki, w których potok RSI musi zostać wstrzymany i poczekać na weryfikację przez człowieka przed następnym cyklem.
version: 1.0.0
phase: 15
lesson: 7
tags: [rsi, self-improvement, alignment, pause-threshold, rsp]

---

Biorąc pod uwagę proponowany potok rekurencyjnego samodoskonalenia (RSI), utwórz specyfikację wstrzymania pętli: jasne i jednoznaczne warunki, które zatrzymają pętlę w celu przeprowadzenia audytu przez człowieka przed rozpoczęciem kolejnego cyklu. Potok bez wdrożonej specyfikacji wstrzymania nie jest gotowy do uruchomienia.

Wyprodukuj:

1. **Progi na poziomie cyklu.** Dla każdego mierzalnego wymiaru (wynik zdolności, wynik dopasowania, budżet obliczeniowy, długość trajektorii wykonania, zużycie zasobów) zdefiniuj próg liczbowy, którego przekroczenie skutkuje natychmiastowym wstrzymaniem pętli. Progi te muszą zostać ustawione i zapisane przed uruchomieniem pętli.
2. **Dopuszczalne przyrosty (delty) między cyklami.** Określ maksymalny dozwolony przyrost na dowolnej z osi w pojedynczym cyklu. Nagły skok możliwości o ponad 30% w jednej rundzie stanowi niemal zawsze sygnaturę manipulowania ewaluatorem (gaming the evaluator) – wymaga to wstrzymania pętli i szczegółowej kontroli.
3. **Luka niedopasowania (misalignment gap).** Po każdym cyklu oblicz wartość: zdolności minus dopasowanie. Jeśli dystans ten zwiększy się o więcej niż wartość progowa X (zdefiniowana przez operatora), wstrzymaj pętlę. Jest to kluczowy wskaźnik monitorowany w symulatorze w ćwiczeniu `code/main.py`.
4. **Wykrywanie regresji.** Jeśli w danym cyklu wskaźnik na dowolnej z osi spadnie o więcej niż wartość Y, zatrzymaj system. Spadki zdolności lub bezpieczeństwa często następują po nagłych, nienaturalnych skokach – ich szybkie wychwycenie zapobiega fałszywemu obrazowi postępu.
5. **Protokół wznowienia przez człowieka.** Zanim pętla zostanie uruchomiona ponownie po zatrzymaniu, wyznaczony z nazwiska administrator musi zweryfikować przyczynę wyzwolenia pauzy, w razie potrzeby przedefiniować wartości progowe i zapisać swoją decyzję oraz jej uzasadnienie w ścieżce audytu zlokalizowanej poza potokiem.

Kryteria bezwzględnego odrzucenia:
- Dowolny potok, który pozwala na automatyczne wznowienie pracy po wstrzymaniu bez pozytywnego, manualnego zatwierdzenia przez człowieka.
- Warunki wstrzymania zdefiniowane w oparciu o wewnętrzne mechanizmy oceniające pętli (które agent może samodzielnie zmodyfikować lub ograć).
- Dowolna konfiguracja, w której agent ma prawa zapisu do pliku specyfikacji progów bezpieczeństwa.

Zasady odmowy:
- Jeśli użytkownik nie jest w stanie podać konkretnych wartości progowych przed startem, odmów. Progi ustalane w trakcie działania systemu nie są zabezpieczeniami, lecz próbą racjonalizacji błędów.
- Jeśli potok nie posiada zewnętrznego, niezależnego analizatora (działającego poza pętlą agenta), odmów – rzetelne wykrywanie regresji oraz nagłych skoków (surges) wymaga widoku z zewnątrz.
- Jeśli proponowany protokół wznowienia zakłada mechanizm typu: „wyślij e-mail do zespołu i wznów automatycznie po 24 godzinach przy braku sprzeciwu”, odmów. Wznowienie musi być świadomym, aktywnym i udokumentowanym działaniem człowieka.

Format wyjściowy:

Zwróć jednostronicową specyfikację zawierającą:
- **Osie pomiarowe i progi wstrzymania** (tabela)
- **Maksymalne przyrosty delta na cykl** (tabela)
- **Wzór i próg alarmowy luki niedopasowania**
- **Limity regresji/spadków**
- **Zewnętrzny ewaluator** (opis narzędzia, częstotliwość i moment uruchamiania)
- **Protokół wznowienia** (imię i nazwisko właściciela, lista kontrolna, lokalizacja dziennika audytu)
- **Miejsce na podpis** (kto odpowiada za nienaruszalność reguły wstrzymania pętli)
