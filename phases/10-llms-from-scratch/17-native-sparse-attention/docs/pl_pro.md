# Natywna rzadka uwaga (DeepSeek NSA)

> Przy 64 tys. tokenów mechanizm uwagi pochłania 70–80% opóźnienia dekodowania. Każde laboratorium modeli open-source ma plan, by to zmienić. Praca DeepSeek NSA (najlepszy artykuł ACL 2025) wyróżnia się spośród nich: trzy równoległe gałęzie uwagi — skompresowane tokeny gruboziarniste, selektywnie zachowywane tokeny drobnoziarniste oraz przesuwane okno dla kontekstu lokalnego — połączone wyuczoną bramką. Mechanizm jest dostosowany sprzętowo (przyjazny dla jądra) i natywnie nadaje się do treningu (działa już na etapie wstępnego uczenia, nie jest dołączany wyłącznie przy wnioskowaniu). Podczas dekodowania przy 64 tys. tokenów działa szybciej niż FlashAttention, dorównując lub przewyższając jakością pełną uwagę. Ta lekcja buduje trzy gałęzie od podstaw i wyjaśnia, dlaczego rzadkość jest różniczkowalna w całym potoku.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 12 (pamięć podręczna KV, uwaga flash), Faza 7 · 15 (warianty uwagi), Faza 10 · 16 (uwaga różnicowa)
**Czas:** ~60 minut

## Cele nauczania

- Wymienić trzy gałęzie uwagi NSA i opisać, co każda z nich wychwytuje.
- Wyjaśnić, dlaczego NSA można „natywnie trenować", podczas gdy wcześniejsze metody rzadkiej uwagi działały wyłącznie na etapie wnioskowania.
- Obliczyć oszczędności obliczeniowe NSA w porównaniu z pełną uwagą przy kontekście 64k jako funkcję rozmiaru bloku kompresji i wartości top-k.
- Zaimplementować kombinację trzech gałęzi w czystym Pythonie na krótkiej sekwencji syntetycznej i zbadać zachowanie wag bramkujących.

## Problem

Pełna uwaga dla sekwencji o długości N kosztuje `O(N^2)` czasu i `O(N)` pamięci podręcznej KV na warstwę. Przy 64 tys. tokenów koszty obliczeniowe i przepustowość pamięci osiągają katastrofalne rozmiary. Zgodnie z pomiarami z artykułu NSA, uwaga odpowiada za 70–80% całkowitego opóźnienia dekodowania przy 64 tys. tokenów. Wszystkie kluczowe wskaźniki — TTFT, tokeny/s, koszt na milion tokenów — są zdominowane przez ten koszt.

Rzadka uwaga jest oczywistym rozwiązaniem. Dotychczasowe podejścia dzielą się na dwie grupy. Rzadkość o ustalonym wzorcu (przesuwane okno, krokowa, lokalna blokowa) odrzuca część informacji i zawodzi w zadaniach wymagających odwoływania się do odległych fragmentów sekwencji. Rzadkość stosowana na etapie wnioskowania (przycinanie pamięci podręcznej KV, H2O, StreamingLLM) nakładana jest na model wstępnie wytrenowany z pełną uwagą — odzyskuje jedynie ułamek potencjalnego przyspieszenia, ponieważ model nigdy nie uczył się kierowania informacji przez rzadki wzorzec.

Native Sparse Attention (Yuan i in., DeepSeek + PKU + UW, najlepszy artykuł ACL 2025, arXiv:2502.11089) łączy obie zalety: wzorzec rzadkości wyuczony podczas wstępnego treningu, zaimplementowany jako algorytm wyrównany do jądra, który faktycznie zapewnia oszczędności obliczeniowe na etapie wnioskowania. W ciągu najbliższych lat NSA lub jej bezpośredni następca stanie się podstawowym mechanizmem w każdym granicznym modelu o długim kontekście.

