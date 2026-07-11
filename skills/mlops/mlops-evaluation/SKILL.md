---

name: mlops-evaluation
description: 'Model evaluation: lm-eval-harness benchmarks (MMLU, GSM8K, HumanEval,
  etc.) and W&B experiment tracking. Use when benchmarking model quality, comparing
  models, tracking training progress, or logging ML experiments.'
version: 1.0.0
author: Hermes
license: MIT
platforms:
- linux
- macos
metadata:
  hermes:
    tags:
      trigger:
      - 评测
      - benchmark
      - ML评估
      - 模型评估
      - llm评测
      - benchmark测试
      - 评估指标
      disable:
      - deep_review
      - long_context
    category: mlops
    absorbed_from:
    - evaluating-llms-harness
    - weights-and-biases
---

# MLOps Evaluation — Model Benchmarking & Experiment Tracking

## What this skill covers

| Workflow | Tool | Use when |
|----------|------|----------|
| **Academic benchmarks** | `lm-eval` (EleutherAI harness) | Reporting standardized metrics, comparing models, tracking training |
| **Experiment tracking** | W&B | Logging training runs, sweeping hyperparameters, sharing results |

## lm-eval — Academic Benchmarking

Full reference in `templates/lm-evaluation-harness.md` (absorbed from `mlops/evaluation/lm-evaluation-harness`).

```bash
pip install lm-eval

lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag \
  --device cuda:0 \
  --batch_size auto \
  --num_fewshot 5
```

**Standard suite**: `mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge`

vLLM backend (5-10x faster):
```bash
lm_eval --model vllm \
  --model_args pretrained=model-name,tensor_parallel_size=2 \
  --tasks mmlu --batch_size auto
```

## Weights & Biases — Experiment Tracking

Full reference in `templates/weights-and-biases.md` (absorbed from `mlops/evaluation/weights-and-biases`).

```python
import wandb
wandb.init(project="my-project", name="run-001")
wandb.log({"loss": 0.5, "accuracy": 0.8})

# Sweep
wandb.agent(sweep_id, function=train)

# Auto-log PyTorch
wandb.watch(model, log_freq=100)
```

## When to use each

- **Academic paper / model release**: use `lm-eval` with standard tasks
- **Training iteration / hyperparameter search**: use W&B sweeps
- **Both**: run `lm-eval` on checkpoints, log results to W&B for unified tracking

## References

- `templates/lm-evaluation-harness.md` — full benchmark guide (60+ tasks, vLLM backend, model comparison, custom tasks, API evaluation, distributed eval)
- `templates/weights-and-biases.md` — full W&B reference (logging, artifacts, sweeps, resuming, integration patterns)
      - benchmark测试
      - 评估指标
