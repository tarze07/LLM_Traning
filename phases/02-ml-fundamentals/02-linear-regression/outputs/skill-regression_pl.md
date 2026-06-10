---

name: skill-regression
description: Wybierz odpowiednie podejście regresyjne w oparciu o charakterystykę danych i ograniczenia problemu
version: 1.0.0
phase: 2
lesson: 2
tags: [regression, linear-regression, polynomial-regression, ridge, regularization]

---

# Przewodnik po strategii regresji

Regresja przewiduje wartości ciągłe. Właściwe podejście zależy od relacji między cechami a celem, liczby cech i ryzyka nadmiernego dopasowania.

## Lista kontrolna decyzji

1. Czy związek między cechami a celem jest w przybliżeniu liniowy?
   - Tak: zacznij od zwykłej regresji liniowej
   - Nie: wypróbuj funkcje wielomianowe lub model nieliniowy

2. Ile funkcji masz w porównaniu z próbkami?
   - Niewiele funkcji, wiele próbek: zwykła regresja liniowa działa dobrze
   - Wiele funkcji, kilka próbek: użyj regularyzacji (Ridge lub Lasso)
   - Więcej funkcji niż próbek: Lasso (L1), aby wybrać funkcje lub Ridge (L2), aby zmniejszyć wszystkie wagi

3. Czy potrzebujesz interpretowalności?
   - Tak: regresja liniowa z kilkoma cechami lub Lasso do automatycznego wyboru cech
   - Nie: funkcje wielomianowe lub przejdź do modeli opartych na drzewach lub sieci neuronowych

4. Czy Twój zbiór danych jest mały (poniżej 10 000 wierszy)?
   - Użyj równania normalnego (rozwiązanie w formie zamkniętej) dla prędkości
   - Walidacja krzyżowa jest niezbędna do wiarygodnej oceny

5. Czy Twój zbiór danych jest duży (miliony wierszy)?
   - Stosuj zniżanie w gradiencie stochastycznym (SGD) lub zniżanie w gradiencie mini-wsadowym
   - Równanie normalne jest zbyt wolne z powodu inwersji macierzy O(n^3).

## Kiedy zastosować każde podejście

**Zwykła regresja liniowa**: punkt odniesienia dla dowolnego zadania regresji. Zacznij tutaj. Jeśli R-kwadrat jest akceptowalny, a model jest prosty, zatrzymaj się tutaj.

**Regresja wielomianowa**: wykres punktowy przedstawia krzywą, a nie linię. Zacznij od stopnia 2. Zwiększaj tylko wtedy, gdy jest to uzasadnione wynikami walidacji. Stopień > 5 prawie zawsze przewyższa.

**Regresja grzbietu (L2)**: wiele skorelowanych cech. Wszystkie wagi kurczą się w stronę zera, ale żadna nie osiąga dokładnie zera. Dobrze, jeśli wierzysz, że wszystkie funkcje mają swój udział.

**Regresja Lasso (L1)**: wiele funkcji, a podejrzewasz, że tylko kilka ma znaczenie. Lasso ustawia nieistotne wagi cech dokładnie na zero, dokonując automatycznego wyboru cech.

**Elastyczna siatka**: łączy kary L1 i L2. Użyj, jeśli masz wiele skorelowanych funkcji i chcesz wybrać pewne funkcje.

## Typowe błędy

- Pomijanie skalowania cech przed spadkiem gradientu (zbieżność staje się bardzo powolna)
- Wykorzystanie wydajności zestawu testowego do dostrojenia hiperparametrów (użyj zestawu walidacyjnego lub walidacji krzyżowej)
- Dopasowywanie wielomianów wysokiego stopnia bez sprawdzania błędu walidacji (trenowanie R^2 zawsze rośnie wraz ze stopniem)
- Ignorowanie wykresów reszt (R^2 może wprowadzać w błąd, jeśli reszty wykazują wzorce)
- Traktowanie R^2 jako jedynej metryki (sprawdź rozkład rezydualny, MAE i progi specyficzne dla domeny)

## Szybkie odniesienie

| Metoda | Kiedy używać | Regularyzacja | Wybór funkcji |
|------------|------------|---------------|--------------------------------|
| OLS | Baza, kilka funkcji | Brak | Instrukcja |
| Grzbiet | Wiele funkcji, wszystkie istotne | L2 (zmniejszenie) | Nie |
| Lasso | Wiele funkcji, kilka istotnych | L1 (zero) | Automatyczny |
| Elastyczna siatka | Wiele skorelowanych funkcji | L1 + L2 | Częściowe |
| Wielomian | Zależność nieliniowa | Dodaj Ridge/Lasso na górze | Ręczny wybór stopnia |