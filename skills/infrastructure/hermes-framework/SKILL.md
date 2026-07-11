---
name: hermes-framework
description: >-
  Hermes 微内核框架的 CLASS-LEVEL 总纲：架构（文件结构/加载机制/铁律/4层召回）、
  配置文件加载与 profile、框架演进（新增铁律/skill/路由的安全流程）、变更日志规范、
  框架自身故障诊断与回滚、system prompt 微内核优化（SOUL.md 瘦身/技能抽取）、
  自身进化规则（改进优先于新增/增量变更/验证/持久化边界）。
  触发：框架架构/设计/故障、加载顺序/SOUL.md/USER.md/MEMORY.md/profile、
  vdb不工作/skill加载失败/召回不准/铁律失效、新增或扩展规则或skill、
  变更日志/框架审计、system prompt优化/SOUL.md精简/降低token消耗/微内核、
  改进/优化/重构/patch/增量变更/进化。
  禁用：日常任务执行、用户业务代码变更、不涉及框架的普通查询。
version: 2.0.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
        - 框架架构
        - 框架设计
        - 文件结构
        - 加载机制
        - 框架故障
        - 框架原理
        - 系统设计
        - 修改框架
        - 架构优化
        - 重构框架
        - 加载顺序
        - SOUL.md加载
        - 框架文件
        - profile切换
        - system prompt
        - 配置文件
        - 新增铁律
        - 新增规则
        - 创建约束
        - 新增skill
        - 修改方法
        - 框架演进
        - 路由表更新
        - 扩展框架
        - 变更日志
        - 框架历史
        - 回溯变更
        - 框架审计
        - vdb不工作
        - skill加载失败
        - 索引过期
        - 召回不准
        - 铁律失效
        - is_healthy false
        - build_index失败
        - 系统prompt优化
        - SOUL.md精简
        - 降低token消耗
        - 微内核架构
        - 技能抽取
        - prompt thinning
        - 规则拆分
        - 去除冗余
        - SOUL.md瘦身
        - prompt瘦身
        - 精简内核
        - 改进
        - 优化
        - 重构
        - 增量变更
        - 微内核
        - SOUL.md重写
      disable:
        - 日常任务执行
        - 用户业务代码变更
        - 不涉及框架的普通查询
        - 项目开发 commit
    skill_type: methodology
    priority: high
    related_skills:
      - vdb-retrieval-pipeline
      - autoload-vdb
      - hermes-agent-skill-authoring
      - hermes-evolution-rules
---
# Hermes Framework — 微内核架构总纲

本 skill 是框架类知识的总入口，吸收并取代原先分散的 7 个框架微技能：
`hermes-framework-architecture`、`hermes-framework-loader`、`hermes-framework-evolution`、
`hermes-framework-changelog`、`hermes-framework-troubleshooting`、`hermes-self-optimization`、
`hermes-evolution-rules`。按需阅读对应小节。

## 0. 概览（第一性原理）

Hermes 采用**微内核路由**架构：SOUL.md 是精简内核（身份 + 铁律 one-liner + 技能路由表 +
故障处理），细则全部分布到独立 skill，通过 vdb 语义召回按需加载。每一条新增约束必须放在唯一正确的位置。

```
system prompt = SOUL.md(~2,500t) + USER.md(~180t) + MEMORY.md(~650t) + 固定框架(~2,800t) ≈ ~6,100t/轮
```

## 1. 文件结构

```
~/.hermes/
├── SOUL.md                 微内核（铁律 + 路由表 + 故障处理）
├── AGENTS.md               已废弃（2026-07-10 删除）
├── memories/
│   ├── USER.md             用户画像
│   └── MEMORY.md           环境事实
├── skills/                 按分类组织（71 技能）
├── vdb/
│   ├── matcher.py          主入口：search() + is_healthy()
│   ├── indexer.py          索引构建与过期检查 check_index_stale()
│   ├── embed.py            云端稠密 BGE-M3 1024d + 本地 sparse
│   ├── sparse.py           lexical matching
│   ├── chroma/             Chroma hnsw 持久化
│   ├── vdb_state.json      索引状态
│   └── .venv/              Python 虚拟环境
└── plans/                  计划文件
```

## 2. 加载机制与配置文件

会话启动注入顺序：**SOUL.md → USER.md → MEMORY.md**。

- 默认 profile：`~/.hermes/SOUL.md`
- 非 default profile：`~/.hermes/profiles/<name>/SOUL.md`
- USER.md：`~/.hermes/memories/USER.md`
- MEMORY.md：`~/.hermes/memories/MEMORY.md`
- Profile 技能目录：`~/.hermes/profiles/<name>/skills/`（与 vdb 索引默认 SKILLS_DIR 不同；
  设置 `HERMES_SKILL_DIR` 环境变量或用 `install.sh --profile <name>` 安装）

