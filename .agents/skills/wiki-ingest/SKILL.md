---
name: wiki-ingest
description: 将 `raw/` 中的新资料增量编译进 `wiki/`。当用户要求摄入、导入、录入原始资料，或执行 `/ingest`、`/ingest <path>` 时使用。
user-invocable: true
---

# wiki-ingest 技能

## 核心目标

把 `raw/` 中的原始资料增量整合到现有 wiki，而不是每次重新发明一套新结构。`raw/` 是不可修改的 source of truth，`wiki/` 是持续维护的编译产物。

## 前置依赖

本 skill 假设 wiki 已完成基础初始化。若发现以下任一项缺失，先执行 `wiki-init` 技能，再继续 ingest：

- `raw/`
- `raw/09-archive/`
- `wiki/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/tags.md`

## 目录约定

- `raw/01-articles/`：网页剪藏的 Markdown 文章
- `raw/02-papers/`：论文等研究资料（常见为 PDF）
- `raw/03-transcripts/`：转录文稿
- `raw/09-archive/`：已处理资料归档区；不要把它当作待处理队列扫描
- `wiki/sources/`：单个 source 的摘要页
- `wiki/entities/`：实体页
- `wiki/concepts/`：概念页
- `wiki/syntheses/`：综合页
- `wiki/tags.md`：主题标签词表与复用规则
- `wiki/index.md`：全局目录入口
- `wiki/log.md`：按时间追加的操作日志

## 触发场景

- 用户执行 `/ingest`
- 用户执行 `/ingest <path>`
- 用户说“把这份资料摄入知识库”“导入这篇文章”“把这个 source 加进 wiki”“录入这份资料”

## 先决规则

在处理任何 source 前，先做这几件事：

1. 确认目标 source 不在 `raw/09-archive/` 下。
2. 读取 `wiki/index.md`、`wiki/log.md`、`wiki/tags.md`。
3. 若用户未指定路径，扫描 `raw/` 下除 `09-archive/` 外的文件，逐个处理；默认一次处理一个 source，上一份完成后再处理下一份。

## 命名规范

统一使用一套稳定命名，禁止混用：

- source 页面文件名：`source-{source-slug}.md`
- concept 页面文件名：`concept-{concept-slug}.md`
- entity 页面文件名：使用实体的规范名称作为页面名；保留官方大小写，如 `OpenAI.md`、`Andrej Karpathy.md`
- `index.md` 中显示的页面名必须与实际文件页名一致

命名时先查现有 wiki，优先复用已有页面，不要仅因为别名、大小写或中英文差异就创建重复页。

## ingest 流水线

对每个待处理 source，严格按以下顺序执行。

### 1. 读取 source

- `.md` / `.txt`：完整读取文本
- `.pdf`：尝试提取文本
- 若 PDF 无法提取有效文本：仅记录文件元信息和可见上下文，不要伪造摘要
- 不修改 `raw/` 中原文件内容

### 2. 先定位现有知识

在写任何页面前，基于 `wiki/index.md` 和相关现有页面做归并判断：

- 找出可能对应的已有 entity / concept / source 页面
- 若只是已有页面的补充信息，则更新现有页
- 只有在确认不存在合适页面时，才新建页面
- 不是每个名词都值得建页；只有会被反复引用、对主题结构有独立价值的实体或概念才建独立页

### 3. 提炼 source

从 source 中提取：

- 核心主旨：1 到 2 句话
- 关键事实：3 到 7 条，优先保留可复用信息
- 实体：人、公司、产品、工具、组织等
- 概念：方法、理论、框架、术语等
- 与现有 wiki 的关系：支持、补充、更新、冲突

如原文不是中文，用中文写入 wiki；专有名词保留原文或官方写法。

### 3.5 选择 tags

对 source、entity、concept 三类页面，都使用“基础标签 + 主题标签”的结构：

- source 页固定包含 `source`
- entity 页固定包含 `entity`
- concept 页固定包含 `concept`

主题标签按以下顺序决定：

1. 从当前资料中提取候选主题词
2. 先对照 `wiki/tags.md` 的 `Aliases` 做归一化，再与 `Canonical Tags` 比对
3. 若存在语义等价、单复数差异或常见缩写关系，必须复用已有 canonical tag
4. 只有现有 canonical tags 无法表达当前主题时，才允许新增 1 个主题标签
5. 单页总标签控制为“1 个基础标签 + 1-3 个主题标签”

新增主题标签时遵守：

- 默认使用英文、小写、短 slug
- 优先使用更通用、更短、未来可复用的标签
- 不要把文件名、作者名、日期、具体项目名直接做成标签，除非它们已经是稳定标签体系的一部分
- 新增后同步更新 `wiki/tags.md` 的 `Canonical Tags`
- 若发现明显近义的新写法，应补一条 alias，而不是新增重复 canonical tag

近义复用示例：

