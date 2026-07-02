# Learning Tracking v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the Android Interview learning system to the v2 model where learning cards are the only state source, queues are index views, the task pool only stores not-yet-started learning ideas, and daily/weekly/log files stop duplicating state.

**Architecture:** `04_学习追踪/学习追踪操作手册.md` becomes the execution protocol. Templates and live queue files become thin views that refer back to the manual, while historical daily tasks, weekly plans, and logs remain unchanged as history.

**Tech Stack:** Markdown, YAML front matter, Obsidian wikilinks, shell verification with `rg`, `sed`, and `git diff`.

---

## File Structure

Modify:

- `04_学习追踪/学习追踪操作手册.md`: authoritative v2 protocol.
- `02_动态执行/任务池/任务池.md`: live not-yet-started task pool.
- `99_模板/任务池.md`: task pool template.
- `99_模板/每日任务模板.md`: daily workbench template.
- `99_模板/本周计划模板.md`: weekly direction and capacity template.
- `04_学习追踪/复习队列.md`: review queue index view.
- `04_学习追踪/薄弱点.md`: weak-point index view.
- `04_学习追踪/未完成队列.md`: unfinished index view.
- `99_模板/知识点学习情况记录.md`: learning-card-compatible template.

Create:

- `99_模板/学习日志模板.md`: daily fact log template.

Historical migration rule from user:

- Do not modify `03_知识资产/**`.
- Convert historical `02_动态执行/学习日志/*.md` into v2 fact logs.
- Delete old `02_动态执行/今日任务/*.md` and `02_动态执行/本周计划/*.md` if they are awkward to migrate.
- Preserve current learning cards and queue indexes under `04_学习追踪/**`, but update their structure to v2.

---

### Task 1: Rewrite The Operation Manual As The v2 Protocol

**Files:**
- Modify: `04_学习追踪/学习追踪操作手册.md`

- [ ] **Step 1: Replace the manual with the v2 protocol**

Replace `04_学习追踪/学习追踪操作手册.md` with:

````md
---
type: tracking-manual
title: 学习追踪操作手册
updated: 2026-07-02
rule: 学习卡片是唯一状态源；任务池只放未开始任务；队列只做索引视图
---

# 学习追踪操作手册

## 0. v2 核心原则

```text
学习卡片 = 唯一状态源。
任务池 = 想学但还没开始学习的候选输入。
本周计划 = 方向和容量约束。
今日任务 = 当天工作台。
复习队列 / 薄弱点 / 未完成队列 = 学习卡片索引视图。
学习日志 = 当天事实流水和决策记录。
```

全局规则集中在本手册。其他模板只引用本手册，不重复完整协议。

---

## 1. 文件职责

### 1.1 任务池

只保存“想学但还没开始学习”的任务。

字段：

```md
| 优先级 | 模块 | 想学任务 | 为什么想学 | 预计投入 | 触发条件 | 备注 |
```

不保存状态、产出物、完成标准、未完成原因、重试日。

任务池项被选中并真正开始学习前，必须先创建学习卡片。创建学习卡片并开始推进后，从任务池移除。

### 1.2 本周计划

只保存方向和容量约束：

- 本周方向
- 本周容量
- 本周优先清理
- 本周不做
- 本周候选新学

本周计划不维护每日完成状态、掌握度、复习日期。

### 1.3 今日任务

今日任务是当天工作台，只回答今天对哪些对象做什么动作。

今日任务可以勾选，但日终后只作为当天计划快照，不作为长期状态源。

### 1.4 学习卡片

学习卡片是唯一状态源。

卡片按可复习知识单元创建，不按当天动作创建。

合格卡片必须满足：

1. 未来可以拿来复习。
2. 能列出 3 到 7 个核心回忆问题。
3. 没学完时可以明确说明差哪一步。

### 1.5 队列索引

复习队列只回答：哪张卡、哪天复习、为什么排到这里。

薄弱点只回答：哪张卡薄弱、薄弱表现是什么、优先级为什么。

未完成队列只回答：哪张卡没达完成标准、为什么、下一步怎么推进。

队列不复制卡片状态、易错、间隔、复习次数、连续答对。

