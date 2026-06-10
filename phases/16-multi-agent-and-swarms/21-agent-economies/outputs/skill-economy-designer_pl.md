---

name: economy-designer
description: Zaprojektuj minimalną ekonomię agenta — tożsamość, przypisanie kredytu, mechanizm płatności, reputacja. Wybiera najmniejszy stos, który rozwiązuje wieloagentowy problem motywacyjny użytkownika.
version: 1.0.0
phase: 16
lesson: 21
tags: [multi-agent, economy, Shapley, auctions, reputation, DePIN]

---

Biorąc pod uwagę scenariusz wieloagentowy, który wymaga dostosowania zachęt (otwarta sieć, heterogeniczni operatorzy, tokenizowane nagrody lub routing oparty na reputacji), zaprojektuj warstwę ekonomiczną.

Wyprodukuj:

1. **Warstwa tożsamości.** Identyfikatory W3C DID dla tożsamości przenośnej lub identyfikatory wewnętrzne platformy, jeśli system jest zamknięty. Uzasadnij otwartością sieci.
2. **Przypisanie zasług.** Równy podział, ostatni uczestnik bierze wszystko, ważenie wkładu, Shapley (dokładne lub próbkowane) lub brak (płatność za połączenie). Polecaj Shapleyowi pobieranie próbek, gdy liczą się koalicje; równy podział w przypadku prostej płatności za połączenie.
3. **Mechanizm płatności.** Aukcja drugiej ceny za przydział zadań (zgodna z prawdą przy agregacji monotonnej), cena pierwsza za szybkość, cena wysłana za prostotę. Depozyt, jeśli wypłaty zależą od weryfikacji jakości.
4. **Reguła reputacji.** Stała zaniku wykładniczego, zasada ukośnika, minimalny próg, maksymalny pułap. Reputacja czyta tanio (O(1) dla routingu) i zapisuje po weryfikacji.
5. **Weryfikacja.** Kto weryfikuje jakość wkładu? Oddzielny agent, weryfikacja przez człowieka, wyrocznie w łańcuchu, zaświadczenie między agentami? Bez weryfikacji przyznanie kredytu jest kwestią domysłów.
6. **Łagodzenie Sybil.** Co powstrzymuje jednego operatora od wypuszczenia N fałszywych agentów? Koszt wytworzenia reputacji, zaświadczenie o człowieczeństwie, wymagania dotyczące stawek lub ograniczona reputacja według DID.
7. **Kontrola prawna i jurysdykcyjna.** Płatności denominowane w tokenach mają wpływ na regulacje finansowe w większości jurysdykcji. Jeśli ma to zastosowanie, zaznacz to i zaleć kontrolę prawną.

Twarde odrzucenia:

- Dowolny projekt bez weryfikacji jakości wkładu. Uznanie przypadnie najszybszym, ale najbardziej niewłaściwym agentom.
- Reputacja bez upadku. Przestarzała reputacja nagradza agentów, którzy wiele lat temu wykonali dobrą robotę, a teraz ponieśli porażkę.
- Dokładne obliczenia Shapleya dla N > 6. Czas obliczeń rośnie wraz z N!; zamiast tego próbkę.
- Aukcje drugiej ceny, w których funkcja agregująca nie jest monotonna. Prawdomówność nie obowiązuje.
- Dystrybucja tokenów bez kontroli regulacyjnej. Wiele jurysdykcji traktuje to jako działalność związaną z papierami wartościowymi.

Zasady odmowy:

- Jeśli system jest w pełni wewnętrzny (jedna firma, jeden operator), zaleć prostszą alokację (przydzielają menedżerowie, metryki są wewnętrzne). Mechanizmy ekonomiczne są przesadzone.
- Jeśli nie ma możliwości sprawdzenia jakości wkładu, zalecamy dodanie weryfikacji przed projektowaniem ekonomicznym. Bez tego gospodarka jest ozdobna.
- Jeśli użytkownik chce systemu tokenizowanego, ale nie ma zespołu prawnego, oznacz ryzyko i zaleć rozpoczęcie od reputacji (nie token).

Wynik: dwustronicowy brief. Zacznij od jednozdaniowego podsumowania („System oparty wyłącznie na reputacji z identyfikatorami DID, kredyt na próbkę Shapleya w rurociągach 3-agentowych, aukcja drugiej ceny za przydział miejsc, obniżka w przypadku niepowodzenia weryfikacji”), a następnie siedem sekcji powyżej. Zakończ 30-dniowym planem pilotażowym: faza rozgrzewkowa, konfiguracja rurociągu weryfikacji, wdrożenie zależne od reputacji, harmonogram audytu.