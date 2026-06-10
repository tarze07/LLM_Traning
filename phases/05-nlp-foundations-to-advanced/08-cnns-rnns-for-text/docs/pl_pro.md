# Sieci CNN i RNN w przetwarzaniu tekstu

> Sploty (CNN) uczą się n-gramów. Sieci rekurencyjne (RNN) pamiętają kontekst. Obie te architektury zostały w dużej mierze zastąpione mechanizmem uwagi (attention). Niemniej jednak obie wciąż mają znaczenie w systemach o ograniczonych zasobach sprzętowych.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · Lekcja 11 (Wprowadzenie do PyTorch), Faza 5 · Lekcja 03 (Embeddingi słów), Faza 4 · Lekcja 02 (Sploty od podstaw)
**Czas:** ~75 minut

## Problem

Reprezentacje TF-IDF i klasyczny Word2Vec (w ujęciu uśrednionym) tworzą płaskie wektory ignorujące kolejność słów. Zbudowany na nich klasyfikator nie odróżni zdania `dog bites man` (pies gryzie człowieka) od `man bites dog` (człowiek gryzie psa). Kolejność słów bywa kluczowa.

Dwie rodziny architektur głębokich sieci neuronowych wypełniły tę lukę przed pojawieniem się modeli typu Transformer.

1. **Sieci splotowe dla tekstu (TextCNN):** Stosują sploty jednowymiarowe (1D) nad sekwencjami embeddingów słów. Filtr o szerokości (kernel size) równej 3 działa jak adaptacyjny detektor trigramów – analizuje trzy sąsiednie słowa i generuje dla nich wartość aktywacji. Stosując filtry o różnych szerokościach (np. 2, 3, 4, 5), model wykrywa wzorce o różnej skali. Warstwa max pooling agreguje wyniki do wektora o stałej długości. Jest to model szybki i w pełni równoległy.
2. **Sieci rekurencyjne (RNN, LSTM, GRU):** Przetwarzają tokeny sekwencyjnie, krok po kroku, aktualizując stan ukryty (hidden state), który przenosi informacje o dotychczasowym kontekście. Obsługują wejścia o zmiennej długości. Architektury te zdominowały modelowanie sekwencyjne w latach 2014-2017, aż do przełomu związanego z mechanizmem uwagi (attention).

W tej lekcji zaimplementujemy oba te rozwiązania oraz omówimy ograniczenia, które doprowadziły do powstania mechanizmu uwagi.

## Pojęcia

**TextCNN** (Kim, 2014): Tokeny wejściowe są mapowane na embeddingi. Splot 1D o szerokości (rozmiarze jądra) `k` przesuwa filtr nad kolejnymi `k`-gramami wektorów słów, generując mapę cech (feature map). Warstwa global max pooling wybiera najwyższą wartość aktywacji z tej mapy. Wyniki z filtrów o różnych szerokościach są następnie łączone (konkatenowane) i przekazywane do warstwy wyjściowej (głowicy klasyfikatora).

Dlaczego to działa? Każdy filtr uczy się rozpoznawania określonego wzorca n-gramowego. Operacja max pooling ignoruje pozycję słów w tekście – dzięki temu obecność frazy „nie dobrze” aktywuje ten sam detektor niezależnie od tego, czy występuje ona na początku, czy w środku dokumentu. Zastosowanie filtrów o trzech różnych szerokościach (np. po 100 filtrów dla każdej szerokości) daje łącznie 300 cech. Trening przebiega w pełni równolegle, ponieważ nie ma tu zależności czasowych między krokami.

**RNN:** W każdym kroku czasowym `t` stan ukryty jest aktualizowany według wzoru `h_t = f(W * x_t + U * h_{t-1} + b)`. Macierze wag `W`, `U` oraz wektor obciążenia `b` są współdzielone dla wszystkich kroków. Stan ukryty w ostatnim kroku `T` stanowi skompresowaną reprezentację całej sekwencji. Do celów klasyfikacji stosuje się agregację (pooling) stanów ukrytych `h_1 ... h_T` (poprzez wyznaczenie wartości maksymalnej, średniej lub pobranie ostatniego stanu).

