---
name: wiki-init
description: 初始化空项目中的 LLM wiki 骨架。当项目目录中尚未建立 `raw/`、`wiki/`、索引文件或标签词表时使用；也适用于用户要求初始化、重建知识库骨架。
user-invocable: true
---

# wiki-init 技能

## 核心目标

为一个刚开始的项目建立最小可用的 LLM wiki 骨架。默认假设项目起始时可能只有 skill 相关文件，`raw/`、`wiki/` 以及各类索引文件都还不存在。

## 触发场景

- 用户执行 `/wiki-init`
- 用户要求“初始化 wiki”“建立知识库骨架”“重建 wiki 目录”
- 其他 skill 发现 `raw/`、`wiki/index.md` 或 `wiki/tags.md` 缺失，无法继续工作

## 初始化内容

若以下目录不存在，创建它们：

- `raw/`
- `raw/01-articles/`
- `raw/02-papers/`
- `raw/03-transcripts/`
- `raw/09-archive/`
- `wiki/`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/syntheses/`

若以下文件不存在或为空，初始化它们：

- `wiki/index.md`
- `wiki/log.md`
- `wiki/tags.md`

`wiki/index.md` 初始化为：

```markdown
# Wiki Index

## Sources

## Entities

## Concepts

## Syntheses
```

`wiki/log.md` 初始化为空文件。

`wiki/tags.md` 通过复制 `.agents/skills/wiki-init/references/tags.md` 生成。

## 执行规则

- 只创建缺失目录与文件，不覆盖已有内容
- 若目标文件已存在且非空，保留原文件
- 初始化完成后，向用户报告本次新增了哪些目录和文件
- 不向 `wiki/log.md` 追加初始化日志，除非用户明确要求把初始化动作写入日志

## 关联说明

- `wiki-ingest` 默认依赖本技能产出的目录骨架与 `wiki/tags.md`
- 若后续需要调整默认标签词表，修改 `.agents/skills/wiki-init/references/tags.md`
