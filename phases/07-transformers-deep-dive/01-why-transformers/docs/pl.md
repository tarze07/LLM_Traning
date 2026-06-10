# Dlaczego transformatory — problemy z RNN

> RNN przetwarzają tokeny pojedynczo. Transformatory przetwarzają wszystkie żetony na raz. Ten pojedynczy projekt architektoniczny zmienił każdą krzywą skalowania w głębokim uczeniu się po 2017 roku.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 3 (rdzeń głębokiego uczenia się), faza 5 · 09 (sekwencja po sekwencji), faza 5 · 10 (mechanizm uwagi)
**Czas:** ~45 minut

## Problem

Przed 2017 rokiem każdy najnowocześniejszy model sekwencji na świecie – język, tłumaczenie, mowa – był powtarzającą się siecią neuronową. LSTM i GRU przez pół dekady wygrywały testy porównawcze odpowiedników tłumaczeń ImageNet. Były jedynym narzędziem, jakie ktoś miał.

Mieli trzy fatalne słabości. Obliczenia sekwencyjne oznaczały, że nie można było wykonywać operacji równoległych wzdłuż osi czasu: token `t+1` potrzebuje stanu ukrytego z tokena `t`. Sekwencja 1024 tokenów oznaczała 1024 kroki szeregowe procesora graficznego, który może wykonać 1 000 000 operacji zmiennoprzecinkowych na cykl. Czas zegara szkoleniowego skalowany liniowo z długością sekwencji na sprzęcie zaprojektowanym pod kątem równoległości.

Zanikające gradienty oznaczały, że informacja znajdująca się 50 tokenów wstecz została już skompresowana poprzez 50 nieliniowości. Bramkowane jednostki rekurencyjne (LSTM, GRU) złagodziły ucisk, ale nigdy go nie wyeliminowały. Zależności dalekosiężne – „książka, którą przeczytałem latem ubiegłego roku w samolocie do Kioto, to…” – regularnie zawodziły.

Stany ukryte o stałej szerokości oznaczały, że koder umieścił całą sekwencję źródłową w jednym wektorze, zanim dekoder cokolwiek zobaczył. Nie ma znaczenia, czy źródłem jest 5 żetonów, czy 500; wąskie gardło ma ten sam kształt.

W artykule z 2017 r. „Attention Is All You Need” zaproponowano radykalne rozwiązanie: całkowite wyeliminowanie nawrotów choroby. Niech każda pozycja odpowiada równolegle każdej innej pozycji. Trenuj jedno duże mnożenie macierzy zamiast 1024 kolejnych.

Rezultatem będzie dominacja w każdej modalności do 2026 r. Język (GPT-5, Claude 4, Llama 4), wzrok (ViT, DINOv2, SAM 3), dźwięk (Whisper), biologia (AlphaFold 3), robotyka (RT-2). Ten sam blok, różne wejścia.

## Koncepcja

![Obliczenia sekwencyjne RNN a uwaga równoległa transformatora](../assets/rnn-vs-transformer.svg)

**Nawrót jako wąskie gardło.** RNN oblicza `h_t = f(h_{t-1}, x_t)`. Każdy krok zależy od poprzedniego. Nie można obliczyć `h_5` przed `h_4`. W przypadku nowoczesnych procesorów graficznych z ponad 10 000 równoległych rdzeni powoduje to marnowanie 99% krzemu w długiej sekwencji.

**Uwaga jako transmisja.** Samouwaga oblicza `output_i = sum_j(a_ij * v_j)` dla każdej pary `(i, j)` jednocześnie. Cała macierz uwagi N×N wypełnia jeden matmul wsadowy. Żaden krok nie zależy od drugiego. Procesory graficzne to uwielbiają.

