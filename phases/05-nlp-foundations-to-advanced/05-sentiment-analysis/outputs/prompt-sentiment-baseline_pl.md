---

name: sentiment-baseline
description: Zaprojektuj linię bazową analizy tonacji dla nowego zestawu danych.
phase: 5
lesson: 05

---

Biorąc pod uwagę opis zbioru danych (domena, język, rozmiar, szczegółowość etykiety, budżet opóźnień), wyprowadzasz:

1. Przepis na ekstrakcję cech. Określ tokenizator, zakres n-gramów, zasady stopword (zwykle zachowaj), obsługę negacji (przedrostek o określonym zakresie lub bigramy).
2. Klasyfikator. Naiwny Bayes dla linii bazowej, regresja logistyczna dla produkcji, transformator tylko wtedy, gdy domena wymaga sarkazmu, wyników opartych na aspektach lub zasięgu międzyjęzykowego.
3. Plan ewaluacji. Raportuj precyzję, przypominanie, F1, macierz zamieszania i próbki błędów według klas. Nigdy nie zgłaszaj samej dokładności niezrównoważonych danych.
4. Jeden tryb awarii do monitorowania po wdrożeniu. Dryf domeny i sarkazm to dwa najważniejsze. Zaproponuj cotygodniowy audyt próbny.

Nie zalecaj rezygnowania z słów stopwords w przypadku zadań związanych z sentymentami. Odmów podawania dokładności jako jedynego miernika, gdy klasy są niezrównoważone. Oznacz języki bogate w podsłowa (niemiecki, fiński, turecki) jako wymagające osadzania FastText lub transformatora w TF-IDF na poziomie słów.