---

name: skill-prompt-injection-detector
description: Layered detector pipeline that returns a category and confidence for any prompt, with measurable precision and recall
version: 1.0.0
phase: 19
lesson: 83
tags: [safety, detector, prompt-injection]

---

# Prompt Injection Detector

A detector here is a function from prompt to verdict. The verdict carries a category from the Lesson 82 taxonomy and a confidence in [0, 1].

## The Pipeline

1. Normalize - strip zero-width chars, undo homoglyphs, decode base64/hex, fold leet-speak digits, attempt rot13 against a common-word sanity check.
2. Substring Rules - hand-written needles like `ignore previous`, `from now on you are`, `decode this base64`.
3. Regex Rules - token-level patterns like `\bignor\w*\s+(all|prior|previous|earlier)\b`.

Aggregation takes the max score per category, and returns the highest scoring category, or `benign` if nothing fires.

## Adding a Rule

Edit `code/rules.py`. A rule is a dictionary with `name`, `category` (one of the six taxonomy categories), `score` (float 0 to 1), and one of `substring` or `regex`. Rerun `main.py` to see the impact on category precision and recall.

## Artifact

`outputs/detector_report.json` is the per-category metrics file. The end-to-end gate in Lesson 87 reads this to threshold confidences.
