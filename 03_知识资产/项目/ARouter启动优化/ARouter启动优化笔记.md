# ARouter 启动优化笔记

> 本文是“启动优化方法论”中增量劣化治理路线的项目案例。首页案例负责说明如何降低存量水位；本案例负责说明一次构建升级如何穿透前置防线，并在灰度阶段被发现、止损、修复和回填。

## 0. 接入启动优化方法论：一次穿透前置防线的增量劣化

### 0.1 为什么这是增量劣化治理

这次不是稳定版本长期偏慢，而是升级 Gradle/AGP 后，候选版本相对原稳定版突然变慢。

因此它属于增量治理：

```text
Gradle / AGP 升级
→ ARouter register 插件链路失效
→ 运行时回退到 Dex 扫描
→ 候选版本冷启动突然劣化
→ 灰度 Stage/Task 告警
```

完整处理链路是：

```text
静态检测、CI、整包自动化漏网
→ 灰度告警
→ startup.stage.app_init
→ startup.task.arouter.init
→ 暂停放量并选择低端机复现
→ AS Profiler 快速定位 Dex 扫描
→ 查 GitHub issue，修复 AGP 插件链路
→ 再处理 Java 21 / ASM / variant 兼容
→ 建立可重复 Benchmark
→ 分级灰度
→ 回到原冷启动水位
→ 将事故条件回填 CI
```

### 0.2 为什么有预算，CI 和自动化仍然没拦住

项目已经为 `app_init` 和 `arouter.init` 设置预算。问题不是“预算不够严格”，而是测试没有稳定触发超预算路径。

ARouter 的运行时 Dex 扫描存在 SP 缓存：

```text
首次安装 / 包版本变化后的第一次启动
→ 扫描 Dex，记录 routes 类名集合
→ 写入 SP

后续启动
→ 读取 SP 中的类名集合
→ 不再执行完整 Dex 扫描
```

因此原有 Benchmark 只有第一次可能出现 7～8 秒扫描，后续轮次命中缓存后恢复到较短耗时。如果流水线复用应用数据、把首轮当作 warm-up，或者只看多轮中位数，这个一次性劣化就会被隐藏。

各层防线的真实能力边界是：

| 防线 | 为什么漏网 |
| --- | --- |
| 静态 Lint | 业务代码没有新增主线程 IO；变化发生在构建插件是否成功插桩，普通源码规则无法判断 |
| MR CI Benchmark | 没有固定覆盖“升级安装后的第一次冷启动”，SP 缓存让后续样本恢复正常 |
| 整包自动化 | 场景覆盖了常规冷启动，但没有把 clean install、upgrade first launch 与 cache-hit 分开统计 |
| 灰度 | 真实用户升级后第一次启动天然满足缓存失效条件，因此最终暴露问题 |

这次事故说明：

> **有预算不等于有防线。只有测试真正执行到超预算路径，预算门禁才有意义。**

### 0.3 灰度沿 Stage/Task 定位

灰度告警后，先按版本、启动场景和设备档位比较，再沿统一埋点下钻：

```text
startup.total
└── startup.stage.app_init
    └── startup.task.arouter.init
```

`startup.stage.app_init` 对应 Application 初始化阶段；不要再把 Stage 写成笼统的 `Application.onCreate`。`startup.task.arouter.init` 才是本次横向对比中增量最大的具体任务。

演练用的 P50 采用 Mock 数据，P90 和本地 Profiler 使用项目记录：

| 版本 | P50（Mock） | LOW 档 P90 | 说明 |
| --- | ---: | ---: | --- |
| 原稳定版，旧 Gradle | 2.1s | 4.5s | 原冷启动水位 |
| 灰度候选版，新 Gradle、插件失效 | 5.6s | 12.8s | P90 相对基线增加约 8.3s |
| 修复版，新 Gradle、插件恢复 | 2.2s | 约 4.7s | ARouter 劣化基本消除 |

这里必须明确：P50 是面试演练用 Mock 值，不得表述为生产平台真实数据。

P90 的正确表达也不是“P90 劣化到了 8.3s”，而是：

