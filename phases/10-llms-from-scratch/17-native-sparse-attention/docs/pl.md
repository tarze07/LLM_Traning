# Natywna rzadka uwaga (DeepSeek NSA)

> Przy 64 tys. tokenów uwaga pochłania 70–80% opóźnienia dekodowania. Każde laboratorium modelu otwartego ma plan, aby to naprawić. Utknęła praca DeepSeek NSA (najlepszy artykuł ACL 2025): trzy równoległe gałęzie uwagi — skompresowane tokeny gruboziarniste, selektywnie zachowywane tokeny drobnoziarniste i przesuwane okna dla kontekstu lokalnego — połączone za pomocą wyuczonej bramki. Jest dostosowany sprzętowo (przyjazny dla jądra), natywnie daje się trenować (działa w trybie wstępnego uczenia, nie jest włączany przy wnioskowaniu), a przy dekodowaniu 64 tys. działa szybciej niż FlashAttention, dopasowując lub pobijając jakość pełnej uwagi. Ta lekcja buduje trzy gałęzie od końca do końca i pokazuje, dlaczego rzadkość jest różniczkowalna od końca do końca.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 12 (pamięć podręczna KV, uwaga flash), Faza 7 · 15 (warianty uwagi), Faza 10 · 16 (uwaga różnicowa)
**Czas:** ~60 minut

## Cele nauczania

- Podaj trzy gałęzie uwagi NSA i co każda z nich wychwytuje.
- Wyjaśnij, dlaczego NSA można „natywnie przeszkolić”, podczas gdy wcześniejsze metody skupiające się na rozproszonej uwadze opierały się wyłącznie na wnioskowaniu.
- Oblicz oszczędności w obliczeniach uwagi NSA w porównaniu z pełną uwagą w kontekście 64k jako funkcję rozmiaru bloku kompresji i wyboru top-k.
- Zaimplementuj kombinację trzech gałęzi w stdlib Python na krótkiej sekwencji syntetycznej i sprawdź zachowanie wag bramkujących.

## Problem

Pełna uwaga na długości sekwencji N kosztuje `O(N^2)` czasu i `O(N)` pamięci podręcznej KV na warstwę. Przy 64 tys. tokenów wydajność obliczeniowa i przepustowość pamięci są katastrofalne. Zmierzone szacunki teoretyczne z artykułu NSA: uwaga odpowiada za 70–80% całkowitego opóźnienia dekodowania przy 64 tys. Wszystko na dalszym etapie łańcucha dostaw — TTFT, tokeny/s, koszt na milion tokenów — jest zdominowane przez koszt uwagi.

Rzadka uwaga jest oczywistą odpowiedzią. Wcześniejsze próby dzielą się na dwie grupy. Rzadkość o ustalonym wzorze (przesuwane okno, krokowa, lokalna blokowa) wyrzuca informacje i zawodzi w przypadku zadań przywracania dalekiego zasięgu. Rzadkość czasu wnioskowania (czyszczenie pamięci podręcznej KV, H2O, StreamingLLM) jest stosowana do modelu wstępnie wyszkolonego na gęstej uwadze i odzyskuje tylko ułamek potencjalnego przyspieszenia, ponieważ model nigdy nie był proszony o kierowanie informacji przez wzorzec rzadki.

Native Sparse Attention (Yuan i in., DeepSeek + PKU + UW, najlepszy artykuł ACL 2025, arXiv:2502.11089) zapewnia jedno i drugie: wzorzec rzadkości, którego model uczy się podczas wstępnego szkolenia, zaimplementowany jako algorytm wyrównany do jądra, który faktycznie zapewnia oszczędności obliczeniowe na etapie wnioskowania. Za dwa lata NSA lub jej bezpośredni potomek będą głównym obiektem zainteresowania każdego granicznego modelu o długim kontekście.

## Koncepcja

### Trzy równoległe gałęzie

Dla każdego zapytania NSA trzykrotnie sprawdza trzy różne widoki pamięci podręcznej KV:

1. **Gałąź skompresowana.** Tokeny są pogrupowane w bloki o rozmiarze `l` (zwykle 32 lub 64). Każdy blok jest kompresowany w pojedynczy token podsumowujący za pomocą małego wyuczonego MLP. Zapytanie sprawdza te skompresowane tokeny, uzyskując gruboziarnisty obraz całej sekwencji.

2. **Wybrana gałąź.** Na podstawie ocen uwagi ze skompresowanej gałęzi identyfikowanych jest k górnych bloków, które są najbardziej odpowiednie dla bieżącego zapytania. Odczytywane są szczegółowe (nieskompresowane) tokeny z tych bloków, a zapytanie dotyczy wszystkich z nich. Pomyśl o uwadze skompresowanej gałęzi jako o sygnale routingu dla selekcji.

