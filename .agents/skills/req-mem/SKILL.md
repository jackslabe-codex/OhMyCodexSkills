---
name: req-mem
description: 记录 Codex 对话中的明确需求、实现过程和人类验证结果，供后续 AI 解决问题时检索参考。Use when the user states a concrete requirement to implement or deliver, confirms a completed requirement should be recorded, or provides human verification feedback. Maintains an Obsidian-style lightweight index plus split detailed records under agent-req-mem/.
user-invocable: true
---

# req-mem 技能

## 核心目标

把“需求、实现、验证”沉淀为后续 AI 可检索的项目记忆。记录必须轻量、可导航、可增量维护，避免单文件随着项目推进变得过大。

## 存储位置

默认在当前目标项目根目录维护：

```text
agent-req-mem/
  index.md
  log.md
  requirements/
    YYYY-MM/
      req-YYYYMMDD-HHMMSS-short-slug.md
```

如果用户正在编辑一个独立项目，在该项目根目录创建或更新 `agent-req-mem/`。不要默认把不同项目的需求记录写回 skill 仓库。

## 触发场景

- 用户明确提出一个需要 Codex 执行、修改、创建、修复、部署、分析或交付的需求。
- 用户确认 Codex 已完成某个需求，并要求或允许记录实现方法与过程。
- 用户反馈人工验证结果，例如“我测试通过了”“这里验证失败”“在设备上现象是...”“人工确认没问题”。
- 用户显式要求“记录这个需求”“把实现过程记下来”“把验证结果写入需求记忆”。

## 前置检查

使用本 skill 前先确认目标项目根目录。若 `agent-req-mem/` 不存在，创建最小结构：

```text
agent-req-mem/
  index.md
  log.md
  requirements/
```

`index.md` 初始内容：

```markdown
# Agent Requirement Memory Index

## Open

## Implemented

## Verified

## Rejected
```

`log.md` 允许为空，后续按时间追加。

## 记录命名

新需求记录文件名使用：

```text
req-YYYYMMDD-HHMMSS-short-slug.md
```

规则：

- `YYYYMMDD-HHMMSS` 使用当前本地时间。
- `short-slug` 用 2 到 6 个英文小写词概括需求；无法自然翻译时使用拼音或稳定英文技术词。
- 详情文件放入 `agent-req-mem/requirements/YYYY-MM/`。
- 页面名与文件名去掉 `.md` 后一致，索引用 `[[req-YYYYMMDD-HHMMSS-short-slug]]` 双链引用。

## 详情记录模板

```markdown
---
id: req-YYYYMMDD-HHMMSS-short-slug
type: requirement-record
status: requested
created_at: YYYY-MM-DD HH:mm
updated_at: YYYY-MM-DD HH:mm
tags: []
---

# 需求标题

## Requirement

- **user_request**: 用户明确提出的原始需求摘要。
- **goal**: 要达成的结果。
- **success_criteria**: 可判断完成的条件。
- **constraints**: 已知限制、偏好、环境或不做事项。

## Implementation

尚未记录。仅在人类确认需求完成后填写。

## Human Verification

尚未记录。仅在人类反馈验证情况后填写。

## Links
```

## 记录需求

当用户提出明确需求时：

1. 先读取 `agent-req-mem/index.md`，判断是否已有同一需求记录。
2. 若是新需求，创建详情文件，状态设为 `requested`。
3. 若是已有需求的补充，更新该详情文件的 `Requirement`，不要创建重复记录。
4. 更新 `index.md` 的 `Open` 分区，条目格式：

```markdown
- [[req-YYYYMMDD-HHMMSS-short-slug]] — 一句话需求摘要；status: requested; tags: [tag1, tag2]
```

5. 向 `log.md` 追加：

```markdown
## [YYYY-MM-DD HH:mm] requested | [[req-YYYYMMDD-HHMMSS-short-slug]]
- **summary**: 一句话需求摘要
```

## 记录实现

只有在人类确认 Codex 已完成需求后，才填写 `Implementation`。不要在刚完成代码修改时自行宣称可写实现记录。

记录内容应包含：

- 实现方法：做了什么，不需要逐行描述。
- 关键文件或模块：使用绝对必要的路径，不列无关文件。
- 关键命令或验证：只记录对复现有帮助的命令。
- 重要取舍：为什么这样实现，以及放弃了什么。
- 已知风险或后续事项。

更新后：

- 将详情文件 `status` 更新为 `implemented`。
- 将 `updated_at` 更新为当前时间。
- 把 `index.md` 中对应条目移动或同步到 `Implemented` 分区。
- 向 `log.md` 追加 `implemented` 事件。

## 记录人类验证

当人类反馈验证情况时，追加到 `Human Verification`：

```markdown
### YYYY-MM-DD HH:mm

- **verifier**: human
- **environment**: 人类提到的设备、环境或版本；未知则写“未说明”。
- **steps**: 人类实际做过的验证动作。
- **result**: passed | failed | partial | unknown
- **notes**: 现象、错误信息、截图说明或补充判断。
```

如果验证通过，将状态更新为 `verified`，并同步到 `index.md` 的 `Verified` 分区。如果验证失败或部分通过，保留或更新为 `implemented`，并在索引摘要中标记 `verification: failed` 或 `verification: partial`。

## 索引维护

- `index.md` 只保存短摘要、状态、标签和双链，不写长实现过程。
- 详情记录才保存完整上下文。
- 同一条记录只应出现在最能代表当前状态的主分区；状态变化时避免重复条目。
- 使用 Obsidian 双链格式 `[[record-id]]` 连接相关需求。
- 若发现索引条目与详情状态不一致，以详情文件 frontmatter 为准修正索引。

## 硬约束

- 默认使用简体中文记录，技术名词保留英文。
- 不记录敏感密钥、token、密码、私有证书内容。
- 不把普通聊天、临时想法或未形成执行目标的讨论记为需求。
- 不在没有人类确认的情况下记录 Implementation。
- 不伪造验证结果；只有人类反馈过的验证才写入 Human Verification。
- 不为控制文件体积而删除历史；需要压缩时新增 synthesis 或归档记录，并保留原始记录链接。
