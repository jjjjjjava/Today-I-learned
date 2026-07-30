# 阶段四 · 第一轮：AGP升级与Dex扫描治理

> 本轮完整包含触发、证据、根因、方案、落地困难和验证。
> 事实源：[[../ARouter启动优化笔记#6.1 实现过程中遇到的困难和问题]]

## 1. 正常快速路径

```text
APT生成路由表Class
→ Gradle插件收集Root/Provider/Interceptor
→ 插桩LogisticsCenter.loadRouterMap
→ 运行时register
→ registerByPlugin=true
→ 跳过Dex扫描
```

## 2. 触发与根因

Alibaba旧`arouter-register`依赖旧Transform API。升级AGP 8后，原接入方式无法继续正确处理目标Class产物。

结果：

```text
loadRouterMap缺少register
→ registerByPlugin=false
→ ClassUtils.getFileNameByPackageName
→ 打开并遍历Dex
→ openDexFileNative产生秒级成本
```

完整证据：

1. 灰度增量集中在`arouter.init`。
2. Profiler进入Dex扫描调用栈。
3. 构建产物缺少完整`register()`。
4. 相关issue确认旧插件的新AGP兼容问题。
5. 恢复插桩后Dex扫描大块消失。

## 3. 方案比较

| 方案 | 问题 | 结论 |
|---|---|---|
| 异步初始化 | 不消除扫描；引入路由可用时序 | 不治本 |
| 更换路由框架 | 改造与回归范围过大 | 成本过高 |
| 恢复编译期注册 | 直接消除运行时发现成本 | 采用 |

第一轮接入兼容AGP Artifacts API的插件。

## 4. 落地困难

插件能编译，不代表目标variant真正执行插桩。项目variant使用驼峰命名，原任务匹配未正确覆盖，导致启动耗时没有下降。

补构建日志后定位variant命名问题。修复后，目标variant的`loadRouterMap()`才真正包含完整`register()`。

## 5. 验证

### 产物与运行路径

- `loadRouterMap()`存在完整`register()`。
- `registerByPlugin=true`。
- 缓存失效时不进入`ClassUtils.getFileNameByPackageName`。
- `openDexFileNative`大块消失。

### ABC控制变量

- A：旧AGP，插件正常。
- B：新AGP，插桩失效。
- C：新AGP，插桩修复。

`B→C`隔离ARouter修复；`A→C`观察AGP升级后剩余差异。

### 性能与功能

- 本地ARouter初始化约7.84s降到100ms以内。
- 本地整段冷启动约9.4s降到1.54s。
- 灰度LOW档P90从12.8s恢复到约4.5s。
- 页面、Provider、Interceptor、多模块和目标variant回归通过。

## 6. 结论边界

不能说“Gradle升级本身产生全部8.3s”。准确结论：

> Gradle/AGP升级触发插件注册链失效；同AGP环境恢复插桩后，新增ARouter耗时基本消失。

## 复习检查

1. AGP升级怎样让快速路径退回Dex扫描？
2. 为什么恢复插件比异步更治本？
3. 为什么构建成功仍可能没有性能收益？
4. ABC实验怎样隔离变量？
5. 第一轮必须验证哪些层？
