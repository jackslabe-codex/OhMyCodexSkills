---
name: gesp-outline-ingest
description: 从 GESP 考试大纲 Markdown 提取考点 concept 页面，并更新 catalog blueprint。
user-invocable: true
---

# gesp-outline-ingest 技能

## 输入

- `/gesp-ingest-outline <md-path>`
- `/gesp-ingest-outline`
  不传路径时，默认扫描 `raw/syl/` 下的 Markdown 文件。

## 输出

- `wiki/concepts/concept-*.md`
- `state/catalog/blueprint.yaml`

## 规则

- 每个可复用知识点写成一个 `concept`
- `concept` 支持父子层级；顶层大知识点可拆成若干二级 `concept`
- 默认使用 LLM 直接从大纲 Markdown 生成 concept 树，不再依赖本地硬编码拆分
- frontmatter 必须包含：`exam`、`level`、`module`、`parent_concept`、`prerequisites`、`question_refs`
- `state/catalog/blueprint.yaml` 中的 concept 元数据必须同步写入：`parent_concept`、`children`、`is_leaf`
- 若一级知识点未细分，则它自己仍然是可直接挂题的叶子 `concept`
- 若重复 ingest，应复用已有 concept，而不是创建重复页面
- 默认处理完成后，将原始 Markdown 归档到 `raw/09-archive/syl/`
- 调用前需设置环境变量 `DEEPSEEK_API_KEY`

## 推荐执行方式

```bash
DEEPSEEK_API_KEY=*** /Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .agents/skills/gesp-init/scripts/gesp_tool.py ingest-outline <md-path> --model deepseek-v4-flash
```
