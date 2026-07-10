---
name: hermes-framework-architecture
description: 'Hermes 框架架构参考：微内核路由 + skill 按需加载 + vdb 语义召回。
  包含完整文件结构、加载机制、recall 链路、故障诊断、改进方向。
  Use when troubleshooting framework issues, understanding how Hermes loads configs,
  planning architecture changes, or onboarding to the framework design.
  禁用：日常任务执行、不涉及框架的普通查询。'
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
      - 框架架构
      - 框架设计
      - 文件结构
      - 加载机制
      - 框架故障
      - 框架原理
      - 系统设计
      - 修改框架
      - 架构优化
      - 架构说明
      - 架构回顾
      - 框架评估
      - 框架健康
      - 重构框架
      - 改进框架
      disable:
      - 日常任务
      - 简单查询
      - 与框架无关
    skill_type: methodology
    priority: normal
---
# Hermes 框架架构参考

## 概述

Hermes 采用**微内核路由**架构。SOUL.md 是精简内核（身份 + 铁律 one-liner + 技能路由表 + 故障处理），细则全部分布到独立 skill，通过 vdb 语义召回按需加载。

## 文件结构

```
~/.hermes/
├── SOUL.md                 微内核（铁律 + 路由表 + 故障处理）
├── AGENTS.md               已废弃（2026-07-10 删除）
├── memories/
│   ├── USER.md             用户画像
│   └── MEMORY.md           环境事实
├── skills/                 所有技能（69 个）
├── vdb/
│   ├── matcher.py          主入口：search() + is_healthy()
│   ├── indexer.py          索引构建与过期检查 check_index_stale()
│   ├── embed.py            云端稠密 BGE-M3 1024d + 本地 sparse
│   ├── sparse.py           lexical matching
│   ├── chroma/             Chroma hnsw 持久化
│   ├── vdb_state.json      索引状态
│   └── .venv/              Python 虚拟环境
└── plans/                  计划文件
```

## 加载机制

会话启动注入顺序：SOUL.md → USER.md → MEMORY.md

```
system prompt = SOUL.md(~2,500t) + USER.md(~180t) + MEMORY.md(~650t) + 固定框架(~2,800t)
             = ~6,100t/轮
```

## 7 条铁律

| # | 铁律 | 对应 skill |
|---|------|-----------|
| 0 | 技能检索优先 vdb | 无（检索方法本身） |
| 1 | 信息真实性 | hermes-truth-redline |
| 2 | 代码输出 | hermes-code-output |
| 3 | 验证前置 | hermes-verification-rules |
| 4 | 安全约束 | hermes-safety |
| 5 | 改进优先于新增 | hermes-evolution-rules |
| 6 | 思考范围限本轮 | 无（行为约束） |

## 4 层召回通道

1. vdb 语义检索（BGE-M3, ~116ms, top-5）
2. 路由表查表（SOUL.md §技能路由表, 21 条）
3. available_skills 列表扫描（系统 prompt 内置,"MUST load"）
4. skills_list + skill_view 手动扫描（最后兜底）

## 故障诊断

| 症状 | 修复 |
|------|------|
| vdb 返回空 | `init-vdb.sh` 重装 |
| 旧技能召回 | `build_index(force=True)` |
| skill_view 失败 | 检查 SKILL.md frontmatter |
| recall 全无关 | 补 trigger 标签 |
| prompt 膨胀 | 非铁律移入 skill |

## 改进方向

- token 优化：单轮 >8,000t 时移内容到 skill
- recall 精度：top-5 分 <0.3 时优化 trigger 词汇
- 技能覆盖：频发场景无 skill 则新建
- 铁律加固：agent 偏离行为则加 stronger wording

## 历史

2026-07-10：AGENTS.md 删除，SOUL.md 重写为微内核，14 个新 skill 创建，vdb 54→69 技能。system prompt 从 ~11,500t 降到 ~6,100t（省 47%）。

优先级：SOUL.md 铁律 > USER.md 偏好 > skill 细则
