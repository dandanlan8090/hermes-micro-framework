# Hermes Micro Framework

> Hermes 微内核框架配置模板仓库。极致拆解 SOUL.md + 按分类组织的技能集 + vdb 语义检索。

本仓库提供一套**微内核架构**的 Hermes 配置方案：SOUL.md 仅保留不可撼动的铁律和路由表，所有方法论、工作流、约束细则全部分布在独立 skill 中，通过 vdb 按需加载。

相比传统全量 SOUL.md 模式，token 开销降低 60%+，且框架演进完全由用户驱动。

---

## 目录结构

```
hermes-micro-framework/
├── install.sh                 # 一键部署（新装全量 / 存量补充 / --profile）
├── README.md                  # 本文件
├── LICENSE                    # MIT
├── TROUBLESHOOTING.md         # 故障排查指南
│
├── SOUL.md                    # → ~/.hermes/SOUL.md
├── .env.example               # → ~/.hermes/.env
│
├── memories/
│   ├── USER.md                # 用户画像模板
│   └── FRAMEWORK_EVOLUTION.md # 框架演进记录
│
├── vdb/                       # 技能检索工具链
│   ├── sparse.py              # 词法权重
│   ├── embed.py               # BGE-M3 API 包装
│   ├── indexer.py             # Chroma 索引构建
│   ├── matcher.py             # 混合检索
│   └── __init__.py
│
├── scripts/
│   ├── init-vdb.sh            # 环境初始化
│   └── vdb-autoload.py        # 预热 + 索引检测
│
└── skills/
    ├── core/                  # 铁律细则（9 个微技能）
    ├── workflow/              # 高频工作流（9 个）
    ├── methodology/           # 思维框架（13 个）
    ├── infrastructure/        # 框架机制（8 个）
    ├── integration/           # 外部集成（4 个）
    └── templates/             # NEW_SKILL_TEMPLATE.md
```

---

## 系统要求

### 必须
- **Hermes Agent**（任意版本，推荐最新）
  - 安装：`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
  - 或：`pip install hermes-agent`
- **Git**（clone 仓库）
- **Python 3.10+**（vdb 工具链）
- **网络**（vdb 需要访问 SiliconFlow API 做嵌入）

### 可选
- `gh` CLI（推荐，用于推送/查看仓库）
- SiliconFlow API Key（免费 2000 RPM，[注册](https://siliconflow.cn)）

---

## 安装

### 全新安装（无 `~/.hermes/`）

```bash
git clone https://github.com/dandanlan8090/hermes-micro-framework.git
cd hermes-micro-framework
bash install.sh
```

脚本自动完成：
1. 复制 `SOUL.md`、`memories/USER.md` 到 `~/.hermes/`
2. 从 `.env.example` 创建 `~/.hermes/.env`
3. 补充 skills/ 到 `~/.hermes/skills/`
4. 复制 vdb/ 工具链
5. 创建 Python 虚拟环境 + 安装依赖
6. 重建 Chroma 向量索引
7. **vdb 预热 + 索引过期检测**（自动重建）

完成后：
```bash
# 编辑 API Key
nano ~/.hermes/.env

# 启动 Hermes
hermes chat
```

### 存量更新（已有 `~/.hermes/`）

```bash
git clone https://github.com/dandanlan8090/hermes-micro-framework.git
cd hermes-micro-framework
bash install.sh
```

存量模式特点：
- **跳过** SOUL.md / USER.md（提示手动 `diff` 合并）
- **补充** skills/ 中不存在的技能
- **覆盖** vdb/ 工具链（安全）
- 跳过 .venv 重建

手动合并核心文件：
```bash
diff -u ~/.hermes/SOUL.md  SOUL.md
diff -u ~/.hermes/memories/USER.md memories/USER.md
```

### 多 Profile 安装

```bash
# 先确认当前 profile
hermes profile list   # ◆ 标记活跃 profile

# 安装到指定 profile
bash install.sh --profile work
```

如果不指定 `--profile`，脚本会自动检测非 default profile 并警告。
Profile 模式下：
- `SOUL.md` → `~/.hermes/profiles/<name>/`
- `skills/` → `~/.hermes/profiles/<name>/skills/`
- `vdb/` → 全局共享，自动跟随 `$HERMES_HOME`
- `.env` → 全局共享

### 强制覆盖

```bash
bash install.sh --force
```

全量覆盖包括 SOUL.md / USER.md。仅新装机使用。

---

## 配置

### 1. API Key（必须）

vdb 使用硅基流动的 BGE-M3 做云端嵌入。编辑 `~/.hermes/.env`：

```bash
SILICONFLOW_API_KEY=sk-your-key-here
```

免费注册：https://siliconflow.cn

### 2. 切换嵌入模型（可选）

修改 `vdb/embed.py` 顶部两个常量：

```python
API_URL = "https://api.siliconflow.cn/v1/embeddings"  # 换 URL
MODEL = "BAAI/bge-m3"                                   # 换模型名
```

改完重建索引：`cd ~/.hermes/vdb && source .venv/bin/activate && PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"`

