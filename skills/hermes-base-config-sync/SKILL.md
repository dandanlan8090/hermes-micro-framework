---
name: hermes-base-config-sync
description: Hermes Base Config GitHub 同步流程 —— 从本地 Hermes 配置整理通用 SOUL.md/AGENTS.md/USER.md/skills
  到开源 repo。触发：更新 hermes-base-config、同步 SOUL.md、发布配置模板、整理技能到 GitHub。禁用：普通 repo push、非
  Hermes 配置、未经脱敏的私有资料。
version: 1.5.0
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
      - hermes-base-config
      - 同步 SOUL.md
      - 同步 AGENTS.md
      - 发布配置模板
      - 整理技能到 GitHub
      - Hermes Base Config
      - github sync
      - 配置 repo
      - 脱敏发布
      - NEW_SKILL_TEMPLATE
      - 新建 repo
      - 新仓库创建
      disable:
      - 普通 git push
      - 非 Hermes 配置
      - 未经脱敏
      - 私有 MEMORY.md
      - 不发布到开源
    skill_type: workflow
    priority: high
    related_skills:
    - NEW_SKILL_TEMPLATE
    - hermes-agent-skill-authoring
    - github
    - plan
prerequisites:
  commands:
  - git
  - gh
  config: {}
  # NOTE: config.yaml is user-authorization scope, not project-managed.
  # See references/config-dependencies.md for the full dependency analysis.
---
# Hermes Base Config GitHub Sync

## Overview

这个技能用于维护 `hermes-base-config` 这类公开模板仓库：从本地 `~/.hermes/` 提取 SOUL.md / AGENTS.md / USER.md / 核心 skills，整理成通用、脱敏、可复用的 GitHub repo。

核心原则：**本地文件不能直接复制发布。repo 内容必须是通用模板，发布前必须脱敏和结构校验。**

---

## When to Use

- 用户要求整理或更新 Hermes Base Config repo
- 用户要求同步 SOUL.md / AGENTS.md / USER.md 到 GitHub
- 用户要求把本地技能整理为可公开分享的模板
- 用户要求补充 `NEW_SKILL_TEMPLATE.md` 或关联核心技能
- 用户要求维护公开的 Hermes 配置模板仓库

**Do not use for:**
- 普通代码 repo 的 git push
- 私有 MEMORY.md 备份
- 未经脱敏的配置迁移
- 不发布到开源社区的本地个人配置

---

## Variant: New Repo Creation

本 skill 主要覆盖**更新已有 repo**（如 `hermes-base-config`）的流程。
当需要**新建一个 repo**（如 `hermes-micro-framework`），在进入主 Workflow 前执行以下预步骤。

### Pre-Step A: 定义 Repo 技能范围

决定哪些文件/skill 放进新仓库。三个条件依次叠加：

1. **Baseline（基准）** — 以最接近的现有仓库（如 `hermes-base-config`）的 file/skill 集为起点。这是最低基线。
2. **SOUL.md 路由表补充** — 添加 `~/.hermes/SOUL.md §技能路由表` 中引用的、与本 repo 主题相关（框架架构、方法论、工作流）的 skill。路由表中与 repo 定位无关的 skill（如飞书、媒体、research）即使被引用也排除。
3. **排除系统自带（system-bundled）** — 移除 Hermes 自身分发的 skill（如 `hermes-agent`、`agent-reach`、`computer-use`、`autonomous-ai-agents/` 下的子 skill 等）。这些属于 Hermes 发行版，不属于框架模板。

结果 = **（baseline + 路由表相关引用）− 系统自带 skill**。

### Pre-Step B: 创建 GitHub 仓库

```bash
gh repo create <owner>/<repo-name> --public --description "<description>" --license MIT
```

### Pre-Step C: Clone 并初始化

```bash
git clone https://github.com/<owner>/<repo-name>.git /tmp/<repo-name>
cd /tmp/<repo-name>
```

然后进入主 Workflow Step 1（加载技能），后续步骤中的 repo 路径和 scope 按新仓库名称调整。

**与更新流程的关键区别**：Step 3 使用 `git clone`（而非 `git pull`），且不存在已有 repo 结构做 diff 参照——从零搭建。

---

## Canonical Repo Layout

`NEW_SKILL_TEMPLATE.md` 是 `skills/` 目录下的**独立文件**，不是技能目录。

`.env.example` 和 `.vdb_state.json` 的区别：
- `.env.example` 在**仓库中**（API Key 模板），安装时复制到 `~/.hermes/.env`
- `.vdb_state.json` **不在仓库中**，`build_index()` 运行时自动生成在 `~/.hermes/vdb/`

