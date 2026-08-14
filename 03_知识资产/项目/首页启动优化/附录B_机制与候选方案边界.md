# 附录 B｜这些机制与本次优化是什么关系？

## 本篇只解决一个问题

Tinker、ContentProvider、DAG 和 Baseline Profile 都与启动有关，哪些是现有机制，哪些只是后续候选？

| 内容 | 项目中的身份 | 计入本次收益 |
|---|---|---|
| Tinker | 现有启动机制背景 | 否 |
| ContentProvider 治理 | P2 候选 | 否 |
| DAG 初始化编排 | 初步设计，未落地 | 否 |
| Baseline Profile | 待验证候选 | 否 |
| ViewPager2 懒加载 | P0 已落地 | 是 |
| WebView 按需创建 | P0 已落地 | 是 |

## Tinker 为什么出现在启动流程？

Tinker 用补丁包更新 dex、资源或 native library。它是热修复框架，不是启动优化方案。

补丁检查和加载通常发生在 Application 前置阶段：

```text
系统创建 TinkerApplication
→ attachBaseContext
→ 检查并准备补丁
→ 建立补丁类加载关系
→ 继续业务 Application 生命周期
```

Dex 补丁的高层原理，是让补丁中的业务类在类查找时拥有更高优先级。

低版本可能把补丁 `dexElements` 插到原搜索数组前面；其他版本可能使用新的补丁 ClassLoader。具体实现取决于 Tinker 和 Android 版本。

已经加载的旧类通常不会在同一进程内被同名补丁类替换，因此 Dex 补丁一般需要重启进程生效。

本项目没有 Tinker 优化前后的对照数据，所以它只用于解释启动背景。

## ContentProvider 为什么可能拖慢启动？

三方 SDK 可以在 Manifest 中声明 Provider。系统会在应用启动时创建它并调用 `onCreate()`，不要求业务主动调用 SDK。

因此 Provider 内的类加载、数据库、文件 IO 或 SDK 初始化可能在 `Application.onCreate()` 前进入主线程路径。

确认方式是检查合并后的 Manifest，再结合 Perfetto 和 SDK 文档定位具体初始化。确认非首屏依赖后，才考虑关闭自动初始化或改为业务入口按需初始化。

本项目 `bindApplication` 约 220ms，不是本轮最大热点，因此 Provider 治理保留为 P2。

## DAG 想解决什么问题？

项目的 `Application.onCreate()` 涉及 Network、个推、WebRTC 和地图等 SDK。初步设想是把每段初始化声明为任务，并标注前置依赖、执行线程和业务优先级。

例如：

```text
NetworkConfig
→ HttpManager
→ OkGo
→ TokenHeader
→ Push

Map：进入地图前完成
WebRTC：进入音视频前完成
```

构图后统计每个任务的入度，先运行入度为 0 的节点；任务完成后减少后继入度，后继变为 0 时加入可执行队列。

DAG 不会减少任务本身。它只有在拆掉伪依赖、并行独立任务或后置非首屏任务时，才可能缩短首屏关键链。

这个方案没有正式落地，也没有 Benchmark、Trace 和线上结果，因此只能写成后续设计。类似“依赖环、隐藏线程要求、缺少降级”等通用工程风险不进入主笔记。

## Baseline Profile 怎样减少启动成本？

Java、Kotlin 代码最终编译成 DEX。ART 会结合解释执行、JIT、AOT 和运行时 Profile 执行这些代码。

Baseline Profile 随应用发布启动和关键交互涉及的类、方法规则。设备可以据此提前优化关键代码，减少首次启动时的解释执行和 JIT 成本。

它能改善必要代码的执行准备成本，却不能消除提前创建的 Fragment、静态 WebView、主线程 IO 或锁等待。

验证时要使用相同设备、Release 包、`StartupMode.COLD` 和业务场景，仅改变 Profile/编译条件，并比较多轮 TTID、项目区间和 Trace。

原资料没有提供 Profile 生成、安装确认和对照结果，因此 Baseline Profile 仍是候选，不计入本次 P0 收益。

## 四个典型判断

1. 项目接入 Tinker：只能说明它可能进入启动前置路径，不能说明它就是瓶颈。
2. Manifest 中存在三方 Provider：应先确认其耗时和业务依赖，不能直接删除。
3. DAG 任务全部改成并行：如果首屏仍等待所有任务，总关键链未必缩短。
4. Baseline Profile 文件已经生成：还需要确认打包、安装、编译状态和对照结果。

## 常见误区

1. 把热修复原理写成本次启动优化成果。
2. 把一种 Tinker 类加载实现描述成所有版本的统一行为。
3. 看到 Provider 就全部删除。
4. DAG 节点越多，启动就一定越快。
5. 用 Baseline Profile 掩盖非首屏 View 和 WebView 的过早创建。
6. 把未落地候选写进最终优化率。

## 本篇自测

1. Tinker 为什么通常需要重启进程后让 Dex 补丁生效？
2. Provider 为什么可能早于业务主动初始化？
3. DAG 真正需要缩短的是什么？
4. Baseline Profile 能解决和不能解决哪些成本？
5. 本次真正计入收益的是哪两个方案？

## 一句话总结

与启动有关不等于已经优化；只有完成对照验证的落地方案，才能计入本次项目收益。
