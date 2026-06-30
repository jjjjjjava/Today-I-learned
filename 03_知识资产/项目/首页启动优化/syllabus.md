# 首页启动优化 · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：深入
> 文档数量因人而异，但掌握内容不打折扣。
> 配套素材：同目录 `启动优化笔记.md`（你的原始项目复盘，作为骨架底料）+ 归档卡片 `037-启动全流程时序.yaml`（流程机制底料）
> 本课目标：**把「项目操作」与「背后流程机制」融成一份知识资产**，让你在面试中以项目为骨架讲出，被追问机制时有底。

## 核心掌握项

完成本课题后，你将能够：

### 模块一 · 口径与可观测起点
- [x] 能讲清「启动优化第一步是定口径而非改代码」，并用 TTID/TTFD 区别说明本项目为何选 TTFD（首帧可见 ≠ 首页工作台可见）
- [x] 能复述本项目 TTFD 定义（`bindApplication` → `TTFD_HomeWorkDesk`，权限模块 View 添加并经下一次 draw 后打点），并解释「为什么要等下一次 draw」
- [x] 🔧 能从流程机制解释「为什么起点选 `bindApplication`」：点击 → `ActivityThread.main` 之前是 Launcher → ATMS/AMS → Zygote fork 的**系统不可控区间**

### 模块二 · 工具 · 计算 · 归因方法
- [x] 能说清 Perfetto + 业务 marker 的分工（marker 定终点、Perfetto 看中间），及 `sectionBegin/End`=`Trace.beginSection`、`profileable` 的作用
- [x] 能用 SQL（限定进程、ns→ms）算 TTFD，并用 **Wall / Self / Count** 组合判断瓶颈类型
- [x] 🔧 能从机制解释「为什么 `doFrame` Wall 高 Self 低不是根因」：`Choreographer#doFrame` → `performTraversals` 的嵌套外层结构

### 模块三 · 首屏瓶颈归因与渲染机制（重头）
- [x] 🔧 能解释 `inflate` 106 次为何这么贵：`setContentView` 三阶段 + `LayoutInflater` 反射 new View
- [x] 🔧 能解释 `RelativeLayout` / `RV OnLayout` / `traversal` 重的机制：`performMeasure` 递归 + **RelativeLayout 双重测量**
- [x] 🔧 能解释 WebView `gone` 仍创建且昂贵的根因（inflate 即反射 new 对象 + Chromium 重量级），及 `binder transaction` 579 次的来源（生命周期 / 跨进程调用都走 Binder）

### 模块四 · 方案 · 取舍 · 回归
- [x] 能讲清首屏路径裁剪 P0 / P1 / P2 的优先级逻辑，并 🔧 从机制解释「为什么 Application 同步初始化排 P2」（阶段3 onCreate / ContentProvider 串行，本项目占比小）
- [x] 能复述 P0 前后复测数据，并说清门店页「分阶段缓存」、"我的"页「状态快照 + replay」两个回归取舍的本质（**状态生产早于 UI 消费 ready**）

### 模块五 · 面试表达与全流程复述
- [x] 能用「口径 → 工具 → 计算 → 归因 → 方案 → 验证 → 回归」2 分钟讲完项目主线，并稳接高频追问
- [x] 🔧 能脱离项目、独立复述**启动全流程 5 阶段机制全景**（进程创建 → 主线程 → Application → Activity → 渲染），含 fork 返回值、三层创建时机等精确点（见附录篇）

## 不在本课题范围内

- Binder 驱动层 mmap / 事务实现细节（只用「跨进程调用」抽象）
- Handler / Looper / MessageQueue 完整源码（按需引用，不展开消息机制本身）
- Perfetto 的 trace processor 进阶用法（只用到算 TTFD 与导 slice 所需）
- 其他性能维度（内存、运行期卡顿、功耗）——本课聚焦冷启动 TTFD

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 模块一全部（口径定义 + 为什么 TTFD + 为什么 bindApplication 起点的流程机制 + 为什么等下一次 draw）✅ 已 re-narration 演练，口径/分层掌握 | 2026-06-26 |
| 02.md | 模块二全部（Perfetto+marker 分工、category↔流程、profileable；SQL 算 TTFD；Wall/Self/Count 组合判断）+ 🔧 doFrame Wall 高 Self 低=容器型外层；含 01 思考题复盘 | 2026-06-26 |
| 03.md | 模块三全部（🔧 inflate 三阶段反射 newView；🔧 RelativeLayout 双重测量+measure 递归；🔧 WebView gone 仍创建+Chromium；🔧 binder 579 次溯源[纠正"渲染走 binder"误解]）+ 项目归因三类矛盾；含 02 思考题复盘。**补丁：拆清 RV(RecyclerView)≠RelativeLayout** | 2026-06-26 |
| 04.md | 模块四全部（首屏裁剪 P0/P1/P2 优先级；🔧 Application 排 P2 的串行机制+异步天花板；P0 前后复测数据；门店页分阶段缓存、"我的"页状态快照+replay 两回归取舍）；含 03 思考题复盘（纠 RV/RelativeLayout、反射 vs 手写） | 2026-06-26 |
| 05.md | 模块五全部（面试 2 分钟主线 + 高频追问表[含白屏诊断、RV≠RelativeLayout]；🔧 附录·启动全流程 5 阶段机制全景）；含 04 思考题复盘（382 binder ROI、异步天花板、白屏时序诊断）+ 纠正优化率 33%→约 36%。 | 2026-06-26 |
| 06.md | **评估篇**（`<!-- eval-article -->`）：全课终检清单（5 块带标准答案，逐条自测）。读毕「我读完了」→ 自动生成 summary.md | 2026-06-27 |
