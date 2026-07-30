# 阶段二 · Stage/Task下钻与场景复现

> 回答：线上怎样缩小范围；线下怎样稳定触发风险路径。
> 事实源：[[../ARouter启动优化笔记#0.3 灰度沿 Stage/Task 定位]]

## 线上下钻

```text
startup.total
└── startup.stage.app_init
    └── startup.task.arouter.init
```

- Stage说明增量集中在应用初始化阶段。
- Task说明本次横向增量主要来自ARouter。
- Stage/Task负责缩小调查范围，不能单独证明内部一定走Dex扫描。

## 为什么旧防线漏网

ARouter运行时Dex扫描会把生成类名集合写入SP：

```text
首次安装/版本升级后的第一次启动：缓存失效，执行Dex扫描
后续启动：命中缓存，不再完整扫描
```

若CI复用应用数据、把首轮当warm-up、只看多轮中位数，7～8s首启劣化会被后续正常样本掩盖。

## 线下复现场景

- 代表性低端机；
- 固定构建类型、入口、账号和数据；
- clean install first launch；
- upgrade first launch；
- cache-hit cold start单独统计。

本地区间称“业务可控冷启动区间”，不强称标准TTFD：

```text
Application.attachBaseContext → 首页可见
```

## 复习检查

1. Stage与Task分别证明什么？
2. 为什么中位数会隐藏本次问题？
3. 三种启动场景为什么必须分开？
4. 为什么不把本地区间绝对值等同线上P90？