### 3. 框架演进钩子

框架变更自动记录到 `~/.hermes/memories/FRAMEWORK_EVOLUTION.md`，每积累 3 条触发一次评审。

---

## 使用

### 启动 Hermes

```bash
hermes chat                    # 默认 profile
hermes -p work chat            # 指定 profile
```

### SOUL.md 铁律

启动后 SOUL.md 的 7 条铁律自动加载：

| # | 铁律 | 完整细则 |
|---|------|----------|
| 0 | 技能检索（强制入口）：命中路由表/任务对应skill/不确定/涉铁律操作时必须检索 | 四层检索 vdb > 路由表 > 列表 > 手动 |
| 1 | 信息真实性：不得编造 | `hermes-truth-redline` |
| 2 | 代码输出：完整代码块 | `hermes-code-output` |
| 3 | 验证前置：IDENTIFY→RUN→READ→VERIFY | `hermes-verification-rules` |
| 4 | 安全约束：不生成恶意脚本 | `hermes-safety` |
| 5 | 改进优先：patch > 新建 | `hermes-evolution-rules` |
| 6 | 思考范围：不规划后续/不预判/不过度推演/不拓展 | 4 个 boundary 微技能 |

铁律#6 拆为 4 个微技能，按违规行为精准触发：
- 规划后续对话 → `skill_view(name='hermes-boundary-no-future-planning')`
- 预判后续任务 → `skill_view(name='hermes-boundary-no-task-prediction')`
- 过度推演 → `skill_view(name='hermes-boundary-no-over-reasoning')`
- 自行拓展场景 → `skill_view(name='hermes-boundary-no-scope-creep')`

### vdb 按需加载

框架技能通过 vdb 语义检索按需加载：

```bash
# 健康检查
python3 ~/.hermes/scripts/vdb-autoload.py --check

# 手动测试召回
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from matcher import search; [print(r['skill_name'], r['final_score']) for r in search('你的问题')[:5]]"
```

### 主脑模式

当需要多 Agent 调度时，说"使用主脑模式"或"Oracle Mode"，
系统自动加载 `hermes-oracle-mode` skill。

### 技能速览索引

SOUL.md 末尾附有完整技能索引（§技能索引），按 5 个分类列出所有 skill 名称。
需要浏览可用技能时，直接查阅该索引。

---

## 技能全集

### core/ — 铁律细则（9 个）

| 技能 | 说明 | 触发 |
|------|------|------|
| `hermes-truth-redline` | 信息真实性红线 | 编造/不确定/高危操作 |
| `hermes-code-output` | 代码输出规范 | 脚本/配置输出 |
| `hermes-verification-rules` | 验证铁律 | 完成/成功结论前 |
| `hermes-safety` | 安全约束 | 恶意/入侵/脱敏 |
| `hermes-evolution-rules` | 改进优先 | 修改框架自身 |
| `hermes-boundary-no-future-planning` | 不规划后续对话 | agent 引导下一轮 |
| `hermes-boundary-no-task-prediction` | 不预判任务 | agent 脑补需求 |
| `hermes-boundary-no-over-reasoning` | 不过度推演 | 思考链过长 |
| `hermes-boundary-no-scope-creep` | 不拓展场景 | agent 主动给额外建议 |

### workflow/ — 工作流（10 个）

| 技能 | 说明 |
|------|------|
| `hermes-oracle-mode` | 主脑模式：多 Agent 调度 |
| `hermes-plan-workflow` | Plan + todo 推进 |
| `hermes-tdd-workflow` | TDD 测试驱动 |
| `hermes-shipping-verification` | 发布验证 + 回滚 |
| `hermes-parallel-dispatch` | 并行 Agent 派发 |
| `hermes-git-worktree` | Git 工作流 + worktree 隔离 |
| `hermes-fault-troubleshooting` | 系统故障处理 |
| `repo-publishing-workflow` | 仓库发布与同步 |
| `agent-collaboration-workflow` | 三 Agent 协作 |
| `ci-cd-and-automation` | CI/CD pipeline 自动化 |

### methodology/ — 思维框架（19 个）