> **LOW 档 P90 从约 4.5s 上升到 12.8s，相对劣化约 8.3s。**

### 0.4 如何剥离 Gradle 升级本身的影响

事故由 Gradle/AGP 升级触发，但不能把候选版的全部 8.3 秒都笼统归因给 Gradle。需要三个版本做对照：

```text
A：旧 Gradle + 原稳定插件链路
B：新 Gradle + register 插桩失效
C：新 Gradle + register 插桩修复
```

- `B → C`：Gradle 环境相同，主要差异是 ARouter 插桩是否生效，可以隔离 ARouter 修复收益。
- `A → C`：ARouter 都处于正常路径，用来观察升级 Gradle 后是否仍有剩余启动差异。

如果 `B` 的 LOW P90 是 12.8s，`C` 回到约 4.5s，可以说“约 8.3 秒的 ARouter 劣化被消除”。但不能仅凭最终都为 4.5s 就断言 Gradle 升级完全没有影响；还要结合样本量、波动区间和其他 Stage 对比。

### 0.5 为什么紧急定位选择 AS Profiler

这次已经由线上 Stage/Task 把范围缩小到 `arouter.init`，而且是 8 秒级单点异常。紧急流程的目标是尽快回答“ARouter 内部在做什么”，不是先完成一套精细的系统级归因。

因此使用 Android Studio Profiler 查看方法调用栈：

```text
ARouter.init
→ LogisticsCenter.init
→ ClassUtils.getFileNameByPackageName
→ DexFile.openDexFile
→ openDexFileNative
```

Profiler 很快确认候选版本没有走编译期 register 路径，而是回退到了运行时 Dex 扫描。它适合定位这种秒级单点瓶颈；最终收益仍需由 Benchmark、Stage/Task 和灰度数据证明。

## 1. 优化口径

### 1.1 问题背景

这个问题首先由灰度告警发现，而不是个人打 Debug 包偶然发现。线上已经定位到 `startup.stage.app_init`，并进一步看到 `startup.task.arouter.init` 横向对比增长最多。

为了快速复现，我们选择低端机和首次安装/升级后的第一次冷启动。小米 8 这类设备能把 Dex 打开、类名遍历和反射加载的成本进一步放大，启动到首页可见会接近 10 秒。

线上 Stage/Task 负责缩小范围；本地 Profiler 负责解释 `arouter.init` 内部为什么慢；后续 Benchmark 负责证明修复前后差异。

### 1.2 主统计区间

本次 ARouter 启动优化的主统计区间定义为：

```text
Application.attachBaseContext() -> 首页可见
```

起点选择 `Application.attachBaseContext()`，是因为从这里开始进入业务代码更可控的启动阶段。

完整冷启动还包括很多系统阶段，但是这些系统阶段会受到系统调度、设备状态、进程创建等因素影响，不是本次优化主要处理的业务代码区间。

终点选择首页可见，或者 `HomeOldActivity.onWindowFocusChanged(true)` 附近，是为了覆盖从业务初始化到首页真正展示出来的过程，而不是只停在 `Activity.onCreate()` 或 `onResume()` 这类生命周期节点。

同时保留一组更窄的任务口径：

```text
startup.stage.app_init
└── startup.task.arouter.init
```

总启动区间回答“用户最终慢了多少”，`arouter.init` Task 回答“本次增量由谁贡献”。

### 1.3 面试表达

可以这样表达：

