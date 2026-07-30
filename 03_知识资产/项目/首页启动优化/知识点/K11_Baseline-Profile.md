# K11 · Baseline Profile

Baseline Profile向ART提供常用代码路径规则，使安装时可对命中路径做AOT编译，减少首次运行时的解释与JIT成本。

它适合：

- App启动关键代码路径；
- 页面导航、滚动等关键用户旅程。

它不直接解决：

- 非首屏View创建过多；
- WebView错误进入关键路径；
- 网络等待；
- 错误任务依赖与生命周期时序。

所以Baseline Profile是“让必要代码执行更快”，关键路径裁剪是“减少不必要工作”。两者可组合，不能互相替代。

本项目未把Baseline Profile作为P0真实实践。

官方参考：[Baseline Profiles overview](https://developer.android.com/topic/performance/baselineprofiles/overview)

检索题：

1. Baseline Profile优化什么？
2. 它为什么不能替代关键路径裁剪？
3. 如何避免把建议工具说成项目真实落地？
