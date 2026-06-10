# Mechanizm uwagi (Attention Mechanism) – kamień milowy

> Dekoder przestaje polegać na skompresowanym podsumowaniu enkodera i uzyskuje bezpośredni dostęp do całej sekwencji źródłowej. Dalszy rozwój NLP to już głównie mechanizm uwagi i kwestie inżynieryjne.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 09 (Modele typu Sequence-to-Sequence)
**Czas:** ~45 minut

## Problem

Lekcja 09 zakończyła się jednoznacznym niepowodzeniem. Model Encoder-Decoder oparty na sieci GRU w zadaniu kopiowania sekwencji osiągnął dokładność rzędu 89% przy długości sekwencji równej 5, lecz przy długości 80 skuteczność spadła do poziomu losowego. Przyczyna ma charakter strukturalny i nie wynika z błędów w treningu: cała informacja przetworzona przez enkoder must zmieścić się w pojedynczym stanie ukrytym o stałym rozmiarze, a dekoder nie ma dostępu do żadnych innych informacji pośrednich.

Bahdanau, Cho i Bengio zaproponowali rozwiązanie tego problemu w 2014 roku. Zamiast przekazywać dekoderowi wyłącznie ostateczny stan ukryty enkodera, zachowujemy stany ukryte dla wszystkich kroków enkodera. W każdym kroku dekodera obliczana jest średnia ważona stanów enkodera. Wagi określają poziom istotności: „jak bardzo dekoder powinien w danym momencie skupić się na pozycji `i` w zdaniu źródłowym?”. Taka dynamicznie wyznaczana średnia ważona stanowi wektor kontekstu, który zmienia się przy generowaniu każdego kolejnego tokenu.

To cała istota tej metody. Kolejne lata przyniosły jej rozwój: w architekturze Transformer zastosowano mechanizm samouwagi (self-attention) w obrębie pojedynczej sekwencji oraz uwzględniono uwagę wielogłową (multi-head attention) przetwarzaną równolegle. Jednak to publikacja z 2014 roku przełamała krytyczne wąskie gardło seq2seq – zrozumienie tego kroku sprawia, że późniejsze innowacje w Transformerach stają się kwestią inżynierii, a nie rewolucją koncepcyjną.

## Pojęcia

![Uwaga Bahdanau: dekoder odpytuje wszystkie stany enkodera](../assets/attention.svg)

W każdym kroku dekodera `t`:

1. Używamy poprzedniego stanu ukrytego dekodera `s_{t-1}` jako **zapytania (query)**.
2. Wyznaczamy miarę dopasowania zapytania do każdego stanu ukrytego enkodera `h_1, ..., h_T` (kluczy/wartości). Otrzymujemy jedną wartość skalarną dla każdej pozycji enkodera.
3. Nakładamy funkcję softmax na uzyskane wyniki, aby otrzymać wagi uwagi (alignment weights) `α_{t,1}, ..., α_{t,T}`, których suma wynosi 1.
4. Obliczamy wektor kontekstu `c_t = Σ α_{t,i} * h_i` jako średnią ważoną stanów enkodera.
5. Dekoder przyjmuje wektor kontekstu `c_t` oraz poprzednio wygenerowany token i wyznacza kolejny stan ukryty oraz token wyjściowy.

Kluczem jest elastyczność średniej ważonej. Kiedy model tłumaczy francuskie słowo „Je” na angielskie „I”, wagi uwagi skupiają się na pozycji słowa „Je”, podczas gdy dla pozostałych wyrazów są bliskie zeru. Podczas tłumaczenia partykuły przeczącej model skieruje uwagę na słowo „ne” lub „pas”. Wektor kontekstu jest obliczany na nowo dla każdego kroku.

## Analiza wymiarów (najczęstsze źródło błędów)

Niezgodność wymiarów tensorów to najczęstszy problem przy pierwszej próbie implementacji mechanizmu uwagi. Przeanalizuj poniższe zestawienie:

| Obiekt | Wymiary | Opis |
|-------|-------|------|
| Ukryte stany enkodera `H` | `(T_enc, d_h)` | Jeśli BiLSTM, to `d_h = 2 * d_hidden` |
| Stan ukryty dekodera `s_{t-1}` | `(d_s,)` | Pojedynczy wektor |
| Wynik punktacji `e_{t,i}` | skalar | Jedna wartość dla każdej pozycji enkodera |
| Waga uwagi `α_{t,i}` | skalar | Po nałożeniu softmax na wszystkie pozycje `i` |
| Wektor kontekstu `c_t` | `(d_h,)` | Taki same wymiary jak stan enkodera |

