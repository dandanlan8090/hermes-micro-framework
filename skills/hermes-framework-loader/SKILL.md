---
name: hermes-framework-loader
description: '框架文件加载规则：Hermes 在会话启动时注入 SOUL.md/USER.md/MEMORY.md 到 system prompt。
  加载顺序：SOUL.md → USER.md → MEMORY.md。AGENTS.md 已废弃。
  Use when understanding how Hermes loads its configuration files, managing profiles, or troubleshooting startup behavior.
  禁用：普通任务执行、无需了解加载机制的操作。'
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
      - 加载顺序
      - 框架文件
      - SOUL.md加载
      - USER.md
      - MEMORY.md
      - AGENTS.md
      - profile切换
      - 文件加载
      - system prompt
      - 配置文件
      disable:
      - 普通任务执行
      - 无需了解加载机制
      - 简单查询
    skill_type: methodology
    priority: normal
    related_skills:
    - hermes-evolution-rules
---
# 框架文件加载规则

## 加载顺序

会话启动时，按以下顺序注入 system prompt：

1. SOUL.md（核心身份与路由）
2. USER.md（用户画像）
3. MEMORY.md（环境事实与踩坑记录）

## 路径规则

- 默认 profile：`~/.hermes/SOUL.md`
- 非 default profile：`~/.hermes/profiles/<name>/SOUL.md`
- USER.md：`~/.hermes/memories/USER.md`
- MEMORY.md：`~/.hermes/memories/MEMORY.md`

## 确认当前 profile

执行文件操作（install.sh、cp、write_file）前先确认：

```
hermes profile list
```

◆ 标记当前活跃 profile。

## AGENTS.md

已废弃（2026-07-10）。被以下机制替代：

- **SOUL.md 铁律 §0** — 技能检索 4 层链（vdb → 路由表 → available_skills → 手动扫描）
- **SOUL.md §技能路由表** — 场景名→skill 名直接映射
- **各独立 skill** — 原 AGENTS.md 方法论内容已全部分布到 20+ 个 skill
- **系统 prompt 内置指令** — "Before replying, scan the skills below" 仍不可绕过

## Profile 下的技能目录

```
~/.hermes/profiles/<name>/skills/
```

与 vdb 索引的默认 SKILLS_DIR 不同。
需设置 HERMES_SKILL_DIR 环境变量或使用 `install.sh --profile <name>` 安装。
