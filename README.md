# OhMyCodexSkills

这个仓库用于集中管理、测试和迭代我选定的 Codex skills。

当前仓库只跟踪与 skill 相关的文件，其他本地测试产物、编辑器配置和缓存文件默认通过 `.gitignore` 排除。

## 目录结构

```text
.agents/
  skill-groups/
    active.json
    disabled/
  skills/
    wiki-ingest/
    wiki-init/
    wiki-lint/
    wiki-query/
    req-mem/
    skill-group-switcher/
    gesp-init/
    gesp-outline-ingest/
    gesp-paper-ingest/
    gesp-practice/
    gesp-grade/
    gesp-report/
AGENTS.md
```

每个 skill 目录通常包含：

- `SKILL.md`：skill 的主说明和执行约束
- `references/`：可选的参考资料、模板或辅助文档
- `scripts/`：可选的本地实现脚本，供该 skill 复用

## 当前收录的 Skills

- `wiki-ingest`
- `wiki-init`
- `wiki-lint`
- `wiki-query`
- `req-mem`
- `skill-group-switcher`
- `memory(req-mem)`
- `gesp-init`
- `gesp-outline-ingest`
- `gesp-paper-ingest`
- `gesp-practice`
- `gesp-grade`
- `gesp-report`

## 仓库约定

- 仅提交 skill 相关文件
- `references/` 目录中的普通文档允许提交
- `scripts/` 目录中的本地实现文件允许提交
- 本地缓存、系统垃圾文件和常见开发环境产物不提交
- 全局行为约束由 `AGENTS.md` 统一定义

## 使用目标

- 统一管理可复用 skills
- 在真实任务中验证技能提示词和工作流
- 逐步优化 skill 的结构、边界和可维护性
- 为面向特定任务域的 skill 组提供稳定的组织方式，例如 GESP 考试相关技能
- 用项目级活动组配置约束本地 skill 的触发范围，避免无关领域 skill 在同一会话中混用
- 关闭某个 skill 组时，将其目录移出 `.agents/skills/`，使其不再出现在 `$` 技能列表中
- `skill-group-switcher` 在未指定目标组时，应先展示当前可选 groups，方便从默认 `core` 状态下继续开启其他组
- `req-mem` 不再属于 `core`，而是归入可单独关闭的 `memory` 组
