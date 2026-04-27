---
name: gesp-outline-ingest
description: 从 GESP 考试大纲 PDF 提取考点 concept 页面，并更新 catalog blueprint。
user-invocable: true
---

# gesp-outline-ingest 技能

## 输入

- `/gesp-ingest-outline <pdf-path>`
- `/gesp-ingest-outline`
  不传路径时，默认扫描 `raw/syl/` 下的 PDF。

## 输出

- `wiki/concepts/concept-*.md`
- `state/catalog/blueprint.yaml`

## 规则

- 每个可复用知识点写成一个 `concept`
- frontmatter 必须包含：`exam`、`level`、`module`、`prerequisites`、`question_refs`
- 若重复 ingest，应复用已有 concept，而不是创建重复页面
- 默认处理完成后，将原文件归档到 `raw/09-archive/syl/`

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py ingest-outline <pdf-path>
```
