# K02 · `bindApplication` 边界

`bindApplication`前主要经历Launcher、ATMS/AMS调度、Zygote fork和`ActivityThread.main`建立。

本项目从`bindApplication`开始，因为此后进入Application、Provider、Activity和首屏构建等业务相对可控链路。

边界：这是测量与治理范围选择，不代表点击到`bindApplication`绝对无法优化；那部分可控度与ROI更低，应另建问题。

检索题：

1. `bindApplication`前发生什么？
2. 为什么它适合作为本项目起点？
3. 如何避免把“业务相对不可控”说成“完全不可优化”？
