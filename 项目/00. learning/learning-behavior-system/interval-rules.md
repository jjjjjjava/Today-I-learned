# 动态间隔与毕业/退步规则

## 动态间隔查表

| consecutive_success | 建议间隔（天） |
|---------------------|---------------|
| 0 | 1 |
| 1 | 2 |
| 2 | 4 |
| 3 | 7 |
| 4 | 14 |
| 5 | 21 |
| 6 | 30 |
| 7 | 45 |
| 8 | 60 |
| 9+ | 90 |

增长率约 1.4-1.7x，比 SM-2 的 2.5x EF 保守，适合手动复习系统。

---

## 按 result 分类的间隔计算规则

### result: good

- `consecutive_success += 1`
- `consecutive_failures = 0`（good 重置失败计数）
- `suggested_interval_days` = 查表值（按新的 consecutive_success 查上面的表）

### result: ok

- `consecutive_success += 1`（ok 等同 success，已有 memory 规则）
- `consecutive_failures = 0`
- `suggested_interval_days` = `min(查表值, 上次间隔 × 1.3)`
- 解释：ok 表示通过但有瑕疵，间隔增长受限，防止 ok 连击过快拉长间隔

### result: fail

- `consecutive_failures += 1`
- `consecutive_success` 不变（独立累计，已有 memory 规则）
- `suggested_interval_days = 1`（强制明天复习）

---

## 毕业规则（GRADUATE-02）

```
毕业条件：consecutive_success >= 8 AND 上次实际间隔 >= 30 天
```

毕业后行为：
- `status` 从 `active` 改为 `archived`
- 文件保留在 `states/active/` 目录不移动
- 不再出现在每日复习队列
- 如需重新激活：手动将 `status` 改回 `active`，重置 `consecutive_success` 为 0

---

## 退步规则（GRADUATE-03）

```
退步条件：consecutive_failures >= 3（连续 3 次失败）
```

退步后行为：
- `next_review` = 明天（强制 1 天间隔）
- `consecutive_success` 不重置（保留历史累计）
- `consecutive_failures` 继续累计（不重置）
- 在 `last_assessment.weak_points` 中标注退步触发

本系统使用连续失败计数（consecutive），比 Anki 的累计失败计数（cumulative）信号更强，因此阈值设为 3 而非 Anki 默认的 8。

---

## 示例

### 示例 1 — Card 009（consecutive_success=6，result=good）

```
当前 consecutive_success: 6
本次 result: good
→ consecutive_success: 7
→ 查表: 7 → 45 天
→ suggested_interval_days: 45
→ next_review: today + 45 天
```

### 示例 2 — Card 027（consecutive_success=1，result=ok，上次间隔=2天）

```
当前 consecutive_success: 1
本次 result: ok
→ consecutive_success: 2
→ 查表: 2 → 4 天
→ ok 上限: min(4, 2 × 1.3) = min(4, 2.6) = 2.6 → 取整 3 天
→ suggested_interval_days: 3
→ next_review: today + 3 天
```
