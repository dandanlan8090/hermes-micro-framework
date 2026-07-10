---
name: hermes-evolution-rules
description: '自身进化规则：改进优先于新增、增量变更(patch而非覆盖)、变更后必须验证、所有变更在 ~/.hermes/ 边界内。
  Use when modifying SOUL.md/AGENTS.md/USER.md, improving an existing skill, or refactoring files.
  禁用：全新项目初始化、用户明确要求新建文件。'
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
      - 改进
      - 优化
      - 修改
      - 重构
      - 更新
      - patch
      - 增量变更
      - 进化
      - 升级
      - 维护
      - 架构优化
      - 系统重构
      - prompt优化
      - 微内核
      - SOUL.md重写
      disable:
      - 新建项目
      - 全新初始化
      - 用户明确要求新建
    skill_type: methodology
    priority: high
---
# 自身进化规则

## 改进优先于新增

任何改动优先在现有文件/skill 上 patch（find-replace），
只有证明现有结构无法承载时才允许新文件。

自问："这能加到现有文件哪个函数/段落里？"
确认不能才新建。若新开文件，在 commit/总结中说明理由。

## 增量变更

所有改动必须是 patch（find-replace），不允许 write_file 整文件覆盖。
覆盖行为触发审查。

## 环境适配验证

变更后必在当前主机跑 1 次验证确认兼容运行，禁止只改不测。

## 持久化边界

所有变更必须在 ~/.hermes/ 边界内，兼容 cmd_update 更新机制。
不依赖 hermes 核心代码，仅使用已知持久化目录（vdb/ / skills/ / memories/）。
确保跨会话、主机重启后功能不丢失。

## 技能维护

使用 skill 时发现过时、不完整或错误 → 立即 patch。
复杂任务成功后 → 保存为 skill。

## 微内核架构重构（system prompt 优化）

当需要优化 system prompt 或重组 SOUL.md/USER.md/MEMORY.md 时，使用微内核模式。

### 目标架构

- SOUL.md（精简内核 ~2,300t）：身份 + 铁律 one-liner + 技能路由表 + 新增规则守则
- USER.md（用户画像 ~180t）：称呼 + 硬件 + Agent 分工
- MEMORY.md（环境事实 ~650t）：工具认证 + 踩坑记录 + 架构决策
- Skills（完整细则 按需加载）：每个规则/方法域 = 独立 skill

### 铁律格式

每条铁律 = 一句话规则（可独立执行）+ skill 引用：

```
### N. 规则名称
一句话规则，不依赖 skill 也能执行基础判断。
→ 完整细则：`skill_view(name='skill-name')`
```

### 路由表格式

每个路由条目 = 场景关键词列表 + skill 名：

```
| 场景描述关键词 | `skill-name` |
```

### 迁移步骤

1. 识别每段内容是铁律级（始终需要）还是方法论级（按需加载）
2. 铁律 → 保留在 SOUL.md，缩为 one-liner
3. 方法论 → 移入独立 skill，设合适 trigger tags 和 priority
4. 所有 skill 加路由条目
5. 删除 AGENTS.md（内容全部分布）
6. vdb 索引重建 + 测试 recall

### 注意事项

- vdb 强制使用铁律（SOUL.md §0）必须写入，不可省略
- available_skills 扫描是系统内置不可绕过的 Layer 2，不需要在 prompt 中重复
- 优先将非 CLI 必需场景移入技能以降低固定开销
- 每轮 input 目标控制在 5,000~6,000t 以内
