# CNN i RNN dla tekstu

> Sploty uczą się n-gramów. Nawroty pamiętają. Obydwa są zastąpione przez uwagę. Obydwa nadal mają znaczenie na ograniczonym sprzęcie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 11 (Wprowadzenie do PyTorch), Faza 5 · 03 (Osadzanie słów), Faza 4 · 02 (Zwoje od podstaw)
**Czas:** ~75 minut

## Problem

TF-IDF i Word2Vec stworzyły płaskie wektory, które ignorowały kolejność słów. Zbudowany na nich klasyfikator nie potrafił odróżnić `dog bites man` od `man bites dog`. Kolejność słów czasami niesie sygnał.

Dwie rodziny architektur wypełniły tę lukę przed pojawieniem się transformatorów.

**Sieci splotowe dla tekstu (TextCNN).** Zastosuj sploty 1D w sekwencjach osadzania słów. Filtr o szerokości 3 jest wykrywaczem trygramów, którego można się nauczyć: obejmuje trzy słowa i generuje wynik. Układaj różne szerokości (2, 3, 4, 5), aby wykryć wzory wieloskalowe. Maksymalna pula do reprezentacji o stałym rozmiarze. Płasko, równolegle, szybko.

**Sieci rekurencyjne (RNN, LSTM, GRU).** Przetwarzaj tokeny pojedynczo, zachowując ukryty stan, który przenosi informacje do przodu. Sekwencyjne, nośne, elastyczne długości wejściowe. Zdominowane modelowanie sekwencji od 2014 do 2017 roku, potem zwrócono na to uwagę.

Ta lekcja buduje jedno i drugie, a następnie wymienia niepowodzenie, które zmotywowało uwagę.

## Koncepcja

**TekstCNN** (Kim, 2014). Tokeny zostają osadzone. Splot 1D o szerokości `k` przesuwa filtr po kolejnych `k`-gramach osadzania, tworząc mapę cech. Globalne maksymalne zgromadzenie na tej mapie wybiera najsilniejszą aktywację. Połącz maksymalnie zbiorcze dane wyjściowe z kilku szerokości filtrów. Podaj dane do głowicy klasyfikatora.

Dlaczego to działa. Filtr to n-gram, którego można się nauczyć. Maksymalne łączenie nie zależy od pozycji, więc „niedobrze” uruchamia tę samą funkcję na początku lub w środku recenzji. Trzy szerokości filtrów po 100 filtrów każdy dają 300 wyuczonych detektorów n-gramowych. Szkolenie jest równoległe; brak zależności sekwencyjnej.

**RNN.** W każdym kroku `t` stan ukryty `h_t = f(W * x_t + U * h_{t-1} + b)`. Udostępniaj `W`, `U`, `b` w czasie. Stan ukryty w momencie `T` jest podsumowaniem całego przedrostka. Do klasyfikacji użyj puli obejmującej `h_1 ... h_T` (maks., średnia lub ostatnia).

Zwykłe sieci RNN charakteryzują się zanikającymi gradientami. **LSTM** dodaje bramki, które decydują o tym, o czym zapomnieć, co przechowywać i co wyprowadzić, stabilizując gradienty w długich sekwencjach. **GRU** upraszcza LSTM do dwóch bramek; działa podobnie przy mniejszej liczbie parametrów.

**Dwukierunkowe sieci RNN** obsługują jeden RNN do przodu i drugi do tyłu, łącząc ukryte stany. Reprezentacja każdego tokena widzi zarówno lewy, jak i prawy kontekst. Niezbędne do oznaczania zadań.

## Zbuduj to

### Krok 1: TextCNN w PyTorch

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

`transpose(1, 2)` zmienia kształt `[batch, seq_len, embed_dim]` na `[batch, embed_dim, seq_len]`, ponieważ `nn.Conv1d` traktuje oś środkową jako kanały. Łączne dane wyjściowe mają stały rozmiar niezależnie od długości danych wejściowych.

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

