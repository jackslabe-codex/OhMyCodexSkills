---
name: gesp-init
description: 在现有 wiki 体系之上初始化 GESP 考试专用骨架、索引和状态文件。
user-invocable: true
---

# gesp-init 技能

## 核心目标

补齐 GESP 考试知识库的目录、索引和状态文件，作为后续大纲摄入、真题摄入、练习、判分和报告的统一基线。

## 目录约定

- `raw/syl/`：考试大纲（`syllabus` 简写）
- `raw/pp/`：考试真题（`past papers` 简写）
- `raw/09-archive/`
- `wiki/questions/`
- `wiki/exams/`
- `wiki/concepts/`
- `wiki/syntheses/`
- `state/candidates/`
- `state/attempts/`
- `state/catalog/`

## 初始化产物

- `wiki/index.md`：包含 `Concepts`、`Syntheses`、`Questions`、`Exams`
- `wiki/log.md`
- `state/candidates/default.yaml`
- `state/catalog/blueprint.yaml`

## 推荐执行方式

```bash
/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py init
```

## 强制约束

- 不覆盖已有非空 wiki 页面
- 默认 ingest 从 `raw/syl/` 或 `raw/pp/` 扫描 Markdown 文件
- 处理完成后将原始 Markdown 归档到 `raw/09-archive/`
- 默认只创建单考生状态文件 `state/candidates/default.yaml`