```text
hermes-base-config/
├── README.md
├── LICENSE
├── install.sh                # 一键部署脚本（新装/存量两种模式）
├── SOUL.md
├── AGENTS.md
├── .env.example              # API Key 模板（复制到 ~/.hermes/.env）
│
├── memories/
│   └── USER.md               # 用户画像模板（原在根目录，重构后移至此处）
│
├── vdb/                      # 技能检索运行时工具链
│   ├── sparse.py
│   ├── embed.py
│   ├── indexer.py
│   ├── matcher.py
│   └── __init__.py
│
├── scripts/
│   ├── init-vdb.sh           # vdb 一键初始化（.venv + pip + build_index）
│   └── vdb-autoload.py       # 启动预热 + 索引过期检测 + 自动重建
│
└── skills/
    ├── NEW_SKILL_TEMPLATE.md
    ├── ai-conv-style-discipline/
    │   └── SKILL.md
    ├── codebase-memory-first/
    │   └── SKILL.md
    ├── doubt-driven-development/
    │   └── SKILL.md
    ├── hermes-agent/
    │   └── SKILL.md
    ├── hermes-base-config-sync/
    │   └── SKILL.md
    ├── hermes-oracle-mode/
    │   └── SKILL.md
    ├── hermes-shipping-verification/
    │   └── SKILL.md
    ├── plan/
    │   └── SKILL.md
    └── source-driven-development/
        └── SKILL.md
```

---

## Absolute Source Files

Use these local source paths only for reading. Do not publish them without sanitization.

参见 `references/config-dependencies.md`：repo 对 Hermes 配置项的依赖关系清单。
参见 `references/session-2026-07-10-review.md`：2026-07-10 用户审查归档（8 点评设计原则 + 已知风险点）。
参见 `references/session-2026-07-10-vdb-profile-path.md`：2026-07-10 vdb profile 路径修正（`_resolve_skills_dir`、`active_profile`、`--profile` 参数）。
参见 `references/session-2026-07-10-micro-framework.md`：2026-07-10 新建 hermes-micro-framework repo 的 skill 选择方法论（baseline + 路由表 − 系统自带）。

```text
~/.hermes/SOUL.md
~/.hermes/AGENTS.md
~/.hermes/memories/USER.md        # 注意：源文件在 memories/ 下
~/.hermes/memories/MEMORY.md
~/.hermes/skills/NEW_SKILL_TEMPLATE.md
~/.hermes/skills/<category>/<skill>/SKILL.md
```

Publication rule:
- `MEMORY.md` is private by default and must not be published.
- `USER.md` must become a template, not the user's real profile.
- `SOUL.md` / `AGENTS.md` / `USER.md` — 对已有 Hermes 用户，这三个文件**不应自动覆盖**。
  repo 的 `install.sh` 检测到 `~/.hermes/` 存时会跳过它们，提示用户手动 diff 合并。
- `SOUL.md` must replace personalized identity with a generic name like `Hermes`.
- Any path, username, token hint, account name, host name, machine-specific value must be removed or generalized.

Repo-to-local mapping:

| repo 路径 | ~/.hermes/ 目标 | 备注 |
|-----------|----------------|------|
| `SOUL.md` | `~/.hermes/SOUL.md` | 存量用户不自动覆盖 |
| `AGENTS.md` | `~/.hermes/AGENTS.md` | 存量用户不自动覆盖 |
| `memories/USER.md` | `~/.hermes/memories/USER.md` | 存量用户不自动覆盖，模板 |
| `.env.example` | `~/.hermes/.env` | 仅当目标不存在时复制 |
| `vdb/*.py` | `~/.hermes/vdb/*.py` | 工具链，可安全覆盖 |
| `scripts/init-vdb.sh` | `~/.hermes/scripts/init-vdb.sh` | 存量用户跳过 .venv 重建 |
| `skills/*` | `~/.hermes/skills/` | 存量用户只补充不覆盖已有技能 |
| `install.sh` | **不复制** | 入口脚本，repo 本地运行 |

**install.sh 行为**：\n- 新装机（`~/.hermes/` 不存在）：全量复制 SOUL.md + AGENTS.md + USER.md + vdb/ + skills/\n- 存量用户（`~/.hermes/` 存在）：**跳过** SOUL.md/AGENTS.md/USER.md，只补 skills/ 和 vdb/\n- 永远不覆盖 `~/.hermes/.env`（仅模板复制到 `.env.example`）\n- `--profile <name>` 参数：安装到 `~/.hermes/profiles/<name>/`，导出 `HERMES_SKILL_DIR` 给索引步骤\n- 自动 profile 检测：非 default profile 下运行弹警告\n- vdb 路径感知：`indexer.py` 读取 `$HERMES_HOME`（profile 会话自动设）决定技能目录，不依赖持久化标记文件

