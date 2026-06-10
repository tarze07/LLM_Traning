---

name: hybrid-planner
description: Zbuduj hybrydowy planista — ChatHTN dla sprawdzonych planów, AlphaEvolve do wyszukiwania kodu za pomocą oceniającego sprawdzalnego maszynowo — i wybierz właściwy dla problemu.
version: 1.0.0
phase: 14
lesson: 11
tags: [planning, htn, chathtn, alphaevolve, evolutionary-search]

---

Biorąc pod uwagę klasę problemu (przepływ pracy związany z zasadami vs optymalizacja kodu vs zadanie otwarte), wybierz planistę i utwórz prawidłowe rusztowanie.

Decyzja:

1. Czy problem ma twarde warunki wstępne/ograniczenia związane z polityką/harmonogramem? -> HTN (ChatHTN).
2. Czy problem ma deterministyczną, sprawdzalną maszynowo funkcję przystosowania? -> Ewolucyjny (AlphaEvolve).
3. Ani? -> Zamiast tego sięgnij po ReAct (lekcja 01) lub ReWOO (lekcja 02).

Dla HTN wyprodukuj:

1. Typ `Operator` z `preconditions`, `effects_add`, `effects_remove`.
2. Typ `Method` z `task`, `preconditions`, `subtasks`.
3. Planista, który najpierw wypróbowuje metody, następnie wraca do dekompozycji LLM i buforuje udane dekompozycje LLM.
4. Etap walidacji, który odrzuca rozkłady LLM odwołujące się do nieznanych operatorów lub metod.

Dla Evolutionary wyprodukuj:

1. Populacja zalążkowa programów kandydujących.
2. Deterministyczny ewaluator zwracający sprawność skalarną.
3. Operator mutacji (sterowany LLM lub oparty na regułach).
4. Pętla wyboru (utrzymaj górne-k, zmutuj, powtórz) z wcześniejszym zatrzymaniem.

Twarde odrzucenia:

- ChatHTN, w którym dane wyjściowe LLM są stosowane bezpośrednio, bez sprawdzania schematu operatora. Twierdzenie o solidności nie sprawdza się.
- AlphaEvolve, gdzie oceniający wzywa sędziego LLM. Sprawność musi być deterministyczna; Sędziowie LLM wprowadzają szum stochastyczny, po którym pętla nie może się zregenerować.
- Dowolny wzór dla zadań otwartych („napisz post na blogu”). Bez oceniającego, bez warunków wstępnych -> użyj ReAct.

Zasady odmowy:

- Jeśli domena nie ma jasnego schematu operatora, odrzuć ChatHTN. Zaproponuj ReWOO lub zwykły ReAct.
- Jeśli domena nie ma możliwości sprawdzenia maszynowego, odrzuć AlphaEvolve. Zaproponuj samodoskonalenie (lekcja 05).
- Jeśli użytkownik chce, aby „planista + LLM podjął ostateczną decyzję”, odmów. Rozdźwięk pomiędzy poprawnością symboliczną a eksploracją LLM jest nośny.

Dane wyjściowe: `operators.py`, `methods.py`, `planner.py` (HTN) lub `evaluator.py`, `mutator.py`, `loop.py` (ewolucyjne) plus `README.md` z uzasadnieniem decyzji. Zakończ słowami „co dalej czytać”, wskazując Lekcję 25, jeśli weryfikacja w stylu debaty pasuje do problemu, lub Lekcję 02, jeśli mimo wszystko zadanie ma kształt ReWOO.