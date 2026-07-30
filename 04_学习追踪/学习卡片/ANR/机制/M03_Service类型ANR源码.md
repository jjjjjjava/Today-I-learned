---
type: learning-card
id: ANR机制_M03_Service类型ANR源码
主题: ANR/机制/Service源码
创建日期: 2026-07-30
上次复习: null
下次复习: 2026-09-01
间隔天数: 33
难度系数: 2.5
复习次数: 0
连续答对: 0
失误次数: 0
易错: false
状态: 待复习
来源: [[../../../../03_知识资产/Android/ANR复习/02_Service ANR 源码全流程]]
---

# M03 · Service 类型 ANR 源码

## 核心章节

- 从 `startService` 到主线程回调的链路是什么？
- `bumpServiceExecutingLocked` 怎样埋雷？
- `serviceDoneExecuting` 怎样拆雷？
- `serviceTimeout` 怎样找到超时对象？
- `mExecutingServices`、`executeNesting`、`executingStart` 有什么区别？

## 复习规则

讲完整源码链；回来源核对；整张卡自评。

## 状态记录

| 日期 | 动作 | 自评 | 间隔天数 | 下次复习 | 状态变化 | 备注 |
|---|---|---|---:|---:|---|---|
| 2026-07-30 | 从综合卡分离机制 |  | 33 | 2026-09-01 | 新建 -> 待复习 | 服务阶段05。 |
