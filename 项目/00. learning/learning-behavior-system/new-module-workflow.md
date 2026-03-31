# 新模块学习标准工作流 v1.1

学习一个新技术模块时，从立项到交付 YAML card 进入 active pool 的完整步骤。

---

## 全局流程

```
立项 → 学习 → 笔记 → 拆卡 → 校验 → 入池
```

---

## 第一层：立项决策

### 何时创建新 GSD phase

满足以下**任意一条**时，在当前 milestone 下创建一个新 phase：

- 要学的模块有 ≥ 3 个独立知识点，每个知识点预计笔记 > 300 字
- 该模块与现有 phase 之间有明确依赖关系（如：学 EGL 前需要先掌握 OpenGL 渲染管线）
- 面试中这个模块会被单独考察（不是附属于其他话题的小知识点）

### 立项内容

在 GSD ROADMAP.md 中添加 phase，填写：

```markdown
### Phase N: {模块名}

**Goal:** {一句话：学完后能做到什么，面试场景下能回答什么}

**Plans:** TBD

**Requirements:** {需求 ID 列表}

**Success Criteria:**
- [ ] {可观测的验证标准，参考面试追问场景}

**Dependencies:** {依赖哪些前置 phase}
```

---

## 第二层：学习执行

### Step 1: 读材料，写原始笔记

- 将原始笔记放在 `04. 学习_*/` 对应目录下
- 格式参考 `00.标准化/02. study文件模板.md`
- 笔记不要求完美，先覆盖全部内容

### Step 2: 知识点拆解

阅读完成后，列出该模块的**独立知识点列表**：

- 每个知识点：能被单独考察、有独立答题思路
- 一般一个模块 3-8 个知识点
- 每个知识点对应一张 YAML card

**示例（OpenGL EGL 模块）：**

```
- EGL 初始化完整流程（6步）
- EGLContext 共享机制
- SurfaceView vs TextureView 核心差异
- MediaCodec + OpenGL 联动链路
```

### Step 3: 为每个知识点写 sub_points

在创建 YAML card 之前，为每个知识点列出 3-8 个子知识点：

- 能独立被追问
- 有 weak/ok/good 可区分的掌握程度

---

## 第三层：创建 YAML card 并入池

### Step 4: 创建 YAML card

文件命名：`{id}-{title}.yaml`，放入 `states/active/`。

**完整 card 模板：**

```yaml
id: {3位数字，如 028}
title: {知识点名称，简洁}
category: android           # android / project / cross-platform
core: true                  # 面试核心知识点填 true
level: 1                    # 新卡从 1 开始
review_stage: 0
status: active
last_study: {YYYY-MM-DD}    # 首次学习日期
next_review: {last_study + 3天}  # 新卡默认 3 天后第一次复习
importance: {1-5}           # 面试重要度
created: {YYYY-MM-DD}
stability_score: 60         # 新卡默认 60
consecutive_success: 0
consecutive_failures: 0
last_assessment:
  date: {last_study}
  result: good              # 刚学完默认 good
  score: 3
  mode: study               # study / qa / joint
  weak_points: []
  suggested_interval_days: 3
notes: {一行摘要，覆盖核心考点}
related_cards: []           # 参考现有卡片的分组关系填写
sub_points:
  - id: sp1
    desc: "{子知识点描述}"
    status: ok              # 新卡默认 ok（刚学，还不稳定）
    last_reviewed: {last_study}
  # ... 最多 8 个

review_sessions:
  - date: {last_study}
    covered_sub_points: [sp1, sp2, ...]  # 首次学习覆盖所有
    result: good
    score: 3
```

### Step 5: 校验清单

创建 YAML card 后，逐项检查：

- [ ] `id` 唯一，不与已有卡片冲突
- [ ] `next_review` 已设置（不为空）
- [ ] `sub_points` 至少 3 个，最多 8 个
- [ ] `related_cards` 已参考现有卡片分组填写（可为空列表）
- [ ] `status: active`（确认放入 active pool）
- [ ] 文件名格式正确：`{id}-{title}.yaml`，放在 `states/active/` 目录

### Step 6: 更新 GSD ROADMAP

在当前 phase 的 Success Criteria 中打勾，并更新 ROADMAP 状态：

```markdown
**Plans:** {N} cards created

**Success Criteria:**
- [x] {验证标准}

**Completed:** {YYYY-MM-DD}
```

### Step 7: 更新 SKILL.md meta.md（可选）

如果新模块属于一个全新分类（如首次添加 Flutter 相关卡片），更新 `meta.md` 中的卡片总数和分类。

---

## 快速参考

| 动作 | 位置 |
|------|------|
| 原始笔记 | `04. 学习_*/` |
| YAML card | `00. learning/learning-behavior-system/states/active/` |
| 间隔规则 | `interval-rules.md` |
| 子知识点规则 | `sub-points-rules.md` |
| 联合考察规则 | `graph-rules.md` |
| 联合考察日志 | `joint-review-log.md` |
