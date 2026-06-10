# Prawa skalowania

> Artykuł Kaplana z 2020 r. głosił: większy model, mniejsze straty. Artykuł Hoffmanna z 2022 r. odpowiedział: Twój model był niedostatecznie wytrenowany. Budżet obliczeniowy dzieli się na dwa elementy — parametry i tokeny — a proporcja między nimi nie jest oczywista.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

Dysponując budżetem C FLOP na trening, chcesz uzyskać jak najlepszy model. Do dyspozycji masz dwa regulatory:

1. **Ile parametrów (N)?** Większy model oznacza wyższą wydajność.
2. **Ile tokenów treningowych (D)?** Więcej danych pozwala lepiej wykorzystać pojemność modelu.

Liczba FLOPów skaluje się w przybliżeniu jako `6 × N × D`. Możesz zwiększać N kosztem D albo odwrotnie. Co jest korzystniejsze?

Przed rokiem 2022 odpowiedź brzmiała: „zdecydowanie zwiększaj N". GPT-3 (2020) miał 175 miliardów parametrów i był trenowany na około 300 miliardach tokenów — stosunek wynoszący około 1,7 tokena na parametr. Potwierdzały to prawa skalowania Kaplana.

Hoffmann i in. (2022), trenując rodzinę małych modeli o nazwie Chinchilla, odkryli coś zaskakującego: optymalny stosunek jest bliższy **20 tokenów na parametr**. GPT-3 był dziesięciokrotnie niedotrenowany. Chinchilla (70B parametrów, 1,4T tokenów) przewyższa GPT-3 (175B parametrów, 300B tokenów) na wszystkich testach porównawczych, generując przy tym 2,5 razy niższe koszty wnioskowania.

Rok 2026 to era Chinchilli — z jednym istotnym zastrzeżeniem. Llama 3 8B była trenowana na 15 bilionach tokenów, co daje stosunek 1875 tokenów na parametr. To dziewięćdziesiąt cztery razy więcej niż wynikałoby z optymalnej dla Chinchilli. W przypadku modeli wdrażanych na dużą skalę koszt wnioskowania przeważa nad kosztem treningu. Dlatego w 2026 r. standardowym podejściem jest nadmierne trenowanie — powyżej progu Chinchilli — w celu uzyskania mniejszego modelu nadającego się do efektywnego wdrożenia.

## Koncepcja

![Krzywe Chinchilli: strata vs. obliczenia przy różnych współczynnikach N/D](../assets/scaling-laws.svg)

### Prawo Hoffmanna

Z artykułu Chinchilla funkcja straty ma postać:

```
L(N, D) = A / N^α + B / D^β + E
```

- `N` = liczba parametrów (bez warstwy osadzania).
- `D` = liczba tokenów treningowych.
- `α ≈ 0.34`, `β ≈ 0.28` (w przybliżeniu symetryczne).
- `E ≈ 1.69`, dolna granica nieredukowalnej straty.
- `A ≈ 406`, `B ≈ 411`.

Podczas skalowania oba człony równania rywalizują ze sobą. Wyznaczając pochodną względem `N` przy stałym budżecie obliczeniowym (C = 6ND) i rozwiązując równanie, otrzymujemy:

```
N_opt ≈ 0.6 × (C/6)^0.5
D_opt ≈ 0.6 × (C/6)^0.5
D_opt / N_opt ≈ 20
```

Optymalna proporcja obliczeniowa wynosi zatem 20 tokenów na parametr.

### Dlaczego warto przetrenowywać model

Optymalna dla Chinchilli proporcja minimalizuje stratę treningową na każdy FLOP przeznaczony na trening. Koszty treningu ponosi się jednak tylko raz, natomiast koszty wnioskowania narastają bezterminowo.

Weźmy chatbota obsługującego bilion tokenów miesięcznie — tam to właśnie wnioskowanie dominuje w całkowitym rachunku. Strategia Llamy polega na trenowaniu mniejszego modelu dłużej. Model 8B trenowany na 15T tokenów jest głęboko zoptymalizowany pod kątem wnioskowania:

- Mieści się w pamięci konsumenckich procesorów graficznych.
- Opóźnienie odpowiedzi stanowi ułamek tego, co oferuje model 70B optymalny dla Chinchilli.
- Jakość jest wystarczająca do większości zastosowań.

