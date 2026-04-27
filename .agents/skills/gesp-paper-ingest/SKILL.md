---
name: gesp-paper-ingest
description: 从 GESP 真题 PDF 提取试卷页、题目页和题目到 concept 的映射。
user-invocable: true
---

# gesp-paper-ingest 技能

## 输入

- `/gesp-ingest-paper <pdf-path>`
- `/gesp-ingest-paper`
  不传路径时，默认扫描 `raw/pp/` 下的 PDF。

## 输出

- `wiki/questions/question-<year>-<month>-<no>.md`
- `wiki/exams/exam-<year>-<month>.md`
- 更新相关 `wiki/concepts/*.md` 的 `question_refs`

## 规则

- GESP 每年 4 次，命名使用月份，不使用 `paper`
- 题型固定为 `single_choice`、`true_false`、`programming`
- 题目页 frontmatter 固定包含：`question_id`、`year`、`month`、`no`、`question_type`、`answer`、`analysis`、`concept_refs`、`difficulty`
- 无法可靠提取时写 `extraction_status: needs_review`
- 默认处理完成后，将原文件归档到 `raw/09-archive/pp/`

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py ingest-paper <pdf-path>
```
