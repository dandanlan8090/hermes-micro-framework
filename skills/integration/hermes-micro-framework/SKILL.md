---
name: hermes-micro-framework
description: Hermes Micro Framework 仓库维护技能——记录 repo 推送规则、脱敏标准、目录结构和更新工作流。当需要向 github.com/dandanlan8090/hermes-micro-framework 推送内容时使用。
version: 1.1.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
metadata:
  hermes:
    tags:
      trigger:
      - hermes-micro-framework
      - 推送 micro-framework
      - 更新 micro-framework
      - micro-framework repo
      - 同步微框架
      - 发布 micro-framework
      - 脱敏检查
      - 技能合规验证
      disable:
      - 普通 git push
      - 非 Hermes 配置
      - 私有 MEMORY.md
      - 不发布到开源
    skill_type: workflow
    priority: high
    related_skills:
    - hermes-base-config-sync
    - repo-publishing-workflow
    - hermes-agent-skill-authoring
---
# Hermes Micro Framework Repo Sync

## Overview

本 skill 用于维护 `dandanlan8090/hermes-micro-framework` 仓库。该仓库是 Hermes 微内核架构的配置模板仓库，包含极致拆解后的 SOUL.md、按分类组织的技能集和 vdb 检索工具链。

核心原则：**内容必须脱敏、结构必须合规、每次推送必须用户明确授权。**

---

## Canonical Repo Layout

```
hermes-micro-framework/
├── install.sh                 # 一键部署（新装全量 / 存量补充 / --profile）
├── README.md                  # 开发者文档
├── LICENSE
├── TROUBLESHOOTING.md         # 故障排查指南
│
├── SOUL.md                    # → ~/.hermes/SOUL.md（存量不覆盖）
├── .env.example               # → ~/.hermes/.env（如果不存在）
│
├── memories/
│   ├── USER.md                # 用户画像模板（存量不覆盖）
│   └── FRAMEWORK_EVOLUTION.md # 框架演进钩子文件
│
├── vdb/                       # 技能检索工具链
│   ├── sparse.py              # 词法权重（纯 Python）
│   ├── embed.py               # SiliconFlow BGE-M3 云端嵌入
│   ├── indexer.py             # Chroma 索引构建
│   ├── matcher.py             # 0.6 dense + 0.4 sparse 混合检索
│   └── __init__.py
│
├── scripts/
│   ├── init-vdb.sh            # .venv + pip + build_index
│   └── vdb-autoload.py        # 预热 + 索引过期检测 + 自动重建
│
│   └── skills/
│       ├── core/                  # 铁律细则（9 skills）
│       ├── workflow/              # 高频工作流（10 skills）
│       ├── methodology/           # 思维框架（19 skills）
│       ├── infrastructure/        # 框架机制（8 skills）
│       ├── integration/           # 外部集成（5 skills）
    └── templates/             # NEW_SKILL_TEMPLATE.md
```

**分类职责：**

| 分类 | 加载特点 | Token |
|------|---------|-------|
| `core/` | 检测到铁律违规时触发对应微技能 | 150-200 |
| `workflow/` | 用户触发场景关键词时加载 | 400-800 |
| `methodology/` | vdb 语义匹配或用户明确要求 | 300-600 |
| `infrastructure/` | 框架故障排查时低频加载 | 300-600 |
| `integration/` | 涉及外部系统交互时加载 | 400-800 |
| `templates/` | 创建新技能时人工查阅 | — |

---

## 源文件映射

| Repo 路径 | ~/.hermes/ 目标 | 备注 |
|-----------|----------------|------|
| `SOUL.md` | `~/.hermes/SOUL.md` | 存量用户不自动覆盖 |
| `memories/USER.md` | `~/.hermes/memories/USER.md` | 模板，存量不覆盖 |
| `.env.example` | `~/.hermes/.env` | 仅当目标不存在时复制 |
| `vdb/*.py` | `~/.hermes/vdb/*.py` | 安全覆盖 |
| `scripts/init-vdb.sh` | `~/.hermes/scripts/init-vdb.sh` | 全量覆盖 |
| `skills/*` | `~/.hermes/skills/` | 存量只补充不覆盖 |

**不发布：**
- `~/.hermes/memories/MEMORY.md`（隐私）
- 任何含个人路径、用户名、token、hostname 的内容

---

## Workflow

### Step 1: 确定变更范围

| 变更类型 | 影响范围 |
|----------|---------|
| 新增 skill | SOUL.md 路由表 + skills/ + README.md |
| 修改 SOUL.md 铁律 | SOUL.md + README.md + core/ 对应 skill |
| 修改路由表 | SOUL.md §技能路由表 |
| 框架演进变更 | FRAMEWORK_EVOLUTION.md + 对应 skill |
| 修复 bug | 对应文件 + TROUBLESHOOTING.md |

### Step 2（补充）：外部技能吸收

从外部仓库（如 addyosmani/agent-skills）吸收 skill 时：

