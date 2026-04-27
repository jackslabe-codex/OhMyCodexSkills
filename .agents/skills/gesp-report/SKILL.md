---
name: gesp-report
description: 汇总单考生在各 GESP concept 上的掌握度、正确率和薄弱题目。
user-invocable: true
---

# gesp-report 技能

## 输入

- `/gesp-report`
- `/gesp-report concept=<slug>`
- `/gesp-report weak_only=true`

## 输出维度

- `mastery_level`
- 最近作答次数
- 最近正确率
- 关联薄弱题目
- 建议复习顺序

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py report --weak-only
```
