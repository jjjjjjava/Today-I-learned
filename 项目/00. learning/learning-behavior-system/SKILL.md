---
name: learning-behavior-system
description: 面向 Android 工程师的长期学习行为管理系统。当用户询问"今天该干嘛"、"今日任务"、"学习计划"、"复习安排"、"今天学什么"或任何关于学习进度、复习提醒、知识点管理、项目管理的问题时触发。这是一个学习行为状态机，管理记忆强度、遗忘风险、核心知识偏置和认知负债，支持知识点和项目两种类型的学习内容。
---

# Learning Operating System v2.0

面向 Android 工程师的一年期学习行为管理系统（支持知识点 + 项目）。

## 参考文档

| 文档 | 内容 |
|------|------|
| SKILL.md（本文件） | 核心规则：字段定义、状态机、调度逻辑、AI 行为约束 |
| [interval-rules.md](interval-rules.md) | 动态间隔查表、毕业/退步规则 |
| [sub-points-rules.md](sub-points-rules.md) | sub_points 字段规则、review_sessions 追加规则 |
| [graph-rules.md](graph-rules.md) | related_cards 字段、联合考察触发与独立记录、MOOD 签到规则 |
| [joint-review-log.md](joint-review-log.md) | 联合考察独立日志（不影响单卡计分） |
| [new-module-workflow.md](new-module-workflow.md) | 新模块学习 7 步工作流 |
| [SKILL-ops.md](SKILL-ops.md) | 操作协议详细版（新增/提升/复习的完整示例流程） |

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
  result: ok                      # good | ok | fail
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
  result: fail                    # good | ok | fail
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

原有 `review_stage` 基准值仍作为参考（0→1天、1→3天、2→7天、3→14天、4→30天），**但 v1.1 以后 `next_review` 以 [interval-rules.md](interval-rules.md) 的查表规则为准**。

**v1.1 规则摘要：**
- `good`（稳定掌握）→ 按 consecutive_success 查表，间隔递增
- `ok`（部分掌握）→ 查表值，但不超过上次间隔 × 1.3
- `fail`（明显失误）→ 强制 1 天
- 毕业：`consecutive_success ≥ 8` 且间隔 ≥ 30 天 → `status: archived`
- 退步：`consecutive_failures ≥ 3` → 间隔重置为 1 天

### AI 执行要求

- 每次复习或升级后，AI 必须先给出考核结论，再更新 `next_review`
- AI 必须在输出中说明：本次结果是什么、为什么、`next_review` 怎么算出来的
- 跳过检验时，默认按 `ok` 处理，避免间隔拉得过长

---

## 状态转移规则

### 状态流转图

```
pool (level=0)
  ↓ 用户开始学习
active (level 1-3, 正在提升)
  ├─ consecutive_success≥8 且间隔≥30天 → archived（毕业，文件留在 active/，停止出现在复习队列）
  └─ 达到 level=4
review (level=4, review_stage 0-3)
  ↓ review_stage≥4 且 consecutive_success≥3 且 stability_score≥85
mastered (稳定掌握)
```

### 自动状态转移

**1. active → review**
- 触发条件：level 提升到 4
- 操作：移动文件从 states/active/ 到 states/review/
- 初始化：`review_stage=0`、`stability_score=50`、`consecutive_success/failures=0`

**2. active → archived（毕业）**
- 触发条件：`consecutive_success ≥ 8` 且上次实际间隔 ≥ 30 天
- 操作：将 `status` 改为 `archived`，**文件留在 states/active/**，不移动
- 效果：不再出现在每日复习队列，但可手动查询

**3. review → mastered**
- 触发条件：level=4 且 review_stage≥4 且 consecutive_success≥3 且 stability_score≥85
- 操作：移动文件从 states/review/ 到 states/mastered/

**4. pool → active**
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

详细操作流程见 [SKILL-ops.md](SKILL-ops.md)。

**操作类型摘要：**

| 操作 | 触发词示例 | 核心动作 |
|------|-----------|---------|
| 新增知识点 | "新增知识点：XXX" | 创建 yaml，直接进 active，next_review = 今天+3天 |
| 新增项目 | "新增项目：XXX" | category: project，询问代码路径 |
| 提升 Level | "XXX 提升到 level N" | 先检验，再更新 level + next_review |
| 完成复习 | "XXX 仅复习" | 考核，更新 consecutive_*/next_review，追加 review_sessions |
| 批量更新 | 多行指令 | 按顺序依次处理 |

**result 枚举**（统一）：`good`（稳定）| `ok`（部分）| `fail`（失误）

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
     - `result`: `good`（稳定掌握）| `ok`（部分掌握，有遗漏）| `fail`（回答明显错误或无法回忆）
     - `score`: 1-5
     - `weak_points`: 当前薄弱点
   - 这个评级将直接影响 `next_review`，规则见 [interval-rules.md](interval-rules.md)

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

格式：按日期分节，每节记录一次系统调整或观察，见实际 meta.md 文件。

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
