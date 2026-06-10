---

name: prompt-tokenizer-builder
description: Build and debug production-grade tokenizers for LLM projects
version: 1.0.0
phase: 10
lesson: 2
tags: [tokenizer, bpe, byte-level, special-tokens, chat-template, multilingual]

---

# Production Tokenizer Builder

When building or debugging a tokenizer for an LLM project, follow this framework.

## Pipeline Checklist

Every production tokenizer needs these five stages. If any is missing, you will hit edge cases in production.

1. **Normalize** - Apply Unicode NFKC normalization. This collapses ligatures ("fi" -> "fi"), normalizes full-width characters, and standardizes whitespace. Skip this, and the same word will get different token IDs depending on how it was typed.

2. **Pre-tokenize** - Split text into chunks before BPE. Use a GPT-2 style regex pattern for English-focused models. Use SentencePiece's raw byte approach for multilingual models. This choice determines if BPE can merge across word boundaries.

3. **BPE Merge** - Apply the learned merge table to the byte sequences within each chunk. The merge table IS the tokenizer's learned knowledge. Everything else is plumbing.

4. **Special Token Injection** - Match special tokens exactly before running BPE. [BOS], [EOS], [PAD], and chat template tags get fixed IDs. They never participate in merges.

5. **ID Mapping** - Convert token strings to integers. The model only sees integers.

## Debugging Tokenizer Issues

**Symptom: The model generates garbage on chat inputs**
- Check the chat template. Every model has a different format. Llama 3 uses `<|start_header_id|>` tags. ChatGPT uses `<|im_start|>` tags. A wrong template puts the input out of the training distribution.

**Symptom: Non-English text uses too many tokens**
- Check the fertility (tokens per word). Above 2.0 means the tokenizer is wasting the context window in that language. Solutions: retrain with more multilingual data, increase vocabulary size, or use SentencePiece with Unigram.

**Symptom: Numbers and arithmetic fail**
- Check how digits are tokenized. "1234" as a single token means the model cannot do digit-level operations. Split digits individually during pre-tokenization.

**Symptom: Code tokens are inefficient**
- Check how indentation is handled. The GPT-2 tokenizer wastes tokens on spaces. Codex and StarCoder use special indentation tokens (4 spaces = 1 token).

## Vocabulary Size Decision

- 32K tokens: Monolingual, small model, constrained compute. Embedding layer has 32K * d_model parameters.
- 50K-64K: Multilingual or code-heavy. Good balance for most projects.
- 100K+ (GPT-4, Llama 3): Only with massive training data. Shorter sequences, but 100K * d_model embedding parameters.

For a 4096-dimensional model: 32K vocab = 131M embedding parameters. 128K vocab = 524M embedding parameters. That's a 400M parameter difference in the embedding layer alone.

## Speed Requirements

- Training data tokenization: Use Rust-based libraries (tiktoken, HuggingFace tokenizers). Pure Python is 10-100x slower.
- Inference tokenization: Latency matters less (single sequence), but still use compiled implementations.
- Benchmark: Tokenize 1GB of text and measure wall-clock time. If it takes more than 60 seconds, switch to a Rust backend.

## Chat Template Validation

Before deploying any chat model, validate its template:

1. Encode a known conversation with the tokenizer
2. Decode it back to text
3. Compare character-by-character with the expected format from the model's documentation
4. Look out for: newlines after header tokens, spaces before content, turn-end tags
5. Edge test cases: empty system prompt, very long user message, multiple assistant turns

A misaligned chat template is the most common cause of degraded chat model performance.
