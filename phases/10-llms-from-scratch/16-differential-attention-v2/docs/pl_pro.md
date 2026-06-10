# Uwaga różnicowa (V2)

> Uwaga Softmax rozprasza niewielką część prawdopodobieństwa na każdy nieistotny token. Przy ponad 100 tys. tokenów ten szum kumuluje się i tłumi sygnał. Differential Transformer (Ye i in., ICLR 2025) rozwiązuje ten problem, obliczając uwagę jako różnicę dwóch softmaxów i eliminując w ten sposób wspólny poziom szumów. DIFF V2 (Microsoft, styczeń 2026 r.) to przepisanie stosu produkcyjnego: wyrównanie opóźnienia dekodowania do podstawowego Transformera, rezygnacja z niestandardowych jąder CUDA oraz pełna zgodność z FlashAttention. Niniejsza lekcja stanowi kompletne omówienie przejścia od V1 do V2, wraz z działającą implementacją operacji różnicowej, którą można uruchomić w czystym Pythonie (stdlib).

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 02 (samouwaga), Faza 7 · 15 (warianty uwagi), Faza 10 · 14 (omówienie architektury)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnić dokładnie, dlaczego uwaga softmax generuje poziom szumów i dlaczego rośnie on wraz z długością kontekstu.
- Wyprowadzić wzór na uwagę różnicową i uzasadnić, w jaki sposób odejmowanie eliminuje wspólną składową szumu przy zachowaniu sygnału.
- Prześledzić różnice między wersjami V1 i V2: co przyspieszyło, co uproszczono, co zyskało na stabilności i dlaczego każda zmiana była niezbędna do przedtrenowania produkcyjnego.
- Zaimplementować uwagę różnicową od podstaw w czystym Pythonie i empirycznie zweryfikować właściwość redukcji szumów na syntetycznym zapytaniu typu sygnał plus szum.

## Problem

Standardowa uwaga softmax posiada właściwość matematyczną, która w dużej skali staje się poważnym problemem operacyjnym. Dla zapytania `q` wagi uwagi przyjmują postać `softmax(qK^T / sqrt(d))`. Softmax nie może wygenerować dokładnych zer — każdy nieistotny token otrzymuje pewną dodatnią wagę. Ta resztkowa masa to szum, który narasta wraz z długością kontekstu. Przy 128 tys. tokenów, nawet jeśli każdy nieistotny token ma jedynie 0,001% prawdopodobieństwa, łączny wkład 127 999 takich tokenów sięga około 12% całości. Model musi nauczyć się omijać rosnący wraz z kontekstem poziom szumów.

Empirycznie objawia się to jako zaburzenia uwagi: halucynacyjne cytaty w RAG przy długim kontekście, błędy „zagubienia w środku" w zadaniach wymagających przeszukiwania 100 tys. tokenów oraz stopniowe pogarszanie dokładności w testach typu „igła w stogu siana" powyżej 32 tys. W artykule o Differential Transformerze (arXiv:2410.05258, ICLR 2025) zmierzono wyraźne różnice: modele DIFF charakteryzują się niższą perpleksją, wyższą dokładnością przy długim kontekście i mniejszą skłonnością do halucynacji niż modele bazowe tej samej wielkości.

DIFF V1 miał trzy problemy uniemożliwiające jego zastosowanie w granicznych potokach przedtrenowania. Po pierwsze, pamięć podręczna wartości musiała być ładowana dwukrotnie na krok dekodowania. Po drugie, wymagał niestandardowych jąder CUDA, które łamały kompatybilność z FlashAttention. Po trzecie, RMSNorm stosowany na każdą głowicę destabilizował długoterminowe trenowanie w skalach powyżej 70B. DIFF V2 (blog Microsoft unilm, 20 stycznia 2026 r.) rozwiązuje wszystkie trzy problemy. W tej lekcji omówiono obie wersje, zbudowano operator różnicy i porównano redukcję szumów na syntetycznym przykładzie.

## Koncepcja

### Poziom szumów softmax

