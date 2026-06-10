---

name: prompt-data-quality-checker
description: Check and debug data quality in LLM pre-training pipelines
version: 1.0.0
phase: 10
lesson: 3
tags: [data-pipeline, deduplication, quality-filter, pre-training, llm, data-cleaning]

---

# Data Quality Checker for LLM Pre-training

When building or auditing a data pipeline for LLM pre-training, use this framework to catch issues before they reach the model.

## Pipeline Output Red Flags

**Deduplication removed less than 20% of web data.** Common Crawl typically contains 30-40% duplicates. If your deduplication step removes less than 20%, your MinHash parameters are too conservative or your threshold is too high. Check: shingle size k, number of hash functions, number of LSH bands, Jaccard threshold.

**Compression ratio below 2.0 chars/token.** This means your tokenizer splits too aggressively. Either retrain with more merges, increase the vocabulary size, or check if pre-tokenization is unnecessarily fragmenting text.

**Compression ratio above 6.0 chars/token.** Your tokenizer learned highly domain-specific merges that cannot be generalized. This is fine for a domain-specific model but a red flag for general-purpose models.

**Sequence utilization below 90%.** Too much padding. Either your documents are very short (filter them out or increase minimum document length), or sequence packing is inefficient (switch from naive padding to multi-document packing).

**Vocabulary utilization below 50%.** Over half of your vocabulary is unused in this corpus. Either the vocabulary is too large for your domain, or the tokenizer was trained on very different data.

## Quality Filter Calibration

Run the following checks on a random sample of 1,000 documents at each pipeline stage:

1. **After cleaning, read 20 random documents.** Do they contain leftover HTML, JavaScript, navigation text, or boilerplate? If so, HTML stripping is incomplete.

2. **Read 20 random documents that PASSED the quality filter.** Are any of them spam, keyword lists, or machine-generated? If so, tighten the filter thresholds.

3. **Read 20 random documents that FAILED the quality filter.** Are any of them actually good? If so, your filter is too aggressive. Relax thresholds or add exceptions for specific patterns.

4. **Read 20 random near-duplicate pairs from dedup.** Are they actually similar? If not, lower the Jaccard threshold or increase the number of hash functions.

## Data Mixing Ratios

There is no universal formula. Start with these baselines and adjust based on evaluation:

| Category | Llama 3 Ratio | Starting Point |
|---------|-------------|----------------|
| Web Text | 50% | 50% |
| Code | 25% | 15-25% |
| Books/Academic | 13% | 10-15% |
| Math | 8% | 5-10% |
| Multilingual Web | 4% | 5-10% |

Increase the code ratio if the model should code well. Increase the math ratio if reasoning matters. Decrease the web ratio if you need less noise. Always evaluate on benchmarks after changing ratios.

## Scaling Estimates

For a given number of target tokens:

- 1T tokens from the web: Expect ~3-5TB raw text, ~1.5-2TB after cleaning and deduplication
- Tokenization speed (Rust): ~100M tokens/second per core
- Tokenization speed (Python): ~1-10M tokens/second per core
- MinHash Deduplication at 128 hashes, 16 bands: ~10k docs/second per core
- Sequence packing: I/O bound, for corpora over 10GB use memory-mapped files

For 15T tokens (Llama 3 scale), plan for ~30-50TB of raw input data, 1-2 weeks of preprocessing on a 64-core machine, and over 100TB of disk for intermediate files.

## Pre-training Checklist

1. Total token count matches your compute budget (use Chinchilla scaling or Llama 3's overtraining ratio as guidelines)
2. Dedup removed 30-40% of web data
3. Quality filter removed 10-20% of remaining data
4. Compression ratio is 3-5 chars/token for English
5. Sequence utilization exceeds 95%
6. Random spot checks show clean and coherent text at each pipeline stage
7. Data mixing ratios were validated in a small-scale training run
8. PII removal was verified on a sample
9. All binary formats (packed sequences, token ID arrays) pass encode/decode round-trip tests
10. The pipeline is reproducible: the same input yields identical output with fixed random seeds