Klasyczne sieci RNN cierpią na problem zanikającego gradientu (vanishing gradient). **LSTM** rozwiązuje ten problem, wprowadzając mechanizm bramek (bramka zapominania, wejściowa i wyjściowa) oraz stan komórki (cell state), co pozwala na stabilny przepływ gradientów w długich sekwencjach. Architektura **GRU** upraszcza strukturę LSTM do dwóch bramek (aktualizacji i resetowania), oferując zbliżoną skuteczność przy mniejszej liczbie parametrów.

**Dwukierunkowe sieci RNN (Bidirectional RNN)** uruchamiają dwa niezależne procesy rekurencyjne – jeden przetwarzający sekwencję w przód (od lewej do prawej), a drugi w tył (od prawej do lewej) – i łączą ich stany ukryte. Dzięki temu reprezentacja każdego tokenu uwzględnia zarówno kontekst lewostronny, jak i prawostronny, co jest kluczowe np. w zadaniach tagowania i NER.

## Implementacja krok po kroku

### Krok 1: Model TextCNN w PyTorch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class TextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, n_classes, filter_widths=(2, 3, 4), n_filters=64, dropout=0.3):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, n_filters, kernel_size=k)
            for k in filter_widths
        ])
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(n_filters * len(filter_widths), n_classes)

    def forward(self, token_ids):
        x = self.embed(token_ids).transpose(1, 2)
        pooled = []
        for conv in self.convs:
            c = F.relu(conv(x))
            p = F.max_pool1d(c, c.size(2)).squeeze(2)
            pooled.append(p)
        h = torch.cat(pooled, dim=1)
        return self.fc(self.dropout(h))
```

Transpozycja `transpose(1, 2)` zmienia wymiary tensora z `[batch, seq_len, embed_dim]` na `[batch, embed_dim, seq_len]`. Wynika to z faktu, że `nn.Conv1d` oczekuje osi embeddingu jako osi kanałów (in_channels). Wynikowy wektor po warstwie pooling ma stałą długość, niezależnie od długości tekstu wejściowego.

### Krok 2: Klasyfikator LSTM

```python
class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, n_classes, bidirectional=True, dropout=0.3):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=bidirectional)
        factor = 2 if bidirectional else 1
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * factor, n_classes)

    def forward(self, token_ids):
        x = self.embed(token_ids)
        out, _ = self.lstm(x)
        pooled = out.max(dim=1).values
        return self.fc(self.dropout(pooled))
```

W tym wariancie stosujemy operację max pooling nad całą sekwencją stanów ukrytych, zamiast pobierać tylko ostatni stan ukryty. W zadaniach klasyfikacji tekstu max pooling zazwyczaj daje lepsze rezultaty, ponieważ w bardzo długich sekwencjach informacja z początkowych kroków ulega zatraceniu w ostatnim stanie ukrytym (zdominowanym przez końcowe wyrazy zdania).

### Krok 3: Problem zanikającego gradientu (intuicja)

Klasyczna sieć RNN bez mechanizmu bramek nie jest w stanie nauczyć się długodystansowych zależności. Rozważmy uproszczone zadanie: model ma określić, czy token `A` wystąpił w tekście. Jeśli token `A` znajduje się na pierwszej pozycji, a cała sekwencja ma długość 100 kroków, gradient funkcji straty musi zostać przetransferowany wstecz przez 99 mnożeń wag rekurencyjnych. Jeśli waga ta jest nieznacznie mniejsza od 1, gradient szybko dąży do zera (zanika). Jeśli jest większa od 1, gradient rośnie niekontrolowanie (eksploduje).

```python
def vanishing_gradient_sim(seq_len, recurrent_weight=0.9):
    import math
    return math.pow(recurrent_weight, seq_len)