**Przyspieszenie nie jest stałe.** Jest to różnica pomiędzy głębokością szeregową `O(N)` i głębokością szeregową `O(1)`. W praktyce transformatory uczą się 5–10 razy szybciej na epokę na dopasowanym sprzęcie przy N=512, a różnica zwiększa się wraz z długością sekwencji, aż dojdziesz do ściany pamięci uwagi `O(N²)` (którą Flash Attention później naprawił — zobacz Lekcja 12).

**Ile kosztują transformatory.** Skala pamięci uwagi wynosi `O(N²)`. W kontekście 2K w porządku. W kontekście 128 KB potrzebne są przesuwane okna, ekstrapolacja RoPE, kafelkowanie Flash Attention lub warianty uwagi liniowej. Nawrót wynosił `O(N)` zarówno pod względem czasu, jak i pamięci; transformatory wymieniają czas na pamięć, a następnie odzyskują go poprzez równoległość.

**Indukcyjne przesunięcie obciążenia.** RNN zakładają lokalność i niedawność. Transformatory niczego nie zakładają – każda para jest kandydatem do uwagi. Dlatego też transformatory potrzebują więcej danych, aby dobrze trenować, ale gdy już je uzyskają, skalują się dalej. Chinchilla (2022) sformalizowała to: mając wystarczającą liczbę tokenów, transformator zawsze pokonuje RNN o równej liczbie parametrów.

## Zbuduj to

Nie ma tu żadnej sieci neuronowej — symulujemy numerycznie wąskie gardło w rdzeniu, abyś wyczuł lukę na swoim laptopie.

### Krok 1: zmierz głębokość seryjną

Zobacz `code/main.py`. Budujemy dwie funkcje. Koduje się sekwencję jako łańcuch dodatków (seryjny, jak RNN). Koduje się to jako redukcję równoległą (rozgłaszanie, jak uwaga). Ta sama matematyka, inny wykres zależności.

```python
def rnn_style(xs):
    h = 0.0
    for x in xs:
        h = 0.9 * h + x   # can't parallelize: h depends on previous h
    return h

def attention_style(xs):
    return sum(xs) / len(xs)  # every x is independent
```

Obydwa mierzymy czasowo na sekwencjach do 100 000 elementów. Wersja RNN to O(N) i pojedynczy potok procesora. Nawet w czystym Pythonie redukcja stylu uwagi jest lepsza na długości ≥ 1000, ponieważ `sum()` Pythona jest zaimplementowany w C i iteruje bez narzutu interpretera na krok.

### Krok 2: policz operacje teoretyczne

Obydwa algorytmy wykonują N dodań. Różnica polega na *głębokości zależności*: ile operacji musi nastąpić sekwencyjnie, zanim będzie można rozpocząć następną. Głębokość RNN = N. Głębokość uwagi = log(N) w przypadku redukcji drzewa lub 1 w przypadku skanowania równoległego. Głębokość, a nie liczba operacji, decyduje o czasie GPU.

### Krok 3: skalowanie empiryczne na długich sekwencjach

Drukujemy tabelę taktowania, która uwidacznia przerwę O(N). Na laptopie Mac z 2026 r. sekwencje poniżej 1000 elementów są zbyt szybkie, aby je zmierzyć. Sekwencje 100 000 pokazują czysty skan liniowy. Skaluj to do transformatora o pojemności 16 384 tokenów i 12-warstwowego odpowiednika LSTM, a zobaczysz, dlaczego zegar ścienny do trenowania był blokerem w 2016 roku.

## Użyj tego

Kiedy nadal wybrać RNN w 2026 r.:

| Sytuacja | Wybierz |
|----------|------|
| Wnioskowanie strumieniowe, jeden token na raz, stała pamięć | RNN lub model przestrzeni stanów (Mamba, RWKV) |
| Bardzo długie sekwencje (> 1M tokenów), w których eksploduje pamięć uwagi | Uwaga liniowa, Mamba 2, Hiena |
| Urządzenie brzegowe bez akceleratora Matmul | RNN z możliwością rozdzielenia wgłębnego nadal wygrywa na FLOP/wat |
| Wszystko inne (szkolenie, wnioskowanie wsadowe, kontekst do 128 KB) | Transformator |

