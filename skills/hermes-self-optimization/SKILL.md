---
name: hermes-self-optimization
description: 'Hermes 系统 Prompt 微内核优化方法论。将 SOUL.md/AGENTS.md/USER.md 中的稠密规则抽取为独立 skill，
  SOUL.md 精简为铁律 one-liner + 技能路由表，实现每轮只加载命中 skill 的按需架构。
  Use when reducing system prompt size, restructuring SOUL.md, or extracting rules into skills.
  禁用：单次技能创建、配置变更、日常问答。'
version: 1.0.0
author: Hermes (extracted from session 2026-07-10)
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
      - 系统 prompt 优化
      - SOUL.md 精简
      - 降低 token 消耗
      - 微内核架构
      - 路由表
      - 技能抽取
      - prompt architecture
      - system prompt thinning
      - 规则拆分
      - 去除冗余
      - iron law
      - 铁律路由
      - AGENTS.md 清理
      disable:
      - 写单个 skill
      - 日常对话
      - 纯功能开发
    skill_type: methodology
    priority: high
    related_skills:
    - hermes-agent
    - hermes-base-config-sync
    - hermes-agent-skill-authoring
---

# Hermes 系统 Prompt 微内核优化

## 核心理念

SOUL.md = 精简内核（身份 + 铁律 one-liner + 技能路由表）
每个规则域 = 独立 skill（完整细则）
每轮 system prompt 只含铁律概要 + 路由表，技能通过 vdb 按需加载

## 架构示意

```
system prompt (~3,200t)              skills (按需加载)
┌─────────────────────┐             ┌──────────────────┐
│ SOUL.md  精简版       │             │ hermes-verification│
│ ├── 身份/语言         │    vdb      │ ├── IDENTIFY→RUN  │
│ ├── 铁律6条+路由表     │ ←──召回──  │ ├── 验证对照表     │
│ ├── 思考范围约束       │             │ └── 禁止措辞      │
│ └── 主脑触发段         │  desc扫描   ├──────────────────┤
│                      │  (内置指令)  │ hermes-code-output│
│ USER.md 精简          │             │ ├── 完整块规范     │
│ MEMORY.md 压缩        │             │ └── 字面量铁律     │
└─────────────────────┘             └──────────────────┘
```

## 何时使用

1. 用户抱怨 token 消耗太大、上下文太胖
2. SOUL.md/AGENTS.md 超过 2,000 tokens
3. 发现 SOUL.md 中有大量非核心规则（oracle mode、飞书、skill 规范等）
4. AGENTS.md 与 SOUL.md 存在大量重复
5. 用户主动要求"瘦身"或"微内核"

## 方法论（7 步法）

### Step 1: 内容审计

逐段分析 SOUL.md/AGENTS.md/USER.md 中每段内容，标记为三类：

| 分类 | 含义 | 去向 | 参考 tokens |
|------|------|------|-------------|
| 🔴 CORE | 每轮必需的身份/红线/安全/通信约束 | 留在 system prompt | ~800t |
| 🟡 SKILL | 只在特定场景需要的规则/方法论 | 抽取为独立 skill | ~5,000t |
| ⚪ PROFILE | 与 profile 绑定的规则(飞书/文生图) | 移入对应 profile | ~1,000t |

#### CORE 判定标准（不可移动）
- 影响模型行为基座（身份、真实性红线、安全约束）
- 影响每轮回复风格（通信约束、输出规范）
- 技能系统本身的前置条件（skill 加载铁律）
- 验证前置的概要（防止无条件"完成"声明）

#### SKILL 判定标准（可移动）
- 仅在特定用户场景下触发的规则
- 有明确的触发条件（用户说了/做了某事）
- 方法论式内容（TDD、debug 四阶段、code review）
- 不违反时行为退化为"无约束但不错误"

### Step 2: 设计铁律 one-liner

每条铁律 = 一句可执行的指令 + "完整规则见 skill:xxx"

```
铁律 3: 验证前置：任何"完成/搞定/成功"结论前必须运行验证命令。
        完整规则 → skill:hermes-verification-rules
```

铁律的设计原则：
- 不依赖 skill 即可执行（one-liner 本身是一个完整约束）
- skill 加载后补全细则（验证的具体流程 IDENTIFY→RUN→READ→VERIFY）
- 未加载时退化到"知道要这么做，但不一定知道最佳做法"