```text
线上用 startup.total、startup.stage.app_init 和 startup.task.arouter.init 判断影响范围与增量贡献。

本地复现时，再用 Application.attachBaseContext 到首页可见圈定业务可控区间，并以 arouter.init 作为方法归因锚点。线上口径负责发现和验收，本地区间负责快速解释根因，两者不能混用绝对值。
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
灰度已经把问题定位到 startup.task.arouter.init，而且是 8 秒级异常。紧急流程优先追求定位速度，所以我选择成本较低、能直接看方法调用栈的 Android Studio Profiler。

Profiler 不等价于线上真实耗时，也不适合判断小收益。但这次只需要快速确认 ARouter 内部是否存在秒级任务。最终修复收益仍由同环境 Benchmark、线上 Stage/Task 和分级灰度证明。
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

#### 第一轮：Gradle/AGP 升级后，官方 register 插件失效

Alibaba 官方 `arouter-register` 基于旧 Transform API。升级 AGP 8 后，`registerTransform` 被移除，插件无法继续沿原方式接管 class 产物。

这个判断不是凭空猜测。我们先检索 GitHub issue，找到 [ARouter #1070：registerTransform 被移除，需要适配 Gradle 8](https://github.com/alibaba/ARouter/issues/1070)，再决定不在旧插件上继续硬接。

第一轮处理是引入支持 AGP 7.4+/8 的 [JailedBird/ArouterGradlePlugin](https://github.com/JailedBird/ArouterGradlePlugin)。它通过新的 AGP 构建产物 API 扫描路由表 class，并对 `LogisticsCenter.loadRouterMap()` 做 ASM 插桩。

#### 第二轮：项目升级 Java 21，插件再次不兼容

AGP 8 问题处理后，Java 21 构建又出现：

```text
Unsupported class file major version 65
```

异常发生在插件读取编译产物时。插件使用 ASM `ClassReader` 解析 `.class` 文件头，Java 21 对应 major version 65，旧 ASM 不认识该版本，因此还没完成插桩就失败。

我们 fork 了 JailedBird 插件并形成 [jjjjjjava/ArouterGradlePlugin](https://github.com/jjjjjjava/ArouterGradlePlugin)，主要处理：

```text
ASM / asm-commons / asm-tree 升级到 9.7
Opcodes.ASM7 调整为 ASM9
确保插件运行时依赖真正解析到新版 ASM
修复 Debug / debug 等 variant 大小写匹配
发布自维护插件版本
```

Java 21 修复提交到上游 [PR #16](https://github.com/JailedBird/ArouterGradlePlugin/pull/16)，随后上游发布了 Java 21 兼容版本。

当前项目使用的是自维护版本：

```groovy
classpath "com.github.jjjjjjava.ArouterGradlePlugin:arouter-gradle-plugin:v1.0.5"
apply plugin: "io.github.jjjjjjava.ARouterPlugin"
```

两轮问题要分开表达：第一轮解决“AGP 8 下怎么继续介入构建”；第二轮解决“Java 21 class 能不能被插件中的 ASM 正确读取和改写”。

### 6.2 编译成功后验证插件是否真正生效

插件能编译通过不代表优化已经生效。

接入自己修复后的插件后，项目可以编译成功，但启动耗时没有明显下降。于是继续看构建日志和插件日志，发现没有看到插件应用到目标 variant 的日志，也就是说字节码插桩任务没有真正作用到当前构建变体。

继续在插件里补日志，并结合 Gradle 编译过程排查，最后定位到 variant 命名处理问题。项目里的变体名使用驼峰命名，原插件在为变体配置任务或匹配任务时没有正确处理这个命名规则，导致对应 variant 没有走到预期的插桩逻辑。

修复 variant 命名兼容后，`loadRouterMap()` 才真正被插桩。也只有这个方法里实际插入了 `register(...)` 调用，运行时 ARouter 初始化才能跳过后续 dex 扫描。

### 6.3 为什么 Benchmark 只有第一次能复现

修复过程中遇到一个测量问题：未插桩版本只有第一次启动稳定出现 Dex 扫描，之后再跑就无法复现。

原因不是问题消失，而是第一次扫描后，ARouter 把 routes 类名集合写入 SP。后续 Benchmark 命中缓存，不再重复完整扫描。

如果连续运行十次并取中位数，结果可能是：

```text
第 1 次：7～8 秒，触发 Dex 扫描
第 2～10 次：命中 SP 缓存，只有几十毫秒
中位数：看起来没有明显劣化
```

这正是 CI 和自动化漏网的关键原因，也是为什么灰度中的真实升级用户反而先触发告警。

为了稳定复现，我们在自维护插件和 Benchmark 变体中增加测试专用开关，让每轮测量前强制失效或绕过 ARouter 的 routes SP 缓存，保证未插桩版本每次都走 Dex 扫描。

这里需要校准术语：

> **SP 缓存属于 ARouter 运行时扫描逻辑，不是 Gradle 插件自身的缓存。插件提供的是 Benchmark 专用的失效/绕过手段，生产版本不能为了测量方便永久删除缓存。**

最终验证必须覆盖两条路径：

| 场景 | 验证目标 |
| --- | --- |
| clean install / upgrade first launch | 插件生效后不再因为无 SP 缓存而回退 Dex 扫描 |
| cache-hit cold start | 后续启动保持正常，路由表仍完整注册 |

另外，项目当前 Debug 配置可以关闭插桩。AS Profiler 用于紧急复现和归因；证明生产修复效果时，应使用 Release 或显式开启 Transform 的 Benchmark 变体。

### 6.4 性能与功能验证

性能验证分首次冷启动和后续启动看。

首次冷启动收益最明显。没有可用 SP 缓存时，原路径会打开 Dex 并遍历类名；插桩后改为直接执行 `loadRouterMap()` 中的 `register(...)`。

本地 Profiler/验证数据为：

| 指标 | 修复前 | 修复后 |
| --- | ---: | ---: |
| ARouter 初始化 | 约 7.84s | 100ms 以内 |
| 本地整段冷启动 | 约 9.4s | 约 1.54s |

这些数字来自本地低端机和 Profiler 区间，不应与线上 P50/P90 混为一组数据。

后续启动原来可能命中 `SP` 缓存，不一定每次都重新扫描 dex。这个场景下原方案大致是一次 `SharedPreferences` 读取，加上遍历缓存中的 routes 类名、反射装载路由表。正常情况下耗时可能是几十毫秒级，具体取决于路由表数量和设备 I/O 状态；插件方案则进一步变成直接执行 `loadRouterMap()` 中的 `register(...)` 方法调用，通常可以压到几毫秒到十几毫秒级，并且不受新安装、包更新、debug 安装导致缓存失效的影响。

灰度修复结果按增量治理口径表达为：

```text
原稳定版 LOW P90：约 4.5s
升级候选版 LOW P90：约 12.8s
修复版 LOW P90：约 4.5s
```

因此消除的是候选版相对稳定版新增的约 8.3 秒，而不是把应用原本的 4.5 秒存量耗时也一起优化掉。修复完成后，启动路线回到原有冷启动基线，剩余 4.5 秒继续由存量治理负责。

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

### 6.5 回填增量防线

事故修复后，不能只把代码合进去，还要把漏网条件固化到防线：

```text
CI 场景
├── clean install first launch
├── upgrade first launch
└── cache-hit cold start