Modele przestrzeni stanów (SSM), takie jak Mamba, to w zasadzie RNN ze strukturalną parametryzacją, która zapewnia im to, co najlepsze z obu: `O(N)` pamięć skanująca, uczenie równoległe poprzez skanowanie selektywne. Odzyskują 90% jakości transformatora przy lepszym skalowaniu w długim kontekście. W 2026 r. większość pionierskich laboratoriów szkoli hybrydowe modele SSM + transformator (np. Jamba, Samba) — powtarzalność nie jest martwa, jest jej elementem.

## Wyślij to

Zobacz `outputs/skill-architecture-picker.md`. Umiejętność wybiera architekturę dla nowego problemu sekwencji, biorąc pod uwagę długość, przepustowość i ograniczenia budżetu szkoleniowego. Zawsze należy odmawiać rekomendowania czystego RNN do przebiegów szkoleniowych powyżej tokenów 1B bez podawania kompromisu.

## Ćwiczenia

1. **Łatwo.** Weź `rnn_style` z `code/main.py` i zamień skalarny stan ukryty na wektor stanów ukrytych o długości 64. Zmierz ponownie. O ile wzrasta narzut szeregowy w przypadku wymiaru stanu ukrytego?
2. **Średni.** Zaimplementuj równoległą sumę prefiksów (skan Hillis-Steele) w czystym Pythonie. Sprawdź, czy daje taki sam wynik numeryczny jak skanowanie szeregowe na długości 1024. Policz głębokość.
3. **Trudne.** Przenieś redukcję stylu uwagi do PyTorch na GPU. Czas obu, przesuwając długość sekwencji z 64 do 65 536. Narysuj i wyjaśnij kształt krzywej.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Nawrót | „RNN są sekwencyjne” | Obliczenie, w którym krok `t` zależy od kroku `t-1`, wymuszając wykonanie szeregowe wzdłuż osi czasu. |
| Głębokość seryjna | „Jak głęboki jest wykres” | Najdłuższy łańcuch zależnych operacji; ogranicza zegar ścienny nawet na nieskończonym sprzęcie. |
| Uwaga | „Niech tokeny patrzą na siebie” | Suma ważona `sum_j a_ij v_j` gdzie `a_ij` pochodzi z wyniku podobieństwa między pozycjami i oraz j. |
| Okno kontekstowe | „Ile widzi modelka” | Liczba pozycji, które warstwa uwagi może przyjąć jako dane wejściowe; tutaj kwadratowa skala kosztów pamięci. |
| Odchylenie indukcyjne | „Założenia wpisane w architekturę” | Wcześniej o tym, jak wyglądają dane; CNN zakładają niezmienność tłumaczenia, RNN zakładają aktualność. |
| Model przestrzeni stanów | „RNN z algebrą” | Powtarzanie sparametryzowane pod kątem uczenia równoległego za pomocą ustrukturyzowanych macierzy przestrzeni stanów. |
| Kwadratowe wąskie gardło | „Dlaczego kontekst tyle kosztuje” | Pamięć uwagi = `O(N²)` w długości sekwencji; Flash Attention ukrywa stałe, a nie skalowanie. |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz](https://arxiv.org/abs/1706.03762) — artykuł, który zabił nawroty w głównym nurcie NLP.
- [Bahdanau, Cho, Bengio (2014). Neural MT autorstwa Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) – miejsce, w którym narodziła się uwaga, przykręcone do RNN.
- [Hochreiter, Schmidhuber (1997). Długa pamięć krótkotrwała] (https://www.bioinf.jku.at/publications/older/2604.pdf) — dla przypomnienia, oryginalna praca LSTM.
- [Gu, Dao (2023). Mamba: Modelowanie sekwencji w czasie liniowym z selektywnymi przestrzeniami stanów](https://arxiv.org/abs/2312.00752) — nowoczesna, rekurencyjna odpowiedź na transformatory.