# Uwaga różnicowa (V2)

> Uwaga Softmax rozkłada niewielką ilość prawdopodobieństwa na każdy niepasujący token. Ponad 100 tys. żetonów ten szum sumuje się i zagłusza sygnał. Transformator różnicowy (Ye i in., ICLR 2025) rozwiązuje ten problem, obliczając uwagę jako różnicę dwóch softmaxów i odejmując wspólny poziom szumów. DIFF V2 (Microsoft, styczeń 2026 r.) to przeróbka stosu produkcyjnego: dopasowanie opóźnienia dekodowania do podstawowego Transformera, brak niestandardowych jąder, zgodność z FlashAttention. Ta lekcja to kompleksowa lekcja od V1 do V2, z działającą zabawkową implementacją operacji różnicowej, którą można uruchomić w stdlib Python.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 02 (samouwaga), Faza 7 · 15 (warianty uwagi), Faza 10 · 14 (omówienie architektury)
**Czas:** ~60 minut

## Cele nauczania

- Określ dokładnie, dlaczego uwaga softmax ma poziom szumów i dlaczego rośnie wraz z długością kontekstu.
- Wyprowadź wzór na uwagę różnicową i wyjaśnij, dlaczego odejmowanie eliminuje wspólną składową szumu, zachowując jednocześnie sygnał.
- Przejdź przez różnicę między wersjami V1 i V2: co stało się szybsze, co prostsze, co stabilniejsze i dlaczego każda zmiana była konieczna do wstępnego szkolenia produkcyjnego.
- Zaimplementuj od podstaw uwagę różnicową w czystym Pythonie i empirycznie zweryfikuj właściwość eliminacji szumów w syntetycznym zapytaniu dotyczącym sygnału plus szumu.

## Problem

Standardowa uwaga softmax ma właściwość matematyczną, która na dużą skalę zamienia się w operacyjny ból głowy. W przypadku zapytania `q` wagi uwagi wynoszą `softmax(qK^T / sqrt(d))`. Softmax nigdy nie może wygenerować dokładnych zer — każdy niepasujący token otrzymuje pewną dodatnią masę. Ta masa resztkowa to szum, który skaluje się wraz z długością kontekstu. Przy 128 tys. tokenów, nawet jeśli każdy niepasujący token ma tylko 0,001% prawdopodobieństwa, 127 999 z nich łącznie stanowi około 12% całości. Model musi nauczyć się trasowania wokół poziomu szumów, który rośnie wraz z kontekstem.

Empirycznie objawia się to jako zakłócenia uwagi: halucynacyjne cytaty w RAG o długim kontekście, błędy zagubienia w środku w zadaniach odzyskiwania 100 tys. tokenów i subtelne pogorszenie dokładności w testach porównawczych „igła w stogu siana” powyżej 32 tys. W artykule na temat transformatora różnicowego (arXiv:2410.05258, ICLR 2025) zmierzono różnicę: transformatory DIFF charakteryzują się niższym poziomem zakłopotania, wyższą dokładnością w długim kontekście i mniejszą liczbą halucynacji niż linie bazowe tej samej wielkości.

DIFF V1 miał trzy problemy, które trzymały go z dala od granicznych rurociągów przedtreningowych. Jego pamięć podręczna wartości musiała być ładowana dwa razy na krok dekodowania, wymagała niestandardowych jąder CUDA, które łamały kompatybilność z FlashAttention, a jej RMSNorm na głowicę destabilizowało długoterminowe szkolenie w skali ponad 70B. DIFF V2 (blog Microsoft unilm, 20 stycznia 2026 r.) naprawił wszystkie trzy. W tej lekcji omówiono obie wersje, zbudowano operator różnicy i porównano eliminację szumów w zapytaniu dotyczącym zabawki.

## Koncepcja

### Poziom szumów softmax

Dla zapytania `q` i kluczy `K = [k_1, ..., k_N]` wagi uwagi wynoszą:

```
w_i = exp(q . k_i / sqrt(d)) / sum_j exp(q . k_j / sqrt(d))
```

Nie `w_i` nigdy nie wynosi zero. Jeśli `k_i` jest całkowicie niezwiązany z `q`, wynik `q . k_i` nie wynosi 0 — oscyluje wokół zera z wariancją `||q||^2 / d`. Po normalizacji Softmax każdy niepowiązany token nadal wnosi `O(1/N)` do sumy ważonej. Całkowity udział niepowiązanych tokenów wynosi `O((N-1)/N) = O(1)` — nie jest to mała ilość.

Model pragnie czegoś w rodzaju twardego top-k: dużej wagi na pasujących żetonach, niemal zerowej wagi wszędzie indziej. Softmax jest zbyt płynny, aby zrobić to bezpośrednio.

### Pomysł różnicowy

Podziel występy Q i K każdej głowy na dwa: Q = (Q_1, Q_2) i K = (K_1, K_2). Oblicz dwie mapy uwagi:

```
A_1 = softmax(Q_1 K_1^T / sqrt(d))
A_2 = softmax(Q_2 K_2^T / sqrt(d))
```

Dane wyjściowe:

```
DiffAttn = (A_1 - lambda * A_2) V
```

Odejmowanie anuluje rozkład szumów wspólny dla obu map. Jeśli obie mapy mają mniej więcej taką samą wagę na 127 tys. niepowiązanych ze sobą tokenów (co będzie miało miejsce przy losowej inicjalizacji), zostaną one anulowane. Sygnał — szczytowy ciężar na kilku faktycznie istotnych żetonach — zostaje anulowany tylko wtedy, gdy pojawia się na obu mapach z tą samą siłą, co nie nastąpi po przeszkoleniu modelu.

`lambda` to możliwy do nauczenia skalar na głowę, sparametryzowany jako `lambda = exp(lambda_q1 dot lambda_k1) - exp(lambda_q2 dot lambda_k2) + lambda_init`. Może być negatywny. `lambda_init` domyślnie przyjmuje małą liczbę dodatnią, np. 0,8.

### Dlaczego to pasuje do funkcji redukcji szumów

Pomyśl o dwóch hałaśliwych mikrofonach nagrywających ten sam głos. Obydwa wychwytują głośnik i skorelowany z nim szum tła. Odejmij jedno od drugiego, a wspólny szum zniknie. Głos przetrwa, ponieważ oba sygnały różnią się fazą lub amplitudą na tyle, aby zapobiec całkowitemu wygaśnięciu. `lambda` na głowę uczy się dokładnie tej równowagi.

### V1 kontra V2: różnica

V1 utrzymywał liczbę parametrów równą transformatorowi bazowemu. Aby uzyskać dwa zapytania na głowę, wymiar głowy zmniejszył się o połowę. Kosztowało to ekspresję głowy i – co było bardziej bolesne – zmniejszyło o połowę bufor wartości na głowę. Dekodowanie wymagało załadowania pamięci podręcznej wartości dwa razy na krok (raz na gałąź softmax). Wynik: dekodowanie jest wolniejsze niż w przypadku linii bazowej, pomimo pasującej liczby parametrów.

V2 podwaja liczbę głowic zapytań i utrzymuje te same głowice KV (pożyczając parametry z projekcji w górę). Wymiary głowy pozostają takie same jak w przypadku linii bazowej. Po odjęciu dodatkowy wymiar jest rzutowany z powrotem w dół, aby dopasować bazową projekcję O_W Transformera. Trzy rzeczy dzieją się jednocześnie:

1. Szybkość dekodowania odpowiada wartości bazowej (pamięć podręczna KV jest ładowana raz).
2. FlashAttention działa bez zmian (bez niestandardowego jądra).
3. Intensywność arytmetyczna przy dekodowaniu wzrasta (więcej obliczeń na bajt załadowany z HBM).

