# Modele typu Sequence-to-Sequence (seq2seq)

> Dwie sieci RNN współpracujące jako tłumacz. Wąskie gardło (bottleneck) tej architektury stało się bezpośrednią przyczyną opracowania mechanizmu uwagi (attention).

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 08 (CNN i RNN w przetwarzaniu tekstu), Faza 3 · Lekcja 11 (Wprowadzenie do PyTorch)
**Czas:** ~75 minut

## Problem

Klasyczna klasyfikacja mapuje sekwencję o zmiennej długości na pojedynczą etykietę. Zadania takie jak tłumaczenie maszynowe wymagają jednak przekształcenia sekwencji wejściowej o zmiennej długości w inną sekwencję o zmiennej długości. Teksty wejściowe i wyjściowe korzystają z różnych słowników, często w różnych językach, a długości obu sekwencji rzadko są równe.

Architektura seq2seq (Sutskever, Vinyals, Le, 2014) rozwiązała ten problem za pomocą bardzo prostej koncepcji opartej na dwóch sieciach RNN. Pierwsza (enkoder) analizuje zdanie źródłowe i tworzy wektor kontekstu (context vector) o stałym rozmiarze. Druga (dekoder) odczytuje ten wektor i generuje zdanie docelowe token po tokenie. Wykorzystuje się tu te same bloki, które poznaliśmy w lekcji 08, lecz połączone w inny sposób.

Zrozumienie tego modelu jest kluczowe z dwóch powodów. Po pierwsze, wąskie gardło (bottleneck) wektora kontekstu to doskonały przykład dydaktyczny ograniczeń klasycznych sieci. To właśnie ono legło u podstaw sukcesu mechanizmu uwagi i architektury Transformer. Po drugie, techniki treningowe (takie jak teacher forcing, scheduled sampling czy beam search podczas wnioskowania) są nadal powszechnie stosowane w nowoczesnych systemach generatywnych, w tym w dużych modelach językowych (LLM).

## Pojęcia

**Enkoder (Encoder):** Sieć RNN analizująca sekwencję źródłową. Jej ostatni stan ukryty (hidden state) stanowi **wektor kontekstu (context vector)** – skompresowane podsumowanie całego wejścia o stałym rozmiarze. Zakładamy w tym miejscu (często błędnie), że wektor ten bezstratnie reprezentuje całe zdanie źródłowe.

**Dekoder (Decoder):** Druga sieć RNN, której stan początkowy jest inicjalizowany wektorem kontekstu. W każdym kroku czasowym dekoder otrzymuje jako wejście poprzednio wygenerowany token i wyznacza rozkład prawdopodobieństwa nad słownikiem docelowym. Następnie za pomocą operacji argmax (lub próbkowania) wybiera kolejny token, który jest przekazywany do kolejnego kroku. Proces ten powtarza się do momentu wygenerowania tokenu końca sekwencji (`<EOS>`) lub osiągnięcia maksymalnego limitu długości.

**Uczenie modelu:** Minimalizacja straty entropii krzyżowej (cross-entropy loss) na każdym kroku dekodera, zsumowanej po całej sekwencji. Proces ten wykorzystuje wsteczną propagację w czasie (BPTT) przechodzącą przez obie sieci.

**Teacher Forcing:** Podczas treningu wejściem do dekodera w kroku `t` jest rzeczywisty token referencyjny (ground truth) z kroku `t-1`, a nie token wygenerowany (przewidziany) przez model w poprzednim kroku. Stabilizuje to proces uczenia i zapobiega sytuacji, w której wczesny błąd uniemożliwia modelowi naukę dalszej części zdania. Podczas wnioskowania model musi jednak korzystać z własnych predykcji, co stwarza rozbieżność między fazą treningu a fazą testową. Zjawisko to nazywamy **błędem ekspozycji (exposure bias)**.

**Wąskie gardło (bottleneck):** Cała informacja wyodrębniona przez enkoder z tekstu źródłowego musi zostać skompresowana do jednego wektora o stałej długości. Przy długich zdaniach szczegóły ulegają zatraceniu, rzadkie słowa stają się nieczytelne dla dekodera, a zmiana szyku wyrazów musi zostać wprost zapamiętana, zamiast być elastycznie wyliczana.

