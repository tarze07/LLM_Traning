---

name: skill-end-to-end-safety-gate
description: Three-checkpoint safety gate composing an input detector, streaming token filter, output classifier, and rules engine with deterministic aggregation table and per-request trace
version: 1.0.0
phase: 19
lesson: 87
tags: [safety, harness, composition]

---

# End-to-End Safety Gate

## Lifecycle

1. pre-gen - run Lesson 83 detector on prompt
   - if confidence >= block_threshold: return refusal, emit trace, halt
2. during-gen - stream from model, buffer two chunks, scan for known harmful continuations
   - if matched: terminate iterator, flag trace, treat as medium severity
3. post-gen - if no early termination, run Lesson 85 classifier router and Lesson 86 rules engine on completed output
4. aggregate - take max severity across pre, during, post.classifier, post.rules
5. apply - map to block, redact, warn, or allow

## Aggregation Table

| Signal State | Action |
|---|---|
| any high severity | block |
| any medium severity | redact |
| any low severity | warn |
| none | allow |

## Trace Structure

```text
RequestTrace
  request_id: str
  prompt: str
  pre_gen: { category, confidence, fired[] }
  during_gen: { terminated_early, matched_pattern, partial_chunks }
  post_gen: { classifier_action, classifier_severity, rules_max_severity, rules_violations[] } | null
  final_action: block | redact | warn | allow
  final_output: str
  latency_ms: float
```

## Artifact

`outputs/gate_trace.json` holds the summary and one trace per request, including 50 taxonomy fixtures and 10 benign prompts.
