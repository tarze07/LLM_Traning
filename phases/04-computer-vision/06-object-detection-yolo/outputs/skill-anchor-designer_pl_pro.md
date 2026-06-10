---

name: skill-anchor-designer
description: Biorąc pod uwagę zbiór danych pól prawdy, uruchom k-średnie na (w, h) i zwróć zestawy kotwic na poziom FPN plus statystyki pokrycia
version: 1.0.0
phase: 4
lesson: 6
tags: [computer-vision, detection, anchors, kmeans]

---

# Projektant ramek kotwiczących (Anchor Designer)

Rozmiary ramek kotwiczących (anchors) to hiperparametr w największym stopniu zależny od specyfiki zbioru danych w detektorach bazujących na kotwicach. Domyślne wymiary kotwic wyznaczone na zbiorze COCO słabo sprawdzają się w przypadku obrazów z hodowli komórkowych, zdjęć satelitarnych czy systemów monitoringu dedykowanych do małych obiektów. Niniejszy moduł pozwala na zaprojektowanie wymiarów kotwic optymalnie dopasowanych do Twoich danych.

## Zastosowanie

- Przed pierwszym uruchomieniem treningu detektora na nowym zbiorze danych.
- Gdy poprawnie skonfigurowany model wykazuje niską czułość (recall) dla obiektów bardzo małych lub bardzo dużych.
- Po znaczącym rozszerzeniu zbioru danych, które mogło wpłynąć na zmianę rozkładu rozmiarów ramek otaczających.

## Dane wejściowe

- `boxes`: tablica NumPy o wymiarach `(N, 4)` zawierająca współrzędne ramek otaczających w formacie `(cx, cy, w, h)` lub `(x1, y1, x2, y2)`. Rekomenduje się dostarczenie co najmniej 1000 ramek obiektów.
- `num_anchors_per_level`: liczba ramek kotwiczących na każdy poziom sieci (zwykle 3).
- `num_fpn_levels`: liczba poziomów sieci FPN (zwykle 3 dla P3, P4, P5 lub 4).
- `input_size`: rozdzielczość obrazów w czasie treningu (szerokość x wysokość).
- Opcjonalny parametr `strides`: kroki próbkowania dla kolejnych poziomów; w przypadku pominięcia, zostaną przyjęte wartości `[8, 16, 32, 64]` dla kolejnych poziomów FPN. Przekaż tę tablicę jawnie, jeśli Twój detektor korzysta z innych wartości.

## Procedura obliczeniowa

1. **Normalizacja wymiarów ramek**: Przelicz wymiary ramek do wartości w pikselach odpowiadających rozdzielczości `input_size`. Odrzuć wszystkie ramki, których szerokość ($w$) lub wysokość ($h$) wynosi mniej niż 2 piksele.

2. **Algorytm K-Means**: Uruchom algorytm K-Means na parach wymiarów `(w, h)` dla liczby klastrów $K = \text{num\_anchors\_per\_level} \times \text{num\_fpn\_levels}$. Jako funkcję odległości (metrykę) zastosuj $1 - \text{IoU}$, a nie odległość euklidesową – odległość euklidesowa na wymiarach `(w, h)` powoduje błędne łączenie wąskich i wysokich ramek z ramkami kwadratowymi. Wszystkie ramki powinny mieć równy wpływ (brak wag); jeśli zbiór danych jest niezbalansowany klasowo i zależy Ci na wysokiej czułości (recall) dla większych ramek, powtórz rzadkie ramki w danych wejściowych, zamiast przekazywać wektor wag.

3. **Sortowanie klastrów**: Posortuj wyznaczone centra klastrów rosnąco według ich pola powierzchni. Podziel je na `num_fpn_levels` grup po `num_anchors_per_level` ramek w każdej. Najmniejsze ramki przypisz do poziomów o najwyższej rozdzielczości (najmniejszy krok próbkowania / stride).

4. **Obliczanie statystyk pokrycia** dla każdego poziomu FPN:
   - Mediana IoU (`median IoU`) każdej rzeczywistej ramki (ground-truth) względem najlepiej dopasowanej kotwicy na tym poziomie.
   - Czułość (`recall@IoU=0.5`) – odsetek ramek, dla których najlepiej dopasowana kotwica osiąga IoU $\ge 0.5$.
   - Pokrycie powierzchni (`area coverage`) – odsetek ramek, których pole powierzchni mieści się w przedziale $[\text{anchor\_min\_area} / 4, \text{anchor\_max\_area} \times 4]$ dla danego poziomu.

5. **Weryfikacja jakości**: Oznacz dany poziom flagą ostrzegawczą, jeśli wartość $\text{recall@IoU=0.5} < 0.9$. Oznacza to, że wymiary kotwic dla tego poziomu są niedopasowane do danych i wymagają korekty lub zwiększenia liczby kotwic na poziom.

## Format raportu

```
[anchor-designer]
  total boxes:         <liczba ramek w zbiorze>
  clusters:            <liczba klastrów K>
  distance metric:     1 - IoU

[level P3  stride=8]
  anchors (w, h):      [(A, B), (C, D), (E, F)]
  median IoU:          <wartość>
  recall@IoU=0.5:      <wartość>
  coverage:            <wartość>
  flag:                ok | retune (dostrój)

[level P4  stride=16]
  ...

[summary]
  overall recall@IoU=0.5: <wartość ogólna>
  smallest anchor:        <szerokość x wysokość>
  largest anchor:         <szerokość x wysokość>
  recommendation:         <jedno zdanie rekomendacji, jeśli którykolwiek poziom ma flagę retune>
```

## Reguły

- Zawsze używaj odległości opartej na IoU ($1 - \text{IoU}$); odległość euklidesowa w K-Means generuje wizualnie poprawne, lecz znacznie gorsze w praktyce zestawy kotwic.
- Sortuj klastry według pola powierzchni przed przypisaniem ich do odpowiednich poziomów FPN (rosnąco).
- Jeśli `num_anchors_per_level == 1`, pomiń algorytm K-Means: podziel ramki na `num_fpn_levels` przedziałów na podstawie kwantyli powierzchni (np. tercyle dla 3 poziomów FPN) i przypisz medianę szerokości oraz wysokości `(w, h)` z każdego przedziału jako kotwicę danego poziomu. Metoda ta jest stabilniejsza na małych zbiorach danych niż uruchamianie K-Means z małym $K$.
- Wymiary kotwicy nie mogą być ujemne; dolna granica to 1 piksel.
- Jeśli zbiór danych zawiera poniżej 200 ramek, wyświetl ostrzeżenie, że wyznaczanie kotwic jest statystycznie niewiarygodne, i zaleć skorzystanie z domyślnych wymiarów COCO wraz z pozyskaniem większej liczby danych treningowych.
