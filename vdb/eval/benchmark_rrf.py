"""
P0: 离线对比 0.6/0.4 加权 vs RRF.
不改线上 matcher.py，只读 Chroma 数据。

方法:
  dense rank  = 1..16 (Chroma cosine 距离排序)
  sparse rank = candidates 内按 sparse_score 排序
  0.6/0.4    = VEC_WEIGHT * dense_score + SPARSE_WEIGHT * sparse_score
  RRF        = 1/(60 + dense_rank) + 1/(60 + sparse_rank)
"""
import json, sys, os
from pathlib import Path

VDB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(VDB_DIR))
os.chdir(str(VDB_DIR))
from matcher import _get_collection, is_healthy
from embed import get_cloud_dense, calculate_sparse_score

BENCHMARK = [
    ("写个 TDD 测试",                 "hermes-tdd-workflow"),
    ("帮我 review 一下这段代码",       "code-review-and-audit"),
    ("调试一下报错信息",               "debugging-patterns"),
    ("部署 flask 到生产环境",          "hermes-shipping-verification"),
    ("写一个 plan",                    "hermes-plan-workflow"),
    ("这个功能的设计方案",              "spec-driven-development"),
    ("看看代码性能瓶颈",                "performance-optimization"),
    ("git 怎么用 worktree 隔离分支",    "hermes-git-worktree"),
    ("写个 agent skill",               "hermes-agent-skill-authoring"),
    ("帮我搜索一下最新的 AI 论文",      "arxiv"),
    ("合并代码到主分支",                "github"),
    ("这个页面交互有点问题",             "dogfood"),
    ("同步配置文件到 base config",      "hermes-base-config-sync"),
    ("系统信息是什么",                  "system-admin"),
    ("先查 codebase 再改代码",         "codebase-memory-first"),
    ("装一个服务到 ubuntu",             "system-admin"),
    ("发一条推特",                      "xurl"),
    ("单元测试怎么写",                  "hermes-tdd-workflow"),
    ("代码简化一下",                    "code-simplification"),
    ("看看我的待办列表",                "hermes-todo-progress"),
    ("帮我排错",                        "debugging-patterns"),
    ("发布新版本",                      "hermes-shipping-verification"),
    ("Oracle Mode 调度一下",            "hermes-oracle-mode"),
    ("YouTube 视频摘要",               "youtube-content"),
    ("检查一下安全规范",                "hermes-safety"),
    ("实验数据可视化分析",              "jupyter-live-kernel"),
    ("消息既然你已发出去",               "yuanbao"),
    ("配置 CI/CD 流水线",              "ci-cd-and-automation"),
    ("写一个 API 接口文档",             "api-and-interface-design"),
    ("重构老系统迁移方案",               "deprecation-and-migration"),
    ("增量实现这个功能",                 "incremental-implementation"),
    ("debug the segmentation fault",   "debugging-patterns"),
    ("run inference on this model",    "mlops-inference"),
    ("search arxiv for NLP papers",    "arxiv"),
    ("evaluate model on MMLU",         "mlops-evaluation"),
    ("what's trending on twitter",     "xurl"),
    ("video transcript and summary",   "youtube-content"),
    ("segment objects in this image",  "segment-anything"),
    ("generate music from text",       "audiocraft"),
    ("find me a GIF for this",         "gif-search"),
    ("send an email",                  "himalaya"),
    ("turn on the living room lights", "openhue"),
    ("query polymarket for prices",    "polymarket"),
    ("check blog feed for updates",    "blogwatcher"),
    ("knowledge base from wiki",       "llm-wiki"),
    ("确认一下部署结果",                "hermes-verification-rules"),
    ("不要编造任何信息",                "hermes-truth-redline"),
    ("信息真实性确认",                  "hermes-truth-redline"),
    ("agent 协作架构",                  "agent-collaboration-workflow"),
    ("framework 文件加载规则",          "hermes-framework-loader"),
    ("微内核框架架构",                  "hermes-framework-architecture"),
    ("fault troubleshooting",          "hermes-fault-troubleshooting"),
    ("changelog 更新了啥",             "hermes-framework-changelog"),
    ("框架演进规则",                    "hermes-framework-evolution"),
    ("开闭原则怎么落地",                "doubt-driven-development"),
    ("写代码前先查官方文档",             "source-driven-development"),
    ("用 openai 兼容模型的思考链",       "openai-compat-thinking"),
    ("vdb 检索怎么工作的",             "vdb-retrieval-pipeline"),
    ("self-optimize my system prompt", "hermes-self-optimization"),
    ("并行派发多个 agent",             "hermes-parallel-dispatch"),
    ("批量调研这个话题",                "agent-reach"),
]

