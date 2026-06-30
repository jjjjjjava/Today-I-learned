# ARouter 启动优化笔记

## 1. 优化口径

### 1.1 问题背景

这个问题是我在日常开发中遇到的，我喜欢打debug包：在小米 8 这类设备上，App 冷启动到首页可见很多时候会达到 10s左右，启动体感明显异常。

我想去看问题到底在哪，所以我要先圈定一个可分析、可复现、可对比的启动区间，找出到底是哪段业务链路卡住了启动。

### 1.2 主统计区间

本次 ARouter 启动优化的主统计区间定义为：

```text
Application.attachBaseContext() -> 首页可见
```

起点选择 `Application.attachBaseContext()`，是因为从这里开始进入业务代码更可控的启动阶段。

完整冷启动还包括很多系统阶段，但是这些系统阶段会受到系统调度、设备状态、进程创建等因素影响，不是本次优化主要处理的业务代码区间。

终点选择首页可见，或者 `HomeOldActivity.onWindowFocusChanged(true)` 附近，是为了覆盖从业务初始化到首页真正展示出来的过程，而不是只停在 `Activity.onCreate()` 或 `onResume()` 这类生命周期节点。

### 1.3 面试表达

可以这样表达：

```text
这次不是为了做线上严格 TTFD 指标，而是为了在本地复现启动慢时，圈定业务可控启动区间，然后抓 trace 找出主要耗时点。

所以我把区间定义为 Application.attachBaseContext 到首页可见。完整冷启动当然还包括 AMS、Zygote fork、进程创建等系统阶段，但这些不是本次主要优化对象。我关注的是业务代码在启动链路里到底做了哪些耗时工作。
```

## 2. 方案选型

### 2.1 为什么选择 Android Studio Profiler / Method Trace

这次选择 Android Studio Profiler / Method Trace 作为第一层归因工具。

因为体感耗时较多，我们不追求完整的精细化的追踪，因此不用perfetto，我们的第一目标是快速定位：

```text
到底被哪个方法卡住了，为什么会卡这么久？
```

相比 Perfetto、线上指标平台或大量业务埋点，AS Profiler 的使用成本最低，可以直接看到启动阶段的方法调用栈和耗时分布，适合快速判断是否存在秒级重量级任务。

### 2.2 Profiler 本身不会产生影响吗？

Profiler 的结果不能直接等价为真实线上启动耗时。

原因是 Method Trace / Profiler 本身存在采样或插桩开销，不适合直接用来判断几十毫秒、几百毫秒级的精细收益。

但本次问题是 10s 级别的异常慢，目标是先判断是否存在单个重量级任务。对于这种秒级瓶颈，Profiler 足够作为第一层归因工具。

如果无法完全判断，或者发现耗时比较分散，或者优化目标是几百毫秒级，再切到 Perfetto + 统一口径做精细化统计。

### 2.3 面试表达

可以这样表达：

```text
因为这个问题最初是我在本地 adb debug 时发现的，不是已经立项的专项优化，所以我先选择成本最低、反馈最快的 Android Studio Profiler 作为第一层归因工具。

Profiler 不适合直接等价线上真实耗时，也不适合判断很小的收益。但这次是 10s 级别的异常慢，我先用它判断是否存在秒级重量级任务。如果无法完全判断，或者耗时比较分散，或者目标是几百毫秒级优化，我会再切到 Perfetto + 统一口径做精细化统计。
```

## 3. 数据计算 / Profiler 数据读取

### 3.1 关键观察

本项目没有先用 SQL 计算，而是直接读取 Android Studio Profiler / Method Trace 的火焰图和调用栈。

Profiler 中观察到的关键数据：

```text
整体 trace 时间约 9.74s
openDexFileNative 约 7.603s
```

这说明启动阶段存在一个非常明显的秒级瓶颈，而不是各个方法均匀分摊的普通慢启动。

### 3.2 分析思路

初步分析：

```text
先在火焰图中找启动阶段最大的耗时块
-> 再沿调用栈去看
-> 确认耗时属于哪个业务初始化链路
-> 发现主要耗时集中在 ARouter.init 链路中
-> 进一步下钻分析
```

这里通过调用栈确认 `openDexFileNative` 是由 ARouter 初始化链路触发的。

下钻分析：Profiler 中看到的关键调用链路可以表达为：

```text
ARouter 的 taskPool 中有一个线程执行 run()
-> 执行到 ARouter.init()
-> LogisticsCenter.init()
-> ClassUtils.getFileNameByPackageName()
-> DexFile.openDexFile()
-> DexFile.openDexFileNative()
```

