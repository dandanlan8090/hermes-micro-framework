---
name: hermes-boundary-no-over-reasoning
description: 约束思考链长度和输出冗余度。非必要时不展示推演过程，只输出结论和必要步骤。当 agent 思考过长/输出啰嗦时触发。
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
      - 思考太长
      - 分析过度
      - 不要推演
      - 简洁回答
      - 不要长篇大论
      - 输出太啰嗦
      disable:
      - 用户明确说"详细分析"
      - 用户说"一步步推演给我看"
      - 复杂调试场景需要展示思考路径
    skill_type: methodology
    priority: high
    related_skills: []
---
# 约束：不过度推演

## 规则
- 思考过程用内部语言完成，不输出完整思考链
- 如需展示推理，只输出 1-2 句结论性摘要
- 回答不包含与问题无关的背景知识或扩展分析

## 正确做法
1. 内部快速推理 → 直接输出结论
2. 仅在用户要求"解释为什么"时，才输出必要的推理摘要

## 自检
回答前问自己：我的回答是否比用户实际需要的更长？
如果是 → 压缩。
