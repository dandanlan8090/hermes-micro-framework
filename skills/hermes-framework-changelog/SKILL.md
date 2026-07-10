---
name: hermes-framework-changelog
description: 记录 Hermes 微内核框架每次变更（新增技能/修改铁律/优化路由/调整结构），便于回溯和审计。当需要查看框架演进历史或记录新变更时使用。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
metadata:
  hermes:
    tags:
      trigger:
      - 框架演进记录
      - 变更日志
      - 框架历史
      - 回溯变更
      - 框架审计
      - 框架修改记录
      - 架构变更
      - 版本历史
      disable:
      - 普通代码变更日志
      - 项目开发 commit
      - 日常任务记录
    skill_type: methodology
    priority: normal
    related_skills:
    - hermes-framework-evolution
    - hermes-framework-architecture
---
# Hermes Framework Changelog

## 第一性原理
框架变更必须有记录可查。没有记录的变更等于没发生过——无法回滚、无法审计、无法协作。

每条变更记录回答三个问题：
1. **改了什么**（具体修改内容）
2. **为什么改**（触发场景）
3. **怎么验证的**（证明修改有效）

---

## 记录位置

`~/.hermes/memories/FRAMEWORK_EVOLUTION.md` — 与框架演进钩子共享同一文件。

---

## 变更记录格式

每条记录按时间顺序追加：

```markdown
## [2026-07-10] feat: 新增 hermes-framework-troubleshooting skill
- 类型：新增 skill
- 原因：SOUL.md §框架故障处理 拆解为独立 skill，减小 SOUL.md token
- 变更内容：
  - 创建 infrastructure/hermes-framework-troubleshooting/SKILL.md
  - SOUL.md 路由表新增一行
- 验证结果：recall '框架故障' → top-1 命中，score 0.62
- 决策人：@lan
```

---

## 类型标签规范

| 标签 | 适用场景 |
|------|---------|
| `feat:` | 新增 skill / 路由条目 |
| `refactor:` | 现有内容重构（拆解/合并） |
| `fix:` | 修复 recall / 铁律失效 |
| `perf:` | 优化 token 消耗 |
| `docs:` | 仅文档/注释变更 |

---

## 审计流

查看全部演进历史：

```bash
grep "^## " ~/.hermes/memories/FRAMEWORK_EVOLUTION.md
```

按类型筛选：

```bash
grep -A 3 "^##.*feat:" ~/.hermes/memories/FRAMEWORK_EVOLUTION.md
```

回滚到某个版本前的状态：

```bash
# 查看变更序列，找到目标版本之前的提交
cat ~/.hermes/memories/FRAMEWORK_EVOLUTION.md
# 手动逆向操作（删除 skill / 还原路由 / 还原 SOUL.md）
```