Mechanizm uwagi (lekcja 10) eliminuje to ograniczenie, pozwalając dekoderowi na dynamiczny dostęp do *każdego* stanu ukrytego enkodera w trakcie generowania. To zmienia wszystko.

## Implementacja krok po kroku

### Krok 1: Enkoder

```python
import torch
import torch.nn as nn

class Encoder(nn.Module):
    def __init__(self, src_vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(src_vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True)

    def forward(self, src):
        e = self.embed(src)
        outputs, hidden = self.gru(e)
        return outputs, hidden
```

Tensor `outputs` ma wymiary `[batch, seq_len, hidden_dim]` – zawiera stany ukryte dla każdej pozycji wejściowej. Tensor `hidden` ma wymiary `[1, batch, hidden_dim]` i reprezentuje stan ukryty z ostatniego kroku czasowego. W odróżnieniu od klasyfikacji tekstu (lekcja 08), gdzie agregowaliśmy wszystkie stany, w klasycznym seq2seq zachowujemy wyłącznie ten ostatni stan ukryty jako wektor kontekstu, ignorując stany pośrednie enkodera.

### Krok 2: Dekoder

```python
class Decoder(nn.Module):
    def __init__(self, tgt_vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(tgt_vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, tgt_vocab_size)

    def forward(self, token, hidden):
        e = self.embed(token)
        out, hidden = self.gru(e, hidden)
        logits = self.fc(out)
        return logits, hidden
```

Dekoder jest wywoływany iteracyjnie (krok po kroku). Wejście: paczka pojedynczych tokenów z poprzedniego kroku oraz aktualny stan ukryty. Wyjście: logity (logits) dla słownika docelowego oraz zaktualizowany stan ukryty.

### Krok 3: Pętla treningowa z mechanizmem Teacher Forcing

```python
def train_batch(encoder, decoder, src, tgt, bos_id, optimizer, teacher_forcing_ratio=0.9):
    optimizer.zero_grad()
    _, hidden = encoder(src)
    batch_size, tgt_len = tgt.shape
    input_token = torch.full((batch_size, 1), bos_id, dtype=torch.long)
    loss = 0.0
    loss_fn = nn.CrossEntropyLoss(ignore_index=0)

    for t in range(tgt_len):
        logits, hidden = decoder(input_token, hidden)
        step_loss = loss_fn(logits.squeeze(1), tgt[:, t])
        loss += step_loss
        use_teacher = torch.rand(1).item() < teacher_forcing_ratio
        if use_teacher:
            input_token = tgt[:, t].unsqueeze(1)
        else:
            input_token = logits.argmax(dim=-1)

    loss.backward()
    optimizer.step()
    return loss.item() / tgt_len
```

Kluczowe szczegóły: `ignore_index=0` pomija obliczanie straty dla tokenów dopełnienia (padding). Parametr `teacher_forcing_ratio` określa prawdopodobieństwo użycia rzeczywistego tokenu referencyjnego zamiast predykcji modelu w danym kroku. Trening zazwyczaj zaczyna się od wartości 1.0 (pełny Teacher Forcing), którą stopniowo obniża się do około 0.5 (scheduled sampling), aby zredukować błąd ekspozycji.

### Krok 4: Pętla wnioskowania (dekodowanie zachłanne)

```python
@torch.no_grad()
def greedy_decode(encoder, decoder, src, bos_id, eos_id, max_len=50):
    _, hidden = encoder(src)
    batch_size = src.shape[0]
    input_token = torch.full((batch_size, 1), bos_id, dtype=torch.long)
    output_ids = []
    for _ in range(max_len):
        logits, hidden = decoder(input_token, hidden)
        next_token = logits.argmax(dim=-1)
        output_ids.append(next_token)
        input_token = next_token
        if (next_token == eos_id).all():
            break
    return torch.cat(output_ids, dim=1)
```

