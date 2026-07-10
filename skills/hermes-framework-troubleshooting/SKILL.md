---
name: hermes-framework-troubleshooting
description: 诊断和修复 Hermes 微内核框架自身故障。当 vdb 不工作/skill 不加载/recall 不准/铁律未执行/系统行为退化时使用。提供症状-根因-修复表、一键诊断脚本和回滚流程。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
metadata:
  hermes:
    tags:
      trigger:
      - vdb不工作
      - skill加载失败
      - skill_view报错
      - 索引过期
      - 召回不准
      - 铁律失效
      - 框架故障
      - 框架行为异常
      - is_healthy false
      - build_index失败
      disable:
      - 普通代码报错
      - 用户业务逻辑错误
      - 外部工具安装失败
      - 模型回答质量问题
    skill_type: workflow
    priority: high
    related_skills:
    - hermes-framework-architecture
    - vdb-retrieval-pipeline
---
# Hermes Framework Troubleshooting

## 第一性原理
框架故障的本质是**某条加载链路中断**：
- vdb 链路：文件 → 索引 → API → 召回
- skill 链路：路由表 → skill_view → SKILL.md 解析
- 铁律链路：SOUL.md → Agent 行为约束

诊断时沿链路逐段排查，找到第一个断裂点。

---

## 症状 → 根因 → 修复速查表

| 症状 | 根因 | 修复动作 |
|------|------|----------|
| vdb 返回空 / is_healthy()==False | chromadb 损坏 / .venv 丢失 / API key 无效 | `~/.hermes/scripts/init-vdb.sh` 重装 |
| vdb 返回旧技能（索引与 filesystem 不符） | 新增/修改 skill 后未 rebuild | `build_index(force=True)` 重建 |
| skill_view 失败 / skill 不存在 | SKILL.md frontmatter 损坏 / 文件被误删 | `ls ~/.hermes/skills/` 检查；`skill_manage(action='create')` 重建 |
| recall top-5 全部无关 | trigger 标签太少或脱离用户查询词汇 | 检查对应 skill 的 trigger，补用户实际用词后 rebuild |
| 铁律在行为中未体现 | SOUL.md 铁律措辞模糊 / agent 忽略 | 检查铁律格式：one-liner + `→ skill_view(...)` |
| system prompt 膨胀（感知变慢） | SOUL/USER/MEMORY 内容过多 | 检查各文件 tokens，非铁律移入 skill |
| 路由表找不到场景 | 路由未覆盖该场景 | 在 SOUL.md §技能路由表 新增一行 |
| 新 skill 在 vdb 中无法召回 | 新增后未 rebuild | `build_index(force=True)` |

---

## 一键诊断脚本

```bash
cd ~/.hermes/vdb && source .venv/bin/activate || { echo ".venv 激活失败"; exit 1; }

# 1. vdb 健康检查
python3 -c "from matcher import is_healthy; from indexer import check_index_stale; \
print(f'healthy={is_healthy()}'); stale,reason=check_index_stale(); print(f'stale={stale} {reason}')"

# 2. 索引统计
python3 -c "import chromadb; from chromadb.config import Settings; \
from indexer import CHROMA_DIR, COLLECTION_NAME; \
c=chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False)); \
print(f'skills={c.get_collection(COLLECTION_NAME).count()}')"

# 3. 测试 recall
python3 -c "from matcher import search; [print(r['skill_name'], r['final_score']) \
for r in search('框架故障')[:5]]"

# 4. 各文件 Token 估算
python3 -c "
import os, pathlib
def tok_est(t): return sum(1 for c in t if '\u4e00'<=c<='\u9fff') + sum(1 for c in t if c.isascii())/4
for f in ['SOUL.md','USER.md','MEMORY.md']:
    p = pathlib.Path(os.path.expanduser(f'~/.hermes{\"/memories/\" if f!=\"SOUL.md\" else \"/\"}{f}'))
    if p.exists(): t=p.read_text(); print(f'{f:10s} {len(t):>5}ch {int(tok_est(t)):>4}tok')
    else: print(f'{f:10s} 不存在')
"
```

---

## 回滚流程

任何修改后出现行为退化，立即回退并调查根因：

```bash
# 核心文件回滚（通过 git）
cd ~/.hermes && git checkout -- SOUL.md memories/USER.md memories/MEMORY.md

# vdb 索引重建（如有必要）
cd ~/.hermes/vdb && source .venv/bin/activate && \
PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"

# 验证回滚后状态
python3 ~/.hermes/scripts/vdb-autoload.py --check
```

---

## 失败模式与处理

| 失败模式 | 典型表现 | 处理方式 |
|----------|---------|---------|
| SiliconFlow API 限流 | 返回 429 / 超时 | 等待 30s 后重试，或切备用模型 |
| .venv 损坏 | pip 报错 / 模块缺失 | 删除 .venv/，重新执行 init-vdb.sh |
| Chroma 锁文件残留 | 无法写入索引 | `rm -rf ~/.hermes/vdb/chroma/.lock` 后重试 |
| 磁盘空间不足 | build_index 中途失败 | 清理 chroma/ 中旧索引 |

---

## 详细架构参考

如上述流程无法解决问题，加载 `hermes-framework-architecture` skill 查看完整系统设计。
