# Milestone v1.1 Requirements — 学习系统基建改造

## 毕业与间隔机制（GRADUATE）

- [x] **GRADUATE-01**: 系统根据 consecutive_success 自动拉长 next_review 间隔，不使用固定 level 映射
- [x] **GRADUATE-02**: 卡片达到毕业阈值（consecutive_success ≥ N，间隔 ≥ X 天）后自动移入 archived 状态
- [x] **GRADUATE-03**: 表现差时（consecutive_failures ≥ 阈值）自动缩短间隔，拉回高频复习

## 子知识点追踪（SUBPOINT）

- [x] **SUBPOINT-01**: YAML 卡片支持 sub_points 字段，列出该卡的独立子知识点
- [x] **SUBPOINT-02**: 每次复习记录本次覆盖了哪些 sub_points，未覆盖的保留待下次
- [x] **SUBPOINT-03**: sub_points 有独立的 weak/ok/good 状态，跨多次复习累计追踪

## 跨卡知识图谱（GRAPH）

- [x] **GRAPH-01**: 卡片支持 related_cards 字段，记录强关联的其他卡片 ID
- [x] **GRAPH-02**: 定期触发跨卡联合考察，考察跨多张卡的完整调用链
- [x] **GRAPH-03**: 联合考察结果独立记录，不影响单卡的 consecutive_success

## 状态签到与自适应复习（MOOD）

- [x] **MOOD-01**: 每次复习会话开始前有简短状态签到环节，用户选择当前学习状态
- [x] **MOOD-02**: 状态与复习方式的映射基于认知科学/SRS 研究，有调研依据（不拍脑袋）
- [x] **MOOD-03**: 状态差时，逾期卡的处理策略有明确规则（不由用户临场决定）
- [x] **MOOD-04**: 签到状态记录在当次复习日志中，供后续趋势分析

## GSD 新学习工作流（WORKFLOW）

- [x] **WORKFLOW-01**: 定义标准工作流文档：新学习模块如何走 GSD milestone → phase → 交付 YAML card
- [x] **WORKFLOW-02**: 学习完成时，YAML card 作为 phase 的交付物，存入 active pool

## Future Requirements

- 卡片热度地图可视化（哪些卡长期没被联合考察到）
- 基于错误模式的自动推荐（频繁出错的 sub_point 优先出题）

## Out of Scope

- GSD 管理每日复习调度 — 存量复习由 YAML next_review 驱动，GSD 不介入
- 替换现有 YAML 结构 — 改造是在现有结构上扩展字段，不是重建

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GRADUATE-01 | Phase 7 | Complete (07-01) |
| GRADUATE-02 | Phase 7 | Complete (07-01) |
| GRADUATE-03 | Phase 7 | Complete (07-01) |
| SUBPOINT-01 | Phase 7 | Complete (07-01) |
| SUBPOINT-02 | Phase 7 | Complete (07-01) |
| SUBPOINT-03 | Phase 7 | Complete (07-01) |
| GRAPH-01 | Phase 8 | Complete |
| GRAPH-02 | Phase 8 | Complete |
| GRAPH-03 | Phase 8 | Complete |
| MOOD-01 | Phase 8 | Complete |
| MOOD-02 | Phase 8 | Complete |
| MOOD-03 | Phase 8 | Complete |
| MOOD-04 | Phase 8 | Complete |
| WORKFLOW-01 | Phase 9 | Complete |
| WORKFLOW-02 | Phase 9 | Complete |
