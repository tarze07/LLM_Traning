# Modele sekwencji do sekwencji

> Dwa RNN udające tłumacza. Wąskie gardło, na które natrafiono, jest powodem istnienia uwagi.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 08 (CNN + RNN dla tekstu), Faza 3 · 11 (Wprowadzenie do PyTorch)
**Czas:** ~75 minut

## Problem

Klasyfikacja odwzorowuje sekwencję o zmiennej długości na pojedynczą etykietę. Tłumaczenie odwzorowuje sekwencję o zmiennej długości na inną sekwencję o zmiennej długości. Dane wejściowe i wyjściowe są realizowane w różnych słownikach, być może w różnych językach, bez gwarancji parzystości długości.

Architektura seq2seq (Sutskever, Vinyals, Le, 2014) rozwiązała ten problem za pomocą celowo prostego przepisu. Dwa RNN. Czyta się zdanie źródłowe i tworzy wektor kontekstu o stałym rozmiarze. Drugi odczytuje ten wektor i generuje zdanie docelowe żeton po żetonie. Ten sam kod, który napisałeś dla lekcji 08, ale sklejony inaczej.

Warto się tego uczyć z dwóch powodów. Po pierwsze, wąskie gardło oparte na wektorze kontekstu jest najbardziej użyteczną pedagogicznie porażką w NLP. Motywuje wszystko, w czym uwaga i transformatory są dobre. Po drugie, przepis na szkolenie (wymuszenie przez nauczyciela, zaplanowane próbkowanie, przeszukiwanie wiązki przy wnioskowaniu) nadal ma zastosowanie do każdego nowoczesnego systemu generacji, w tym LLM.

## Koncepcja

**Koder.** RNN odczytujący zdanie źródłowe. Jego ostatecznym stanem ukrytym jest **wektor kontekstu** — podsumowanie całego sygnału wejściowego o stałym rozmiarze. Podobno nie tracisz nic oprócz źródła.

**Dekoder.** Kolejny RNN zainicjowany z wektora kontekstu. Na każdym kroku jako dane wejściowe pobiera wcześniej wygenerowany token i generuje rozkład na słownictwo docelowe. Próbka lub argmax, aby wybrać następny token. Podaj go z powrotem. Powtarzaj tę czynność, aż zostanie wygenerowany token `<EOS>` lub osiągnięta zostanie maksymalna długość.

**Trening:** Strata entropii krzyżowej na każdym etapie dekodera, zsumowana po sekwencji. Standardowe wsparcie w czasie przez obie sieci.

**Nauczyciel wymusza.** Podczas szkolenia dane wejściowe dekodera w kroku `t` to token *podstawowej prawdy* w pozycji `t-1`, a nie wcześniejsze przewidywania dekodera. To stabilizuje trening; bez tego wczesne błędy kaskadują się i model nigdy się nie uczy. Podczas wnioskowania należy użyć własnych przewidywań modelu, więc zawsze istnieje luka w rozkładzie pociągu/wnioskowania. Ta luka nazywa się **błędem ekspozycji**.

**Wąskie gardło.** Wszystko, czego koder dowiedział się o źródle, musi zostać wciśnięte w jeden wektor kontekstu. Długie zdania tracą szczegóły. Rzadkie słowa ulegają zamazaniu. Zmiana kolejności (czarny kot kontra czarny kot) musi zostać zapamiętana, a nie obliczona.

Uwaga (lekcja 10) rozwiązuje ten problem, pozwalając dekoderowi sprawdzić *każdy* stan ukryty kodera, a nie tylko ostatni. To jest całe boisko.

## Zbuduj to

### Krok 1: koder

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

`outputs` ma kształt `[batch, seq_len, hidden_dim]` — jeden stan ukryty na pozycję wejściową. `hidden` ma kształt `[1, batch, hidden_dim]` — ostatni krok. Lekcja 08 mówiła o „łączeniu wyników w celu klasyfikacji”. Tutaj zachowujemy ostatni ukryty stan jako wektor kontekstu i ignorujemy dane wyjściowe poszczególnych kroków.

