"""Sparse lexical embedding — 纯 CPU 本地, 无需 torch, 无额外依赖。

算法对齐 BGE-M3 `compute_lexical_matching_score`:
  1. Tokenize: 中文按字 + 英文/数字按词 (BPE 风格代理)
  2. Weight: log(1 + tf)   ← BGE-M3 内部公式
  3. Score:  ∑ w_q[t] × w_d[t]  for token ∈ overlap

v2.1 leading word boost:
  - 命中 LEADING_WORD_BOOST 池中 token，权重 ×2
  - 池子与 NEW_SKILL_TEMPLATE.md §leading word 词汇库对齐
  - 命中判断：trigger_tags 中含 leading word 的子串
"""

import math, re
from typing import Dict, Iterable, Optional


def _tokenize(text: str) -> list[str]:
    """将文本拆分为 token 列表。

    中文单字 + 英文词/数字词组（保持数字完整）。
    """
    tokens = []
    # 按词拆分：匹配中文单字 OR 英文词 OR 数字
    for part in re.findall(r"[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+(?:\.?[0-9])*", text):
        if re.match(r"[\u4e00-\u9fff]", part):
            # 中文单字逐个拆开（保证细粒度匹配）
            tokens.extend(list(part))
        else:
            tokens.append(part.lower())
    return tokens


def _compute_weight(tf: int) -> float:
    """log(1 + tf) — BGE-M3 权重公式。"""
    return math.log(1.0 + tf)


# ── leading word 池子 (v2.1) ────────────────────────────────────────
# 来自 NEW_SKILL_TEMPLATE.md §leading word 词汇库（21 个初始词）
# query 端命中池子任意 token，sparse 权重 ×2
LEADING_WORD_POOL = {
    # methodology
    "red", "green", "fog", "war", "tracer", "bullet", "root", "cause",
    "verify", "first", "sunk", "cost", "ship", "it", "ground", "truth",
    # workflow
    "dispatch", "gate", "handoff", "slice",
    # tool
    "probe", "fire", "scaffold",
    # integration
    "bridge", "mirror",
}
LEADING_WORD_BOOST = 2.0


def _is_leading_token(token: str) -> bool:
    """token 是否属于 leading word 池。"""
    return token.lower() in LEADING_WORD_POOL


def get_sparse_weights(
    text: str,
    leading_word_boost: float = LEADING_WORD_BOOST,
    boost_pool: Optional[Iterable[str]] = None,
) -> Dict[str, float]:
    """对文本计算 sparse lexical weights（token -> weight 字典）。

    参数:
        text: 输入文本（trigger_tags 或 query）
        leading_word_boost: leading word 命中后权重乘数（默认 2x）
        boost_pool: 自定义 leading word 集合；None 用默认池
    返回:
        {token: weight} 字典（可 JSON 序列化）
    """
    tokens = _tokenize(text)
    if not tokens:
        return {}
    # term frequency
    tf: Dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    # weight = log(1+tf) — docs/query 端一致
    pool = set(boost_pool) if boost_pool is not None else LEADING_WORD_POOL
    weights = {}
    for token, freq in tf.items():
        w = _compute_weight(freq)
        if token.lower() in pool:
            w *= leading_word_boost
        weights[token] = w
    return weights


def compute_lexical_matching_score(
    query_weights: Dict[str, float],
    doc_weights: Dict[str, float],
) -> float:
    """与 FlagEmbedding compute_lexical_matching_score 算法对齐。

    score = Σ query_weight[t] × doc_weight[t]   for overlapping t

    返回 0–1 归一化分数。
    """
    if not query_weights or not doc_weights:
        return 0.0
    overlap = set(query_weights) & set(doc_weights)
    if not overlap:
        return 0.0
    raw = 0.0
    q_norm = 0.0
    d_norm = 0.0
    for t in query_weights:
        q_norm += query_weights[t] ** 2
    for t in doc_weights:
        d_norm += doc_weights[t] ** 2
    for t in overlap:
        raw += query_weights[t] * doc_weights[t]
    return raw / (math.sqrt(q_norm) * math.sqrt(d_norm) + 1e-8)
