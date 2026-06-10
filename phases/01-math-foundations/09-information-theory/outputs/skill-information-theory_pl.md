---

name: skill-information-theory
description: Zastosuj koncepcje teorii informacji do funkcji strat ML, oceny modelu i wyboru funkcji
version: 1.0.0
phase: 1
lesson: 9
tags: [information-theory, entropy, loss-functions]

---

# Teoria informacji dla ML

Kiedy stosować entropię, entropię krzyżową, rozbieżność KL i wzajemne informacje w systemach uczenia maszynowego.

## Lista kontrolna decyzji

1. Pomiar niepewności w pojedynczym rozkładzie? Użyj **entropii**.
2. Mierzenie tego, jak dobrze model przybliża prawdziwe etykiety? Użyj **entropii krzyżowej** (jest to utrata klasyfikacji).
3. Pomiar odległości pomiędzy dwoma rozkładami? Użyj **rozbieżności KL**.
4. Sprawdzanie, czy dwie zmienne są ze sobą powiązane? Korzystaj z **wzajemnych informacji**.
5. Jakość modelu języka raportowania? Użyj **zakłopotania** (wykładniczy entropii krzyżowej).
6. Destylacja jednego modelu w drugi? Minimalizuj **rozbieżności KL** pomiędzy nauczycielem a uczniem.

## Kiedy używać poszczególnych miar

| Zmierz | Formuła | Przypadek użycia | Aplikacja ML |
|---|---|---|---|
| Entropia H(P) | -sum(p log p) | Jak niepewny jest ten rozkład? | Złożoność danych, modele maksymalnej entropii |
| Entropia krzyżowa H(P,Q) | -sum(p log q) | Jak dobry jest model Q w przewidywaniu prawdziwego P? | Utrata klasyfikacji, utrata modelu językowego |
| Rozbieżność KL D(P\|\|Q) | suma(plog(p/q)) | Jak różne są P i Q? | Strata VAE (ELBO), destylacja wiedzy, RLHF |
| Wzajemne informacje I(X;Y) | H(X) - H(X\|Y) | Ile Y mówi nam o X? | Wybór cech, uczenie się reprezentacji |
| Zakłopotanie | exp(H(P,Q)) lub 2^H | Jak bardzo zdezorientowany jest model? | Ocena modelu języka |
| Entropia warunkowa H(X\|Y) | -sum(p(x,y) log p(x\|y)) | Pozostała niepewność w X po poznaniu Y | Funkcja informacyjna |

## Kluczowe relacje

```
Cross-entropy  = Entropy + KL divergence
H(P, Q)        = H(P)   + D_KL(P || Q)

Since H(P) is constant during training:
  Minimizing cross-entropy = Minimizing KL divergence

Mutual information = Entropy - Conditional entropy
I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)

Perplexity = exp(cross-entropy in nats)
           = 2^(cross-entropy in bits)
```

## Skrócona instrukcja: formuły i jednostki

| Formuła | Bity (podstawa logu 2) | Nats (podstawa dziennika e) |
|---|---|---|
| Informacja: -log(p) | -log2(p) | -ln(p) |
| Entropia: -sum(p log p) | bity | nat |
| 1 nat = | 1,4427 bitów | 1 nat |
| Domyślne PyTorch | -- | nat |
| Artykuły z teorii informacji | bity | -- |

## Interpretowanie wartości

| Wartość entropii | Co to znaczy |
|---|---|
| 0 | Deterministyczny. Prawdopodobieństwo jednego wyniku wynosi 1. |
| log(n) | Maksymalna niepewność. Równomierny rozkład na n wyników. |
| Niski | Dystrybucja osiąga szczyt. Modelka jest pewna siebie. |
| Wysoki | Dystrybucja jest płaska. Model jest niepewny. |

| Wartość zakłopotania | Jakość modelu języka |
|---|---|
| 1 | Perfekcyjne przewidywanie (w praktyce nigdy się nie zdarza) |
| 10 | Wybieranie średnio spośród ~10 równie prawdopodobnych żetonów |
| 50 | Poziom GPT-2 w standardowych benchmarkach |
| < 10 | State-of-the-art for well-represented domains |

## Common mistakes

- Computing KL divergence and treating it as symmetric. D_KL(P||Q) != D_KL(Q||P). For a symmetric measure, use Jensen-Shannon divergence: JS = 0.5 * KL(P||M) + 0.5 * KL(Q||M) where M = 0.5*(P+Q).
- Forgetting that cross-entropy with one-hot labels simplifies to -log(p_true_class). You do not need to sum over all classes when the true distribution is one-hot.
- Using log base 2 in code but reporting nats (or vice versa). PyTorch uses natural log by default. Multiply by log2(e) = 1.4427 to convert nats to bits.
- Computing entropy of an empty or zero-probability event. Convention: 0 * log(0) = 0, because lim(p->0) p*log(p) = 0.
- Porównywanie zakłopotania w różnych słownikach. Modelu ze słownictwem o rozmiarze 50 tys. i zakłopotaniem 30 nie można bezpośrednio porównywać z modelem o rozmiarze słownictwa 10 tys. i zakłopotaniu 30.

## Gdzie każda koncepcja pojawia się w produkcyjnym ML

| Koncepcja | Gdzie to widzisz |
|---|---|
| Strata między entropią | Każdy model klasyfikacyjny (nn.CrossEntropyLoss) |
| Rozbieżność KL | VAE ELBO, wycinanie PPO, destylacja wiedzy |
| Uregulowanie entropii | Premia za eksplorację w RL (wyższa entropia = więcej eksploracji) |
| Wzajemne informacje | Wybór funkcji, utrata InfoNCE (uczenie kontrastowe) |
| Zakłopotanie | Testy porównawcze modelu języka (niższy = lepszy) |
| Wygładzanie etykiet | Zastępuje jeden gorący cel miękkim celem, zmniejsza nadmierną pewność entropii krzyżowej |
| Skalowanie temperatury | Dzieli logity przez T przed softmax, kontroluje entropię wyjścia |