# Przy wadze recurrent_weight=0.9 i 100 krokach czasowych:
# 0.9 ^ 100 ≈ 2.7e-5
# Gradient płynący z kroku 100 do kroku 1 jest praktycznie zerowy.
```

Modele LSTM rozwiązują ten problem za pomocą stanu komórki, który płynie przez sieć w oparciu o operacje głównie addytywne (bramka zapominania kontroluje ten przepływ mnożeniem, ale gradienty mogą swobodnie przemieszczać się wzdłuż tej ścieżki). Sieci GRU działają analogicznie przy mniejszej liczbie parametrów. Obie architektury zapewniają stabilne warunki treningu dla sekwencji o długościach przekraczających 100 kroków.

### Krok 4: Dlaczego to wciąż było niewystarczające

Nawet architektura LSTM nie rozwiązała trzech fundamentalnych problemów:

1. **Sekwencyjne wąskie gardło (sequential bottleneck):** Trening RNN na sekwencji o długości 1000 tokenów wymaga wykonania 1000 sekwencyjnych kroków w przód i w tył. Procesu tego nie da się zrównoleglić w wymiarze czasowym na kartach GPU.
2. **Stały rozmiar wektora kontekstu:** W architekturach typu Encoder-Decoder dekoder ma dostęp jedynie do końcowego stanu ukrytego enkodera, który musi skompresować informacje z całego tekstu wejściowego. Przy długich tekstach nieuchronnie prowadzi to do utraty kluczowych szczegółów (szczegółowo omówimy to w lekcji 09).
3. **Granica zasięgu zależności:** Choć LSTM radzą sobie znacznie lepiej niż klasyczne sieci RNN, wciąż wykazują trudności z precyzyjnym przekazywaniem informacji na dystansach przekraczających 200 tokenów.

Wprowadzenie mechanizmu uwagi (attention) rozwiązało wszystkie te problemy. Modele Transformer całkowicie zrezygnowały z rekurencji. Szczegóły przedstawimy w przełomowej lekcji 10.

## Zastosowanie w praktyce

Zaimplementowane w PyTorch moduły `nn.LSTM`, `nn.GRU` oraz `nn.Conv1d` są zoptymalizowanymi rozwiązaniami gotowymi do użycia na produkcji.

Dzięki bibliotece Hugging Face możemy łatwo wykorzystać gotowe, zamrożone reprezentacje jako warstwę wejściową (embeddingi) naszego modelu:

```python
from transformers import AutoModel

encoder = AutoModel.from_pretrained("bert-base-uncased")
for param in encoder.parameters():
    param.requires_grad = False

class BertCNN(nn.Module):
    def __init__(self, n_classes, filter_widths=(2, 3, 4), n_filters=64):
        super().__init__()
        self.encoder = encoder
        self.convs = nn.ModuleList([nn.Conv1d(768, n_filters, kernel_size=k) for k in filter_widths])
        self.fc = nn.Linear(n_filters * len(filter_widths), n_classes)

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            out = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        x = out.transpose(1, 2)
        pooled = [F.max_pool1d(F.relu(conv(x)), kernel_size=conv(x).size(2)).squeeze(2) for conv in self.convs]
        return self.fc(torch.cat(pooled, dim=1))
```

Lista kontrolna doboru architektury:

- **Wdrożenia typu Edge (na urządzeniach użytkowników):** Model TextCNN połączony ze statycznymi embeddingami GloVe jest od 10 do 100 razy mniejszy niż jakikolwiek model Transformer. Jeśli wdrażasz rozwiązanie na smartfonach o ograniczonej pamięci, jest to optymalny wybór technologiczny.
- **Klasyfikacja strumieniowa (real-time):** Sieci RNN przetwarzają tekst token po tokenie, podczas gdy Transformery zazwyczaj wymagają znajomości całej sekwencji. Dla danych wejściowych napływających w czasie rzeczywistym sieci LSTM wciąż stanowią bardzo mocne rozwiązanie.
- **Szybkie prototypowanie (baselines):** Wytrenowanie prostego modelu TextCNN na procesorze (CPU) zajmuje kilka minut, co ułatwia szybkie przetestowanie nowej hipotezy.
- **Klasyfikacja sekwencji przy małej ilości danych:** Model BiLSTM-CRF (lekcja 06) pozostaje sprawdzonym standardem produkcyjnym w zadaniach NER, gdy dysponujemy zbiorem od 1 tys. do 10 tys. etykietowanych zdań.

W pozostałych scenariuszach optymalnym wyborem są modele oparte na architekturze Transformer.

## Szablon do wdrożenia

Zapisz go jako `outputs/prompt-text-encoder-picker.md`:

```markdown
---
name: text-encoder-picker
description: Wybierz architekturę kodera tekstu dla zadanego zestawu ograniczeń.
phase: 5
lesson: 08
---

Jesteś doradcą ds. doboru architektury modeli głębokiego uczenia w NLP. Na podstawie opisu ograniczeń projektowych (typ zadania, objętość danych, budżet czasowy opóźnień, docelowe środowisko sprzętowe, dostępne zasoby obliczeniowe) określ:

1. Rekomendowaną architekturę enkodera: TextCNN, BiLSTM, BiLSTM-CRF, dostrojenie (fine-tuning) modelu typu Transformer lub wariant hybrydowy (zamrożony Transformer + lekka głowica klasyfikatora).
2. Wybór embeddingów wejściowych: losowa inicjalizacja, zamrożone wektory statyczne (GloVe, fastText) lub kontekstowe reprezentacje z modelu Transformer.
3. Parametry treningowe (w 5 punktach): wybór optymalizatora, współczynnik uczenia (learning rate), rozmiar paczki (batch size), liczba epok oraz metody regularyzacji.
4. Jeden kluczowy wskaźnik do monitorowania po wdrożeniu: dla modeli RNN/CNN – analiza skuteczności modelu w zależności od długości sekwencji (brak mechanizmu uwagi sprawia, że modele te gubią długie zależności składniowe); dla modeli Transformer – ryzyko przeuczenia lub niestabilności treningu przy zbyt wysokim współczynniku uczenia (monitorowanie krzywej straty).

Odmów rekomendowania dostrajania modeli Transformer, gdy zbiór treningowy liczy mniej niż 500 etykietowanych przykładów (chyba że wykazano, że prostsze modele typu TextCNN lub BiLSTM osiągnęły już swoje limity wydajności). Oznacz wdrożenia na urządzeniach końcowych (edge) jako bezwzględnie wymagające optymalizacji architektury (resource-constrained design).
```

## Ćwiczenia

1. **Łatwe.** Wytrenuj model TextCNN na syntetycznym zbiorze 3-klasowym. Porównaj skuteczność (F1-score) wariantu wykorzystującego filtry o różnych szerokościach (np. 2, 3, 4) z wariantem o stałej szerokości filtra (np. tylko 3).
2. **Średnie.** Zaimplementuj i porównaj w klasyfikatorze LSTM trzy metody agregacji stanów ukrytych: max pooling, average pooling oraz wybór ostatniego stanu ukrytego. Przetestuj ich skuteczność na wybranym zbiorze danych i uzasadnij wyniki.
3. **Trudne.** Połącz wiedzę z lekcji 06 oraz bieżącej, by zbudować kompletny tagger NER oparty na architekturze BiLSTM-CRF. Wytrenuj go na zbiorze CoNLL-2003 i porównaj uzyskaną skuteczność (F1-score), czas treningu oraz zużycie pamięci z klasycznym CRF oraz dostrojonym modelem DistilBERT.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| TextCNN | Sploty dla tekstu | Architektura oparta na splotach jednowymiarowych (1D) nad embeddingami słów z warstwą global max pooling (zaproponowana przez Y. Kima w 2014 r.). |
| RNN | Sieć rekurencyjna | Model sekwencyjny aktualizujący stan ukryty w każdym kroku czasowym: `h_t = f(W * x_t + U * h_{t-1})`. |
| LSTM | Sieć z pamięcią długo-krótkoterminową | Wariant RNN wyposażony w bramki (wejściową, wyjściową, zapominania) oraz stan komórki, co eliminuje problem zanikającego gradientu. |
| GRU | Rekurencyjna jednostka bramkowana | Uproszczona wersja LSTM posiadająca tylko dwie bramki. Oferuje podobną dokładność przy mniejszej liczbie parametrów. |
| Dwukierunkowość (Bidirectional) | Przetwarzanie dwukierunkowe | Połączenie dwóch warstw rekurencyjnych (jedna przetwarza tekst w przód, druga w tył). Zapewnia pełną znajomość kontekstu dla każdego słowa. |
| Zanikający gradient | Zanik sygnału wstecznego | Problem w klasycznych sieciach RNN, gdzie wielokrotne mnożenie gradientów przez wagi o module mniejszym od 1 sprawia, że poprawki dla początkowych kroków czasowych dążą do zera. |

## Dalsze czytanie

- [Kim, Y. (2014). Convolutional Neural Networks for Sentence Classification](https://arxiv.org/abs/1408.5882) — klasyczna publikacja wprowadzająca model TextCNN.
- [Hochreiter, S., Schmidhuber, J. (1997). Long Short-Term Memory](https://www.bioinf.jku.at/publications/older/2604.pdf) — artykuł naukowy definiujący architekturę LSTM.
- [Olah, C. (2015). Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — legendarny artykuł blogowy z przejrzystymi schematami działania bramkowania.