- 若已有 `llm`，不得新建 `large-language-models`
- 若已有 `agent`，不得新建 `agents`
- 若已有 `rag`，不得新建 `retrieval-augmented-generation`
- 若现有词表中没有 `alignment`，且该资料的核心主题就是 alignment，可以新增 `alignment`

### 4. 写入或更新 source 页

在 `wiki/sources/` 创建或更新 `source-{source-slug}.md`：

```markdown
---
title: "source-{source-slug}"
type: source
tags: [source, llm, training]
sources: [raw/01-articles/example.md]
last_updated: YYYY-MM-DD
---

## Summary

[3-5 句中文摘要；若原文无法可靠提取，只写可确认的元信息]

## Key Facts

- ...

## Links

- [[OpenAI]] — 相关实体
- [[concept-in-context-learning]] — 相关概念
```

要求：

- 保持摘要忠于 source，不要凭空补全
- 若页面已存在，做增量更新，不要覆盖掉已有有效信息
- `tags` 必须先复用 `wiki/tags.md` 中的 canonical tags；只有现有标签不足时才新增
- 主题标签只保留 1-3 个，不要把细碎关键词全部写进 `tags`
- `Links` 至少包含本次 ingest 中最关键的相关页面

### 5. 写入或更新 entity / concept 页

对每个决定保留的实体与概念：

- entity 写入 `wiki/entities/`
- concept 写入 `wiki/concepts/`
- 先读取现有页面，再决定补充还是新建

推荐模板：

```markdown
---
title: "OpenAI"
type: entity
tags: [entity, llm, agent]
sources: [raw/01-articles/example.md]
last_updated: YYYY-MM-DD
---

## Definition

[一句话定义]

## Notes

- ...

## Links

- [[source-example]]
- [[concept-in-context-learning]]
```

```markdown
---
title: "concept-in-context-learning"
type: concept
tags: [concept, llm, prompting]
sources: [raw/01-articles/example.md]
last_updated: YYYY-MM-DD
---

## Definition

[一句话定义]

## Notes

- ...

## Links

- [[source-example]]
- [[OpenAI]]
```

更新时遵守：

- 优先追加新事实、修正过时表述、补足链接
- 不要把 source 摘要整段复制到所有相关页
- `tags` 优先复用 `wiki/tags.md` 的 canonical tags，不因措辞变化创建同义新标签
- 若只是弱相关，宁可仅在 source 页链接，不要滥建页面

### 6. 冲突分级

只有“实质性知识冲突”才暂停并询问用户。以下情况不算冲突，应直接整合：

- 新 source 只是补充细节
- 新 source 提供了更新日期更晚的信息
- 新旧说法角度不同但可并存

以下情况算冲突，必须暂停：

- 新旧页面对同一事实给出互斥结论
- 现有页的核心定义会被新 source 实质性推翻
- 无法判断是别名、版本差异还是事实矛盾

暂停时报告：

- 冲突页面
- 新旧说法各是什么
- 冲突来自哪些 source
- 建议处理方式：并存标注、覆盖旧结论、放弃本次 ingest

### 7. 更新 index 与 log

完成页面写入后，先按需更新 `wiki/tags.md`：

- 若新增了新的 canonical tag，追加到 `## Canonical Tags`
- 若确认某个新表述应映射到旧标签，追加到 `## Aliases`
- 不要无谓重排整个文件；保持 append-friendly

然后更新 `wiki/index.md`：

- 确保新增页面在对应分类下注册
- 每项格式统一为 `- [[页面名]] — 一句话说明`
- 若页面已注册，更新描述即可，不要重复添加

然后向 `wiki/log.md` 追加一条 append-only 日志：

```markdown
## [YYYY-MM-DD] ingest | <source 标题或文件名>

- **source**: `raw/...`
- **changes**: 新增/更新了哪些页面
- **conflicts**: 无 / 已暂停等待用户决策
```

### 8. 归档原文件

只有在以下条件全部满足后，才能归档 source：

- source 页已创建或更新
- 相关 entity / concept 页已完成本轮更新
- `wiki/tags.md` 已完成本轮需要的增量更新
- `wiki/index.md` 已同步
- `wiki/log.md` 已追加
- 当前 source 没有未决冲突

归档时将原文件移动到 `raw/09-archive/`。如需避免重名，优先保留原文件名并按原来源子目录组织。

## 硬约束

- 不扫描 `raw/09-archive/` 作为待处理队列
- 可以读取已有 wiki 页面；archive 区只是不作为新的 ingest 输入
- 所有 wiki 内容默认使用简体中文
- 所有 wiki 页面都应包含可继续导航的 `Links` 区域，避免孤岛
- 若 wiki 尚未初始化，先切到 `wiki-init`，不要在本 skill 内重复执行完整初始化流程
- 标签体系以 `wiki/tags.md` 为主词表，默认先复用、后新增
- 不要依赖模型记忆决定命名或分类；先查现有 wiki
- 不要静默吞掉冲突；发现实质冲突必须暂停说明
