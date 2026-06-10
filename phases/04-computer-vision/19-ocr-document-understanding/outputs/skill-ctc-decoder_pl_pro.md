---

name: skill-ctc-decoder
description: Implementacja od zera dekoderów CTC (zachłannego oraz wyszukiwania wiązkowego) wraz z normalizacją długości
version: 1.0.0
phase: 4
lesson: 19
tags: [ocr, ctc, decoding, sequence-models]

---

# Dekodery CTC

Zaimplementuje dwie procedury dekodowania dla wyników CTC: zachłanną (szybką) oraz wyszukiwania wiązkowego (ang. beam search, efektywniejszą przy zaszumionych danych wejściowych).

## Zastosowanie

- Wykonywanie wnioskowania (inference) OCR na wyjściach z własnych architektur CRNN.
- Testowanie i porównywanie gotowych modeli OCR przy użyciu różnych metod dekodowania.
- Implementacja prostego algorytmu wyszukiwania wiązkowego (beam search) bez konieczności instalowania zewnętrznych zależności (np. `ctcdecode`).

## Dane wejściowe

- `log_probs`: macierz o wymiarach `(T, N, C)` reprezentująca wartości log-softmax dla słownika (indeks 0 domyślnie oznacza znak pusty – blank).
- `vocab`: lista zawierająca `C` znaków ze słownika.
- `beam_width` (tylko dla wyszukiwania wiązkowego): zazwyczaj w przedziale 5-10.

## Dekoder zachłanny (Greedy Decoder)

```python
def greedy_ctc_decode(log_probs, vocab, blank=0):
    preds = log_probs.argmax(dim=-1).transpose(0, 1).cpu().tolist()
    out = []
    for seq in preds:
        decoded = []
        prev = None
        for idx in seq:
            if idx != prev and idx != blank:
                decoded.append(vocab[idx])
            prev = idx
        out.append("".join(decoded))
    return out
```

## Dekoder wyszukiwania wiązkowego (Beam Search Decoder)

```python
import heapq
import math

def beam_ctc_decode(log_probs, vocab, beam_width=5, blank=0):
    T, N, C = log_probs.shape
    lp = log_probs.cpu()
    results = []
    for n in range(N):
        beams = {("",): (0.0, -math.inf)}  # (krotka_prefiksu) -> (p_blank, p_nonblank)
        for t in range(T):
            logits_t = lp[t, n]
            new_beams = {}
            for prefix, (p_b, p_nb) in beams.items():
                for c in range(C):
                    p = logits_t[c].item()
                    if c == blank:
                        nb = p_b + p
                        nnb = p_nb + p
                        upd = new_beams.get(prefix, (-math.inf, -math.inf))
                        new_beams[prefix] = (
                            _logsumexp(upd[0], _logsumexp(nb, nnb)),
                            upd[1],
                        )
                    else:
                        last = prefix[-1] if prefix else ""
                        char = vocab[c]
                        if char == last:
                            # Przypadek 1: pozostanie przy tym samym prefiksie
                            upd = new_beams.get(prefix, (-math.inf, -math.inf))
                            new_beams[prefix] = (upd[0], _logsumexp(upd[1], p_nb + p))
                            # Przypadek 2: wydłużenie prefiksu o powtórzony znak oddzielony blankiem ("a_a" -> "aa")
                            new_prefix = prefix + (char,)
                            upd = new_beams.get(new_prefix, (-math.inf, -math.inf))
                            new_beams[new_prefix] = (upd[0], _logsumexp(upd[1], p_b + p))
                        else:
                            new_prefix = prefix + (char,)
                            upd = new_beams.get(new_prefix, (-math.inf, -math.inf))
                            nb = _logsumexp(p_b, p_nb) + p
                            new_beams[new_prefix] = (upd[0], _logsumexp(upd[1], nb))
            beams = dict(heapq.nlargest(
                beam_width,
                new_beams.items(),
                key=lambda kv: _logsumexp(kv[1][0], kv[1][1]),
            ))
        best = max(beams.items(), key=lambda kv: _logsumexp(kv[1][0], kv[1][1]))[0]
        results.append("".join(best))
    return results


def _logsumexp(a, b):
    if a == -math.inf: return b
    if b == -math.inf: return a
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))
```

## Zasady i dobre praktyki

- Indeks znaku pustego (blank) w CTC wynosi 0, zgodnie z konwencją przyjętą w klasie `nn.CTCLoss` w bibliotece PyTorch.
- Wyszukiwanie wiązkowe poprawia wyniki rozpoznawania dla danych o niskim poziomie pewności; w przypadku wyraźnych obrazów wejściowych poprawa wynosi zazwyczaj mniej niż 1% CER.
- Nie ustawiaj szerokości wiązki (`beam_width`) poniżej 5; spadek dokładności nie kompensuje wówczas nieznacznego zysku czasowego.
- Przy rygorystycznym budżecie opóźnień (latency) zaleca się powrót do dekodowania zachłannego; dla większości zastosowań produkcyjnych OCR różnica w jakości jest marginalna.
- W przypadku bardzo dużych słowników (np. CJK zawierających ponad 3000 znaków) należy skorzystać z zoptymalizowanej biblioteki `ctcdecode` (napisanej w C++) zamiast powyższej implementacji w czystym Pythonie, która szybko stanie się wąskim gardłem wydajnościowym.
