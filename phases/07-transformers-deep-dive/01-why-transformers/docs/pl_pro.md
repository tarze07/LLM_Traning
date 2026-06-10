# Dlaczego transformatory — problemy z RNN

> RNN przetwarzają tokeny jeden po drugim. Transformatory przetwarzają wszystkie tokeny jednocześnie. Ta jedna decyzja architektoniczna zmieniła każdą krzywą skalowania w głębokim uczeniu po 2017 roku.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 3 (rdzeń głębokiego uczenia), Faza 5 · 09 (sequence-to-sequence), Faza 5 · 10 (mechanizm uwagi)
**Czas:** ~45 minut

## Problem

Przed rokiem 2017 każdy czołowy model sekwencji — językowy, tłumaczeniowy, mowy — był rekurencyjną siecią neuronową. LSTM i GRU przez pół dekady dominowały w testach porównawczych odpowiadających ImageNet dla tłumaczenia maszynowego. Były jedynym dostępnym narzędziem.

Miały jednak trzy poważne słabości.

Sekwencyjność obliczeń uniemożliwiała zrównoleglenie wzdłuż osi czasu: token `t+1` wymaga stanu ukrytego z tokena `t`. Sekwencja 1024 tokenów oznaczała 1024 szeregowe kroki na procesorze graficznym zdolnym do miliona operacji zmiennoprzecinkowych na cykl. Czas uczenia rósł liniowo wraz z długością sekwencji na sprzęcie zaprojektowanym z myślą o równoległości.

Zanikające gradienty powodowały, że informacja sprzed 50 tokenów była kompresowana przez 50 nieliniowości. Bramkowane jednostki (LSTM, GRU) łagodziły ten problem, lecz nie eliminowały go całkowicie. Zależności długodystansowe — „książka, którą czytałem latem ubiegłego roku w samolocie do Kioto, to…" — regularnie gubiły się podczas uczenia.

Stan ukryty o stałym rozmiarze zmuszał koder do skompresowania całej sekwencji źródłowej w jeden wektor, zanim dekoder cokolwiek zobaczył. Bez względu na to, czy źródłem było 5 tokenów, czy 500, wąskie gardło miało ten sam kształt.

W 2017 roku artykuł „Attention Is All You Need" zaproponował radykalne rozwiązanie: całkowite wyeliminowanie rekurencji. Każda pozycja miałaby odpytywać równolegle wszystkie pozostałe. Zamiast 1024 kolejnych kroków — jedno duże mnożenie macierzy.

Efektem jest dominacja w każdej modalności do 2026 roku. Język (GPT-5, Claude 4, Llama 4), obraz (ViT, DINOv2, SAM 3), dźwięk (Whisper), biologia (AlphaFold 3), robotyka (RT-2). Ten sam blok, różne dane wejściowe.

## Koncepcja

![Sekwencyjne obliczenia RNN a równoległa uwaga transformatora](../assets/rnn-vs-transformer.svg)

**Rekurencja jako wąskie gardło.** RNN oblicza `h_t = f(h_{t-1}, x_t)`. Każdy krok zależy od poprzedniego — nie można obliczyć `h_5` przed `h_4`. Przy ponad 10 000 równoległych rdzeni nowoczesnego procesora graficznego oznacza to marnowanie 99% możliwości obliczeniowych podczas przetwarzania długich sekwencji.

**Uwaga jako przetwarzanie równoległe.** Samouwaga oblicza `output_i = sum_j(a_ij * v_j)` dla każdej pary `(i, j)` jednocześnie. Cała macierz uwagi N×N wypełnia jedno wsadowe mnożenie macierzy. Żaden krok nie zależy od innego. Procesory graficzne radzą sobie z tym znakomicie.

**Przyspieszenie nie jest stałą wartością.** To różnica między głębokością szeregową `O(N)` a `O(1)`. W praktyce transformatory uczą się 5–10 razy szybciej na epokę na identycznym sprzęcie przy N=512, a przewaga rośnie wraz z długością sekwencji — aż do osiągnięcia limitu pamięci `O(N²)` dla mechanizmu uwagi (który Flash Attention rozwiązał później — zob. Lekcja 12).

