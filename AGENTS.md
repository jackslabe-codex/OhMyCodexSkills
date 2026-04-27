# Global Codex Instructions

## Language

- 默认使用中文回复，除非用户明确要求英文。
- 技术名词可以保留英文，但解释用中文。

## Requirement Memory

- 当 `memory` 组处于激活状态且用户在对话中明确提出一个需要 Codex 执行或交付的需求时，使用 `req-mem` skill 将需求记录到当前目标项目的 `agent-req-mem/`。
- 当 `memory` 组处于激活状态且 Codex 完成需求后，只有在人类确认“已完成、确认记录、可以记下实现过程”等明确信号后，才使用 `req-mem` skill 记录实现方法与过程。
- 当 `memory` 组处于激活状态且人类反馈人工验证情况时，使用 `req-mem` skill 追加验证记录，并同步更新索引状态。
- `AGENTS.md` 只定义触发规则；具体目录结构、命名、索引和记录格式以 `req-mem` skill 为准。

## Skill Group Activation

- 使用本项目 `.agents/skills/` 下的本地 skill 前，先遵守 `.agents/skill-groups/active.json` 中的活动组配置。
- `core` 属于始终启用组，任何会话都允许触发；当前仅包含 `skill-group-switcher`。
- `memory` 为普通可开关组，默认承载 `req-mem`。
- 非激活组中的本地 skill 不应被主动触发；关闭组的 skill 应移到 `.agents/skill-groups/disabled/<group>/`，避免继续出现在 `.agents/skills/` 与 `$` 技能列表中。若用户明确要求使用该组能力，先提示开启对应组，或在用户明确要求下代为开启。
- 本规则控制的是项目级触发策略，不修改 Codex 底层 skill 注册表。