### 1.6 学习日志

学习日志只记录事实、卡点、回写动作和明日建议，不作为状态查询来源。

---

## 2. 学习卡片结构

每张学习卡片使用这些字段：

```yaml
type: learning-card
id: 卡片唯一名
主题: 大主题/子主题
创建日期: YYYY-MM-DD
上次复习: YYYY-MM-DD 或 null
下次复习: YYYY-MM-DD
间隔天数: 整数
难度系数: 2.5
复习次数: 0
连续答对: 0
失误次数: 0
易错: false
状态: 学习中 / 未完成 / 待复习 / 需复习 / 已掌握 / 暂缓 / 拆小重试
来源: [[来源笔记]]
```

正文结构：

```md
## 核心章节

- 核心问题 1
- 核心问题 2
- 核心问题 3

## 复习规则

看核心章节 -> 凭记忆回顾 -> 回来源笔记核对 -> 整张卡自评。

## 状态记录

| 日期 | 动作 | 自评 | 间隔天数 | 下次复习 | 状态变化 | 备注 |
|---|---|---|---:|---:|---|---|
```

---

## 3. 状态机

学习卡片状态只允许：

```text
学习中
未完成
待复习
需复习
已掌握
暂缓
拆小重试
```

允许流转：

```text
任务池项转卡 -> 学习中

学习中 -> 待复习
学习中 -> 未完成
学习中 -> 拆小重试
学习中 -> 暂缓

未完成 -> 学习中
未完成 -> 拆小重试
未完成 -> 暂缓

待复习 -> 需复习
待复习 -> 已掌握
待复习 -> 待复习

需复习 -> 待复习
需复习 -> 已掌握
需复习 -> 拆小重试

拆小重试 -> 新建更小卡片，原卡暂缓或关闭
暂缓 -> 学习中
```

规则：

1. 任务池项转卡后，初始状态为 `学习中`。
2. 初学达到完成标准后，状态变为 `待复习`，并进入复习队列。
3. 复习没答出或明显磕绊，状态变为 `需复习`，并进入薄弱点。
4. 当天没达到完成标准，状态变为 `未完成`，并进入未完成队列。
5. 连续未完成或卡片太大，状态变为 `拆小重试`。
6. 连续顺畅后，状态变为 `已掌握`。

---

## 4. 今日任务生成流程

先读本手册，再读取状态源和索引。

读取顺序：

```text
1. 本手册
2. 本周计划
3. 复习队列
4. 未完成队列
5. 薄弱点
6. 任务池
7. 相关学习卡片
```

选择优先级：

```text
1. 到期或逾期复习卡片
2. 未完成卡片
3. 薄弱卡片
4. 本周计划指定方向
5. 任务池未开始任务
```

硬约束：

```text
每天最多 1 个新学习任务。
新学习任务必须先转成学习卡片，再进入今日任务。
不追全部历史欠账，只恢复关键链路。
```

---

## 5. 日终回写流程

必须按固定顺序：

```text
1. 更新学习卡片
2. 更新复习队列 / 薄弱点 / 未完成队列
3. 更新任务池
4. 写学习日志
5. 今日任务只保留当天快照
```

具体规则：

1. 先更新学习卡片的状态、复习字段、状态记录和今日卡点。
2. 再更新索引视图。
3. 再更新任务池，只移除已转卡并开始学习的任务。
4. 最后写学习日志，记录事实、卡点、回写和明日建议。

---

## 6. 常用口令

```text
生成今日任务。
录入学习卡片：来源、卡片 id、主题、核心章节。
开始复习。
复习完成：[[学习卡片/路径/卡片名]] 自评：顺畅 / 磕绊 / 没答出。
标记薄弱：[[学习卡片/路径/卡片名]] 表现：具体讲不清的位置。
标记未完成：[[学习卡片/路径/卡片名]] 原因：具体原因 下一步：拆小 / 明天继续 / 暂缓。
看学习追踪状态。
按学习追踪操作手册处理。
```

---

## 7. 默认日期规则

- 今天日期以系统当前日期为准。
- 新卡默认明天复习。
- 状态只在用户主动发起命令时推进。
- 不后台提醒。

---

## 8. 复习评分口径