---

## Workflow

### Step 1: Load Required Skills

Before any SKILL.md write, load:

```text
skill_view(name='NEW_SKILL_TEMPLATE')
skill_view(name='hermes-agent-skill-authoring')
skill_view(name='github')      # if pushing to GitHub
skill_view(name='plan')        # for multi-step sync
```

Completion criteria:
- NEW_SKILL_TEMPLATE checklist is visible before writing any `*/SKILL.md`.
- Every new skill has frontmatter satisfying the full template, not only Hermes runtime's minimal validator.

### Step 2: Build or Update Plan

Write a plan under `.hermes/plans/` or `~/.hermes/plans/` before mutating files.

Include:
- Target repo path
- Source files
- Sanitization rules
- File list to publish
- Validation commands
- Git push strategy

### Step 3: Stage Files in a Temporary or Repo Workdir

Preferred workdir:

```bash
REPO=/tmp/hermes-base-config
```

If repo does not exist:

```bash
git clone https://github.com/<USER_OR_ORG>/hermes-base-config.git "$REPO"
```

If repo already exists:

```bash
cd "$REPO"
git status --short
git pull --ff-only
```

### Step 4: Sanitize Before Writing Repo Files

Never do blind copy for public repo content. Apply transformations first.

Required replacements:

| Local/private pattern | Public replacement |
|----------------------|--------------------|
| `Hermes` （或其他个性化 agent 名） | `Hermes`（标准名） |
| real GitHub username | `YOUR_USERNAME` or repo owner placeholder |
| `/home/<user>` | `~` or `<HOME>` |
| Windows user path | `~/.hermes/` or `<HERMES_HOME>` |
| hostnames | `<HOSTNAME>` |
| real account names | `<ACCOUNT>` |
| token/PAT hints | remove entirely |
| real hardware inventory | template placeholders |

Do not publish:
- `~/.hermes/memories/MEMORY.md`
- secrets, API keys, PAT scope notes, auth file paths with real accounts
- social media account IDs, phone numbers, emails, machine hostnames
- logs containing tokens or private URLs

**额外：SOUL.md/AGENTS.md 规则自洽性。** 这些文件自身定义的约束必须不自相矛盾。例如 SOUL.md 的"输出字面量铁律"禁止单反斜杠，则规则正文中的示例必须用 `\\n` 而非 `\n`。发布前逐条检查规则正文是否违反它自己。

### Step 5: Preserve Template Structure

Rules:
- `skills/NEW_SKILL_TEMPLATE.md` stays as a file.
- Normal skills are directories: `skills/<skill-name>/SKILL.md`.
- Repo root contains only public docs/config templates.
- README examples must use `YOUR_USERNAME` or `<USER_OR_ORG>` placeholders.

### Step 6: Validate Skill Frontmatter

For every `skills/*/SKILL.md`, verify:
- `name`, `description`, `version`, `author`, `license`, `platforms`
- `metadata.hermes.tags.trigger` has at least 5 items
- `metadata.hermes.tags.disable` has at least 3 items
- `metadata.hermes.skill_type` is one of `methodology|workflow|tool|integration`
- `metadata.hermes.priority` is one of `highest|high|normal|low`
- body is non-empty

Validation command:

```bash
python3 - <<'PY'
import pathlib, re, sys, yaml
root = pathlib.Path('/tmp/hermes-base-config')
errors = []
for p in sorted(root.glob('skills/*/SKILL.md')):
    text = p.read_text(encoding='utf-8')
    if not text.startswith('---'):
        errors.append(f'{p}: missing frontmatter start')
        continue
    m = re.search(r'\n---\s*\n', text[3:])
    if not m:
        errors.append(f'{p}: missing frontmatter end')
        continue
    fm = yaml.safe_load(text[3:m.start()+3]) or {}
    for key in ['name','description','version','author','license','platforms']:
        if key not in fm:
            errors.append(f'{p}: missing {key}')
    h = (fm.get('metadata') or {}).get('hermes') or {}
    tags = h.get('tags') or {}
    trig = tags.get('trigger') or []
    dis = tags.get('disable') or []
    if len(trig) < 5:
        errors.append(f'{p}: trigger < 5')
    if len(dis) < 3:
        errors.append(f'{p}: disable < 3')
    if h.get('skill_type') not in {'methodology','workflow','tool','integration'}:
        errors.append(f'{p}: invalid/missing skill_type')
    if h.get('priority') not in {'highest','high','normal','low'}:
        errors.append(f'{p}: invalid/missing priority')
    if not text[m.end()+3:].strip():
        errors.append(f'{p}: empty body')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('skill frontmatter validation OK')
PY
```

