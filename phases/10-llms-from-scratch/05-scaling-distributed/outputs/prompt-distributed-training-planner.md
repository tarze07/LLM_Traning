---

name: prompt-distributed-training-planner
description: Plan distributed training given model size and available hardware
version: 1.0.0
phase: 10
lesson: 5
tags: [distributed-training, fsdp, deepspeed, tensor-parallelism, pipeline-parallelism, scaling]

---

# Distributed Training Planner

When planning a distributed training run for a large language model, use this framework to determine the parallelism strategy, memory budget, communication overhead, and expected throughput.

## Input Requirements

Provide:
- **Model Size** (parameters in billions)
- **Target Training Tokens** (in trillions)
- **Available GPUs** (type: A100/H100/H200, count, interconnect: NVLink/InfiniBand)
- **GPU Memory** (80GB for A100/H100, 141GB for H200)
- **Nodes** (GPUs per node, node count)
- **Budget Constraints** (maximum dollar cost, maximum wall-clock time)

## Step 1: Memory Budget

Calculate per-GPU memory for each component:

| Component | Formula | FP16 | FP32 |
|----------|---------|------|------|
| Weights | params x bytes_per_param | params x 2 | params x 4 |
| Adam Optimizer (m + v) | params x 4 x 2 | 8 bytes/param always | 8 bytes/param |
| Gradients | params x bytes_per_param | params x 2 | params x 4 |
| Activations (estimate) | seq_len x batch x hidden x layers x 2 | varies | varies |

If the sum exceeds GPU memory, sharding is required. Try in order:
1. ZeRO-1 (shard optimizer only) - cheapest communication
2. ZeRO-2 (+ gradients) - moderate communication
3. FSDP/ZeRO-3 (+ weights) - highest communication, but maximum memory savings
4. Add activation checkpointing if activations are still too large
5. Add tensor parallelism if a single layer does not fit on one GPU

## Step 2: Parallelism Strategy

### Decision Tree

1. **Does one layer fit on a single GPU?**
   - No: You need Tensor Parallelism. Set TP = 2, 4, or 8 (within a node).
   - Yes: Skip Tensor Parallelism.

2. **Does the full model (with sharding) fit across GPUs in a single node?**
   - No: You need Pipeline Parallelism. Set PP = number of nodes/groups.
   - Yes: Skip Pipeline Parallelism.

3. **How many GPUs are left for Data Parallelism?**
   - DP = total_gpus / (TP x PP)

4. **What level of sharding within the Data Parallel group?**
   - Start with FSDP (ZeRO-3). If communication is a bottleneck, step down to ZeRO-2 or ZeRO-1.

### Typical Configurations

| Model Size | Total GPUs | TP | PP | DP | Sharding |
|-----------|-----------|----|----|-----|----------|
| 7B | 8 | 1 | 1 | 8 | FSDP |
| 13B | 16 | 2 | 1 | 8 | FSDP |
| 70B | 64 | 8 | 1 | 8 | FSDP |
| 70B | 128 | 8 | 2 | 8 | FSDP |
| 405B | 16,384 | 8 | 16 | 128 | FSDP |

## Step 3: Communication Analysis

Estimate communication volume per training step:

- **Data Parallel (all-reduce)**: 2 x gradient_size x (N-1)/N per step
- **FSDP (all-gather + reduce-scatter)**: ~3 x weight_size x (N-1)/N per step (higher than DP)
- **Tensor Parallel (all-reduce per layer)**: 2 x activation_size x num_layers per step (requires NVLink)
- **Pipeline Parallel (point-to-point)**: activation_size per stage boundary (minimal)

If communication time exceeds 20% of compute time, the strategy is communication-bound. Solutions:
- Gradient accumulation (reduce all-reduce frequency)
- Overlap communication with compute (FSDP does this by default)
- Increase micro-batch size (better compute-to-communication ratio)
- Fall back to a less communication-heavy sharding stage

## Step 4: Throughput and Cost Estimation

**FLOPS per training step:**
- Forward: ~2 x params x tokens_per_batch
- Backward: ~4 x params x tokens_per_batch (2x forward)
- Total: ~6 x params x tokens_per_batch

**Training Time:**
- total_flops = 6 x params x total_tokens
- time_seconds = total_flops / (num_gpus x gpu_tflops x 1e12 x utilization)
- Typical utilization: 35-45% (accounting for communication, pipeline bubbles, memory overhead)

**Cost:**
- total_gpu_hours = num_gpus x time_seconds / 3600
- cost = total_gpu_hours x gpu_hourly_cost

## Step 5: Validation Checklist

Before launching:

1. Per-GPU memory is within hardware limit (with 10% headroom)
2. Effective batch size matches the target (per_gpu_batch x DP x gradient_accumulation_steps)
3. Communication-to-compute ratio is below 20%
4. Pipeline bubble fraction is below 15% (enough micro-batches)
5. Learning rate is scaled for the effective batch size
6. Checkpoint frequency accounts for failure probability (for large runs, save every 1-2 hours)
7. Gradient clipping is set (usually 1.0 for large models)
8. Warmup steps are proportional to total steps (usually 0.1-1% of total)

## Red Flags

- **TP > 8**: Tensor parallelism across nodes (via InfiniBand) is almost always slower than pipeline parallelism
- **Pipeline Stages > 32**: Bubble overhead becomes significant even with many micro-batches
- **Effective Batch Size > 10M tokens**: Diminishing returns; might hurt convergence
- **Utilization < 30%**: Communication-bound - re-evaluate parallelism strategy
- **No Activation Checkpointing above 13B**: You will run out of memory during the backward pass
- **No Gradient Accumulation on small per-GPU batches**: Increases gradient noise; accumulate to an effective batch > 256 samples
