# Sub-points 子知识点追踪规则

## 设计原则

- sub_points 是卡片内的静态知识点列表，不独立调度（卡片仍是最小调度单位）
- 每张卡片最多 8 个 sub_points
- 没有 sub_points 字段的卡片按现有规则处理，向后兼容
- sub_points 的状态跨复习会话累计追踪，不自动重置

---

## sub_points 字段 Schema

```yaml
sub_points:
  - id: sp1                          # 短 ID，在 review_sessions 中引用
    desc: "知识点描述"                 # 人类可读描述
    status: weak                     # weak | ok | good（跨会话累计）
    last_reviewed: 2026-03-27        # 上次复习此 sub_point 的日期
```

字段规则：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 格式 sp1, sp2, ... sp8，卡片内唯一 |
| desc | string | 子知识点的一句话描述 |
| status | enum | weak / ok / good，初始值为 weak |
| last_reviewed | date | 格式 YYYY-MM-DD，该 sub_point 上次被覆盖的日期 |

---

## review_sessions 字段 Schema

```yaml
review_sessions:
  - date: 2026-03-27
    covered_sub_points: [sp1, sp2]   # 本次覆盖的 sub_point id 列表
    result: ok                       # 本次整体结果
    score: 3                         # 本次整体评分
```

字段规则：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | date | 复习日期 |
| covered_sub_points | list | 本次覆盖的 sub_point id 列表 |
| result | enum | fail / ok / good（本次整体结果） |
| score | int | 1-5 评分 |

规则：
- review_sessions 是 append-only 日志，只追加不修改历史记录
- 每次复习生成一条记录
- covered_sub_points 列出本次实际考察到的 sub_point id

---

## sub_point 状态更新规则

```
每次复习后，对每个 sub_point 执行以下判断：

情况 A — 本次 covered（出现在 covered_sub_points 列表中）：
  整体 result = good → sub_point.status 升至 good
  整体 result = ok   → sub_point.status 至少升至 ok（如果原来是 weak 则升为 ok，如果已经是 good 则保持 good）
  整体 result = fail → sub_point.status 降至 weak
  更新 sub_point.last_reviewed 为本次日期

情况 B — 本次未 covered（不在 covered_sub_points 列表中）：
  sub_point.status 不变（保留上次状态）
  sub_point.last_reviewed 不变
  → 这是核心设计：未覆盖不等于遗忘，状态保持
```

---

## 向后兼容

- 没有 sub_points 字段的卡片：按现有规则处理，不报错
- 没有 review_sessions 字段的卡片：正常复习，只是没有会话级追踪
- 迁移方式：逐步为卡片添加 sub_points，不需要一次性全部迁移

---

## 完整示例 — Card 017 OpenGL ES 零拷贝图形管线

```yaml
sub_points:
  - id: sp1
    desc: "BufferQueue 三缓冲机制（producer/consumer + 3 个 GraphicBuffer）"
    status: good
    last_reviewed: 2026-03-27
  - id: sp2
    desc: "updateTexImage 本质（引用更新非拷贝，在 GL 线程调用）"
    status: ok
    last_reviewed: 2026-03-27
  - id: sp3
    desc: "EGLImage 绑定机制（eglCreateImageKHR → glEGLImageTargetTexture2DOES）"
    status: weak
    last_reviewed: 2026-03-20
  - id: sp4
    desc: "GL_TEXTURE_EXTERNAL_OES vs GL_TEXTURE_2D（外部纹理 = 引用不拥有）"
    status: ok
    last_reviewed: 2026-03-27
  - id: sp5
    desc: "完整数据流：MediaCodec → GraphicBuffer → BufferQueue → SurfaceTexture → GPU"
    status: good
    last_reviewed: 2026-03-27

review_sessions:
  - date: 2026-03-27
    covered_sub_points: [sp1, sp2, sp4, sp5]
    result: ok
    score: 3
```

状态更新演算：
- sp1 covered + result ok → status stays good（already good，ok 不降级已达 good 的 sub_point）
- sp2 covered + result ok → status stays ok（已是 ok，保持）
- sp3 NOT covered → status stays weak（未覆盖不等于遗忘，状态保持）
- sp4 covered + result ok → status stays ok（已是 ok，保持）
- sp5 covered + result ok → status stays good（already good，ok 不降级）
