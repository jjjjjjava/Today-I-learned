# 跨卡知识图谱规则 v1.1

## related_cards 字段

### Schema

```yaml
related_cards: [id1, id2, id3]   # 强关联的其他卡片 ID 列表，整数
```

**强关联的定义**：两张卡片在面试中经常被连续追问，或其中一张的原理依赖另一张（调用链/实现依赖/概念依赖）。

**添加规则**：
- 双向添加：A → B 则 B → A
- 每张卡最多列 4 个强关联（避免图谱过于发散）
- 同组内的卡片不必两两互联，优先列最强的 2-3 个

---

## 联合考察规则（GRAPH-02 / GRAPH-03）

### 触发条件

满足以下**任意一条**时，AI 可发起联合考察：

1. 当日任务中包含 2 张以上互为 related_cards 的卡片
2. 用户明确要求："联合考察 / 跨卡考察 / 串讲 xxx 和 yyy"
3. 某张卡 consecutive_success ≥ 5，且其 related_cards 中有卡片 consecutive_success < 3（强弱关联触发补强）

### 联合考察执行

1. AI 出一道跨卡问题，要求覆盖 2-3 张卡的完整调用链
2. 示例问题形式：
   - "从 MediaCodec 解码一帧 YUV，到 OpenGL 渲染到屏幕，完整链路是什么？"（涉及 009 + 017/018/021/027）
   - "音视频同步的基准时钟选择如何影响解码器缓冲策略？"（涉及 010 + 011 + 009）
3. 用户回答后，AI 根据覆盖情况评分：good / ok / fail

### 独立记录规则（GRAPH-03）

**联合考察结果写入 `joint-review-log.md`，不修改任何单卡的 consecutive_success / next_review。**

单卡的 consecutive_success 只由该卡单独被考察时的结果更新。

---

## MOOD 状态签到规则（MOOD-01 ~ MOOD-04）

### 签到时机（MOOD-01）

每次复习会话开始时，AI 先问：

```
今天状态怎么样？
  A. 状态好，正常推进
  B. 一般，轻量复习
  C. 很累，只想做最少的
```

### 状态与复习策略映射（MOOD-02）

基于 SM-2 / 认知负荷理论：大脑在疲劳状态下编码效率低，强行推进高难度内容反而加深错误记忆。

| 状态 | 策略 |
|------|------|
| A（好） | 正常调度，优先 next_review 到期的卡，可触发联合考察 |
| B（一般） | 缩减至 3-5 张，优先 core: true 的卡，跳过联合考察 |
| C（累） | 只做 1-2 张最高优先级卡（逾期最久 + core: true），以"快速过一遍"代替深度考察 |

### 逾期卡的状态差处理规则（MOOD-03）

当状态为 B 或 C，且存在逾期卡时：

- **不跳过逾期卡**：逾期卡必须至少"接触一次"（哪怕只是用户翻看答案）
- **降低考察强度**：允许用户"自评"代替 AI 出题，结果可填 ok 但不填 good
- **不强制推进**：不在状态差时触发联合考察或新知识点学习

### 签到记录格式（MOOD-04）

```yaml
# 在 joint-review-log.md 的当日 session 中记录
mood: B   # A / B / C
```

每次 review_session 的 YAML 记录中**不加** mood 字段（避免污染单卡数据）；mood 仅记录在 joint-review-log.md。

---

## 关联目录

- [sub-points-rules.md](sub-points-rules.md) — 子知识点追踪规则
- [interval-rules.md](interval-rules.md) — 动态间隔与毕业机制
- [joint-review-log.md](joint-review-log.md) — 联合考察独立日志
