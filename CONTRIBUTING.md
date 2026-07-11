# Contributing to Hermes Micro Framework

感谢你考虑为 Hermes Micro Framework 做贡献！本指南面向所有协作者——无论你是修一个 typo 还是吸收一个全新的外部技能。

---

## 目录

- [行为准则](#行为准则)
- [项目结构速览](#项目结构速览)
- [开发工作流](#开发工作流)
- [提交规范](#提交规范)
- [PR 流程](#pr-流程)
- [Skill 命名与格式规范](#skill-命名与格式规范)
- [吸收外部技能](#吸收外部技能)
- [脱敏红线](#脱敏红线)

---

## 行为准则

- 尊重、包容、就事论事
- 讨论聚焦在技能内容本身，不针对个人
- 提出不同方案时用数据/示例支撑，而非立场

---

## 项目结构速览

```
hermes-micro-framework/
├── SOUL.md              # 铁律 + 路由表（框架核心，改动需谨慎）
├── README.md            # 开发者文档
├── TROUBLESHOOTING.md   # 故障排查
├── CONTRIBUTING.md       # 本文件
├── vdb/                 # 检索工具链（纯代码）
├── scripts/             # 安装/索引脚本
└── skills/              # 62 个技能（元数据资产，全量同步）
```

**架构分界（重要）**：代码 + 元数据（`skills/**` frontmatter）入库；**索引（Chroma）和运行时（`.venv`/`.env`）不入库**，由 `install.sh` 在用户机器上就地生成。

---

## 开发工作流

```bash
# 1. Fork 并 clone
git clone https://github.com/<your-username>/hermes-micro-framework.git
cd hermes-micro-framework

# 2. 创建特性分支
git checkout -b feat/your-change

# 3. 本地修改（SOUL.md / skills / vdb / README 等）

# 4. 脱敏检查（详见下方「脱敏红线」）
grep -rnE "/home/[a-z]+|fnubuntu|dandanlan|Hermes-fn" \
  --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/" || echo "CLEAN"

# 5. 技能合规验证（如改了 skills/）
python3 - <<'PY'
import pathlib, re, yaml
root = pathlib.Path('skills')
for p in sorted(root.glob('**/SKILL.md')):
    t = p.read_text()
    assert t.startswith('---'), f'{p}: no frontmatter'
    fm = yaml.safe_load(t[3:re.search(chr(10)+'---'+chr(10), t[3:]).start()+3])
    h = fm.get('metadata',{}).get('hermes',{})
    assert len(h.get('tags',{}).get('trigger',[])) >= 7, f'{p}: trigger<7'
    assert len(h.get('tags',{}).get('disable',[])) >= 2, f'{p}: disable<2'
print('frontmatter OK')
PY

# 6. 提交
git add -A
git commit -m "type: subject"

# 7. 推送并开 PR
git push origin feat/your-change
```

---

## 提交规范

提交信息格式：`type: subject`

| type | 用途 |
|------|------|
| `feat` | 新增技能 / 新功能 |
| `fix` | 修复 bug / 修正内容错误 |
| `refactor` | 重构（不改行为） |
| `docs` | 文档（README / TROUBLESHOOTING / 本文件） |
| `sanitize` | 脱敏 / 安全相关 |
| `chore` | 杂项（版本号、依赖） |

示例：
```
feat: 新增 performance-optimization 技能（methodology/）
fix: debugging-patterns trigger 误召 "排查报错"
docs: README 增 Mermaid 架构图
sanitize: 移除 SKILL.md 中的个人路径
```

---

## PR 流程

1. **Fork** 本仓库到你的 GitHub 账号
2. **创建分支**：`feat/xxx` 或 `fix/xxx`（不要直接推 `main`）
3. **本地验证**：跑上面的脱敏检查 + frontmatter 合规验证
4. **推送分支** 到你的 fork
5. **开 PR** 到 `dandanlan8090/hermes-micro-framework:main`
6. **PR 描述** 说明：
   - 改了什么、为什么
   - 是否改了 `skills/`（如果是，frontmatter 是否合规）
   - 是否改了 `SOUL.md`（铁律变更需额外说明动机）
7. **等待 review**：维护者会检查脱敏 + 合规 + 内容质量
8. **合并**：通过后由维护者 squash merge

> 注意：**每次向公开仓库推送都需要明确的授权**。如果你是维护者，推送前确认本轮对话中用户已明确说"推"/"push"。

---

## Skill 命名与格式规范

### 命名

- **技能目录名**：全小写 + 连字符，≤ 64 字符
  - ✅ `performance-optimization` `hermes-tdd-workflow`
  - ❌ `PerformanceOptimization` `perf_opt` `性能优化`
- **放在正确分类目录**下（见下）

### 分类目录

| 目录 | 加载特点 | 示例 |
|------|---------|------|
| `core/` | 铁律违规时触发 | `hermes-truth-redline` |
| `workflow/` | 用户触发场景关键词 | `hermes-tdd-workflow` |
| `methodology/` | vdb 语义匹配 / 用户明确要求 | `debugging-patterns` |
| `infrastructure/` | 框架故障排查时低频加载 | `autoload-vdb` |
| `integration/` | 外部系统交互时加载 | `hermes-agent` |
| `media/` `research/` `mlops/` `smart-home/` 等 | 外部吸收的领域技能 | `youtube-content` `arxiv` |

> 不确定放哪？看技能"被触发的方式"：是铁律触发、关键词触发、还是领域专属。

### Frontmatter 完整模板

```yaml
---
name: my-skill-name               # 小写 + 连字符，≤64 字符
description: Use when <触发场景>. <核心动作 + 产出>.   # ≤1024 字符，三段式
version: 1.0.0
author: Hermes Agent             # 公开 repo 用通用名，勿用内部代号
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
      - 触发词1
      - 触发词2
      # ... 至少 7 条，全用用户视角自然语言
      disable:
      - 易误召本技能的短语
      # ... 至少 2-3 条，phrase-level（见 METADATA_GUIDE.md）
    skill_type: methodology      # workflow / methodology / infrastructure / integration
    priority: high
    related_skills:
    - other-skill
---

# 技能正文（# 标题 → ## When to Use → 工作流 → 失败模式 → 验证清单）
```

### 关键约束

- **trigger_tags ≥ 7 条**：全用高频自然语言（用户口语），不写内部概念词、不写纯英文
- **disable_tags ≥ 2 条**：写"容易误召本技能、但该走别处"的 query 子串
- **description 含中文优先**：纯英文 desc 进不了 sparse 中文索引，降低中文 query 召回
- **改完必须重建索引**：`python3 ~/.hermes/scripts/vdb-autoload.py --auto`
- 完整规范见 `autoload-vdb/references/METADATA_GUIDE.md`

---

## 吸收外部技能

框架持续从优秀的外部技能仓库吸收方法论。已参考并吸收的来源：

| 仓库 | Stars | 状态 |
|------|-------|------|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | ~77k | 已吸收 10+ 技能（tdd/git-worktree/debugging/ci-cd/spec-driven 等） |
| [obra/superpowers](https://github.com/obra/superpowers) | ~252k | 方法论参考（agentic skills framework） |
| [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | ~8k | vdb 检索管道对比参考（稠密+稀疏融合策略、RRF vs 加权、IDF 过期检测） |

### 吸收流程（摘要）

1. **扫描结构**：了解对方仓库布局与格式
2. **同类定位**：按名称/描述匹配已有技能，标记 重叠 / 缺失 / 无关
3. **质量评估**：读重叠技能的 SKILL.md，对比深度/广度/准确性
4. **格式适配**：补全 Hermes frontmatter（name/description/version/author/license/platforms + trigger≥7/disable≥2 + skill_type + related_skills）
5. **放入正确分类目录**
6. **同步**：SOUL.md 路由表 + 技能索引 + README 技能全集
7. **脱敏 + 重建索引**

> 详细记录见 `skills/integration/hermes-micro-framework/references/addyosmani-absorption.md` 和 `addyosmani-agent-skills-comparison.md`。

### 评估标准（是否值得吸收）

- **通用性**：不绑定特定框架/平台
- **可复用性**：至少 3 个以上场景能用
- **方法论性**：不是工具教程 / 不是元技能（教人用框架本身）
- ** Attribution**：吸收外部内容保留原作者信息，不冒领

---

## 脱敏红线

**公开仓库，任何个人身份信息都不得入库。**

推送前必须确保以下内容**不出现**在 diff 中：

| 禁止 | 说明 |
|------|------|
| `/home/<username>` 等个人路径 | 用 `~` 替代 |
| 主机名（如 `fnubuntu`） | 用 `[HOSTNAME]` 替代 |
| 内部代号（如 `Hermes-fn`） | 用 `Hermes` 替代 |
| GitHub 用户名（非仓库 owner） | 用 `YOUR_USERNAME` 替代 |
| Token / API Key | 绝不入库（`.env` 不入库） |
| `MEMORY.md` / 个人记忆 | 不发布 |

快速自检：
```bash
grep -rnE "/home/[a-z]+|fnubuntu|dandanlan|Hermes-fn|ghp_|sk-[A-Za-z0-9]{20}" \
  --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/" || echo "CLEAN"
```

---

## 有问题？

- 开 Issue 描述你遇到的问题或建议
- 参考 `TROUBLESHOOTING.md` 排查常见安装/索引问题
- 技能写法细节见 `autoload-vdb/references/METADATA_GUIDE.md`

再次感谢你的贡献！🚀
