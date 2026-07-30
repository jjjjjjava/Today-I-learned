# K03 · Profiler证据边界

本次异常是秒级单点，AS CPU Profiler Sampling适合快速定位主要调用栈：

```text
ARouter.init → LogisticsCenter.init → openDexFileNative
```

它能证明本地候选版本进入Dex扫描，并显示主要耗时方向。

它不能直接证明：

- 线上绝对耗时；
- 精细毫秒级收益；
- AGP升级就是唯一根因；
- 插件修复已经在所有variant生效。

检索题：

1. 为什么本次优先Profiler？
2. Sampling数据能承担什么证据职责？
3. 最终收益还需要哪些证据？
