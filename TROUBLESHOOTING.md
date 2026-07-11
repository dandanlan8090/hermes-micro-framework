# Troubleshooting — Hermes Micro Framework

## vdb 问题

### 何时用哪个命令（快速决策）

| 场景 | 命令 | 行为 |
|------|------|------|
| 日常怀疑索引旧了 | `python3 ~/.hermes/scripts/vdb-autoload.py --check` | 只检测，报告"最新/过期" |
| 刚装/改了技能、要刷新 | `python3 ~/.hermes/scripts/vdb-autoload.py --auto` | 过期才重建，否则跳过（**推荐**） |
| 索引明显错乱、强制刷新 | `python3 ~/.hermes/scripts/vdb-autoload.py --force` | 无视过期，全量重建 |
| 全装/重装整个框架 | `bash ~/.hermes/scripts/init-vdb.sh` 或 `bash install.sh` | 环境 + 依赖 + 代码 + 最后 `--auto` |

> 索引过期的判定：`vdb-autoload.py` 对 `~/.hermes/skills/` 文件列表做哈希，与索引时记录的快照比对。**新增/删除/修改了技能文件后，旧索引即判为过期**——此时必须重建才能让新技能被召回。

### vdb 索引过期

**症状**：新建/修改技能后，用 `matcher.search()` 或实际对话里该技能**搜不到**；或 `--check` 报告"过期"。

**诊断**：
```bash
python3 ~/.hermes/scripts/vdb-autoload.py --check
# 输出示例：
#   [vdb] ⚠ 索引过期：skills 列表已变更（新增 N 个 / 修改 M 个）
#   [vdb] 运行：python3 vdb-autoload.py --auto  自动重建
```

**处理**（选一种）：
```bash
# 方式一：自动检测过期并重建（最常用，过期才动、否则秒过）
python3 ~/.hermes/scripts/vdb-autoload.py --auto

# 方式二：强制全量重建（索引疑似错乱时用）
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"

# 方式三：全框架重装（连 .venv / 依赖 / 代码一起刷新）
bash ~/.hermes/scripts/init-vdb.sh
```

重建后验证：
```bash
python3 ~/.hermes/scripts/vdb-autoload.py --check   # 应返回"索引最新"
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from matcher import search; [print(r['skill_name'], round(r['final_score'],3)) for r in search('你的查询')[:5]]"
```

### API Key 无效（SiliconFlow 403）

**症状**：`build_index` 或 `search` 时报 403 / 401 / `Authentication failed` / `Invalid API key`。

**诊断**：
```bash
# 1. 确认 .env 存在且 key 已填
cat ~/.hermes/.env | grep SILICONFLOW_API_KEY
#   应为：SILICONFLOW_API_KEY=sk-xxxxxxxx（真实 key，非 sk-your-key 占位符）

# 2. 直接验证 key 是否有效（curl 探测）
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $(grep SILICONFLOW_API_KEY ~/.hermes/.env | cut -d= -f2)" \
  https://api.siliconflow.cn/v1/embeddings \
  -d '{"model":"BAAI/bge-m3","input":["test"]}'
#   200 = key 有效；401/403 = key 失效或额度耗尽
```

**处理**：
```bash
# 1. 编辑 .env 填入有效 key（免费注册 https://siliconflow.cn）
nano ~/.hermes/.env

# 2. 重新构建索引（key 变更后必须重建，向量由新 key 对应的端点生成）
python3 ~/.hermes/scripts/vdb-autoload.py --force

# 3. 若持续 403，检查依赖是否完整
cd ~/.hermes/vdb && source .venv/bin/activate
pip install --upgrade chromadb openai python-dotenv
```

> 注意：`.env` 是**本地文件，不入库**。clone 仓库后 `.env.example` 会被复制为 `.env`，但内容是占位符 `sk-your-key`，必须手动替换。

### Chroma 无法启动 / ImportError
```bash
cd ~/.hermes/vdb
source .venv/bin/activate
pip install --upgrade chromadb
```

### 索引为空（search 返回 0 结果）
```bash
cd ~/.hermes/vdb && source .venv/bin/activate
PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"
```

## skill 问题

### skill_view(name='xxx') 说找不到技能
```bash
ls ~/.hermes/skills/*/SKILL.md    # 检查是否存在
```
如果不存在，`bash install.sh` 补充缺失技能。

### vdb 召回不准确
触发标签太少或脱离用户查询词汇。检查对应 skill 的 trigger 标签，补用户实际用词后 rebuild（详见 `autoload-vdb/references/METADATA_GUIDE.md`）。

## 框架问题

### SOUL.md 更新后 agent 行为不变
重启 Hermes 会话（`/reset` 或退出重进）。

### system prompt 膨胀
检查 SOUL.md / USER.md / MEMORY.md 各文件 tokens，非铁律内容移入 skill。