**Koszt transformatorów.** Pamięć mechanizmu uwagi skaluje się jak `O(N²)`. Dla kontekstu 2K to nie problem. Dla kontekstu 128 KB potrzebne są przesuwające się okna, ekstrapolacja RoPE, kafelkowanie Flash Attention lub warianty uwagi liniowej. Rekurencja wymagała `O(N)` zarówno czasu, jak i pamięci; transformatory zamieniają czas na pamięć, a następnie odzyskują go dzięki równoległości.

**Założenia wbudowane w architekturę.** RNN zakładają lokalność i aktualność informacji. Transformatory nie zakładają niczego — każda para pozycji jest kandydatem do uwagi. Dlatego transformatory potrzebują więcej danych do skutecznego uczenia, lecz gdy je otrzymają, skalują się znacznie lepiej. Chinchilla (2022) to sformalizowała: przy wystarczającej liczbie tokenów transformator zawsze przewyższa RNN o tej samej liczbie parametrów.

## Zbuduj to

Nie ma tu żadnej sieci neuronowej — symulujemy numerycznie wąskie gardło w samym rdzeniu, by poczuć różnicę na własnym laptopie.

### Krok 1: zmierz głębokość szeregową

Zobacz `code/main.py`. Budujemy dwie funkcje. Pierwsza koduje sekwencję jako łańcuch dodawań (szeregowo, jak RNN). Druga robi to samo jako redukcję równoległą (jak uwaga). Ta sama matematyka, inny graf zależności.

```python
def rnn_style(xs):
    h = 0.0
    for x in xs:
        h = 0.9 * h + x   # can't parallelize: h depends on previous h
    return h

def attention_style(xs):
    return sum(xs) / len(xs)  # every x is independent
```

Obie funkcje mierzymy czasowo na sekwencjach do 100 000 elementów. Wersja RNN działa w czasie O(N) jako pojedynczy potok procesora. Nawet w czystym Pythonie redukcja w stylu uwagi okazuje się lepsza dla długości ≥ 1000, ponieważ `sum()` jest zaimplementowany w C i iteruje bez narzutu interpretera na każdy krok.

### Krok 2: policz operacje teoretyczne

Oba algorytmy wykonują N dodawań. Różnica tkwi w *głębokości zależności*: ile operacji musi wykonać się szeregowo, zanim możliwe będzie przejście do następnej. Głębokość RNN wynosi N. Głębokość uwagi wynosi log(N) dla redukcji drzewiastej lub 1 dla skanowania równoległego. O czasie pracy na GPU decyduje głębokość, nie liczba operacji.

### Krok 3: empiryczne skalowanie dla długich sekwencji

Wydrukujemy tabelę pomiarów czasu, która uwidacznia lukę O(N). Na laptopie Mac z 2026 roku sekwencje poniżej 1000 elementów są zbyt krótkie, by je zmierzyć. Sekwencje 100 000-elementowe pokazują czysty skan liniowy. Przeskaluj to do transformatora obsługującego 16 384 tokenów i porównywalnego pod względem rozmiaru 12-warstwowego LSTM, a zobaczysz, dlaczego czas uczenia był blokerem w 2016 roku.

## Użyj tego

Kiedy warto nadal wybierać RNN w 2026 roku:

| Sytuacja | Wybierz |
|----------|------|
| Wnioskowanie strumieniowe, jeden token na raz, stała pamięć | RNN lub model przestrzeni stanów (Mamba, RWKV) |
| Bardzo długie sekwencje (> 1M tokenów), gdzie pamięć uwagi nie wystarcza | Uwaga liniowa, Mamba 2, Hyena |
| Urządzenia brzegowe bez akceleratora Matmul | RNN z separowanymi splotami wciąż wygrywa pod względem FLOP/W |
| Wszystko inne (uczenie, wsadowe wnioskowanie, kontekst do 128 KB) | Transformator |

