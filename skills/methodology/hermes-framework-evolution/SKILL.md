---
name: hermes-framework-evolution
description: 指导如何向 Hermes 微内核框架中安全新增规则/铁律/方法论技能/路由条目。提供类型判断、五步决策流程和验证方法。当需要扩展或修改框架行为时使用。
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
      - 新增铁律
      - 新增规则
      - 创建约束
      - 新增skill
      - 修改方法
      - 框架演进
      - 怎么加规则
      - 路由表更新
      - 扩展框架
      disable:
      - 用户业务代码变更
      - 项目配置文件修改
      - 外部工具配置
    skill_type: methodology
    priority: high
    related_skills:
    - hermes-agent-skill-authoring
    - hermes-framework-changelog
---
# Hermes Framework Evolution

## 第一性原理
框架演进的核心原则是**归属正确**：
- 每一条新增约束必须放在唯一正确的位置
- 错误归属导致：铁律膨胀、skill 难召回、USER/MEMORY 污染

| 内容类型 | 特征 | 正确存放位置 |
|----------|------|-------------|
| 铁律 | 每轮必须遵守、不依赖场景 | SOUL.md §铁律 |
| 方法论/工作流 | 特定场景使用、有完整步骤 | 独立 skill（skills/） |
| 用户偏好 | 关于用户个人习惯 | USER.md |
| 环境事实 | 系统/设备/工具信息 | MEMORY.md |
| 场景→skill 映射 | 路由入口 | SOUL.md §技能路由表 |

---

## 五步决策流程

### 第一步：判断归属
根据上表判断新增内容属于哪一类。

### 第二步：新增铁律
1. 在 SOUL.md §铁律末尾新增一条
2. 格式：**一句话规则（可执行，不依赖 skill）** + `→ 完整细则：skill_view(name='xxx')`
3. 如果规则有完整细则 → 创建对应 skill（按第三步）
4. 如果只有一句话无需细则 → 不创建 skill，不加路由

### 第三步：新增方法论/工作流 skill
1. 创建 `~/.hermes/skills/<category>/<name>/SKILL.md`
2. 遵守 `hermes-agent-skill-authoring` 规范
3. 在 SOUL.md §技能路由表新增一行
4. 重建 vdb 索引

### 第四步：修改已有规则
1. 优先在现有 skill 上 patch，不新建
2. 如果规则跨多个 skill → 修改路由表或扩 trigger 标签
3. 改完后重建 vdb 索引

### 第五步：验证

```bash
# 重建索引
cd ~/.hermes/vdb && source .venv/bin/activate && \
PYTHONPATH=$PWD python3 -c "from indexer import build_index; build_index(force=True)"

# 测试 recall（top-5 应包含新 skill，score > 0.3 合格）
python3 -c "from matcher import search; [print(r['skill_name'], r['final_score']) \
for r in search('用户实际查询词')[:5]]"
```

---

## 触发规则阈值

| 指标 | 阈值 | 动作 |
|------|------|------|
| 单轮 input token | > 8,000 | 检查 SOUL/USER/MEMORY，移除非铁律到 skill |
| 新 skill recall top-5 分 | < 0.3 | 检查 trigger 标签用词，改为用户实际查询词汇 |
| 铁律执行偏离 | 用户反馈 | 检查铁律格式（必须 one-liner + skill 引用） |
| 频发场景无对应 skill | 同一场景出现 ≥3 次 | 按第三步新建 skill |

---

## 演进记录钩子

每次完成框架变更后，在 `~/.hermes/memories/FRAMEWORK_EVOLUTION.md` 中追加一条记录：

```markdown
## [YYYY-MM-DD] 变更描述
- 类型：新增铁律 / 新增 skill / 修改路由 / 优化 token
- 原因：[触发场景]
- 变更内容：[简述]
- 验证结果：[recall top-5 / token 变化]
- 决策人：@username
```

积累 3 条记录后，触发一次评审，评估是否需要进一步优化框架结构。
