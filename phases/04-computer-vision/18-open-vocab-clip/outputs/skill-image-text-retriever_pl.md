---

name: skill-image-text-retriever
description: Zbuduj indeks osadzania obrazu z dowolnym punktem kontrolnym CLIP; obsługuje zapytania według tekstu i zapytania według obrazu
version: 1.0.0
phase: 4
lesson: 18
tags: [clip, retrieval, faiss, zero-shot]

---

# Funkcja pobierania obrazu i tekstu

Zamień folder obrazów w indeks z możliwością przeszukiwania, korzystając z osadzania CLIP.

## Kiedy używać

- Budowanie wyszukiwania obrazów typu zero-shot w wewnętrznym katalogu.
- Deduplikacja niemal identycznych obrazów poprzez osadzanie odległości.
- Budowanie szybkiego komponentu „znajdź podobny” bez oznaczonego zestawu danych.

## Wejścia

- `image_folder`: katalog plików obrazów.
- `clip_model`: Identyfikator HuggingFace, taki jak `openai/clip-vit-base-patch32` lub `google/siglip-base-patch16-224`.
- `index_type`: płaski | Zapłodnienie in vitro | HNSW.
- `embedding_dim`: wywnioskowany z modelu.

## Kroki

1. Załaduj model CLIP i preprocesor.
2. Zakoduj wsadowo każdy obraz w folderze. Zapisz osadzenia jako (N, D) float32 + lista nazw plików.
3. Zbuduj indeks FAISS na osadzonych elementach. Użyj iloczynu wewnętrznego na wektorach znormalizowanych L2 dla podobieństwa cosinus.
4. Udostępnij dwa interfejsy zapytań:
   - `search_by_text(text, k)` — wstaw tekst, wyszukaj.
   - `search_by_image(image_path, k)` — wstaw obraz, wyszukaj.

## Szablon wyjściowy

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

## Zgłoś

```
[retriever]
  model:          <name>
  num_images:     <int>
  dim:            <int>
  index_type:     flat | IVF | HNSW
  index_size_mb:  <float>
```

## Zasady

- Zawsze normalizuj osadzanie L2 przed indeksowaniem; Iloczyn wewnętrzny FAISS na znormalizowanych wektorach jest równy cosinusowi podobieństwa.
- W przypadku < 100k images, PHIC10 (exact) is simplest and fastest.
- For 100k-10M, PHIC11 is the standard trade-off.
- For > 10M należy zastosować HNSW lub wariant skwantowany według produktu.
- Nigdy nie buduj indeksu przy każdym zapytaniu; osadzić raz, szukać wiele razy.