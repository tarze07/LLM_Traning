---

name: economy-designer
description: Zaprojektuj uproszczony system ekonomiczny dla populacji agentów (tożsamość, podział nagród, mechanizm płatności, reputacja). Narzędzie dobiera minimalny zestaw technologii niezbędny do rozwiązania problemu motywacyjnego w systemie wieloagentowym.
version: 1.0.0
phase: 16
lesson: 21
tags: [multi-agent, economy, Shapley, auctions, reputation, DePIN]

---

Na podstawie założeń scenariusza wieloagentowego wymagającego kalibracji bodźców (np. otwarta sieć, heterogeniczni właściciele węzłów, tokenizacja nagród lub routing oparty na reputacji), zaprojektuj warstwę ekonomiczną systemu.

Opracuj następujące elementy:

1. **Warstwa tożsamości (Identity).** Zastosowanie standardu W3C DID w celu zapewnienia przenośnej tożsamości lub identyfikatorów wewnętrznych platformy (w systemach zamkniętych). Uzasadnij wybór poziomem otwartości sieci.
2. **Podział nagród (credit assignment).** Wybierz model: równy podział, „zwycięzca bierze wszystko”, ważenie wkładu, wartość Shapleya (dokładna lub próbkowana) lub brak podziału (płatność za pojedyncze wywołanie/pay-per-call). Rekomenduj próbkowanie wartości Shapleya w sytuacjach, gdy kluczowe znaczenie ma wkład koalicji agentów; dla prostych rozliczeń wybierz płatność za połączenie.
3. **Mechanizm płatności.** Wybierz model: aukcja drugiej ceny przy przydziale zadań (zapewniająca szczerość ofert przy monotonicznej agregacji), aukcja pierwszej ceny w celach optymalizacji szybkości, lub cena stała (posted price) dla uproszczenia systemu. Wprowadź mechanizm depozytowy (escrow), jeśli wypłata zależy od weryfikacji jakości wyników.
4. **Zarządzanie reputacją.** Określenie stałej wykładniczego zaniku, mechanizmu kar (slashing), progu minimalnego oraz limitu maksymalnego. Odczyt reputacji powinien być tani obliczeniowo (klasy O(1) na potrzeby routingu), a jej aktualizacja (zapis) powinna następować wyłącznie po weryfikacji wkładu.
5. **Weryfikacja wkładu.** Kto i jak ocenia jakość dostarczonych danych? (np. wydzielony agent oceniający, weryfikacja manualna przez człowieka, wyrocznie on-chain, wzajemne atestacje agentów). Bez rzetelnej weryfikacji podział nagród opiera się na spekulacjach.
6. **Ochrona przed atakami Sybil.** Co uniemożliwia jednemu podmiotowi uruchomienie N fałszywych tożsamości? (np. koszt wypracowania reputacji, testy potwierdzenia człowieczeństwa/proof of humanity, wymagania dotyczące depozytów/stakingu, ograniczenie transferowalności reputacji przypisanej do DID).
7. **Analiza zgodności prawnej i podatkowej.** Rozliczenia oparte na tokenach podlegają ścisłym regulacjom finansowym w większości jurysdykcji. Jeśli planujesz ich wdrożenie, wyraźnie wskaż to ryzyko i zaleć audyt prawny.

Kryteria twardego odrzucenia projektu:

- Projektowanie systemu bez mechanizmów weryfikacji jakości wyników. W takim układzie nagrody trafiałyby do agentów najszybszych, lecz generujących błędne odpowiedzi.
- Systemy reputacji pozbawione mechanizmu parowania/zaniku (decay). Przestarzała reputacja nagradzałaby agentów, którzy wykazali się wysoką jakością w przeszłości, lecz obecnie dostarczają błędne wyniki.
- Obliczanie dokładnej wartości Shapleya dla populacji powyżej 6 agentów (N > 6). Złożoność obliczeniowa rośnie w tempie silni (N!); w takich przypadkach należy bezwzględnie stosować próbkowanie.
- Wdrożenie aukcji drugiej ceny in warunkach, gdy funkcja agregacji nie jest monotoniczna. Wtedy zasada szczerości ofert (truthfulness) przestaje obowiązywać.
- Dystrybucja tokenów bez przeprowadzenia audytu prawnego. W wielu jurysdykcjach transakcje takie mogą zostać zakwalifikowane jako obrót papierami wartościowymi.

Zasady odmowy (rekomendacje alternatywne):

- Jeśli system ma charakter zamknięty i wewnętrzny (jedna organizacja, jeden zarządca infrastruktury), zalecaj prostsze metody alokacji zadań (przydział centralny, wewnętrzny monitoring). Zaawansowane mechanizmy ekonomiczne stanowią w tym przypadku zbędny narzut (overengineering).
- Jeśli nie ma możliwości automatycznego lub manualnego zweryfikowania jakości wkładu, zaleć wdrożenie modułu weryfikacji przed przystąpieniem do projektowania zasad rynkowych. Bez tego ekonomia ma wymiar wyłącznie fasadowy.
- Jeśli klient dąży do tokenizacji rozliczeń, ale nie dysponuje wsparciem prawnym, wskaż ryzyka regulacyjne i rekomenduj rozpoczęcie od systemu reputacji bezgotówkowej.

Format wyjściowy: dwustronicowy brief projektowy. Rozpocznij od jednozdaniowego podsumowania (np. „System oparty wyłącznie na reputacji powiązanej z DID, podział nagród oparty na próbkowaniu wartości Shapleya dla potoków 3-agentowych, aukcje drugiej ceny przy przydziale zadań, slashing w przypadku negatywnej weryfikacji wkładu”), po którym następuje omówienie siedmiu powyższych punktów. Dokument zakończ 30-dniowym planem wdrożenia pilotażowego (faza rozbiegowa, wdrożenie modułu weryfikacji, uruchomienie routingu opartego na reputacji, harmonogram audytów).
