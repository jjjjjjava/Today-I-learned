# K07 · JSBIND_PFUNCTION 异步语义

`JSBIND_PFUNCTION` 生成 Promise 适配、参数转换和非 JS 线程执行。调用时 JS 线程快速得到 Promise，FFmpeg 在 Native 执行器继续运行。

它不保证每次创建新线程，也不代表底层 fftools 可并发。

## 自检

1. 改成同步绑定会发生什么？
2. `P` 保证什么，不保证什么？
3. Promise 完成怎样回到 ArkTS？
