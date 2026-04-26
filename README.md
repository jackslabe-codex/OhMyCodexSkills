# OhMyCodexSkills

这个仓库用于集中管理、测试和迭代我选定的 Codex skills。

当前仓库只跟踪与 skill 相关的文件，其他本地测试产物、编辑器配置和缓存文件默认通过 `.gitignore` 排除。

## 目录结构

```text
.agents/
  skills/
    wiki-ingest/
    wiki-init/
    wiki-lint/
    wiki-query/
```

每个 skill 目录通常包含：

- `SKILL.md`：skill 的主说明和执行约束
- `references/`：可选的参考资料、模板或辅助文档

## 当前收录的 Skills

- `wiki-ingest`
- `wiki-init`
- `wiki-lint`
- `wiki-query`

## 仓库约定

- 仅提交 skill 相关文件
- `references/` 目录中的普通文档允许提交
- 本地缓存、系统垃圾文件和常见开发环境产物不提交

## 使用目标

- 统一管理可复用 skills
- 在真实任务中验证技能提示词和工作流
- 逐步优化 skill 的结构、边界和可维护性
