---

name: hybrid-planner
description: Zbuduj planer hybrydowy — ChatHTN dla planów o formalnie dowiedzionej poprawności, AlphaEvolve do wyszukiwania kodu z maszynowo weryfikowalnym ewaluatorem — i dobierz właściwe rozwiązanie do problemu.
version: 1.0.0
phase: 14
lesson: 11
tags: [planning, htn, chathtn, alphaevolve, evolutionary-search]

---

W zależności od klasy problemu (zgodność z regułami biznesowymi vs optymalizacja kodu vs zadanie otwarte), wybierz odpowiedni planer i wygeneruj jego szkielet.

Drzewo decyzyjne:

1. Czy problem posiada sztywne warunki wstępne lub ograniczenia regulacyjne/biznesowe/harmonogramowe? -> Wybierz HTN (ChatHTN).
2. Czy problem posiada deterministyczną, weryfikowalną maszynowo funkcję przystosowania (fitness function)? -> Wybierz podejście ewolucyjne (AlphaEvolve).
3. Żadne z powyższych? -> Zastosuj klasyczny wzorzec ReAct (Lekcja 01) lub ReWOO (Lekcja 02).

Dla wariantu HTN wygeneruj:

1. Typ danych `Operator` z polami `preconditions`, `effects_add`, `effects_remove`.
2. Typ danych `Method` z polami `task`, `preconditions`, `subtasks`.
3. Planer próbujący w pierwszej kolejności dopasować istniejące metody, a w przypadku ich braku korzystający z dekompozycji LLM jako mechanizmu zapasowego (fallback) z buforowaniem (cache) udanych dekompozycji.
4. Etap walidacji odrzucający dekompozycje LLM odwołujące się do nieznanych operatorów lub metod.

Dla wariantu ewolucyjnego wygeneruj:

1. Populację początkową (zalążkową) programów kandydujących.
2. Deterministyczny ewaluator zwracający skalarny wynik dopasowania (fitness score).
3. Operator mutacji (napędzany przez LLM lub oparty na regułach).
4. Pętlę selekcji i mutacji (zachowanie top-k najlepszych rozwiązań, mutacja, powtórzenie) z warunkiem wczesnego zatrzymania (early stopping).

Kryteria odrzucenia (Hard rejects):

- Systemy ChatHTN, w których wyniki działania LLM są aplikowane bezpośrednio, bez walidacji na podstawie schematu operatora. W takim przypadku gwarancje poprawności przestają obowiązywać.
- Systemy AlphaEvolve, w których ewaluator odpytuje LLM w roli sędziego (LLM-as-a-judge). Funkcja przystosowania musi być deterministyczna; oceny LLM wprowadzają szum stochastyczny, który uniemożliwia zbieżność pętli.
- Stosowanie tych wzorców do zadań otwartych (np. „napisz artykuł na bloga”). Przy braku ewaluatora lub warunków wstępnych należy stosować prostszą pętlę ReAct.

Zasady odmowy (Guardrails):

- Jeśli domena nie posiada precyzyjnie określonego schematu operatorów, odrzuć wdrożenie ChatHTN. Zaproponuj ReWOO lub klasyczny ReAct.
- Jeśli domena nie oferuje możliwości maszynowej weryfikacji kodu, odrzuć wdrożenie AlphaEvolve. Zaproponuj wzorzec samodoskonalenia (Lekcja 05).
- Jeśli użytkownik wymaga, aby „planer oparty na LLM podejmował ostateczne, nieweryfikowane decyzje”, odmów. Należy bezwzględnie zachować rozdział pomiędzy symbolicznym sprawdzaniem poprawności a generatywnymi propozycjami LLM.

Wygenerowana struktura: pliki `operators.py`, `methods.py`, `planner.py` (dla wariantu HTN) lub `evaluator.py`, `mutator.py`, `loop.py` (dla wariantu ewolucyjnego) oraz `README.md` z uzasadnieniem wyboru architektury. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 25 (weryfikacja w stylu debaty wieloagentowej) lub Lekcji 02 (jeśli zadanie ostatecznie pasuje do schematu ReWOO).
