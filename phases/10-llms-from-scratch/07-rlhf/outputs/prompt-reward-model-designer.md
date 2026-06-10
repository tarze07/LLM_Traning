---

name: prompt-reward-model-designer
description: Design reward model training pipelines for RLHF alignment
version: 1.0.0
phase: 10
lesson: 7
tags: [rlhf, reward-model, ppo, alignment, human-feedback, preference-learning]

---

# Reward Model Designer

When building an RLHF pipeline to align a language model to a target behavior (helpfulness, coding ability, safety, fairness), use this framework to design the data collection protocol, train the reward model, and configure PPO.

## Input Requirements

Provide:
- **Target Behavior** (e.g., "helpful and harmless assistant", "expert Python programmer", "medical Q&A with safety")
- **Base Model** (e.g., Llama 3 8B post-SFT, Mistral 7B Chat)
- **Reward Model Size** (typically the same size or larger than the policy model)
- **Annotation Budget** (available labor hours or comparison pairs)
- **Compute Budget** (GPU hours for RM training + PPO)

## Step 1: Preference Data Collection

### Annotation Protocol

1. **Prompt Selection**: Sample from the SFT training distribution plus out-of-distribution prompts (10-20% novelty)
2. **Response Generation**: Generate 2-4 responses per prompt using the SFT model with varied temperatures (0.3, 0.7, 1.0)
3. **Comparison Format**: Show annotators exactly 2 responses and ask "Which response is better?"
4. **Criteria Framework**: Define what "better" means for your specific use case

### Rubric Template

| Criterion | Weight | Description |
|----------|--------|------------|
| Helpfulness | 40% | Does it answer the prompt completely and correctly? |
| Harmlessness | 25% | Does it avoid harmful, biased, or misleading content? |
| Honesty | 20% | Does it acknowledge uncertainty rather than hallucinating? |
| Conciseness | 15% | Is the response an appropriate length for the prompt? |

Adjust weights for your use case. A coding assistant might weight correctness at 60% and conciseness at 20%.

### Data Size Guidelines

| Scale | Pair Comparisons | Annotator Labor Hours | Expected RM Accuracy |
|----------------|---|-----------------|---------------------------------|
| Minimum Viable | 5,000-10,000 | 400-800 | 60-65% |
| Production v1 | 20,000-50,000 | 1,600-4,000 | 65-72% |
| Production v2 | 100,000-500,000 | 8,000-40,000 | 72-78% |

InstructGPT used 33,000 comparisons from 40 contractors. The first Anthropic paper used 22,000 from 20 annotators. Inter-annotator agreement is typically 70-75% - the reward model cannot exceed the human agreement rate.

### Quality Control

- **Agreement Filtering**: Discard pairs where fewer than 70% of annotators agree
- **Annotator Calibration**: Run calibration rounds with known-good pairs before real annotation
- **Bias Detection**: Monitor if annotators consistently prefer longer answers, formal language, or specific patterns
- **Adversarial Examples**: Include 5-10% of examples designed to catch annotators who aren't reading carefully

## Step 2: Reward Model Architecture

### Architecture Decisions

| Decision | Recommendation | Rationale |
|---------|---------------|----------|
| Base Architecture | Same transformer as policy | Weight initialization from SFT checkpoint provides strong starting features |
| Output Head | Single linear projection from last hidden state | Scalar reward on the most complete representation of the sequence |
| Model Size | >= policy model size | Smaller RM produces unreliable signals that destabilize PPO |
| Initialization | SFT checkpoint with new output head | Pre-trained features already capture language quality |

### Training Configuration

| Parameter | Range | Notes |
|----------|-------|-------|
| Learning Rate | 1e-5 to 5e-5 | Lower than SFT because the task is simpler |
| Epochs | 1-3 | Overfitting is a major risk with limited comparison data |
| Batch Size | 64-256 | Each "example" is a pair, so effective data is 2x |
| Loss Function | Bradley-Terry: -log(sigmoid(r_preferred - r_rejected)) | The standard for pairwise comparisons |
| Validation Split | 10-20% | Monitor accuracy on held-out pairs |

### Evaluation Metrics

1. **Pairwise Accuracy**: What fraction of held-out preference pairs does the RM rank correctly? Target: > 65%
2. **Margin Distribution**: Plot the distribution of (r_preferred - r_rejected). It should be centered above 0 with few negatives.
3. **Calibration**: Is sigmoid(r_preferred - r_rejected) close to the actual probability of human preference?
4. **Out-of-Distribution Generalization**: Test on prompts from a different distribution than training. Accuracy should drop < 10%.

## Step 3: PPO Configuration

### Hyperparameters

| Parameter | Typical Value | Effect of Being Too High | Effect of Being Too Low |
|-----------|--------------|-------------------------|------------------------|
| KL coefficient (beta) | 0.01-0.05 | Model barely learns, stays too close to SFT | Reward hacking, degenerate outputs |
| Learning rate | 5e-6 to 3e-5 | Training instability, divergence | Slow convergence, wasted compute |
| Clip ratio (epsilon) | 0.1-0.3 | Large, potentially destabilizing updates | Very conservative updates, slow learning |
| PPO epochs per batch | 1-4 | Overfitting to current batch | Underutilizing each batch |
| Generation batch size | 128-512 | Memory issues | Noisy gradient estimates |
| Max response length | 256-1024 | Slow generation, memory issues | Truncates useful responses |

### Monitoring Dashboard

Track these metrics during PPO training:

1. **Mean reward**: Should increase over training. Plateau is fine; decrease means instability.
2. **KL divergence**: Should stay below 10-20 nats. Spike = reward hacking.
3. **Response length**: Should stay stable. Monotonic increase = verbosity reward hacking.
4. **Entropy**: Token distribution entropy should decrease slowly. Rapid decrease = mode collapse.
5. **Reward model agreement**: Score PPO responses with the reward model; agreement should improve.

### Red Flags During PPO

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Reward increases but outputs degrade | Reward hacking | Increase KL coefficient, retrain RM on adversarial examples |
| KL divergence explodes | Learning rate too high or KL coefficient too low | Reduce lr, increase beta |
| Response length grows monotonically | RM rewards verbosity | Add length penalty to reward, retrain RM with length-controlled pairs |
| All responses become identical | Mode collapse | Increase generation temperature, reduce PPO epochs |
| Reward oscillates wildly | PPO instability | Reduce learning rate, increase clip ratio |

## Step 4: End-to-End Validation

Before deploying an RLHF-trained model:

1. **A/B test vs SFT**: Run the SFT and RLHF models on 200+ test prompts. Have 3+ evaluators compare responses. The RLHF model should win > 60% of the time.
2. **Safety Evaluation**: Test on known adversarial prompts (jailbreaks, harmful requests). The RLHF model should refuse appropriately.
3. **Regression Check**: Run standard benchmarks (MMLU, HumanEval, MT-Bench) to ensure the RLHF model hasn't lost core capabilities.
4. **Forgetting Check**: Measure perplexity on a general text corpus. Increase should be < 10% vs the SFT model.
5. **Length analysis**: Compare average response length between SFT and RLHF models. If RLHF is > 50% longer, the reward model likely has a verbosity bias.