Dekodowanie zachłanne (greedy decoding) wybiera w każdym kroku token o najwyższym prawdopodobieństwie. Jego wadą jest brak możliwości cofnięcia błędnych decyzji. Alternatywą jest **wyszukiwanie wiązkowe (beam search)**, które utrzymuje w pamięci `k` najbardziej prawdopodobnych częściowych sekwencji (wiązek), wybierając na końcu tę o najwyższym łącznym prawdopodobieństwie. W praktyce stosuje się zazwyczaj szerokość wiązki (beam width) rzędu 3-5.

### Krok 5: Prezentacja ograniczenia wąskiego gardła

Przetestujmy model w zadaniu kopiowania (copy task): zdanie docelowe jest identyczne ze źródłowym (np. `[a, b, c, d, e]`). Zwiększajmy długość sekwencji i obserwujmy dokładność (accuracy) rekonstrukcji:

```
seq_len=5   copy accuracy: 98%
seq_len=10  copy accuracy: 91%
seq_len=20  copy accuracy: 62%
seq_len=40  copy accuracy: 23%
```

Pojedyńczy stan ukryty sieci GRU nie jest w stanie zapamiętać bezstratnie 40-tokenowej sekwencji. Choć informacje są dostępne na etapach pośrednich enkodera, dekoder ma dostęp wyłącznie do jego ostatniego stanu. Mechanizm uwagi eliminuje to ograniczenie.

## Zastosowanie w praktyce

PyTorch oferuje gotowe moduły enkodera i dekodera oparte na `nn.Transformer` oraz `nn.LSTM`. W zastosowaniach praktycznych wykorzystuje się gotowe architektury Encoder-Decoder (np. BART, T5, mBART, NLLB) z biblioteki Hugging Face `transformers`, wytrenowane na ogromnych korpusach tekstowych:

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tok = AutoTokenizer.from_pretrained("facebook/bart-base")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")

src = tok("Translate this to French: Hello, how are you?", return_tensors="pt")
out = model.generate(**src, max_new_tokens=50, num_beams=4)
print(tok.decode(out[0], skip_special_tokens=True))
```

Współczesne modele seq2seq porzuciły sieci RNN na rzecz Transformerów. Jednak ogólny schemat działania (enkoder, dekoder, generowanie sekwencji krok po kroku) pozostaje tożsamy z oryginalną koncepcją seq2seq z 2014 roku – zmianie uległa jedynie wewnętrzna architektura poszczególnych bloków.

### Kiedy wciąż warto stosować seq2seq oparty na RNN

- Generowanie/tłumaczenie strumieniowe przy bardzo ograniczonych zasobach pamięci RAM (gdzie możemy przetwarzać po jednym tokenie).
- Wdrożenia na urządzeniach końcowych (edge), gdzie narzut pamięciowy Transformerów jest zbyt wysoki.
- Dydaktyka: zrozumienie ograniczeń enkodera i dekodera w seq2seq to najlepszy sposób na pojęcie przewag architektury Transformer.

### Metody redukcji błędu ekspozycji

1. **Scheduled Sampling:** Stopniowe obniżanie prawdopodobieństwa używania Teacher Forcing w trakcie treningu, co zmusza model do korygowania własnych błędów.
2. **Minimum Risk Training:** Optymalizacja modelu bezpośrednio pod kątem docelowych metryk tekstowych (np. BLEU na poziomie zdań) zamiast straty entropii krzyżowej dla pojedynczych tokenów.
3. **Uczenie przez wzmacnianie (RL):** Strojenie generatora przy użyciu funkcji nagrody (np. oceny ludzkiej lub modelu nagrody), co stanowi podstawę metody RLHF stosowanej w LLM.

## Szablon do wdrożenia

Zapisz go jako `outputs/prompt-seq2seq-design.md`:

```markdown
---
name: seq2seq-design
description: Zaprojektuj potok sekwencyjny dla danego zadania.
phase: 5
lesson: 09
---

Jesteś doradcą ds. architektury systemów generatywnych seq2seq. Na podstawie opisu zadania (tłumaczenie, podsumowanie, parafraza, przekształcanie zapytań) określ:

1. Rekomendowaną architekturę: Domyślnie gotowe modele typu Encoder-Decoder (np. BART, T5, mBART, NLLB). Klasyczna architektura RNN-seq2seq tylko w przypadku specyficznych ograniczeń sprzętowych.
2. Wybór modelu bazowego (checkpointu): Podaj dokładną nazwę modelu z Hugging Face (np. `facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`), dopasowaną do specyfiki zadania i obsługiwanych języków.
3. Strategię dekodowania: Dekodowanie zachłanne dla powtarzalnych wyników deterministycznych, wyszukiwanie wiązkowe (beam search, szerokość 4-5) dla maksymalnej jakości generowania, lub próbkowanie z temperaturą dla zwiększenia kreatywności (różnorodności) wraz z uzasadnieniem.
4. Jeden scenariusz awaryjny (testowy): Ryzyko błędu ekspozycji (exposure bias), objawiające się zapętlaniem tekstu lub halucynacjami przy długich sekwencjach wyjściowych. Zaproponuj weryfikację jakościową dla 20 najdłuższych generowanych tekstów (90. percentyl).

Odmów polecania trenowania modeli seq2seq od podstaw, jeśli zbiór par równoległych liczy mniej niż milion przykładów. Oznacz potoki wykorzystujące dekodowanie zachłanne do generowania tekstów dla użytkowników końcowych jako podatne na błędy (ryzyko powtórzeń i pętli nieskończonych).
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj zadanie kopiowania sekwencji (copy task). Wytrenuj sieć GRU seq2seq na parach wejście-wyjście, gdzie sekwencja wyjściowa jest kopią wejściowej. Zmierz i porównaj dokładność rekonstrukcji dla długości 5, 10 oraz 20 tokenów. Odtwórz zjawisko wąskiego gardła.
2. **Średnie.** Dodaj dekodowanie wiązkowe o szerokości 3 do swojego modelu. Zmierz wynik BLEU na małym korpusie równoległym i porównaj go z dekodowaniem zachłannym. Wskaż przypadki, w których wyszukiwanie wiązkowe przyniosło największą poprawę.
3. **Trudne.** Dostrój model `facebook/bart-base` na zbiorze danych parafrazy złożonym z 10 tys. par. Porównaj jakość wyjściową dekodowania wiązkowego (beam width = 4) modelu dostrojonego z modelem bazowym. Zgłoś metrykę BLEU i przedstaw analizę jakościową dla 10 wybranych przykładów.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| Enkoder | Wejściowa sieć RNN | Odpowiada za analizę tekstu źródłowego, generując stany ukryte i końcowy wektor kontekstu. |
| Dekoder | Wyjściowa sieć RNN | Inicjalizowany wektorem kontekstu. Odpowiada za generowanie kolejnych tokenów sekwencji docelowej. |
| Wektor kontekstu | Skompresowany kontekst | Ostatni stan ukryty enkodera. Posiada stałą długość, co tworzy wąskie gardło (eliminowane przez mechanizm uwagi). |
| Teacher Forcing | Wymuszanie odpowiedzi | Metoda podawania rzeczywistych tokenów referencyjnych na wejście dekodera w trakcie treningu w celu przyspieszenia zbieżności. |
| Błąd ekspozycji | Exposure bias | Zjawisko rozbieżności między treningiem a wnioskowaniem, wynikające z faktu, że model uczony z Teacher Forcing nie potrafi korygować własnych błędów popełnionych w fazie testowej. |
| Wyszukiwanie wiązkowe | Beam search | Heurystyczny algorytm dekodowania utrzymujący `k` najbardziej prawdopodobnych ścieżek generowania tekstu. |

## Dalsze czytanie

- [Sutskever, I., Vinyals, O., Le, Q. V. (2014). Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) — przełomowy artykuł wprowadzający architekturę seq2seq.
- [Cho et al. (2014). Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation](https://arxiv.org/abs/1406.1078) — praca wprowadzająca sieć GRU oraz modelowanie koder-dekoder.
- [Bahdanau, D., Cho, K., Bengio, Y. (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — kluczowy artykuł wprowadzający mechanizm uwagi. Warto przeczytać tuż po tej lekcji.
- [PyTorch Tutorial: Translation with a Sequence to Sequence Network and Attention](https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html) — praktyczny kod implementacji seq2seq z mechanizmem uwagi od podstaw w PyTorch.
