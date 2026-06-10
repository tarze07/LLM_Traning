# Ścieżka szybkiego startu (Fast Track) do rozdziału LLMs from Scratch

Ta analiza przedstawia minimalną ścieżkę zależności (prerequisites) wymaganą, by szybko i bez utraty zrozumienia przejść bezpośrednio do sekcji **Phase 10: LLMs from Scratch** w tym programie nauczania.

---

## 🗺️ Rekomendowana Ścieżka Lekcji (Kluczowe Zależności)

Poniższe lekcje są niezbędne do zrozumienia matematyki i implementacji modeli językowych (np. GPT-2) od zera.

### 1. 🧠 Fundamenty Deep Learningu (Phase 3)
Bez tych podstaw napotkasz trudności przy implementacji sieci neuronowych i obsłudze bibliotek autogradu:
* [Phase 3 Lesson 03: Backpropagation from Scratch](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/03-deep-learning-core/03-backpropagation/docs/en.md)
* [Phase 3 Lesson 10: Build Your Own Mini Framework](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/03-deep-learning-core/10-mini-framework/docs/en.md)
* [Phase 3 Lesson 11: Introduction to PyTorch](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/03-deep-learning-core/11-intro-to-pytorch/docs/en.md)

### 2. 🔤 Przetwarzanie Języka Naturalnego (Phase 5)
Lekcje wprowadzające w wektoryzację słów oraz ewolucję mechanizmów seq2seq i uwagi:
* [Phase 5 Lesson 03: Word Embeddings (Word2Vec)](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/05-nlp-foundations-to-advanced/03-word-embeddings-word2vec/docs/en.md)
* [Phase 5 Lesson 09: Sequence-to-Sequence Models](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md)
* [Phase 5 Lesson 10: Attention Mechanism](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/05-nlp-foundations-to-advanced/10-attention-mechanism/docs/en.md)
* [Phase 5 Lesson 19: Subword Tokenization](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/05-nlp-foundations-to-advanced/19-subword-tokenization/docs/en.md)

### 3. ⚡ Architektura Transformerów (Phase 7)
Najważniejszy krok przygotowujący do budowy LLM. Skupia się na elementach składowych GPT:
* [Phase 7 Lesson 02: Self-Attention from Scratch](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/02-self-attention-from-scratch/docs/en.md)
* [Phase 7 Lesson 03: Multi-Head Attention](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/03-multi-head-attention/docs/en.md)
* [Phase 7 Lesson 04: Positional Encoding](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/04-positional-encoding/docs/en.md)
* [Phase 7 Lesson 05: The Full Transformer](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/05-full-transformer/docs/en.md)
* [Phase 7 Lesson 07: GPT (Causal LM)](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/07-gpt-causal-language-modeling/docs/en.md)
* [Phase 7 Lesson 12: KV Cache & Flash Attention](file:///home/tarze07/poligon/ai-engineering-from-scratch/phases/07-transformers-deep-dive/12-kv-cache-flash-attention/docs/en.md)

---

## 🚫 Działy, Które Możesz Bezpiecznie Pominąć

Te działy nie są wymagane do poprawnego zrozumienia i implementacji kodu w **Phase 10**:

1. **Phase 4 (Computer Vision)** – Sploty, YOLO, generowanie obrazów.
2. **Phase 6 (Speech and Audio)** – Modele dźwiękowe (np. Whisper).
3. **Phase 8 (Generative AI)** – Klasyczne modele generatywne (GANy, autokodery).
4. **Phase 9 (Reinforcement Learning)** – Klasyczne RL (Q-learning, etc.). Podstawy RL potrzebne do RLHF/DPO w lekcjach 10.07/10.08 są wyjaśniane bezpośrednio w tamtych materiałach.

---

> [!NOTE]
> Szczegółowy i pełny plan lekcji wraz z ich statusami znajdziesz w pliku głównym: [ROADMAP.md](file:///home/tarze07/poligon/ai-engineering-from-scratch/ROADMAP.md).
