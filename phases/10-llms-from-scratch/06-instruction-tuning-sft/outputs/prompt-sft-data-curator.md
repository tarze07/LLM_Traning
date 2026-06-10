---

name: prompt-sft-data-curator
description: Design and curate instruction datasets for supervised fine-tuning
version: 1.0.0
phase: 10
lesson: 6
tags: [sft, instruction-tuning, fine-tuning, data-curation, alignment]

---

# SFT Data Curator

When designing an instruction tuning dataset for a specific capability (code generation, math, conversation, safety), use this framework to plan data collection, define quality criteria, and structure the training pipeline.

## Input Requirements

Provide:
- **Target Capability** (e.g., "Python code generation", "medical Q&A", "multi-turn conversation")
- **Base Model** (e.g., Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Budget** (annotation hours, API costs for synthetic generation)
- **Format Preferences** (Alpaca, ShareGPT, ChatML)

## Step 1: Dataset Design

### Size Guidelines

| Quality Level | Examples Needed | Expected Outcome |
|-------------|----------------|--------------------------------|
| Research Prototype | 1,000-5,000 | LIMA quality: competitive with larger datasets if examples are expert-written |
| Production v1 | 10,000-50,000 | Stanford Alpaca level: solid instruction following for common tasks |
| Production v2 | 50,000-200,000 | Vicuna/Llama 2 Chat level: robust multi-turn, domain coverage |

Quality always beats quantity. 1,000 expert-written examples (LIMA, May 2023) matched models trained on 50,000+ examples. Prioritize:

1. **Diversity** - Covers the full range of the target capability
2. **Accuracy** - Every response must be factually correct
3. **Clarity** - Responses should be concise and well-structured
4. **Difficulty** - Includes easy, medium, and hard examples

### Diversity Checklist

For a general-purpose assistant:
- Open-ended generation (20%)
- Factual Q&A (20%)
- Creative writing (10%)
- Code generation (15%)
- Reasoning and math (15%)
- Summarization (10%)
- Instruction following with constraints (10%)

Adjust percentages for domain-specific models. A coding assistant might allocate 60% to code generation and 20% to code explanation.

## Step 2: Data Format

### Alpaca Format (single-turn)

```json
{
  "instruction": "Write a function that reverses a string in Python.",
  "input": "",
  "output": "def reverse_string(s):\n    return s[::-1]"
}
```

Use when: Single-turn tasks, straightforward instruction-response pairs, quick prototyping.

### ShareGPT Format (multi-turn)

```json
{
  "conversations": [
    {"from": "system", "value": "You are a Python expert."},
    {"from": "human", "value": "How do I reverse a string?"},
    {"from": "gpt", "value": "Use slicing: s[::-1]"},
    {"from": "human", "value": "What about for a list?"},
    {"from": "gpt", "value": "Same syntax works: my_list[::-1]"}
  ]
}
```

Use when: Conversational applications, multi-turn context is important.

### ChatML Format (with special tokens)

```
<|im_start|>system
You are a Python expert.<|im_end|>
<|im_start|>user
How do I reverse a string?<|im_end|>
<|im_start|>assistant
Use slicing: s[::-1]<|im_end|>
```

Use when: Targeting models that natively use ChatML (Qwen, Yi).

## Step 3: Quality Criteria

### Example-level Checks

1. **Relevance**: Does the response actually address the instruction?
2. **Factual Accuracy**: Are all claims verifiable and correct?
3. **Completeness**: Does the response fully address the instruction?
4. **Conciseness**: Could the same information be conveyed in fewer words?
5. **Format Consistency**: Does the response follow the expected style?

### Red Flags (Reject Example)

- Response contradicts itself
- Response includes harmful content without refusal
- Response hallucinates facts or citations
- Instruction is ambiguous and response does not clarify
- Response is a copy of a rephrased instruction

### Dataset-level Checks

- No more than 5% of examples from a single source/template
- At least 80% of response tokens carry meaning (not padding)
- Average response length is 50-200 tokens (avoid very short or very long)
- System prompt diversity: at least 10 different system prompts represented

## Step 4: Training Configuration

| Parameter | Recommended Range | Notes |
|----------|--------------------------------|-------|
| Learning Rate | 1e-5 to 5e-5 | Lower for larger models (1e-5 for 70B, 5e-5 for 7B) |
| Epochs | 1-3 | Monitor validation loss, stop at first sign of increase |
| Batch Size | 32-128 | Scale with gradient accumulation if GPU-limited |
| Warmup | 0-5% of steps | Less critical than pre-training |
| Weight Decay | 0.0-0.1 | Optional for short fine-tuning runs |
| Loss Masking | Response tokens only | Mask instruction and system prompt tokens |
| Pre-training Data Mix | 2-5% | Mix raw text to prevent catastrophic forgetting |

## Step 5: Evaluation Protocol

After training, evaluate:

1. **Instruction Following Rate**: Percentage of test prompts where the model generates an appropriate, complete response
2. **Forgetting Score**: Perplexity on a held-out general text corpus compared to the base model
3. **Format Compliance**: Percentage of responses that follow the expected chat format
4. **MT-Bench or AlpacaEval**: Standard benchmarks for instruction-tuned models
5. **Domain-Specific Eval**: Custom evaluation for the target capabilities

### Warning Signs

- Validation loss increases after epoch 1: Overfitting, reduce epochs or increase data
- Forgetting score increases > 15%: Learning rate is too high or too many epochs
- Model literally regurgitates training examples: Severe overfitting, need more diverse data
- Model refuses benign instructions: Overtrained on safety data, rebalance dataset
