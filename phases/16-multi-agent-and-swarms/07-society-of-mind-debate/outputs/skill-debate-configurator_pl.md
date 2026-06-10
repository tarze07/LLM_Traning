---

name: debate-configurator
description: Skonfiguruj debatę wieloagentową dla danego zadania, szacując przyrost jakości i koszt tokena przed uruchomieniem.
version: 1.0.0
phase: 16
lesson: 07
tags: [multi-agent, debate, society-of-mind, consensus]

---

Biorąc pod uwagę pytanie lub zadanie, utwórz konfigurację debaty gotową do uruchomienia w dowolnym środowisku agenta (LangGraph, AutoGen, pętla niestandardowa).

Wyprodukuj:

1. **Kontrola dopasowania zadania.** Czy to zadanie można poprawić w drodze konsensusu? Debata pomaga w rozumowaniu, faktach i dekompozycji; nie pomaga w zadaniach, które są już deterministyczne (arytmetyka, kompilacja kodu) lub czysto generatywne (twórcze pisanie).
2. **Liczba agentów.** 3, 4 lub 5. Domyślnie 3; 4+ tylko wtedy, gdy nie jest wrażliwy na koszty i wymaga bardziej zróżnicowanych poglądów.
3. **Liczba rund.** 2 lub 3. Domyślnie 3; rzadko więcej. Cytuj Du i in. plateau.
4. **Heterogeniczność.** Ten sam model podstawowy (prostszy, tańszy, więcej skorelowanych błędów) lub rodzina mieszana (Lama + Claude + GPT; dekorelacja; droższa, wymaga warstwy routingu).
5. **Przypisanie ról.** Symetryczny (wszyscy agenci pełnią tę samą rolę) vs jeden kontradyktoryjny (jeden agent poinstruowany, aby się nie zgodzić). Slot kontradyktoryjny to tanie zabezpieczenie przed kaskadami pochlebstw.
6. **Metoda agregacji.** Głosowanie większością (odpowiedzi dyskretne), średnia ważona (liczbowa) lub synteza sędziego LLM (otwarta).
7. **Oszacowanie kosztów.** N agentów × R rund × mediana żetonów na turę. Podaj szacunkową kwotę w dolarach, biorąc pod uwagę aktualne ceny dostawcy.

Twarde odrzucenia:

- Dowolna konfiguracja obejmująca więcej niż 5 agentów lub więcej niż 3 rundy bez konkretnego uzasadnienia kosztów.
- Debaty wyłącznie symetryczne na temat zadań o znanym ryzyku pochlebstwa.
- Używanie debaty do zadań, które mają deterministyczny weryfikator (kompilacja, testowanie, dokładna matematyka) - zamiast tego uruchom weryfikator.

Zasady odmowy:

- Jeśli zadanie polega na prostym wyszukiwaniu faktów, odmów i zalecaj pojedynczego agenta ze wspomaganiem wyszukiwania.
- Jeśli zadanie ma charakter generatywny (napisz wiersz), odmów – debata przesuwa wyniki w stronę średniej.
- Jeśli użytkownik nie ustalił budżetu na tokeny/dolary, odmów i poproś o taki. Debata kosztuje 5–15 razy więcej niż koszt pojedynczego agenta.

Dane wyjściowe: jednostronicowy opis konfiguracji. Zacznij od sprawdzenia dopasowania zadania i zakończ szacunkowym kosztem całkowitym.