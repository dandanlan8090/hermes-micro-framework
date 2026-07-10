# Hermes Micro Framework

> Hermes 微内核框架配置模板仓库。包含核心 SOUL.md、架构技能集和 vdb 技能检索工具链。

repo 目录结构直接镜像 `~/.hermes/`，clone 后 `bash install.sh` 即可部署。

**⚠ 关键安全注意：Hermes 对自身所处的 profile 环境感知弱。**
如果你在使用 Hermes 多 profile（非默认 profile），hermes 可能把配置装错目录。
**运行 install.sh 前，务必确认当前是否在 profile 会话中：**

```bash
hermes profile list   # ◆ 标记当前活跃 profile
```

- 如果 `◆default` → 直接 `bash install.sh`
- 如果 `◆work` 或其他 profile → `bash install.sh --profile work`
- 不确定时，默认 `bash install.sh` 会装到全局 `~/.hermes/`

安装脚本会自动检测非 default profile 并警告。

---

## 与 hermes-base-config 的区别

此仓库是当前正在磨合的新架构——微内核 + skill 按需加载 + vdb 语义匹配。
相比旧版全量 SOUL.md 模式，当前架构更省 token 但仍在迭代。

| 特性 | hermes-base-config（旧版） | hermes-micro-framework（当前） |
|------|---------------------------|-------------------------------|
| 架构 | 全量 SOUL.md + AGENTS.md | 微内核 SOUL.md，skill 按需加载 |
| 技能加载 | 预加载全部 | vdb 语义匹配 + 路由表 |
| AGENTS.md | 有 | 已废弃，内容分布到 skill |
| token 开销 | 较高 | 较低 |
| 成熟度 | 稳定 | 磨合中 |

---

## 重要说明（必读）

**已有 Hermes 用户的核心文件不要直接覆盖：**

| 文件 | 说明 |
|------|------|
| `SOUL.md` | Agent 执行铁律，你可能已有自定义修改 |
| `memories/USER.md` | 你的画像和环境配置，仓库只提供模板 |

`install.sh` 检测到 `~/.hermes/` 已存在时会**跳过这两个文件**，并提示手动 diff 合并。
**新装机用户（无 `~/.hermes/`）会全量复制。**

其余目录（`vdb/` `skills/` `scripts/` `.env.example`）可安全覆盖/补充。

**profile 用户特别注意**：如果你使用 Hermes 多 profile（`~/.hermes/profiles/<name>/`），
安装路径有所不同：
- `SOUL.md` → 每个 profile 独立，分别复制到 `~/.hermes/profiles/<name>/`
- `skills/` → 每个 profile 可能有自己的技能集，需按需同步
- `vdb/` 工具链 → 全局共享 `~/.hermes/vdb/`，技能目录自动跟随当前 profile 会话：
  - profile 会话（`hermes -p work chat`）自动设 `HERMES_HOME` → `indexer.py` 读 `$HERMES_HOME/skills`
  - default 会话（`hermes chat`）无 `HERMES_HOME` → 默认 `~/.hermes/skills/`
  - 环境变量 `HERMES_SKILL_DIR` 可临时覆盖（最高优先级）
- `.env` → 全局共享 `~/.hermes/.env`，不受 profile 影响

---

## 目录结构

```
hermes-micro-framework/
├── install.sh              # 一键部署（新装全量 / 存量仅补技能和工具链）
├── README.md
├── LICENSE
├── TROUBLESHOOTING.md
│
├── SOUL.md                 # → ~/.hermes/SOUL.md（存量不覆盖）
├── .env.example            # → ~/.hermes/.env（如果不存在）
│
├── memories/
│   └── USER.md             # → ~/.hermes/memories/USER.md（存量不覆盖）
│
├── vdb/                    # 技能检索系统工具链
│   ├── sparse.py           # 中文/英文 token 分词 + lexical weights
│   ├── embed.py            # SiliconFlow BGE-M3 API 包装
│   ├── indexer.py          # Chroma 索引构建器
│   ├── matcher.py          # 0.6 dense + 0.4 sparse 混合检索
│   └── __init__.py         # 包入口
│
├── scripts/
│   ├── init-vdb.sh         # 虚拟环境 + 依赖 + API Key + 索引构建
│   └── vdb-autoload.py     # 启动预热 + 索引过期检测 + 自动重建
│
└── skills/                 # 架构核心技能集
    ├── NEW_SKILL_TEMPLATE.md
    ├── plan/
    ├── ai-conv-style-discipline/
    ├── codebase-memory-first/
    ├── code-review-and-audit/
    ├── debugging-patterns/
    ├── doubt-driven-development/
    ├── hermes-agent/
    ├── hermes-agent-skill-authoring/
    ├── hermes-base-config-sync/
    ├── hermes-code-output/
    ├── hermes-evolution-rules/
    ├── hermes-fault-troubleshooting/
    ├── hermes-framework-architecture/
    ├── hermes-framework-loader/
    ├── hermes-git-worktree/
    ├── hermes-knowledge-base/
    ├── hermes-oracle-mode/
    ├── hermes-parallel-dispatch/
    ├── hermes-plan-workflow/
    ├── hermes-safety/
    ├── hermes-shipping-verification/
    ├── hermes-tdd-workflow/
    ├── hermes-todo-progress/
    ├── hermes-truth-redline/
    ├── hermes-verification-rules/
    ├── repo-publishing-workflow/
    ├── source-driven-development/
    ├── system-admin/
    └── vdb-retrieval-pipeline/
```

