---

name: mlops-inference
description: 'Local LLM inference: llama.cpp (GGUF), vLLM (production serving), HuggingFace
  Hub model discovery. Use when running models locally, deploying production LLM APIs,
  choosing quant methods, or searching HuggingFace for GGUF files. Replaces narrow
  siblings llama-cpp and serving-llms-vllm.'
version: 1.0.0
author: Hermes
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
      - 推理
      - llm部署
      - 模型推理
      - vllm
      - llama
      - 跑模型
      - inference
      disable:
      - long_context
      - read_only
    category: mlops
    absorbed_from:
    - llama-cpp
    - serving-llms-vllm
    - huggingface-hub
---

# MLOps Inference — Local & Production LLM Serving

## What this skill covers

Three inference modes and their trade-offs, plus HuggingFace Hub model discovery:

| Mode | Use when | Key tools |
|------|----------|-----------|
| **llama.cpp / GGUF** | CPU/Apple Silicon/edge, custom quants, local-first | `llama-server`, `llama-cli`, HF Hub search |
| **vLLM** | Production API serving, high throughput, OpenAI compat | `vllm serve`, OpenAI SDK |
| **HuggingFace Hub** | Model discovery, download, upload | `hf` CLI (`hf download`, `hf upload`, `hf models list`) |

## llama.cpp — Local GGUF Inference

Full reference in `templates/llama-cpp.md` (absorbed from `mlops/inference/llama-cpp`).

### Core workflow (URL-first)

1. Search: `https://huggingface.co/models?apps=llama.cpp&sort=trending`
2. Open: `https://huggingface.co/<repo>?local-app=llama.cpp` — copy exact command
3. Verify: `https://huggingface.co/api/models/<repo>/tree/main?recursive=true` for exact filenames
4. Run: `llama-server -hf <repo>:<QUANT>` or `--hf-repo <repo> --hf-file <filename>`

### Quant selection

- General chat: `Q4_K_M`
- Code/technical: `Q5_K_M` or `Q6_K`
- Tight RAM: `Q3_K_M` or `IQ` variants
- Audio/video: mention `mmproj-*.gguf` separately

### OpenAI-compatible server check

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Write a limerick about Python exceptions"}]}'
```

## vLLM — Production Serving

Full reference in `templates/vllm.md` (absorbed from `mlops/inference/vllm`).

### When to use vs llama.cpp

- **Use vLLM**: production APIs (100+ req/sec), OpenAI compat, multi-user
- **Use llama.cpp**: CPU/edge, single-user, custom quants

### Quick start

```bash
pip install vllm
vllm serve meta-llama/Llama-3-8B-Instruct

# Query
python -c "
from openai import OpenAI
c = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(c.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
"
```

### Quantization (AWQ/GPTQ/FP8)

```bash
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95
```

## HuggingFace Hub — Model Discovery

Full `hf` CLI reference in `templates/huggingface-hub.md` (absorbed from `mlops/huggingface-hub`).

```bash
hf download <repo_id>                    # Download files
hf upload <repo_id>                      # Upload (single-commit)
hf upload-large-folder <repo_id> <path>  # Resumable large dirs
hf auth login/logout                     # Token management
hf repos create/delete/duplicate         # Repo lifecycle
hf models list --search <term>           # Search models
hf datasets list/sql                     # Datasets + SQL
hf endpoints deploy/pause/resume          # Inference Endpoints
```

## Hardware Requirements

| Model size | llama.cpp (CPU/GPU) | vLLM (GPU) |
|-----------|---------------------|-----------|
| 7B-13B | 8-16GB | 1x A10 (24GB) or A100 (40GB) |
| 30B-40B | 24-32GB | 2x A100 (tensor parallel) |
| 70B+ | 48GB+ | 4x A100 or 2x A100-80GB + AWQ |

## References

- `templates/llama-cpp.md` — full llama.cpp reference (hub discovery, server, CLI, Python bindings, quants, troubleshooting)
- `templates/vllm.md` — full vLLM reference (production workflows, quantization, Docker, performance tuning)
- `templates/huggingface-hub.md` — complete `hf` CLI reference (download, upload, search, discussions, Inference Endpoints)
      - 跑模型
      - inference
