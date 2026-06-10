---

name: skill-evaluation
description: Lista kontrolna strategii oceny dla modeli klasyfikacji i regresji
version: 1.0.0
phase: 2
lesson: 9
tags: [evaluation, metrics, cross-validation, model-selection]

---

# Strategia oceny modelu

Lista kontrolna umożliwiająca prawidłową ocenę dowolnego modelu ML. Postępuj zgodnie z poniższą sekwencją, aby uniknąć najczęstszych błędów w ocenie.

## Krok 1: Prawidłowo podziel dane

- Podziel przed jakimkolwiek przetwarzaniem wstępnym (skalowanie, imputacja, kodowanie)
- Używaj podziałów warstwowych do zadań klasyfikacyjnych
- Zarezerwuj zestaw testowy, którego dotkniesz dokładnie raz na końcu
- W przypadku małych zbiorów danych użyj 5- lub 10-krotnej walidacji krzyżowej zamiast pojedynczego podziału
- W przypadku szeregów czasowych używaj podziałów opartych na czasie (nigdy nie mieszaj)

## Krok 2: Wybierz odpowiednie dane

### Klasyfikacja

| Sytuacja | Użyj tej metryki | Dlaczego |
|----------|----------------|-----|
| Zrównoważone zajęcia, proste porównanie | Dokładność | Łatwe do interpretacji, znaczące, gdy klasy są równe |
| Fałszywe alarmy są kosztowne (filtr spamu, powiadomienia o oszustwach) | Precyzja | Mierzy, ile oznaczonych elementów jest faktycznie pozytywnych |
| Fałszywie negatywne wyniki są kosztowne (badania przesiewowe w kierunku raka, bezpieczeństwo) | Przypomnijmy | Mierzy liczbę rzeczywistych pozytywów, które udało Ci się złapać |
| Trzeba zrównoważyć precyzję i zapamiętywanie | Wynik F1 | Średnia harmoniczna, karze skrajną nierównowagę |
| Porównywanie modeli w różnych progach | AUC-ROC | Jakość rankingu niezależna od progu |
| Niezrównoważone dane | F1, AUC-ROC lub PR-AUC | Dokładność wprowadza w błąd w przypadku niezrównoważonych klas |

### Regresja

| Sytuacja | Użyj tej metryki | Dlaczego |
|----------|----------------|-----|
| Regresja standardowa, dopuszczalne wartości odstające | RMSE | Te same jednostki co cel, karze za duże błędy |
| Ocena wartości odstających | MAE | Traktuje wszystkie błędy jednakowo, nie dominują wartości odstające |
| Porównywanie modeli w różnych skalach | R-kwadrat | Znormalizowana skala 0-1 (wyjaśniony ułamek wariancji) |
| Biznes wymaga kwot w dolarach | MAE lub RMSE | Bezpośrednio interpretowalny jako wielkość błędu |

## Krok 3: Ustalenie wartości bazowych

Przed oceną modelu oblicz wydajność bazową:
- Klasyfikacja: predyktor klasy większościowej (zawsze przewiduje najczęstszą klasę)
- Regresja: zawsze przewidywaj średnią celu treningowego
- Żaden model, który nie jest w stanie pokonać tych wartości bazowych, nie uczy się

## Krok 4: Weryfikacja krzyżowa

- Aby uzyskać stabilne szacunki, użyj współczynnika K (K=5 lub K=10).
- Do klasyfikacji użyj warstwowego współczynnika K-fold
- Podaj średnią i odchylenie standardowe w fałdach
- Model ze średnią=0,85 i std=0,02 jest bardziej godny zaufania niż średnia=0,87 i std=0,10

## Krok 5: Porównaj statystycznie modele

- Nie wybieraj modelu z najwyższym średnim wynikiem bez sprawdzenia istotności
- Użyj sparowanego testu t dla przypadków krzyżowej walidacji
- Jeśli |t| < 2,78 (dla K=5, df=4, p<0,05), różnica może wynikać z przypadku
- Rozważ prostszy model, gdy różnice w wydajności nie są znaczące

## Krok 6: Sprawdź, czy nie występują typowe błędy

- Wyciek danych: czy jakiekolwiek informacje dotyczące danych testowych wpłynęły do ​​szkolenia? (skalowanie przed podziałem, funkcje wywodzące się z celu)
- Nierównowaga klas: czy dokładność ukrywa słabe wyniki klas mniejszościowych?
- Nadmierne dopasowanie: czy różnica pomiędzy wynikami szkolenia i walidacji jest duża?
- Zbyt wiele ocen: czy przeglądałeś zestaw testowy więcej niż raz?

## Krok 7: Zgłoś końcowe wyniki

- Pociąg w pociągu + walidacja łącznie
- Oceń na wyciągniętym zestawie testowym dokładnie raz
- Jeśli to możliwe, zgłoś wybraną metrykę wraz z przedziałami ufności
- Podaj porównanie bazowe (o ile lepsze niż losowe/średnie)