Dla zapytania `q` i kluczy `K = [k_1, ..., k_N]` wagi uwagi wynoszą:

```
w_i = exp(q . k_i / sqrt(d)) / sum_j exp(q . k_j / sqrt(d))
```

Żadne `w_i` nigdy nie wynosi zero. Gdy `k_i` jest całkowicie niezwiązany z `q`, iloczyn `q . k_i` nie jest równy 0 — oscyluje wokół zera z wariancją `||q||^2 / d`. Po normalizacji przez softmax każdy niezwiązany token nadal wnosi `O(1/N)` do sumy ważonej. Łączny wkład niezwiązanych tokenów wynosi `O((N-1)/N) = O(1)` — nie jest to pomijalnie mała wartość.

Model dąży do czegoś w rodzaju twardego top-k: wysokiej wagi na tokenach istotnych i niemal zerowej wagi na pozostałych. Softmax jest zbyt płynny, by bezpośrednio osiągnąć ten efekt.

### Pomysł różnicowy

Podziel projekcje Q i K każdej głowy na dwie połowy: Q = (Q_1, Q_2) i K = (K_1, K_2). Oblicz dwie mapy uwagi:

```
A_1 = softmax(Q_1 K_1^T / sqrt(d))
A_2 = softmax(Q_2 K_2^T / sqrt(d))
```

Wyjście:

```
DiffAttn = (A_1 - lambda * A_2) V
```

Odejmowanie niweluje rozkład szumów wspólny dla obu map. Jeśli obie mapy przypisują zbliżone wagi 127 tys. niezwiązanych tokenów — co zachodzi przy losowej inicjalizacji — wkłady te wzajemnie się znoszą. Sygnał, czyli duża waga na kilku faktycznie istotnych tokenach, zanika tylko wtedy, gdy pojawia się w obu mapach z jednakową siłą. Po wytrenowaniu modelu tak się nie dzieje.

`lambda` to skalar uczony na głowicę, sparametryzowany jako `lambda = exp(lambda_q1 dot lambda_k1) - exp(lambda_q2 dot lambda_k2) + lambda_init`. Może przyjmować wartości ujemne. Domyślna wartość `lambda_init` to mała liczba dodatnia, np. 0,8.

### Dlaczego mechanizm działa jako reduktor szumów

Wyobraź sobie dwa mikrofony nagrywające ten sam głos. Oba rejestrują mówcę i skorelowany z nim szum tła. Po odjęciu jednego sygnału od drugiego wspólny szum zanika, a głos pozostaje — ponieważ oba sygnały różnią się w fazie lub amplitudzie na tyle, by nie doszło do całkowitego wygaszenia. `lambda` uczony na głowicę wyznacza dokładnie tę równowagę.

### V1 kontra V2: kluczowe różnice

V1 utrzymywał liczbę parametrów na poziomie Transformera bazowego. Aby uzyskać dwa zestawy zapytań na głowicę, wymiar głowicy zmniejszono o połowę. Kosztowało to ekspresyjność głowicy, a co bardziej dotkliwe — zmniejszyło o połowę bufor wartości na głowicę. Dekodowanie wymagało dwukrotnego załadowania pamięci podręcznej wartości na krok (po jednym razie na każdą gałąź softmax). Efektem było wolniejsze dekodowanie niż w modelu bazowym, mimo porównywalnej liczby parametrów.

V2 podwaja liczbę głowic Q przy zachowaniu tej samej liczby głowic KV (pożyczając parametry z projekcji rozszerzającej). Wymiary głowic pozostają takie same jak w modelu bazowym. Po odjęciu dodatkowy wymiar jest rzutowany z powrotem, by dopasować bazową projekcję O_W Transformera. Trzy efekty pojawiają się jednocześnie:

1. Szybkość dekodowania dorównuje modelowi bazowemu (pamięć podręczna KV ładowana raz).
2. FlashAttention działa bez modyfikacji (bez niestandardowych jąder).
3. Intensywność arytmetyczna przy dekodowaniu wzrasta (więcej obliczeń na bajt ładowany z HBM).

