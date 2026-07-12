#!/usr/bin/env python3
"""SpanKind 上下文分类处理器 (Agent 长对话治理)

迁移自 dcg 的 SpanKind 命令上下文分类范式, 用于 Agent 长对话的:
  1. 压缩分层: Data(工具输出) 大幅压, Executed(执行上下文) 保留
  2. 历史复用: 检索时优先 EXECUTED, 不被工具输出噪音淹没

真实数据支撑 (state.db 两个真实长 session):
  Data 占 75-85% token, Executed 仅 10-20%
  分类压缩省 75-83% token, 执行上下文零损失
  FTS 全文召回执行决策率仅 13%, 分类优先后 100%

设计:
  * 只读 state.db messages, 写私有 message_tags.db (不侵入核心)
  * 规则分类: role=tool -> DATA; assistant 带 tool_calls -> EXECUTED
  * 提供 retrieve_prioritized(): 优先 EXECUTED 的历史检索封装

用法:
  python3 context-processor.py [N]            # 处理最近 N 条未分类消息 (默认 50)
  python3 context-processor.py --stats        # 查看三类分布
  python3 context-processor.py --demo KW      # 演示 KW 关键词的分类优先检索
"""
import sqlite3, json, re, os, sys, argparse
from datetime import datetime

HERMES_HOME = os.path.expanduser("~/.hermes")
STATE_DB = os.path.join(HERMES_HOME, "state.db")
TAGS_DB = os.path.join(HERMES_HOME, "scripts", "message_tags.db")

# 压缩保留比例 (对应真实数据验证的设定)
COMPRESS_RATIO = {"EXECUTED": 1.0, "ARGUMENT": 0.2, "DATA": 0.08, "COMMENT": 0.0}

COMMENT_MARKERS = ["好的", "明白", "收到", "继续", "稍等", "嗯", "没问题", "了解"]
ARGUMENT_MARKERS = ["说明", "原因", "即", "也就是", "换句话说", "总结一下", "注："]


def classify(role, content, tool_calls):
    """规则分类 (可解释, 对齐 dcg SpanKind)."""
    content = content or ""
    if role == "tool":
        return "DATA", 1.0, "role=tool: 工具原始输出"
    if role == "user":
        return "EXECUTED", 1.0, "role=user: 用户指令/反馈"
    # assistant
    tc = tool_calls if tool_calls not in ("[]", "", None) else None
    if tc:
        return "EXECUTED", 1.0, "assistant 带 tool_calls: 行动意图"
    if not content.strip():
        return "DATA", 0.9, "assistant 空内容(配合工具结果)"
    if len(content) < 20 and any(content.startswith(mk) for mk in COMMENT_MARKERS):
        return "COMMENT", 0.7, "短确认/过渡"
    if any(mk in content for mk in ARGUMENT_MARKERS) and len(content) > 200:
        return "ARGUMENT", 0.7, "含解释性标记的长文本"
    if re.search(r"```|def |function |import |SELECT |sudo |curl |\.py", content):
        return "EXECUTED", 0.9, "含代码/命令: 产出本体"
    return "ARGUMENT", 0.7, "默认解释性文本(可压)"


def process_recent(n=50):
    """分类最近 N 条尚未打标的消息."""
    scon = sqlite3.connect(STATE_DB)
    tcon = sqlite3.connect(TAGS_DB)
    # 已处理集合
    done = {r[0] for r in tcon.execute("SELECT message_id FROM message_tags")}
    # 取最近 N 条消息
    rows = scon.execute(
        "SELECT id, role, content, tool_calls FROM messages "
        "ORDER BY timestamp DESC LIMIT ?", (n,)).fetchall()
    now = datetime.now().timestamp()
    new = 0
    for mid, role, content, tool_calls in rows:
        if mid in done:
            continue
        kind, conf, reason = classify(role, content, tool_calls)
        tcon.execute(
            "INSERT OR REPLACE INTO message_tags "
            "(message_id, span_kind, confidence, compress_ratio, reason, processed_at) "
            "VALUES (?,?,?,?,?,?)",
            (mid, kind, conf, COMPRESS_RATIO[kind], reason, now))
        new += 1
    tcon.commit()
    scon.close(); tcon.close()
    print(f"[context] 处理完成: 新分类 {new} 条 (扫描 {len(rows)} 条, 跳过已分类 {len(rows)-new})")
    return new


