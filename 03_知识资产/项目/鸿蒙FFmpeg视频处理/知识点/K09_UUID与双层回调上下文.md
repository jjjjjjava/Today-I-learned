# K09 · UUID 与双层回调上下文

UUID 在 JS 函数表区分任务；`g_callbacks` 保存 C 桥函数地址；`g_currentCallback` 保存当前任务的 JS 函数句柄。

三者分别解决“哪个任务”“调用哪座桥”“桥最终回到哪个 JS 函数”。

## 自检

1. 为什么 C 函数指针不能直接保存 ArkTS 函数？
2. 两个全局量有什么区别？
3. UUID 与 thread_local 为什么不能互相替代？
