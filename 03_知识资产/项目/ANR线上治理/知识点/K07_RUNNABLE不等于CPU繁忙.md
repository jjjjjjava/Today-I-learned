# K07 · RUNNABLE 不等于 CPU 繁忙

JVM 的 `RUNNABLE` 可能表示：

- 正在执行 Java/Kotlin 计算；
- 可运行但暂未获得 CPU；
- 进入 native IO；
- 正在同步 Binder；
- 内核调用尚未返回。

必须继续看栈顶与完整业务调用链。`RUNNABLE + FileOutputStream.write` 支持主线程处于文件 IO 路径，不自动证明它持续阻塞了整个超时窗口。

## 相关

- [[../阶段/05_单点归因_主线程与堆栈状态]]
- [[K11_主线程同步IO]]
