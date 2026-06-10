---
name: skill-perceptron
description: Zrozumienie wzorca perceptronu i tego, kiedy używać architektur jednowarstwowych, a kiedy wielowarstwowych
version: 1.0.0
phase: 3
lesson: 1
tags: [perceptron, neural-networks, classification, deep-learning]
---

# Wzorzec Perceptronu (The Perceptron Pattern)

Perceptron oblicza ważoną sumę wejść i obciążenia (bias), a następnie nakłada funkcję skokową, tworząc tym samym wynik binarny. Jest podstawową jednostką sieci neuronowych.

```
output = step(w1*x1 + w2*x2 + ... + wn*xn + bias)
```

## Kiedy pojedynczy perceptron wystarcza

- Problem jest liniowo separowalny: linia prosta (lub hiperpłaszczyzna) może podzielić dwie klasy.
- Bramki logiczne: AND, OR, NOT, NAND
- Proste decyzje z wartościami progowymi: "czy wynik jest wyższy niż X?"
- Klasyfikatory binarne na danych, które naturalnie grupują się w dwóch nienakładających się na siebie rejonach.

## Kiedy potrzebujesz wielu warstw

- Problem nie jest separowalny liniowo: nie ma takiej pojedynczej linii, która mogłaby oddzielić od siebie klasy.
- Problemy XOR i parytetowe
- Każde zdanie wymagające analizy w stylu "to tak, ale tamto nie" (kombinacje warunków)
- Klasyfikacje na rzeczywistych danych: obrazy, tekst, audio - w ich przypadku zależności niemal zawsze są nieliniowe.

## Lista kontrolna podczas podejmowania decyzji

1. Naszkicuj albo zbadaj swoje dane. Jesteś w stanie narysować pojedynczą, prostą linię podziału pomiędzy klasami?
   - Tak: pojedynczy perceptron zadziała
   - Nie: będziesz potrzebować chociaż dwóch warstw
2. Da się podzielić ten problem na prostsze, liniowe zdania bazujące na logice AND/OR?
   - Taki podział pokaże Ci minimalną wymaganą strukturę sieci
   - XOR = (A OR B) AND (NOT (A AND B)) = 3 perceptrony, 2 warstwy
3. Problem z więcej niż 2 klasami wymaga posiadania pojedynczego węzła wyjściowego (node) dla każdej klasy.

## Reguła treningowa

```
error = expected - predicted
weight_new = weight_old + learning_rate * error * input
bias_new = bias_old + learning_rate * error
```

Jeśli przewidywania są poprawne, nic się nie zmienia. Jeśli złe, wagi zmienią się, w celu zmniejszenia błędu. Działa to wyłącznie na perceptronach z jedną warstwą. Systemy o wielu warstwach wykorzystują algorytmy propagacji wstecznej.

## Częste błędy

- Staranie się wykorzystać nieliniowe zależności z perceptronem mającym tylko 1 warstwę (nigdy nie znajdzie rozwiązania)
- Ustalenie zbyt wysokiego progu uczenia się (learning rate) powoduje oscylowanie wag, a ustalenie go zbyt nisko sprawia, że cały proces trwa w nieskończoność
- Zapominanie o wyrazie obciążenia (bias) – bez niego granica decyzyjna musi przejść przez środek układu (0)
- Mylenie zbieżności perceptronu (która jest gwarantowana na zbiorach danych liniowo separowalnych) z uniwersalną zbieżnością sieci neuronowych (która gwarantowana nie jest)