RRF_K = 60
VEC_WEIGHT = 0.6
SPARSE_WEIGHT = 0.4

def eval_one(query, expected):
    """返回 (hit_baseline_top1, hit_baseline_top3, hit_rrf_top1, hit_rrf_top3)"""
    collection = _get_collection()
    # 1. 稠密向量
    q_text = query if len(query) >= 15 else f"调用{query}。"
    query_dense = get_cloud_dense([q_text])[0]

    # 2. Chroma 召回 top16
    from indexer import TOP_K_CANDIDATES
    results = collection.query(
        query_embeddings=[query_dense],
        n_results=TOP_K_CANDIDATES,
        include=["distances", "metadatas"],
    )
    if not results["ids"][0]:
        return 0, 0, 0, 0

    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    # 构建候选列表
    candidates = []
    for dense_rank, (dist, meta) in enumerate(zip(distances, metadatas), start=1):
        dense_score = 1.0 - dist
        tag_sparse = meta.get("tag_sparse", "{}")
        sparse_score = calculate_sparse_score(query, tag_sparse)
        disable = json.loads(meta.get("disable_tags", "[]"))
        trigger = json.loads(meta.get("trigger_tags", "[]"))
        skill_name = meta["skill_name"]

        # filter disabled
        query_lower = query.lower().replace("_", " ")
        hit = False
        for d in disable:
            d_lower = d.lower().replace("_", " ")
            parts = d_lower.split()
            if len(parts) > 1 and all(p in query_lower for p in parts):
                hit = True
                break
            if d_lower in query_lower:
                hit = True
                break

        candidates.append({
            "skill_name": skill_name,
            "dense_score": round(dense_score, 4),
            "sparse_score": round(sparse_score, 4),
            "dense_rank": dense_rank,
            "disable_hit": hit,
        })

    # 过滤 disable
    valid = [c for c in candidates if not c["disable_hit"]]

    # 当前方式: 0.6/0.4
    baseline_sorted = sorted(
        valid,
        key=lambda c: VEC_WEIGHT * c["dense_score"] + SPARSE_WEIGHT * c["sparse_score"],
        reverse=True
    )
    baseline_top1 = baseline_sorted[0]["skill_name"] if baseline_sorted else None
    baseline_top3 = [c["skill_name"] for c in baseline_sorted[:3]] if baseline_sorted else []

    # RRF: dense rank 已在 Chroma 结果中; sparse rank 从候选内排序
    # sorted 按 sparse_score 降序, rank=1..N
    sparse_sorted = sorted(valid, key=lambda c: c["sparse_score"], reverse=True)
    sparse_rank_map = {}
    for i, c in enumerate(sparse_sorted, start=1):
        sparse_rank_map[c["skill_name"]] = i

    # RRF score = 1/(k + dense_rank) + 1/(k + sparse_rank)
    rrf_results = []
    for c in valid:
        sr = sparse_rank_map.get(c["skill_name"], len(valid) + 1)
        rrf_score = 1.0 / (RRF_K + c["dense_rank"]) + 1.0 / (RRF_K + sr)
        rrf_results.append((c["skill_name"], rrf_score, c["dense_rank"], sr))

    rrf_sorted = sorted(rrf_results, key=lambda x: x[1], reverse=True)
    rrf_top1 = rrf_sorted[0][0] if rrf_sorted else None
    rrf_top3 = [x[0] for x in rrf_sorted[:3]] if rrf_sorted else []

    hit_baseline_top1 = 1 if baseline_top1 == expected else 0
    hit_baseline_top3 = 1 if expected in baseline_top3 else 0
    hit_rrf_top1 = 1 if rrf_top1 == expected else 0
    hit_rrf_top3 = 1 if expected in rrf_top3 else 0

    return (hit_baseline_top1, hit_baseline_top3, hit_rrf_top1, hit_rrf_top3,
            baseline_top1, baseline_top3, rrf_top1, rrf_top3)