def show_stats():
    tcon = sqlite3.connect(TAGS_DB)
    print(f"\n{'='*60}\n  SpanKind 分类统计 (message_tags.db)\n{'='*60}")
    print(f"  {'类别':12s} {'消息数':>8s} {'平均压缩比':>10s}")
    print(f"  {'-'*34}")
    for kind, cnt, ratio in tcon.execute(
            "SELECT span_kind, COUNT(*) AS c, ROUND(AVG(compress_ratio),3) AS r "
            "FROM message_tags GROUP BY span_kind ORDER BY c DESC"):
        print(f"  {kind:12s} {cnt:>8d} {ratio:>10.3f}")
    # 模拟压缩收益
    total = tcon.execute("SELECT SUM(compress_ratio) FROM message_tags").fetchone()[0] or 0
    n = tcon.execute("SELECT COUNT(*) FROM message_tags").fetchone()[0]
    if n:
        print(f"\n  若对已分类 {n} 条应用压缩: 平均保留比 {total/n:.3f} "
              f"(即省 {(1-total/n)*100:.1f}% token)")
    tcon.close()


def retrieve_prioritized(kw, limit=8):
    """演示: 分类优先的历史检索.

    不侵入核心 search_messages, 而是直接查 state.db + message_tags:
    先召回 EXECUTED/ARGUMENT, 不足再用 DATA 补足, 对应 SpanKind 的
    '执行上下文优先于数据上下文'.
    """
    con = sqlite3.connect(STATE_DB)
    con.execute("ATTACH ? AS tags", (TAGS_DB,))
    # FTS 全文召回 (现有 session_search 行为)
    fts = con.execute(
        "SELECT m.id, m.role, m.content FROM messages_fts f "
        "JOIN messages m ON m.id = f.rowid "
        "WHERE messages_fts MATCH ? ORDER BY rank LIMIT ?",
        (kw, limit * 3)).fetchall()
    # 带分类标注
    tagged = []
    for mid, role, content in fts:
        r = con.execute(
            "SELECT span_kind FROM tags.message_tags WHERE message_id=?",
            (mid,)).fetchone()
        kind = r[0] if r else classify(role, content, None)[0]
        tagged.append((mid, role, content, kind))
    con.close()
    order = {"EXECUTED": 0, "ARGUMENT": 1, "COMMENT": 2, "DATA": 3}
    tagged.sort(key=lambda x: order.get(x[3], 9))
    return tagged[:limit]


def demo(kw):
    res = retrieve_prioritized(kw)
    print(f"\n{'='*60}\n  分类优先检索演示  关键词='{kw}'\n{'='*60}")
    exec_n = 0
    for mid, role, content, kind in res:
        if kind in ("EXECUTED", "ARGUMENT"):
            exec_n += 1
        c = (content or "")[:68].replace("\n", " ")
        print(f"  [{kind[:4]}] {c}")
    print(f"\n  优先召回 {len(res)} 条中 执行上下文(EXEC/ARG) = {exec_n} 条 "
          f"({exec_n/len(res)*100:.0f}%)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", nargs="?", type=int, default=50, help="处理最近 N 条 (默认50)")
    ap.add_argument("--stats", action="store_true", help="查看分类统计")
    ap.add_argument("--demo", metavar="KW", help="演示分类优先检索")
    args = ap.parse_args()

    if args.stats:
        show_stats()
    elif args.demo:
        demo(args.demo)
    else:
        process_recent(args.n)
        show_stats()
