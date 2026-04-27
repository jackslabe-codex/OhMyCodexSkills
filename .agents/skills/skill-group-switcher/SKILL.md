---
name: skill-group-switcher
description: 按组控制当前项目本地 skills 的启用状态。当用户要求“启用 wiki 组”“关闭 gesp 组”“关闭 memory 组”“只保留 wiki”“当前有哪些组开启”，或使用 `/skills status`、`/skills on <group>`、`/skills off <group>`、`/skills set <group1,group2,...>` 时使用。若用户只是启动该技能但未指定 group，先列出当前可选 groups 与状态供其选择。该技能维护项目规则层的活动组配置，并通过移动目录让关闭组从 `.agents/skills/` 与 `$` 技能列表中隐藏，不修改 Codex 底层 skill 注册表。
user-invocable: true
---

# skill-group-switcher 技能

## 核心目标

维护当前项目 `.agents/skills/` 的活动 group 配置，让后续会话只在被激活的本地 skill 组内工作；关闭的组会被移到停用目录，从 `$` 技能列表中隐藏。

## 触发场景

- 用户输入 `/skills status`
- 用户输入 `/skills on wiki`、`/skills off gesp`、`/skills off memory`、`/skills set wiki,gesp`
- 用户用自然语言要求“启用 wiki 组”“关闭 gesp 组”“关闭 memory 组”“只保留 wiki”“查看当前启用的 skill 组”
- 用户只输入 `$skill-group-switcher` 或“打开 skill 开关”，但还没说要操作哪个 group
- 用户明确要求检查某个本地 skill 当前是否因 group 未启用而不可触发

## 持久化状态

活动组配置固定保存在：

`/.agents/skill-groups/active.json`

关闭组的 skill 会移动到：

`/.agents/skill-groups/disabled/<group>/`

规则：

- `core` 属于始终启用组，不能被关闭；仅保留 `skill-group-switcher` 自身
- `memory` 组默认承载 `req-mem`，可按需开启或关闭
- 新会话默认仅激活 `core`
- 分组按目录命名规则推断，不维护手工的完整 skill 列表

## 执行步骤

1. 读取 `.agents/skill-groups/active.json`
2. 扫描 `.agents/skills/*/SKILL.md` 与 `/.agents/skill-groups/disabled/<group>/*/SKILL.md`
3. 运行本地脚本：

```bash
python3 .agents/skills/skill-group-switcher/scripts/manage_skill_groups.py status
python3 .agents/skills/skill-group-switcher/scripts/manage_skill_groups.py on wiki
python3 .agents/skills/skill-group-switcher/scripts/manage_skill_groups.py off gesp
python3 .agents/skills/skill-group-switcher/scripts/manage_skill_groups.py set wiki,gesp
```

4. 向用户返回：

- 当前可选 groups
- 当前激活组
- 始终启用组
- 本次变更影响到的 skill 列表
- 未分组 skill 或未知 group 的报错与提醒

## 默认交互

如果用户启动本 skill 时没有明确给出要操作的 group 或命令：

1. 先运行 `status`
2. 列出：
   - 可选 groups
   - 当前激活组
   - 每个 group 里有哪些 skill，哪些当前可见、哪些已隐藏
3. 再让用户从可开关 groups 中直接选择

## 解释边界

- 这是项目规则层开关，不是运行时卸载 skill
- 配置关闭的本地 skill 组，会被移出 `.agents/skills/`，因此不会出现在 `$` 技能列表中
- 如果用户要求使用未激活组中的 skill，应先提示开启对应组，或在用户明确要求下代为开启

## 强制约束

- 不要在 `SKILL.md` 内重复实现分组逻辑，统一调用脚本
- 不要允许关闭 `always_on_groups`
- 发现未分组的本地 skill 时必须明确告知，不能静默忽略
