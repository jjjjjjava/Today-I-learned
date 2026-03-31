# 用户操作协议（详细版）

SKILL.md 的补充参考文档。AI 在执行具体操作时按此文档执行。

---

## 1. 新增知识点

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
4. 用户确认或修改
5. 创建文件 `states/active/005-Jetpack-Compose状态管理.yaml`（新卡直接进 active）：
   ```yaml
   id: 005
   title: Jetpack Compose 状态管理
   category: android
   core: true
   level: 1
   review_stage: 0
   status: active
   last_study: {今日日期}
   next_review: {今日日期 + 3天}
   importance: 4
   created: {今日日期}
   stability_score: 60
   consecutive_success: 0
   consecutive_failures: 0
   last_assessment:
     date: {今日日期}
     result: ok
     score: 3
     mode: study
     weak_points: []
     suggested_interval_days: 3
   notes: ""
   related_cards: []
   sub_points: []
   review_sessions: []
   ```
6. 告知用户：
   ```
   已创建 states/active/005-Jetpack-Compose状态管理.yaml
   - id: 005, category: android, importance: 4, core: true
   - next_review: {日期}（3天后首次复习）
   ```

---

## 1.1 新增项目

**用户输入**：
```
新增项目：视频加水印项目
```

**AI 执行流程**：

1. 扫描序号，确认 category: project
2. 询问项目代码路径
3. 创建文件 `states/active/006-视频加水印项目.yaml`（project 类型）
4. 创建项目笔记目录 `notes/006-视频加水印项目/` 和 state.yaml
5. 告知用户，提示可以说"开始学习视频加水印项目"触发 project-interview-prep skill

---

## 2. 提升 Level

**用户输入**：
```
Android生命周期 提升到 level 3
```

**AI 执行流程**：

1. **检验**：要求用户口述，追问 2-3 个细节
2. **判断达标**：给出 `good / ok / fail` + score
3. **更新文件**：
   ```yaml
   level: 3
   last_study: {今日}
   last_assessment:
     date: {今日}
     result: good    # good | ok | fail
     score: 4
     mode: qa
     weak_points: []
     suggested_interval_days: {按 interval-rules.md 计算}
   next_review: {按 interval-rules.md 计算}
   ```
4. **状态转移**：level 变成 4 → 移动文件到 states/review/，review_stage 重置为 0
5. **明确告知**变更内容

---

## 3. 完成复习

**用户输入**：
```
Android生命周期 仅复习
```

**AI 执行流程**：

1. 读取状态文件，判断类型（知识点 or 项目）
2. **执行考核**：1 个主问题 + 2-3 个追问，给出 `good / ok / fail` + score
3. **更新字段**（按 [interval-rules.md](interval-rules.md) 计算 next_review）：
   ```yaml
   last_study: {今日}
   consecutive_success: +1（result: good/ok）或 重置为 0（result: fail）
   consecutive_failures: +1（result: fail）或 重置为 0（result: good/ok）
   last_assessment:
     date: {今日}
     result: good    # good | ok | fail
     score: 4
     mode: qa
     weak_points: [...]
     suggested_interval_days: {计算值}
   next_review: {计算值}
   ```
4. **追加 review_sessions 记录**（如有 sub_points）
5. **判断状态转移**：
   - `consecutive_success ≥ 8` 且间隔 ≥ 30 天 → `status: archived`（毕业，文件留原位）
   - `consecutive_failures ≥ 3` → 间隔重置为 1 天
   - level=4 且 review_stage≥4 且 consecutive_success≥3 且 stability_score≥85 → 移至 mastered/
6. **明确告知**结果和 next_review

---

## 4. 批量更新

按顺序处理每个操作，遵循各自流程。

---

## 5. sub_points 更新规则

复习时如有 sub_points：
- 本次覆盖到的 sub_point：根据表现更新状态（good/ok/fail → weak/ok/good）
- 未覆盖的 sub_point：状态不变
- 在 review_sessions 追加一条记录

详细规则见 [sub-points-rules.md](sub-points-rules.md)。
