---

name: skill-classification-diagnostics
description: Biorąc pod uwagę macierz zamieszania i nazwy klas, wykaż awarie poszczególnych klas i zaproponuj jedną, najskuteczniejszą poprawkę
version: 1.0.0
phase: 4
lesson: 4
tags: [computer-vision, classification, evaluation, debugging]

---

# Diagnostyka błędów klasyfikacji (Classification Diagnostics)

Narzędzie do interpretacji macierzy pomyłek (confusion matrix). Podczas gdy zagregowana dokładność (accuracy) pokazuje jedynie ogólny poziom działania klasyfikatora, macierz pomyłek ujawnia, *jakich błędów model wciąż nie potrafi uniknąć*.

## Zastosowanie

- Ocena jakości predykcji modelu na zbiorze walidacyjnym po zakończeniu treningu.
- Analiza różnic między kolejnymi próbami treningowymi w celu podjęcia decyzji o zmianie hiperparametrów lub danych.
- Weryfikacja działania modelu przed wdrożeniem produkcyjnym w celu upewnienia się, że żadna krytyczna klasa nie wykazuje cichych błędów.
- Analiza spadków jakości działania systemu produkcyjnego (np. gdy zagregowana dokładność obniżyła się o 1 punkt procentowy).

## Dane wejściowe

- `cm`: macierz pomyłek o wymiarach $C \times C$ (wiersze = rzeczywiste klasy, kolumny = przewidywane klasy).
- `labels`: uporządkowana lista zawierająca $C$ nazw klas.
- Opcjonalny parametr `class_priors`: rozkład klas w zbiorze treningowym (domyślnie suma wierszy macierzy `cm`).

## Procedura diagnostyczna

1. **Obliczenie miar dla poszczególnych klas**: W przypadku wystąpienia dzielenia przez zero, oznacz metrykę jako niezdefiniowaną (`n/a`) – nie wolno automatycznie zastępować jej wartością 0.
   - $\text{precyzja}_i (\text{precision}) = \frac{cm[i,i]}{\sum_j cm[j, i]}$ (niezdefiniowana, gdy klasa ani razu nie została przewidziana)
   - $\text{czułość}_i (\text{recall}) = \frac{cm[i,i]}{\sum_j cm[i, j]}$ (niezdefiniowana, gdy w zbiorze brak rzeczywistych próbek dla danej klasy)
   - $F1_i = \frac{2 \cdot \text{precyzja}_i \cdot \text{czułość}_i}{\text{precyzja}_i + \text{czułość}_i}$ (niezdefiniowana, gdy precyzja lub czułość ma wartość `n/a`)

2. **Wybór trzech najsłabszych klas** pod kątem miary F1. Jeśli model klasyfikuje mniej niż 3 klasy, przeanalizuj wszystkie dostępne. Wyklucz z rankingu klasy o niezdefiniowanych metrykach.

3. **Identyfikacja najczęstszej pomyłki dla każdej ze słabych klas**: Odszukaj komórkę poza główną przekątną o najwyższej wartości w danym wierszu macierzy pomyłek (klasa, z którą model najczęściej myli klasę rzeczywistą). Zgłoś w formacie: `klasa rzeczywista -> klasa przewidywana`.

4. **Klasyfikacja typu błędu (failure mode)** dla każdej z najsłabszych klas na podstawie kryteriów ilościowych:
   - **ambiguity (niejednoznaczność)**: obustronne mylenie klas ze sobą, gdy zachodzi jednocześnie: $\frac{cm[i,j]}{\sum_k cm[i, k]} \ge 0.15$ oraz $\frac{cm[j,i]}{\sum_k cm[j, k]} \ge 0.15$.
   - **imbalance (niezbalansowanie)**: liczba próbek treningowych dla analizowanej klasy jest mniejsza niż połowa ($< 0.5\times$) liczby próbek klasy, z którą jest najczęściej mylona.
   - **label_noise (szum w etykietach)**: gdy zachodzi $|\text{precyzja}_i - \text{czułość}_i| \ge 0.2$, a klasa nie wykazuje cech niezbalansowania lub niejednoznaczności.
   - **systematic (błąd systematyczny)**: żaden pojedynczy błąd mylenia z inną klasą nie stanowi więcej niż 20% wszystkich pomyłek; błędy są rozproszone na trzy lub więcej różnych klas.

5. **Określenie rekomendacji (działania naprawczego)** o najwyższym priorytecie:
   - **ambiguity**: pozyskaj lub wygeneruj (np. syntetycznie) przykłady zawierające unikalne cechy różnicujące te klasy; dodaj dedykowaną augmentację danych, która nie niszczy cech charakterystycznych dla danej klasy.
   - **imbalance**: zastosuj oversampling dla klasy mniejszościowej lub wprowadź ważoną funkcję straty (wagi klas w `CrossEntropyLoss`).
   - **label_noise**: przeprowadź audyt jakości etykietowania dla tej klasy; popraw błędne etykiety przed dokonywaniem jakichkolwiek innych zmian w kodzie lub parametrach uczenia.
   - **systematic**: zwiększ wolumen danych treningowych dla tej klasy lub zwiększ wagę przypisaną do jej straty.

## Format raportu

```
[diagnostics]
  ogólna dokładność:  X.XX
  macro F1:           X.XX

[top-3 najsłabsze klasy]
  1. klasa <nazwa>  F1 = X.XX  precyzja = X.XX  czułość = X.XX
     najczęstsza pomyłka: <klasa rzeczywista> -> <klasa przewidywana> (N przypadków)
     typ błędu:           ambiguity | imbalance | label_noise | systematic
     działanie:           <rekomendacja opisana w jednym zdaniu>

  2. ...
  3. ...

[rekomendacja]
  najważniejsze działanie naprawcze: <konkretna klasa, wskazany problem i sposób jego naprawy w jednym zdaniu>
```

## Reguły

- Analizuj maksymalnie trzy najsłabsze klasy. Raportowanie większej liczby klas rozmywa istotne wnioski.
- Zawsze wskazuj jedną konkretną klasę, z którą model najczęściej myli analizowaną klasę; unikaj ogólnych stwierdzeń typu „klasa często mylona z wieloma innymi”.
- Każde zalecenie musi bezpośrednio wynikać z analizy liczbowej macierzy pomyłek. Unikaj ogólnych rad typu „dodaj więcej danych” bez precyzyjnego wskazania klasy i proponowanego typu próbek.
- Gdy precyzja (precision) i czułość (recall) różnią się o więcej niż 0.2, zawsze w pierwszej kolejności podejrzewaj szum w etykietach (label noise) – w prawidłowo wytrenowanym modelu na czystych danych te dwie miary są zazwyczaj na zbliżonym poziomie.