### Step 3: 构建路由表

SOUL.md 中放一个场景→skill 的映射表：

```
| 场景 | 参阅 skill |
|------|-----------|
| 调试 / debug / 错误排查 | debugging-patterns |
| 部署 / 发布 / 上线 | hermes-shipping-verification |
| TDD / 单元测试 / pytest | hermes-tdd-workflow |
```

路由表格式要求：
- 左栏放用户实际会说的自然语言（3-5 个覆盖词）
- 右栏放 skill 名（可直接 skill_view 加载）
- 按使用频率排序

### Step 4: 创建/修改 skills

为每个 🟡 SKILL 分类的规则创建或扩展现有 skill：

**新增 skill 时**：
- 使用 NEW_SKILL_TEMPLATE 标准 frontmatter
- trigger_tags ≥5 个，按用户真实用语写
- disable_tags ≥3 个，明确排除场景
- priority: 验证/安全类用 highest，方法论用 high/normal

**修改现有 skill 时**：
- 扩 trigger_tags 以覆盖路由表中的场景词
- 升级 priority（如 normal→high）
- patch 方式修改，不整文件覆盖

### Step 5: 4 层召回设计

```
L1: vdb 语义召回 (matcher.py)
L2: available_skills description 扫描 (系统内置 'MUST scan skills' 指令)
L3: SOUL.md 路由表查表 (system prompt 里始终存在)
L4: 铁律 one-liner 兜底 (即使无 skill 加载也有约束)

可靠度: L1(~70%) + L2(~95%) + L3(100%) + L4(100%) = 无单点依赖
```

AGENTS.md 删掉后，其 §1（skill 加载铁律）由系统内置的 "Before replying, scan the skills below" 指令替代。这条指令是 Hermes 框架级注入，不依赖任何文件。

### Step 6: 文件变更

| 文件 | 操作 |
|------|------|
| SOUL.md | 重写为铁律+路由表格式（~3,000t → ~800t） |
| AGENTS.md | 删除，内容全部分布到 skills |
| USER.md | 精简为仅身份/硬件/Agent分工（~700t → ~150t） |
| MEMORY.md | 压缩环境事实（~1,400t → ~600t） |
| vdb/matcher.py | 如需要，加 priority=highest 硬注入（可选） |

### Step 7: 验证

#### Token 节省验证
```
优化前: SOUL+USER+MEMORY+AGENTS = ~8,700t + 框架~2,800t = ~11,500t/轮
优化后: SOUL(精简)+USER(精简)+MEM(压缩) = ~1,660t + 框架~2,800t = ~4,460t/轮
无 skill 命中: 省 ~7,000t/轮 (61%)
命中 1 skill: 省 ~4,000t/轮
命中 3 skill: 持平
```

#### 行为等价验证
用以下场景检测是否退化：
```
"帮我看个报错" → 应有 debugging-patterns 被加载
"部署完了"     → 应有 verification 规则生效（铁律#3 兜底）
"写个 pytest"  → 应有 tdd-workflow 被加载
"现在几点"     → 无 skill 加载,直接答
```

#### vdb 召回验证
```
cd ~/.hermes/vdb && source .venv/bin/activate
python3 -c "from matcher import search; [print(r['skill_name'],r['final_score']) for r in search('部署一下')]"
```

## 注意事项

### 铁律不要超过 8 条
超过 8 条的铁律说明 CORE 分类太宽松了。每增加一条铁律，要考虑"这条真的每轮都需要吗？"

### AGENTS.md 删除后的残留感知
如果用户习惯用 `skill_view(name='AGENTS.md')` 或引用 AGENTS.md 内容，需要确认没有硬编码引用。

### MEMORY.md 压缩策略
- 保留跨会话环境事实（sudo 免密、gh 认证、平台封号率）
- 删除过时会话进度（PR 号、commit SHA、完成的任务）
- 删除"已固化到 skill"的偏好说明

### 路由表维护
新增 skill 后记得更新 SOUL.md 路由表。路由表是 L3 召回的关键，
漏更新会导致 agent 无法通过查表找到新 skill。

## 参考

- 完整方案: `~/.hermes/plans/2026-07-10_prompt-optimization-v2.md`
- 4 层召回测试: `recall_test.py` (该 skill 的 scripts/ 目录)
- 当前 SOUL.md 草稿: `/tmp/new-soul-preview.md`
