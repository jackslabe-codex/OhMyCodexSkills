---
name: gesp-grade
description: 对一次 GESP 练习会话自动判分，并回写 attempts 与 candidates 状态。
user-invocable: true
---

# gesp-grade 技能

## 输入

- `/gesp-grade <attempt-id>`

## 判分策略

- `single_choice`：严格自动判分
- `true_false`：有标准答案时严格判分，否则标记待人工复核
- `programming`：给出建议判定、置信度和理由，保留人工覆盖入口

## 回写字段

- `question_id`
- `concept_refs`
- `result`
- `score`
- `confidence`
- `judgement_reason`
- `review_status`

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py grade <attempt-id> --answers question-2025-12-01=A
```
