# Tag Registry

用于维护 wiki 的主题标签主词表。`wiki-init` 在第一次初始化时应将此文件复制到 `wiki/tags.md`，后续由 `ingest` 读取和增量维护。

## Canonical Tags

- `llm`
- `agent`
- `training`
- `rag`
- `alignment`

## Aliases

- `large-language-models` -> `llm`
- `agents` -> `agent`
- `retrieval-augmented-generation` -> `rag`

## Rules

- 页面 frontmatter 中的 `tags` 优先复用 canonical tags
- 若当前主题无法用现有 canonical tags 表达，才允许新增一个新标签
- 新标签默认使用英文、小写、短 slug
- 若只是新写法、复数形式或缩写差异，补 alias，不新增 canonical tag
- 单页总标签控制为 1 个基础标签加 1-3 个主题标签
