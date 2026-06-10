---

name: skill-classification-diagnostics
description: Biorąc pod uwagę macierz zamieszania i nazwy klas, wykaż awarie poszczególnych klas i zaproponuj jedną, najskuteczniejszą poprawkę
version: 1.0.0
phase: 4
lesson: 4
tags: [computer-vision, classification, evaluation, debugging]

---

# Diagnostyka klasyfikacyjna

Soczewka do czytania matryc zamieszania. Zagregowana dokładność mówi, że klasyfikator działa. Matryca zamieszania mówi *czego jeszcze nie wie*.

## Kiedy używać

- Najpierw spójrz na wydajność walidacji przeszkolonego klasyfikatora.
- Pomiędzy biegami treningowymi, aby zdecydować, co dalej zmienić.
- Przed wysyłką modelu: sprawdzenie, czy żadna klasa krytyczna nie ulega cichym awariom.
- Debugowanie regresji produkcyjnej, w której ogólna dokładność spadła o jeden punkt i musisz wiedzieć, dlaczego.

## Wejścia

- `cm`: macierz zamieszania CxC (wiersze = prawda, kolumny = przewidywane).
- `labels`: lista nazw klas C, w tej samej kolejności.
- Opcjonalnie `class_priors`: częstotliwość szkoleń w poszczególnych klasach (domyślnie jest to suma wierszy `cm`).

## Kroki

1. **Oblicz metryki dla poszczególnych klas.** Każde dzielenie przez zero należy traktować jako metrykę niezdefiniowaną dla tej klasy i zgłosić ją jako `n/a`; nigdy nie zastępuj po cichu 0.
   - precyzja_i = cm[i,i] / suma(cm[:, i]) (nieokreślona, gdy klasa nigdy nie była przewidziana)
   - przypomnieć_i = cm[i,i] / sum(cm[i, :]) (niezdefiniowane, gdy klasa nie ma próbek prawdy podstawowej)
   - f1_i = 2 * p * r / (p + r) (nieokreślony, gdy którykolwiek ze składników jest niezdefiniowany)

2. **Awansuj do trzech najgorszych klas** w F1. Jeżeli macierz zamieszania ma mniej niż trzy klasy, należy uszeregować dowolną ich liczbę. Wyklucz klasy z niezdefiniowanymi wszystkimi metrykami.

3. **Znajdź górną komórkę znajdującą się poza przekątną w każdym rzędzie** — jest to jedyna klasa, która najczęściej kradnie z tej klasy. Zgłoś jako `true -> predicted`.

4. **Sklasyfikuj tryb awarii** dla każdej najgorszej klasy. Użyj tych progów ilościowych, aby etykieta była powtarzalna:
   - `ambiguity` — dwukierunkowe pomieszanie z inną klasą: zarówno `cm[i,j] / sum(cm[i, :]) >= 0.15`, jak i `cm[j,i] / sum(cm[j, :]) >= 0.15`.
   - `imbalance` — klasa ma `< 0.5x` jako liczbę treningową swojego najwyższego zakłócacza.
   - `label_noise` — `|precision_i - recall_i| >= 0.2` i klasa nie znajduje się na ścieżkach nierównowagi/niejednoznaczności.
   - `systematic` — żaden pojedynczy dezorientator nie przekracza 0,2 udziału błędów tej klasy; błędy rozłożone na trzy lub więcej innych klas.

5. **Zaproponuj kolejne, najbardziej wpływowe działanie**:
   - `ambiguity` -> zbieraj lub syntetyzuj wyróżniające przykłady, dodaj ukierunkowane wzmocnienie, które zachowuje cechę wyróżniającą.
   - `imbalance` -> nadpróbkuj klasę mniejszości lub zastosuj stratę ważoną klasą.
   - `label_noise` -> audyt warstwowej próby klasy; napraw błędne etykiety przed wprowadzeniem jakichkolwiek innych zmian.
   - `systematic` -> zwiększ dane dla klasy lub dostosuj z wyższą wagą straty tej klasy.

## Zgłoś

```
[diagnostics]
  aggregate accuracy: X.XX
  macro F1:           X.XX

[top-3 worst classes]
  1. class <name>  F1 = X.XX  prec = X.XX  rec = X.XX
     top confusion: <name> -> <other>  (N cases)
     failure mode:  ambiguity | imbalance | label_noise | systematic
     action:        <one sentence>

  2. ...
  3. ...

[recommendation]
  single biggest lever: <one sentence naming the class and the fix>
```

## Zasady

- Wróć maksymalnie trzy klasy. Więcej ukrywa sygnał.
- Wymień dominujący czynnik zakłócający dla każdej najgorszej klasy; nigdy nie podsumowuj jako „mylący z wieloma”.
- Oprzyj każde zalecenie na dowodach z matrycy zamieszania. Żadnego ogólnego „dodaj więcej danych” bez określenia, która klasa.
- Kiedy precyzja i zapamiętywanie różnią się o więcej niż 0,2, zawsze zaznaczaj szum na etykiecie jako kandydata — w prawdziwych klasach zwykle po szkoleniu wyrównane są P i R.