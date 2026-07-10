"""Embedding 层 — 云端稠密 + 本地 sparse。

云端: SiliconFlow BAAI/bge-m3 生成 1024d 稠密向量（prose 模板拼接 name+leading+desc+branches）
本地: sparse.py 计算 trigger_tags 的 lexical weights（完全隔离英文 description）
v2.1: leading word 命中给 2x sparse 权重（见 sparse.LEADING_WORD_BOOST）
"""

import os, json
from typing import List, Optional
from dotenv import load_dotenv

from openai import OpenAI
from sparse import get_sparse_weights, compute_lexical_matching_score


load_dotenv()

_sf_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _sf_client
    if _sf_client is None:
        _sf_client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=os.getenv("SILICONFLOW_API_KEY"),
        )
    return _sf_client


def get_cloud_dense(texts: List[str]) -> List[List[float]]:
    """调用硅基流动 BAAI/bge-m3 获取稠密向量 (1024d)。"""
    resp = _get_client().embeddings.create(
        model="BAAI/bge-m3",
        input=texts,
    )
    return [item.embedding for item in resp.data]


def get_tag_sparse_dict(tag_list: List[str]) -> str:
    """仅对 trigger_tags 计算 lexical weights，完全隔离 description。

    返回 JSON 序列化字符串，存入 Chroma metadata。
    """
    combined = "\n".join(tag_list)
    weights = get_sparse_weights(combined)
    return json.dumps(weights, ensure_ascii=False)


def calculate_sparse_score(query: str, doc_sparse_json: str) -> float:
    """计算 query 与技能预存 sparse 权重的词匹配得分。

    参数:
        query: 用户原始查询（无模板包装）
        doc_sparse_json: meta 中 tag_sparse 字段（JSON 字符串）
    返回:
        0–1 区间 lexical matching score
    """
    doc_weights = json.loads(doc_sparse_json)
    query_weights = get_sparse_weights(query)
    return compute_lexical_matching_score(query_weights, doc_weights)
