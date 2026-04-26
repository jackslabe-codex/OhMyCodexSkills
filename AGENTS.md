# Global Codex Instructions

## Language

- 默认使用中文回复，除非用户明确要求英文。
- 技术名词可以保留英文，但解释用中文。

## Requirement Memory

- 当用户在对话中明确提出一个需要 Codex 执行或交付的需求时，使用 `req-mem` skill 将需求记录到当前目标项目的 `agent-req-mem/`。
- 当 Codex 完成需求后，只有在人类确认“已完成、确认记录、可以记下实现过程”等明确信号后，才使用 `req-mem` skill 记录实现方法与过程。
- 当人类反馈人工验证情况时，使用 `req-mem` skill 追加验证记录，并同步更新索引状态。
- `AGENTS.md` 只定义触发规则；具体目录结构、命名、索引和记录格式以 `req-mem` skill 为准。