预算
├── startup.stage.app_init
└── startup.task.arouter.init

构建校验
├── 目标 variant 确实执行插桩任务
├── loadRouterMap 中存在 register 调用
├── registerByPlugin 路径生效
└── Java 21 / AGP 8 / Release 构建矩阵通过
```

CI 不应把第一次启动当作可丢弃的 warm-up。首次安装和升级后的第一次启动必须单独出结果，并直接检查 `arouter.init` Task 是否超预算。

### 6.6 工程落地表达

可以这样表达：

```text
落地过程中不是简单引入一个插件。原版 arouter-register 不兼容 AGP8，这点我是先从 GitHub issue 里确认的。后面接了一个兼容 AGP8 的三方插件源码，又遇到 Java 21 字节码读取失败，报 Unsupported class file major version 65。

我继续看源码，定位到插件使用 ASM ClassReader 读取 class 文件时，会检查 class 文件头里的 version，而 Java 21 是 major version 65，旧 ASM 版本不支持，所以我 fork 插件升级 ASM，并处理 ASM API 和依赖问题。修复后我也给对方百星项目提了 PR，作者邮件感谢，并在项目里对我做了致谢。

后面项目能编译通过后，启动耗时一开始并没有下降。我没有直接认为方案无效，而是补插件日志看 Gradle 构建过程，发现没有应用到目标 variant。最后定位到我们项目变体名是驼峰，原插件任务命名处理不兼容，修复后 loadRouterMap 才真正被插桩。