V2 usuwa również RMSNorm stosowany na głowicę, który w V1 służył do stabilizacji odejmowania. W skalach przedtrenowania klasy 70B ta norma destabilizowała trening na późnych etapach. V2 zastępuje ją prostszym schematem inicjalizacji, gwarantującym stabilność treningu bez dodatkowego modułu.

### Kiedy stosować uwagę różnicową

| Scenariusz | Korzyści |
|---------|---------|
| RAG przy długim kontekście (64 tys.+) | Czystsze mapy uwagi, mniej halucynacyjnych cytowań |
| Testy typu „igła w stogu siana" | Wyraźny wzrost dokładności powyżej 32 tys. tokenów |
| Analiza porównawcza wielu dokumentów | Mniejsze zakłócenia między dokumentami |
| Uzupełnianie kodu w oknie 8k | Marginalne korzyści, nieuzasadniające zmiany architektury |
| Krótki czat (< 4k) | Wyniki praktycznie nieodróżnialne od modelu bazowego |

Korzyść rośnie wraz z długością kontekstu. Przy 4 tys. tokenów poziom szumów jest na tyle niski, że standardowa uwaga jest wystarczająca. Przy 128 tys. staje się odczuwalnym problemem.

### Powiązania z innymi rozwiązaniami z 2026 roku

| Funkcja | Kompatybilność z DIFF V2 |
|--------|--------------------------------------|
| GQA | Tak (V2 zwiększa liczbę głowic Q, nie KV) |
| MLA (DeepSeek) | Tak w zasadzie; nie opublikowano artykułu łączącego oba podejścia |
| MoE | Tak (uwaga jest niezależna od bloku MLP) |
| LINA | Tak (bez zmian) |
| YARN / skalowanie długiego kontekstu | Tak (dokładnie tam, gdzie DIFF przynosi największe korzyści) |
| FlashAttention | Tak w V2 (w V1 — nie) |
| Spekulatywne dekodowanie | Tak (zmiana w warstwie uwagi jest niewidoczna dla pętli spec-decode) |

## Implementacja

`code/main.py` implementuje uwagę różnicową w czystym Pythonie. Syntetyczne zapytanie o znanej strukturze sygnał plus szum pozwala bezpośrednio zmierzyć współczynnik redukcji szumów.

### Krok 1: Standardowa uwaga softmax

Operacje macierzowe w stdlib: listy list, ręczne mnożenie macierzy, softmax z odejmowaniem maksimum dla stabilności numerycznej.

```python
def softmax(row):
    m = max(row)
    exps = [math.exp(x - m) for x in row]
    s = sum(exps)
    return [e / s for e in exps]
```

### Krok 2: Podział Q i K na dwie połowy

Podejście V1: zmniejszenie wymiaru głowicy o połowę. Podejście V2: zachowanie wymiaru głowicy i podwojenie liczby głowic. Implementacja demonstracyjna korzysta z wariantu V1 dla przejrzystości — matematyka jest identyczna, różni się jedynie sposób zarządzania wymiarami.

### Krok 3: Dwie gałęzie softmax i odejmowanie

```python
A1 = [softmax([dot(q1, k) / scale for k in K1]) for q1 in Q1]
A2 = [softmax([dot(q2, k) / scale for k in K2]) for q2 in Q2]
diff_weights = [[a1 - lam * a2 for a1, a2 in zip(r1, r2)] for r1, r2 in zip(A1, A2)]
out = [[sum(w * v[j] for w, v in zip(row, V)) for j in range(d_v)] for row in diff_weights]
```

Uwaga: wagi wyjściowe mogą być ujemne. Jest to poprawne — pamięć podręczna wartości obsługuje wkłady ze znakiem. Kolejna projekcja V pochłania ten znak.

### Krok 4: Pomiar redukcji szumów

