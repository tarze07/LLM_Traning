---

name: skill-recall-at-k-runner
description: Napisz czystą wiązkę ewaluacyjną dla wycofania@K z podziałem na pociąg/val/galerię i odpowiednim kontraktem danych
version: 1.0.0
phase: 4
lesson: 20
tags: [retrieval, evaluation, recall, faiss]

---

# Przypomnij @K Runner

Zamień folder zawierający obrazy zapytań i galerii oraz etykiety w powtarzalny numer przypomnienia@K.

## Kiedy używać

- Pierwszy punkt odniesienia pobierania dla nowego szkieletu.
- Śledzenie jakości osadzania w różnych epokach.
- Porównanie dwóch systemów wyszukiwania na tym samym zbiorze danych.

## Wejścia

- `query_images`: lista ścieżek.
- `gallery_images`: lista ścieżek (zapytanie może się nakładać lub nie).
- `query_labels`, `gallery_labels`: identyfikatory klas lub instancji.
- `encoder_fn`: wywoływalny `image -> embedding` (wstępnie obliczony lub na żywo).
- `ks`: lista taka jak `[1, 5, 10]`.

## Kroki

1. Zakoduj raz każdy obraz z galerii. Zapisz jako tablicę numpy.
2. Zakoduj każdy obraz zapytania.
3. L2-normalizuj oba zestawy osadzania.
4. Dla każdego zapytania oblicz podobieństwo względem wszystkich elementów galerii.
5. Sortuj malejąco, weź górę max(ks).
6. Dla każdego K sprawdź, czy którykolwiek z najważniejszych K elementów galerii ma tę samą etykietę zapytania.
7. Zgłoś `recall@K = fraction of queries that had at least one correct neighbour in top K`.

## Szablon wyjściowy

```python
import numpy as np
from sklearn.preprocessing import normalize

def encode_all(images, encoder_fn, batch=32):
    out = []
    for i in range(0, len(images), batch):
        embs = encoder_fn(images[i:i + batch])
        out.append(embs)
    return np.concatenate(out)


def recall_at_k(query_emb, gallery_emb, q_labels, g_labels,
                ks=(1, 5, 10), query_ids=None, gallery_ids=None):
    if len(query_emb) == 0 or len(gallery_emb) == 0:
        return {f"recall@{k}": 0.0 for k in ks}

    g_label_set = set(g_labels.tolist())
    keep = np.array([lbl in g_label_set for lbl in q_labels])
    if not keep.any():
        return {f"recall@{k}": 0.0 for k in ks}

    q_emb_f = query_emb[keep]
    q_lab_f = q_labels[keep]
    q_id_f = query_ids[keep] if query_ids is not None else None

    q = normalize(q_emb_f)
    g = normalize(gallery_emb)
    sims = q @ g.T

    if q_id_f is not None and gallery_ids is not None:
        self_mask = q_id_f[:, None] == gallery_ids[None, :]
        sims = np.where(self_mask, -np.inf, sims)

    top_k_max = min(max(ks), g.shape[0])
    if top_k_max <= 0:
        return {f"recall@{k}": 0.0 for k in ks}

    top = np.argpartition(-sims, top_k_max - 1, axis=1)[:, :top_k_max]
    sorted_top = np.take_along_axis(
        top, np.argsort(-sims[np.arange(len(q))[:, None], top], axis=1), axis=1
    )
    out = {}
    for k in ks:
        k_eff = min(k, top_k_max)
        hits = np.any(g_labels[sorted_top[:, :k_eff]] == q_lab_f[:, None], axis=1)
        out[f"recall@{k}"] = float(hits.mean())
    return out


def evaluate(query_images, query_labels, gallery_images, gallery_labels, encoder_fn, ks=(1, 5, 10)):
    q_emb = encode_all(query_images, encoder_fn)
    g_emb = encode_all(gallery_images, encoder_fn)
    return recall_at_k(q_emb, g_emb, np.array(query_labels), np.array(gallery_labels), ks)
```

## Zgłoś

```
[evaluation]
  num queries:   <int>
  num gallery:   <int>
  embedding_dim: <int>

[recall]
  recall@1:  <float>
  recall@5:  <float>
  recall@10: <float>
```

## Zasady

- Normalizuj osadzenie przed obliczeniem podobieństwa; FAISS IndexFlatIP na znormalizowanych wektorach jest równy cosinusowi.
- Jeśli w galerii nie ma etykiety opartej na podstawie zapytania, należy ją wykluczyć; w przeciwnym razie przypomnienie jest trywialnie ograniczone poniżej 1.
- Jeśli zapytanie i galeria nakładają się, wyklucz samo zapytanie z jego własnego górnego K lub zmierzysz samopodobieństwo, a nie wyszukiwanie.
- W przypadku `num_queries > 10,000` wsaduj matmul podobieństwa, aby uniknąć OOM.