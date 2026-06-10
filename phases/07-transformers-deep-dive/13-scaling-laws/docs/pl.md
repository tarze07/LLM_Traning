# Prawa skalowania

> W artykule Kaplana z 2020 r. napisano: większy model, mniejsze straty. W artykule Hoffmanna z 2022 r. napisano: byłeś niedostatecznie przeszkolony. Obliczenia dzielą się na dwa segmenty — parametry i tokeny — a podział nie jest oczywisty.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

Kiedy masz C FLOP obliczeń treningowych i chcesz najlepszego modelu, masz do czynienia z dwoma pokrętłami:

1. **Ile parametrów (N)?** Większy model, większa wydajność.
2. **Ile tokenów szkoleniowych (D)?** Więcej danych, lepsze wykorzystanie pojemności.

FLOPy skalują się w przybliżeniu jako `6 × N × D`. Możesz naciskać N w górę i D w dół lub D w górę i N w dół. Co jest lepsze?

Przed 2022 r. odpowiedzią było „mocne naciskanie N”. GPT-3 (2020) miał 175B wytrenowanych parametrów na tokenach ~300B. Stosunek około 1,7 tokenów na parametr. Potwierdziły to prawa skalowania Kaplana.

Hoffmann i in. (2022), trenując małą rodzinę modeli o nazwie Chinchilla, odkryli coś innego: optymalny stosunek jest bliższy **20 tokenów na parametr**. GPT-3 był 10 razy niedotrenowany. Szynszyla (parametry 70B, tokeny 1,4T) pokonuje GPT-3 (tokeny 175B, 300B) w każdym benchmarku przy 2,5 razy mniejszym koszcie wnioskowania.

Rok 2026 to świat szynszyli – z jednym ważnym zwrotem akcji. Lama 3 8B została przeszkolona na 15 bilionach tokenów, co daje stosunek 1875 tokenów na parametr. Dziewięćdziesiąt cztery razy więcej niż optymalnie dla szynszyli. Koszt wnioskowania ma większe znaczenie niż koszt szkolenia w przypadku modeli, które będą używane na dużą skalę, dlatego w roku 2026 domyślnym ustawieniem jest nadmierne szkolenie (powyżej Chinszyli) w celu uzyskania mniejszego zasięgu, który można wdrożyć.

## Koncepcja

![Krzywe szynszyli: strata vs obliczenia przy różnych współczynnikach N/D](../assets/scaling-laws.svg)

### Prawo Hoffmanna

Z artykułu Chinchilla strata jest następująca:

```
L(N, D) = A / N^α + B / D^β + E
```

- `N` = parametry (bez osadzania).
- `D` = tokeny szkoleniowe.
- `α ≈ 0.34`, `β ≈ 0.28` (w przybliżeniu symetryczny).
- `E ≈ 1.69`, pułap nieredukowalnej straty.
- `A ≈ 406`, `B ≈ 411`.

W miarę skalowania dwa terminy są ze sobą sprzeczne. Weź pochodną w.r.t. `N` przy stałych obliczeniach (C = 6ND) i rozwiąż:

```
N_opt ≈ 0.6 × (C/6)^0.5
D_opt ≈ 0.6 × (C/6)^0.5
D_opt / N_opt ≈ 20
```

Obliczenia optymalne: 20 tokenów na parametr.

### W każdym razie po co przetrenowywać

Optymalna dla szynszyli minimalizuje straty treningowe na FLOP treningowy. Ale płacisz koszty szkolenia raz; koszt wnioskowania na zawsze.

W przypadku chatbota, który obsługuje bilion tokenów miesięcznie, całkowity koszt dominuje wnioskowanie. Podejście Lamy: trenuj mniej, dłużej. Tokeny 8B przy 15T są głęboko zoptymalizowane pod kątem wnioskowania:

- Pasuje do konsumenckich procesorów graficznych.
- Opóźnienie to ułamek 70B optymalne dla szynszyli.
- Jakość jest wystarczająca do większości zadań.

W artykule DeepMind z 2024 r. („Przetrenowanie to nowy optymalny stan”) sformalizowano tę kwestię. W przypadku obciążeń zdominowanych przez wnioskowanie właściwy stosunek jest bliższy 100–500 tokenów na parametr, w zależności od objętości udostępniania.

