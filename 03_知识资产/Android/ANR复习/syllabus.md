# Android ANR · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：标准
> 文档数量因人而异，但掌握内容不打折扣。
> 配套素材：`../Android ANR 原理.md`（你的原始笔记，作为底料，但讲解会重新提炼、高于笔记）

## 核心掌握项

完成本课题后，你将能够：

### 模块一 · ANR 本质与检测模型
- [x] 能用「系统在等 App 完成某个有时限的关键任务」来定义 ANR，而不是含糊地说「主线程卡顿」，并说清为什么需要它
- [x] 能用「埋雷 → 拆雷 → 爆雷」模型描述组件类 ANR 的检测流程，并解释为什么计时与判定必须由 system_server 负责、而非 App 自检

### 模块二 · 组件 ANR 全流程与四类差异
- [x] 能完整复述 Service ANR 从 `startService` 到 `serviceTimeout` 判定的链路（含 Binder 跨进程、主线程执行回调）
- [x] 能区分 `mExecutingServices`（进程维度）与 `executeNesting`（单 ServiceRecord 维度），并说清「超时消息只是触发器、真正判据是 `executingStart`」
- [x] 能说出四类 ANR 的超时阈值与爆雷处理，并归纳「时间触发型 vs 流式触发型」两大类
- [x] 能解释 ContentProvider ANR 为何是「异类」、Input ANR 为何是「独立王国」

### 模块三 · traces 实战诊断
- [x] 能说明 traces 能看什么、不能看什么，及「快照滞后」陷阱
- [x] 能用 A / B / C 三分类，结合线程状态 + CPU + 堆栈三方证据定位根因
- [x] 能做锁链追踪（`waiting to lock` → `locked`）判断死锁，并识别 MessageQueue WAITING、GC 线程 WAITING、CPU 低等高频陷阱；能把 A/B/C 重构为「线上诊断流水线」（reason 分流 → 在场判定 → A/B/C+D+E → 聚合合议）

### 模块四 · 线上 ANR 监控方案
- [x] 能描述 ANR 后系统的 `SIGQUIT` → SignalCatcher dump → traces 流程
- [x] 能区分 `sigaction` 与 `sigwait`，并解释「同一信号只能消费一次」带来的核心冲突
- [x] 能对比 Bugly / xCrash / Matrix 三方案，并说清 Matrix 委托线程模式为何更可靠

## 不在本课题范围内

- 图形渲染、布局优化、过度绘制、空间投影等性能话题（与 ANR 无直接关系）
- Handler / Looper / MessageQueue 的完整源码实现（仅在解释 ANR 链路时按需引用，不展开消息机制本身）
- Binder 驱动层细节（仅用到「跨进程调用」这一抽象，不深入驱动）
- 具体监控 SDK 的接入与配置（只讲机制原理，不讲集成步骤）

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 模块一全部（定义/为什么需要、埋雷-拆雷-爆雷、为什么由 system_server 判定）✅ 思考题已评估，掌握 | 2026-06-22 |
| 02.md | 模块二前两条（Service 全链路；mExecutingServices vs executeNesting，executingStart 才是判据）✅ 已复述评估，掌握；纠正点：阈值 20s/200s、nesting≠多次埋雷、爆雷找最早 | 2026-06-22 |
| 03.md | 模块二后两条（四类阈值/爆雷处理、两大类划分；ContentProvider 异类、Input 独立王国）✅ 已按学员思路重排+Input 四层骨架；纠正点：Reader/Receiver 分侧、outboundQueue、Provider 与 Application.onCreate 顺序 | 2026-06-22 |
| 04_traces分析流程.md | 模块三全部（trace 来源[Bugly 三组件]+快照滞后特殊性+三步分析法；A/B/C 融入第三层；锁链追踪+死锁判定+速查卡）＋模块四 Bugly 旁观者部分；✅ 按学员复述覆写，含真实极验/联通 AB-BA 死锁锁链案例；校准：5s 采样 vs SignalCatcher 一次性 dump、Watchdog 仅 Java 栈、误报/漏报 Input | 2026-06-23 |
| 05_SIGQUIT与xCrashMatrix.md | 模块四全部（SIGQUIT→SignalCatcher dump；sigaction vs sigwait + 信号只能消费一次的冲突；Bugly/xCrash/Matrix 对比 + Matrix 为何更可靠）✅ 按学员"如果让你设计监控方案"设计视角重写（被动 vs 主动），与第 1 篇设计题对称；校准：信号上下文/async-signal-safe（非"系统调用"）、Matrix 真因是时序可控 | 2026-06-23 |
