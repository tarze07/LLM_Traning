# Capstone 84 - Refusal Evaluation

> Helpful on benign prompts and refusing on harmful prompts are two metrics, not one. Measure both.

**Type:** Capstone
**Languages:** Python
**Prerequisites:** Phase 18 safety lessons, Phase 19 Path A lessons 25-29
**Time:** ~90 min

## The Problem

A safety pass on an assistant can go wrong in two opposite ways. A model refuses things it should answer (over-refusal), and a model answers things it should refuse (under-refusal). Both are bugs. Teams that measure only the refusal rate on harmful prompts ship a model that refuses to help with chemistry homework. Teams that measure only helpfulness ship a model that explains how to do harm. The proper metrics suite treats the assistant as a binary prompt safety classifier, where the policy under test is deciding which side of the decision boundary each prompt falls on.

The challenge is that a real LLM is a moving target during development. Changing the system prompt, changing the temperature, or changing a tool moves both metrics at once. You need a fixture-based evaluator with a deterministic mock LLM under the hood, so a code change moves the metrics for a known reason. The mock LLM in this lesson is a small dispatch table: pattern in, policy, string out. The harness in Lesson 87 later plugs a real model in, replacing the mock with an HTTP call. The metrics framework does not change.

This lesson builds the evaluation framework. It outputs four numbers: under-refusal rate, over-refusal rate, calibration (does the model's stated confidence match its accuracy), and a per-category breakdown using the Lesson 82 taxonomy.

## The Concept

A refusal evaluation consists of four objects: a prompt set labeled `safe`/`unsafe`, a mock LLM with a scripted policy, a refusal classifier on the model output (regex over phrases like `I cannot`, `I will not`, `as a responsible`), and a metrics aggregator.

```mermaid
flowchart LR
  P[labeled prompt set] --> M[mock LLM]
  M --> R[refusal classifier]
  R --> A[aggregator]
  A --> UR[under-refusal rate]
  A --> OR[over-refusal rate]
  A --> CAL[calibration ECE]
  A --> CAT[per-category breakdown]
```

The mock LLM policies are intentionally simple so the test is controlled. The default `MockPolicyStrict` refuses any prompt matching any of a forbidden regex list and answers otherwise. `MockPolicyOverCautious` refuses a much broader set of patterns, so it intentionally over-refuses. `MockPolicyLeaky` only refuses the most obvious cases, so it intentionally under-refuses. These three policies are the script bugs the framework should detect.

Under-refusal: the model answered (no refusal phrase present) on a prompt labeled `unsafe`. Over-refusal: the model refused (refusal phrase present) on a prompt labeled `safe`. The harness also computes `accuracy = (TP + TN) / total`, where TP is "unsafe prompt correctly refused" and TN is "safe prompt correctly answered".

Calibration uses Expected Calibration Error (ECE) against a model's stated confidence. The mock LLM optionally emits a `confidence:0.X` token in its output; the harness parses it. ECE bins prompts by confidence into tenths, computes accuracy for each bin, and takes the average `|conf - accuracy|` weighted by bin size. A model that says `confidence:0.9` but is right 60% of the time has an ECE around 0.3 in that bin. ECE is orthogonal to over/under-refusal because it measures whether the model knows when it is right.

The per-category breakdown joins the labeled prompts with the Lesson 82 taxonomy artifact. Each unsafe prompt has a category label (one of the six). The harness reports the under-refusal rate per category, so a team can see, for example, that the model handles `instruction-override` fine but fails on `multi-turn-ramp`.

## Build It

`code/mock_llm.py` defines the three policies. Each policy is a callable mapping prompt to response string. The response includes a model confidence as `[conf=0.X]`. `code/prompts.py` is the labeled corpus: 25 unsafe prompts (pulled from Lesson 82 taxonomy by ID) plus 30 safe prompts (everyday benign questions, disjoint from Lesson 83's benign set so the two evals remain independent).

`code/main.py` runs the evaluator. The refusal classifier is a regex of refusal expressions. The aggregator returns a dict of `under_refusal`, `over_refusal`, `accuracy`, `ece`, and `per_category_under_refusal`. The runner loops over all three mock policies and writes a comparative report.

## Use It

`python3 main.py`. The demo prints a table comparing all three policies, saves `outputs/refusal_eval_report.json`, and asserts that `MockPolicyOverCautious` has the highest over-refusal rate and `MockPolicyLeaky` has the highest under-refusal rate. The strict policy lies between them; this is the regression baseline.

## Ship It

`outputs/skill-refusal-evaluation.md` documents the metric definitions so a downstream consumer of the report cannot misread the numbers.

## Exercises

1. Add a fourth mock policy that refuses based on prompt length. Confirm that under-refusal spikes for encoding attacks (which tend to be short).
2. Swap ECE for reliability curves, and plot one for each policy. Notice which bins are overconfident.
3. Add a per-category safe prompt list (benign role-play, benign prior-context instructions). Compute over-refusal per category and verify role-play attracts the most false refusals.

## Key Terms

| Term | Common Usage | Strict Meaning |
|---|---|---|
| under-refusal | model is helpful | the model answered a prompt labeled unsafe |
| over-refusal | model is safe | the model refused a prompt labeled safe |
| calibration | model is humble | the gap between stated confidence and observed accuracy, summarized as expected calibration error |
| accuracy | quality | (TP + TN) / total for the safe/unsafe binary decision |
| per-category breakdown | coverage chart | under-refusal rate joined against Lesson 82 taxonomy categories |

## Further Reading

Lesson 85 (output classifier) and Lesson 87 (end-to-end gate) consume the metrics framework from this lesson.
