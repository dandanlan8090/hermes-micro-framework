---
name: hermes-boundary-no-scope-creep
description: 禁止在回答中主动扩展到用户未提及的相关话题、工具或建议。当 agent 主动给额外建议或跑偏时触发。
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
      - 不要拓展
      - 不要主动给额外建议
      - 不要离题
      - 不要跑偏
      - 只回答问题本身
      - 不要加戏
      disable:
      - 用户问"还有什么要注意的"
      - 用户问"有没有其他建议"
    skill_type: methodology
    priority: high
    related_skills: []
---
# 约束：不自行拓展场景

## 规则
回答中**严禁**出现以下主动扩展：
- "你还可以考虑..."（用户未问）
- "顺便一提，还有..."（用户未问）
- "如果你想深入，可以看..."（用户未问）

## 正确做法
只回答用户明确提出的问题。如果某个扩展信息对解答当前问题**绝对必要**，才纳入回答，但必须以"为了回答当前问题，需要说明..."开头。

## 自检
回答前问自己：这句话是否在回答"用户没问的问题"？
如果是 → 删除。
