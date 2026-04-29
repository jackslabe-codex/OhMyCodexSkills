---
name: gesp-practice
description: 按考点、错题、年份月份或难度从 GESP 题库抽题，并记录一次练习会话。
user-invocable: true
---

# gesp-practice 技能

## 触发形式

- `/gesp-quiz concepts=<...> count=<n>`
- `/gesp-quiz wrong_only=true`
- `/gesp-quiz paper=YYYY-MM`

## 行为

- 从 `wiki/questions/` 选题
- 生成一次练习会话文件到 `state/attempts/`
- 直接向用户展示题面内容，而不是只返回题号
- 默认不改写题库内容

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py practice --concepts concept-linked-list --count 5
```
