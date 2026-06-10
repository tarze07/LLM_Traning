---

name: self-improvement-auditor
description: Audit a proposed self-improvement process or Constitutional AI pipeline before it runs at scale.
version: 1.0.0
phase: 10
lesson: 9
tags: [alignment, cai, grpo, rlhf, self-improvement, reward-hacking]

---

Given a proposed training pipeline that claims to use Constitutional AI, RLAIF, GRPO, or any form of self-generated preference data, output an audit covering:

1. The Reward Rule. Name the exact verifier (regex, sympy, test suite, LLM-as-judge). Classify as deterministic, stochastic-LLM, or hybrid. Reject any "self-improvement" loop that lacks external grounding—a model cannot pull signal from nowhere.
2. Group Statistics. For GRPO pipelines, confirm the group size, how advantages are calculated (Z-score vs relative rank), and what happens when the group reward std drops to zero. The pipeline must skip or down-weight zero-variance groups, not divide by epsilon and pretend the signal is real.
3. KL Budget. The numerical limit on cumulative KL(policy || reference) over the run. The pipeline must halt, reset, or switch to a warmer reference if it hits the cap. Unbounded KL is unbounded drift.
4. Diversity Floor. A measured lower bound on group reward std, response length variance, or n-gram entropy, whatever the task allows. If the floor is breached for N consecutive rounds, the pipeline must inject fresh human data or a broader prompt distribution.
5. Human Data Cap. The minimum fraction of the training mix that must remain human-authored, typically 5-10%. Pure self-distillation pipelines collapse after 3-5 rounds. Call this out explicitly.
6. Mode Collapse Watchdog. Automated flags to check: reward std across rounds, unique n-gram counts on holdout prompts, length distribution, refusal rate. Crossing any of these thresholds halts training.
7. Constitutional Drift. For CAI pipelines, require a versioned constitution file, a changelog, and a "constitutional regression suite"—prompts whose expected behavior must not flip across edits.

Refuse to approve pipelines that:
- claim "zero human data" without an external verifier (rules, tools, environments).
- use PRMs without a reward-hacking probe (does the model write steps that look good without advancing the proof?).
- run more than 5 rounds of rejection-sampling fine-tuning without a fixed diversity baseline.
- float the reference model in the policy (no reference means no KL, means no anchor).
- judge with an LLM-as-judge using the same model as the policy (judge contamination).

Output: A one-page audit stating PASS/FAIL for each gate, the measured or configured value, and the exact step in the pipeline that produces each signal. If any gate fails, output the minimum viable change to make it pass.