Artykuł DeepMind z 2024 r. („Przetrenowanie to nowy optymalny stan") formalizuje to podejście. W przypadku obciążeń zdominowanych przez wnioskowanie właściwy stosunek wynosi od 100 do 500 tokenów na parametr, zależnie od skali udostępniania.

### Emergencja a ciągłość

Zgodnie z jedną z hipotez pewne zdolności — arytmetyka, wieloetapowe rozumowanie, przestrzeganie łańcucha myślowego — „wyłaniają się" nagle po przekroczeniu określonej skali modelu.

Schaeffer i in. (2023) wykazali, że jest to artefakt metryki: popularne miary stosują nieciągłe systemy punktacji (dokładne dopasowanie, dokładność progową), które maskują płynną poprawę w podstawowych logitach. Metryki ciągłe, takie jak entropia krzyżowa, ujawniają gładkie krzywe wzrostu.

Konsensus na rok 2026 jest następujący: prognozy oparte na ciągłych stratach są wiarygodne. Skoki widoczne w wynikach testów porównawczych są najczęściej artefaktami wynikającymi z doboru metryk. Budżety należy planować na podstawie wskaźników ciągłych.

### Stan wiedzy w 2026 r.

Prawa skalowania pozostają aktualne, choć krajobraz uległ zmianie:

| Czynnik | Zmiana |
|------------|------------|
| Jakość danych | Staranne dobieranie „wartościowych" tokenów (w stylu Phi) przesuwa krzywe o ponad 2× efektywnych obliczeń |
| MoE | Łączna liczba parametrów oddziela się od aktywnych FLOPów; prawa skalowania działają w odniesieniu do aktywnych FLOPów |
| Dostrajanie | Niektóre możliwości — przestrzeganie instrukcji, generowanie kodu — zmieniają się pod wpływem SFT+RLHF w stopniu większym niż w trakcie wstępnego treningu |
| Multimodalność | Tokeny obrazu i tekstu skalują się łącznie; osobne krzywe dla każdej modalności |
| Dane syntetyczne | Modele generują własne dane treningowe; efektywne obliczenia mogą się składać |

Optymalizator Muon (Kimi Moonlight, 2024) wykazał około dwukrotny wzrost efektywnej mocy obliczeniowej w porównaniu z AdamW przy tych samych danych. Część przebiegów treningowych z 2026 r. domyślnie korzysta z Muon. Zmienia on stałe bezwzględne w prawie skalowania, nie wpływając na jego kształt.

## Zbuduj to

Patrz `code/main.py`. Implementujemy równanie straty Chinchilli i szukamy optymalnego `(N, D)` dla kilku wybranych budżetów obliczeniowych.

### Krok 1: Funkcja straty Chinchilli

```python
def chinchilla_loss(N, D, A=406.4, B=410.7, alpha=0.34, beta=0.28, E=1.69):
    return A / N ** alpha + B / D ** beta + E
```

Narysuj `L` jako mapę konturową nad `(N, D)` przy ustalonym `C = 6ND`. Znajdź minimum.

### Krok 2: Granica optymalności obliczeniowej

Dla budżetów obliczeniowych od `1e17` do `1e25` FLOPów znajdź `(N, D)` minimalizujące stratę przy ograniczeniu `6ND = C`. Zweryfikuj, czy współczynnik `D/N ≈ 20`.

### Krok 3: Koszt przetrenowania

Oblicz dodatkową stratę ponoszoną przy trenowaniu modelu 10× mniejszego (1/10 optymalnego N, 10× optymalnego D). Określ uzyskane oszczędności w FLOPach wnioskowania (proporcjonalne do N).

### Krok 4: Porównanie z rzeczywistymi modelami

Nanieś znane pary `(N, D)` dla GPT-3, Chinchilla, Llama 3 8B i DeepSeek-V3 (aktywne parametry), a następnie porównaj przewidywaną stratę ze zgłoszoną.

## Zastosowanie praktyczne

Trenowanie modelu granicznego na własną rękę jest mało prawdopodobne. Prawa skalowania są jednak przydatne w codziennej pracy:

1. **Czy Twoje dostrajanie ma wystarczającą ilość danych.** Jeśli dane specyficzne dla zadania obejmują mniej niż 20 tokenów na parametr modelu bazowego, spodziewaj się nasycenia przy określonym minimalnym poziomie straty.
2. **Czy wybrać większy model bazowy.** Jeśli cały budżet pochłania wnioskowanie, wybierz mniejszy model wymagający dłuższego treningu.
3. **Gdzie zyski maleją.** Powyżej 1000× optymalnej dla Chinchilli zmiany logarytmicznej straty stają się szumem pomiarowym.

**Kierunki badań w 2026 r.:**

- **Reżim ograniczonych danych.** Sieć zawiera skończoną liczbę wysokiej jakości tokenów (~5–10 bilionów angielskich po filtrowaniu). Wstępne trenowanie modeli granicznych zbliża się do tego pułapu. Kolejnymi dźwigniami wzrostu są dane syntetyczne, wielojęzyczne, wielomodalne oraz dostrajanie w skali RLHF.
- **Mnożniki obliczeniowe.** Optymalizator Muon, MoE, lepsza selekcja danych — każdy z tych czynników przesuwa stałe bezwzględne, nie zmieniając asymptoty prawa skalowania.
- **Prawa skalowania dla uczenia przez wzmacnianie.** Pytanie pozostaje otwarte. Wczesne dowody wskazują na prawo potęgowe w próbkach RL, lecz z wykładnikami znacznie różniącymi się od tych w treningu wstępnym.

## Wyślij to

Patrz `outputs/skill-training-budget-estimator.md`. Narzędzie dobiera `(N, D, hours, GPU)` dla nowego przebiegu treningowego na podstawie budżetu obliczeniowego, ograniczeń wdrożeniowych i docelowej straty.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Wyświetl `(N, D)` optymalne dla Chinchilli dla budżetów `1e20`, `1e22`, `1e24`. Porównaj wyniki z tabelą rzeczywistych modeli.
2. **Średnie.** Zaimplementuj krzywą straty Hoffmanna jako funkcję budżetu obliczeniowego. Wykreśl stratę w zależności od `log10(C)` wzdłuż granicy optymalnej. Ustal, kiedy prawo przewiduje potrzebę przekroczenia `10^28` FLOPów, aby uzyskać kolejne zmniejszenie entropii krzyżowej o 0,1.
3. **Trudne.** Dopasuj własne prawo skalowania do 5 małych modeli (od 100 tys. do 10M parametrów) wytrenowanych na tym samym zbiorze danych. Oszacuj `α` i `E`. Jak dobrze Twoje wykładniki pokrywają się z opublikowanymi wartościami?

## Kluczowe terminy

| Termin | Potoczne rozumienie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Parametry (N) | „Rozmiar modelu" | Liczba wag z pominięciem warstwy osadzania; określa pojemność modelu. |
| Tokeny (D) | „Dane treningowe" | Liczba tokenów obserwowanych podczas treningu; decyduje o stopniu wykorzystania pojemności. |
| Obliczenia (C) | „Wydane FLOPy" | Około `6 × N × D` dla standardowego transformatora. |
| Optymalność Chinchilli | „D/N ≈ 20" | Stosunek minimalizujący stratę na FLOP wstępnego treningu. |
| Przetrenowanie | „Powyżej Chinchilli" | Poświęcenie dodatkowych FLOPów treningowych, by zaoszczędzić na FLOPach wnioskowania; D/N >> 20. |
| Nieredukowalna strata | „Podłoga" | Człon `E` w prawie skalowania; odpowiada entropii samych danych. |
| Emergencja zdolności | „Nagłe skoki w skali" | Często artefakt metryki; ciągła strata rośnie płynnie. |
| Efektywne obliczenia | „Mnożnik efektywności treningu" | Lepsze dane, optymalizator lub architektura zwielokrotniają zasięg budżetu FLOPów. |

## Dalsza lektura

- [Kaplan i in. (2020). Prawa skalowania dla modeli języka neuronowego](https://arxiv.org/abs/2001.08361) — pionierska praca o prawach skalowania; zakładała niedotrenowanie.
- [Hoffmann i in. (2022). Szkolenie obliczeniowo optymalnych dużych modeli językowych](https://arxiv.org/abs/2203.15556) — Chinchilla.
- [Schaeffer i in. (2023). Czy wyłaniające się zdolności dużych modeli językowych są mirażem?](https://arxiv.org/abs/2304.15004) — emergencja jako artefakt pomiarowy.
- [Sardana, Frankle (2024). Poza optymalną Chinchillą: uwzględnienie wnioskowania w prawach skalowania modeli językowych](https://arxiv.org/abs/2401.00448) — uzasadnienie przetrenowania Llamy pod kątem typowego obciążenia.
- [Jordan i in. (2024). Muon: Optymalizator warstw ukrytych w sieciach neuronowych](https://kellerjordan.github.io/posts/muon/) — dwukrotny mnożnik obliczeniowy.