## Koncepcja

### Trzy równoległe gałęzie

Dla każdego zapytania NSA sprawdza pamięć podręczną KV z trzech różnych perspektyw:

1. **Gałąź skompresowana.** Tokeny są grupowane w bloki o rozmiarze `l` (zazwyczaj 32 lub 64). Każdy blok jest kompresowany do pojedynczego tokenu podsumowującego za pomocą niewielkiego, wyuczonego MLP. Zapytanie jest wykonywane na tych skompresowanych tokenach, co daje gruboziarnisty obraz całej sekwencji.

2. **Gałąź selekcji.** Na podstawie wyników uwagi z gałęzi skompresowanej wskazywanych jest k bloków najbardziej istotnych dla bieżącego zapytania. Odczytywane są oryginalne, nieskompresowane tokeny z tych bloków i zapytanie wykonywane jest na ich pełnej reprezentacji. Uwaga skompresowanej gałęzi pełni tu rolę sygnału routingu dla procesu selekcji.

3. **Gałąź przesuwanego okna.** Zapytanie wykonywane jest na ostatnich tokenach `W` (zazwyczaj 512) dla kontekstu lokalnego. Ta gałąź wychwytuje wzorce krótkosiężne obciążone strukturą — składnię, koreferencję lokalną — które pozostałe dwie mogłyby pominąć.

Wyniki trzech gałęzi są łączone za pomocą wyuczonej bramki zależnej od pozycji:

```
out = g_cmp * out_cmp + g_sel * out_sel + g_win * out_win
```

`g_cmp, g_sel, g_win` to wagi bramek generowane przez niewielki MLP działający na zapytaniu. Nie muszą sumować się do 1 — mogą niezależnie ważyć poszczególne gałęzie.

### Dlaczego możliwy jest trening natywny

Etap selekcji (wybór k górnych bloków) jest operacją dyskretną, a operacje dyskretne przerywają przepływ gradientu. Wcześniejsze prace ze rzadką uwagą albo pomijały gradienty przez operację selekcji — ograniczając możliwości treningu — albo stosowały ciągłe relaksacje, które nie dawały rzeczywistej rzadkości podczas wnioskowania.

NSA omija ten problem: uwaga w gałęzi skompresowanej jest w pełni różniczkowalną, gruboziarnistą uwagą na całą sekwencję. Operacja top-k jedynie ponownie wykorzystuje najwyższe wyniki z gałęzi skompresowanej, by wybrać, które drobnoziarniste bloki załadować. Gradienty przepływają przez wyniki gałęzi skompresowanej (które wpływają zarówno na jej własny wynik, jak i na logikę selekcji), a wkład wybranych bloków w końcowy wynik jest również różniczkowalny. Niedyferencjowalna operacja `top_k` nie leży na grafie obliczeniowym — decyduje jedynie o tym, które bloki zostaną załadowane z pamięci.

Właśnie dlatego NSA nadaje się do stosowania od samego początku treningu. Model uczy się wspólnie kierować informacje przez trzy gałęzie, tworząc rzadki wzorzec, który podczas wnioskowania faktycznie zapewnia obiecane przyspieszenie.

### Jądro dostosowane sprzętowo

Jądro NSA zostało zaprojektowane z myślą o nowoczesnych hierarchiach pamięci GPU. Ładuje zapytania według grup GQA (pętla zewnętrzna), pobiera odpowiednie rzadkie bloki KV dla każdej grupy (pętla wewnętrzna) i kieruje obliczenia uwagi na pamięć SRAM. Ponieważ każda grupa zapytań widzi te same wybrane bloki — selekcja odbywa się na poziomie grupy zapytań, nie pojedynczej głowicy — ładowania KV są amortyzowane w całej grupie. Intensywność arytmetyczna pozostaje wysoka.