```text
顺畅：核心章节基本都能秒答且正确。
磕绊：漏一个点，或有些点想半天。
没答出：整张卡想不起来，或漏一半以上。
```
````

- [ ] **Step 2: Verify the manual has required v2 sections**

Run:

```bash
rg -n "v2 核心原则|文件职责|状态机|今日任务生成流程|日终回写流程" 04_学习追踪/学习追踪操作手册.md
```

Expected: five matching lines.

- [ ] **Step 3: Commit the manual rewrite**

```bash
git add 04_学习追踪/学习追踪操作手册.md
git commit -m "docs: define learning tracking v2 protocol"
```

---

### Task 2: Simplify The Live Task Pool And Its Template

**Files:**
- Modify: `02_动态执行/任务池/任务池.md`
- Modify: `99_模板/任务池.md`

- [ ] **Step 1: Replace the live task pool**

Replace `02_动态执行/任务池/任务池.md` with:

````md
---
type: task-pool
updated: 2026-07-02
rule: 任务池只放想学但还没开始学习的任务；开始学习前必须先转学习卡片
---

# 任务池

> 任务池只回答：有哪些想学但还没开始学习的任务。  
> 一旦任务被选中并真正开始学习，先创建学习卡片，再从这里移除。

## 1. 未开始候选任务

| 优先级 | 模块 | 想学任务 | 为什么想学 | 预计投入 | 触发条件 | 备注 |
|---|---|---|---|---:|---|---|
| P0 | 算法 | 恢复手感题包：217、242、121、704、21、141 | 恢复算法推进感，避免面试前手生 | 80-120m | 本周计划允许开启算法新学时 | 被选中后拆成可复习算法卡片 |
| P2 | 基础八股 | Java 剩余 3 题：`volatile`、线程池、`synchronized` vs `ReentrantLock` | 高频基础表达补齐 | 35-45m | 当天没有 P0 新学任务，且复习负债可控 | 被选中后按知识点拆卡 |
| P2 | 基础八股 | Kotlin 基础 5 题 | Kotlin 高频基础复习补齐 | 40-50m | 当天没有 P0 新学任务，且复习负债可控 | 被选中后按问题组拆卡 |

## 2. 使用规则

```text
1. 本页不保存进行中、已完成、未完成、需复习状态。
2. 今日任务不能直接执行任务池项；必须先创建学习卡片。
3. 创建学习卡片并开始推进后，从本页移除对应任务。
4. 未完成、薄弱、复习都由学习卡片和索引队列处理。
```
````

- [ ] **Step 2: Replace the task pool template**

Replace `99_模板/任务池.md` with:

````md
---
type: task-pool
updated: {{date}}
rule: 任务池只放想学但还没开始学习的任务；开始学习前必须先转学习卡片
---

# 任务池

> 任务池只回答：有哪些想学但还没开始学习的任务。  
> 一旦任务被选中并真正开始学习，先创建学习卡片，再从这里移除。

## 1. 未开始候选任务

| 优先级 | 模块 | 想学任务 | 为什么想学 | 预计投入 | 触发条件 | 备注 |
|---|---|---|---|---:|---|---|
| P0 |  |  |  |  |  |  |

## 2. 使用规则

```text
1. 本页不保存进行中、已完成、未完成、需复习状态。
2. 今日任务不能直接执行任务池项；必须先创建学习卡片。
3. 创建学习卡片并开始推进后，从本页移除对应任务。
4. 未完成、薄弱、复习都由学习卡片和索引队列处理。
```
````

- [ ] **Step 3: Verify forbidden task-pool fields are gone**

Run:

```bash
rg -n "未完成原因|重试日|状态 \\||产出物|进行中 /|已完成|需复习" 02_动态执行/任务池/任务池.md 99_模板/任务池.md
```

Expected: no matches.

- [ ] **Step 4: Commit task pool changes**

```bash
git add 02_动态执行/任务池/任务池.md 99_模板/任务池.md
git commit -m "docs: simplify task pool to unstarted tasks"
```

---

### Task 3: Rewrite The Daily Workbench Template

**Files:**
- Modify: `99_模板/每日任务模板.md`

