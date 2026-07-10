---
name: vdb-retrieval-pipeline
description: >-
  Chroma + SiliconFlow BAAI/bge-m3 混合检索管道。云端稠密向量(name+desc+tags) + 本地
  sparse关键词权重(仅trigger_tags,完全隔离英文description)。打分: 0.6dense+0.4sparse。
  Hermes 技能检索核心基础设施。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      trigger:
        - vdb
        - 技能检索
        - 向量数据库
        - 技能匹配
        - skill retrieval
        - skill search
        - 稠密检索
        - 混合检索
        - 重建索引
        - rebuild index
        - chroma
        - bge-m3
        - 硅基流动
        - siliconflow
      disable:
        - deep_review
        - code_development
    skill_type: infrastructure
    priority: highest
---

# vdb-retrieval-pipeline — Hermes 技能混合检索管道

## 架构

```
query
  │
  ├──▶ 云端 (SiliconFlow API)
  │     BAAI/bge-m3 ── 稠密向量 (1024d)
  │     Chroma hnsw cosine 召回 top-16
  │
  ├──▶ 本地 (sparse.py, 纯 Python, 无 torch)
  │     仅 trigger_tags ── 词权重 ── compute_lexical_matching_score
  │     (完全隔离英文 description)
  │
  └──▶ final = 0.6 × dense + 0.4 × sparse
       → disable 过滤 → top-5
```

## 文件位置

| 文件 | 作用 |
|------|------|
| `~/.hermes/vdb/sparse.py` | 纯 Python lexical weights，无额外依赖 |
| `~/.hermes/vdb/embed.py` | 云端稠密 API + 本地 sparse 接口 |
| `~/.hermes/vdb/indexer.py` | Chroma 索引构建 |
| `~/.hermes/vdb/matcher.py` | 检索入口 `search(query, top_k=5)` |
| `~/.hermes/vdb/__init__.py` | 包入口，导出 `build_index` / `search` |
| `~/.hermes/vdb/chroma/` | Chroma 持久化存储（~1.2MB） |

## 依赖

```
pip install chromadb openai python-dotenv
```

`sparse.py` 无依赖（纯 Python）。

## 常规操作

### 检查索引状态

```python
from indexer import check_index_stale
stale, reason = check_index_stale()
print(f"索引过期: {stale}, 原因: {reason}")
```

### 重建索引（技能更新后）

```python
from indexer import build_index
build_index(force=True)
```

### 检索

```python
from matcher import search
results = search("部署 flask", top_k=5)
# 返回: [{"skill_name", "final_score", "dense_score", "sparse_score", ...}]
```

### 修改模型/提供方

只改 `embed.py` 中 `_get_client()` 的 `base_url` + `api_key` 来源。

## 权重调整

`matcher.py` 顶部：

```python
VEC_WEIGHT = 0.6    # 稠密向量权重
SPARSE_WEIGHT = 0.4 # 标签关键词权重
```

## 配置

API Key 从 `~/.hermes/.env` 读取 `SILICONFLOW_API_KEY`。
