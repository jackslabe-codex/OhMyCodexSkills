---
name: gesp-paper-ingest
description: 从 GESP 真题 Markdown 提取试卷页、题目页和题目到 concept 的映射。
user-invocable: true
---

# gesp-paper-ingest 技能

## 输入

- `/gesp-ingest-paper <md-path>`
- `/gesp-ingest-paper`
  不传路径时，默认扫描 `raw/pp/` 下的 Markdown 文件。

## 输出

- `wiki/questions/question-<year>-<month>-<no>.md`
- `wiki/exams/exam-<year>-<month>.md`
- `state/catalog/paper_ingest/requests/<paper-id>.json`
- `state/catalog/paper_ingest/results/<paper-id>.json`
- 更新相关 `wiki/concepts/*.md` 的 `question_refs`

## 规则

- GESP 每年 4 次，命名使用月份，不使用 `paper`
- 题型固定为 `single_choice`、`true_false`、`programming`
- 题目页 frontmatter 固定包含：`question_id`、`year`、`month`、`no`、`question_type`、`answer`、`analysis`、`concept_refs`、`difficulty`
- `paper-ingest` 直接调用 DeepSeek API 对题目做结构化知识点识别，并立即回写正式 `concept_refs`
- 同时保留请求与结果工件，便于审计与人工复核
- LLM 分类结果固定输出字段：`question_id`、`concept_refs`、`primary_concept`、`fallback_parent_used`、`confidence`、`reason`
- 题目标注默认优先子级 `concept`，`concept_refs` 不设数量上限
- 若 LLM 输出不合规、置信度不足、或同时命中父子 concept，则写 `classification_status: needs_review`
- 默认处理完成后，将原始 Markdown 归档到 `raw/09-archive/pp/`
- 调用前需设置环境变量 `DEEPSEEK_API_KEY`

## 推荐执行方式

```bash
DEEPSEEK_API_KEY=*** /Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py ingest-paper <md-path> --model deepseek-v4-flash
```

```bash
DEEPSEEK_API_KEY=*** /Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py reingest-archived-papers --model deepseek-v4-flash
```