3. **Gałąź okna przesuwnego.** Zapytanie dotyczy najnowszych tokenów `W` (zwykle 512) dla kontekstu lokalnego. Ta gałąź przechwytuje obciążone strukturą wzorce krótkiego zasięgu (składnia, koreferencja lokalna), które pozostałe dwa mogą przeoczyć.

Trzy wyjścia rozgałęźne są łączone za pomocą wyuczonej bramki dla poszczególnych pozycji:

```
out = g_cmp * out_cmp + g_sel * out_sel + g_win * out_win
```

`g_cmp, g_sel, g_win` to wagi bramek z małego MLP w zapytaniu. Nie muszą sumować się do 1 — mogą niezależnie ważyć gałęzie.

### Dlaczego można to „natywnie wyszkolić”

Etap selekcji (k górnych bloków) jest dyskretny. Operacje dyskretne przerywają przepływ gradientowy. Wcześniejsze prace wymagające rzadkiej uwagi albo pomijały podpory poprzez selekcję (ograniczając trening), albo stosowały ciągłe relaksacje, które nie zapewniały rzeczywistej rzadkości przy wnioskowaniu.

NSA omija to: uwaga skompresowanej gałęzi JEST różnicowalną, gruboziarnistą uwagą na całą sekwencję. Operacja top-k po prostu ponownie wykorzystuje najwyższe wyniki uwagi ze skompresowanej gałęzi, aby wybrać, które drobnoziarniste bloki mają zostać załadowane. Gradienty przepływają przez wyniki skompresowanej gałęzi (które wpływają zarówno na skompresowany wynik ORAZ na logikę wyboru), a udział wybranych bloków w końcowym wyniku jest również różniczkowy. Nieróżniczkowalna operacja `top_k` nie jest możliwa na wykresie obliczeniowym w przód — kontroluje tylko, które bloki zostaną załadowane z pamięci.

Właśnie dlatego NSA można stosować od początku do końca przed treningiem. Model uczy się kierować informacje łącznie przez trzy gałęzie, tworząc rzadki wzór, który przy wnioskowaniu faktycznie zapewnia obiecane przyspieszenie.

### Jądro dostosowane sprzętowo

Jądro NSA zostało zaprojektowane dla nowoczesnych hierarchii pamięci GPU. Jądro ładuje zapytania według grup GQA (pętla zewnętrzna), pobiera odpowiednie rzadkie bloki KV na grupę (pętla wewnętrzna) i kieruje uwagę na pamięć SRAM. Ponieważ każda grupa zapytań widzi te same wybrane bloki (wybór odbywa się na grupę zapytań, a nie na głowicę zapytania), obciążenia KV są amortyzowane w całej grupie. Intensywność arytmetyczna pozostaje wysoka.

W artykule podano, że jądra Tritona działają 9 razy szybciej niż FlashAttention przy dekodowaniu 64 tys., a współczynnik przyspieszenia rośnie wraz z długością sekwencji. Dostępne są zarówno jądra do przodu, jak i do tyłu.

### Budżet obliczeniowy

Niech `N` będzie długością sekwencji, `l` rozmiarem bloku kompresji, `k` liczbą selekcji górnego k, `w` przesuwanym oknem, `b` wybrany rozmiar bloku (zwykle równy `l`).

- Skompresowana gałąź: `O(N/l)` kluczy na zapytanie, więc łącznie `O(N * N / l)`.
- Wybrana gałąź: `O(k * b)` kluczy na zapytanie, więc `O(N * k * b)`.
- Gałąź przesuwna: `O(w)` kluczy na zapytanie, więc `O(N * w)`.

Razem: `O(N * (N/l + k*b + w))`.

W przypadku `N = 64k, l = 64, k = 16, b = 64, w = 512`: koszt zapytania wynosi `1000 + 1024 + 512 = 2536 keys`. Pełna uwaga to `64000 keys`. 25-krotna redukcja obliczeń.

W przypadku `N = 128k, l = 64, k = 16, b = 64, w = 512`: koszt zapytania wynosi `2000 + 1024 + 512 = 3536 keys`. Pełna uwaga to `128000 keys`. Redukcja 36x. Korzyści rosną wraz z długością sekwencji i o to właśnie chodzi.

### Jak to porównać

