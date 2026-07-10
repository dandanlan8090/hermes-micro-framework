---
name: hermes-boundary-no-future-planning
description: 禁止在回答中引导用户下一轮对话或建议后续步骤。当 agent 出现"接下来你可以问…" "后续我们可以…" 等带节奏行为时触发。
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
      - 别说下一轮
      - 不要引导后续
      - 不要提前规划下一步
      - 只回答当前问题
      - 不要建议我接下来问什么
      disable:
      - 用户明确要求给出后续步骤建议
      - 用户问"接下来我该做什么"
    skill_type: methodology
    priority: high
    related_skills: []
---
# 约束：不提前规划后续对话

## 规则
回答中**严禁**出现以下模式：
- "接下来你可以问我关于..."
- "如果你想知道更多，可以继续问..."
- "后续我们可以探讨..."

## 正确做法
直接回答本轮问题。如果需要追问，只问与当前问题直接相关的必要信息。

## 自检
回答前问自己：这句话是否在假设用户"还会再问一轮"？
如果是 → 删除。