V2 usuwa również normę RMS na głowicę, której V1 użył do stabilizacji odejmowania. W skali przedtreningowej klasy 70B, RMSNorm destabilizował późny trening. Wersja 2 zastępuje go prostszym schematem inicjalizacji, który zapewnia stabilność treningu bez dodatkowego modułu.

### Kiedy po nią sięgnąć

| Obciążenie pracą | Korzyści |
|---------|---------|
| RAG o długim kontekście (64 tys.+) | Czystsze mapy uwagi, mniej cytatów z halucynacjami |
| Testy porównawcze igły w stogu siana | Znaczący wzrost dokładności powyżej 32 tys. |
| Kontrola jakości wielu dokumentów | Mniej zakłóceń między dokumentami |
| Ukończenie kodu w 8k | Marginalne, nie warte zmiany architektury |
| Krótki czat (< 4k) | Zasadniczo nie do odróżnienia od wartości wyjściowych |

Wartość rośnie wraz z długością kontekstu. Przy żetonach 4 tys. poziom szumów jest na tyle mały, że standardowa uwaga jest w porządku. Przy 128 tys. to cię boli.

### Jak to się łączy z innymi gałkami z 2026 roku

| Funkcja | Kompatybilny z DIFF V2? |
|--------|--------------------------------------|
| GQA | Tak (V2 zwiększa głowice Q, a nie głowice KV) |
| MLA (DeepSeek) | Tak w zasadzie, nie opublikowano artykułu łączącego je |
| Ministerstwo Środowiska | Tak (uwaga jest niezależna od bloku MLP) |
| LINA | Tak (bez zmian) |
| Przędza / skalowanie długiego kontekstu | Tak (dokładnie tam, gdzie DIFF pomaga najbardziej) |
| FlashUwaga | Tak w V2 (było nie w V1) |
| Dekodowanie spekulatywne | Tak (zmiana uwagi jest niewidoczna dla pętli spec-decode) |

## Zbuduj to

`code/main.py` implementuje różnicową uwagę w czystym Pythonie. Zapytanie o zabawkę ze znaną strukturą sygnał plus szum pozwala bezpośrednio zmierzyć współczynnik redukcji szumów.

### Krok 1: standardowa uwaga softmax

Stdlib matrix ops: listy list, ręczne matmul, softmax z odejmowaniem wartości max przy stabilności numerycznej.

```python
def softmax(row):
    m = max(row)
    exps = [math.exp(x - m) for x in row]
    s = sum(exps)
    return [e / s for e in exps]
```

### Krok 2: podziel Q, K na dwie połowy

Styl V1: zmniejsz o połowę wymiar głowy. Styl V2: zachowaj wymiar głowy i podwoj liczbę głów. Implementacja zabawki wykorzystuje wersję V1 dla przejrzystości pedagogicznej — matematyka jest identyczna, różni się jedynie księgowość.

### Krok 3: dwie gałęzie softmax + odejmowanie

```python
A1 = [softmax([dot(q1, k) / scale for k in K1]) for q1 in Q1]
A2 = [softmax([dot(q2, k) / scale for k in K2]) for q2 in Q2]
diff_weights = [[a1 - lam * a2 for a1, a2 in zip(r1, r2)] for r1, r2 in zip(A1, A2)]
out = [[sum(w * v[j] for w, v in zip(row, V)) for j in range(d_v)] for row in diff_weights]
```

Uwaga: wagi wyjściowe mogą być ujemne. To dobrze — pamięć podręczna wartości nadal obsługuje podpisane wkłady. Kolejna projekcja V pochłania znak.

### Krok 4: pomiar redukcji szumów

Zbuduj syntetyczny ciąg o długości 1024. Umieść żeton sygnału w znanym miejscu, resztę wypełnij szumem. Oblicz (a) standardową wagę uwagi softmax na pozycji sygnału i (b) różnicową wagę uwagi. Zmierz stosunek sygnału do szumu w każdym z nich. Uwaga DIFF niezawodnie zapewnia wyższy stosunek sygnału do szumu od 3 do 10 razy, w zależności od tego, jak bardzo obie gałęzie zostały wyszkolone w zakresie różnic.

