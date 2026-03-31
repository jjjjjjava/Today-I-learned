---
name: learning-behavior-system
description: 面向 Android 工程师的长期学习行为管理系统。当用户询问"今天该干嘛"、"今日任务"、"学习计划"、"复习安排"、"今天学什么"或任何关于学习进度、复习提醒、知识点管理、项目管理的问题时触发。这是一个学习行为状态机，管理记忆强度、遗忘风险、核心知识偏置和认知负债，支持知识点和项目两种类型的学习内容。
---

# Learning Operating System v2.0

面向 Android 工程师的一年期学习行为管理系统（支持知识点 + 项目）。

## 目录

- [系统本质](#系统本质)
- [设计哲学](#设计哲学)
- [与 project-interview-prep 的联动](#与-project-interview-prep-的联动)
- [目录结构](#目录结构)
- [状态文件规范](#状态文件规范)
  - [文件命名](#文件命名)
  - [YAML 字段定义](#yaml-字段定义)
- [Level 定义](#level-定义)
  - [Level 3 的判断标准](#level-3-的判断标准)
  - [Level 4 的判断标准](#level-4-的判断标准)
- [复习周期规则](#复习周期规则)
- [状态转移规则](#状态转移规则)
  - [状态流转图](#状态流转图)
  - [自动状态转移](#自动状态转移)
- [每日任务生成](#每日任务生成)
  - [触发条件](#触发条件)
  - [执行流程](#执行流程)
  - [学习债务提醒机制](#学习债务提醒机制)
- [用户操作协议](#用户操作协议)
  - [1. 新增知识点](#1-新增知识点)
  - [2. 提升 Level](#2-提升-level)
  - [3. 完成复习](#3-完成复习)
  - [4. 批量更新](#4-批量更新)
- [AI 检验机制](#ai-检验机制)
  - [何时检验](#何时检验)
  - [如何检验](#如何检验)
  - [用户权力](#用户权力)
- [用户权力规则](#用户权力规则)
- [meta.md 的作用](#metamd-的作用)
- [长期稳定性原则](#长期稳定性原则)
- [子知识点追踪规则](#子知识点追踪规则)
- [跨卡知识图谱规则（v1.1 新增）](#跨卡知识图谱规则v11-新增)
- [状态签到规则（v1.1 新增）](#状态签到规则v11-新增)
- [新模块学习工作流（v1.1 新增）](#新模块学习工作流v11-新增)
- [注意事项](#注意事项)
- [快速参考](#快速参考)

---

## 系统本质

这不是一个知识管理系统，而是一个**学习行为状态机**。它管理的是：
- 记忆强度的衰减
- 遗忘风险的预警
- 认知负债的累积
- 核心知识的偏置权重

## 设计哲学

1. **管理学习行为，而非仅管理知识**
2. **状态与内容分离** - 状态文件独立于学习笔记
3. **动态复习调度** - 基于学习状态和考核表现调整复习周期
4. **量化掌握等级** - 可验证的行为标准
5. **核心知识优先** - 面试导向的优先级
6. **学习债务提醒** - 可视化遗忘风险
7. **用户拥有最终决策权** - AI 提供建议，用户决定
8. **AI 具备检验与追问能力** - 防止等级虚高
9. **模型与 Agent 可替换** - 无状态 AI，所有状态在文件中
10. **支持知识点和项目** - 统一管理，差异化处理

---

## 与 project-interview-prep 的联动

### 联动机制

learning-behavior-system 作为总调度系统，管理所有学习内容（知识点 + 项目）的复习周期。project-interview-prep 作为项目学习的执行系统，管理项目的学习进度。

### 工作流

```
用户：今天该干嘛？
learning-behavior-system：建议学习"视频加水印项目"（level 2, 需复习）

用户：开始学习视频加水印项目
→ 触发 project-interview-prep skill
project-interview-prep：读取状态 → 发现 level 2 → 继续第3轮学习

用户：完成第3轮学习
project-interview-prep：更新 learning-behavior-system（level 2→3, last_study）
```

### 状态同步规则

1. **learning-behavior-system 管理**：
   - 复习周期（next_review, review_stage）
   - 优先级排序（core, importance）
   - 状态转移（pool/active/review/mastered）

2. **project-interview-prep 管理**：
   - 学习进度（current_round: 0-4）
   - 学习笔记（round-N-XXX.md）
   - 面试问答库

3. **同步时机**：
   - 完成项目轮次时，project-interview-prep 更新 learning-behavior-system 的 level 和 last_study
   - 项目复习时，learning-behavior-system 调用 project-interview-prep 执行模拟面试

---

## 目录结构

```
learning-behavior-system/
├── SKILL.md              # 本文件（AI 的操作手册）
├── interval-rules.md         # 动态间隔/毕业/退步规则（v1.1 新增）
├── sub-points-rules.md       # 子知识点追踪规则（v1.1 新增）
├── states/               # 状态管理（AI 读写）
│   ├── pool/            # 待规划知识点/项目
│   ├── active/          # 正在提升等级的知识点/项目
│   ├── review/          # 进入复习周期的知识点/项目
│   └── mastered/        # 稳定掌握
├── notes/               # 学习笔记
│   ├── 001-Android生命周期/  # 知识点笔记（用户自由管理）
│   └── 003-视频加水印项目/    # 项目笔记（project-interview-prep 管理）
│       ├── state.yaml        # 项目学习状态
│       ├── architecture.md   # 技术架构分析
│       ├── round-1-了解.md
│       ├── round-2-初步学会.md
│       ├── round-3-深入掌握.md
│       ├── round-4-可以面试.md
│       └── code-snippets/    # 核心代码片段
└── meta.md              # 学习方法反思与系统调整记录
```

---

## 状态文件规范

### 文件命名

格式：`序号-标题.yaml`

例如：
- `001-Android生命周期.yaml`
- `002-Kotlin协程原理.yaml`
- `005-Android-GSON学习.yaml`

规则：
- 序号全局唯一，永远递增（扫描所有状态目录，找最大序号+1）
- 用户可以修改文件名（包括标题部分）便于记忆
- 序号是唯一标识，不可重复使用

### YAML 字段定义

**知识点类型**：
```yaml
id: 001                           # 序号（与文件名一致）
title: Android生命周期             # 知识点标题
category: android                 # 分类：android | architecture | interview | flutter | harmonyos
core: true                        # 是否核心知识点
level: 3                          # 掌握等级：0-4
review_stage: 2                   # 复习阶段：0-5
status: active                    # 状态：pool | active | archived | review | mastered
last_study: 2026-02-18           # 上次学习日期
next_review: 2026-03-04          # 下次复习日期
importance: 5                     # 重要性：1-5
created: 2026-01-15              # 创建日期
stability_score: 62               # 记忆稳定度：0-100
consecutive_success: 1            # 连续通过次数
consecutive_failures: 0           # 连续不稳定/失败次数
last_assessment:
  date: 2026-02-18
  result: pass                    # fail | weak | pass | good | excellent
  score: 3                        # 1-5，便于快速记录
  mode: recall                    # recall | qa | mock_interview | skip_check
  weak_points:
    - 配置变更时的生命周期回调顺序
  suggested_interval_days: 7      # 本次计算得到的建议间隔
sub_points:                          # 子知识点列表（可选，最多8个）
  - id: sp1                          # 短 ID（sp1-sp8）
    desc: "子知识点描述"               # 一句话描述
    status: weak                     # weak | ok | good（跨会话累计）
    last_reviewed: 2026-03-27        # 上次复习此子知识点的日期
review_sessions:                     # 复习会话日志（append-only）
  - date: 2026-03-27
    covered_sub_points: [sp1, sp2]   # 本次覆盖的子知识点
    result: ok                       # 本次整体结果
    score: 3                         # 1-5 评分
```

`archived` 状态：卡片达到毕业条件后自动设置。文件保留在 `states/active/` 目录，不再出现在每日复习队列。详见 interval-rules.md。

**项目类型**（新增）：
```yaml
id: 003                           # 序号（与文件名一致）
title: 视频加水印项目              # 项目标题
category: project                 # 分类：project（标记为项目类型）
core: true                        # 是否核心项目
level: 2                          # 掌握等级：0-4（对应学习轮次）
review_stage: 1                   # 复习阶段：0-5
status: active                    # 状态：pool | active | archived | review | mastered
last_study: 2026-03-02           # 上次学习日期
next_review: 2026-03-05          # 下次复习日期
importance: 5                     # 重要性：1-5
created: 2026-02-20              # 创建日期
project_path: D:\Projects\video-watermark  # 项目代码路径（项目特有）
stability_score: 55               # 记忆稳定度：0-100
consecutive_success: 0            # 连续通过次数
consecutive_failures: 0           # 连续不稳定/失败次数
last_assessment:
  date: 2026-03-02
  result: weak                    # fail | weak | pass | good | excellent
  score: 2                        # 1-5，便于快速记录
  mode: mock_interview            # recall | qa | mock_interview | skip_check
  weak_points:
    - 编码链路中的性能瓶颈解释不清
  suggested_interval_days: 3      # 本次计算得到的建议间隔
```

补充说明：
- `review_stage` 仍保留，表示当前复习阶段
- `next_review` 不再仅由 `review_stage` 决定，而是 AI 根据 `last_assessment`、`stability_score`、连续表现动态计算
- `last_assessment` 是关键证据，不能省略

---

## Level 定义

### 知识点 Level 定义

强制统一标准：

```
0 = 未接触
1 = 熟悉（看过）
2 = 理解概念
3 = 能完整讲清楚
4 = 面试可稳定回答
```

### 项目 Level 定义

对应 project-interview-prep 的学习轮次：

```
0 = 未接触
1 = 了解（完成第1轮）
2 = 初步学会（完成第2轮）
3 = 深入掌握（完成第3轮）
4 = 可以面试（完成第4轮）
```

### Level 3 的判断标准

- 能说出核心概念
- 能解释关键细节
- 能回答 2-3 个追问
- 逻辑连贯，没有明显错误

### Level 4 的判断标准

- 满足 Level 3 的所有要求
- 能举例说明
- 能对比相关概念
- 能回答刁钻问题
- 表达清晰，有条理

---

## 复习周期规则

### 动态间隔规则（v1.1 新增）

从 v1.1 开始，`next_review` 主要由 `consecutive_success` 驱动的动态间隔查表决定，不再仅依赖 `review_stage` 基准值。

完整规则详见：[interval-rules.md](interval-rules.md)

核心变化：
- `result: good` → 查表取间隔，间隔按 consecutive_success 递增
- `result: ok` → 查表取间隔，但不超过上次间隔的 1.3 倍
- `result: fail` → 强制 1 天间隔
- 毕业条件：consecutive_success >= 8 AND 间隔 >= 30 天 → status 变为 archived
- 退步条件：consecutive_failures >= 3 → next_review 重置为明天

原有 `review_stage` 基准值仍保留作为参考，但以动态间隔查表为准。

采用”基准间隔 + 动态修正”机制，而不是固定天数。

### 基准间隔

`review_stage` 仍然代表大致复习阶段，但只提供基准值：

```
review_stage 0 → 基准 1天
review_stage 1 → 基准 3天
review_stage 2 → 基准 7天
review_stage 3 → 基准 14天
review_stage 4 → 基准 30天
```

### 动态修正输入

`next_review` 必须综合以下因素计算：

1. **当前 level**
   - level 0-1：说明只是接触或初识，间隔不要拉长
   - level 2：可以进入短周期复习
   - level 3：允许按正常基准推进
   - level 4：根据考核稳定性决定能否放大间隔

2. **本次考核结果**
   - 由 AI 通过口述、追问、对比题、细节题判断
   - 统一映射为：
     - `fail` = 回答错误明显、无法回忆
     - `weak` = 能答部分，但不稳定、需要提示
     - `pass` = 基本答对，有少量遗漏
     - `good` = 回答完整，追问也较稳
     - `excellent` = 回答完整、准确、能迁移和对比

3. **连续表现**
   - `consecutive_success`：连续 `pass/good/excellent` 次数
   - `consecutive_failures`：连续 `fail/weak` 次数
   - 连续通过越多，才允许逐步拉长
   - 连续失败时，应缩短间隔，必要时回退阶段

4. **稳定度**
   - `stability_score`：0-100，表示当前记忆稳定程度
   - 初始建议 50
   - 回答好则上升，回答差则下降
   - 它不是绝对科学值，而是系统内部的“长期表现摘要”

5. **内容权重**
   - `core=true`：同等表现下更保守，不轻易放太长
   - `importance` 高：同等表现下优先安排，不延后太久
   - `category=project`：项目复习要看是否能讲清架构、流程、取舍，不只看概念记忆

### 计算规则

先取 `review_stage` 对应基准天数，再乘以动态系数：

```
fail      -> 0.5x
weak      -> 0.8x
pass      -> 1.0x
good      -> 1.3x
excellent -> 1.6x
```

再叠加稳定度与连续表现修正：

- `consecutive_success >= 3`：额外 `+0.2x`
- `consecutive_failures >= 2`：额外 `-0.2x`
- `stability_score >= 80`：额外 `+0.2x`
- `stability_score <= 40`：额外 `-0.2x`
- `core=true` 且 `review_stage < 4`：额外 `-0.1x`

最后做边界约束：

- 最小间隔 1 天
- 普通知识点最大间隔 45 天
- 核心知识点在进入 `mastered` 前最大间隔 30 天
- 如果本次结果为 `fail`，允许 `next_review=今天` 或 `明天`

### 状态调整规则

- 每次复习后，不再无条件 `review_stage + 1`
- 改为：
  - `excellent/good`：`review_stage +1`（上限 4）
  - `pass`：`review_stage` 保持不变，或在连续通过 2 次后 `+1`
  - `weak`：`review_stage` 保持不变
  - `fail`：`review_stage -1`（下限 0），必要时降回 `active`

- 当 `level=4` 且满足以下条件时才进入 `mastered`：
  - `review_stage>=4`
  - `consecutive_success>=3`
  - `stability_score>=85`

### AI 执行要求

- 每次复习或升级后，AI 必须先给出考核结论，再更新 `next_review`
- AI 必须在输出中解释：
  - 本次考核结果是什么
  - 为什么这样判断
  - `next_review` 是如何算出来的
- 如果用户要求跳过检验，AI 仍可更新，但必须标记为 `pass` 以下的保守结果，默认按 `weak` 处理

---

## 状态转移规则

### 状态流转图

```
pool (level=0) 
  ↓ 用户开始学习
active (level 1-3, 正在提升)
  ↓ 达到 level=4
review (level=4, review_stage 0-3)
  ↓ review_stage >= 4
mastered (稳定掌握)
```

### 自动状态转移

**1. active → review**
- 触发条件：level 提升到 4
- 操作：移动文件从 states/active/ 到 states/review/
- 初始化：
  - `review_stage=0`
  - `stability_score` 默认 50
  - `consecutive_success=0`
  - `consecutive_failures=0`
  - 完成一次 level 4 检验后，再根据结果计算 `next_review`

**2. review → mastered**
- 触发条件：level=4 且 review_stage>=4
- 操作：移动文件从 states/review/ 到 states/mastered/

**3. pool → active**
- 触发条件：用户开始学习某个 pool 中的知识点
- 操作：移动文件从 states/pool/ 到 states/active/

---

## 每日任务生成

核心调度逻辑。

### 触发条件

当用户询问以下任何问题时触发：
- "今天该干嘛？"
- "今日任务"
- "学习计划"
- "复习安排"
- "今天学什么"
- 或任何关于学习进度、复习提醒的语义相关问题

### 执行流程

**Step 1：扫描所有状态文件**

读取 states/ 下所有子目录（pool/active/review/mastered）中的 yaml 文件，提取：
- level
- next_review
- last_study
- core
- importance
- status

**Step 2：计算优先级**

排序规则（按优先级从高到低）：
1. 已到期复习（next_review <= 今天）
2. overdue 天数多的优先（今天 - next_review）
3. 核心知识点优先（core=true）
4. importance 高优先
5. active 状态优先于 pool

**Step 3：任务数量限制**
- 最多 3 个任务
- 建议时间总计不超过 2 小时

**Step 4：输出格式**

必须包含以下内容：

```
📊 今日学习债务：X个知识点超期
⚠️ 最久未复习：XXX（overdue N天，核心知识点）

📋 今日建议任务（3个）：

1. [复习] Android 生命周期
   - 上次学习：2026-02-18
   - 当前状态：Level 3, Review Stage 2
   - Overdue：12天
   - 今日目标：完成第3次复习，进入14天周期
   - 验证方式：口述完整生命周期流程3分钟

2. [提升] Kotlin 协程原理
   - 上次学习：2026-02-28
   - 当前状态：Level 2, Active
   - 今日目标：从理解概念 → 能完整讲清楚
   - 验证方式：解释挂起函数的底层实现

3. [新学习] Jetpack Compose 状态管理
   - 状态：Pool, Level 0
   - 今日目标：熟悉基本概念
```

### 学习债务提醒机制

定义：
> overdue 超过 7 天的知识点视为学习债务

每日输出必须包含：
- 当前债务数量
- 最久未复习的知识点
- 核心知识点是否超过 7 天未触碰
---

## 用户操作协议

### 1. 新增知识点

**用户输入**：
```
新增知识点：Jetpack Compose 状态管理
```

**AI 执行流程**：

1. 扫描 states/ 下所有 yaml 文件，找到最大序号（例如 004）
2. 新序号 = 005
3. 智能推断 category、importance、core：
   ```
   我推断这是一个 android 类的知识点，重要性 4，核心知识。
   是否确认？或者你可以修改。
   ```
4. 用户确认或修改：
   ```
   确认
   或
   改成 architecture, 5, true
   ```
5. 创建文件 `states/pool/005-Jetpack-Compose状态管理.yaml`：
   ```yaml
   id: 005
   title: Jetpack Compose 状态管理
   category: android
   core: true
   level: 0
   review_stage: 0
   status: pool
   last_study: null
   next_review: null
   importance: 4
   created: 2026-03-02
   ```
6. 告知用户：
   ```
   已创建 states/pool/005-Jetpack-Compose状态管理.yaml
   - id: 005
   - category: android
   - importance: 4
   - core: true
   - status: pool
   ```

---

### 1.1 新增项目（新增）

**用户输入**：
```
新增知识点：视频加水印项目
或
新增项目：视频加水印优化
```

**AI 执行流程**：

1. 扫描 states/ 下所有 yaml 文件，找到最大序号（例如 005）
2. 新序号 = 006
3. 智能推断这是一个项目：
   ```
   我推断这是一个项目（而非知识点）。
   请提供项目代码路径（例如：D:\Projects\video-watermark）
   ```
4. 用户提供路径：
   ```
   D:\Projects\video-watermark
   ```
5. 智能推断 importance、core：
   ```
   我推断这是一个核心项目，重要性 5。
   是否确认？或者你可以修改。
   ```
6. 用户确认或修改
7. 创建文件 `states/pool/006-视频加水印项目.yaml`：
   ```yaml
   id: 006
   title: 视频加水印项目
   category: project
   core: true
   level: 0
   review_stage: 0
   status: pool
   last_study: null
   next_review: null
   importance: 5
   created: 2026-03-02
   project_path: D:\Projects\video-watermark
   ```
8. 创建项目笔记目录：
   ```
   mkdir notes/006-视频加水印项目/
   ```
9. 创建项目状态文件 `notes/006-视频加水印项目/state.yaml`：
   ```yaml
   project_id: 006
   title: 视频加水印项目
   project_path: D:\Projects\video-watermark
   current_round: 0
   tech_stack: []
   architecture_analyzed: false
   rounds_completed: []
   interview_questions:
     basic: 0
     deep: 0
     extend: 0
   last_updated: 2026-03-02
   ```
10. 告知用户：
    ```
    已创建项目：视频加水印项目
    - id: 006
    - category: project
    - importance: 5
    - core: true
    - status: pool
    - project_path: D:\Projects\video-watermark
    - 项目笔记目录：notes/006-视频加水印项目/
    
    提示：当你准备学习这个项目时，说"开始学习视频加水印项目"，
    将自动触发 project-interview-prep skill 进行项目分析和学习。
    ```

---

### 2. 提升 Level

**用户输入**：
```
Android生命周期 提升到 level 3
```

**AI 执行流程**：

1. **检验阶段**（防止等级虚高）：
   ```
   好的，请口述一下 Android 生命周期的核心概念
   ```
   
2. **用户口述后，AI 追问**（数量不固定，基于回答完整性）：
   ```
   [追问 1] onCreate 和 onStart 的区别是什么？
   [追问 2] 配置变更时会调用哪些生命周期方法？
   [追问 3] onSaveInstanceState 在什么时候调用？
   ```

3. **判断达标**：
   ```
   我认为你已经达到 level 3（能完整讲清楚）。是否确认更新？
   ```

4. **用户确认后，更新文件**：
   - 读取 states/active/001-Android生命周期.yaml
   - 更新字段：
     ```yaml
     level: 3
     last_study: 2026-03-02
     last_assessment:
       date: 2026-03-02
       result: good
       score: 4
       mode: qa
       weak_points: []
       suggested_interval_days: 3
     ```
   - 判断状态转移：
     
     - 如果 level 变成 4 → 移动到 states/review/
   
5. **明确告知**：
   ```
   已更新 Android生命周期 到 level 3
   - level: 2 → 3
   - last_study: 2026-03-02
   ```
   
   如果发生状态转移：
   ```
   已更新 Android生命周期 到 level 4
   - level: 3 → 4
   - status: active → review
   - 文件已移动：states/active/001-Android生命周期.yaml → states/review/001-Android生命周期.yaml
   - review_stage: 0
   - assessment_result: pass
   - next_review: 2026-03-03（基于 stage 0 基准 1 天，按 pass 保守处理）
   - last_study: 2026-03-02
   ```

---

### 3. 完成复习

**用户输入**：
```
Android生命周期 仅复习
```

**AI 执行流程**：

1. 读取状态文件，判断类型（知识点 or 项目）

2. **执行考核并记录结果**：
   - 默认必须做一次简短检验，至少包含：
     - 1 个主问题：让用户口述核心内容
     - 2-3 个追问：验证细节、边界、对比、易错点
   - AI 根据回答给出 `fail | weak | pass | good | excellent`

3. **如果是知识点**：
   - 读取 states/review/001-Android生命周期.yaml
   - 更新字段：
     ```yaml
     review_stage: 2 → 3
     last_study: 2026-03-02
     stability_score: 68 → 78
     consecutive_success: 1 → 2
     consecutive_failures: 0 → 0
     last_assessment:
       date: 2026-03-02
       result: good
       score: 4
       mode: recall
       weak_points:
         - onSaveInstanceState 触发时机还不够稳
       suggested_interval_days: 18
     next_review: 2026-03-20  # stage 3 基准 14 天 * good(1.3x)，向上取整后约 18 天
     ```
   - 判断状态转移：
     
     - 如果 level=4 且 review_stage>=4 且 consecutive_success>=3 且 stability_score>=85 → 移动到 states/mastered/
   - 明确告知：
     ```
     已完成 Android生命周期 的复习
     - assessment_result: good
     - review_stage: 2 → 3
     - stability_score: 68 → 78
     - next_review: 2026-03-20（stage 3 基准 14 天 × good 1.3）
     - last_study: 2026-03-02
  ```
   
4. **如果是项目**（category: project）：
   - 读取 states/review/003-视频加水印项目.yaml
   - 调用 project-interview-prep skill 执行模拟面试
   - 模拟面试完成后，更新字段：
     ```yaml
     review_stage: 2 → 2
     last_study: 2026-03-02
     stability_score: 72 → 70
     consecutive_success: 2 → 0
     consecutive_failures: 0 → 1
     last_assessment:
       date: 2026-03-02
       result: weak
       score: 2
       mode: mock_interview
       weak_points:
         - MediaCodec 输入输出队列协作过程解释不完整
         - 性能优化前后瓶颈对比不够清楚
       suggested_interval_days: 11
     next_review: 2026-03-13  # stage 2 基准 7 天 × weak(0.8) 后，再考虑核心项目保守处理
     ```
   - 明确告知：
     ```
     已完成 视频加水印项目 的复习（模拟面试）
     - assessment_result: weak
     - review_stage: 2 → 2
     - next_review: 2026-03-13（表现不稳定，缩短复习周期）
     - last_study: 2026-03-02
     ```

---

### 4. 批量更新

**用户输入**：
```
Android生命周期 提升到 level 3
Kotlin协程 仅复习
新增知识点：ViewModel 原理
```

**AI 执行流程**：

按顺序处理每个操作，遵循上述各自的流程。

---

## AI 检验机制

### 何时检验

当用户声称提升 level 时，或用户说“仅复习”时。

### 如何检验

1. **要求口述**：
   ```
   请口述一下 XXX 的核心概念
   ```

2. **追问**（数量不固定，基于回答完整性）：
   - 如果回答完整、清晰 → 追问 2-3 个问题
   - 如果回答模糊、有遗漏 → 追问更多问题
   - 追问应该针对关键细节、易错点、对比概念

3. **输出考核评级**：
   - 必须明确给出：
     - `result`: fail | weak | pass | good | excellent
     - `score`: 1-5
     - `weak_points`: 当前薄弱点
   - 这个评级将直接影响 `next_review`

4. **判断达标**：
   - 基于 Level 定义的标准
   - 考虑回答的完整性、准确性、逻辑性

5. **给出结论**：
   ```
   我认为你已经达到 level X。是否确认更新？
   或
   我认为还未达到 level X，建议继续学习。是否仍要更新？
   ```

6. **动态更新状态**：
   - 更新 `last_assessment`
   - 更新 `stability_score`
   - 更新 `consecutive_success / consecutive_failures`
   - 重新计算 `next_review`

### 用户权力

- 用户可以说"我不想检验，直接更新"→ AI 按用户要求更新，但提示：
  ```
  好的，已跳过检验。但建议定期自我检验，避免等级虚高。
  ```
- 跳过检验时，`last_assessment.mode=skip_check`，且 `result` 默认按 `weak` 处理，避免把复习周期拉得过长
- 用户可以拒绝 AI 的判断 → AI 尊重用户决定

---

## 用户权力规则

1. **用户拥有最终任务选择权**
   - 用户可以拒绝当日建议
   - 用户可以自行选择学习内容

2. **系统必须提示偏离影响**
   ```
   你选择跳过今日建议任务。提醒：
   - Android生命周期（核心知识点）已 10 天未触碰
   - 当前有 3 个知识点超期 7 天以上
   ```

3. **用户可以修改任何状态文件**
   - 用户可以手动编辑 yaml 文件
   - 用户可以手动移动文件
   - AI 读取时以文件内容为准

---

## meta.md 的作用

meta.md 用于记录学习方法反思和系统调整。

### AI 需要读取 meta.md

在生成每日任务前，AI 应该读取 meta.md，了解：
- 用户的学习习惯调整
- 系统参数的变化（例如复习周期调整）
- 长期趋势观察

### 示例内容

```markdown
# 学习系统调整日志

## 2026-03-02
- 发现 7 天复习周期对于复杂知识点太短
- 考虑将 review_stage 2 的周期从 7 天改为 10 天
- 决定：暂不调整，先观察一个月

## 2026-02-25
- 发现口述验证效果很好，增加口述频率
- 核心知识点的 importance 权重应该更高
- 决定：在优先级计算中，core=true 的权重提升

## 2026-02-20
- 某些知识点总是学不会，可能需要拆分成更小的知识点
- 例如：Kotlin协程 → 拆分为"协程基础"、"协程原理"、"Flow"
```

---

## 长期稳定性原则

1. **不引入黑盒算法** - 使用可解释的动态规则，而非复杂不可控模型
2. **不依赖模型记忆** - 所有状态存在 yaml 文件
3. **所有状态存在文件** - 文件即数据库
4. **可替换模型与 Agent** - 任何 AI 读取 SKILL.md 后都能执行
5. **GitHub 作为长期持久化** - 版本控制即历史记录

---

## 子知识点追踪规则

每张卡片可选包含 `sub_points` 字段，追踪卡片内的独立子知识点掌握状态。

完整规则详见：[sub-points-rules.md](sub-points-rules.md)

核心要点：
- 每张卡片最多 8 个 sub_points，每个有独立的 weak/ok/good 状态
- 每次复习后在 `review_sessions` 中追加一条记录，记录本次覆盖了哪些 sub_points
- 未覆盖的 sub_point 状态保持不变（不自动重置）
- 没有 sub_points 字段的卡片按现有规则处理，向后兼容

---

## 跨卡知识图谱规则（v1.1 新增）

详细规则见 [graph-rules.md](graph-rules.md)。

### related_cards 字段

```yaml
related_cards: [10, 11, 14]   # 强关联的其他卡片 ID（整数列表）
```

- 双向添加：A → B 则 B → A
- 每张卡最多 4 个强关联

### 联合考察

- 触发：当日任务中有 ≥2 张互为 related_cards 的卡，或用户主动要求
- 结果写入 [joint-review-log.md](joint-review-log.md)，**不修改**单卡的 `consecutive_success`

---

## 状态签到规则（v1.1 新增）

详细规则见 [graph-rules.md](graph-rules.md)。

每次复习会话开始时签到：A（状态好）/ B（一般）/ C（很累）

| 状态 | 策略 |
|------|------|
| A | 正常调度，可触发联合考察 |
| B | 缩减至 3-5 张，跳过联合考察 |
| C | 只做 1-2 张最高优先级卡，降低考察强度 |

mood 记录在 joint-review-log.md，不写入单卡 review_sessions。

---

## 新模块学习工作流（v1.1 新增）

详细步骤见 [new-module-workflow.md](new-module-workflow.md)。

**7步流程：**

1. **立项** — 在 GSD ROADMAP.md 创建新 phase，写 Goal 和 Success Criteria
2. **学习** — 原始笔记写入 `04. 学习_*/` 目录
3. **拆解** — 列出 3-8 个独立知识点，每个对应一张 YAML card
4. **设计 sub_points** — 每个知识点列 3-8 个子知识点
5. **创建 YAML card** — 放入 `states/active/`，新卡默认 `level:1`、`next_review: 学习日 + 3天`
6. **校验** — id 唯一、sub_points 已填、related_cards 已参考分组、status: active
7. **更新 ROADMAP** — 打勾 Success Criteria，标记 phase 完成

**关键约束：**
- 新卡 `status` 必须是 `active`（不是 `draft` 或其他）才会进入复习队列
- `next_review` 必须设置，不能为空，否则不会出现在每日任务中

---

## 注意事项

1. **状态与内容分离**
   - AI 只读写 states/ 目录
   - notes/ 目录：
     - 知识点笔记：用户自由管理，AI 不读取
     - 项目笔记：project-interview-prep 管理，AI 读写

2. **序号管理**
   - 序号永远递增，不重复使用
   - 用户可以修改文件名（包括标题部分）

3. **明确告知**
   - 状态转移时，明确告知文件移动
   - 更新字段时，列出变更内容

4. **智能推断**
   - 新增知识点时，智能推断 category/importance/core
   - 新增项目时，智能推断 importance/core，并要求提供 project_path
   - 给出推断理由，等待用户确认

5. **检验机制**
   - 防止等级虚高
   - 但尊重用户最终决定

6. **项目与知识点的区别**
   - 知识点：AI 追问验证，用户口述
   - 项目：调用 project-interview-prep skill，执行四轮学习或模拟面试

7. **联动机制**
   - 当用户说"开始学习XXX项目"时，自动触发 project-interview-prep skill
   - project-interview-prep 完成轮次后，自动更新 learning-behavior-system 的 level 和 last_study
   - 项目复习时，learning-behavior-system 调用 project-interview-prep 执行模拟面试

---

## 快速参考

### 常用命令

**知识点相关**：
- `今天该干嘛？` - 生成每日任务
- `新增知识点：XXX` - 创建新知识点
- `XXX 提升到 level N` - 提升等级（带检验）
- `XXX 仅复习` - 完成复习
- `跳过今日任务` - 拒绝建议（会提示影响）

**项目相关**（新增）：
- `新增项目：XXX` - 创建新项目
- `开始学习 XXX 项目` - 开始项目学习（触发 project-interview-prep）
- `XXX 项目 仅复习` - 项目复习（模拟面试）

### 状态转移

- pool → active：用户开始学习
- active → review：level 达到 4
- review → mastered：level=4 且 review_stage>=4

### 复习周期

- Stage 0: 基准 1天
- Stage 1: 基准 3天
- Stage 2: 基准 7天
- Stage 3: 基准 14天
- Stage 4: 基准 30天
- 最终 `next_review`: 基准间隔 × 考核结果 × 稳定度/连续表现修正

### Level 对应关系

**知识点**：
- Level 0: 未接触
- Level 1: 熟悉
- Level 2: 理解概念
- Level 3: 能完整讲清楚
- Level 4: 面试可稳定回答

**项目**：
- Level 0: 未接触
- Level 1: 了解（第1轮）
- Level 2: 初步学会（第2轮）
- Level 3: 深入掌握（第3轮）
- Level 4: 可以面试（第4轮）

---

**这是一个学习行为状态机系统，它管理记忆强度、遗忘风险、核心偏置和认知负债，支持知识点和项目两种类型的学习内容。**
