---
name: hermes-git-worktree
description: 'Git worktree 工作流：feature 工作隔离、worktree 创建、路径优先级、baseline testing。
  Use when creating new features on isolated branches, working across multiple commits,
  or needing parallel worktree isolation.
  禁用：单文件改动、hotfix 直接提交、文档修改。'
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
      - worktree
      - git worktree
      - 分支隔离
      - 并行开发
      - 新建分支
      - feature branch
      - 隔离开发
      - 同时改
      - 多分支
      - git branch
      disable:
      - 单文件改动
      - hotfix直接提交
      - 文档修改
    skill_type: workflow
    priority: normal
---
# Git Worktree 工作流

## 触发条件

任何 feature 工作需要隔离、动手写代码前、跨多 commit 的任务。

## 路径优先级

1. 用户在当前消息明示路径 → 用
2. 存在 .worktrees → 用
3. 存在 worktrees → 用
4. 默认 .worktrees/
5. 必须 verify 在 .gitignore（git check-ignore），否则先加 ignore 再 commit

## 检测已隔离

执行前先判 GIT_DIR != GIT_COMMON，已在 worktree 直接复用，不嵌套。
sub-module 同样行为。

## Baseline Testing

进 worktree 后立刻跑测试，看到 passing 才许动代码。

| 项目类型 | 测试命令 |
|---------|---------|
| Python | pytest |
| Node | npm test |
| Go | go test |
| Rust | cargo test |
| Docker | docker compose ps |

## Cleanup

merge 完成或放弃时清理 worktree。
merges / PR 别问"收拾什么"，自动清理。