也就是说，`openDexFileNative` 虽然是 Android 系统 native 方法，但它不是孤立出现的。它是在 ARouter 初始化过程中，为了运行时扫描 dex、枚举类名、寻找路由表生成类而触发的。

## 4. Trace 问题归因

这一段 trace 下钻到的核心方法是 `ClassUtils.getFileNameByPackageName()`，它做的事情本质上是 ARouter 路由表加载。ARouter 在初始化时需要找到编译期生成的路由表相关类，后续才能把路由信息装载进运行时容器里，支持通过 path 找到对应页面、Provider 或拦截器。

在没有插件提前注册的情况下，ARouter 走的是 dex 加载方案。它会逐个打开 dex 文件，遍历其中的大量类名，然后筛选出 routes 相关的生成类，再完成后续装载。这个过程本身不是复杂业务逻辑，而是一个启动期的全量扫描动作。

这个方法为什么耗时，关键在于我们项目 dex 数量多、体量大。为了找到少量路由表类，却需要打开多个 dex，并遍历大量类名。这个扫描成本在小项目里可能不明显，但在多模块、大体量项目里会被放大，所以 trace 里最终表现为 `openDexFileNative` 占了很大头。

所以这一步的归因结论是：

```text
启动慢不是普通 Activity 创建或 UI 渲染导致的，而是 ARouter 默认 dex 路由表加载方案在当前项目体量下成本过高，启动期逐个打开 dex、遍历类名，最终形成秒级耗时。
```

面试时可以留一个追问点：

```text
我后面继续看了 ARouter 的路由表生成、加载和 register 插件机制，确认这个问题不是简单把初始化异步化就能根治，而是要绕开运行时 dex 扫描。
```

## 5. 方案设计

### 5.1 源码层面的现有机制

看 ARouter 源码后，发现路由表加载主要有两条路径。

第一条是默认的 dex 加载路径。它会通过 `ClassUtils.getFileNameByPackageName()` 打开 dex、遍历类名、筛选 routes 相关类，再完成路由表装载。这里虽然有 `SP` 缓存优化，但它只是 dex 扫描结果的缓存；在新安装、包更新、debug 频繁安装等场景下，缓存可能不存在或失效，最终仍然会回到 dex 扫描。

第二条是插件注册路径。`LogisticsCenter.init()` 里会先调用 `loadRouterMap()`。这个方法本身依赖字节码插桩：如果没有插件，它基本是空的，后续还是走 dex 扫描；如果被插件插桩，就会执行 `register(...)`，把路由表类直接注册进去，并跳过后续 dex 加载流程。

### 5.2 可选方案

异步初始化 ARouter 是一个直观方案。它可以把初始化从主线程挪到子线程，但没有消除 dex 扫描成本，而且会带来路由可用时机问题。一个典型场景是：主线程启动流程已经完成，业务马上跳转其他页面，但此时子线程里的 ARouter 初始化还没结束，路由表还没有装载完成，就可能出现跳转失败，或者需要额外等待和兜底。

更换路由框架也可以规避 ARouter 默认扫描机制，但项目已经大量使用 ARouter，涉及页面跳转、Provider、Interceptor 和多模块路由，替换成本和回归风险都很高。

接入 register 插件是更贴近根因的方案。它不是继续依赖启动期 dex 扫描，而是通过字节码插桩让 `loadRouterMap()` 生效，把路由表注册逻辑前移到编译期准备好。

### 5.3 最终选择及结果判断

最终选择 register 插件方案。

它的本质是把“启动期打开 dex、遍历类名找 routes 类”替换成“运行时执行 `loadRouterMap()` 里的简单 `register(...)` 方法调用”。也就是把重扫描从运行时挪到编译期，启动时不再逐个打开 dex，所以耗时会明显缩短。

## 6. 结果验证以及回归

### 6.1 实现过程中遇到的困难和问题

落地过程中不是简单接一个现成插件。

首先，原版Alibaba官方仓库是有 `arouter-register` 插件的，但是太老了，21年后就不维护了，不兼容当前项目的 AGP8 环境。这个判断不是凭空猜的，而是先查了 GitHub issue，确认社区里已经有人反馈 AGP8 兼容问题，所以没有继续在原插件上硬接。

后面改用一个兼容 AGP8 的三方 ARouter 插件，并把源码接进项目验证。接入后又遇到 Java 21 字节码兼容问题：

