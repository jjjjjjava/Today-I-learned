# 02｜ARouter 为什么会在启动时扫描 Dex？

## 本篇只解决一个问题

Profiler 已经定位到 ARouter 打开 Dex。一次普通的路由跳转，为什么需要在应用初始化时发现路由表类？

## 从 `/user/login` 开始

传统跳转直接引用目标 Class：

```kotlin
Intent(context, UserLoginActivity::class.java)
```

ARouter 调用方只持有字符串 path：

```kotlin
ARouter.getInstance()
    .build("/user/login")
    .navigation()
```

调用方不知道 `UserLoginActivity.class`，因此运行时必须存在一张间接寻址表：

```text
/user/login → UserLoginActivity.class
```

## Postcard 什么时候知道目标页面？

`build(path)` 先创建 Postcard，保存 path、group、Bundle、flags 和动画等跳转信息。

如果没有显式指定 group，通常从 path 第一段提取：

```text
/user/login → group = user
```

此时 Postcard 还不知道 destination 和路由类型。调用 `navigation()` 后，流程进入：

```text
LogisticsCenter.completion(postcard)
```

`completion()` 根据 path 查找 RouteMeta，再用其中的 destination、type、priority 和 extra 补全 Postcard。Activity 类型最终组装 Intent 并调用 `startActivity()`。

## Warehouse 为什么分成 Root 和 Group？

与页面路由直接相关的两个仓库是：

```text
groupsIndex：group → Group Class
routes：path → RouteMeta
```

初始化时，Root 先把下面的索引写进 `groupsIndex`：

```text
user → ARouter$$Group$$user.class
```

第一次访问 `/user/login` 时，如果 `routes` 中没有 RouteMeta，`completion()` 才根据 group 找到 Group Class，并调用：

```text
Group.loadInto(Warehouse.routes)
```

于是该组的 `path → RouteMeta` 被加载，再次查询即可补全 Postcard。

Root 在初始化时建立分组索引，Group 在首次访问时加载具体路由。这保留了分组懒加载，也解释了插件为什么不需要直接注册全部 Group。

## `@Route` 怎样变成路由表 Class？

业务页面声明：

```kotlin
@Route(path = "/user/login")
class UserLoginActivity : Activity()
```

编译期生成链如下：

```text
@Route
→ RouteProcessor
→ RoundEnvironment 取得标注 Element
→ 解析注解和类型
→ 构造 RouteMeta
→ 按 group 整理
→ JavaPoet 生成 Java 源码
→ 编译为 Class
```

主要生成物：

| 生成类 | 保存内容 |
|---|---|
| `ARouter$$Root$$app` | `group → Group Class` |
| `ARouter$$Group$$user` | `path → RouteMeta` |
| `ARouter$$Providers$$app` | Provider 服务映射 |
| `ARouter$$Interceptors$$...` | 拦截器索引 |

APT 结束只表示这些 Class 已经进入构建产物。应用初始化时仍要找到 Root、Provider、Interceptor，并调用它们的 `loadInto()`。

## 初始化怎样找到这些生成类？

`LogisticsCenter.init()` 先调用 `loadRouterMap()`，随后根据插件注册是否生效，在两条路径中选择。

### 插件注册路径

插件成功插桩后，`loadRouterMap()` 中会出现：

```java
register("com.alibaba.android.arouter.routes.ARouter$$Root$$app");
register("com.alibaba.android.arouter.routes.ARouter$$Providers$$app");
register("com.alibaba.android.arouter.routes.ARouter$$Interceptors$$app");
```

运行时直接根据这些已知类名创建生成类并执行 `loadInto()`，`registerByPlugin` 生效后跳过 Dex 扫描。

插件没有删除路由表加载，只删除了“运行时到哪里寻找这些生成类”的全量发现成本。

### Dex 扫描路径

如果 `loadRouterMap()` 没有注册成功，ARouter 会回退到：

```text
获取 APK 中的 Dex 路径
→ 逐个打开 Dex
→ DexFile.entries() 枚举全部类名
→ 按 routes 包名前缀筛选
→ 按 Root / Provider / Interceptor 类名前缀分类
→ 反射创建并执行 loadInto()
```

真正昂贵的不是几次 `startsWith()`，而是为了找到少量生成类，必须打开多个 Dex 并遍历全部类名。

本项目 APK 体量超过 400MB，同时 Dex 和类数量较多，因此运行时全量发现成本被明显放大。APK 体量是项目背景，不等于 Dex 文件本身有 400MB。

## AGP 升级怎样让快速路径退回慢路径？

旧 `arouter-register` 插件依赖 Transform API 接入 Class 处理流程。升级到新的 AGP 后，旧接入方式无法继续正确完成插桩。

结果是：

```text
loadRouterMap 缺少完整 register()
→ registerByPlugin=false
→ ClassUtils.getFileNameByPackageName
→ 打开并遍历 Dex
→ openDexFileNative 出现秒级聚合耗时
```

完整根因不是“Dex 很慢”，而是构建升级破坏了编译期注册链，运行时因此回退到适合兜底、却不适合当前项目体量的发现方式。

## 三个典型判断

1. APT 已生成 Root 和 Group：只能证明路由表存在，不能证明初始化已经装载。
2. 插件路径仍执行 `loadInto()`：它消除的是发现成本，不是删除所有初始化工作。
3. 初始化不直接注册 Group：Root 已经间接索引 Group，全部注册反而会破坏懒加载。

## 常见误区

1. 把 Postcard 当成完整路由表。
2. 认为 APT 生成完成后，运行时不再需要加载。
3. 认为插件把全部 Group 提前注册。
4. 把字符串前缀匹配说成 7 秒耗时的主要来源。
5. 只看到 `openDexFileNative`，就跳过构建产物直接认定 AGP 根因。

## 本篇自测

1. Postcard 与 RouteMeta 分别保存什么？
2. Root 与 Group 为什么分开？
3. `@Route` 怎样变成生成类？
4. 插件注册和 Dex 扫描分别怎样发现路由表类？
5. AGP 升级怎样最终触发 `openDexFileNative`？

## 一句话总结

ARouter 必须先找到编译期生成的路由表；插件失效后，这项发现工作从编译期退回运行时全量 Dex 扫描，最终制造秒级启动增量。
