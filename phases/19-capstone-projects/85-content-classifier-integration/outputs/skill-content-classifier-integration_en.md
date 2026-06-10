---

name: skill-content-classifier-integration
description: Three output-side classifiers (toxicity, PII, instruction-leakage) behind a single severity router with block, redact, warn, and log actions
version: 1.0.0
phase: 19
lesson: 85
tags: [safety, classifier, output-filter]

---

# Content Classifier Integration

Three classifiers, one router, four actions.

## Verdict Structure

```text
ClassifierVerdict
  name: str
  severity: none | low | medium | high
  score: float in [0, 1]
  findings: list[str]
```

## Action Table

| Severity | Action | Effect |
|---|---|---|
| high | block | output replaced by policy refusal |
| medium | redact | per-classifier redactors applied in sequence |
| low | warn | output delivered with a soft note appended |
| none | log | output shipped as-is, verdict recorded |

## Per-Classifier Behavior

- toxicity - harassment terms with whitespace boundary and small left-window negation check; redacts to `[redacted-language]`
- pii - email, phone, SSN, Luhn-validated card, IPv4; severity elevates for SSN and card; redacts each shape to a tag
- instruction-leakage - trigram cosine vs known system prompt; overlapping severity scales; redacts the first line of the system prompt

## Artifact

`outputs/classifier_report.json` holds the action verb, severity, redacted output, and full verdict list for each fixture.