- [ ] **Step 1: Replace the daily template**

Replace `99_模板/每日任务模板.md` with:

````md
---
type: daily-workbench
date: {{date}}
status: planned
source:
  - [[../../04_学习追踪/学习追踪操作手册]]
  - [[../../04_学习追踪/复习队列]]
  - [[../../04_学习追踪/未完成队列]]
  - [[../../04_学习追踪/薄弱点]]
  - [[../任务池/任务池]]
---

# 今日任务 - {{date}}

> 今日任务是当天工作台。日终后只保留为计划快照，不作为长期状态源。

## 1. 今日生成依据

```text
1. 先读学习追踪操作手册。
2. 再读本周计划、复习队列、未完成队列、薄弱点、任务池。
3. 最后打开今日涉及的学习卡片。
```

## 2. 今日原则

```text
1. 优先处理到期或逾期复习卡片。
2. 其次处理未完成卡片。
3. 再处理薄弱卡片。
4. 每天最多 1 个新学习任务。
5. 新学习任务必须先转成学习卡片。
```

## 3. 今日动作

| 优先级 | 动作 | 对象 | 来源 | 今日目标 | 预计用时 |
|---|---|---|---|---|---:|
| P0 | 复习 / 完成未完成 / 补薄弱 / 新学 | [[../../04_学习追踪/学习卡片/路径/卡片名]] | 复习队列 / 未完成队列 / 薄弱点 / 任务池 |  |  |

## 4. 时间块

| 时间 | 动作 | 对象 |
|---|---|---|
| 00:00 - 00:25 |  |  |
| 00:25 - 00:50 |  |  |
| 00:50 - 01:10 |  |  |

## 5. 完成标准

### 最低完成

- [ ] 

### 标准完成

- [ ] 

### 超额完成

- [ ] 

## 6. 日终回写清单

按固定顺序回写：

```text
1. 更新学习卡片
2. 更新复习队列 / 薄弱点 / 未完成队列
3. 更新任务池
4. 写学习日志
5. 今日任务只保留当天快照
```

| 顺序 | 写入位置 | 回写内容 | 是否完成 |
|---:|---|---|---|
| 1 | 学习卡片 | 状态、复习字段、状态记录、今日卡点 | [ ] |
| 2 | 队列索引 | 复习队列 / 薄弱点 / 未完成队列 | [ ] |
| 3 | 任务池 | 移除已转卡并开始学习的任务 | [ ] |
| 4 | 学习日志 | 今日事实、卡点、回写和明日建议 | [ ] |
````

- [ ] **Step 2: Verify the daily template no longer stores long-term state**

Run:

```bash
rg -n "原掌握度|今日掌握度|next_review|放回任务池|明天继续|状态更新" 99_模板/每日任务模板.md
```

Expected: no matches.

- [ ] **Step 3: Commit the daily template**

```bash
git add 99_模板/每日任务模板.md
git commit -m "docs: make daily template a workbench"
```

---

### Task 4: Rewrite The Weekly Plan Template

**Files:**
- Modify: `99_模板/本周计划模板.md`

- [ ] **Step 1: Replace the weekly plan template**

Replace `99_模板/本周计划模板.md` with:

````md
---
type: weekly-plan
week: {{week}}
start_date: {{start_date}}
end_date: {{end_date}}
status: planning
goal: 8月前 Android 高级面试准备
source:
  - [[../04_学习追踪/学习追踪操作手册]]
---

# 本周计划 - {{week}}

> 本周计划是方向盘和容量闸门，不维护任务完成状态。

## 1. 本周方向

| 优先级 | 方向 | 为什么本周做 | 预期结果 |
|---|---|---|---|
| P0 |  |  |  |

## 2. 本周容量

```text
可学习天数：
每日可用时间：
本周最多新增学习卡片数：
每天最多新学习任务数：1
```

## 3. 本周优先清理

| 类型 | 对象 | 原因 | 处理原则 |
|---|---|---|---|
| 逾期复习 / 未完成 / 薄弱 | [[../04_学习追踪/学习卡片/路径/卡片名]] |  |  |

## 4. 本周不做

- 

## 5. 本周候选新学