---

## 安装

### 全新安装

```bash
git clone https://github.com/dandanlan8090/hermes-micro-framework.git
cd hermes-micro-framework
bash install.sh
```

脚本自动完成：
1. 复制 SOUL.md / USER.md 到 ~/.hermes/
2. 创建 .env（从 .env.example 复制）
3. 补充 skills/ 到 ~/.hermes/skills/
4. 复制 vdb/ 工具链
5. 创建 Python 虚拟环境 + pip 安装依赖
6. 重建 Chroma 向量索引
7. **vdb 预热 + 索引过期检测**（自动重建，无需手动执行）

完成后：
```bash
nano ~/.hermes/.env            # 编辑 API Key
hermes chat                    # 启动
```

### 已有用户（推荐）

```bash
git clone https://github.com/dandanlan8090/hermes-micro-framework.git
cd hermes-micro-framework
bash install.sh
```

脚本检测到 `~/.hermes/` 已存在，会：
- **跳过** SOUL.md / USER.md（提示手动 diff 合并）
- **补充** skills/ 中不存在的技能
- **覆盖** vdb/ 工具链（安全）
- 跳过 .venv 重建（如需：`bash ~/.hermes/scripts/init-vdb.sh`）

手动合并核心文件的差异：
```bash
diff -u ~/.hermes/SOUL.md  SOUL.md
diff -u ~/.hermes/memories/USER.md memories/USER.md
```

### 强制覆盖（谨慎）

```bash
bash install.sh --force
```

全量覆盖，包括 SOUL.md / USER.md。只有确定是新装机时才用。

---

## 技能说明

| 技能 | 类型 | 说明 |
|------|------|------|
| `plan` | workflow | Plan Mode：行动方案写作规范 |
| `source-driven-development` | methodology | 源码驱动：必须引用官方文档 |
| `hermes-oracle-mode` | workflow | 主脑模式：多 Agent 统筹调度 |
| `hermes-shipping-verification` | workflow | 发布验证：质量门控 + 回滚计划 |
| `hermes-base-config-sync` | workflow | 配置仓库同步、脱敏、结构校验 |
| `hermes-agent` | integration | Hermes 配置与排障 |
| `codebase-memory-first` | workflow | 代码任务前必查知识图谱 |
| `doubt-driven-development` | methodology | 怀疑驱动：对抗性审查非平凡决策 |
| `ai-conv-style-discipline` | methodology | CLI 对话风格规范 |
| `vdb-retrieval-pipeline` | infrastructure | vdb 技能语义检索管道 |
| `hermes-agent-skill-authoring` | methodology | Skill 创建规范与模板检查 |
| `code-review-and-audit` | methodology | 代码审查与审计 |
| `debugging-patterns` | methodology | 交互式调试模式 |
| `hermes-tdd-workflow` | methodology | TDD 测试驱动工作流 |
| `hermes-git-worktree` | tool | Git worktree 分支隔离 |
| `hermes-parallel-dispatch` | workflow | 并行多 Agent 派发 |
| `hermes-fault-troubleshooting` | workflow | 故障处理流程 |
| `hermes-knowledge-base` | methodology | 知识库整理规范 |
| `hermes-todo-progress` | tool | TODO 进度展示 |
| `hermes-plan-workflow` | workflow | Plan + todo 推进工作流 |
| `repo-publishing-workflow` | workflow | 发布工作流 |
| `hermes-verification-rules` | methodology | 验证铁律 |
| `hermes-code-output` | methodology | 代码输出规范 |
| `system-admin` | workfloW | 系统管理任务 |
| `hermes-framework-loader` | methodology | 框架文件加载规则 |
| `hermes-framework-architecture` | infrastructure | 框架架构参考 |
| `hermes-truth-redline` | methodology | 信息真实性红线 |
| `hermes-safety` | methodology | 安全约束规范 |
| `hermes-evolution-rules` | methodology | 自身进化规则 |

---

## 技能检索系统（vdb）

详见 [`skills/vdb-retrieval-pipeline/SKILL.md`](skills/vdb-retrieval-pipeline/SKILL.md)。

### 健康检查

```bash
# 索引过期检测
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from indexer import check_index_stale; s,r=check_index_stale(); print('过期' if s else '最新', r)"

# 完整启动检测
python3 ~/.hermes/scripts/vdb-autoload.py --check   # 只检测
python3 ~/.hermes/scripts/vdb-autoload.py --force   # 检测 + 过期自动重建
```

### 架构

```text
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