最终验证时，首次冷启动里 ARouter 初始化从秒级降到 100ms 以内，整体冷启动从约 9.4s 降到约 1.54s。后续启动原来可能走 SP 缓存，大概是几十毫秒级；插件方案变成直接方法注册，通常是几毫秒到十几毫秒级，并且规避了缓存失效后重新扫描 dex 的问题。功能上回归了页面跳转、Provider、Interceptor、多模块路由、debug/release 和不同 variant 构建。
```

## 7. 面试表达

### 7.1 两分钟主线

> 这个案例属于增量劣化治理。我们升级 Gradle/AGP 后，静态检查、CI Benchmark 和整包自动化都没有拦住，最终在灰度阶段触发告警。按版本和 LOW 档设备比较，P90 从原稳定版约 4.5 秒上升到 12.8 秒，相对增加约 8.3 秒。
>
> 我们沿统一埋点下钻到 `startup.stage.app_init`，再定位到 `startup.task.arouter.init` 横向增量最大。因为已经是 8 秒级单点异常，紧急阶段选择 AS Profiler 快速看调用栈，很快定位到 `ARouter.init → LogisticsCenter.init → ClassUtils.getFileNameByPackageName → openDexFileNative`，说明 register 插桩失效后回退到了运行时 Dex 扫描。
>
> 第一轮先查 GitHub issue，确认 Alibaba 原 `arouter-register` 依赖的 Transform API 在 AGP 8 被移除，于是接入支持 AGP 7.4+/8 的插件，把 routes 类扫描和 `loadRouterMap()` 注册前移到编译期。
>
> 后续升级 Java 21 又遇到 `Unsupported class file major version 65`。根因是插件中的旧 ASM `ClassReader` 不认识 Java 21 class。我们 fork 插件，将 ASM 依赖升级到 9.7、API 调整到 ASM9，并修复 Debug 变体大小写和目标 variant 未执行插桩的问题，发布自维护的 v1.0.5。
>
> Benchmark 还遇到一个坑：未插桩版本只有第一次慢，之后 ARouter 把扫描结果写入 SP，后续轮次命中缓存，导致中位数掩盖问题。我们给 Benchmark 变体增加测试专用的缓存失效机制，让每轮都能稳定复现首次扫描；最终验证则同时覆盖 first launch 和 cache-hit 两条路径。
>
> 修复后本地 ARouter 初始化从约 7.84 秒降到 100 毫秒以内。灰度 LOW P90 从候选版约 12.8 秒回到原基线约 4.5 秒，说明新增的约 8.3 秒劣化被消除。为了剥离 Gradle 本身的影响，我们比较旧 Gradle 稳定版、新 Gradle 故障版和新 Gradle 修复版，主要用同为新 Gradle 的故障版与修复版隔离 ARouter 收益。
>
> 最后把 clean install、upgrade first launch、cache-hit 三种场景，以及 `startup.stage.app_init`、`startup.task.arouter.init` 预算和插件生效校验回填 CI，避免相同问题再次穿透到灰度。

### 7.2 一句话收束

> **这次不是把 ARouter 做得比以前更快，而是修复构建升级导致的 register 插桩失效，消除新增的 8.3 秒劣化，让启动回到原本 4.5 秒的冷启动路线，并补上首次启动场景的增量防线。**

## 参考证据

- [Alibaba ARouter #1070：AGP 8 移除 registerTransform 后插件无法编译](https://github.com/alibaba/ARouter/issues/1070)
- [JailedBird/ArouterGradlePlugin：AGP 7.4+/8 自动注册插件](https://github.com/JailedBird/ArouterGradlePlugin)
- [JailedBird PR #16：Java 21 / ASM 兼容修复](https://github.com/JailedBird/ArouterGradlePlugin/pull/16)
- [项目自维护 jjjjjjava/ArouterGradlePlugin](https://github.com/jjjjjjava/ArouterGradlePlugin)
