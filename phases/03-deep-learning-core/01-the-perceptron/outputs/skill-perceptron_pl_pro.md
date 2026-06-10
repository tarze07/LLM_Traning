---
name: skill-perceptron
description: Zrozumienie zasady działania perceptronu oraz różnic w zastosowaniach architektur jednowarstwowych i wielowarstwowych.
version: 1.0.0
phase: 3
lesson: 1
tags: [perceptron, neural-networks, classification, deep-learning]
---

# Wzorzec Perceptronu (The Perceptron Pattern)

Perceptron oblicza sumę ważoną sygnałów wejściowych oraz wyrazu wolnego (bias), a następnie przepuszcza ją przez funkcję skokową, generując wynik binarny. Stanowi on podstawową jednostkę budulcową sztucznych sieci neuronowych.

```
output = step(w1*x1 + w2*x2 + ... + wn*xn + bias)
```

## Kiedy pojedynczy perceptron jest wystarczający?

- Problem jest liniowo separowalny: można oddzielić od siebie dwie klasy za pomocą prostej (lub hiperpłaszczyzny).
- Modelowanie bramek logicznych: AND, OR, NOT, NAND.
- Proste decyzje oparte na progach: "czy wartość przekracza X?".
- Binarne klasyfikatory pracujące na danych, które naturalnie dzielą się na dwa nienakładające się na siebie obszary.

## Kiedy potrzebne są architektury wielowarstwowe?

- Problem nie jest separowalny liniowo: nie istnieje pojedyncza prosta, która rozdzieliłaby klasy.
- Rozwiązywanie problemu XOR i sprawdzanie parzystości.
- Problemy wymagające złożonych, warunkowych reguł decyzyjnych (np. "to tak, ale tylko wtedy, gdy tamto nie").
- Klasyfikacja danych rzeczywistych: obrazy, tekst, dźwięk – w tych przypadkach zależności są niemal zawsze nieliniowe.

## Lista kontrolna przy podejmowaniu decyzji

1. Naszkicuj lub przeanalizuj swoje dane. Czy potrafisz narysować pojedynczą, prostą linię oddzielającą klasy?
   - Tak: pojedynczy perceptron poradzi sobie z problemem.
   - Nie: będziesz potrzebować co najmniej dwóch warstw (wielowarstwowej sieci neuronowej).
2. Czy problem da się rozłożyć na zbiór prostszych, liniowych warunków logicznych (AND/OR)?
   - Taka dekompozycja wskaże Ci minimalną wymaganą strukturę sieci.
   - XOR = (A OR B) AND (NOT (A AND B)) = 3 perceptrony w 2 warstwach.
3. W klasyfikacji wieloklasowej (więcej niż 2 klasy) warstwa wyjściowa musi posiadać osobny neuron dla każdej z klas.

## Reguła uczenia

```
error = expected - predicted
weight_new = weight_old + learning_rate * error * input
bias_new = bias_old + learning_rate * error
```

Jeśli predykcja jest poprawna, parametry pozostają bez zmian. Jeśli model popełnia błąd, wagi są aktualizowane w kierunku zmniejszającym ten błąd. Mechanizm ten sprawdza się wyłącznie w przypadku perceptronów jednowarstwowych. Sieci wielowarstwowe do nauki wykorzystują algorytm wstecznej propagacji błędu (backpropagation).

## Najczęstsze błędy

- Próba modelowania nieliniowych zależności przy użyciu jednowarstwowego perceptronu (model nigdy nie zbiegnie do poprawnego rozwiązania).
- Ustawienie zbyt wysokiego współczynnika uczenia (learning rate) prowadzi do oscylacji wag, natomiast zbyt niski współczynnik drastycznie spowalnia cały proces.
- Zapominanie o wyrazie wolnym (bias) – bez niego granica decyzyjna jest zmuszona do przechodzenia przez środek układu współrzędnych (początek układu).
- Mylenie gwarancji zbieżności perceptronu (która zachodzi tylko dla danych liniowo separowalnych) z problemem zbieżności złożonych sieci neuronowych (gdzie uniwersalna gwarancja zbieżności do minimum globalnego nie istnieje).
