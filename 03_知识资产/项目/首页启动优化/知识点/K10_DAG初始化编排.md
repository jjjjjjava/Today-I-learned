# K10 · DAG 初始化编排

DAG用于显式表达初始化任务依赖：

```text
节点：初始化任务
边：前置依赖
```

只有无依赖且线程安全的任务才能并行；非首屏任务可延迟或按需触发。DAG解决顺序、依赖、并行机会和可观测性，不会自动减少总工作量。

Jetpack App Startup通过`Initializer.dependencies()`表达依赖，并可把多个组件聚合到共享Provider；也支持手动懒初始化。

边界：本项目P0是UI关键路径裁剪，不是DAG落地。DAG是Application初始化后续治理工具。

官方参考：[App Startup](https://developer.android.com/topic/libraries/app-startup)

检索题：

1. DAG的节点和边是什么？
2. 哪些任务可以并行或延迟？
3. DAG为什么不等于“全部异步”？
