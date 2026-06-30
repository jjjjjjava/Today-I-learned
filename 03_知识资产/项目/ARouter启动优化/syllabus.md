# ARouter 启动优化 · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：深入
> 文档数量因人而异，但掌握内容不打折扣。
> 配套素材：同目录 `ARouter启动优化笔记.md`（你的原始项目复盘，作为骨架底料）+ `../../Android/ARouter.md`（ARouter 原理机制底料）
> 本课目标：**把「项目操作」与「背后 ARouter 原理机制」融成一份知识资产**，让你在面试中以项目为骨架讲出，被追问机制（路由表怎么生成、怎么加载、register 插桩怎么做）时有底。

## 核心掌握项

完成本课题后，你将能够：

### 模块一 · 优化口径与问题定位
- [x] 能讲清「启动优化第一步是定口径」，并说明本项目为何把主统计区间定为 `Application.attachBaseContext()` → 首页可见（业务可控区间），以及终点为何不停在 `onCreate()`/`onResume()`
- [x] 能讲清第一层归因工具为何选 Android Studio Profiler / Method Trace 而非 Perfetto（10s 级异常慢、目标是快速定位重量级任务、成本最低反馈最快），并说清 Profiler 的局限（采样/插桩开销，不适合判断几百毫秒级收益）；🔧 能区分插桩 `startMethodTracing` 与采样 `startMethodTracingSampling(file, 8MB, 1000μs)` 两种模式的原理与取舍，并解释本项目为何选采样
- [x] 🔧 能从机制解释 ARouter 是什么、解决什么（用 `path` 间接寻址替代 `Class` 引用 → 解耦 / 动态跳转 / 统一拦截），作为项目背景铺垫

### 模块二 · Trace 归因与 ARouter 加载机制（重头）
- [x] 能读 Profiler 数据定位瓶颈：整体 trace 约 9.74s、`openDexFileNative` 约 7.6s，并沿调用栈确认它来自 `ARouter.init` → `LogisticsCenter.init` → `ClassUtils.getFileNameByPackageName` → `DexFile.openDexFileNative`
- [x] 🔧 能解释 `openDexFileNative` 为什么贵的机制：ARouter 默认 **Dex 扫描方案**——运行时逐个打开 dex、遍历类名、筛 `com.alibaba.android.arouter.routes` 包下生成类、反射 `loadInto()`；项目 dex 多、体量大时被放大
- [x] 🔧 能解释路由表三大运行时概念 `RouteMeta` / `Postcard` / `Warehouse` 与**分组懒加载**，说清「扫描出的路由表最终装到哪里、怎么按需加载」
- [x] 🔧 能解释路由表从哪来：编译期 APT 注解处理器 `RouteProcessor` 扫 `@Route` → JavaPoet 生成 `Root` / `Group` / `Provider` 三类文件，以及为什么按 group 分组

### 模块三 · 方案设计：为什么是 register 字节码插桩
- [x] 能讲清三个候选方案的取舍：异步初始化（没消除 dex 扫描成本 + 路由可用时机问题）、换路由框架（替换成本/回归风险高）、register 插件（贴近根因）
- [x] 🔧 能解释 register 插桩机制：`LogisticsCenter.loadRouterMap()` 默认是空壳 → Gradle 插件借 AGP Artifacts API 接管 `CLASSES` 产物，用 ASM 在 `loadRouterMap()` 的 `return` 前插入 `register("生成类名")`，把运行时 dex 扫描**前移到编译期**
- [x] 🔧 能解释为什么 SP 缓存不算根治：它只缓存「上次扫描到的类名集合」，新安装 / 包更新 / debug 频繁安装时缓存失效，仍回退到 dex 扫描

### 模块四 · 落地踩坑与回归验证
- [x] 能复述三个真实踩坑：①原版 `arouter-register` 不兼容 AGP8（先查 GitHub issue 确认，非凭空猜）②Java 21 报 `Unsupported class file major version 65` → fork 升级 ASM ③variant 驼峰命名导致插桩没作用到目标变体
- [x] 🔧 能解释 Java 17/21 兼容根因：ASM 的 `ClassReader` 读 class 文件头里的 major version，旧 ASM 不认识新版本（Java 17 = 61 / Java 21 = 65），需确保插件运行时真正使用支持新 class version 的 ASM
- [x] 能复述收益数据与回归口径：首次冷启动 ARouter 初始化从 7.84s → 100ms 内、整体冷启动约 9.4s → 1.54s；功能回归（页面跳转 / Provider / Interceptor / 多模块路由 / debug-release / 不同 variant）；并能讲清「编译通过 ≠ 优化生效」的验证意识

### 模块五 · 面试表达与全链路复述
- [ ] 能用「口径 → 工具 → 数据 → 归因 → 方案 → 落地 → 回归」2 分钟讲完项目主线，并稳接高频追问
- [ ] 🔧 能脱离项目、独立复述 **ARouter 全流程机制全景**（编译期生成路由表 → init 加载到 Warehouse → 运行时 `navigation` 查表跳转），含三类文件、分组懒加载、`completion()` 补全 `Postcard` 等精确点

## 不在本课题范围内

- ARouter 拦截器调度的完整实现（`IInterceptor` 优先级 / 异步链式拦截细节，只用「统一拦截」抽象）
- `@Autowired` 参数注入 / 依赖查找的完整机制（只点到 Provider 服务获取）
- AGP Transform / Artifacts API 的完整任务生命周期源码（只用到「在 D8 前接管 CLASSES 产物」抽象）
- ASM 字节码指令集细节（只用到「在 return 前插入 register 调用」的抽象）
- 其他启动优化手段（首屏裁剪、Application 瘦身等已在「首页启动优化」课题覆盖）

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 模块一全部（口径：attachBaseContext→首页可见为何是业务可控区间、终点为何不停在 onCreate/onResume；工具：为何 Profiler 先行而非 Perfetto + Profiler 局限；🔧 ARouter 是什么/解决什么 + 三步链路铺垫） | 2026-06-29 |
| 02.md | 模块二全部（Profiler 调用栈归因 openDexFileNative≈7.6s 来自 ARouter.init→LogisticsCenter.init→ClassUtils.getFileNameByPackageName；🔧 默认 dex 扫描方案为何贵；🔧 Warehouse/RouteMeta/Postcard 三概念+分组懒加载=装到哪；🔧 APT RouteProcessor+JavaPoet 生成 Root/Group/Provider=路由表哪来）；含 01 思考题复盘 | 2026-06-29 |
| 03.md | 模块三全部（异步/换框架/register 三方案取舍；🔧 为何必须 ASM=源码已成 .class；🔧 构建四阶段+AGP Artifacts API 接管 CLASSES 产物；🔧 插桩两步=扫 routes 包认三接口 + ASM 在 loadRouterMap return 前插 register，含为何要复制 class；🔧 SP 缓存非根治）；含 02 思考题复盘 | 2026-06-29 |
| 04.md | 模块四全部（三坑：AGP8 不兼容[查 issue]、Java21 major version 65[🔧 ASM ClassReader 读版本号根因+fork 升 ASM+PR 致谢]、variant 驼峰致插桩未生效[编译通过≠生效]；回归：首次冷启动 init 7.84s→100ms内/整体 9.4s→1.54s、后续启动几十ms→几ms、功能回归清单）；含 03 思考题复盘 | 2026-06-29 |
