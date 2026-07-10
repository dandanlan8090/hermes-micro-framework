# FRAMEWORK_EVOLUTION.md — 框架演进记录

> 自动记录每次框架变更（新增 skill/修改铁律/优化路由），积累 3 条触发评审。

## [2026-07-10] feat: 极致拆解 SOUL.md，创建 4 个新 skill
- 类型：refactor / feat
- 原因：SOUL.md token 太大（12,529ch），极致拆解后降至 4,783ch
- 变更内容：
  - SOUL.md §框架故障处理 → 独立 skill infrastructure/hermes-framework-troubleshooting
  - SOUL.md §增加约束/方法守则 → 独立 skill methodology/hermes-framework-evolution
  - 铁律#6 细则 → 独立 skill core/hermes-focus-scope
  - 新增 methodology/hermes-framework-changelog（框架变更审计）
  - SOUL.md 路由表新增 3 行
- 验证结果：待 vdb 重建后确认 recall
- 决策人：@lan
