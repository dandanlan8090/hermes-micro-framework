# Troubleshooting — Hermes Micro Framework

## vdb 问题

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

### API Key 无效（SiliconFlow 403）
检查 `~/.hermes/.env` 中的 `SILICONFLOW_API_KEY` 是否有效。
注册：https://siliconflow.cn

## skill 问题

### skill_view(name='xxx') 说找不到技能
```bash
ls ~/.hermes/skills/*/SKILL.md    # 检查是否存在
```
如果不存在，`bash install.sh` 补充缺失技能。

### vdb 召回不准确
触发标签太少或脱离用户查询词汇。检查对应 skill 的 trigger 标签，补用户实际用词后 rebuild。

## 框架问题

### SOUL.md 更新后 agent 行为不变
重启 Hermes 会话（`/reset` 或退出重进）。

### system prompt 膨胀
检查 SOUL.md / USER.md / MEMORY.md 各文件 tokens，非铁律内容移入 skill。
