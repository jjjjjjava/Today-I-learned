# K12 · 两阶段扫描与LogisticsCenter

Class遍历顺序不确定。插件必须：

1. 扫描全部Class，收集完整Root、Provider、Interceptor类名；
2. 缓存`LogisticsCenter.class`；
3. 扫描完成后一次性插入全部`register()`。

若遇到`LogisticsCenter`就立即修改，只能写入当时已发现的类名，后出现的路由表会静默漏注册。

检索题：

1. 为什么不能立即修改LogisticsCenter？
2. 插桩依赖什么全量信息？
3. 立即插桩会产生什么功能风险？
