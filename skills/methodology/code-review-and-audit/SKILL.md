---
name: code-review-and-audit
description: 'Review code (diff + test + subagent), pre-commit gates, local diff scanning,
  simplifications, source-level repo audits, LOC analysis, research and academic review.
  遵循 Code Review 纪律：禁止措辞、接受反馈方式、YAGNI 兜底。
  禁用：纯代码开发(无审查需求)、无 diff 的架构讨论。'
version: 1.0.1
author: Hermes Agent (umbrella consolidation)
license: MIT
metadata:
  hermes:
    tags:
      trigger:
      - 代码审查
      - 审计
      - code review
      - review
      - review代码
      - 审查
      - 看看代码
      - 写得对不对
      - 审计代码
      - 代码质量
      - pre-commit
      - diff审查
      disable:
      - 纯代码开发
      - 无diff的架构讨论
      - 运维脚本审查
    related_skills:
    - github
    - code-simplification
    - doubt-driven-development
    skill_type: methodology
    priority: high
---
# Code Review & Audit — Class-Level Guidance

## Code Review 纪律

### 禁止措辞
- "你说得对" / "你说得太对了"
- "好建议" / "好主意"
- "感谢" / "谢谢"
- "让我现在改" / "让我去做"（在没验证之前）
- 任何 performative agreement

### 必须做
- 重述技术要求（用自己的话）/ 反问 / 直接动手
- ext review 永不复读自己：技术正确 > 关系舒适
- 不明确项先问再动，不要猜
- YAGNI 兜底：grep 代码库确认有调用再写

### 接受建设性反馈时
✅ "Fixed. [改动描述]"
✅ "Good catch — [具体问题]. Fixed in [位置]."
✅ 直接给代码
❌ 任何感谢表达

---

## Review Workflow

1. Read the diff / changes
2. Run the tests (pytest --tb=short)
3. Check for:
   - Correctness
   - Edge cases
   - Error handling
   - Security concerns
   - Performance implications
4. Leave actionable comments (not general praise/criticism)
5. Verify again after fixes

## Audit Types

### Source-level audit
- Dead code detection
- Deprecated API usage
- Security vulnerabilities
- Dependency analysis

### LOC / complexity analysis
- Hotspot detection
- Cyclomatic complexity
- Test coverage gaps
