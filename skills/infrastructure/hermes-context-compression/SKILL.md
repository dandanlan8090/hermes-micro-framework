---
name: hermes-context-compression
description: >-
  对长对话上下文进行分类压缩（DATA/EXECUTED/ARGUMENT），保留 100% 执行决策，
  压缩 75-83% 工具输出 token；历史检索时通过 role_filter 优先返回 user/assistant 消息。
  Use when token 敏感的长 session、上下文太长、压缩对话、历史检索全是工具输出、
  会话卡顿或长 session 管理。Not for 单轮短对话、需保留完整日志、调试模式看原始输出、审计合规场景。
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
      - token 太多
      - 上下文太长
      - 压缩对话
      - 历史检索全是工具输出
      - 会话卡顿
      - 长 session 管理
      disable:
      - 单轮短对话
      - 保留完整日志
      - 调试模式
      - 审计合规
---

# Hermes Context Compression

## 第一性原理
长对话中 75-85% token 是工具原始输出（Data），只有 10-20% 是执行上下文（Executed）。
按语义类型分类后，Data 类可安全压缩，Executed 类必须 100% 保留。

范式来源：借鉴 dcg（Destructive Command Guard）的 SpanKind 命令上下文分类——
它把命令行切成 Executed/Data/Comment 等，分类的唯一目的是决定"是否影响结果"。
这里把同一范式上移到 Agent 长对话治理：分类轴是"这段上下文是否驱动执行"。

## 设计原则（迁移外部范式的通用纪律，来自本 skill 的诞生会话）
- 分析外部项目时，重其**架构/钩子关系**而非功能清单；借用的理念须用**真实数据验证**而非空谈。
- 向量/语义检索的天花板内，不靠**置信度加权/分数微调**去抢救召不回的 case
  （用户原话："置信度加权之类大可不必，允许命中失败是没问题的"）。
  正确方向是"进检索前的路由/分层"（如 SpanKind 上下文分类），不是改融合公式。
- 落到实现时优先在私有侧扩展（side table / 调用侧 `role_filter`），**不侵入核心代码**，
  符合 hermes-agent AGENTS.md 的"核心窄腰"约束。

## 落地实现（~/.hermes/scripts/）
| 文件 | 作用 |
|------|------|
| `init-context-tables.sql` | 创建 `message_tags.db` 私有 side table（不侵入 Hermes 核心） |
| `context-processor.py` | 规则分类最近 N 条消息：`role=tool` → DATA，`assistant+tool_calls` → EXECUTED |
| `vdb-autoload.py --process-context` | `--auto` 模式自动触发分类 |

分类映射（对齐 dcg SpanKind，可解释）：
- EXECUTED：user 指令/反馈 + assistant 工具调用意图 + 含代码/命令的产出 → 压缩比 1.0
- ARGUMENT：assistant 解释性长文本（含"说明/原因/即"等标记） → 压缩比 0.2
- DATA：tool 角色原始输出（命令结果/文件内容/API 返回） → 压缩比 0.08
- COMMENT：短确认/过渡（实测为 0，此用户交互风格直接给方案）

## 调用侧优先检索约定（不改核心）
`hermes_state.py` 的 `search_messages` 已有 `role_filter` 参数，直接传
`role_filter=["user","assistant"]` 即可排除 tool（Data 类），无需改 JOIN。
这符合铁律#5（改进优先于新增），也守住"不碰上游 core"的边界。

也可直接用 `context-processor.py --demo <关键词>` 做分类优先检索演示
（先召回 EXECUTED/ARGUMENT，不足再用 DATA 补足）。

## 真实验证数据（两个长 session，state.db 实测）
| 指标 | 结果 |
|------|------|
| Data 类占比 | 75.5% / 85.4% |
| 分类压缩节省 | 74.1% / 83.0% |
| 历史检索命中执行决策率 | FTS 50% → 分类优先 100% |
| 执行上下文保留 | 100%（EXECUTED 压缩比 1.0） |

当前已分类 208 条消息：EXECUTED 101（保留比 1.0），DATA 96（保留比 0.08），
ARGUMENT 11（保留比 0.2）。平均省 46.7% token（混合近期消息，Data 占比低于极端长 session）。

## 能力边界
- 当前分类靠规则（`role=tool` → DATA），在实测 session 中准确率足够。
  `COMMENT` 类实测为 0（符合此用户"反馈阈值低、直接给方案"的交互风格）。
- 真实价值集中在"Data 识别"这一刀，不夸大四分类全上。
- 复杂边缘场景（如 tool 输出中混入决策性内容）暂不处理，后续可引入轻量 LLM 二次校验。

> 完整真实验证报告（session 元数据、分布明细、复现脚本）见 `references/empirical-validation.md`。

## 触发方式
```bash
# 手动处理最近 50 条
python3 ~/.hermes/scripts/context-processor.py 50

# 查看分类统计
python3 ~/.hermes/scripts/context-processor.py --stats

# 演示分类优先检索
python3 ~/.hermes/scripts/context-processor.py --demo disable

# 随 vdb 自动触发（--auto 模式已包含 --process-context）
python3 ~/.hermes/scripts/vdb-autoload.py --auto

# 单独运行分类
python3 ~/.hermes/scripts/vdb-autoload.py --process-context
```

## 后续进化方向（未实现，记录待用）
- 轻量 LLM 二次校验：规则分类在复杂场景不够准时，用极小模型（如 hermes-2-pro）做二次校验。
- 语义压缩：对 DATA 类内容，除截断外用 vdb 做语义摘要（保留关键信息）。
- 与 vdb 技能检索联动：检索历史时优先展示 EXECUTED 决策点，并自动关联当时触发的 skill，
  形成"决策-执行"链路。