1. 对比分析：识别重叠（吸收精华）和缺失（新增）的技能
2. 格式转换：补全 Hermes metadata（trigger ≥5, disable ≥3, skill_type, priority）
3. 分类放置：按 core/workflow/methodology/infrastructure/integration 放入正确目录
4. 路由表注册：SOUL.md §技能路由表 新增对应行
5. README 更新：技能全集表同步新增
6. SOUL.md 技能索引：末尾分类速览同步更新数量
7. 去重清理：原 repo 的 SVN.md 不要混入（仅吸收 SKILL.md 内容）
8. 参考文档：每次吸收建立 `references/<repo>-absorption.md` 记录范围和方法

### Step 3: 脱敏扫描

```bash
cd /tmp/hermes-micro-framework
grep -rnE "/home/lan|fnubuntu|dandanlan|Hermes-fn" \
  --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/" || echo "CLEAN"
```

### Step 4: 合规验证

```bash
# Frontmatter 验证（全部 skill）
python3 - <<'PY'
import pathlib, re, sys, yaml
root = pathlib.Path('/tmp/hermes-micro-framework/skills')
errors = []
for p in sorted(root.glob('*/*/SKILL.md')):
    text = p.read_text(encoding='utf-8')
    if not text.startswith('---'): errors.append(f'{p}: missing frontmatter')
    m = re.search(r'\n---\s*\n', text[3:])
    if not m: errors.append(f'{p}: missing frontmatter end')
    fm = yaml.safe_load(text[3:m.start()+3]) or {}
    for key in ['name','description','version','author','license','platforms']:
        if key not in fm: errors.append(f'{p}: missing {key}')
    h = (fm.get('metadata') or {}).get('hermes') or {}
    tags = h.get('tags') or {}
    if len(tags.get('trigger') or []) < 5: errors.append(f'{p}: trigger < 5')
    if len(tags.get('disable') or []) < 3: errors.append(f'{p}: disable < 3')
if errors: print('\n'.join(errors)); sys.exit(1)
print('frontmatter OK')
PY
```

### Step 5: 验证目录结构

```bash
find /tmp/hermes-micro-framework -maxdepth 3 -type f | grep -v ".git/" | sort
```

必须包含：`SOUL.md`, `install.sh`, `README.md`, `LICENSE`, `.env.example`, `memories/USER.md`, `vdb/*.py`, `scripts/`, `skills/core/workflow/methodology/infrastructure/integration/templates`

### Step 6: 预览变更

```bash
cd /tmp/hermes-micro-framework
git status --short
git diff --cached --stat
```

### Step 7: Commit + Push

```bash
cd /tmp/hermes-micro-framework
git add -A
git commit -m "type: subject"
# Token 注入推送，推完立即还原
git remote set-url origin "https://$(gh auth token)@github.com/dandanlan8090/hermes-micro-framework.git"
git push
git remote set-url origin "https://github.com/dandanlan8090/hermes-micro-framework.git"
```

---

## Iron Rule: 每次推送必须用户明确授权

**绝对禁止在用户未明确指令的情况下向 `github.com/dandanlan8090/hermes-micro-framework` 推送任何内容。**

- 每次 push 需要本轮对话中单独的、明确的指令（"推"、"push"、"发布"）
- commit ≠ push。本地 commit 完成不等于可以发 remote
- "上轮说过推"不构成当前轮的授权
- 违反 = 侵蚀用户对公开项目的可控性

---

## Common Pitfalls

1. **Blind copy SOUL.md** — 本地 SOUL.md 可能含个性化修改，发布前检查
2. **Publishing MEMORY.md** — 永远不发布
3. **skills/ 目录结构不一致** — 新 skill 必须放在正确分类下（core/workflow/methodology/infrastructure/integration），见目录分类表
4. **路由表未同步** — 新增 skill 后忘记在 SOUL.md §技能路由表 加一行
5. **Token 残留 remote URL** — 推完立即 `git remote set-url origin https://github.com/...`
6. **vdb 未重建** — 新增/修改 skill 后必须 `build_index(force=True)`
7. **install.sh 未适配新结构** — 如果改了 skills/ 目录结构，同步更新 install.sh
8. **外部技能未做格式转换** — 从 addyosmani/agent-skills 等外部仓库吸收技能时，需补 Hermes metadata（trigger/disable tags）并放入正确分类目录；对比分析见 `references/addyosmani-absorption.md`
9. **SOUL.md 技能索引未同步** — 新增/删除 skill 后忘记更新末尾 §技能索引 的分类数量和名称
10. **铁律#0 加固后 README 未更新** — 修改铁律#0 触发条件后需同步更新 README.md 的铁律说明表

---

## Verification Checklist

- [ ] 用户在本轮明确说"推"/"push"
- [ ] 脱敏扫描无个人路径/hostname/token
- [ ] 所有 skill frontmatter 合规（trigger ≥5, disable ≥3）
- [ ] SOUL.md 路由表与 skills/ 目录一致
- [ ] SOUL.md 末尾技能索引（数量+列表）已同步
- [ ] README.md 已同步更新（技能列表、目录结构、铁律说明）
- [ ] install.sh 已适配（如果改了目录结构）
- [ ] vdb 已重建（`build_index(force=True)`）
- [ ] Git remote 不含 token
- [ ] `git log --oneline -1` 确认预期 commit