### Step 7: Run Sanitization Scan

Use a denylist scan before commit.

```bash
cd /tmp/hermes-base-config
# 扫描本地化的 agent 名、用户名、路径、密钥
grep -RInE 'dandanlan|/home/lan|C:\\\\Users\\\\lan|fnubuntu|ghp_|token|PAT|password|api[_-]?key|secret|老黎|菜鸡的老黎|YOUR-CUSTOM-AGENT-NAME'
  --include='*.md' . || true
```

Interpretation:
- Expected words like `token` in generic security examples may be acceptable only if no real value or account appears.
- Any real username/account/host/path must be fixed before push.

### Step 8: Verify Repo Structure

```bash
find /tmp/hermes-base-config -maxdepth 3 -type f | sort
```

Must include:

```text
./install.sh
./SOUL.md
./AGENTS.md
./.env.example
./README.md
./LICENSE
./memories/USER.md
./skills/NEW_SKILL_TEMPLATE.md
./skills/<skill>/SKILL.md
./vdb/sparse.py
./vdb/embed.py
./vdb/indexer.py
./vdb/matcher.py
./vdb/__init__.py
```

Must not include:

```text
./MEMORY.md
./skills/NEW_SKILL_TEMPLATE/SKILL.md
./USER.md          # 旧位置：已迁移到 memories/USER.md
```

### Step 9: Preview and Push

**修改前必须展示给用户确认：**

```bash
cd /tmp/hermes-base-config
git status --short
git diff --cached --stat
```

用户确认后再执行：

```bash
cd /tmp/hermes-base-config
git commit -m "<type>: <subject>"
git remote set-url origin "https://$(gh auth token)@github.com/<USER_OR_ORG>/hermes-base-config.git"
git push
git remote set-url origin "https://github.com/<USER_OR_ORG>/hermes-base-config.git"
```

If HTTPS remote cannot read username in non-interactive shell, use `gh auth token` only for the push, then reset remote immediately:

```bash
git remote set-url origin "https://$(gh auth token)@github.com/<USER_OR_ORG>/hermes-base-config.git"
git push
git remote set-url origin "https://github.com/<USER_OR_ORG>/hermes-base-config.git"
```

Do not leave token-bearing remote URLs in `.git/config`.

---

## Iron Rule: No Auto-Push (2026-07-09 用户红线)

**绝对禁止在用户未明确指令的情况下向 `github.com/dandanlan8090/hermes-base-config` 推送任何内容。**

- 这是公开发布项目，不是私人 git remote
- 每次 commit + push 之前必须：
  1. 用户在本轮对话中明确说"推"、"发布"、"同步到 GitHub"、"push"等动词
  2. **先加载本项目对应的 skill（hermes-base-config-sync），阅读全部流程和约束**
  3. 跑完 Step 6 (frontmatter 验证) + Step 7 (脱敏扫描) + Step 8 (结构验证)
  4. **对照 README.md 描述确认本次变更是否需要同步更新 README**（新增功能、改目录结构、增删文件、改安装步骤等必须更新 README）
  5. 把 `git status --short` 和 `git diff --stat` 给用户看
  6. **等待用户确认后再执行 commit + push**（不可自认已确认就跳过）
- "工作流收尾"、"我整理完了顺便推一下"、"自动同步" → 全部**不构成明确指令**
- 如果不确定是否要推 → 问用户，等回答再动
- **记忆回放风险**：即使 MEMORY.md 或 session_search 找出了 "用户上次说推"，也**不构成当前对话的指令**。每次 push 需要本轮对话中单独、明确的指令。
- 详细来源：MEMORY.md "GitHub 发布禁令" 条目

**违反这条规则 = 直接侵蚀用户对 hermes-base-config 这个公开项目的可控性，每次违规都是一次小事故。**

## Common Pitfalls

1. **Blind copying local SOUL.md to repo.** Local SOUL.md may contain a personalized agent name. Replace with generic `Hermes` before publishing.

2. **Publishing MEMORY.md.** MEMORY.md contains environment facts, accounts, tokens descriptions, host quirks, and private lessons. It is not part of the public base config.

3. **Turning NEW_SKILL_TEMPLATE.md into a skill folder.** It is a standalone file under `skills/`, not `skills/NEW_SKILL_TEMPLATE/SKILL.md`.

4. **Relying on Hermes runtime validator only.** `skill_manage` only enforces minimal `name` and `description`; community template requires full frontmatter including tags, skill_type, priority.

