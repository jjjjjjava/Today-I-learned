# K09 · ContentProvider 初始化

系统在`Application.onCreate`前安装并调用ContentProvider。

多个三方库各自用Provider自动初始化，会把对象创建与初始化工作提前放进启动主链路。

治理：

- 审查Manifest合并结果；
- 删除不需要的自动初始化；
- 可延迟组件改为显式或懒初始化；
- 需要依赖关系时统一编排。

边界：Provider治理减少初始化入口与工作量，但不能消除框架必须执行的Provider安装阶段。

官方参考：[App Startup](https://developer.android.com/topic/libraries/app-startup)

检索题：

1. Provider与Application谁先？
2. 三方Provider为什么可能拖慢启动？
3. App Startup解决什么，不解决什么？