### Wyłanianie się a gładkość

Twierdzenie: pewne zdolności (arytmetyka, rozumowanie wieloetapowe, podążanie za łańcuchem myślowym) „wyłaniają się” nagle w pewnej skali.

Schaeffer i in. (2023) argumentowali, że jest to artefakt pomiaru: nowe metryki wykorzystują nieciągłą punktację (dokładne dopasowanie, dokładność na poziomie progowym), która ukrywa płynną poprawę podstawowych logitów. Metryki ciągłe (entropia krzyżowa) pokazują gładkie krzywe.

Konsensus na rok 2026 jest następujący: prognozy oparte na ciągłych stratach są wiarygodne. Skoki do benchmarków są często artefaktami strzelców. Planuj budżety na podstawie wskaźników ciągłych.

### Zdjęcie z 2026 r

Przepisy dotyczące skalowania nadal działają, ale:

| Czynnik | Zmieniono sposób |
|------------|------------|
| Jakość danych | Opieka nad „dobrymi” tokenami (w stylu Phi) przesuwa krzywe o >2× efektywne obliczenia |
| Ministerstwo Środowiska | Całkowite parametry oddzielają się od aktywnych FLOPów; prawa skalowania na-aktywny-FLOP |
| Po szkoleniu | Niektóre możliwości (przestrzeganie instrukcji, kod) zmieniają się w przypadku SFT+RLHF w stopniu większym niż wstępne szkolenie |
| Multimodalność | Tokeny obrazu i tekstu skalują się razem; oddzielne krzywe dla każdej modalności |
| Dane syntetyczne | Modele generują dane szkoleniowe; efektywne obliczenia mogą składać |

Optymalizator Muon (Kimi Moonlight, 2024) wykazał ~2× przyrost efektywnej mocy obliczeniowej w porównaniu z AdamW przy dopasowanych danych. Niektóre przebiegi szkoleniowe z roku 2026 domyślnie korzystają z Muon. Zmienia stałą bezwzględną w prawie skalowania, a nie jej kształt.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy równanie straty szynszyli i szukamy optymalnego `(N, D)` obliczeń dla każdego z kilku budżetów obliczeniowych.

### Krok 1: Utrata szynszyli

```python
def chinchilla_loss(N, D, A=406.4, B=410.7, alpha=0.34, beta=0.28, E=1.69):
    return A / N ** alpha + B / D ** beta + E
```

Narysuj `L` jako kontur nad `(N, D)` w ustalonym `C = 6ND`. Znajdź minimum.

### Krok 2: granica optymalna obliczeniowo

W przypadku budżetów obliczeniowych od `1e17` do `1e25` FLOPów znajdź `(N, D)`, które minimalizują stratę z zastrzeżeniem `6ND = C`. Sprawdź współczynnik `D/N ≈ 20`.

### Krok 3: koszt przeszkolenia

Oblicz dodatkową stratę, jaką płacisz za wytrenowanie 10× mniejszego modelu (1/10 optymalnego N, 10× optymalnego D). Podaje wnioski dotyczące oszczędności FLOP (proporcjonalne do N) w zamian.

### Krok 4: porównaj z prawdziwymi modelami

Wrzuć znane pary `(N, D)` dla GPT-3, Chinchilla, Lama 3 8B, DeepSeek-V3 (aktywne parametry) i porównaj przewidywaną i zgłoszoną stratę.

## Użyj tego

Jest mało prawdopodobne, że sam będziesz trenował model z pogranicza. Ale prawa skalowania mówią:

1. **Czy Twoje dostrojenie ma wystarczającą ilość danych.** Jeśli Twoje dane specyficzne dla zadania są poniżej 20 tokenów na parametr modelu podstawowego, spodziewaj się nasycenia przy pewnym minimalnym poziomie strat.
2. **Czy wybrać większy model podstawowy.** Jeśli wydajesz cały budżet na wnioskowanie, wybierz mniejszy model, który wymaga dłuższego treningu.
3. **Tam, gdzie zyski maleją.** Powyżej 1000× optymalnej dla szynszyli zmiany utraty logarytmicznej stają się szumem.

**Trajektoria badań w 2026 roku:**

