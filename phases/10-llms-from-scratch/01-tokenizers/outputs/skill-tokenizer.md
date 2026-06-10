---

name: skill-tokenizer
description: Selecting and building tokenizers for LLM projects
version: 1.0.0
phase: 10
lesson: 1
tags: [tokenizer, bpe, wordpiece, sentencepiece, llm, nlp]

---

# Tokenizer Selection and Implementation

When starting an LLM project, use this decision framework for selecting a tokenizer.

## When to Use Each Tokenizer

**Byte-level BPE (tiktoken):** You are building or fine-tuning models from the GPT family. You need guaranteed support for any input byte sequence. You do not want any unknown tokens.

**WordPiece (Hugging Face):** You are working with BERT-family models for classification, NER, or embedding tasks. You need the "##" continuation prefix for downstream tasks that rely on word boundary signals.

**SentencePiece (BPE or Unigram):** You are training from scratch. You need language-independent tokenization. Your data includes CJK languages, Thai, and other scripts without whitespace. LLaMA, T5, and most multilingual models use this.

## Vocabulary Size Guidelines

- 32K tokens: Good default for monolingual models, keeps the embedding layer small
- 50K–64K tokens: Better for multilingual or code-heavy models
- 100K+ tokens: Only if you have massive training data and want short sequences

A larger vocabulary means shorter sequences (cheaper inference), but more parameters in the embedding matrix. For a 100K vocabulary with a 4096-dimensional embedding, the embedding layer alone has 400M parameters.

## Pre-tokenization Rules That Matter

1. Split whitespace before BPE to prevent cross-word merges
2. Split digits individually if you want the model to learn arithmetic
3. Normalize Unicode (NFC) before tokenization for consistent behavior
4. Add special tokens for your use case: `<pad>`, `<eos>`, `<bos>`, `<unk>`, and any task-specific tags

## Warning Signs in Tokenizer Behavior

- Fertility above 2.0 for your target language: The model is wasting context window
- Common domain words split into 3+ tokens: Retrain with domain data
- Inconsistent number tokenization: Check digit splitting rules
- Large vocabulary with many one-off tokens: Reduce vocabulary size

## Building a Custom Tokenizer - Checklist

1. Collect representative training data (at least 1 GB of text in the target domain)
2. Choose an algorithm: BPE for general use, Unigram for multilingual use
3. Set vocabulary size based on the guidelines above
4. Configure pre-tokenization: whitespace splitting, digit handling, punctuation
5. Add special tokens
6. Train using the Hugging Face tokenizers library (Rust backend, fast)
7. Validate: check round-trip retention across all target languages
8. Test edge cases: empty string, very long input, binary data, emoji, RTL text
9. Save and version the tokenizer along with model checkpoints
