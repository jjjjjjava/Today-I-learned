---
type: learning-card
id: 线上ANR处理
主题: 稳定性/线上ANR处理
创建日期: 2026-06-23
上次复习: 2026-07-14
下次复习: 2026-07-22
间隔天数: 8
难度系数: 2.5
复习次数: 3
连续答对: 3
失误次数: 0
易错: false
状态: 待复习
来源:
  - [[../../../03_知识资产/Android/ANR复习/syllabus]]
  - [[../../../03_知识资产/Android/ANR复习/06_ANR线上治理方法论]]
---

# 线上ANR处理

> 主题：稳定性/线上ANR处理
> 来源：[[../../03_知识资产/项目/ANR]]
> 说明：本卡只记录复习状态和回忆线索，不存答案；细节回到来源笔记核对。

## 核心章节

  - ANR 项目回答的背景、问题、定位、证据、治理、结果、风险怎么组织？
  - 拿到 trace 后先看什么？
  - 如何判断主线程卡在 IO、锁、Binder、生命周期回调或消息处理？
  - ANR 和 MessageQueue 的关系怎么表达？

## 复习规则

- 复习时只看上面的核心章节，凭记忆回顾。
- 回顾后回到来源笔记核对。
- 对整张卡自评：没答出 / 磕绊 / 顺畅。

## 状态记录

| 日期 | 自评 | 间隔天数 | 下次复习 | 备注 |
|---|---|---:|---:|---|
| 2026-06-29 | 顺畅 | 3 | 2026-07-02 | 首复（用户判定算过）；同日给来源笔记04补充A/B类真实案例速览（7例带Issue ID） |
| 2026-07-02 | 顺畅 | 8 | 2026-07-10 | 二复；口头复述覆盖全主链路（Bugly三组件→意义三视角→埋雷拆雷爆雷→Service全链路→四类差异→Input→trace三步SOP→实战案例）。校准3处：爆雷找最早非最近、traces路径/data/anr/traces.txt、Input少outboundQueue一跳。答疑：Watchdog dump=getAllStackTraces仅Java栈、死穴是采样时刻≠ANR时刻。【勘误】Bugly进程内拿不到系统CPU：Android8+ /proc hidepid=2+SELinux挡住/proc/stat与他进程/proc/[pid]，只能读自己进程/线程CPU；ANR日志里的系统CPU段是system_server的ProcessCpuTracker写的，靠系统侧trace(FileObserver读/data/anr/，高版本已被SELinux焊死)才拿得到。【勘误2】系统无ANR广播：Bugly定性=轮询getProcessesInErrorState()（NOT_RESPONDING+shortMsg即reason来源），已修正04/05篇。【勘误3】空闲主线程trace态是Native(nativePollOnce)非Sleeping。SOP改口径：无CPU段→环境类用线程数暴多/多样本栈落点随机/低端机集中做代理证据 |
| 2026-07-14 | 完成 | 8 | 2026-07-22 | 学习 [[../../../03_知识资产/Android/ANR复习/06_ANR线上治理方法论]]，补强 ANR 治理方法论：前置防线、灰度监控、全量常态化监控、单点/聚合/爆发归因、分阶段止损与修复验证。 |


## 学习完成记录

| 日期 | 动作 | 结果 | 备注 |
|---|---|---|---|
| 2026-06-23 | 完成 ANR 学习 | 转入待复习 | 当前只是完成学习，没有进行复习评分；首次复习安排到 2026-06-24。 |