> 候选新学来自任务池。真正开始前必须先创建学习卡片。

| 优先级 | 任务池对象 | 开启条件 | 是否允许本周开启 |
|---|---|---|---|
| P0 |  |  | 是 / 否 |

## 6. 周末复盘问题

1. 本周是否超过容量？
2. 本周新增学习卡片是否过多？
3. 哪些卡片应成为下周优先清理对象？
4. 任务池是否需要新增或移除未开始任务？
````

- [ ] **Step 2: Verify weekly template no longer tracks task status**

Run:

```bash
rg -n "每日安排|本周回流区|今日掌握度|状态 \\||未完成任务同步|每天最多安排" 99_模板/本周计划模板.md
```

Expected: no matches.

- [ ] **Step 3: Commit the weekly template**

```bash
git add 99_模板/本周计划模板.md
git commit -m "docs: make weekly plan capacity focused"
```

---

### Task 5: Convert Queue Files To Index Views

**Files:**
- Modify: `04_学习追踪/复习队列.md`
- Modify: `04_学习追踪/薄弱点.md`
- Modify: `04_学习追踪/未完成队列.md`

- [ ] **Step 1: Replace the review queue**

Replace `04_学习追踪/复习队列.md` with:

````md
---
type: review-queue
updated: 2026-07-02
rule: 复习队列只索引学习卡片；卡片状态和复习字段以学习卡片为准
---

# 复习队列

> 本页只回答：哪张卡、哪天复习、为什么排到这里。  
> 状态、间隔、易错、复习次数以学习卡片为准。

## 1. 当前复习索引

| 卡片 | 下次复习 | 触发原因 | 备注 |
|---|---:|---|---|
| [[学习卡片/ANR/ANR_治理骨架v0]] | 2026-07-02 | SRS 到期 | 06-29 首复顺畅 |

## 2. 处理规则

```text
复习前打开卡片确认状态。
复习结果先回写卡片，再更新本索引。
本页不保存状态、间隔、易错、复习次数。
```
````

- [ ] **Step 2: Replace weak points**

Replace `04_学习追踪/薄弱点.md` with:

````md
---
type: weak-points
updated: 2026-07-02
rule: 薄弱点只索引学习卡片；卡片状态以学习卡片为准
---

# 薄弱点

> 本页只回答：哪张卡薄弱、薄弱表现是什么、优先级为什么。  
> 状态和易错字段以学习卡片为准。

## 1. 当前薄弱索引

| 卡片 | 薄弱表现 | 优先级 | 发现日期 | 处理建议 |
|---|---|---|---:|---|
| [[学习卡片/启动优化/启动优化_Perfetto证据链]] | 优化率口径、反射 vs 手写 new 差异不稳 | P1 | 2026-06-27 | 下次复习时重点校准口径 |
| [[学习卡片/ARouter/ARouter_插件加载模式]] | AGP 任务注册、class/jar 处理、ASM 插桩点不稳 | P1 | 2026-06-11 | 下次复习时只校准插件链路 |

## 2. 处理规则

```text
标记薄弱时，先更新学习卡片状态和易错字段，再更新本索引。
薄弱解除时，先确认学习卡片已满足解除条件，再从本索引移除或补充备注。
本页不保存状态、易错、复习字段。
```
````

- [ ] **Step 3: Replace unfinished queue**

Replace `04_学习追踪/未完成队列.md` with:

````md
---
type: unfinished-queue
updated: 2026-07-02
rule: 未完成队列只索引学习卡片；卡片状态以学习卡片为准
---

# 未完成队列

> 本页只回答：哪张卡没达完成标准、为什么、下一步怎么推进。  
> 状态以学习卡片为准。

## 1. 当前未完成索引

| 卡片 | 未完成原因 | 下一步动作 | 重试建议日 | 是否需要拆小 |
|---|---|---|---:|---|
| [[学习卡片/启动优化/启动优化_ARouter_MessageQueue关联口径]] | 未完成启动优化与 ARouter / MessageQueue 的表达收口 | 完成 1 段面试口径 | 2026-06-25 | 否 |
| [[学习卡片/算法/LeetCode_1_88]] | 加时任务未占用主线 | 保留为加时卡片 | 下一次算法加时日 | 否 |
| [[学习卡片/算法/LeetCode_78]] | 仅初次预热，未完整写一遍 | 完整写通一遍后转待复习 | 2026-06-26 | 否 |

