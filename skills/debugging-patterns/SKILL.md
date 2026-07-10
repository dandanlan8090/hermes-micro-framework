---
name: debugging-patterns
description: 'Interactive code debugging patterns — Python (pdb/debugpy) and Node.js
  (inspect/CDP). Class-level guidance for choosing, setting up, and effective breakpoint-driven
  debugging across both ecosystems. 按 Systematic Debugging 四阶段排查错误（根因→模式→假设→实现）。
  禁用：纯运维故障（见 hermes-fault-troubleshooting）、无需调试的代码审查。'
version: 1.0.1
author: Hermes Agent (CURATOR umbrella consolidation)
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
      - 调试
      - debug
      - 错误排查
      - 代码不工作
      - pdb
      - 报错
      - exception
      - traceback
      - 异常
      - 定位问题
      - 代码报错
      - 哪里错了
      - debugpy
      - 断点调试
      disable:
      - 运维故障
      - 服务挂了
      - 配置错误
      - 网络问题
      - 纯文档审查
    skill_type: methodology
    priority: high
    related_skills:
    - hermes-fault-troubleshooting
    - source-driven-development
---
# Debugging Patterns — Class-Level Guidance

## Systematic Debugging 四阶段

### Iron Law
不查根因禁止修。症状修复 = 失败。

### Phase 1: Root Cause
读错 → 复现 → 看最近变更 → 多组件逐层插桩 → 数据流反向追溯

### Phase 2: Pattern Analysis
找 working example，对比差异，读完参考实现再动手

### Phase 3: Hypothesis + Test
单一假设、最小改动、一个变量

### Phase 4: Implementation
先写 failing test / failing 复现脚本 → 修 → 验证回归

### 3 次失败停止
同一问题累计 3 次修复失败 → 停止，问架构，不继续打补丁：
是否架构本身错？是否应该重写模块？是否 YAGNI 被违反？

### 一行复现
```bash
bash -c '原命令' 2>&1 | tee /tmp/repro.log
```
看到原始报错 → 留着不删，作为 disclosed symptom。

---

## Python Debugging (pdb / debugpy)

### Quick Start

```bash
# pdb — drop into script
python -m pdb script.py

# debugpy — attach to running process
python -m debugpy --listen 5678 --wait-for-client script.py
```

### Recommended Workflow

1. Set breakpoint: `breakpoint()` or `import pdb; pdb.set_trace()`
2. Run until breakpoint
3. Inspect: `p variable`, `locals()`, `dir(obj)`
4. Step: `n` (next), `s` (step into), `c` (continue)
5. Evaluate: `!expression`

### Conditional Breakpoints

```python
# In code
breakpoint() if condition else None

# In pdb
b 42, x > 10
```

## Node.js Debugging (inspect / CDP)

### Quick Start

```bash
# Built-in inspector
node --inspect script.js
node --inspect-brk script.js  # pause at start

# Chrome DevTools Protocol
node --inspect=0.0.0.0:9229 script.js
```

### Debugging with CDP

```javascript
// chrome://inspect in browser
// or use v8-inspector directly
const inspector = require('node:inspector');
inspector.open(9229, '0.0.0.0', true);
```

## Choosing the Right Tool

| Situation | Tool |
|-----------|------|
| Quick script, no deps | pdb |
| Complex app, remote debugging | debugpy |
| Node.js backend | inspect / CDP |
| CI/debugging tests | pytest --pdb or --trace |
| Post-mortem | python -m pdb -c c core.dump |