Autorzy artykułu podają, że jądra Tritona działają 9 razy szybciej niż FlashAttention podczas dekodowania przy 64 tys. tokenów, a współczynnik przyspieszenia rośnie wraz z długością sekwencji. Dostępne są jądra zarówno dla przejścia w przód, jak i wstecz.

### Budżet obliczeniowy

Niech `N` oznacza długość sekwencji, `l` — rozmiar bloku kompresji, `k` — liczbę wybieranych bloków top-k, `w` — rozmiar przesuwanego okna, `b` — rozmiar wybranego bloku (zazwyczaj równy `l`).

- Gałąź skompresowana: `O(N/l)` kluczy na zapytanie, łącznie `O(N * N / l)`.
- Gałąź selekcji: `O(k * b)` kluczy na zapytanie, łącznie `O(N * k * b)`.
- Gałąź przesuwanego okna: `O(w)` kluczy na zapytanie, łącznie `O(N * w)`.

Razem: `O(N * (N/l + k*b + w))`.

Dla `N = 64k, l = 64, k = 16, b = 64, w = 512`: koszt na zapytanie wynosi `1000 + 1024 + 512 = 2536` kluczy. Pełna uwaga wymaga `64000` kluczy — to 25-krotna redukcja obliczeń.

Dla `N = 128k, l = 64, k = 16, b = 64, w = 512`: koszt na zapytanie wynosi `2000 + 1024 + 512 = 3536` kluczy. Pełna uwaga wymaga `128000` kluczy — redukcja 36-krotna. Korzyści rosną wraz z długością sekwencji i na tym właśnie polega przewaga tej metody.

### Porównanie metod

| Metoda | Różniczkowalność | Realne przyspieszenie wnioskowania | Odwoływanie dalekiego zasięgu |
|------------|--------------|----------------------|--------------------------------|
| Tylko okno przesuwne | tak | tak | zawodzi |
| Rzadkość blokowa | tak | tak | częściowe |
| Przycinanie KV (H2O, StreamingLLM) | N/A (czas wnioskowania) | tak | częściowe |
| MoBA (Moonshot) | częściowe | tak | dobre |
| NSA | tak (natywnie) | tak (9x przy 64 tys.) | dorównuje pełnej uwadze |

MoBA (Moonshot, arXiv:2502.13189) zostało opublikowane równolegle i przyjmuje podobne podejście łączenia wielu gałęzi, stosując zasadę MoE do bloków uwagi. NSA i MoBA to dwie architektury warte dogłębnego poznania w kontekście wstępnego treningu z długim kontekstem w 2026 roku.

## Zbuduj to

`code/main.py` implementuje trzy gałęzie na krótkiej sekwencji syntetycznej i ilustruje:

- Kompresję MLP (dla przejrzystości pedagogicznej stosuje się prostą linię bazową średniej puli; właściwa NSA używa wyuczonego MLP).
- Wybór top-k bloków na podstawie wyników gałęzi skompresowanej.
- Uwagę przesuwanego okna na ostatnie tokeny `w`.
- Kombinację z bramką.
- Zestawienie kosztów obliczeniowych względem pełnej uwagi.

### Krok 1: skompresuj tokeny w bloki

```python
def compress(K, l):
    n = len(K)
    n_blocks = (n + l - 1) // l
    out = []
    for b in range(n_blocks):
        start, end = b * l, min((b + 1) * l, n)
        block = K[start:end]
        summary = [sum(row[d] for row in block) / len(block) for d in range(len(K[0]))]
        out.append(summary)
    return out
```

### Krok 2: uwaga gałęzi skompresowanej

Wykonaj uwagę z softmax dla zapytania na skompresowanych kluczach. Gałąź skompresowana pełni podwójną rolę: dostarcza wynik uwagi oraz sygnał do wyboru top-k.

### Krok 3: wybór najważniejszych bloków

Wybierz indeksy `k` skompresowanych bloków o najwyższym wyniku. Załaduj oryginalne, nieskompresowane tokeny z tych bloków i wykonaj na nich uwagę.

