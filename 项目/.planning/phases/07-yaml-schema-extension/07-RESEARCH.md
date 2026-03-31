# Phase 7 & 8: YAML Schema Extension + Cross-Card Graph Validation — Research

**Researched:** 2026-03-31
**Domain:** Spaced repetition algorithms, cognitive science of learning, YAML schema design
**Confidence:** HIGH (core algorithms), MEDIUM (cognitive state research), HIGH (schema design patterns)

---

## Summary

This research covers the technical and scientific foundations needed to plan Phase 7 (dynamic intervals, graduation, sub-points) and Phase 8 (cross-card graph, state check-in). The deliverables are YAML schema extensions and Markdown workflow rules — not a software product.

The SM-2 algorithm provides the scientific basis for interval growth and failure reset. For a manual review system without automated EF tracking, a simplified consecutive-success-driven lookup table is the right pragmatic approach — SM-2's EF machinery is too fragile to maintain by hand. FSRS is not applicable (requires 1,000+ automated reviews to calibrate). Sub-points should use a flat list with per-item status inside `last_assessment` — no independent scheduling per sub-point. Cognitive science on learning state strongly supports lighter review modes on low-state days but does NOT support skipping entirely. Interleaving (cross-card joint review) has strong experimental support for long-term retention over blocked practice.