| Metoda | Różniczkowa | Prawdziwe przyspieszenie wnioskowania | Przywołanie dalekiego zasięgu |
|------------|--------------|----------------------|--------------------------------|
| Tylko okno przesuwne | tak | tak | zawodzi |
| Kroczący / rzadki blok | tak | tak | częściowe |
| Przycinanie KV (H2O, StreamingLLM) | N/A (czas wnioskowania) | tak | częściowe |
| MoBA (Moonshot) | częściowe | tak | dobrze |
| NSA | tak (natywnie) | tak (9x przy 64 tys.) | pasuje do pełnej uwagi |

MoBA (Moonshot, arXiv:2502.13189) zostało opublikowane jednocześnie i przyjmuje podobne podejście „trzy znaczy lepiej niż jeden”, stosując zasadę MoE do bloków uwagi. NSA i MoBA to dwie architektury, które warto poznać w przypadku szkoleń wstępnych w długim kontekście w roku 2026.

## Zbuduj to

`code/main.py` implementuje trzy gałęzie w krótkiej syntetycznej sekwencji i pokazuje:

- Kompresja MLP (dla przejrzystości pedagogicznej stosuje się prostą linię bazową średniej puli; prawdziwa NSA używa wyuczonego MLP).
- Wybór górnego k bloku na podstawie wyników skompresowanych gałęzi.
- Uwaga przesuwanego okna na ostatnie tokeny `w`.
- Zamknięta kombinacja.
- Wydruk obliczeń w porównaniu do pełnej uwagi.

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

### Krok 2: uwaga skompresowanej gałęzi

Uruchom softmax uwagę zapytania na skompresowanych kluczach. Skompresowana gałąź ma podwójną wartość jako sygnał do wyboru górnego k.

### Krok 3: wybór górnego bloku

Wybierz indeksy `k` skompresowanych bloków o najwyższym wyniku. Załaduj oryginalne nieskompresowane tokeny z tych bloków i zwróć na nie uwagę.

### Krok 4: uwaga w przesuwanym oknie

Weź ostatnie tokeny `w` i skieruj na nie standardową uwagę.

### Krok 5: brama + kombajn

Mały MLP w zapytaniu generuje trzy wagi bramek. Wynik końcowy jest sumą ważoną wyników trzech gałęzi.

### Krok 6: oblicz liczenie

Wydrukuj liczbę kluczy obsługiwanych na zapytanie dla każdego oddziału i sumę. Porównaj z `N` (pełna uwaga). Na syntetycznym 1024 tokenach z `l = 32, k = 4, w = 128` NSA widzi `32 + 128 + 128 = 288` kluczy na zapytanie w porównaniu z 1024 w przypadku pełnej uwagi — 3,5 razy mniej.

## Użyj tego

NSA realizuje własny długoterminowy program szkoleń przedszkoleniowych DeepSeek. Stan integracji w publicznych stosach wnioskowania na kwiecień 2026 r.:

- **Wewnętrzna funkcja DeepSeek**: natywne, opublikowane wagi korzystają z NSA lub jego następcy DSA (Deepseek Sparse Attention).
- **vLLM**: eksperymentalne wsparcie NSA w rozwoju wag DeepSeek-V3.x.
- **SGLang**: Opublikowano benchmarki NSA; ścieżka produkcji przebiega według vLLM.
- **llama.cpp / CPU**: nieobsługiwane; narzut związany z rozkładem jądra nie jest tego wart przy przepustowości procesora.

Kiedy sięgnąć po NSA:

— Uruchomienie przedtreningowe lub w ramach kontynuacji szkolenia, obejmujące kontekst ponad 64 tys. z poważnym budżetem obliczeniowym.
- Wnioskowanie z własnych punktów kontrolnych o długim kontekście DeepSeek. Wagi pochodzą z NSA.

Kiedy nie:

— Obsługa istniejącego, wstępnie wyszkolonego modelu o dużej koncentracji uwagi. Nie można modernizować NSA bez ciągłego szkolenia.
- Kontekst poniżej 16 tys. W oszczędnościach dominuje trójgałęziowy narzut.
- Interaktywny czat wsadowy-1. Korzyści z dekodowania wrażliwego na opóźnienia, ale tylko w długich kontekstach.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-nsa-integrator.md`. Biorąc pod uwagę specyfikację przebiegu przedtreningowego w długim kontekście, tworzy plan integracji NSA: rozmiar bloku kompresji, top-k, okno przesuwne, szerokość bramki MLP, wybór jądra i specyficzne wartości ewaluacyjne w długim kontekście, które uzasadniałyby zmianę architektury.

## Ćwiczenia

1. Uruchom `code/main.py` na syntetycznym tokenie 1024. Przejrzyj `(l, k, w)` trzy ustawienia wstępne i wydrukuj liczniki obliczeń. Zidentyfikuj ustawienie wstępne, które osiąga najniższą liczbę kluczy na zapytanie, zachowując 95% przypomnienia przy pełnej uwadze w teście igły w stogu siana.

2. Wymień kompresor średniej puli na mały, wyuczony MLP (2-warstwowy, ukryty 32). Trenuj go w syntetycznym zadaniu, w którym sygnał jest średnią bloku. Zmierz lukę w zakłopotaniu w stosunku do wartości bazowej średniej puli na podstawie wstrzymanych danych.

3. Zaimplementuj bramkę MLP. Przyjmuje zapytanie jako dane wejściowe i wyprowadza trzy skalary. Pokaż, że bramka zachowuje się rozsądnie: prawie równomierne ważenie w przypadku losowych zapytań, duża waga w wybranej gałęzi, gdy zapytanie trafia w odległy blok.

4. Oblicz budżet pamięci podręcznej KV dla modelu 70B z obsługą NSA w kontekście 128 kB. Głowice KV to 8, średnica głowicy 128, BF16. Porównaj z pełną uwagą i MLA (faza 10 · 14 pokazała liczby MLA). Zidentyfikuj długość sekwencji, przy której szczegółowa pamięć podręczna KV oddziału NSA równa się pełnej uwadze.

5. Przeczytaj sekcję 4 artykułu NSA (arXiv:2502.11089) i wyjaśnij w trzech zdaniach, dlaczego wyniki uwagi skompresowanej gałęzi są ponownie wykorzystywane do wyboru górnego k, zamiast obliczać oddzielny wynik routingu. Powiąż odpowiedź z przepływem gradientowym.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Skompresowana gałąź | „Zgrubny widok” | Uwaga na klucze uśredniane blokowo, które zapewniają kontekst globalny w kluczach O(N/l) na zapytanie |
| Wybrany oddział | „Top-k bloków” | Szczegółowa uwaga dotycząca bloków `k` z najwyższymi wynikami skompresowanych gałęzi |
| Przesuwane okno | „Kontekst lokalny” | Uwaga na ostatnie tokeny `W` dla wzorców krótkiego zasięgu |
| Natywna możliwość trenowania | „Przed treningiem z włączonym trybem rzadkości” | Wzorzec rzadkości jest wyuczony podczas wstępnego treningu, a nie przykręcany na podstawie wniosków |
| Rozmiar bloku kompresyjnego l | „Rozmiar grupy dla widoku zgrubnego” | Ile tokenów zostanie połączonych w jedno podsumowanie; 32-64 typowe |
| Top-k | „Bloki do zatrzymania” | Liczba skompresowanych bloków, których nieskompresowane tokeny są odczytywane; 16 typowych |
| Okno przesuwne W | „Lokalny promień uwagi” | Zazwyczaj 512; krócej szkodzi lokalnej spójności, dłuższe obliczenia marnują |
| Brama oddziału | „Jak wymieszać te trzy” | Dane wyjściowe MLP na pozycję, które ważą wkłady trzech oddziałów |
| Wyrównanie sprzętu | „Rzadkość przyjazna dla jądra” | Rzadki wzór wybrany tak, aby rzeczywiste jądro GPU osiągnęło teoretyczne przyspieszenie |
| DSA | „Następca NSA” | Deepseek Sparse Attention, architektura następująca po NSA w linii DeepSeek |

## Dalsze czytanie

- [Yuan i in. — Native Sparse Attention: Hardware-Aligned and Native Trainable Sparse Attention (arXiv:2502.11089, ACL 2025 Best Paper)](https://arxiv.org/abs/2502.11089) — artykuł
- [Raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — rodzina architektur, do których dąży NSA
- [Moonshot AI — MoBA: Mieszanka uwagi blokowej dla LLM o długim kontekście (arXiv:2502.13189)](https://arxiv.org/abs/2502.13189) — praca równoległa, uwaga w stylu MoE nad blokami
- [Beltagy i in. — Longformer: The Long-Document Transformer (arXiv:2004.05150)](https://arxiv.org/abs/2004.05150) — Początki przesuwanego okna
- [Xiao i in. — StreamingLLM: wydajne modele języka przesyłania strumieniowego z pochłaniaczami uwagi (arXiv:2309.17453)](https://arxiv.org/abs/2309.17453) — bazowa rzadkość wnioskowania NSA poprawia
- [Dao i in. — FlashAttention-2 (arXiv:2307.08691)](https://arxiv.org/abs/2307.08691) — podstawowe jądra NSA pełnej uwagi pracują z prędkością 64 tys.