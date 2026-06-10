---

name: skill-ctc-decoder
description: Napisz od podstaw dekodery CTC zachłanne i przeszukujące wiązkę, łącznie z normalizacją długości
version: 1.0.0
phase: 4
lesson: 19
tags: [ocr, ctc, decoding, sequence-models]

---

# Dekoder CTC

Stwórz dwie procedury dekodowania dla wyjść CTC: zachłanną (szybką) i wiązkową (lepsza na zaszumionych wejściach).

## Kiedy używać

— Uruchamianie wnioskowania OCR na niestandardowych wyjściach CRNN.
- Porównanie wstępnie wytrenowanego modelu OCR z różnymi dekoderami.
- Implementacja prostego wyszukiwania belek bez wciągania ctcdecode.

## Wejścia

- `log_probs`: (T, N, C) log-softmax na słownictwie (indeks 0 = zgodnie z konwencją pusty).
- `vocab`: lista znaków C.
- `beam_width` (tylko wiązka): typowo 5-10.

## Chciwy dekoder

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

## Dekoder wyszukiwania wiązki

```python
import heapq
import math

def beam_ctc_decode(log_probs, vocab, beam_width=5, blank=0):
    T, N, C = log_probs.shape
    lp = log_probs.cpu()
    results = []
    for n in range(N):
        beams = {("",): (0.0, -math.inf)}  # (prefix_tuple) -> (p_blank, p_nonblank)
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
                            # Case 1: stay on same prefix (collapse from p_nb)
                            upd = new_beams.get(prefix, (-math.inf, -math.inf))
                            new_beams[prefix] = (upd[0], _logsumexp(upd[1], p_nb + p))
                            # Case 2: extend prefix via blank-separated repeat ("a_a" -> "aa")
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

## Zasady

- Pusty indeks w CTC wynosi 0 zgodnie z konwencją w `nn.CTCLoss` firmy PyTorch.
- Wyszukiwanie wiązki poprawia dokładność danych wejściowych o niskim poziomie pewności; na czystych wejściach poprawa wynosi <1% CER.
- Nigdy nie przycinaj belki poniżej 5; Poniżej tej wartości handlu dokładność-opóźnienie spłaszcza się.
- Gdy uruchamiasz wyszukiwanie wiązki przy ograniczonym budżecie opóźnień, przejdź do zachłanności; W przypadku większości produkcyjnych danych OCR wynik jakości jest niewielki.
- W przypadku dużych słowników (CJK z ponad 3000 znakami) przełącz się na `ctcdecode` (C++) zamiast powyższej czystej wersji Pythona; wiązka Pythona szybko staje się wąskim gardłem.