5. **Not loading NEW_SKILL_TEMPLATE before writing SKILL.md.** AGENTS.md §1.4 makes this action-based: if target path is `*/SKILL.md`, load template first.

6. **Leaving GitHub token in remote URL.** If using `gh auth token` for push, reset origin to non-token URL immediately after push.

7. **README leaking real repo owner.** Public template examples should use `YOUR_USERNAME` or `<USER_OR_ORG>` unless intentionally documenting the canonical upstream.

8. **Assuming current session sees newly created skill.** Skill loader may be cached. Validate file content directly and use a fresh session if needed.

9. **SOUL.md 规则自洽性被忽略。** SOUL.md 自身的约束规则也可能违反自身（例如"禁止输出单反斜杠"这条规则用了 `\n` 而非 `\\n` 演示）。发布前应逐条检查：禁止某行为的规则，演示时必须用允许的形式。

10. **AGENTS.md §10.3 优先级声明可能过时。** AGENTS.md 写 USER.md > AGENTS.md > SOUL.md，但用户优先级链是 SOUL.md > AGENTS.md > USER.md。发布前须与用户确认当前优先级，必要时修正 AGENTS.md。

11. **Profile 路径差异。** 如果你或用户使用 Hermes 多 profile（`~/.hermes/profiles/<name>/`），技能目录是 `profiles/<name>/skills/` 而非 `skills/`。vdb 的 `indexer.py` 现在会读取 `HERMES_HOME` 环境变量（profile 会话自动设置），profile 用户的技能目录自动正确索引。也支持 `HERMES_SKILL_DIR` 环境变量覆盖。`install.sh --profile <name>` 会自动传 `HERMES_SKILL_DIR` 给索引步骤。无需持久化标记文件。发布前确认 repo 的 README 有 `HERMES_HOME` 路径说明。

12. **把 config.yaml 纳入 repo 范围。** config.yaml 是用户的环境配置（provider 端点、API 密钥、超时、安全白名单、显示偏好），不是项目文件。`agent.tool_use_enforcement` 和 `command_allowlist` 属于用户授权范围，repo 不管理、不承诺、不兜底。`install.sh` 不写 config.yaml，不要求用户改任何设置。详见 `references/config-dependencies.md`。

13. **Treating repo creation as repo update.** 新建 repo 需要 scope 定义（按 baseline + 路由表 + 排除系统自带三层过滤选择 skill）、GH repo 创建、初始 layout 搭建——这些在 update-only 流程中都不存在。开始前必须区分是"更新已有"还是"新建 repo"，否则会漏掉关键步骤或套用错误假设（如直接 `git pull` 已有仓库）。

---

## Verification Checklist

- [ ] Plan written before mutations
- [ ] **User explicitly instructed push in this conversation** (Iron Rule)
- [ ] NEW_SKILL_TEMPLATE loaded before any SKILL.md write
- [ ] Repo has `skills/NEW_SKILL_TEMPLATE.md` as a file
- [ ] Repo does not contain `MEMORY.md`
- [ ] USER.md is a template, not a real profile
- [ ] SOUL.md uses generic `Hermes`, not local identity
- [ ] All published skills pass full NEW_SKILL_TEMPLATE frontmatter checklist
- [ ] Sanitization grep returns no private account/path/token/host leakage
- [ ] Git remote does not contain embedded token after push
- [ ] `git log --oneline -1` confirms the intended commit
- [ ] **README.md 已同步**：目录结构、安装步骤、功能说明与本次变更一致
- [ ] **profile 安全**：install.sh 有 `--profile` 参数支持和 profile 检测告警，README 和 SOUL.md 有 profile 路径说明
- [ ] **profile 路径**：`indexer.py` 读取 `HERMES_HOME` 环境变量（profile 会话自动设），无需持久化标记文件；`HERMES_SKILL_DIR` 可覆盖
- [ ] SOUL.md/AGENTS.md 规则自洽性检查（规则演示不违反自身，优先级声明与用户对齐）
- [ ] config 依赖：目标用户的 `agent.tool_use_enforcement` 是否为 `always`？（否则 AGENTS.md §0.5 可能失效）
- [ ] config 依赖：目标用户的 `command_allowlist` 是否包含必要条目？（否则 install.sh 被拦截）
- [ ] vdb 相关：`matcher.py` 有 try/except 冷启动 + `is_healthy()` + `search()` 安全降级
- [ ] vdb 相关：`indexer.py` 写 `vdb_state.json`（`build_index()` 后自动生成）
- [ ] Profile 路径：如果目标用多 profile，README 有路径说明

---

**最后更新**: 2026-07-10