确认当前 profile：`hermes profile list`（◆ 标记活跃 profile）。

**AGENTS.md 已废弃**（2026-07-10），被以下机制替代：SOUL.md §0 铁律（4 层召回链）、
SOUL.md §技能路由表、各独立 skill、系统 prompt 内置的 "Before replying, scan the skills below"。

## 3. 七条铁律与四层召回

| # | 铁律 | 对应 skill |
|---|------|-----------|
| 0 | 技能检索优先 vdb | 无（检索方法本身） |
| 1 | 信息真实性 | hermes-truth-redline |
| 2 | 代码输出 | hermes-code-output |
| 3 | 验证前置 | hermes-verification-rules |
| 4 | 安全约束 | hermes-safety |
| 5 | 改进优先于新增 | hermes-evolution-rules |
| 6 | 思考范围限本轮 | hermes-boundary-rules |

4 层召回通道（可靠度叠加，无单点依赖）：
1. vdb 语义检索（BGE-M3, ~116ms, top-5）
2. 路由表查表（SOUL.md §技能路由表）
3. available_skills 列表扫描（系统 prompt 内置 "MUST load"）
4. skills_list + skill_view 手动扫描（最后兜底）

## 4. 框架故障诊断与回滚

**本质**：某条加载链路中断（vdb 链路 / skill 链路 / 铁律链路）。沿链路逐段排查。

| 症状 | 根因 | 修复动作 |
|------|------|----------|
| vdb 返回空 / is_healthy()==False | chromadb 损坏 / .venv 丢失 / API key 无效 | `~/.hermes/scripts/init-vdb.sh` 重装 |
| vdb 返回旧技能 | 新增/修改后未 rebuild | `build_index(force=True)` |
| skill_view 失败 | frontmatter 损坏 / 文件误删 | `ls ~/.hermes/skills/`；`skill_manage(action='create')` 重建 |
| recall top-5 全无关 | trigger 标签太少/脱离用户用语 | 补 trigger 后 rebuild |
| 铁律未体现 | SOUL.md 措辞模糊 | 检查铁律格式：one-liner + `→ skill_view(...)` |
| system prompt 膨胀 | SOUL/USER/MEMORY 过多 | 移非铁律内容入 skill |
| 新 skill 无法召回 | 新增后未 rebuild | `build_index(force=True)` |

**一键诊断**：
```bash
cd ~/.hermes/vdb && source .venv/bin/activate || { echo ".venv 激活失败"; exit 1; }
python3 -c "from matcher import is_healthy; from indexer import check_index_stale; \
print(f'healthy={is_healthy()}'); stale,reason=check_index_stale(); print(f'stale={stale} {reason}')"
python3 -c "import chromadb; from chromadb.config import Settings; \
from indexer import CHROMA_DIR, COLLECTION_NAME; \
c=chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False)); \
print(f'skills={c.get_collection(COLLECTION_NAME).count()}')"
python3 -c "from matcher import search; [print(r['skill_name'], r['final_score']) for r in search('框架故障')[:5]]"
```

**回滚**（行为退化时立即回退）：
```bash
cd ~/.hermes && git checkout -- SOUL.md memories/USER.md memories/MEMORY.md
cd ~/.hermes/vdb && source .venv/bin/activate && \
PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"
python3 ~/.hermes/scripts/vdb-autoload.py --check
```

**失败模式**：SiliconFlow API 限流(429)→等待30s重试；.venv 损坏→删除后重跑 init-vdb.sh；
Chroma 锁残留→`rm -rf ~/.hermes/vdb/chroma/.lock`；磁盘不足→清理 chroma/ 旧索引。

## 5. 框架演进（新增/扩展规则与 skill）

**归属正确原则** — 每一条新增约束必须放在唯一正确的位置：

| 内容类型 | 特征 | 正确存放位置 |
|----------|------|-------------|
| 铁律 | 每轮必须遵守、不依赖场景 | SOUL.md §铁律 |
| 方法论/工作流 | 特定场景使用、有完整步骤 | 独立 skill（skills/） |
| 用户偏好 | 个人习惯 | USER.md |
| 环境事实 | 系统/设备/工具信息 | MEMORY.md |
| 场景→skill 映射 | 路由入口 | SOUL.md §技能路由表 |

**五步决策流程**：① 判断归属 → ② 新增铁律（SOUL.md §铁律末追加 one-liner + `→ skill_view(name=...)`）→
③ 新增方法论 skill（遵守 `hermes-agent-skill-authoring`，路由表加一行，rebuild vdb）→
④ 修改已有规则（优先 patch 现有 skill，不新建）→ ⑤ 验证（rebuild + 测 recall）。

