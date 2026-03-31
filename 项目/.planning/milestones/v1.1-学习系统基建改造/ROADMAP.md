# Milestone v1.1 Roadmap — 学习系统基建改造

**Milestone goal:** 通过扩展 YAML schema、定义跨卡图谱验证规则、建立 GSD 新学习工作流，将现有学习系统从"单卡静态间隔"升级为"动态毕业间隔 + 子知识点追踪 + 跨卡联合考察"的完整闭环。

**Phases continue from main ROADMAP.md (Phases 1-6).**

---

## Phases

- [ ] **Phase 7: YAML Schema Extension** — 扩展卡片 YAML 字段：动态间隔/毕业/退步规则 + sub_points 子知识点追踪
- [ ] **Phase 8: Cross-Card Graph Validation** — 扩展 related_cards 字段，定义跨卡联合考察规则与独立计分
- [ ] **Phase 9: GSD Learning Workflow** — 定义新学习模块标准工作流文档，将 YAML card 作为 phase 交付物

---

## Phase Details

### Phase 7: YAML Schema Extension
**Goal**: 每张卡片的 YAML 头部能完整表达动态间隔状态和子知识点追踪，存量卡可按新 schema 迁移
**Depends on**: Nothing (first phase of this milestone)
**Requirements**: GRADUATE-01, GRADUATE-02, GRADUATE-03, SUBPOINT-01, SUBPOINT-02, SUBPOINT-03
**Success Criteria** (what must be TRUE):
  1. 打开任意一张 YAML 卡片，能看到 `consecutive_success`、`consecutive_failures`、`next_review` 字段，以及按 consecutive_success 计算的动态间隔规则注释
  2. 一张卡片的 consecutive_success 达到毕业阈值后，其 `status` 字段变为 `archived`，不再出现在每日复习队列
  3. 一张卡片的 consecutive_failures 达到退步阈值后，其 `next_review` 被重置为短间隔（如 1 天内），重新进入高频复习
  4. 任意一张卡片包含 `sub_points` 字段，每个子知识点有独立的 `weak/ok/good` 状态，跨复习会话累计更新而不重置
**Plans:** 3 plans

Plans:
- [ ] 07-01-PLAN.md — 创建动态间隔规则文档和子知识点追踪规则文档
- [ ] 07-02-PLAN.md — 为第一批 7 张卡片（009-019）添加 sub_points/review_sessions + 更新 SKILL.md
- [ ] 07-03-PLAN.md — 为第二批 8 张卡片（020-027）添加 sub_points/review_sessions

### Phase 8: Cross-Card Graph Validation + 状态签到
**Goal**: 卡片强关联显式记录 + 联合考察独立计分 + 基于调研的状态签到与自适应复习方式
**Depends on**: Phase 7
**Requirements**: GRAPH-01, GRAPH-02, GRAPH-03, MOOD-01, MOOD-02, MOOD-03, MOOD-04
**Success Criteria** (what must be TRUE):
  1. 打开任意一张卡片，能看到 `related_cards` 字段，值为其他卡片 ID 列表，语义明确
  2. 触发联合考察时，考察内容覆盖跨卡完整调用链，结果独立记录，单卡 consecutive_success 不变
  3. 复习会话开始前有状态签到，状态→复习方式映射有认知科学依据
  4. 状态差时逾期卡的处理规则明确，无需用户临场决定
**Plans**: TBD

### Phase 9: GSD Learning Workflow
**Goal**: 学习一个新模块时有标准文档可遵循，完成后 YAML card 自动进入 active pool，学习成果不会遗漏
**Depends on**: Phase 7, Phase 8 (工作流文档引用已稳定的 schema 定义)
**Requirements**: WORKFLOW-01, WORKFLOW-02
**Success Criteria** (what must be TRUE):
  1. 存在一份标准工作流文档，描述新模块从 GSD milestone 立项 → phase 分解 → 学习执行 → 交付 YAML card 的完整步骤，不需要凭记忆操作
  2. 按照工作流文档完成一次新模块学习后，产出的 YAML card 出现在 active pool，下次运行复习脚本时该卡出现在队列中
**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 7. YAML Schema Extension | 0/3 | Planned | - |
| 8. Cross-Card Graph Validation | 0/? | Not started | - |
| 9. GSD Learning Workflow | 0/? | Not started | - |
