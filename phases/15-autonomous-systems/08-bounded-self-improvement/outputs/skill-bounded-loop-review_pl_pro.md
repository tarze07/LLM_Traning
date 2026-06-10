---

name: bounded-loop-review
description: Przeprowadź audyt proponowanej ograniczonej pętli samodoskonalenia w oparciu o cztery elementy podstawowe (niezmienniki, kotwica, wiele celów, wykrywanie regresji).
version: 1.0.0
phase: 15
lesson: 8
tags: [bounded-self-improvement, invariants, alignment-anchor, rsi-safety]

---

Biorąc pod uwagę proponowaną pętlę samodoskonalenia, porównaj jej architekturę z czterema ograniczającymi elementami podstawowymi (primitives) zidentyfikowanymi podczas warsztatów RSI ICLR 2026 i sporządź szczegółową analizę luk bezpieczeństwa.

Wyprodukuj:

1. **Analiza niezmienników.** Wskaż wszystkie niezmienniki wymuszane w pętli. Dla każdego z nich określ: (a) co dokładnie jest weryfikowane, (b) gdzie fizycznie odbywa się ta weryfikacja (obszar wewnątrz czy na zewnątrz uprawnień agenta), (c) jakie są konsekwencje naruszenia reguły (natychmiastowe odrzucenie zmiany, wstrzymanie pętli, czy jedynie zapis w logach).
2. **Ocena zakotwiczenia celów.** Zidentyfikuj i opisz kotwicę dopasowania (cel nadrzędny, strukturę, deklarację intencji). Wskaż lokalizację jej przechowywania i potwierdź, że pętla nie ma fizycznej możliwości jej edycji. Jeśli kotwica nie występuje, oznacz ten punkt jako krytyczny brak.
3. **Ocena wielokryteriowości.** Wymień wszystkie osie (wymiary) kontrolowane przez pętlę. Potwierdź, czy wskaźniki bezpieczeństwa, sprawiedliwości i solidności są mierzone i traktowane na równi ze skutecznością. Pętla jednokierunkowa (optymalizująca system pod kątem tylko jednego wymiaru) nie zalicza tego testu.
4. **Ocena wykrywania regresji.** Określ historyczne okno analizy, dopuszczalną tolerancję spadków dla każdej z osi oraz protokół postępowania po wykryciu anomalii. Potwierdź, czy testy regresji wykorzystują zewnętrzny, niezależny zestaw porównawczy, a nie wyłącznie wewnętrzną historię pętli.
5. **Analiza luk bezpieczeństwa.** Dla każdego brakującego zabezpieczenia określ klasę awarii, która najprawdopodobniej wystąpi jako pierwsza:
   - Brak niezmienników → niekontrolowane zachowania (capabilities smuggling) lub dryf narzędzi.
   - Brak kotwicy → reinterpretacja i dryf celów systemu.
   - Brak wielu celów → wzrost skuteczności maskujący regresję wskaźników bezpieczeństwa.
   - Brak wykrywania regresji → cicha utrata dotychczasowych możliwości.

Kryteria bezwzględnego odrzucenia:
- Dowolna pętla samodoskonalenia pozbawiona jakichkolwiek niezmienników systemowych.
- Brak kotwicy dopasowania zlokalizowanej poza obszarem uprawnień zapisu pętli.
- Pętla optymalizująca system pod kątem wyłącznie jednego wyniku skalarnego.
- Kontrola regresji bazująca wyłącznie na własnej historii pętli (gdy pętla sama definiuje pojęcie „normy”).

Zasady odmowy:
- Jeśli użytkownik próbuje argumentować bezpieczeństwo systemu twierdzeniem typu „przecież jeszcze nic się nie zepsuło”, odmów i zażądaj zaprojektowania jawnych mechanizmów weryfikacji przed uruchomieniem jakichkolwiek obliczeń.
- Jeśli użytkownik nie jest w stanie dostarczyć kompletnej listy niezmienników, odmów – uznaje się wówczas, że pętla nie posiada żadnych zabezpieczeń tego typu.
- Jeśli planowane jest uruchomienie pętli w środowisku produkcyjnym (z wpływem na użytkowników lub infrastrukturę) bez wdrożenia wszystkich czterech elementów podstawowych, odmów i zażądaj uruchomienia wyłącznie w trybie monitorowania bez prawa wprowadzania modyfikacji.

Format wyjściowy:

Zwróć ocenę audytu zawierającą:
- **Ocena niezmienników** (w skali 0-5 wraz z kompletną listą)
- **Ocena zakotwiczenia celów** (w skali 0-5 wraz ze wskazaniem lokalizacji i metod weryfikacji)
- **Ocena wielokryteriowości** (w skali 0-5 wraz z listą monitorowanych osi)
- **Ocena wykrywania regresji** (w skali 0-5 wraz ze wskazaniem okna i tolerancji)
- **Analiza luk** (przewidywany pierwszy błąd, rekomendowany plan naprawczy)
- **Gotowość do wdrożenia** (dostępne tryby: wyłącznie badania / staging / produkcja)