### Krok 2: dekoder

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

Dekoder nazywa się krok po kroku. Dane wejściowe: partia pojedynczych tokenów i bieżący stan ukryty. Dane wyjściowe: logiki słownictwa dla następnego tokena i zaktualizowany stan ukryty.

### Krok 3: pętla treningowa z przymusem nauczyciela

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

Dwa pokrętła warte nazwania. `ignore_index=0` pomija utratę tokenów dopełniających. `teacher_forcing_ratio` to prawdopodobieństwo użycia prawdziwego tokena w porównaniu z przewidywaniami modelu na każdym kroku. Zacznij od 1,0 (pełne wymuszanie przez nauczyciela) i obniż do ~0,5 w trakcie treningu, aby zamknąć lukę w odchyleniu od ekspozycji.

### Krok 4: pętla wnioskowania (chciwa)

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

Zachłanne dekodowanie wybiera na każdym kroku token o najwyższym prawdopodobieństwie. Może odejść: kiedy już zaangażujesz się w token, nie możesz go cofnąć. **Wyszukiwanie wiązki** utrzymuje przy życiu górne `k` częściowe sekwencje i na końcu wybiera kompletną sekwencję z najwyższym wynikiem. Szerokość belki 3-5 jest standardem.

### Krok 5: zademonstrowanie wąskiego gardła

Trenuj model w zakresie zadania kopiowania zabawki: źródło `[a, b, c, d, e]`, cel `[a, b, c, d, e]`. Zwiększ długość sekwencji. Przestrzegaj dokładności.

```
seq_len=5   copy accuracy: 98%
seq_len=10  copy accuracy: 91%
seq_len=20  copy accuracy: 62%
seq_len=40  copy accuracy: 23%
```

Pojedynczy ukryty stan GRU nie może bezstratnie zapamiętać 40-tokenowego wejścia. Informacje są dostępne na każdym kroku kodera, ale dekoder widzi tylko ostatni stan. Uwaga naprawia to bezpośrednio.

## Użyj tego

PyTorch ma szablony seq2seq oparte na `nn.Transformer` i `nn.LSTM`. Biblioteka Hugging Face `transformers` zawiera pełne modele koderów-dekoderów (BART, T5, mBART, NLLB) trenowane na miliardach tokenów.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tok = AutoTokenizer.from_pretrained("facebook/bart-base")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")

src = tok("Translate this to French: Hello, how are you?", return_tensors="pt")
out = model.generate(**src, max_new_tokens=50, num_beams=4)
print(tok.decode(out[0], skip_special_tokens=True))
```

Nowoczesne kodery-dekodery porzuciły RNN na rzecz transformatorów. Kształt wysokiego poziomu (koder, dekoder, generowanie tokenu po tokenie) jest identyczny z dokumentem seq2seq z 2014 roku. Mechanizm wewnątrz każdego bloku jest inny.

### Kiedy nadal sięgać po seq2seq oparte na RNN

Prawie nigdy, w przypadku nowych projektów. Konkretne wyjątki:

- Tłumaczenie strumieniowe, w którym zużywasz jeden token wejściowy na raz przy ograniczonej pamięci.
- Generowanie tekstu na urządzeniu, gdzie koszt pamięci transformatora jest wygórowany.
- Pedagogika. Zrozumienie wąskiego gardła kodera i dekodera to najszybsza droga do zrozumienia, dlaczego transformatory zwyciężyły.

### Błąd ekspozycji i jego łagodzenie

- **Próbkowanie zaplanowane.** Nauczyciel wymusza współczynnik wyżarzania podczas szkolenia, dzięki czemu model uczy się naprawiać własne błędy.
- **Szkolenie z zakresu minimalnego ryzyka.** Trenuj na poziomie wyniku BLEU na poziomie zdania zamiast entropii krzyżowej na poziomie tokena. Bliżej tego, czego naprawdę chcesz.
- **Dostrajanie uczenia się przez wzmacnianie.** Nagradzaj generator sekwencji metryką. Używany w nowoczesnym LLM RLHF.

Wszystkie trzy nadal mają zastosowanie do generacji opartej na transformatorach.

## Wyślij to

Zapisz jako `outputs/prompt-seq2seq-design.md`:

```markdown
---
name: seq2seq-design
description: Zaprojektuj potok sekwencyjny dla danego zadania.
phase: 5
lesson: 09
---

