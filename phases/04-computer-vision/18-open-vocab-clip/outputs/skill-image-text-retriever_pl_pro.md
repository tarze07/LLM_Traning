---

name: skill-image-text-retriever
description: Zbuduj indeks wektorowy obrazów przy użyciu modelu CLIP, obsługujący zapytania tekstowe i obrazkowe
version: 1.0.0
phase: 4
lesson: 18
tags: [clip, retrieval, faiss, zero-shot]

---

# Wyszukiwanie obrazów i tekstu (Image-Text Retriever)

Przekształć katalog z obrazami w przeszukiwalny indeks wektorowy przy użyciu reprezentacji (embeddings) CLIP.

## Kiedy stosować

- Budowa systemu wyszukiwania obrazów zero-shot w wewnętrznym katalogu produktów lub plików.
- Deduplikacja wizualnie zbliżonych obrazów na podstawie odległości między ich wektorami cech.
- Wdrożenie szybkiego wyszukiwania podobnych obrazów bez konieczności posiadania oznakowanego zbioru danych.

## Dane wejściowe

- `image_folder`: ścieżka do katalogu z obrazami.
- `clip_model`: identyfikator modelu na platformie Hugging Face (np. `openai/clip-vit-base-patch32` lub `google/siglip-base-patch16-224`).
- `index_type`: Flat (płaski) | IVF (Inverted File Index) | HNSW (Hierarchical Navigable Small World).
- `embedding_dim`: wymiarowość wektorów cech (pobierana automatycznie z modelu).

## Procedura krok po kroku

1. Wczytaj model CLIP oraz powiązany z nim procesor danych.
2. Przetwórz wsadowo (w paczkach) wszystkie obrazy w katalogu. Zapisz wygenerowane wektory cech jako macierz float32 o wymiarach `(N, D)` oraz listę powiązanych nazw plików.
3. Utwórz indeks FAISS dla wygenerowanych wektorów. Użyj metryki iloczynu wewnętrznego (Inner Product) na wektorach znormalizowanych L2, aby uzyskać podobieństwo cosinusowe.
4. Udostępnij dwie metody wyszukiwania:
   - `search_by_text(text, k)` — wyszukiwanie obrazów na podstawie zapytania tekstowego.
   - `search_by_image(image_path, k)` — wyszukiwanie obrazów na podstawie obrazu wejściowego (zapytanie wizualne).

## Kod szablonu

```python
import os
import glob
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import faiss


class ImageTextRetriever:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.model = CLIPModel.from_pretrained(model_name).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.dim = self.model.config.projection_dim
        self.index = None
        self.filenames = []

    @torch.no_grad()
    def _encode_images(self, paths, batch=16):
        embs = []
        for i in range(0, len(paths), batch):
            imgs = [Image.open(p).convert("RGB") for p in paths[i:i + batch]]
            inputs = self.processor(images=imgs, return_tensors="pt")
            out = self.model.get_image_features(**inputs)
            out = out / out.norm(dim=-1, keepdim=True)
            embs.append(out.cpu().numpy())
        return np.concatenate(embs).astype(np.float32)

    @torch.no_grad()
    def _encode_text(self, texts):
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        out = self.model.get_text_features(**inputs)
        out = out / out.norm(dim=-1, keepdim=True)
        return out.cpu().numpy().astype(np.float32)

    def build_index(self, folder, index_type="flat"):
        exts = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp")
        files = []
        for ext in exts:
            files.extend(glob.glob(os.path.join(folder, ext)))
        self.filenames = sorted(files)
        embs = self._encode_images(self.filenames)
        if index_type == "IVF":
            quantizer = faiss.IndexFlatIP(self.dim)
            nlist = min(256, max(4, len(embs) // 32))
            self.index = faiss.IndexIVFFlat(quantizer, self.dim, nlist)
            self.index.train(embs)
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(self.dim, 32, faiss.METRIC_INNER_PRODUCT)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(embs)

    def search_by_text(self, text, k=5):
        q = self._encode_text([text])
        dist, idx = self.index.search(q, k)
        return [(self.filenames[i], float(d)) for d, i in zip(dist[0], idx[0])]

    def search_by_image(self, image_path, k=5):
        q = self._encode_images([image_path])
        dist, idx = self.index.search(q, k)
        return [(self.filenames[i], float(d)) for d, i in zip(dist[0], idx[0])]
```

## Format raportu

```
[retriever]
  model:          <name>
  num_images:     <int>
  dim:            <int>
  index_type:     flat | IVF | HNSW
  index_size_mb:  <float>
```

## Zasady i ograniczenia

- Zawsze normalizuj wektory cech (L2) przed dodaniem ich do indeksu; iloczyn wewnętrzny (Inner Product) w bibliotece FAISS liczony dla wektorów o długości jednostkowej jest równoważny podobieństwu cosinusowemu.
- Dla zbiorów zawierających poniżej 100 tysięcy obrazów indeks płaski `FlatIP` (dokładne dopasowanie) jest najprostszy i najszybszy.
- Dla zbiorów o rozmiarze od 100 tysięcy do 10 milionów obrazów standardowym kompromisem między szybkością a dokładnością jest indeks `IVF`.
- Dla zbiorów powyżej 10 milionów obrazów należy zastosować indeks `HNSW` lub indeksy wykorzystujące kwantyzację wektorową (Product Quantization - PQ).
- Nigdy nie buduj indeksu od nowa przy każdym zapytaniu; stwórz indeks (oblicz wektory) raz, a następnie wielokrotnie wykonuj na nim wyszukiwanie.