### Krok 4: uwaga przesuwanego okna

Pobierz ostatnie tokeny `w` i wykonaj na nich standardową uwagę.

### Krok 5: bramka i łączenie

Niewielki MLP działający na zapytaniu generuje trzy wagi bramek. Wynik końcowy jest ważoną sumą wyników trzech gałęzi.

### Krok 6: oblicz koszty

Wydrukuj liczbę kluczy obsługiwanych na zapytanie dla każdej gałęzi oraz ich sumę. Porównaj z `N` (pełna uwaga). Dla syntetycznej sekwencji 1024 tokenów z `l = 32, k = 4, w = 128` NSA przetwarza `32 + 128 + 128 = 288` kluczy na zapytanie wobec 1024 przy pełnej uwadze — 3,5 razy mniej.

## Zastosowania praktyczne

NSA realizuje długoterminowy plan wstępnego treningu DeepSeek. Stan integracji w publicznych stosach wnioskowania na kwiecień 2026 r.:

- **Wewnętrznie w DeepSeek**: natywnie — opublikowane wagi korzystają z NSA lub jego następcy DSA (Deepseek Sparse Attention).
- **vLLM**: eksperymentalne wsparcie NSA w trakcie prac nad wagami DeepSeek-V3.x.
- **SGLang**: opublikowano benchmarki NSA; ścieżka produkcyjna podąża za vLLM.
- **llama.cpp / CPU**: brak wsparcia; narzut związany z wywołaniami jądra nie jest opłacalny przy przepustowości procesora.

Kiedy warto sięgnąć po NSA:

- Wstępny trening lub kontynuacja treningu przy kontekście powyżej 64 tys. z poważnym budżetem obliczeniowym.
- Wnioskowanie na własnych punktach kontrolnych DeepSeek z długim kontekstem — wagi wywodzą się z NSA.

Kiedy nie warto:

- Obsługa istniejącego modelu wstępnie wytrenowanego z gęstą uwagą. Modernizacja do NSA wymaga dodatkowego treningu ciągłego.
- Kontekst poniżej 16 tys. tokenów — narzut trójgałęziowy dominuje nad oszczędnościami.
- Interaktywny czat z rozmiarem wsadu wynoszącym 1. Korzyści z dekodowania pojawiają się dopiero przy długich kontekstach.

## Wynik

Ta lekcja tworzy `outputs/skill-nsa-integrator.md`. Na podstawie specyfikacji przebiegu wstępnego treningu z długim kontekstem generuje plan integracji NSA: rozmiar bloku kompresji, top-k, rozmiar przesuwanego okna, szerokość MLP bramki, dobór jądra oraz konkretne punkty ewaluacyjne dla długiego kontekstu, uzasadniające zmianę architektury.

## Ćwiczenia

1. Uruchom `code/main.py` na syntetycznej sekwencji 1024 tokenów. Przetestuj trzy zestawy parametrów `(l, k, w)` i wydrukuj liczniki kosztów obliczeniowych. Wskaż konfigurację, która osiąga najniższą liczbę kluczy na zapytanie przy zachowaniu 95% przypominania w teście igły w stogu siana względem pełnej uwagi.

2. Zastąp kompresor oparty na średniej puli małym, wyuczonym MLP (2 warstwy, rozmiar ukryty 32). Wytrenuj go na syntetycznym zadaniu, w którym sygnałem jest średnia bloku. Zmierz różnicę w perplexity względem linii bazowej ze średnią pulą na danych wstrzymanych.

3. Zaimplementuj bramkę MLP. Przyjmuje zapytanie jako wejście i zwraca trzy skalary. Wykaż, że bramka zachowuje się rozsądnie: zbliżone do równomiernego ważenie dla losowych zapytań, wysoka waga gałęzi selekcji gdy zapytanie trafia w odległy blok.