| 技能 | 说明 |
|------|------|
| `source-driven-development` | 源码驱动开发 |
| `doubt-driven-development` | 怀疑驱动审查 |
| `code-review-and-audit` | 代码审查 |
| `debugging-patterns` | 交互式调试 + 生产问题排查 |
| `codebase-memory-first` | 代码知识图谱 |
| `ai-conv-style-discipline` | CLI 对话风格 |
| `hermes-knowledge-base` | 知识库整理 |
| `hermes-todo-progress` | TODO 进度 |
| `hermes-agent-skill-authoring` | 技能创建规范 |
| `hermes-framework-evolution` | 框架演进方法论 |
| `code-simplification` | 代码简化 |
| `plan` | Plan Mode |
| `openai-compat-thinking` | 推理链思考 |
| `performance-optimization` | 性能优化（前端/后端/数据库） |
| `spec-driven-development` | Spec 先行开发 |
| `deprecation-and-migration` | 废弃与迁移管理 |
| `incremental-implementation` | 增量实现（垂直切片） |
| `api-and-interface-design` | API 设计规范 |

### infrastructure/ — 框架机制（8 个）

| 技能 | 说明 |
|------|------|
| `vdb-retrieval-pipeline` | vdb 语义检索管道 |
| `hermes-framework-loader` | 框架文件加载规则 |
| `hermes-framework-architecture` | 框架架构参考 |
| `hermes-framework-troubleshooting` | 框架故障诊断 |
| `hermes-framework-changelog` | 框架变更审计 |
| `autoload-vdb` | vdb 自动加载 |
| `codebase-memory-mcp` | 代码图谱 MCP |
| `hermes-self-optimization` | 系统 Prompt 优化 |

### integration/ — 外部集成（4 个）

| 技能 | 说明 |
|------|------|
| `hermes-agent` | Hermes 配置与排障 |
| `hermes-base-config-sync` | 配置仓库同步 |
| `system-admin` | 系统管理 |
| `github` | GitHub 工作流 |
| `hermes-micro-framework` | **本仓库维护规则** |

---

## 开发者指南

### 本地工作流

```bash
# 1. Clone
git clone https://github.com/dandanlan8090/hermes-micro-framework.git
cd hermes-micro-framework

# 2. 修改内容（SOUL.md / skills / README 等）

# 3. 脱敏检查
grep -rnE "/home/[a-z]+|fnubuntu|dandanlan|Hermes-fn" \
  --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/" || echo "CLEAN"

# 4. 技能合规验证
python3 -c "
import pathlib, re, yaml
root = pathlib.Path('skills')
for p in sorted(root.glob('*/*/SKILL.md')):
    t = p.read_text(); assert t.startswith('---'), f'{p}: no fm'
    fm = yaml.safe_load(t[3:re.search(chr(10)+'---'+chr(10), t[3:]).start()+3])
    h = fm.get('metadata',{}).get('hermes',{})
    assert len(h.get('tags',{}).get('trigger',[])) >= 5, f'{p}: trigger<5'
    assert len(h.get('tags',{}).get('disable',[])) >= 3, f'{p}: disable<3'
print('frontmatter OK')
"

# 5. 提交
git add -A
git commit -m "type: subject"
# type: feat / fix / refactor / docs / sanitize

# 6. 推送（需用户明确授权）
git remote set-url origin "https://$(gh auth token)@github.com/dandanlan8090/hermes-micro-framework.git"
git push
git remote set-url origin "https://github.com/dandanlan8090/hermes-micro-framework.git"
```

### 新增 skill 流程

1. 在正确分类下创建 `skills/<category>/<name>/SKILL.md`
2. 遵守 `hermes-agent-skill-authoring` 规范（trigger ≥5, disable ≥3）
3. 在 `SOUL.md §技能路由表` 新增一行
4. 在 `README.md §技能全集` 新增一行
5. 重建 vdb 索引：`build_index(force=True)`

### 推送红线

**每次推送需要本轮对话中单独的、明确的用户授权。** commit ≠ push。

---

## 技能检索系统（vdb）

### 架构

```
query
  │
  ├──▶ 云端 (SiliconFlow BAAI/bge-m3, 1024d)
  │     Chroma hnsw cosine 召回 top-16
  │
  └──▶ 本地 (sparse.py, 纯 Python)
       仅 trigger_tags → lexical matching
       final = 0.6 × dense + 0.4 × sparse
       → disable 过滤 → top-5
```

### 健康检查

```bash
# 索引过期检测
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from indexer import check_index_stale; s,r=check_index_stale(); print('过期' if s else '最新', r)"

# 完整启动检测
python3 ~/.hermes/scripts/vdb-autoload.py --check   # 只检测
python3 ~/.hermes/scripts/vdb-autoload.py --force   # 检测 + 过期自动重建
```

### 模型替换

默认使用硅基流动 BGE-M3（免费 2000 RPM）。只改 `vdb/embed.py` 两个常量即可切换：

```python
API_URL = "https://api.siliconflow.cn/v1/embeddings"  # → 换 URL
MODEL = "BAAI/bge-m3"                                   # → 换模型名
```

改完 `build_index(force=True)` 重建。

---

## License

MIT
