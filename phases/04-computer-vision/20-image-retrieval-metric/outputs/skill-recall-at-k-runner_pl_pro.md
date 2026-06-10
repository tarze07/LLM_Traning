---

name: skill-recall-at-k-runner
description: Szablon skryptu ewaluacyjnego do wyznaczania metryki Recall@K z uwzględnieniem zbiorów uczącego, walidacyjnego oraz referencyjnego
version: 1.0.0
phase: 4
lesson: 20
tags: [retrieval, evaluation, recall, faiss]

---

# Ewaluator Recall@K (Recall@K Runner)

Przekształć zbiór obrazów zapytań (query), katalogu referencyjnego (gallery) oraz przypisanych etykiet w powtarzalną ewaluację metryki Recall@K.

## Zastosowanie

- Weryfikacja jakości pierwszego modelu bazowego (backbone) w zadaniu wyszukiwania.
- Monitorowanie jakości embeddingów na przestrzeni kolejnych epok szkoleniowych.
- Porównanie skuteczności dwóch alternatywnych systemów Image Retrieval na tym samym zbiorze danych.

## Dane wejściowe

- `query_images`: lista ścieżek do obrazów zapytań.
- `gallery_images`: lista ścieżek do obrazów z galerii (zbiory zapytań i galerii mogą się częściowo nakładać).
- `query_labels`, `gallery_labels`: etykiety klas lub identyfikatory instancji.
- `encoder_fn`: funkcja lub obiekt wywoływalny przekształcający obraz w embedding (generowany w locie lub pobierany z pamięci podręcznej).
- `ks`: lista analizowanych stopni odcięcia (np. `[1, 5, 10]`).

## Algorytm działania

1. Wygeneruj embeddingi dla wszystkich obrazów z galerii referencyjnej i zapisz je jako tablicę NumPy.
2. Wygeneruj embeddingi dla obrazów zapytań.
3. Znormalizuj normą L2 wektory obu zestawów.
4. Dla każdego zapytania oblicz podobieństwo względem każdego elementu galerii.
5. Posortuj wyniki malejąco i wybierz podzbiór o rozmiarze równym maksymalnemu K ze wskazanej listy.
6. Dla każdej wartości K sprawdź, czy przynajmniej jeden z K najbliższych sąsiadów w galerii posiada taką samą etykietę jak zapytanie.
7. Oblicz końcową metrykę `Recall@K = odsetek zapytań, które uzyskały przynajmniej jedno poprawne dopasowanie w TOP K`.

## Szablon kodu

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

## Format raportu

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

## Zasady i dobre praktyki

- Zawsze normalizuj embeddingi przed wyznaczeniem podobieństwa; indeks `FAISS IndexFlatIP` uruchomiony na znormalizowanych wektorach odpowiada metryce cosinusowej.
- Jeśli w galerii referencyjnej nie ma ani jednej próbki z danej klasy zapytania, wyklucz to zapytanie z procesu ewaluacji; w przeciwnym wypadku Recall@K będzie sztucznie zaniżony.
- Jeżeli obrazy zapytań i galerii się nakładają (np. zapytanie pochodzi z galerii), wyklucz samopodobieństwo (szukanie samego siebie) z wyników TOP-K, aby uniknąć fałszywego zawyżenia wyników.
- W przypadku gdy liczba zapytań `num_queries > 10 000`, przetwarzaj mnożenie macierzy podobieństwa paczkami (batching), aby zapobiec wyczerpaniu pamięci (OOM).