**Punktacja Bahdanau (uwaga addytywna):** `e_{t,i} = v_α^T * tanh(W_a * s_{t-1} + U_a * h_i)`.

- Wektor `s_{t-1}` ma wymiar `(d_s,)`, a `h_i` ma wymiar `(d_h,)`.
- Macierz `W_a` ma wymiary `(d_attn, d_s)`. Macierz `U_a` ma wymiary `(d_attn, d_h)`.
- Wynik sumowania wewnątrz funkcji `tanh` ma wymiar `(d_attn,)`.
- Wektor `v_α` ma wymiar `(d_attn,)`. Iloczyn skalarny z wektorem `v_α` redukuje wymiar do wartości skalarnej. To jest jedyne zadanie `v_α` – rzutowanie (projekcja) połączonych cech o wymiarowości uwagi na pojedynczy wynik liczbowy.

**Punktacja Luonga (uwaga multiplikatywna) – trzy warianty:**

- `dot`: `e_{t,i} = s_t^T * h_i`. Wymaga tożsamości wymiarów `d_s == d_h` – jest to sztywne ograniczenie, uniemożliwiające np. bezpośrednie użycie dwukierunkowego enkodera.
- `general`: `e_{t,i} = s_t^T * W * h_i`, gdzie macierz `W` ma wymiary `(d_s, d_h)`. Rozwiązuje to problem różnej wymiarowości enkodera i dekodera.
- `concat`: Zbliżony do wariantu Bahdanau. Rzadko stosowany w praktyce z uwagi na wyższy koszt obliczeniowy w porównaniu do `dot` i `general`.

**Ważna różnica w implementacji:** Bahdanau oblicza uwagę na podstawie stanu `s_{t-1}` (stan dekodera *przed* wyznaczeniem kandydata na kolejny token), natomiast Luong wykorzystuje aktualny stan `s_t` (*po* przejściu rekurencyjnym). Pomieszanie tych dwóch konwencji prowadzi do subtelnych błędów w propagacji gradientów, które są niezwykle trudne do wykrycia. Należy bezwzględnie wybrać jeden wariant i konsekwentnie go stosować.

## Implementacja krok po kroku

### Krok 1: Zaimplementowanie uwagi addytywnej (Bahdanau)

```python
import numpy as np

def additive_attention(decoder_state, encoder_states, W_a, U_a, v_a):
    projected_dec = W_a @ decoder_state
    projected_enc = encoder_states @ U_a.T
    combined = np.tanh(projected_enc + projected_dec)
    scores = combined @ v_a
    weights = softmax(scores)
    context = weights @ encoder_states
    return context, weights

def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / e.sum()
```

Zweryfikujmy wymiary tensorów: `encoder_states` ma wymiary `(T_enc, d_h)`. `projected_enc` ma wymiary `(T_enc, d_attn)`. `projected_dec` ma wymiar `(d_attn,)` i jest automatycznie rozszerzany (broadcasting) w trakcie dodawania. `combined` ma wymiary `(T_enc, d_attn)`. Wektor `scores` ma długość `(T_enc,)`, podobnie jak wektor wag `weights` (`(T_enc,)`). Ostateczny wektor kontekstu `context` ma wymiar `(d_h,)`. Kod jest kompletny i poprawny.

### Krok 2: Uproszczone warianty Luonga (dot oraz general)

```python
def dot_attention(decoder_state, encoder_states):
    scores = encoder_states @ decoder_state
    weights = softmax(scores)
    return weights @ encoder_states, weights

def general_attention(decoder_state, encoder_states, W):
    projected = W.T @ decoder_state
    scores = encoder_states @ projected
    weights = softmax(scores)
    return weights @ encoder_states, weights
```

Zwróćmy uwagę, jak zwięzłe są to implementacje (zaledwie trzy linijki). To właśnie prostota obliczeniowa zdecydowała o popularności metody Luonga – oferuje zbliżoną skuteczność przy znacznie mniejszym narzucie kodu i obliczeń.

### Krok 3: Weryfikacja numeryczna

Zdefiniujmy trzy stany enkodera (reprezentujące słowa „cat”, „sat”, „mat”) oraz stan dekodera, który jest semantycznie zbliżony do pierwszego słowa. Rozkład wag uwagi skupi się na pozycji 0. Jeśli zmienimy wektor dekodera tak, by pasował do słowa „mat”, uwaga automatycznie przeniesie się na pozycję 2.

```python
H = np.array([
    [1.0, 0.0, 0.2],
    [0.5, 0.5, 0.1],
    [0.1, 0.9, 0.3],
])

s_close_to_cat = np.array([0.9, 0.1, 0.2])
ctx, w = dot_attention(s_close_to_cat, H)
print("weights:", w.round(3))
```