4. Oblicz budżet pamięci podręcznej KV dla modelu 70B obsługującego NSA przy kontekście 128k. Głowice KV: 8, wymiar głowicy: 128, format BF16. Porównaj z pełną uwagą i MLA (faza 10 · 14 zawiera odpowiednie liczby). Wyznacz długość sekwencji, przy której szczegółowa pamięć podręczna KV gałęzi selekcji NSA dorównuje pełnej uwadze.

5. Przeczytaj sekcję 4 artykułu NSA (arXiv:2502.11089) i wyjaśnij w trzech zdaniach, dlaczego wyniki uwagi gałęzi skompresowanej są ponownie wykorzystywane do wyboru top-k zamiast obliczania oddzielnego wyniku routingu. Odnieś odpowiedź do przepływu gradientu.

## Kluczowe terminy

| Termin | Popularne określenie | Znaczenie |
|------|----------------|--------------------------------------|
| Gałąź skompresowana | „Widok gruboziarnisty" | Uwaga na klucze uśredniane blokowo, zapewniające globalny kontekst przy O(N/l) kluczach na zapytanie |
| Gałąź selekcji | „Bloki top-k" | Szczegółowa uwaga na `k` bloków z najwyższymi wynikami gałęzi skompresowanej |
| Okno przesuwne | „Kontekst lokalny" | Uwaga na ostatnie tokeny `W` dla wzorców krótkosiężnych |
| Natywna trenowalność | „Rzadkość już od wstępnego treningu" | Wzorzec rzadkości wyuczony podczas wstępnego treningu, nie dokładany dopiero na etapie wnioskowania |
| Rozmiar bloku kompresji l | „Rozmiar grupy dla widoku gruboziarnistego" | Liczba tokenów łączonych w jedno podsumowanie; typowo 32–64 |
| Top-k | „Bloki do zachowania" | Liczba skompresowanych bloków, których nieskompresowane tokeny są odczytywane; typowo 16 |
| Okno przesuwne W | „Promień uwagi lokalnej" | Zazwyczaj 512; mniejsze wartości szkodzą lokalnej spójności, większe marnują obliczenia |
| Bramka gałęzi | „Sposób łączenia trzech gałęzi" | Wyjście MLP zależne od pozycji, ważące wkłady trzech gałęzi |
| Wyrównanie sprzętowe | „Rzadkość przyjazna jądru" | Wzorzec rzadkości dobrany tak, by jądro GPU osiągało teoretyczne przyspieszenie |
| DSA | „Następca NSA" | Deepseek Sparse Attention — architektura następująca po NSA w linii produktów DeepSeek |

## Dalsze czytanie

- [Yuan i in. — Native Sparse Attention: Hardware-Aligned and Native Trainable Sparse Attention (arXiv:2502.11089, ACL 2025 Best Paper)](https://arxiv.org/abs/2502.11089) — artykuł źródłowy
- [Raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — rodzina architektur, do których dąży NSA
- [Moonshot AI — MoBA: Mieszanka uwagi blokowej dla LLM o długim kontekście (arXiv:2502.13189)](https://arxiv.org/abs/2502.13189) — praca równoległa, uwaga w stylu MoE nad blokami
- [Beltagy i in. — Longformer: The Long-Document Transformer (arXiv:2004.05150)](https://arxiv.org/abs/2004.05150) — początki przesuwanego okna
- [Xiao i in. — StreamingLLM: wydajne modele językowe dla strumieniowania z pochłaniaczami uwagi (arXiv:2309.17453)](https://arxiv.org/abs/2309.17453) — bazowa rzadkość wnioskowania, którą NSA ulepsza
- [Dao i in. — FlashAttention-2 (arXiv:2307.08691)](https://arxiv.org/abs/2307.08691) — jądra pełnej uwagi, z którymi NSA rywalizuje przy 64 tys. tokenów