Biorąc pod uwagę zadanie (tłumaczenie, podsumowanie, parafrazę, przepisanie pytania), wynik:

1. Architektura. Wstępnie wytrenowany koder-dekoder transformatorowy (BART, T5, mBART, NLLB) jest domyślny. Seq2seq oparty na RNN tylko dla określonych ograniczeń.
2. Rozpoczęcie punktu kontrolnego. Nadaj mu nazwę (`facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`). Dopasuj punkt kontrolny do zadania i zakresu językowego.
3. Strategia dekodowania. Chciwy na deterministyczne wyniki, wyszukiwanie wiązki (szerokość 4-5) dla jakości, próbkowanie z temperaturą dla różnorodności. Uzasadnienie jednym zdaniem.
4. Jeden tryb awarii do weryfikacji przed wysyłką. Błąd ekspozycji objawia się dryfem generacji na dłuższych wynikach; pobierz 20 próbek wyników na długości 90. percentyla i oceń wzrokowo.

Odmów polecania uczenia seq2seq od zera w przypadku liczby poniżej miliona równoległych przykładów. Oznacz każdy potok używający chciwego dekodowania dla treści zwróconych użytkownikowi jako delikatny (chciwe powtórzenia i pętle).
```

## Ćwiczenia

1. **Łatwe.** Wykonaj zadanie kopiowania zabawek. Trenuj GRU seq2seq na parach wejście-wyjście, gdzie cel jest równy źródłu. Zmierz dokładność na długościach 5, 10, 20. Odtwórz wąskie gardło.
2. **Średni.** Dodaj dekodowanie wyszukiwania wiązki o szerokości wiązki 3. Zmierz BLEU na małym równoległym korpusie względem zachłannego. Dokumentuj, gdzie wygrywa wyszukiwanie belek (zwykle ostatnie żetony), a gdzie nie ma to znaczenia.
3. **Trudne.** Dostosuj `facebook/bart-base` na zestawie danych parafrazy składającym się z 10 tys. par. Porównaj sygnał wyjściowy Beam-4 w precyzyjnie dostrojonym modelu z sygnałem wejściowym modelu podstawowego. Zgłoś BLEU i wybierz 10 przykładów jakościowych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Koder | Wprowadź RNN | Czyta źródło. Tworzy ukryte stany krok po kroku i końcowy wektor kontekstu. |
| Dekoder | Wyjście RNN | Zainicjowano z wektora kontekstu. Generuje żetony celu pojedynczo. |
| Wektor kontekstu | Podsumowanie | Ostateczny stan ukryty kodera. Stały rozmiar. Uwaga wąskiego gardła rozwiązuje się. |
| Nauczyciel zmusza | Użyj prawdziwych tokenów | Podaj poprzedni token prawdy w czasie treningu. Stabilizuje naukę. |
| Błąd ekspozycji | Luka pociągowa/testowa | Modelka trenowana na prawdziwych tokenach nigdy nie ćwiczyła odzyskiwania własnych błędów. |
| Wyszukiwanie wiązki | Lepsze dekodowanie | Utrzymuj przy życiu częściowe sekwencje górnego k na każdym kroku, zamiast zachłannie się angażować. |

## Dalsze czytanie

- [Sutskever, Vinyals, Le (2014). Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) — oryginalny artykuł seq2seq. Cztery strony.
- [Cho i in. (2014). Uczenie się reprezentacji fraz przy użyciu kodera-dekodera RNN do statystycznego tłumaczenia maszynowego](https://arxiv.org/abs/1406.1078) — wprowadzono GRU i ramkowanie kodera-dekodera.
- [Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) – dokument informacyjny. Przeczytaj zaraz po tej lekcji.
- [Poradnik PyTorch NLP od Scratch](https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html) — seq2seq do zbudowania + kod uwagi.