## 2. 处理规则

```text
标记未完成时，先更新学习卡片状态，再更新本索引。
重新开始时，先把学习卡片状态转为学习中。
连续未完成或卡片太大时，把学习卡片状态转为拆小重试。
本页不保存状态字段。
```
````

- [ ] **Step 4: Verify queue files do not copy card state-table fields**

Run:

```bash
rg -n "状态 \\||易错 \\||间隔 \\||复习次数|连续答对|失误次数" 04_学习追踪/复习队列.md 04_学习追踪/薄弱点.md 04_学习追踪/未完成队列.md
```

Expected: no matches.

- [ ] **Step 5: Commit queue changes**

```bash
git add 04_学习追踪/复习队列.md 04_学习追踪/薄弱点.md 04_学习追踪/未完成队列.md
git commit -m "docs: convert tracking queues to index views"
```

---

### Task 6: Update The Learning Card Template

**Files:**
- Modify: `99_模板/知识点学习情况记录.md`

- [ ] **Step 1: Replace the old knowledge-record template**

Replace `99_模板/知识点学习情况记录.md` with:

````md
---
type: learning-card
id: {{id}}
主题: {{topic}}
创建日期: {{date}}
上次复习: null
下次复习: {{next_review}}
间隔天数: 1
难度系数: 2.5
复习次数: 0
连续答对: 0
失误次数: 0
易错: false
状态: 学习中
来源: [[{{source}}]]
---

# {{topic}}

> 学习卡片是唯一状态源。答案和细节留在来源笔记中，本卡只保存回忆线索和状态记录。

## 核心章节

- 
- 
- 

## 初学完成标准

- [ ] 能不看答案回答核心章节。
- [ ] 能说出至少一个真实例子或面试表达入口。
- [ ] 能明确当前卡点。

## 复习规则

看核心章节 -> 凭记忆回顾 -> 回来源笔记核对 -> 整张卡自评。

自评口径：

```text
顺畅：核心章节基本都能秒答且正确。
磕绊：漏一个点，或有些点想半天。
没答出：整张卡想不起来，或漏一半以上。
```

## 状态记录

| 日期 | 动作 | 自评 | 间隔天数 | 下次复习 | 状态变化 | 备注 |
|---|---|---|---:|---:|---|---|
````

- [ ] **Step 2: Verify the learning card template**

Run:

```bash
rg -n "状态: 学习中|状态记录|初学完成标准|复习规则" 99_模板/知识点学习情况记录.md
```

Expected: four matching lines.

- [ ] **Step 3: Commit the learning card template**

```bash
git add 99_模板/知识点学习情况记录.md
git commit -m "docs: align learning card template with v2"
```

---

### Task 7: Add A Learning Log Template

**Files:**
- Create: `99_模板/学习日志模板.md`

- [ ] **Step 1: Create the learning log template**

Create `99_模板/学习日志模板.md` with:

````md
---
type: learning-log
date: {{date}}
source: [[../今日任务/{{date}}]]
status: closed
rule: 学习日志只记录事实流水和决策理由，不作为状态源
---

# 学习日志 - {{date}}

> 学习日志记录当天实际发生了什么。当前状态以学习卡片和队列索引为准。

## 1. 今日实际动作

| 动作 | 对象 | 结果 | 耗时 | 产出 |
|---|---|---|---:|---|
| 新学 / 复习 / 补薄弱 / 完成未完成 / 表达收口 | [[../../04_学习追踪/学习卡片/路径/卡片名]] |  |  |  |

## 2. 今日卡点

| 对象 | 卡点 | 判断 | 后续处理 |
|---|---|---|---|
| [[../../04_学习追踪/学习卡片/路径/卡片名]] |  | 未完成 / 需复习 / 拆小重试 / 暂缓 |  |

## 3. 日终回写