**微技能拆分准则**：一个 skill 只解决一个具体违规行为；若 body 中有多个 H2/H3 描述彼此独立的行为约束 → 拆。
判断标准：大 skill 整体 ~800t 偶尔触发 vs 微技能 ~150-200t 精确匹配。

**外部 skill 仓库吸收**：重叠→patch 我们的 skill 追加精华；我们没有→用 Hermes 格式封装新 skill；
太偏框架/工具→跳过。

**触发规则阈值**：单轮 input token > 8,000 → 移非铁律到 skill；新 skill recall top-5 < 0.3 → 改 trigger 用词；
铁律偏离 → 检查 one-liner 格式；同场景 ≥3 次 → 按第三步新建。

## 6. 变更日志规范

框架变更必须有记录可查（无法回滚/审计/协作 = 没发生过）。记录位置：
`~/.hermes/memories/FRAMEWORK_EVOLUTION.md`（与演进钩子共享）。

每条记录回答三问：改了什么 / 为什么改 / 怎么验证的。格式：
```markdown
## [YYYY-MM-DD] feat: 新增 hermes-framework skill
- 类型：新增 skill
- 原因：7 个框架微技能合并为总纲，减小碎片
- 变更内容：创建 infrastructure/hermes-framework/SKILL.md，归档 7 个旧 skill
- 验证结果：recall '框架故障' → top-1 命中
- 决策人：@lan
```
类型标签：`feat:`(新增) / `refactor:`(重构) / `fix:`(修复 recall/铁律) / `perf:`(优化 token) / `docs:`(文档)。
审计：`grep "^## " ~/.hermes/memories/FRAMEWORK_EVOLUTION.md`；回滚 = 手动逆向操作。

## 7. System Prompt 微内核优化（SOUL.md 瘦身 / 技能抽取）

**核心理念**：SOUL.md = 精简内核（身份 + 铁律 one-liner + 技能路由表）；每个规则域 = 独立 skill（完整细则）；
每轮只含铁律概要 + 路由表，技能通过 vdb 按需加载。

**内容审计（三类）**：
| 分类 | 含义 | 去向 | 参考 tokens |
|------|------|------|-------------|
| 🔴 CORE | 每轮必需的身份/红线/安全/通信约束 | 留 system prompt | ~800t |
| 🟡 SKILL | 仅特定场景需要的规则/方法论 | 抽取为独立 skill | ~5,000t |
| ⚪ PROFILE | 与 profile 绑定的规则 | 移入对应 profile | ~1,000t |

CORE 判定（不可移动）：影响模型行为基座、每轮回复风格、技能系统前置条件、验证前置概要。
SKILL 判定（可移动）：仅特定场景触发、有明确触发条件、方法论式、不违反时退化为"无约束但不错误"。

**7 步法**：① 内容审计 → ② 设计铁律 one-liner（可执行 + `→ skill:xxx`）→ ③ 构建路由表（左栏用户自然语言，右栏 skill 名）→
④ 创建/修改 skills（trigger≥5, disable≥3, priority 按类）→ ⑤ 4 层召回设计 → ⑥ 文件变更（SOUL 重写、AGENTS.md 删除、USER/MEMORY 压缩、vdb rebuild）→
⑦ 验证（token 节省 + 行为等价 + recall）。

**token 验证**：优化前 ~11,500t/轮 → 优化后 ~4,460t/轮（无 skill 命中省 ~61%）。
**铁律不要超过 8 条**。MEMORY.md 压缩：保留跨会话环境事实，删除过时进度与已固化到 skill 的偏好。

## 8. 自身进化规则（hermes-evolution-rules）

- **改进优先于新增**：先 patch 现有文件/skill，只有证明现有结构无法承载才新建。
- **增量变更**：所有改动必须 patch（find-replace），不允许 write_file 整文件覆盖；覆盖触发审查。
- **环境适配验证**：变更后必在当前主机跑 1 次验证，禁止只改不测。
- **持久化边界**：所有变更在 `~/.hermes/` 边界内，兼容 `hermes update`；不依赖核心代码，仅用已知持久化目录（vdb/ skills/ memories/）。
- **技能维护**：使用中发现过时/不完整/错误 → 立即 patch；复杂任务成功后 → 保存为 skill。

## 9. 微内核重构速查

目标架构：SOUL.md(~2,300t 精简内核) + USER.md(~180t) + MEMORY.md(~650t) + Skills(按需加载)。
铁律格式 = 一句话规则（可独立执行）+ `→ skill_view(name='skill-name')`。
迁移步骤：识别铁律级/方法论级 → 铁律缩 one-liner 留 SOUL → 方法论移独立 skill → 所有 skill 加路由 → 删 AGENTS.md → rebuild vdb。
每轮 input 目标 5,000~6,000t。详见 `references/recall-test-results.md`（self-optimization 实证数据）。