### Krok 5: Rozliczanie parametrów V1 i V2

Biorąc pod uwagę konfigurację (hidden=4096, heads=32, d_head=128), wydrukuj:

- Transformator bazowy: Q, K, V każdy rozmiar `hidden * hidden`, MLP przy 4 * ukryty.
- DIFF V1: Q, K każdy rozmiar `hidden * hidden`, rozmiar V `hidden * hidden` (bez zmian), przyciemnienie główki zmniejszone wewnętrznie o połowę. Dodaje parametry `lambda` na głowę (O(heads * d_head)).
- DIFF V2: rozmiar Q `2 * hidden * hidden`, rozmiar K `hidden * hidden`, rozmiar V `hidden * hidden`. Dodatkowe przyciemnienie wyświetlane z powrotem przed O_W. Dodaje te same parametry `lambda`.

Zabawka mierzy koszt dodatkowego parametru dla V2 (w przybliżeniu `hidden * hidden` dodatkowy na blok uwagi) i drukuje go.

## Użyj tego

Od kwietnia 2026 r. DIFF V2 nie będzie jeszcze dostępny na każdym produkcyjnym serwerze wnioskowania, ale trwa integracja z vLLM i SGLang. Tymczasem wzór pojawia się w:

- Wewnętrzne modele produkcyjne Microsoft o długim kontekście.
- Replikacje badawcze w kilku seriach szkoleniowych z otwartym modelem, skierowanych do ponad 256 tys.
- Architektury hybrydowe, które łączą uwagę DIFF z uwagą przesuwanego okna na alternatywnych warstwach.

Kiedy sięgniesz po to w 2026 roku:

- Szkolenie nowego modelu od podstaw w efektywnym kontekście ponad 64 tys. Dodaj od początku zróżnicowaną uwagę; późniejsze przekwalifikowanie jest kosztowne.
- Dostrajanie modelu o długim kontekście, w którym w ocenie dominują awarie zagubione w środku. LoRA na projekcjach Q może przybliżać strukturę DIFF.

Kiedy byś tego nie zrobił:

— Podajesz wstępnie wytrenowany gęsty model ze stabilną wydajnością w długim kontekście. Koszt przekwalifikowania rzadko zwraca się przy istniejących ciężarach.
- Twój kontekst jest zawsze poniżej 16 tys. Poziom szumów jest znikomy.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-diff-attention-integrator.md`. Biorąc pod uwagę architekturę modelu, docelowy kontekst, profil halucynacji i budżet szkoleniowy, tworzy się plan integracji mający na celu dodanie zróżnicowanej uwagi do nowego przebiegu przedtreningowego lub dostrojenie LoRA.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź, czy stosunek sygnału do szumu raportowany dla uwagi różnicowej jest wyższy niż standardowa uwaga softmax w zapytaniu syntetycznym. Zmieniaj amplitudę hałasu i wskaż punkt przecięcia, w którym standardowa uwaga staje się bezużyteczna.

2. Oblicz deltę liczby parametrów od wartości bazowej do DIFF V1 i od wartości bazowej do DIFF V2 dla modelu klasy 7B (hidden=4096, heads=32, d_head=128, 32 warstwy). Pokaż, które komponenty zyskały parametry, a które pozostały bez zmian.

3. Przeczytaj sekcję 3 artykułu DIFF V1 (arXiv:2410.05258) i sekcję 2 bloga DIFF V2 Hugging Face. W dwóch zdaniach wyjaśnij, dlaczego konieczna była norma RMSNorm V1 na głowę i dlaczego V2 mogła ją usunąć, nie powodując rozbieżności w szkoleniu.

4. Wykonaj ablację: oblicz różnicę uwagi za pomocą `lambda = 0` (czysty pierwszy softmax) i `lambda = 1` (pełne odejmowanie). W zapytaniu syntetycznym zmierz, jak zmienia się stosunek sygnału do szumu w całym cyklu. Zidentyfikuj `lambda`, który maksymalizuje stosunek sygnału do szumu.

5. Rozszerz zabawkę do GQA + DIFF V2. Wybierz 8 głowic KV i 32 głowice Q. Pokaż, że rozmiar pamięci podręcznej KV odpowiada podstawowemu modelowi GQA z tą samą konfiguracją (8, 32).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Uwaga różnicowa | „Dwa softmaxy minus siebie” | Podziel Q, K na dwie połowy, oblicz dwie mapy softmax, odejmij drugą (w skali lambda) od pierwszej, a następnie pomnóż przez V |
| Poziom szumów | „Niezerowy ogon softmaxu” | Softmax wagi O(1/N) umieszcza każdy niepowiązany token, co sumuje się do O(1) w długich kontekstach |
| lambda | „Skala odejmowania” | Skalar, którego można się nauczyć na głowę, sparametryzowany jako `exp(lq1.lk1) - exp(lq2.lk2) + lambda_init`; może być ujemny |
| RÓŻNICA V1 | „Wersja ICLR 2025” | Oryginalny transformator różnicowy; przyciemnia połowę głowy, aby zachować liczbę parametrów, wymaga niestandardowego jądra, wolniejsze dekodowanie |
| RÓŻNICA V2 | „Poprawka ze stycznia 2026 r.” | Podwaja głowy Q, utrzymując głowy KV; odpowiada podstawowej szybkości dekodowania i współpracuje z FlashAttention |
| Norma RMS na głowę | „Stabilizator V1” | Dodatkowa norma V1 stosowana po różnicy; V2 usunął go, aby zapobiec niestabilności późnego treningu |
| Stosunek sygnału do szumu | „Ile uwagi się marnuje” | Stosunek wagi na pozycji z prawdziwym sygnałem do średniej wagi na niepowiązanych pozycjach |
| Zagubiony w środku | „Tryb awarii w długim kontekście” | Zjawisko empiryczne, w którym dokładność wyszukiwania dokumentów spada w środku długiego kontekstu — uwaga DIFF to zmniejsza |
| Intensywność arytmetyczna | „Załadowana liczba FLOPów na bajt” | Współczynnik V2 zwiększony przy dekodowaniu poprzez podwojenie liczby zapytań na obciążenie KV; ważne dla dekodowania związanego z pamięcią |

## Dalsze czytanie

- [Ye i in. — Differential Transformer (arXiv:2410.05258, ICLR 2025)](https://arxiv.org/abs/2410.05258) — oryginalna praca poświęcona teorii redukcji szumów i ablacji o długim kontekście
— [Microsoft unilm — Differential Transformer V2 (blog Hugging Face, styczeń 2026 r.)](https://huggingface.co/blog/microsoft/diff-attn-v2) — przepisanie stosu produkcyjnego, dopasowanie dekodowania bazowego, zgodność z FlashAttention
- [Understanding Differential Transformer Unchains Pretrained Self-Attentions (arXiv:2505.16333)](https://arxiv.org/abs/2505.16333) — teoretyczna analiza tego, dlaczego odejmowanie przywraca wstępnie wytrenowaną strukturę uwagi
- [Shared DIFF Transformer (arXiv:2501.17900)](https://arxiv.org/html/2501.17900) — wariant z współdzieleniem parametrów
- [Vaswani i in. — Uwaga to wszystko, czego potrzebujesz (arXiv:1706.03762)](https://arxiv.org/abs/1706.03762) — bazowy DIFF Transformera odejmuje od
- [Liu i in. — Lost in the Middle (arXiv:2307.03172)](https://arxiv.org/abs/2307.03172) — długokontekstowy test porównawczy DIFF cele uwagi