def main():
    if not is_healthy():
        print("[benchmark] vdb 不可用，退出")
        sys.exit(1)

    tot = len(BENCHMARK)
    hits_b1 = hits_b3 = hits_r1 = hits_r3 = 0

    detail_rows = []

    for i, (query, expected) in enumerate(BENCHMARK, 1):
        res = eval_one(query, expected)
        (h_b1, h_b3, h_r1, h_r3, b1, b3, r1, r3) = res
        hits_b1 += h_b1
        hits_b3 += h_b3
        hits_r1 += h_r1
        hits_r3 += h_r3

        b1_flag = "✓" if h_b1 else "✗"
        r1_flag = "✓" if h_r1 else "✗"
        b3_flag = "✓" if h_b3 else " "
        r3_flag = "✓" if h_r3 else " "

        detail_rows.append((i, query[:48], expected, b1_flag, r1_flag, b1, r1))

        if (i % 10) == 0 or i == tot:
            print(f"[benchmark] {i}/{tot} — baseline top1={hits_b1}, rrf top1={hits_r1}")

    # 汇总
    print(f"\n{'='*65}")
    print(f"{'BENCHMARK 结果':^65}")
    print(f"{'='*65}")
    print(f"  总 query: {tot}")
    print(f"")
    print(f"  {'方法':20s} {'Top-1':>8s} {'Top-3':>8s} {'Top-1%':>8s} {'Top-3%':>8s}")
    print(f"  {'-'*54}")
    print(f"  {'0.6/0.4 (基线)':20s} {hits_b1:>4d}/{tot:<3d} {hits_b3:>4d}/{tot:<3d} {hits_b1/tot*100:>7.1f}% {hits_b3/tot*100:>7.1f}%")
    print(f"  {'RRF 融合':20s} {hits_r1:>4d}/{tot:<3d} {hits_r3:>4d}/{tot:<3d} {hits_r1/tot*100:>7.1f}% {hits_r3/tot*100:>7.1f}%")

    delta_t1 = hits_r1 - hits_b1
    delta_t3 = hits_r3 - hits_b3
    t1_str = f"+{delta_t1}" if delta_t1 > 0 else str(delta_t1)
    t3_str = f"+{delta_t3}" if delta_t3 > 0 else str(delta_t3)
    print(f"  {'差值':20s} {t1_str:>8s} {t3_str:>8s}")
    print(f"")

    # 差异明细
    diff = []
    for row in detail_rows:
        i, q, exp, b1f, r1f, b1, r1 = row
        if b1f != r1f:
            diff.append(row)
    if diff:
        print(f"\n{'─'*65}")
        print(f"  Top1 不一致（{len(diff)}/{tot}）:")
        print(f"{'─'*65}")
        for i, q, exp, b1f, r1f, b1, r1 in diff:
            print(f"  #{i:2d} {q:48s} | baseline={b1:35s} | rrf={r1:35s} | 期望={exp:35s}")

    # 保存结果
    out_path = VDB_DIR / "eval" / "benchmark_rrf_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
        "total": tot,
        "baseline_top1": hits_b1,
        "baseline_top3": hits_b3,
        "baseline_top1_pct": round(hits_b1/tot*100, 1),
        "baseline_top3_pct": round(hits_b3/tot*100, 1),
        "rrf_top1": hits_r1,
        "rrf_top3": hits_r3,
        "rrf_top1_pct": round(hits_r1/tot*100, 1),
        "rrf_top3_pct": round(hits_r3/tot*100, 1),
    }, out_path, ensure_ascii=False, indent=2)
    print(f"\n  详细结果已保存: {out_path}")


if __name__ == "__main__":
    main()