**Primary recommendation:** Adopt a simplified SM-2-inspired manual interval table (consecutive_success → days) rather than computing EF by hand. Graduation threshold at consecutive_success ≥ 8 AND interval ≥ 30 days. Failure reset at consecutive_failures ≥ 3 (not 8 like Anki's leech default, because this system uses consecutive not cumulative). State check-in uses 3 levels: Full / Light / Rest-day, with rules derived from cognitive load research.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GRADUATE-01 | consecutive_success drives dynamic next_review interval | SM-2 interval formula; simplified lookup table design |
| GRADUATE-02 | Card graduates to archived when consecutive_success ≥ N AND interval ≥ X | Anki graduation mechanism; Ebbinghaus long-interval stability |
| GRADUATE-03 | consecutive_failures ≥ threshold → reset to short interval | SM-2 reset mechanics; Anki leech behavior; adapted threshold rationale |
| SUBPOINT-01 | YAML cards support sub_points field listing independent sub-knowledge-points | YAML schema design; flat-list approach rationale |
| SUBPOINT-02 | Each review session records which sub_points were covered | session-scoped coverage tracking design |
| SUBPOINT-03 | sub_points have independent weak/ok/good status tracked across sessions | per-item status accumulation design |
| GRAPH-01 | Cards support related_cards field with IDs of strongly associated cards | Schema pattern; semantic relationship types |
| GRAPH-02 | Joint review sessions cover complete cross-card call chains | Interleaving research evidence |
| GRAPH-03 | Joint review results recorded independently, single-card consecutive_success unchanged | Score isolation design rationale |
| MOOD-01 | Pre-session state check-in before each review session | Cognitive load theory; affective computing research |
| MOOD-02 | State → review mode mapping based on cognitive science | Desirable difficulty; fatigue-retrieval interaction evidence |
| MOOD-03 | Overdue cards on low-state days have explicit handling rules | Cascading failure risk; overdue catch-up research |
| MOOD-04 | Check-in state recorded in review log for trend analysis | Log schema extension design |
</phase_requirements>

---

## 1. SM-2 / FSRS 算法核心公式与参数

### 1.1 SM-2 算法（权威来源：SuperMemo 官方文档）

**间隔计算公式：**
```
I(1) = 1 天
I(2) = 6 天
I(n) = I(n-1) × EF      （n > 2）
```

**EF（易度因子）更新公式：**
```
EF_new = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))

其中：
  q = 本次评分（0-5）
  EF 初始值 = 2.5
  EF 最小值 = 1.3（硬约束，不得低于此值）
```

**评分等级（0-5）：**
| 分数 | 含义 | 是否算通过 |
|------|------|-----------|
| 5 | 完美回忆 | 通过 |
| 4 | 正确但有犹豫 | 通过 |
| 3 | 正确但很难想起 | 通过（但EF降低） |
| 2 | 错误，但答案一说出来感觉容易 | 失败 |
| 1 | 错误，但看到答案能想起来 | 失败 |
| 0 | 完全遗忘 | 失败 |

**失败重置规则：**
- q < 3 → repetition counter 重置为 0 → 间隔重置为 1 天
- EF 在失败时依然更新（不重置，只降低）

**间隔增长示例（EF=2.5 时）：**
```
第1次成功 → 1天
第2次成功 → 6天
第3次成功 → 6 × 2.5 = 15天
第4次成功 → 15 × 2.5 = 37.5天
第5次成功 → 37.5 × 2.5 = 93.75天
```

**置信度：HIGH** — 来源：官方算法文档，被多个独立实现交叉验证。

### 1.2 FSRS 算法（现代 Anki 默认）

**核心差异：**
- 使用记忆稳定性（stability）和难度（difficulty）两个参数替代 EF
- 包含 17 个权重参数，通过机器学习从历史数据中自动校准
- 需要至少 1,000 次复习记录才能有效优化
- 效率提升：同等保留率下减少 20-30% 的复习次数

**对本系统的结论（CRITICAL）：**
FSRS **不适用于本系统**。原因：
1. 本系统是手动复习系统（无自动调度器），无法累积足够的机器学习训练数据
2. FSRS 的权重优化需要精确的时间戳记录和自动评分收集，手动系统无法做到
3. 本系统的 consecutive_success/consecutive_failures 计数器已经捕获了 SM-2 的核心语义

**置信度：HIGH** — 来源：RemNote FSRS 文档，FSRS GitHub，多个对比评测。

### 1.3 Anki 的毕业与退步机制（参考基准）

**毕业（Graduating）机制：**
- 新卡学习步骤完成后（通过所有 Learning Steps）→ 毕业为复习卡
- 默认毕业间隔：1 天（可配置）
- Anki 没有"archived"概念，用"suspended"表示手动暂停

**退步（Leech）机制：**
- 触发条件：**累计** lapses（失败次数）达到阈值（默认 8 次）
- 注意：Anki 的 leech 是**累计**计数，不是**连续**计数
- 触发后：标记 leech tag + 自动 suspend 卡片
- 本系统使用 consecutive_failures（**连续**失败），阈值要比 8 小得多

**置信度：HIGH** — 来源：Anki 官方手册。

---

## 2. 手动复习系统的实用动态间隔方案

### 2.1 核心设计原则

本系统的关键约束：
- **手动**设置 next_review（Claude 按规则计算并建议，用户确认）
- 无 EF 自动追踪（EF 需要精确的 0-5 评分，本系统用 good/ok/fail 三档）
- 现有字段：consecutive_success, consecutive_failures, suggested_interval_days

**推荐方案：consecutive_success → 间隔查表（不计算 EF）**

### 2.2 动态间隔查表（推荐）

基于 SM-2 的第 1、2 次固定间隔 + 之后按倍数增长的模式，设计如下查表：

```
consecutive_success → 建议间隔（天）

  0  → 1 天   （刚失败或刚开始，明天必须复习）
  1  → 2 天   （ok/good 第1次，短间隔确认）
  2  → 4 天   （接近 SM-2 的 I(2)=6天，稍保守）
  3  → 7 天   （一周，稳定初级）
  4  → 14 天  （两周，SM-2 level 约等于这里）
  5  → 21 天  （三周）
  6  → 30 天  （一月，接近毕业门槛）
  7  → 45 天  （超过一月，高稳定性）
  8  → 60 天  （两月，毕业候选）
  9+ → 90 天  （季度级，顶级稳定，触发毕业检查）
```

这条间隔序列的增长率约为 1.4-1.7x，比 SM-2 的 2.5x EF 保守，适合手动系统。

**规则说明：**
- `result: good` → consecutive_success += 1，查表取间隔
- `result: ok` → consecutive_success += 1（已有 memory 规则），查表取间隔，但间隔不超过上一次的 1.2x（防止 ok 连续推得太远）
- `result: fail` → consecutive_failures += 1，consecutive_success 不重置（独立计数），但**间隔强制重置为 1 天**
- `suggested_interval_days` 字段记录本次计算结果，最终 next_review 由用户确认

**ok 的特殊处理（来自已有 memory）：**
ok = success（consecutive_success += 1），但表现弱于 good，因此间隔限制为：
```
ok 的实际间隔 = min(查表值, 上次间隔 × 1.3)
```
这样 ok 连击不会像 good 连击一样快速拉长间隔。

### 2.3 毕业规则（GRADUATE-02）

**建议毕业阈值：consecutive_success ≥ 8 AND 上次间隔 ≥ 30 天**

依据：
- Anki 中卡片进入"mature"状态的阈值是间隔 ≥ 21 天
- 间隔 ≥ 30 天意味着一个月的记忆稳定性，对工程知识是合理基准
- consecutive_success ≥ 8 意味着至少有 8 次不间断的成功检验
- 两个条件同时满足才毕业，防止通过短时间密集复习刷到 8 次连胜

**毕业后行为：**
```yaml
status: archived  # 从 active → archived
```
不再出现在每日复习队列。如果后续发现实际遗忘，可手动将 status 改回 active 并重置 consecutive_success。

### 2.4 退步规则（GRADUATE-03）

**建议退步阈值：consecutive_failures ≥ 3**

依据：
- Anki 的 leech 阈值是累计 8 次失败（累计，不是连续）
- 本系统的 consecutive_failures 是**连续**计数，语义更严格
- 连续失败 3 次（3 天内都没过）说明知识点出现了真实遗忘，需要重新高频复习
- 不用到 8 次是因为连续失败比累计失败更强的信号

**退步后行为：**
```
next_review = 明天（强制 1 天间隔）
consecutive_success 不重置（保留历史）
consecutive_failures 保持累计（不重置）
```

**注意：** consecutive_success 和 consecutive_failures 独立累计，失败不归零成功计数（已有 memory 规则）。

---

## 3. Sub-points 追踪的 YAML Schema 设计建议

### 3.1 现有 SRS 系统对粒度追踪的处理方式

**Anki 的方案（Cloze deletion）：**
- 一张大卡拆成多张独立的 Cloze 卡，每个知识点一张卡，独立调度
- 优点：完全独立的 SRS 调度；缺点：卡片数量爆炸，相互间关联丢失

**SuperMemo Element Splitting：**
- 将大主题拆分为多个独立 Element，独立调度
- 同样导致原子化碎片，关联上下文丢失

**本系统的约束（CRITICAL）：**
本系统的卡片粒度是**知识模块**（如"OpenGL ES 零拷贝图形管线"），每张卡包含多个子知识点。将其拆成 Anki 式原子卡不符合系统设计（系统设计是用 Claude 对话复习，考察调用链，不是填空）。

### 3.2 推荐 Schema 设计（SUBPOINT-01~03）

**设计原则：**
- sub_points 是**卡片内**的静态知识点列表，不独立调度
- 每次复习后更新每个 sub_point 的状态（跨会话累计）
- 保持 YAML 可读性，避免深层嵌套

**推荐 Schema：**

```yaml
# 在现有 YAML 字段末尾追加以下字段

sub_points:
  - id: sp1
    desc: "updateTexImage 的本质（引用更新非拷贝）"
    status: good          # weak | ok | good（跨会话累计，不自动重置）
    last_reviewed: 2026-03-27

  - id: sp2
    desc: "BufferQueue 三缓冲状态机（FREE/QUEUED/ACQUIRED）"
    status: ok
    last_reviewed: 2026-03-27

  - id: sp3
    desc: "EGLImage 绑定机制（eglCreateImageKHR）"
    status: weak
    last_reviewed: 2026-03-20

# 每次复习会话追加一条记录
review_sessions:
  - date: 2026-03-27
    covered_sub_points: [sp1, sp2]   # 本次覆盖的 sub_point id 列表
    result: ok
    score: 3
```

**字段说明：**

| 字段 | 说明 | 更新规则 |
|------|------|---------|
| `sub_points[].id` | 短 ID（sp1, sp2...），在 covered 列表中引用 | 创建时设定，不变 |
| `sub_points[].desc` | 人类可读的子知识点描述 | 手动维护 |
| `sub_points[].status` | weak / ok / good，跨会话累计 | 每次复习后按本次表现更新；不自动重置 |
| `sub_points[].last_reviewed` | 上次复习此 sub_point 的日期 | 出现在 covered 列表时更新 |
| `review_sessions[].covered_sub_points` | 本次复习覆盖的 sub_point id 列表 | 每次复习会话追加，不修改历史 |

### 3.3 Sub_points 状态更新规则

```
本次 covered 某 sub_point 时：
  result=good → 该 sub_point.status 升至 good（最高）
  result=ok   → 该 sub_point.status 升至 ok（如果原来是 weak）
  result=fail → 该 sub_point.status 降至 weak

本次未 covered 某 sub_point：
  该 sub_point.status 不变（保留上次状态）
  → 这是 SUBPOINT-03 的核心：未覆盖的子知识点状态不清零
```

### 3.4 不推荐的方案

**方案 A：sub_points 有独立 next_review**
- 问题：复习粒度变成 sub_point 级，与本系统"模块级卡片"的设计冲突
- 问题：YAML 维护成本指数级增加
- 结论：不采用

**方案 B：session 内覆盖记录扁平化为字符串列表**
- 问题：无法追踪哪些 sub_point 从未覆盖，也无法统计弱点累积
- 结论：不采用，用结构化 id 引用代替

---

## 4. 跨卡联合考察的设计依据（GRAPH-01~03）

### 4.1 Interleaving（交错学习）的研究依据

**研究证据（MEDIUM-HIGH 置信度）：**

2021 年 npj Science of Learning 发表的物理学习研究：
- 交错练习 vs 分块练习（blocked），用惊喜测试评估
- **中位值提升：测试1 +50%，测试2 +125%**
- 结论：交错练习在保留测试中表现大幅优于分块练习

2023 年 Frontiers in Psychology 研究（科学概念学习）：
- 交错组：2 周后测试准确率更高
- 分块组：当天测试准确率更高（illusion of learning）
- 结论：交错学习的好处在延迟测试中才显现

**重要约束条件（2025 Language Learning 研究）：**
- 对于**初学者/低水平学习者**，初始阶段先分块学习更优
- 交错的优势在**基础已稳固**之后才显现
- 在本系统的语境下：related_cards 中的联合考察应在各卡 consecutive_success ≥ 2（有一定稳定性）后才触发

**对本系统的设计建议：**
跨卡联合考察（GRAPH-02）的触发条件应是：
- all related_cards 的 status 均为 active（不是 pool/archived）
- 每张相关卡的 consecutive_success ≥ 2（各自已有基础）
- 触发频率：不超过每月一次（联合考察是高认知负荷活动）

### 4.2 Related Cards Schema（GRAPH-01）

**推荐 Schema：**

```yaml
related_cards:
  - id: 021
    relation: prerequisite    # prerequisite | companion | extends
    note: "双Surface架构是EGL的前置基础"
  - id: 024
    relation: companion
    note: "完整实战代码中EGL管理逻辑"
```

**relation 类型定义：**
| 类型 | 语义 | 联合考察方向 |
|------|------|------------|
| prerequisite | 当前卡依赖对方的概念 | 先考 prerequisite 卡，再考当前卡 |
| companion | 同一技术栈的平行知识 | 任意顺序，检验整合调用 |
| extends | 当前卡是对方的深化 | 先考当前卡，再扩展到关联卡 |

### 4.3 联合考察独立计分（GRAPH-03）

**设计依据：**
- 联合考察评估的是**知识整合能力**（cross-card call chain），与单卡知识点的稳定性是不同维度
- 联合考察表现差不应惩罚单卡的 consecutive_success（单卡知识点本身可能是好的）
- 联合考察表现好不应给单卡"加分"（防止虚高）

**推荐的独立记录 Schema：**

在 YAML 中追加 `joint_reviews` 字段（不修改 last_assessment）：

```yaml
joint_reviews:
  - date: 2026-04-15
    partner_cards: [021, 024]
    topic: "EGL完整渲染管线：从SurfaceView到SurfaceFlinger"
    result: ok         # fail | ok | good
    weak_points:
      - "eglMakeCurrent → TLS → FBO链路整体连贯但VSync部分断链"
    note: "单卡知识点均ok，跨卡整合时VSync路径B描述不完整"
```

---

## 5. 状态签到的认知科学依据 + 状态→复习方式映射

### 5.1 学习状态对复习效果的影响（认知科学依据）

**疲劳对认知表现的影响（HIGH 置信度）：**

睡眠剥夺的记忆研究（PMC 8893218，2022 年 meta 分析）：
- 睡眠剥夺后即时测试的记忆缺损：g = 0.410（中等效应量）
- 有恢复睡眠后的持续缺损：g = 0.176（小效应量）
- 结论：**严重疲劳时学习效果显著下降**，但不是零效果

**认知负荷理论与最优挑战点：**
- Challenge Point Framework：学习增益在"接近但不超过认知上限"时最大
- 过高认知负荷（疲劳状态）→ 前额叶激活不足 → 效率下降
- 但关键发现：**即使在疲劳状态下，检索练习仍比完全不复习好**（spacing effect 在低状态下仍然存在，只是效果打折）

**被动复习 vs 主动检索（HIGH 置信度）：**
- Karpicke & Roediger (2008)：主动检索 vs 重新阅读，长期保留率 +150%
- 疲劳状态下，主动检索认知成本更高，但被动复习的学习收益更低
- 折中策略：疲劳时降低检索难度（提示辅助）而非转向被动重读

**Johns Hopkins 过度训练研究（关键警告）：**
- 在肌肉完全耗尽后继续训练 → 学习能力长期受损（not just day-of）
- 对照到认知学习：在极度认知疲劳状态下强行高强度复习可能有负面效果
- 建议：区分"轻度疲劳"（可以复习，降低难度）和"极度疲劳"（应休息）

### 5.2 状态签到设计（MOOD-01）

**推荐：3 档状态，不用 5 档（减少摩擦）**

```
签到选项：
  A. 状态好（Full mode）   — 精力充沛，可以深度检索
  B. 状态一般（Light mode）— 有点累，可以轻量复习
  C. 今天很差（Rest mode） — 疲惫/特殊情况，最小化操作
```

5 档设计会增加签到摩擦，降低一致性（Duolingo 研究表明：降低摩擦是习惯养成的关键）。

### 5.3 状态 → 复习方式映射（MOOD-02）

| 状态 | 复习方式 | 检索深度 | 逾期卡处理 | 依据 |
|------|---------|---------|----------|------|
| Full | QA 深度检索：背对背，无提示，要求完整讲清 | 高 | 全量处理，按正常规则评分 | 主动检索效果最优 |
| Light | 辅助检索：打开 notes 的结构性标题，背对提示复述关键路径 | 中 | 只处理逾期 ≤ 7 天的卡，超期更多的推迟 | 认知负荷降低时保持检索而非放弃 |
| Rest | 快速浏览：只翻阅 notes，不作检索，只更新日期 | 极低 | 所有卡推迟 2 天（统一延后，不逐卡决定）| 避免极端疲劳时的负面学习效果 |

**Full mode 的具体复习流程（现有流程不变）：**
- Claude 出题 → 用户回答 → 评分 good/ok/fail → 更新 YAML

**Light mode 的具体复习流程：**
- Claude 显示 sub_points 标题列表 → 用户针对标题复述（不是无提示回忆）
- 评分标准：能讲清 = ok，讲不清某 sub_point = 该 sub_point 标记 weak

**Rest mode 的具体流程：**
- 不做检索，只更新 `next_review += 2天`
- 在复习日志中记录 `mode: rest_day`，不更新 consecutive_success/failures
- 每月 Rest mode 不超过 4 次（软性限制，超过时 Claude 提醒）

---

## 6. 逾期卡在低状态下的处理建议（MOOD-03）

### 6.1 研究依据

**逾期卡的风险：cascading failure（连锁失败）**

controlaltbackspace.org 的综合分析（基于 Anki 大量用户行为）：
- 跳过复习 → 卡片积压 → 数量过多产生心理压力 → 更倾向放弃 → 恶性循环
- 解决方案：**设置每日上限 + 分批处理**，而非统一推迟

**研究共识：**
- 部分延迟（延迟 2-3 天）的记忆损失 < 完全跳过的记忆损失
- 在疲劳状态下用降低的认知强度（Light mode）复习，比不复习效果好
- 但在极度疲劳状态下强行高强度复习可能有反效果（Johns Hopkins）

### 6.2 逾期卡处理规则（按状态）

**Full mode（状态好）：**
```
所有到期卡：正常全量处理
逾期 1-7 天：正常处理，评分照常
逾期 > 7 天：正常处理，但在评分时 Claude 提示"存在遗忘风险，以 fail 处理不惩罚你的 consecutive_failures"
→ 用户可选：按实际表现评分 / 视为 fail 重置间隔
```

**Light mode（状态一般）：**
```
逾期 ≤ 7 天：处理（Light 模式辅助检索）
逾期 8-14 天：处理（同上），但 suggested_interval_days 减半（不能用疲劳时的 ok 刷长间隔）
逾期 > 14 天：今天跳过，明天优先处理（不堆积超过 1 天）
当天到期卡数 > 5：最多处理 5 张，剩余推迟至明天
```

**Rest mode（状态差）：**
```
所有到期卡：统一 next_review += 2 天
不做检索，不更新 consecutive_success/failures
记录 mode: rest_day
```

### 6.3 逾期卡的关键规则（防止规则漏洞）

1. **Rest mode 下 next_review += 2 天 不算违反毕业条件**（不重置 consecutive 计数）
2. **Light mode 下的 ok 评分，间隔上限 = min(查表值, 上次间隔 × 1.3)**（防止用疲劳ok刷大间隔）
3. **连续 3 天 Rest mode**：触发 Claude 主动询问"是否需要调整系统参数或知识点难度"

---

## 7. 对规划的直接建议（What to Do）

### 7.1 Phase 7 执行建议

**Task 1：动态间隔规则文档（GRADUATE-01）**
- 在 `learning-behavior-system/` 下创建 `interval-rules.md`
- 内容：查表（consecutive_success → 间隔天数）+ good/ok/fail 的更新规则
- 不需要写代码，Claude 按规则文档手动计算

**Task 2：毕业规则文档（GRADUATE-02）**
- 补充进 `interval-rules.md`：毕业阈值 = consecutive_success ≥ 8 AND last_assessment.suggested_interval_days ≥ 30
- 毕业操作：status 改为 archived，不移动文件（archived 是状态值，不是目录）

**Task 3：退步规则文档（GRADUATE-03）**
- 补充进 `interval-rules.md`：连续失败 ≥ 3 → next_review = 明天（间隔1天）

**Task 4：YAML schema 扩展规范（SUBPOINT-01~03）**
- 更新 `SKILL.md` 中的 YAML 字段定义，追加 sub_points 和 review_sessions 字段
- 提供字段示例和更新规则说明

**Task 5：存量卡迁移（017~027）**
- 对 017-027 的 active 卡片，追加空的 sub_points 字段（status: ok 作为默认值）
- 不追加 review_sessions（历史会话不追溯）

**存量兼容性保证：**
- sub_points 是新增可选字段，旧卡片缺少该字段时 Claude 视为"sub_points 未定义"，按现有规则处理
- review_sessions 同理，缺少时视为空列表

### 7.2 Phase 8 执行建议

**Task 6：related_cards schema（GRAPH-01）**
- 更新 `SKILL.md`，追加 related_cards 字段定义（id + relation + note）
- 为 017-027 中已知强关联的卡对（如 017-EGL、021-024）补充 related_cards 字段

**Task 7：联合考察规则文档（GRAPH-02~03）**
- 在 `learning-behavior-system/` 下创建 `joint-review-rules.md`
- 内容：触发条件、考察流程、结果记录格式（joint_reviews 字段）
- 明确：joint review 不修改 last_assessment，不更新 consecutive_success

**Task 8：状态签到规则文档（MOOD-01~04）**
- 在 `learning-behavior-system/` 下创建 `state-checkin-rules.md`
- 内容：3 档状态定义、每档的复习方式、逾期卡处理规则、日志格式
- SKILL.md 中补充：复习会话开始时 Claude 应主动发起签到

**Task 9：复习日志 schema 扩展（MOOD-04）**
- `review_sessions` 字段增加 `mood` 记录：
  ```yaml
  review_sessions:
    - date: 2026-04-01
      mood: light          # full | light | rest
      covered_sub_points: [sp1, sp3]
      result: ok
  ```

### 7.3 关键决策点（需在 PLAN 中明确）

1. **ok 的间隔上限规则**：文档中必须写清楚 `ok 实际间隔 = min(查表值, 上次间隔 × 1.3)`，防止歧义
2. **archived 状态的目录**：archived 卡片留在 `active/` 目录还是移到 `mastered/`？建议：不移动文件，status 字段足够，减少文件操作
3. **sub_points 的初始化时机**：是在创建卡片时就定义好所有 sub_points，还是在第一次复习时补充？建议：创建卡片时先定义（学完后立刻知道有哪些子知识点）
4. **related_cards 的对称性**：如果 017 有 related_cards: [021]，是否要求 021 也有 related_cards: [017]？建议：要求对称（双向），避免图谱信息不完整

---

## Architecture Patterns

### 推荐的文件新增清单（Phase 7 + 8 的交付物）

```
learning-behavior-system/
├── SKILL.md                    # 修改：追加新字段定义
├── interval-rules.md           # 新增：动态间隔查表 + 毕业/退步规则
├── joint-review-rules.md       # 新增：跨卡联合考察规则
├── state-checkin-rules.md      # 新增：状态签到规则 + 复习方式映射
└── states/
    └── active/
        ├── 017-*.yaml          # 修改：追加 sub_points 字段
        ├── 018-*.yaml          # 修改：追加 sub_points 字段
        └── ...（017~027 所有 active 卡）
```

### YAML 字段全集（Phase 7 完成后的目标 Schema）

```yaml
# ——— 现有字段（不变）———
id: 017
title: OpenGL ES零拷贝图形管线
category: android
core: true
level: 2
review_stage: 0
status: active           # pool | active | archived（新增 archived）
last_study: 2026-03-27
next_review: 2026-03-30
importance: 5
created: 2026-03-18
stability_score: 54
consecutive_success: 5
consecutive_failures: 0
last_assessment:
  date: 2026-03-27
  result: ok             # fail | ok | good（保持简化三档）
  score: 3
  mode: qa
  weak_points:
    - "updateTexImage 本质描述不准确"
  suggested_interval_days: 7

# ——— 新增字段（Phase 7）———
sub_points:
  - id: sp1
    desc: "updateTexImage 本质（引用更新，非拷贝）"
    status: good         # weak | ok | good
    last_reviewed: 2026-03-27
  - id: sp2
    desc: "零拷贝完整数据流"
    status: ok
    last_reviewed: 2026-03-27

review_sessions:
  - date: 2026-03-27
    mood: full           # full | light | rest（Phase 8 添加）
    covered_sub_points: [sp1, sp2]
    result: ok

# ——— 新增字段（Phase 8）———
related_cards:
  - id: 021
    relation: prerequisite
    note: "双Surface架构前置"
  - id: 027
    relation: companion
    note: "EGL管理机制"

joint_reviews:
  - date: 2026-04-15
    partner_cards: [021, 027]
    topic: "零拷贝完整管线从Surface到SurfaceFlinger"
    result: ok
    weak_points: []

notes: |
  ...（原有 notes 内容不变）
```

---

## Don't Hand-Roll

| 问题 | 不要自建 | 直接用 | 原因 |
|------|---------|--------|------|
| 间隔调度算法 | 自己实现 EF 计算 | 查表（本文 2.2 节） | EF 需精确评分历史，手动系统无法维护 |
| Sub-point 独立调度 | 给每个 sub_point 设 next_review | 只追踪 status | 独立调度带来维护爆炸，且与模块级复习设计冲突 |
| 复杂签到 UI | 5 档情绪量表 | 3 档（Full/Light/Rest） | 3 档覆盖所有决策分支，5 档增加摩擦无收益 |
| 自动化脚本调度 | 写脚本驱动复习 | YAML next_review + Claude 读取 | 系统已有人工驱动流程，脚本增加复杂性 |

---

## Common Pitfalls

### Pitfall 1：ok 连击导致间隔虚高
**What goes wrong:** 用户连续 5 次 ok（表现平平），查表得到 21 天间隔，但实际上每次都勉强过，没有真正巩固
**Why it happens:** consecutive_success 不区分 good 和 ok
**How to avoid:** ok 的间隔上限 = min(查表值, 上次间隔 × 1.3)，单独写进 interval-rules.md
**Warning signs:** consecutive_success 很高但 score 始终 ≤ 3

### Pitfall 2：archived 后发现遗忘，无退出路径
**What goes wrong:** 卡片 archived 后，用户实际上忘了，但没有机制触发重新学习
**Why it happens:** archived 设计为终态，没有重新激活规则
**How to avoid:** 在规则文档中明确：用户可随时手动将 archived 卡的 status 改回 active，consecutive_success 重置为 0
**Warning signs:** archived 卡数量增多但用户感觉知识不扎实

### Pitfall 3：rest_day 成为逃避机制
**What goes wrong:** 用户每次不想复习就签到 rest，导致复习频率崩溃
**Why it happens:** rest_day 规则设计过于宽松
**How to avoid:** 软性限制：连续 2 天 rest → Claude 提醒；每月超过 4 次 rest → Claude 提醒
**Warning signs:** rest_day 频率上升，overdue 卡数量增加

### Pitfall 4：sub_points 定义过细导致维护成本高
**What goes wrong:** 一张卡有 15 个 sub_points，每次复习都要逐一更新
**Why it happens:** 没有对 sub_points 数量给出建议
**How to avoid:** 规则文档建议每张卡 sub_points ≤ 8，每个 sub_point 用一句话描述（不是完整知识）
**Warning signs:** 单张卡 sub_points > 10

### Pitfall 5：related_cards 不对称导致图谱信息丢失
**What goes wrong:** 017 有 related_cards: [021] 但 021 没有 related_cards: [017]，导致从 021 视角看不到关联
**Why it happens:** 单向更新
**How to avoid:** 规则文档要求 related_cards 双向维护，更新一方时同步更新另一方
**Warning signs:** related_cards 存在单向引用

---

## Validation Architecture

根据 config.json 中 `nyquist_validation: true`，需要说明验证架构。

**本 phase 的验证方式：**
本系统的交付物是 YAML 文件和 Markdown 文档，不是软件代码，无法运行自动测试。验证方式是**手动功能验证**：

| 需求 ID | 验证方式 | 验证命令 |
|---------|---------|---------|
| GRADUATE-01 | 打开 017 卡片，验证存在 suggested_interval_days 并符合查表规则 | 手动检查 |
| GRADUATE-02 | 构造 consecutive_success=8 + interval≥30 的卡片，验证 status=archived 规则触发 | 手动演练 |
| GRADUATE-03 | 构造 consecutive_failures=3 的卡片，验证 next_review=明天 规则触发 | 手动演练 |
| SUBPOINT-01 | 打开任意更新后的 active 卡，验证存在 sub_points 字段 | 手动检查 |
| SUBPOINT-02 | 进行一次复习会话，验证 review_sessions 追加记录，covered_sub_points 正确 | 手动演练 |
| SUBPOINT-03 | 跨两次会话，验证 sub_point.status 跨会话累计（未 covered 的不重置） | 手动演练 |
| GRAPH-01 | 打开 017/027 等卡片，验证 related_cards 字段存在且双向 | 手动检查 |
| GRAPH-02 | 触发一次联合考察，验证覆盖跨卡调用链 | 手动演练 |
| GRAPH-03 | 联合考察后，验证单卡 consecutive_success 未变化，joint_reviews 已追加 | 手动检查 |
| MOOD-01~04 | 进行带签到的复习会话，验证 review_sessions.mood 字段已记录 | 手动演练 |

---

## Environment Availability

Step 2.6: SKIPPED — 本 phase 是纯 YAML/Markdown 变更，无外部工具依赖。所有操作通过 Claude 对话完成。

---

## Open Questions

1. **archived 的目录归属**
   - 当前情况：states/ 下有 active/, mastered/, review/, pool/
   - 问题：archived 卡片放 active/ 还是新建 archived/ 目录？
   - 建议：status=archived 但文件留在 active/ 目录，避免文件移动操作复杂化。可在 PLAN 阶段确认。

2. **sub_points 初始化时机**
   - 当前情况：017-027 的卡片没有 sub_points 字段
   - 问题：是在迁移 task 中批量初始化，还是下次复习时逐卡补充？
   - 建议：Phase 7 中统一为存量卡补充 sub_points（从现有 weak_points 和 notes 中提取）

3. **间隔查表的 ok 上限系数（1.3）**
   - 当前状态：本文建议 1.3x 上限
   - 问题：实际使用后可能需要调整（过紧会让 ok 卡片总是短间隔，挫败感增加）
   - 建议：在 meta.md 中记录该参数，使用 1 个月后复盘调整

4. **联合考察的触发方式**
   - 当前情况：规则文档定义了触发条件，但触发是用户主动说"联合考察017和027"？还是 Claude 在日常任务中建议？
   - 建议：Claude 在每日任务生成时，如果发现两张相关卡都处于 active 且 consecutive_success ≥ 2，建议触发联合考察

---

## Sources

### Primary (HIGH confidence)
- SuperMemo 官方文档（通过 dev.to 技术博客交叉验证）— SM-2 完整公式
- Anki 官方手册 docs.ankiweb.net — leech 机制、graduating interval
- PMC 8893218（2022 meta-analysis）— 睡眠剥夺对记忆的效应量

### Secondary (MEDIUM confidence)
- RemNote FSRS 文档 — FSRS vs SM-2 对比
- npj Science of Learning 2021 — interleaved practice 物理学习研究（+50%/+125%）
- Frontiers in Psychology 2023 — 交错 vs 分块，2周延迟测试结果
- Johns Hopkins Medicine 2019 — 过度训练后的学习能力损伤
- controlaltbackspace.org — 逾期卡处理实践指南（基于 Anki 用户行为）

### Tertiary (LOW confidence — needs validation in practice)
- Duolingo 习惯养成设计原则 — 降低摩擦的重要性
- Language Learning 2025 — 初学者先分块再交错的建议（发表时间最近，需观察复现）

---

## Metadata

**Confidence breakdown:**
- SM-2 算法公式: HIGH — 原始文档多源交叉验证
- 动态间隔查表设计: MEDIUM — 基于 SM-2 推导，实际参数需使用后校准
- Sub-points schema: HIGH — 基于本系统设计约束的直接推导，不依赖外部验证
- 跨卡联合考察: MEDIUM — 交错学习研究支持，但触发参数需实践验证
- 状态签到映射: MEDIUM — 认知科学基础扎实，具体档位划分是工程判断
- 逾期卡处理: MEDIUM — 研究方向明确（不完全跳过），具体规则是设计选择

**Research date:** 2026-03-31
**Valid until:** 2026-09-30（认知科学部分稳定；SM-2/FSRS 算法稳定）
