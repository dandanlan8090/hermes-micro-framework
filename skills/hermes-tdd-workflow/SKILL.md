---
name: hermes-tdd-workflow
description: 'TDD 工作流：生产代码必须先有 failing test 验证失败再写实现再验证通过。
  Use when writing Python/Rust/Go code, creating 30+ line scripts, implementing reusable tools,
  or any code that will be executed multiple times.
  禁用：单行脚本(<10行)、仅配置变更(yaml/conf/env)、文档编写、一次性 throwaway 探查。'
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
      - TDD
      - 测试驱动
      - 单元测试
      - pytest
      - unittest
      - 先写测试
      - 测试先行
      - 写测试
      - 代码测试
      - 自动化测试
      - test-driven
      - red-green
      disable:
      - 单行脚本
      - 配置变更
      - 文档
      - throwaway
    skill_type: methodology
    priority: normal
---
# TDD 工作流

## 核心原则

生产代码 → 必须先有 failing test 验证它失败 → 再写 → 验证它通过。

## 例外清单（运维场景）

不强制 TDD，但保留 verification-before-completion：

- 单行/单步 bash 脚本（< 10 行）
- 仅配置变更（yaml / conf / env）
- 文档（Markdown / txt）
- 一次性 throwaway 探查

## 必须 TDD 的场景

- 长脚本（> 30 行）
- 多 shell 步骤跨多文件
- 任何 Python / Go / Rust 实现
- 任何会被多次调用的工具

## 框架自动检测

| 检测条件 | 框架 |
|---------|------|
| pyproject.toml 存在 | pytest |
| package.json 存在 | npm test |
| go.mod 存在 | go test |
| Cargo.toml 存在 | cargo test |
| *.bats 文件 | bats |
| 以上均不匹配 | pytest fallback |

## Sunk Cost 红律

已写代码无测试 → 删，重写。不保留为参考，不借鉴。
沉没成本不是节省时间的理由。