Maksymalna pula w sekwencji, a nie pula ostatniego stanu. W przypadku klasyfikacji maksymalne łączenie zwykle przewyższa przyjęcie ostatniego ukrytego stanu, ponieważ informacja na końcu długiej sekwencji ma tendencję do dominowania w ostatnim stanie.

### Krok 3: demonstracja znikającego gradientu (intuicja)

Zwykły RNN bez bramkowania nie może nauczyć się zależności dalekiego zasięgu. Rozważmy zadanie zabawkowe: przewidź, czy token `A` pojawił się w dowolnym miejscu sekwencji. Jeśli `A` znajduje się na pozycji 1, a sekwencja ma długość 100 tokenów, gradient straty musi spłynąć z powrotem przez 99 mnożeń powtarzającej się wagi. Jeśli waga jest mniejsza niż 1, gradient znika. Jeśli więcej niż 1, eksploduje.

```python
def vanishing_gradient_sim(seq_len, recurrent_weight=0.9):
    import math
    return math.pow(recurrent_weight, seq_len)

# At weight=0.9 over 100 steps:
#   0.9 ^ 100 ≈ 2.7e-5
# The gradient from step 100 to step 1 is effectively zero.
```

LSTM rozwiązują ten problem za pomocą **stanu komórki**, który przepływa przez sieć tylko z interakcjami addytywnymi (bramka zapominania skaluje to multiplikatywnie, ale gradienty nadal płyną wzdłuż „autostrady”). GRU robią coś podobnego z mniejszą liczbą parametrów. Obydwa zapewniają stabilny trening poprzez ponad 100 sekwencji kroków.

### Krok 4: dlaczego to wciąż nie wystarczyło

Trzy problemy utrzymywały się nawet w przypadku LSTM.

1. **Sekwencyjne wąskie gardło.** Szkolenie RNN na sekwencji o długości 1000 wymaga 1000 seryjnych kroków do przodu/do tyłu. Nie można zrównoleglić w czasie.
2. **Wektor kontekstu o stałym rozmiarze w konfiguracjach kodera-dekodera.** Dekoder widzi tylko końcowy stan ukryty kodera, skompresowany na całym wejściu. Długie wejścia tracą szczegóły. Lekcja 09 omawia to bezpośrednio.
3. **Pułap dokładności zależności od odległości.** LSTM przewyższają zwykłe RNN, ale nadal mają trudności z propagowaniem określonych informacji w ponad 200 krokach.

Uwaga rozwiązała wszystkie trzy. Transformatory całkowicie porzuciły powtarzalność. Lekcja 10 jest punktem zwrotnym.

## Użyj tego

`nn.LSTM`, `nn.GRU` i `nn.Conv1d` PyTorch są gotowe do produkcji. Kod szkoleniowy jest standardem.

Hugging Face dostarcza wstępnie wytrenowane osady, które podłączasz jako warstwę wejściową:

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

Użyj listy kontrolnej, kiedy pasuje do ograniczeń.

- **Wnioskowanie na krawędzi / na urządzeniu.** TextCNN z osadzeniem GloVe jest 10-100 razy mniejszy niż transformator. Jeśli celem wdrożenia jest telefon, jest to stos.
- **Klasyfikacja transmisji strumieniowej / online.** RNN przetwarza jeden token na raz; transformatory potrzebują pełnej sekwencji. W przypadku tekstu przychodzącego w czasie rzeczywistym LSTM nadal wygrywają.
- **Małe modele dla linii bazowych.** Szybka iteracja nowego zadania. Wytrenuj TextCNN w 5 minut na procesorze.
- **Oznaczanie sekwencji z ograniczonymi danymi.** BiLSTM-CRF (lekcja 06) jest nadal architekturą NER klasy produkcyjnej dla oznaczonych 1k-10k zdań.

Cała reszta idzie do transformatora.

## Wyślij to

Zapisz jako `outputs/prompt-text-encoder-picker.md`:

```markdown
---
name: text-encoder-picker
description: Wybierz architekturę kodera tekstu dla zadanego zestawu ograniczeń.
phase: 5
lesson: 08
---

Biorąc pod uwagę ograniczenia (zadanie, objętość danych, budżet opóźnień, docelowe środowisko wdrożeniowe, budżet obliczeniowy), wygeneruj:

1. Architektura kodera: TextCNN, BiLSTM, BiLSTM-CRF, dostrojenie transformatora (fine-tune) lub "użycie wstępnie wytrenowanego transformatora jako zamrożonego kodera + mała głowica".
2. Wejście osadzania: losowa inicjalizacja, zamrożony GloVe / fastText lub kontekstualizowane osadzania transformatorowe.
3. Przepis na trening w 5 liniach: optymalizator, współczynnik uczenia (learning rate), rozmiar partii (batch size), epoki, regularyzacja.
4. Jeden sygnał do monitorowania. Dla modeli RNN/CNN: brak mechanizmu uwagi oznacza, że pomijają one zależności dalekiego zasięgu; sprawdzaj dokładność dla różnych długości sekwencji. Dla transformatorów: załamanie podczas dostrajania, jeśli współczynnik uczenia jest zbyt wysoki; monitoruj stratę treningową (train loss).

Odmów polecania dostrajania transformatora, gdy danych jest mniej niż ~500 oznaczonych przykładów, bez wykazania, że model bazowy TextCNN / BiLSTM osiągnął plateau. Oznacz wdrożenia brzegowe (edge deployment) jako wymagające zasady "architektura przede wszystkim" (architecture-before-everything).
```

## Ćwiczenia

1. **Łatwo.** Trenuj TextCNN na zbiorze danych zabawek składających się z 3 klas (wymyślasz dane). Sprawdź, czy szerokość filtra (2, 3, 4) jest większa niż pojedyncza szerokość (3) średnio F1.
2. **Średni.** Zaimplementuj pulę maksymalną, średnią i ostatni stan dla klasyfikatora LSTM. Porównaj na małym zbiorze danych; udokumentować, które połączenie wygrywa i postawić hipotezę dlaczego.
3. **Trudne.** Zbuduj tager BiLSTM-CRF NER (połącz lekcję 06 i tę). Pociąg na CoNLL-2003. Porównaj z wartością bazową samego CRF z lekcji 06 i dostrojeniem BERT. Raportuj czas treningu, pamięć i F1.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| TekstCNN | CNN dla tekstu | Stos splotów 1D nad osadzaniem słów z globalną pulą maksymalną. Kima (2014). |
| RNN | Powtarzająca się sieć | Stan ukryty aktualizowany na każdym etapie: `h_t = f(W x_t + U h_{t-1})`. |
| LSTM | Ogrodzony RNN | Dodaje bramki wejścia/zapomnienia/wyjścia + stan komórki. Trenuje stabilnie poprzez długie sekwencje. |
| GRU | Prostszy LSTM | Dwie bramy zamiast trzech. Podobna dokładność, mniej parametrów. |
| Dwukierunkowy | Obydwa kierunki | Połączone RNN do przodu i do tyłu. Każdy token widzi obie strony swojego kontekstu. |
| Znikający gradient | Sygnał treningowy umiera | Powtarzane mnożenie przez wagi <1 w zwykłych RNN sprawia, że ​​gradienty na wczesnym etapie są faktycznie zerowe. |

## Dalsze czytanie

- [Kim, Y. (2014). Konwolucyjne sieci neuronowe do klasyfikacji zdań] (https://arxiv.org/abs/1408.5882) — artykuł TextCNN. Osiem stron. Czytelny.
- [Hochreiter, S. i Schmidhuber, J. (1997). Długa pamięć krótkotrwała] (https://www.bioinf.jku.at/publications/older/2604.pdf) — artykuł LSTM. Nieoczekiwanie przejrzysty.
- [Olah, C. (2015). Zrozumienie sieci LSTM](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — diagramy, dzięki którym LSTM są dostępne dla każdego.