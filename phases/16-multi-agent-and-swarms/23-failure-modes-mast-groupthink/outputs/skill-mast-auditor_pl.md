---

name: mast-auditor
description: Uruchom audyt trybu awarii w stylu MAST w systemie wieloagentowym. Kategoryzuj błędy śledzenia wykonania na rodziny specyfikacji/koordynacji/weryfikacji i myślenia grupowego; łagodzenie rang poprzez oczekiwaną redukcję awarii.
version: 1.0.0
phase: 16
lesson: 23
tags: [multi-agent, failure-modes, MAST, groupthink, circuit-breaker, audit]

---

Biorąc pod uwagę system wieloagentowy i próbkowane ślady wykonania, przeprowadź audyt trybu awaryjnego.

Wyprodukuj:

1. **Przykładowa konstrukcja.** Co najmniej 200 śladów z produkcji, próbkowanych jednakowo dla różnych typów zadań i okien czasowych. Metoda pobierania próbek dokumentów i ryzyko stronniczości.
2. **Karta klasyfikacyjna.** Dla każdego śladu zaznaczyć `success | failure`. W przypadku niepowodzeń przypisz jedną kategorię MAST (specyfikacja / koordynacja / weryfikacja) i, jeśli ma to zastosowanie, jeden lub więcej znaczników rodziny Groupthink (monokultura / konformizm / tom / motyw mieszany / kaskada).
3. **Tabela rozkładu.** Liczby i procenty według kategorii MAST i znacznika Groupthink. Porównaj z rozkładem referencyjnym Cemri 2025 (41,77 / 36,94 / 21,30). Systemy mocno odbiegające od wzorca często mają specyficzną słabą warstwę.
4. **Najczęstsze wzorce niepowodzeń.** Zidentyfikuj 3 najczęstsze specyficzne wzorce (np. „przegląd dwóch agentów”). Etapy reprodukcji dokumentu.
5. **Ranking łagodzenia.** Dla każdego głównego wzorca zaproponuj łagodzenie ze standardowej biblioteki: jawne kontrakty ról, wersjonowany stan współdzielony, niezależny weryfikator, wyłącznik automatyczny, trio wykrywanie-diagnostyka-walidacja (STRATUS). Uszereguj według oczekiwanej redukcji awarii, biorąc pod uwagę częstotliwość wzorca.
6. **Ryzyko cichych awarii.** Ile awarii daje wiarygodne, ale błędne wyniki w porównaniu z głośnymi błędami? Cicha szybkość napędza inwestycję w warstwę weryfikacyjną.
7. **Proxy o powolnej awarii.** Zalecane są 2–3 aktualne metryki, które wykażą dryf, zanim stanie się głośnym błędem: współczynnik zgodności, współczynnik ponownych prób, rozkład długości wyjściowej, odległość edycji między agentami.

Twarde odrzucenia:

- Audyty bez próby losowej lub warstwowej. Wyselekcjonowane awarie stanowią nadmierną liczbę dramatycznych przypadków i nie uwzględniają dryftu spowodowanego powolnymi awariami.
- Zalecenia łagodzące bez pomiaru bazowego. „Dodaj weryfikator” nic nie znaczy, jeśli nie jest znany aktualny wskaźnik awaryjności.
- Ignorowanie nieznanych incydentów MAST. Jeśli ślad nie pasuje do kategorii, taksonomia jest niekompletna; zaproponować rozszerzenie zamiast narzucać kategorię.
- Złożenie wniosku o kwartalny audyt jest wystarczające bez operacyjnego monitorowania powolnych awarii. Kwartalne braki w wynikach pomiędzy audytami.

Zasady odmowy:

- Jeśli w śladach nie ma przypisania do poszczególnych agentów (kto co napisał, kto co przeczytał), audyt nie jest w stanie odróżnić błędów koordynacji od konfliktów ról. Przed ponownym audytem zalecamy dodanie strukturalnego rejestrowania dla poszczególnych agentów.
- Jeśli w systemie łącznie znajduje się mniej niż 50 błędnych śladów, próbka jest zbyt mała, aby oszacować rozkład. Zalecane dłuższe okno obserwacyjne.
- Jeśli ślady zawierają informacje umożliwiające identyfikację, zamaskuj je przed analizą.

Wynik: trzystronicowy raport. Zacznij od jednozdaniowego podsumowania („41% błędów specyfikacji, 12% koordynacji, 39% luk w weryfikacji, 8% nieznanych; najważniejszy wzorzec to konflikt dwóch recenzentów; ograniczenie najwyższego ROI to wyraźne umowy ról”), a następnie siedem sekcji powyżej. Zakończ listą działań z priorytetami: trzy środki zaradcze z szacowanym kosztem wdrożenia i oczekiwaną redukcją awaryjności.