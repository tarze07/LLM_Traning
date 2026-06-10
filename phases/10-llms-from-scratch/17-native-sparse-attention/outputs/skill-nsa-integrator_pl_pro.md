---

name: nsa-integrator
description: Plan integracji mechanizmu Native Sparse Attention w procesie pre-trainingu na długich kontekstach
version: 1.0.0
phase: 10
lesson: 17
tags: [nsa, sparse-attention, long-context, pre-training, kernel-aligned, deepseek]

---

Na podstawie parametrów pre-trainingu na długich kontekstach (docelowy kontekst, architektura bazowa, dostępny wolumen tokenów treningowych, topologia GPU, cel wdrożenia), stwórz plan integracji mechanizmu NSA (Native Sparse Attention).

Zwróć:

1. **Rozmiar bloku kompresji l**: Wybierz spośród 32, 64 lub 128. Dobierz wartość do docelowego kontekstu: $l = 32$ dla 16k–32k tokenów, $l = 64$ dla 64k–128k, $l = 128$ dla $\ge$ 256k. Większa wartość $l$ redukuje liczbę skompresowanych kluczy, lecz generuje mniej precyzyjny (zgrubny) sygnał routingu.
2. **Liczbę k-najbliższych sąsiadów (top-k)**: Wybierz wartość z zakresu od 8 do 32 (domyślna wartość w oryginalnej publikacji to 16). Uzasadnij wybór profilem zadań: zadania wymagające zaawansowanego logicznego rozumowania (matematyka, kodowanie) wymagają wyższej wartości $k$ ze względu na potrzebę precyzyjnego wyboru bloków; zadania typu retrieval (wyszukiwanie informacji) efektywnie działają przy niższym $k$.
3. **Szerokość okna przesuwnego (sliding window) W**: Wybierz spośród 256, 512 lub 1024 (domyślnie 512). Krótsze okno zaleca się dla danych o wysokiej strukturze (np. kod źródłowy), gdzie kluczowy jest kontekst lokalny; dłuższe okno dla tekstów pisanych prozą.
4. **Bramkowanie MLP (MLP gate)**: Określ strukturę i inicjalizację warstwy bramkującej. Domyślnie: warstwa liniowa mapująca z wymiaru `hidden` do 3 (reprezentujących gałęzie atencji), z aktywacją `sigmoid` lub `softplus`. Zwróć uwagę, jeśli wagi bramki zaczną drastycznie faworyzować tylko jedną z gałęzi – oznacza to błędne dostrojenie parametrów $l$, $k$ lub $W$.
5. **Dostępność dedykowanych kerneli**: Potwierdź dostępność kerneli Triton lub CUDA dla docelowego akceleratora. Odrzuć pomysł wycofywania się (fallback) do standardowej atencji (dense attention) podczas wnioskowania (celem NSA jest redukcja kosztów obliczeniowych fazy decode). Jeśli dostępne są jedynie kernele dla przejścia w przód (forward pass), a brak kerneli dla przejścia wstecznego (backward pass) – odradź realizację pre-trainingu od zera i zalecaj kontynuację treningu (continual pre-training) na istniejących punktach kontrolnych z gęstą atencją.

Zasady bezwzględnego odrzucenia (red flags):
- Stosowanie NSA na modelu wcześniej wytrenowanym ze standardową gęstą atencją (dense attention) bez przeprowadzenia fazy kontynuacji pre-trainingu. Metdy tej nie da się wdrożyć wyłącznie na etapie wnioskowania.
- Docelowy kontekst o długości poniżej 16k tokenów. W tym zakresie narzut obliczeniowy trójgałęziowej struktury atencji przewyższa zyski ze rzadkości (sparsity).
- Wdrożenia produkcyjne oparte na wnioskowaniu na stosach technologicznych pozbawionych dedykowanych kerneli dla NSA. W takich przypadkach zaleca się stosowanie MLA lub atencji z oknem przesuwnym (Sliding Window Attention).

Kryteria odmowy zatwierdzenia:
- Jeśli brak jest zdefiniowanych zbiorów testowych dla długiego kontekstu (np. RULER, LongBench, Needle In A Haystack) – odrzuć plan i zażądaj dostarczenia danych kalibracyjnych.
- Jeśli w zbiorze treningowym dominują krótkie sekwencje – odrzuć plan i zalecaj zmianę wag danych treningowych (data re-weighting) przed wdrożeniem NSA.
- Jeśli docelowy akcelerator GPU jest starszy niż NVIDIA A100 – odrzuć projekt (zyski wydajnościowe z kerneli NSA opierają się na architekturze pamięci układów klasy H100/H200/MI300).

Rezultat: jednostronicowa specyfikacja zawierająca wartości $l$, $k$, $W$, konfigurację warstwy bramkującej, wskazanie ścieżki do kerneli oraz szacowane oszczędności obliczeniowe. Zakończ dokument sekcją „Kryterium sukcesu”, podającą minimalny oczekiwany przyrost wyniku na benchmarkach RULER lub LongBench (różnica punktów procentowych w stosunku do modelu ze standardową gęstą atencją), który uzasadnia wdrożenie NSA. Uwzględnij również kryterium wycofania (fallback trigger) – próg metryki, poniżej którego należy przywrócić architekturę MLA lub standardowe GQA.