| 顺序 | 写入位置 | 变更 | 完成 |
|---:|---|---|---|
| 1 | 学习卡片 | 状态、复习字段、状态记录、今日卡点 | [ ] |
| 2 | 队列索引 | 复习队列 / 薄弱点 / 未完成队列 | [ ] |
| 3 | 任务池 | 移除已转卡并开始学习的任务 | [ ] |
| 4 | 学习日志 | 记录今日事实、卡点、回写和明日建议 | [ ] |

## 4. 明日建议

> 这里只写建议，不直接改状态。

1. 
2. 
3. 
````

- [ ] **Step 2: Verify the new template**

Run:

```bash
rg -n "不作为状态源|今日实际动作|日终回写|明日建议" 99_模板/学习日志模板.md
```

Expected: four matching lines.

- [ ] **Step 3: Commit the learning log template**

```bash
git add 99_模板/学习日志模板.md
git commit -m "docs: add learning log template"
```

---

### Task 8: Final Consistency Verification

**Files:**
- Verify all files changed in Tasks 1 through 7.

- [ ] **Step 1: Verify the operation manual is the only full protocol**

Run:

```bash
rg -n "状态机|今日任务生成流程|日终回写流程" 04_学习追踪/学习追踪操作手册.md 99_模板 02_动态执行/任务池/任务池.md 04_学习追踪/复习队列.md 04_学习追踪/薄弱点.md 04_学习追踪/未完成队列.md
```

Expected:

- `04_学习追踪/学习追踪操作手册.md` contains `状态机`, `今日任务生成流程`, and `日终回写流程`.
- `99_模板/每日任务模板.md` may contain `日终回写清单`.
- Other files do not duplicate the full protocol sections.

- [ ] **Step 2: Verify task pool and queues do not contain forbidden state-table fields**

Run:

```bash
rg -n "原掌握度|今日掌握度|重试日 \\||状态 \\||易错 \\||复习次数|连续答对|失误次数" 02_动态执行/任务池/任务池.md 99_模板/任务池.md 04_学习追踪/复习队列.md 04_学习追踪/薄弱点.md 04_学习追踪/未完成队列.md 99_模板/每日任务模板.md 99_模板/本周计划模板.md
```

Expected: no matches.

- [ ] **Step 3: Verify all required files are tracked**

Run:

```bash
git status --short
```

Expected: clean working tree after the task commits.

- [ ] **Step 4: Record final implementation summary**

Run:

```bash
git log --oneline -8
```

Expected: shows commits for the v2 protocol, task pool, daily template, weekly template, queue indexes, learning card template, learning log template, and the implementation plan.

---

### Task 9: Migrate Or Remove Historical Dynamic Execution Files

**Files:**
- Modify: `02_动态执行/学习日志/2026-06-11.md`
- Modify: `02_动态执行/学习日志/2026-06-15.md`
- Delete: `02_动态执行/今日任务/*.md`
- Delete: `02_动态执行/本周计划/*.md`
- Verify untouched: `03_知识资产/**`

- [ ] **Step 1: Convert historical learning logs to v2 fact-log shape**

Rewrite each historical learning log with:

```text
type: learning-log
date: 原日期
status: closed
rule: 学习日志只记录事实流水和决策理由，不作为状态源
```

Keep factual learning outcomes, card points, and writeback notes. Do not keep old state-source tables.

- [ ] **Step 2: Delete old daily workbench snapshots and weekly plan snapshots**

Remove old files under:

```text
02_动态执行/今日任务/
02_动态执行/本周计划/
```

These old files predate v2 and are not reliable state sources.

- [ ] **Step 3: Verify no core knowledge assets changed**

Run:

```bash
git diff --name-only -- 03_知识资产
```

Expected: no output.

- [ ] **Step 4: Verify historical dynamic execution has no old state-source terms**

Run:

```bash
rg -n "掌握度|放回任务池|本周回流区|今日状态更新|未完成回流区" 02_动态执行 99_模板 04_学习追踪
```

Expected: no matches except intentional historical wording inside design/plan docs if the command is broadened to `docs`.

- [ ] **Step 5: Commit historical migration**

```bash
git add 02_动态执行 docs/superpowers/plans/2026-07-02-learning-tracking-v2.md
git commit -m "docs: migrate dynamic execution history to v2"
```