Modele przestrzeni stanów (SSM), takie jak Mamba, to w istocie RNN ze strukturalną parametryzacją łączącą zalety obu podejść: pamięć `O(N)` podczas skanowania, równoległe uczenie przez selektywne skanowanie. Odzyskują 90% jakości transformatora przy lepszym skalowaniu w długim kontekście. W 2026 roku większość wiodących laboratoriów szkoli hybrydowe modele SSM + transformator (np. Jamba, Samba) — rekurencja nie jest martwa, lecz stała się jednym z elementów architektury.

## Wyślij to

Zobacz `outputs/skill-architecture-picker.md`. Umiejętność dobiera architekturę do nowego problemu sekwencji na podstawie długości, przepustowości i ograniczeń budżetu uczenia. Należy zawsze odmawiać rekomendowania czystego RNN do przebiegów uczenia przekraczających 1B tokenów bez wskazania związanych z tym kompromisów.

## Ćwiczenia

1. **Łatwe.** Weź `rnn_style` z `code/main.py` i zamień skalarny stan ukryty na wektor o długości 64. Zmierz ponownie. O ile wzrasta narzut szeregowy wraz z wymiarem stanu ukrytego?
2. **Średnie.** Zaimplementuj równoległą sumę prefiksów (skan Hillis-Steele) w czystym Pythonie. Sprawdź, czy daje taki sam wynik numeryczny jak skanowanie szeregowe dla długości 1024. Oblicz głębokość.
3. **Trudne.** Przenieś redukcję w stylu uwagi do PyTorch na GPU. Zmierz czas obu wersji, zwiększając długość sekwencji od 64 do 65 536. Narysuj wykres i wyjaśnij kształt krzywej.

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Rekurencja | „RNN są sekwencyjne" | Obliczenie, w którym krok `t` zależy od kroku `t-1`, wymuszając szeregowe wykonanie wzdłuż osi czasu. |
| Głębokość szeregowa | „Jak głęboki jest graf" | Najdłuższy łańcuch zależnych operacji; ogranicza czas pracy nawet na nieograniczonym sprzęcie. |
| Uwaga | „Niech tokeny patrzą na siebie nawzajem" | Suma ważona `sum_j a_ij v_j`, gdzie `a_ij` pochodzi z wyniku podobieństwa między pozycjami i oraz j. |
| Okno kontekstowe | „Ile widzi model" | Liczba pozycji, które warstwa uwagi przyjmuje jako wejście; pamięć skaluje się tutaj kwadratowo. |
| Założenie indukcyjne | „Założenia wbudowane w architekturę" | Przekonanie a priori o kształcie danych; CNN zakładają niezmienność translacji, RNN — aktualność informacji. |
| Model przestrzeni stanów | „RNN z algebrą" | Rekurencja sparametryzowana pod kątem równoległego uczenia przy użyciu ustrukturyzowanych macierzy przestrzeni stanów. |
| Kwadratowe wąskie gardło | „Dlaczego długi kontekst tyle kosztuje" | Pamięć uwagi wynosi `O(N²)` względem długości sekwencji; Flash Attention ukrywa stałe, nie zmienia skalowania. |

## Dalsze czytanie

- [Vaswani i in. (2017). Attention Is All You Need](https://arxiv.org/abs/1706.03762) — artykuł, który wyparł rekurencję z głównego nurtu NLP.
- [Bahdanau, Cho, Bengio (2014). Neural MT by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — miejsce narodzin mechanizmu uwagi, dołączonego wówczas do RNN.
- [Hochreiter, Schmidhuber (1997). Long Short-Term Memory](https://www.bioinf.jku.at/publications/older/2604.pdf) — oryginalna praca o LSTM, dla przypomnienia.
- [Gu, Dao (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752) — nowoczesna, rekurencyjna odpowiedź na transformatory.