Zbuduj syntetyczną sekwencję o długości 1024. Umieść token sygnału w znane miejsce, resztę wypełnij szumem. Oblicz (a) standardową wagę uwagi softmax na pozycji sygnału oraz (b) wagę uwagi różnicowej. Wyznacz stosunek sygnału do szumu dla obu przypadków. Uwaga DIFF konsekwentnie osiąga 3 do 10 razy wyższy stosunek sygnału do szumu, w zależności od tego, w jakim stopniu obie gałęzie zostały wytrenowane do eksponowania różnicy.

### Krok 5: Analiza parametrów V1 i V2

Dla konfiguracji (hidden=4096, heads=32, d_head=128) wydrukuj:

- Transformer bazowy: Q, K, V każdy o rozmiarze `hidden * hidden`, MLP o rozmiarze 4 * hidden.
- DIFF V1: Q, K każdy o rozmiarze `hidden * hidden`, V bez zmian (`hidden * hidden`), wymiar głowicy zmniejszony wewnętrznie o połowę. Dodatkowe parametry `lambda` na głowicę (O(heads * d_head)).
- DIFF V2: Q o rozmiarze `2 * hidden * hidden`, K i V bez zmian. Dodatkowa projekcja zmniejszająca przed O_W. Te same parametry `lambda` co w V1.

Implementacja mierzy koszt dodatkowych parametrów w V2 (w przybliżeniu `hidden * hidden` na blok uwagi) i wypisuje wynik.

## Zastosowania praktyczne

Od kwietnia 2026 r. DIFF V2 nie jest jeszcze dostępny na wszystkich produkcyjnych serwerach wnioskowania, jednak integracja z vLLM i SGLang jest w toku. W tym czasie wzorzec pojawia się w:

- Wewnętrznych modelach produkcyjnych Microsoft przeznaczonych do długiego kontekstu.
- Replikacjach badawczych w kilku otwartych przebiegach treningowych, celujących w konteksty powyżej 256 tys. tokenów.
- Architekturach hybrydowych łączących uwagę DIFF z uwagą przesuwanego okna na naprzemiennych warstwach.

Kiedy warto po to sięgnąć:

- Trenowanie nowego modelu od podstaw z efektywnym kontekstem powyżej 64 tys. tokenów. Uwagę różnicową należy wprowadzić od początku — późniejsze dostrajanie jest kosztowne.
- Dostrajanie modelu długokontekstowego, w którym w ewaluacji dominują błędy zagubienia w środku. LoRA na projekcjach Q może przybliżyć strukturę DIFF.

Kiedy nie warto:

- Gdy dysponujesz wstępnie wytrenowanym modelem gęstym o stabilnej wydajności przy długim kontekście. Koszt przekwalifikowania rzadko zwraca się przy istniejących wagach.
- Gdy kontekst zawsze mieści się poniżej 16 tys. tokenów. Poziom szumów jest wówczas pomijalny.

## Wyjście lekcji

Lekcja generuje `outputs/skill-diff-attention-integrator.md`. Na podstawie architektury modelu, docelowej długości kontekstu, profilu halucynacji i budżetu treningowego tworzy plan integracji uwagi różnicowej — zarówno dla nowego przebiegu przedtrenowania, jak i dla dostrajania LoRA.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź, czy stosunek sygnału do szumu dla uwagi różnicowej jest wyższy niż dla standardowej uwagi softmax na syntetycznym zapytaniu. Zmieniaj amplitudę szumu i wyznacz punkt, w którym standardowa uwaga przestaje być użyteczna.

2. Oblicz zmianę liczby parametrów w stosunku do modelu bazowego — osobno dla DIFF V1 i DIFF V2 — dla modelu klasy 7B (hidden=4096, heads=32, d_head=128, 32 warstwy). Wskaż, które składniki zyskały parametry, a które pozostały bez zmian.

3. Przeczytaj sekcję 3 artykułu DIFF V1 (arXiv:2410.05258) oraz sekcję 2 wpisu na blogu Hugging Face poświęconego DIFF V2. W dwóch zdaniach wyjaśnij, dlaczego RMSNorm na głowicę był konieczny w V1 i dlaczego V2 mógł go usunąć bez ryzyka rozbieżności treningu.