```text
Unsupported class file major version 65
```

这个问题是在插件源码执行过程中暴露出来的。插件用 ASM 的 `ClassReader` 读取编译后的 class 字节码文件时，会先解析 class 文件头里的 version。Java 21 对应 major version 65，而插件内部使用的 ASM 版本不支持这个 class 文件版本，所以在读取字节码时直接失败。

因此我 fork 了插件并自己修复，主要处理：

```text
升级 ASM 版本，使其支持 Java 21 class 文件
检查 ASM API 常量，例如从 Opcodes.ASM7 调整到 ASM9
确保插件运行时使用正确 ASM 依赖
修复后发布自己的 ARouter Gradle 插件供项目接入
```

这个修复也提了 PR 到对方项目。对方项目是百星级开源项目，作者邮件回复表示感谢，并在项目中对我的贡献做了致谢。

### 6.2 编译成功后验证插件是否真正生效

插件能编译通过不代表优化已经生效。

接入自己修复后的插件后，项目可以编译成功，但启动耗时没有明显下降。于是继续看构建日志和插件日志，发现没有看到插件应用到目标 variant 的日志，也就是说字节码插桩任务没有真正作用到当前构建变体。

继续在插件里补日志，并结合 Gradle 编译过程排查，最后定位到 variant 命名处理问题。项目里的变体名使用驼峰命名，原插件在为变体配置任务或匹配任务时没有正确处理这个命名规则，导致对应 variant 没有走到预期的插桩逻辑。

修复 variant 命名兼容后，`loadRouterMap()` 才真正被插桩。也只有这个方法里实际插入了 `register(...)` 调用，运行时 ARouter 初始化才能跳过后续 dex 扫描。

### 6.3 回归验证

性能验证分首次冷启动和后续启动看。

首次冷启动收益最明显。因为首次启动没有可用的 `SP` 缓存，原来会走 dex 扫描，需要打开 dex、遍历类名，所以优化后从 dex 扫描变成 `loadRouterMap()` 里的方法调用，ARouter 初始化从总计7.84s降到 100ms 以内，整体冷启动从约 9.4s 降到约 1.54s。

后续启动原来可能命中 `SP` 缓存，不一定每次都重新扫描 dex。这个场景下原方案大致是一次 `SharedPreferences` 读取，加上遍历缓存中的 routes 类名、反射装载路由表。正常情况下耗时可能是几十毫秒级，具体取决于路由表数量和设备 I/O 状态；插件方案则进一步变成直接执行 `loadRouterMap()` 中的 `register(...)` 方法调用，通常可以压到几毫秒到十几毫秒级，并且不受新安装、包更新、debug 安装导致缓存失效的影响。

功能回归重点包括：

```text
普通页面路由跳转正常
Provider 注册和获取正常
Interceptor 注册和执行正常
多模块路由表没有缺失
debug / release 构建正常
不同 build variant 构建正常
AGP8 + Java21 环境下插件稳定可用
```

### 6.4 面试表达

可以这样表达：

```text
落地过程中不是简单引入一个插件。原版 arouter-register 不兼容 AGP8，这点我是先从 GitHub issue 里确认的。后面接了一个兼容 AGP8 的三方插件源码，又遇到 Java 21 字节码读取失败，报 Unsupported class file major version 65。

我继续看源码，定位到插件使用 ASM ClassReader 读取 class 文件时，会检查 class 文件头里的 version，而 Java 21 是 major version 65，旧 ASM 版本不支持，所以我 fork 插件升级 ASM，并处理 ASM API 和依赖问题。修复后我也给对方百星项目提了 PR，作者邮件感谢，并在项目里对我做了致谢。

后面项目能编译通过后，启动耗时一开始并没有下降。我没有直接认为方案无效，而是补插件日志看 Gradle 构建过程，发现没有应用到目标 variant。最后定位到我们项目变体名是驼峰，原插件任务命名处理不兼容，修复后 loadRouterMap 才真正被插桩。

最终验证时，首次冷启动里 ARouter 初始化从秒级降到 100ms 以内，整体冷启动从约 9.4s 降到约 1.54s。后续启动原来可能走 SP 缓存，大概是几十毫秒级；插件方案变成直接方法注册，通常是几毫秒到十几毫秒级，并且规避了缓存失效后重新扫描 dex 的问题。功能上回归了页面跳转、Provider、Interceptor、多模块路由、debug/release 和不同 variant 构建。
```

## 7. 面试表达

待补充。