- **Reżim ograniczonych danych.** Sieć zawiera skończoną liczbę tokenów wysokiej jakości (~5–10 bilionów angielskich po filtrowaniu). Wstępne szkolenie graniczne zbliża się do tego pułapu. Kolejnymi dźwigniami są dane syntetyczne, wielojęzyczne, wielomodalne i dostrajanie w skali RLHF.
- **Sztuczki z mnożnikami obliczeniowymi.** Optymalizator mionów, MoE, lepsza selekcja danych — każde przesuwa stałe bezwzględne, a nie asymptotę.
- **Przepisy dotyczące skalowania dla RL.** Pytanie otwarte. Wczesne dowody sugerują prawo potęgowe w próbkach RL, ale z bardzo różnymi wykładnikami niż w przypadku treningu wstępnego.

## Wyślij to

Zobacz `outputs/skill-training-budget-estimator.md`. Umiejętność wybiera `(N, D, hours, GPU)` dla nowego przebiegu szkolenia, biorąc pod uwagę budżet obliczeniowy, ograniczenia wdrożenia i utratę celów.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Drukuj `(N, D)` optymalne dla szynszyli dla budżetów obliczeniowych `1e20`, `1e22`, `1e24`. Porównaj z tabelą rzeczywistych modeli.
2. **Średni.** Zaimplementuj krzywą straty Hoffmanna jako funkcję obliczeniową. Strata wykresu a `log10(C)` dla granicy optymalnej obliczeń. Określ, kiedy prawo przewiduje, że będziemy potrzebować `>10^28` FLOPów, aby uzyskać następne zmniejszenie entropii krzyżowej o 0,1.
3. **Trudne.** Dopasuj własne prawo skalowania na 5 małych modelach (parametry od 100 tys. do 10M) wyszkolonych na tym samym zbiorze danych. Oszacuj `α` i `E`. Jak dobrze Twoje wykładniki odpowiadają opublikowanym?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Parametry (N) | „Rozmiar modelu” | Nie osadzający się licznik masy; określa pojemność. |
| Żetony (D) | „Dane treningowe” | Liczba zaobserwowanych żetonów szkoleniowych; określa, jak dobrze parametry zostaną wykorzystane. |
| Oblicz (C) | „Wydane FLOPy” | Około `6 × N × D` dla standardowego transformatora. |
| Szynszyla-optymalna | „D/N ≈ 20” | Współczynnik minimalizujący straty na FLOP treningu wstępnego. |
| Przetrenowanie | „Przeszłość szynszyli” | Poświęć dodatkowe szkolenia FLOP, aby zaoszczędzić FLOPy z wnioskowaniem; D/N >> 20. |
| Nieredukowalna strata | „Podłoga” | `E` termin w prawie skalowania; entropia samych danych. |
| Pojawiające się możliwości | „Nagłe skoki skali” | Często artefakt strzelca; ciągła strata jest gładka. |
| Efektywne obliczenia | „Mnożnik efektywności szkoleń” | Lepsze dane/optymalizator/architektura zwielokrotniają zasięg FLOP. |

## Dalsze czytanie

- [Kaplan i in. (2020). Prawa skalowania dla modeli języka neuronowego](https://arxiv.org/abs/2001.08361) — pierwszy artykuł dotyczący prawa dotyczącego skalowania; niedoszkolony.
- [Hoffmann i in. (2022). Szkolenie optymalnych obliczeniowo modeli dużych języków](https://arxiv.org/abs/2203.15556) — Chinchilla.
- [Schaeffer i in. (2023). Czy wyłaniające się zdolności dużych modeli językowych są mirażem?](https://arxiv.org/abs/2304.15004) — pojawienie się jako artefakt pomiarowy.
- [Sardana, Frankle (2024). Poza szynszylą optymalną: uwzględnienie wnioskowania w przepisach dotyczących skalowania modelu językowego](https://arxiv.org/abs/2401.00448) — dlaczego nadmierne szkolenie Lamy jest odpowiednie ze względu na jej obciążenie pracą.
- [Jordan i in. (2024). Muon: Optymalizator warstw ukrytych w sieciach neuronowych](https://kellerjordan.github.io/posts/muon/) — mnożnik obliczeniowy 2×.