4. Przeprowadź ablację: oblicz uwagę różnicową dla `lambda = 0` (czysty pierwszy softmax) i `lambda = 1` (pełne odejmowanie). Na syntetycznym zapytaniu zmierz, jak stosunek sygnału do szumu zmienia się w całym zakresie. Wyznacz wartość `lambda` maksymalizującą ten stosunek.

5. Rozszerz implementację o GQA + DIFF V2. Przyjmij 8 głowic KV i 32 głowice Q. Wykaż, że rozmiar pamięci podręcznej KV odpowiada modelowi bazowemu GQA o tej samej konfiguracji (8 głowic KV, 32 głowice Q).

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|----------------|--------------------------------------|
| Uwaga różnicowa | „Dwa softmaxy odjęte od siebie" | Podział Q i K na dwie połowy, obliczenie dwóch map softmax, odjęcie drugiej (przeskalowanej przez lambda) od pierwszej, mnożenie przez V |
| Poziom szumów | „Niezerowy ogon softmaxu" | Wagi O(1/N) przypisywane przez softmax każdemu niezwiązanemu tokenowi, kumulujące się do O(1) przy długich kontekstach |
| lambda | „Skala odejmowania" | Skalar uczony na głowicę, sparametryzowany jako `exp(lq1.lk1) - exp(lq2.lk2) + lambda_init`; może być ujemny |
| DIFF V1 | „Wersja z ICLR 2025" | Oryginalny Differential Transformer; zmniejsza wymiar głowicy o połowę, by zachować liczbę parametrów; wymaga niestandardowego jądra; wolniejsze dekodowanie |
| DIFF V2 | „Poprawka ze stycznia 2026 r." | Podwaja głowice Q przy zachowaniu głowic KV; wyrównuje szybkość dekodowania do modelu bazowego i współpracuje z FlashAttention |
| RMSNorm na głowicę | „Stabilizator V1" | Dodatkowa norma stosowana po odjęciu w V1; usunięta w V2, by zapobiec niestabilności na późnych etapach treningu |
| Stosunek sygnału do szumu | „Ile uwagi jest marnowane" | Stosunek wagi na pozycji rzeczywistego sygnału do średniej wagi na pozycjach niezwiązanych |
| Zagubienie w środku | „Tryb awarii przy długim kontekście" | Zjawisko empiryczne polegające na spadku dokładności wyszukiwania w środkowej części długiego kontekstu — uwaga DIFF je ogranicza |
| Intensywność arytmetyczna | „FLOPy na bajt" | Współczynnik zwiększony w V2 przy dekodowaniu przez podwojenie liczby zapytań przypadających na jedno ładowanie KV; istotny dla dekodowania ograniczonego przepustowością pamięci |

## Dalsza literatura

- [Ye i in. — Differential Transformer (arXiv:2410.05258, ICLR 2025)](https://arxiv.org/abs/2410.05258) — oryginalna praca; teoria redukcji szumów i ablacje przy długim kontekście
- [Microsoft unilm — Differential Transformer V2 (blog Hugging Face, styczeń 2026 r.)](https://huggingface.co/blog/microsoft/diff-attn-v2) — przepisanie stosu produkcyjnego; wyrównanie szybkości dekodowania; zgodność z FlashAttention
- [Understanding Differential Transformer Unchains Pretrained Self-Attentions (arXiv:2505.16333)](https://arxiv.org/abs/2505.16333) — analiza teoretyczna wyjaśniająca, dlaczego odejmowanie przywraca wstępnie wytrenowaną strukturę uwagi
- [Shared DIFF Transformer (arXiv:2501.17900)](https://arxiv.org/html/2501.17900) — wariant z współdzieleniem parametrów
- [Vaswani i in. — Attention Is All You Need (arXiv:1706.03762)](https://arxiv.org/abs/1706.03762) — bazowy Transformer, od którego DIFF odejmuje
- [Liu i in. — Lost in the Middle (arXiv:2307.03172)](https://arxiv.org/abs/2307.03172) — test porównawczy przy długim kontekście, który uwaga DIFF adresuje
