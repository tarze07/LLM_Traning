---

name: skill-llm-evaluation
description: A decision framework for choosing the right LLM evaluation strategy based on task type, budget, and requirements.
version: 1.0.0
phase: 10
lesson: 10
tags: [evaluation, evals, benchmarks, llm-as-judge, elo, metrics]

---

# LLM Evaluation Strategy

When evaluating an LLM system, use this decision framework to select the right approach.

## When to Use Each Eval Type

**Benchmarks (MMLU, HumanEval, SWE-bench):** You are doing initial model selection. You need to narrow 10 potential models down to 3. Benchmarks give you a rough ranking at zero cost. Do not use benchmarks as your final evaluation.

**Custom Evals:** You are building for production. You have a specific task with specific failure modes. Custom evals are the only evaluation that predicts real-world performance. Minimum 50 test cases for a prototype, 200+ for production.

**LLM-as-a-Judge:** Your task is open-ended (summarization, writing, conversation). Exact match and token overlap metrics are too rigid. LLM-as-a-judge costs ~$0.01 per judgment and agrees with humans ~80% of the time. Always use structured rubrics, not vague prompts.

**Human Evals:** The stakes are high, and automated metrics are disagreeing with each other. Human eval is the ground truth, but it costs $0.10-$2.00 per judgment. Reserve for ambiguous cases and periodic calibration of your automated metrics.

**ELO from Pairwise Comparisons:** You are comparing multiple models on the same task. Pairwise is more reliable than absolute scoring because humans (and LLM judges) are better at relative evaluation.

## Scoring Function Selection

- **Exact Match**: Classification, entity extraction, structured outputs with known answers
- **Token F1**: Extraction tasks where partial credit matters
- **ROUGE-L**: Summarization, translation
- **BLEU**: Machine translation
- **LLM-as-a-Judge**: Open-ended generation, conversational quality, helpfulness
- **Execution-based**: Code generation (run the code, check if tests pass)
- **Schema Validation**: Structured outputs (does the JSON match the schema?)

## Red Flags in Eval Design

- Eval set smaller than 50 cases: The results are statistically meaningless
- No edge cases: You are measuring happy-path performance, which is always higher than real-world
- Single metric: Different metrics tell different stories, use at least two
- No versioning: You cannot track improvements without versioned eval suites
- Eval set contamination: Never include eval examples in your fine-tuning data or few-shot prompts
- Testing only one model: You need a baseline (even a simple heuristic) to compare against

## Eval Pipeline Checklist

1. Define the task precisely (not "answer questions", but "triage support tickets into 5 categories")
2. Build test cases across happy path, edge cases, and known regressions
3. Select 2-3 scoring functions appropriate for the task type
4. Set pass/fail thresholds based on production requirements
5. Automate execution: a single command runs the entire suite
6. Version everything: test cases, scoring functions, prompts, model versions
7. Run on every change: prompt updates, model swaps, code deployments
8. Track trends: a single score is noise, a trendline is signal
9. Calibrate against human evaluation quarterly
10. Add regression cases whenever a production failure is detected
