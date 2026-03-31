# 联合考察独立日志

记录跨卡联合考察会话。本文件的结果**不影响**任何单卡的 `consecutive_success` 或 `next_review`。

---

## 日志格式

```yaml
- date: YYYY-MM-DD
  mood: A              # A / B / C（来自当日状态签到）
  cards: [009, 017, 021, 027]
  question: "从 MediaCodec 解码一帧 YUV，到 OpenGL 渲染到屏幕，完整链路是什么？"
  result: ok           # good / ok / fail
  score: 3             # 1-5
  weak_links:
    - "EGL Surface 与 SurfaceTexture 的关系讲不清楚"
  notes: ""
```

### 字段说明

| 字段 | 含义 |
|------|------|
| date | 考察日期 |
| mood | 当日状态签到（A好/B一般/C累） |
| cards | 涉及的卡片 ID 列表 |
| question | AI 出的跨卡问题 |
| result | good/ok/fail |
| score | 1-5 主观评分 |
| weak_links | 跨卡衔接点中答得薄弱的环节 |
| notes | 补充备注 |

---

## 记录

<!-- 联合考察会话按时间顺序追加在此处 -->
