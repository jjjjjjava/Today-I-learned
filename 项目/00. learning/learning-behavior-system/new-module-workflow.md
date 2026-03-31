# 新模块学习标准工作流 v1.2

学习一个新技术模块时，从立项到交付 YAML card 进入 active pool 的完整步骤。

> **工具**：用 planning-with-files-zh 驱动整个流程，收尾用 `/gsd:note` 留档。

---

## 全局流程

```
task_plan.md 立项 → 学习 → 笔记 → 拆卡 → 校验 → 入池 → /gsd:note 收尾
```

---

## 第一层：立项（task_plan.md）

在项目根目录创建 `task_plan.md`（已有则更新），为本次学习模块新增一个任务块：

```markdown
# Task Plan — 学习模块：{模块名}

## 目标
{一句话：学完后能做到什么，面试场景下能回答什么}

## 交付物
- [ ] 原始笔记：`04. 学习_*/{模块名}.md`
- [ ] YAML cards：{预计数量} 张，放入 states/active/
- [ ] 知识点清单：{N} 个

## 阶段

| # | 任务 | 状态 |
|---|------|------|
| 1 | 读材料，写原始笔记 | pending |
| 2 | 知识点拆解 + sub_points 设计 | pending |
| 3 | 创建 YAML cards | pending |
| 4 | 校验 + 入池 | pending |
| 5 | /gsd:note 收尾 | pending |

## 遇到的错误
（暂无）
```

同时在 `progress.md` 新增一个会话条目：
```markdown
## Session {N} — {日期} — 模块：{模块名}
- 开始学习
```

---

## 第二层：学习执行

### Step 1: 读材料，写原始笔记

- 将原始笔记放在 `04. 学习_*/` 对应目录下
- 格式参考 `00.标准化/02. study文件模板.md`
- 笔记不要求完美，先覆盖全部内容
- 完成后：task_plan.md 中 Task 1 → `complete`

### Step 2: 知识点拆解

阅读完成后，列出该模块的**独立知识点列表**，写入 `task_plan.md`：

```markdown
## 知识点清单

| ID | 知识点 | sub_points 数 |
|----|--------|--------------|
| 1 | EGL 初始化完整流程（6步） | 4 |
| 2 | EGLContext 共享机制 | 3 |
| 3 | SurfaceView vs TextureView 核心差异 | 4 |
```

规则：
- 每个知识点：能被单独考察、有独立答题思路
- 一般一个模块 3-8 个知识点
- 每个知识点对应一张 YAML card

### Step 3: 为每个知识点设计 sub_points

在 `task_plan.md` 的知识点清单里为每条知识点列出 3-8 个子知识点（先在文件里设计，再写入 YAML）。

完成后：task_plan.md 中 Task 2 → `complete`

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
next_review: {last_study + 3天}
importance: {1-5}
created: {YYYY-MM-DD}
stability_score: 60
consecutive_success: 0
consecutive_failures: 0
last_assessment:
  date: {last_study}
  result: ok                # 新卡默认 ok（刚学，还不稳定）
  score: 3
  mode: study
  weak_points: []
  suggested_interval_days: 3
notes: {一行摘要，覆盖核心考点}
related_cards: []           # 参考现有卡片的分组关系填写
sub_points:
  - id: sp1
    desc: "{子知识点描述}"
    status: ok
    last_reviewed: {last_study}
  # ... 最多 8 个

review_sessions:
  - date: {last_study}
    covered_sub_points: [sp1, sp2, ...]
    result: ok
    score: 3
```

完成后：task_plan.md 中 Task 3 → `complete`

### Step 5: 校验清单

- [ ] `id` 唯一，不与已有卡片冲突（扫描 states/ 目录确认）
- [ ] `next_review` 已设置（不为空）
- [ ] `sub_points` 至少 3 个，最多 8 个
- [ ] `related_cards` 已参考现有卡片分组（可为空列表）
- [ ] `status: active`（确认进入复习队列）
- [ ] 文件放在 `states/active/` 目录

完成后：task_plan.md 中 Task 4 → `complete`

---

## 第四层：收尾

### Step 6: 更新 task_plan.md

所有任务标记 complete，记录产出：
```markdown
## 产出
- 原始笔记：`04. 学习_*/{模块名}.md`
- YAML cards：{实际创建数量} 张（id {起始}-{结束}）
- 入池时间：{日期}
```

### Step 7: /gsd:note 留档

运行：
```
/gsd:note
```

内容格式：
```
学习完成：{模块名}
- 产出 {N} 张 YAML card（id {起始}-{结束}）进入 active pool
- 核心知识点：{列举 2-3 个}
- 薄弱点：{首次学习时的薄弱 sub_points}
- next_review 最早：{最近一张卡的 next_review 日期}
```

---

## 快速参考

| 动作 | 位置 |
|------|------|
| 立项/追踪 | `task_plan.md`（项目根目录） |
| 会话日志 | `progress.md` |
| 原始笔记 | `04. 学习_*/` |
| YAML card | `states/active/` |
| 间隔规则 | `interval-rules.md` |
| 子知识点规则 | `sub-points-rules.md` |
| 联合考察规则 | `graph-rules.md` |
| 联合考察日志 | `joint-review-log.md` |
