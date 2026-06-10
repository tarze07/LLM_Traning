---

name: skill-refusal-evaluation
description: Two-sided refusal metrics with calibration and category breakdown on a labeled prompt corpus
version: 1.0.0
phase: 19
lesson: 84
tags: [safety, evaluation, calibration]

---

# Refusal Evaluation

A labeled set of safe and unsafe prompts passes through one or more model policies. The outputs are classified as refusals or answers. The framework returns:

- under-refusal: answered unsafe prompts / total unsafe
- over-refusal: refused safe prompts / total safe
- accuracy: (correct refusals + correct answers) / total
- ECE: Expected Calibration Error binned on stated confidence
- under-refusal per category: joined against Lesson 82 taxonomy

## Hooking Up a Real Model

The mock LLM is a callable `(prompt: str) -> str`. Replace it with an HTTP wrapper that returns the model output and embeds a confidence tag (or modify `parse_confidence` to read whatever your provider exposes). Everything else remains identical.

## Artifact

`outputs/refusal_eval_report.json` holds the per-policy metrics. Lesson 87 reads this report to set thresholds.