```
weights: [0.464 0.305 0.231]
```

Wartość dla pierwszego stanu jest najwyższa. Zmodyfikowanie stanu dekodera tak, by odpowiadał trzeciej linii macierzy `H`, przeniesie maksimum rozkładu wag uwagi na pozycję 2. Pokazuje to, jak uwaga precyzyjnie wyrównuje (aligns) semantykę sekwencji.

### Krok 4: Przejście do modeli Transformer (Q, K, V)

Możemy zmapować klasyczne pojęcia na format Query (Q), Key (K) i Value (V):

- **Query (Zapytanie):** Stan dekodera `s_{t-1}` (wektor wyszukujący).
- **Key (Klucz):** Stany enkodera (względem których obliczamy dopasowanie).
- **Value (Wartość):** Stany enkodera (które uśredniamy za pomocą wag uwagi).

W klasycznym mechanizmie uwagi klucze (Keys) i wartości (Values) reprezentują te same wektory (stany enkodera). Mechanizm samouwagi (self-attention) rozdziela je, mapując sekwencję na samą siebie za pomocą różnych wyuczonych macierzy projekcji dla K i V. Uwaga wielogłowa (multi-head attention) wykonuje te operacje równoleglych w niezależnych podprzestrzeniach. Ostatecznie modele Transformer eliminują rekurencję (RNN), opierając całą architekturę na blokach uwagi.

## Zastosowanie w praktyce

Biblioteki PyTorch oraz TensorFlow oferują zoptymalizowane implementacje warstw uwagi.

```python
import torch
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=128, num_heads=8, batch_first=True)
query = torch.randn(2, 5, 128)
key = torch.randn(2, 10, 128)
value = torch.randn(2, 10, 128)

output, weights = mha(query, key, value)
print(output.shape, weights.shape)
```

```
torch.Size([2, 5, 128]) torch.Size([2, 5, 10])
```

W ten sposób definiuje się warstwę uwagi w Transformerze. Przekazujemy paczkę (batch) zapytań o długości 5, paczkę kluczy/wartości o długości 10, przy wymiarowości wektorów równej 128 oraz 8 głowicach uwagi. Wyjście `output` zawiera zaktualizowane, kontekstowe reprezentacje, a tensor `weights` to macierz uwagi o wymiarach 5x10, którą można łatwo poddać wizualizacji.

### Gdzie klasyczny mechanizm uwagi wciąż ma zastosowanie

- **Dydaktyka:** Jednogłowicowy, jednowarstwowy wariant oparty na sieci RNN pozwala na bezpośrednią analizę i wizualizację pojęć teoretycznych.
- **Systemy o małej skali:** Lekkie potoki sekwencyjne na urządzeniach o słabej specyfikacji sprzętowej.
- **Analiza publikacji naukowych z lat 2014-2017:** Znajomość różnic między modelami Bahdanau i Luonga jest niezbędna do poprawnej interpretacji ówczesnych prac.
- **Analiza struktur wyrównania (alignment) w tłumaczeniu maszynowym:** Macierze wag uwagi stanowią główne narzędzie objaśniające decyzje modeli.

### Wizualizacja wag uwagi jako wyjaśnialność (Wyjaśnienie pułapki)

Wizualizacja wag uwagi bywa intuicyjna – wartości sumują się do 1.0, można je przedstawić na wykresie, a wyższe wartości sugerują, na czym skupił się model. Jest to bardzo popularna metoda prezentacji wyników.

Niestety, ich interpretacja nie jest jednoznaczna. Jain i Wallace (2019) wykazali w swojej publikacji „Attention is not Explanation”, że rozkłady wag uwagi można poddać permutacji lub zastąpić zupełnie innymi wartościami bez zmiany ostatecznej predykcji modelu. Z tego powodu nigdy nie należy traktować wag uwagi jako bezpośredniego dowodu na logiczne uzasadnienie decyzji modelu bez przeprowadzenia testów ablacyjnych lub analizy kontrfaktycznej.

## Szablon do wdrożenia

Zapisz go jako `outputs/prompt-attention-shapes.md`:

```markdown
---
name: attention-shapes
description: Diagnozuj i naprawiaj błędy wymiarowości tensorów w implementacjach mechanizmu uwagi.
phase: 5
lesson: 10
---

Jesteś doradcą ds. wdrażania i optymalizacji mechanizmów uwagi w modelach NLP. Twoim zadaniem jest zidentyfikowanie błędów w wymiarach tensorów na podstawie kodu. W wyniku podaj:

1. Wskazanie tensora/macierzy o niepoprawnym kształcie.
2. Prawidłowy docelowy wymiar tensora wyrażony przez zmienne (d_s, d_h, d_attn, T_enc, T_dec, batch_size).
3. Jednoliniową instrukcję naprawy błędu (np. transpozycja, zmiana kształtu za pomocą reshape lub dodanie warstwy projekcji liniowej).
4. Przykładowy test asercji (assert) sprawdzający poprawność kształtów wyjściowych enkodera i wag (np. `assert output.shape == (batch, T_dec, d_h)` oraz `assert weights.shape == (batch, T_dec, T_enc)` i upewnienie się, że suma wag w wymiarze sekwencji jest bliska 1.0).

Odmów rekomendowania rozwiązań, które ukrywają błędy wymiarów poprzez automatyczny rozszerzanie (broadcasting). Błędy maskowane przez broadcasting ujawniają się dopiero później w postaci cichego spadku skuteczności modelu, co stanowi najtrudniejszy do zdiagnozowania typ błędów w mechanizmach uwagi.

W przypadku niejasności w modelu Bahdanau pilnuj, by stanem wejściowym dekodera był `s_{t-1}` (stan przed wykonaniem kroku). W modelu Luonga musi to być `s_t` (stan po kroku). W przypadku uwagi typu dot-product najczęstszym błędem początkowym jest niezgodność wymiarów między zapytaniem (Query) a kluczem (Key).
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj maskowanie (masking) funkcji `softmax` tak, aby tokeny dopełnienia (padding) w enkoderze otrzymały zerową wagę uwagi. Przetestuj rozwiązanie na paczce danych z sekwencjami o różnej długości.
2. **Średnie.** Dodaj mechanizm uwagi wielogłowej (multi-head attention) do wariantu Luonga `general`. Podziel przestrzeń `d_h` na `n_heads` podprzestrzeni, oblicz wagi uwagi dla każdej głowicy niezależnie, a następnie połącz (skonkatynuj) wyniki. Upewnij się, że przypadek z jedną głowicą daje wyniki tożsame z wcześniejszą implementacją.
3. **Trudne.** Wytrenuj model Encoder-Decoder z siecią GRU i mechanizmem uwagi Bahdanau w zadaniu kopiowania sekwencji (lekcja 09). Wykreśl wykres dokładności (accuracy) w zależności od długości sekwencji wejściowej. Porównaj wyniki z modelem bazowym bez mechanizmu uwagi. Zaobserwujesz, że różnica na korzyść modelu z uwagą rośnie wraz z długością zdań, co empirycznie potwierdza wyeliminowanie problemu wąskiego gardła.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Mechanizm uwagi | Skupienie wzroku | Średnia ważona z wektorów wartości (Values), gdzie wagi są wyznaczane na podstawie miary podobieństwa zapytania (Query) do kluczy (Keys). |
| Zapytanie, klucz, wartość (Q, K, V) | Elementy uwagi | Trzy reprezentacje wektorowe: Q (Query) reprezentuje aktualny stan, K (Key) służy do wyznaczenia miary dopasowania, a V (Value) niesie informację merytoryczną. |
| Uwaga addytywna | Model Bahdanau | Metoda punktacji oparta na sieci jednowarstwowej: `v^T * tanh(W * q + U * k)`. |
| Uwaga multiplikatywna | Model Luonga | Metoda punktacji oparta na iloczynie skalarnym: `q^T * k` lub `q^T * W * k`. Wydajniejsza obliczeniowo, oferująca zbliżoną skuteczność. |
| Macierz uwagi (alignment matrix) | Wizualizacja powiązań | Dwuwymiarowa macierz wag uwagi o wymiarach `(T_dec, T_enc)` obrazująca relacje składniowe, na których skupiał się model w poszczególnych krokach. |

## Dalsze czytanie

- [Bahdanau, D., Cho, K., Bengio, Y. (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — oryginalna publikacja wprowadzająca pojęcie uwagi addytywnej.
- [Luong, M.-T., Pham, H., Manning, C. D. (2015). Effective Approaches to Attention-based Neural Machine Translation](https://arxiv.org/abs/1508.04025) — szczegółowe porównanie wariantów uwagi multiplikatywnej.
- [Jain, S., Wallace, B. C. (2019). Attention is not Explanation](https://arxiv.org/abs/1902.10186) — krytyczna analiza i ograniczenia interpretacyjne wag uwagi.
- [Dive into Deep Learning - Bahdanau Attention](https://d2l.ai/chapter_attention-mechanisms-and-transformers/bahdanau-attention.html) — praktyczny samouczek implementacji kodu w PyTorch.
