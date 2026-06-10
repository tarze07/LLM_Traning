---

name: skill-imbalanced-data
description: Lista kontrolna decyzji do rozwiązywania problemów niezrównoważonej klasyfikacji
version: 1.0.0
phase: 2
lesson: 17
tags: [imbalanced-data, smote, class-weights, threshold-tuning, evaluation]

---

# Niezrównoważona strategia danych

Lista kontrolna decyzji dotycząca postępowania w przypadku niezrównoważonej klasyfikacji. Postępuj zgodnie z poniższą sekwencją, aby wybrać właściwe podejście do swojego problemu.

## Krok 1: Zmierz niewyważenie

- Policz próbki na klasę
- Oblicz współczynnik braku równowagi (większość / mniejszość)
- Łagodny: stosunek < 3:1 (e.g., 70/30)
- Moderate: ratio 3:1 to 20:1 (e.g., 95/5)
- Severe: ratio > 20:1 (np. 99/1)

## Krok 2: Wybierz odpowiednie dane

Preferuj precyzję/przywołanie/F1 zamiast dokładności w przypadku niezrównoważonych zbiorów danych. Wybierz w zależności od problemu:

| Sytuacja | Podstawowa metryka | Metryka drugorzędna |
|----------|---------------|--------------------------------|
| Brak wyników pozytywnych jest bardzo kosztowny (oszustwo, choroba) | Przypomnijmy | Wynik F2 |
| Fałszywe alarmy są kosztowne (filtr spamu, rekomendacje) | Precyzja | Wynik F0,5 |
| Obydwa mają znaczenie mniej więcej jednakowo | Wynik F1 | MCC |
| Potrzebujesz jednego wskaźnika rankingowego | AUPRC | AUC-ROC |
| Należy porównać zbiory danych | MCC | AUPRC |

## Krok 3: Wybierz strategię przywracania równowagi

### Według wagi braku równowagi

| Brak równowagi | Pierwsza próba | Druga próba | Unikaj |
|---------------|-----------|------------|-------|
| Łagodny (< 3:1) | Class weights | Threshold tuning | Oversampling (unnecessary) |
| Moderate (3:1 to 20:1) | SMOTE + class weights | Threshold tuning on top | Undersampling (too much data loss) |
| Severe (> 20:1) | SMOTE + wagi klas + próg | Zespół ze zrównoważonym pakowaniem | Samo podpróbkowanie |

### Według rozmiaru zbioru danych

| Rozmiar zbioru danych | Preferowana strategia | Powód |
|------------|----------------------|-------|
| < 1,000 samples | Oversampling or SMOTE | Cannot afford to lose majority data |
| 1,000 - 10,000 | SMOTE + threshold tuning | Enough minority samples for k-NN |
| > 10 000 | Wagi klas lub niedopróbkowanie | Szybkie, wystarczające dane mniejszości |

## Krok 4: Zastosuj technikę

### Wagi klas (zawsze próbuj najpierw)
- W sklearnie: `class_weight='balanced'`
- Nie ma potrzeby modyfikacji danych
- Działa z każdym modelem opartym na stratach
- Odpowiednik nadpróbkowania w oczekiwaniu

### PALENIE
- Zastosuj tylko do danych szkoleniowych (nigdy nie testuj/walidacji)
- Użyj k=5 sąsiadów (domyślnie)
- Połącz z ciężarkami klasowymi, aby uzyskać najlepsze wyniki
- Uważaj na hałaśliwe punkty syntetyczne w pobliżu granicy

### Strojenie progu
- Trenuj model, uzyskaj przewidywane prawdopodobieństwa na zestawie walidacyjnym
- Progi przemiatania od 0,05 do 0,95
- Wybierz próg maksymalizujący wybraną metrykę
- Zawsze dostosowuj się do danych walidacyjnych, nigdy nie testuj danych

## Krok 5: Popraw poprawność

- Użyj warstwowej walidacji krzyżowej (zachowuje współczynniki klas w każdym przypadku)
- Raportuj metryki oryginalnego (nieponownego próbkowania) zestawu testowego
- Nigdy nie nakładaj SMOTE przed rozdzieleniem - tylko w fałdach treningowych
- Porównaj z wartością bazową „zawsze przewidywaj większość”.

## Krok 6: Typowe błędy, których należy unikać

- Zastosowanie SMOTE do całego zbioru danych przed podziałem pociągu/testu (wyciek danych)
- Używanie dokładności jako miernika oceny
- Nie próbowanie najpierw wag klas (najprostsze podejście, często wystarczające)
- Nadpróbkowanie, a następnie weryfikacja krzyżowa (syntetyczne punkty wyciekają w fałdach)
- Ignorowanie dostrajania progów (darmowe działanie, bez konieczności ponownego szkolenia)
- Używanie losowego podpróbkowania na małych zbiorach danych (wyrzuca zbyt dużo danych)

## Szybkie drzewo decyzyjne

1. Czy współczynnik niewyważenia wynosi < 3:1? ->. Wypróbuj tylko odważniki klasy
2. Czy zbiór danych obejmuje > 10 000 próbek? -> Wagi klas + strojenie progów
3. Czy zbiór danych < 1,000 samples? -> SMOTE + ma wagi klas
4. Inaczej -> SMOTE + wagi klas + strojenie progów
5. Nadal nie jesteś wystarczająco dobry? -> Zrównoważony zestaw worków