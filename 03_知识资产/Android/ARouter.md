# ARouter 面试复习笔记

## 第一节：ARouter 简述

### 1. ARouter 是什么？

ARouter 是 Android 组件化场景下常用的路由框架。

它的核心思想是：用 path 替代直接 Class 引用，通过路由表完成间接寻址，从而降低模块间依赖。

传统跳转需要直接依赖目标类：

```kotlin
ShopDetailActivity::class.java
```

ARouter 则可以通过路由地址完成间接寻址：

```kotlin
/shop/shopDetail
```

可以把它理解成一种“间接访问”：调用方不直接拿 `ShopDetailActivity.class`，而是通过 `/shop/shopDetail` 这个 `path` 去路由表中查找目标信息，最终再完成跳转。

### 2. ARouter 解决了什么问题？

#### 2.1 模块解耦

如果直接使用 `ShopDetailActivity.class`，调用方模块必须 `import` 目标模块的类，这会导致业务模块之间强依赖。

使用 ARouter 后，调用方只依赖 ARouter 和约定好的 `path`，不需要直接依赖目标页面所在模块。

本质变化是：

```text
直接 Class 引用 -> path 间接寻址
```

#### 2.2 动态跳转

服务端、运营配置、Push、H5 等场景可以下发字符串 `path`，客户端根据这个 `path` 找到对应页面并跳转。

#### 2.3 统一拦截

ARouter 可以在真正跳转前统一执行拦截逻辑。

例如进入某个页面前需要登录校验，拦截器可以统一判断 token 是否有效。如果未登录，就中断原跳转并跳转到登录页。

这样就不用在每个跳转入口重复编写登录判断逻辑。

### 3. ARouter 的工作链路

ARouter 的核心流程可以分成三步：

```text
编译期生成路由表
    ↓
App 初始化时加载路由表
    ↓
运行时根据 path 查表跳转
```

#### 3.1 编译期生成路由表

编译期通过 APT 注解处理器 `RouteProcessor` 扫描代码中的 `@Route` 注解。

Javac 会把当前编译轮次的信息通过 `RoundEnvironment` 传给处理器。处理器读取注解信息后，生成对应的路由表 Java 文件，主要包括：

```text
Root
Group
Provider
```

#### 3.2 App 初始化时加载路由表

App 启动时调用：

```kotlin
ARouter.init(application)
```

ARouter 会通过 `LogisticsCenter` 加载生成的路由表，并把索引存入 `Warehouse`。

常见加载方式有两类：

```text
运行时扫描 Dex，找到生成的路由表类
Gradle 插件通过ASM提前进行字节码插桩，运行时直接注册路由表类
```

其中，SP 缓存只是用于缓存 Dex 扫描结果，减少重复扫描成本；它不是另一套路由表生成机制。

#### 3.3 运行时根据 path 查表跳转

调用：

```kotlin
ARouter.getInstance()
    .build("/shop/shopDetail")
    .navigation()
```

`build()` 会创建一次跳转请求，也就是 `Postcard`。

`navigation()` 时会去 `Warehouse` 查找对应的 `RouteMeta`，补全目标 `destination`、路由类型、参数等信息。

最后根据路由类型执行真正的操作，例如：

```text
Activity -> startActivity()
Fragment -> 创建 Fragment 实例并返回
Provider -> 获取服务实例
```

### 4.	 面试话术

ARouter 的核心是用 `path` 代替直接 `Class` 引用。编译期通过 APT 生成路由表，初始化时加载到 `Warehouse`，运行时 `navigation()` 根据 `path` 查到 `RouteMeta`，补全 `Postcard` 后完成页面跳转，从而实现组件解耦、动态跳转和统一拦截。

## 第二节：ARouter 核心基础概念

ARouter 中有三个非常核心的基础概念：

```text
RouteMeta：路由表中的一条路由元信息
Postcard：一次运行时跳转请求
Warehouse：ARouter 的运行时路由索引仓库
```

### 1. RouteMeta

`RouteMeta` 表示一条路由记录

例如：

```kotlin
@Route(path = "/shop/detail")
class ShopDetailActivity : Activity()
```

编译期生成的 Group 文件中，会出现类似这样的映射：

```text
"/shop/detail" -> RouteMeta(...)
```

`RouteMeta` 中比较核心的信息包括：

```text
destination：目标 Class，例如 ShopDetailActivity.class
type：目标类型，例如 Activity、Fragment、Provider
path：完整路由路径，例如 /shop/detail
group：路由分组，例如 shop
```

所以 `RouteMeta` 的作用是描述：某个 `path` 最终对应哪个目标类，以及这个目标属于什么类型。

### 2. Postcard

`Postcard` 表示一次运行时跳转请求。

当调用：

```kotlin
ARouter.getInstance()
    .build("/shop/detail")
```

`build()` 会创建一个 `Postcard`，里面先保存本次跳转的 `path`、`group`、参数、`Bundle`、`flags` 等信息。

当继续调用：

```kotlin
.navigation()
```

ARouter 会让这个 `Postcard` 经过一系列处理，其中最核心的一步是：

```text
LogisticsCenter.completion(postcard)
```

这一步会去 `Warehouse` 中根据 `path` 查找对应的 `RouteMeta`，然后把目标 `destination`、`type` 等信息补全到 `Postcard` 中。

补全之后，如果类型是 `Activity`，就组装 `Intent` 并执行 `startActivity()`；如果类型是 `Fragment`，就创建 Fragment 实例并返回；Provider 也可以通过类似方式获取服务实例。

### 3. Warehouse

`Warehouse` 是 ARouter 的运行时路由索引仓库。

它里面最关键的两个结构是：

```text
groupsIndex：group -> Group Class
routes：path -> RouteMeta
```

`groupsIndex` 保存的是分组索引，例如：

```text
shop -> ARouter$$Group$$shop.class
```

`routes` 保存的是具体路由信息，例如：

```text
/shop/detail -> RouteMeta(ShopDetailActivity.class)
```

ARouter 初始化时，`LogisticsCenter.init()` 会先加载 Root 文件，把 group 索引放入 `Warehouse.groupsIndex`。

当第一次访问：

```text
/shop/detail
```

如果 `Warehouse.routes` 中还没有这条路由，ARouter 会根据 group `shop` 去 `groupsIndex` 找到：

```text
ARouter$$Group$$shop.class
```

然后加载这个 Group，把该分组下所有：

```text
path -> RouteMeta
```

放入 `routes` 中。

这就是 ARouter 的分组懒加载设计：先加载 group 索引，再按需加载具体 `path` 对应的 `RouteMeta`。

### 4. 面试话术

`RouteMeta` 是一条路由元信息，描述 `path` 对应的目标 `Class`、类型、`group` 等；`Postcard` 是一次跳转请求，`build(path)` 时创建，`navigation()` 时通过 `LogisticsCenter.completion()` 从 `RouteMeta` 中补全目标信息；`Warehouse` 是运行时路由仓库，里面保存 `groupsIndex` 和 `routes`。初始化时先加载 group 索引，真正访问某个 `path` 时再按需加载对应 group 下的 `RouteMeta`。

## 第三节：路由表生成原理

本节核心问题：

```text
ARouter 如何把 @Route 注解变成路由表 Java 文件？
```

核心链路：

```text
业务类上写 @Route(path = "/shop/detail")
↓
Javac 调用 RouteProcessor
↓
编译期 RouteProcessor 拿到这个类的 Element
↓
通过APT技术，从 @Route 里读 path / group
从 Element 判断目标类型和目标 Class
↓
封装成 RouteMeta
↓
按 group 放入 groupMap
↓
通过JavaPoet技术生成 ARouter$$Group$$shop
    loadInto(routes): "/shop/detail" -> RouteMeta(...)
↓
生成 ARouter$$Root$$app
    loadInto(groupsIndex): "shop" -> ARouter$$Group$$shop.class
↓
运行时 init 先加载 Root 到 Warehouse.groupsIndex
↓
真正访问 /shop/detail 时再懒加载 Group 到 Warehouse.routes
```

### 1. APT 和 JavaPoet

APT 是注解处理技术，全称是 Annotation Processing Tool。

它的作用是在编译期扫描注解，并根据注解信息生成代码或做校验。

ARouter 使用 APT 扫描 `@Route` 注解，然后生成路由表 Java 文件。

JavaPoet 是 Java 代码生成库。

它的作用是用代码生成 Java 源文件。ARouter 用 JavaPoet 生成 `ARouter$$Group$$xxx`、`ARouter$$Root$$xxx`、`ARouter$$Providers$$xxx` 这些路由表文件。

可以简单理解为：

```text
APT 负责扫描注解
JavaPoet 负责生成 Java 文件
```

### 2. RouteProcessor 的作用

`RouteProcessor` 是 ARouter 的注解处理器。

在编译期，Javac 会在注解处理阶段调用 `RouteProcessor.process()`。

处理器会通过：

```java
roundEnv.getElementsAnnotatedWith(Route.class)
```

拿到所有被 `@Route` 标注的类。

例如：

```kotlin
@Route(path = "/shop/detail")
class ShopDetailActivity : Activity()
```

在编译器眼中，`ShopDetailActivity` 会被抽象成一个 `Element`。

通过这个 `Element` 可以拿到类名、包名、父类、接口、注解等信息。

### 3. RouteMeta 的生成

拿到 `Element` 后，`RouteProcessor` 会做几件事：

```text
判断目标类型：Activity / Fragment / Provider / Service
读取 @Route 注解中的 path 和 group
收集 @Autowired 参数信息
生成 RouteMeta
```

例如：

```text
path = /shop/detail
group = shop
destination = ShopDetailActivity.class
type = ACTIVITY
```

如果没有手动指定 `group`，ARouter 会从 path 中提取第一段作为 group：

```text
/shop/detail -> shop
/user/login -> user
```

`RouteMeta` 记录的就是某个 `path` 对应的目标类、类型、分组等元信息。

### 4. 为什么要按 group 分组

分 group 的目的是按需加载。

如果所有路由都在启动时一次性加载进内存，路由数量多时会影响启动性能。

所以 ARouter 会先按照 group 整理路由信息：

```text
shop group
    /shop/detail -> RouteMeta
    /shop/cart -> RouteMeta

user group
    /user/login -> RouteMeta
```

每个 group 会生成一个对应的 Group 文件。

### 5. 生成的文件类型

ARouter 最终主要生成三类文件：

```text
ARouter$$Group$$groupName
ARouter$$Root$$moduleName
ARouter$$Providers$$moduleName
```

它们的作用分别是：

```text
Group 文件：保存 path -> RouteMeta
Root 文件：保存 group -> Group Class
Provider 文件：保存 Provider 服务映射
```

例如：

```text
ARouter$$Group$$shop
    /shop/detail -> RouteMeta(ShopDetailActivity.class)
```

```text
ARouter$$Root$$app
    shop -> ARouter$$Group$$shop.class
```

生成流程可以理解为：

```text
先按 group 整理出 groupMap
遍历 groupMap 生成每个 Group 文件
同时记录 rootMap：group -> Group Class
最后根据 rootMap 生成 Root 文件
```

### 6. 和 Warehouse 懒加载的关系

编译期生成的 Root 和 Group 文件，会在运行时被加载到 `Warehouse` 中。

初始化时，ARouter 先加载 Root 文件，把下面的信息放入 `groupsIndex`：

```text
group -> Group Class
```

也就是：

```text
shop -> ARouter$$Group$$shop.class
```

真正访问：

```text
/shop/detail
```

时，如果 `routes` 中没有对应的 `RouteMeta`，ARouter 会根据 group `shop` 去 `groupsIndex` 找到 `ARouter$$Group$$shop.class`。

然后通过反射创建 Group 实例，调用它的 `loadInto()` 方法，把该 group 下的：

```text
path -> RouteMeta
```

加载进 `routes`。

这就是 ARouter 路由表的分组懒加载设计。

### 7. 面试话术

ARouter 在编译期通过 APT 注解处理器 `RouteProcessor` 扫描 `@Route`。Javac 在注解处理阶段把当前轮次的编译环境 `RoundEnvironment` 传给处理器，处理器从中拿到被 `@Route` 标注的 `Element`，再解析 `path`、`group`、目标类型和目标类等信息，封装成 `RouteMeta`。随后按照 group 分组，通过 JavaPoet 生成 Group、Root、Provider 三类 Java 文件。Group 文件保存 `path` 到 `RouteMeta` 的映射，Root 文件保存 `group` 到 Group Class 的映射。这样运行时就可以先加载 Root 到 `Warehouse.groupsIndex`，真正访问某个 `path` 时再按需加载对应 Group 到 `Warehouse.routes`。

## 第四节：路由表加载与插件插桩优化

本节核心问题：

```text
编译期已经生成了 Root、Group、Provider 文件，App 启动时 ARouter 如何把它们加载到 Warehouse？
```

### 1. 路由表加载要做什么

上一节中，ARouter 已经通过 APT 和 JavaPoet 在编译期生成了路由表 Java 文件，比较关键的是：

```text
Root 文件：group -> Group Class
Group 文件：path -> RouteMeta
Provider 文件：Provider 服务映射
```

启动阶段要做的是：

```text
找到这些生成类
实例化它们
调用它们的 loadInto()
把索引放到 Warehouse
```

初始化时最关键的是加载 Root 文件：

```text
ARouter$$Root$$app.loadInto(Warehouse.groupsIndex)
```

得到：

```text
user -> ARouter$$Group$$user.class
shop -> ARouter$$Group$$shop.class
```

这里通常不是直接把所有 `path -> RouteMeta` 全量加载到 `routes`，而是先加载 `group -> Group Class`。

后续真正访问某个路由时，如果 `Warehouse.routes` 中没有对应的 `RouteMeta`，再根据 group 去 `Warehouse.groupsIndex` 找到对应的 Group Class，反射创建实例并调用 `loadInto(Warehouse.routes)`，把该 group 下的 `path -> RouteMeta` 加载进来。

### 2. 入口方法

调用链大致是：

```text
ARouter.init(application)
    ↓
_ARouter.init(application)
    ↓
LogisticsCenter.init(context, executor)
```

`LogisticsCenter.init()` 的核心逻辑可以理解成：

```text
先尝试插件注册：loadRouterMap()
如果 registerByPlugin == true，说明插件已经完成注册，跳过 Dex 扫描
如果插件没有注册成功，再走运行时 Dex 扫描
```

这里要注意：

```text
插件插桩注册 和 Dex 扫描注册 是两条加载路线
SP 缓存只是 Dex 扫描路线的优化，不是第三种独立加载方式
```

### 3. Dex 扫描加载

如果没有使用插件插桩，ARouter 需要在运行时扫描 Dex。

对于APT生成的路由表类，例如：

```text
ARouter$$Root$$app
ARouter$$Group$$user
ARouter$$Providers$$app
ARouter$$Interceptors$$app
```

它们都同属于如下的包名：

```text
com.alibaba.android.arouter.routes
```

Dex 扫描大致分三步：

```text
找到所有 Dex 路径
打开 Dex 并遍历其中的类名
筛选包名以 com.alibaba.android.arouter.routes 开头的类
```

拿到类名集合后，再根据类名前缀判断类型：

```text
ARouter$$Root$$xxx -> IRouteRoot
ARouter$$Providers$$xxx -> IProviderGroup
ARouter$$Interceptors$$xxx -> IInterceptorGroup
```

然后反射创建实例并调用 `loadInto()`：

```text
Root.loadInto(Warehouse.groupsIndex)
Provider.loadInto(Warehouse.providersIndex)
Interceptor.loadInto(Warehouse.interceptorsIndex)
```

Dex 扫描的本质是：

```text
运行时遍历 Dex 类名
找到 ARouter 生成类
反射调用 loadInto()
把索引写入 Warehouse
```

缺点是：Dex 多、类多时，遍历类名会增加启动耗时。

### 4.  SP 缓存优化

SP 缓存只服务于 Dex 扫描路线。

它缓存的是：

```text
上一次扫描到的 ARouter 生成类名集合
```

不是缓存完整路由表，也不是缓存 `RouteMeta` 对象。

逻辑大致是：

```text
Debug 模式 or App 新版本
    重新扫描 Dex
    把扫描到的类名集合存入 SP

Release 且版本未变化
    不重新扫描 Dex
    直接从 SP 读取上次扫描到的类名集合
```

从 SP 拿到类名后，后续仍然需要：

```text
Class.forName(className)
newInstance()
loadInto(Warehouse.xxx)
```

所以 SP 优化省掉的是：

```text
遍历 Dex 查找类名的成本
```

而不是省掉所有路由表加载成本。

### 5.字节码插桩方案

#### 5.1 前置：整体构建流程

理解字节码插桩前，先明确 Android 项目从点击运行按钮到生成 APK / AAB 的大致链路。这里要抓住四个核心阶段：

```text
配置阶段
Gradle 读取项目配置，AGP 创建 debug / release 等 variant。
ARouterPlugin 在这个阶段为每个 variant 注册 TransformAllClassesTask。
    ↓
编译阶段
JavaCompile / KotlinCompile 编译源码。
Javac 执行 RouteProcessor，扫描 @Route 注解，生成 ARouter$$Root$$xxx 等 Java 文件。
这些生成的 Java 文件继续被编译成 .class。
    ↓
字节码后处理阶段
AGP 汇总当前 variant 的所有 class 产物。
TransformAllClassesTask 接管这些 class，扫描路由表 class，并对 LogisticsCenter.class 做 ASM 插桩。
    ↓
Dex / 打包阶段
D8 将处理后的 class 转成 dex，最后打包成 APK / AAB。
```

这里要注意：

```text
RouteProcessor 属于 Javac 注解处理阶段，处理的是源码和注解信息。
ARouter Gradle 插件的 ASM 插桩属于字节码后处理阶段，处理的是已经编译完成的 .class 字节码。
```

因此：

```text
APT 负责生成路由表类
ASM 插桩负责把这些路由表类注册进 ARouter 初始化逻辑
```

为什么需要ASM插桩？

因为 ARouter 插件介入时，源码已经被编译成 `.class` 字节码文件，不再是可以直接修改的 `.java` 文件。

此时如果想往 `LogisticsCenter.loadRouterMap()` 中插入 `register("xxx")` 调用，不能像写业务代码一样直接改源码，也不能把 `.class` 当普通文本去查找 `loadRouterMap` 字符串后拼接内容。

`.class` 文件是结构化的二进制格式，里面包含常量池、类信息、字段表、方法表、字节码指令、栈帧等内容。要安全地找到某个方法，并在它的 `return` 指令前插入新的调用指令，就需要 ASM 这种能读懂和改写字节码结构的工具。

一句话：

```text
ASM 插桩就是在 class 后处理阶段，结构化地修改 .class 文件，把 register("生成类名") 插入到 loadRouterMap() 中。
```

#### 5.2 Gradle 插件如何介入 class 处理

插件插桩的目标是避免运行时 Dex 扫描。

核心思想是：

```text
既然 Root / Provider / Interceptor 这些生成类在编译期已经存在，
就可以在编译期提前扫描出来，
再把它们的注册调用写入最终 APK 中。
```

核心是通过 AGP 的 Artifacts API 接管当前 variant 的 `CLASSES` 产物

其会把当前 variant 的 class 产物，在进入 D8 之前，先交给 TransformAllClassesTask 处理。

```kotlin
variant.artifacts.forScope(ScopedArtifacts.Scope.ALL)
    .use(taskProviderTransformAllClassesTask)
    .toTransform(
        ScopedArtifact.CLASSES,
        TransformAllClassesTask::allJars,
        TransformAllClassesTask::allDirectories,
        TransformAllClassesTask::output
    )
```

AGP 会把 class 产物分成两类传给任务：

```text
allDirectories：目录形式的 class
allJars：jar 形式的 class
```

任务处理完成后输出新的 `output`，后续 D8 / 打包流程继续使用这份处理后的 class。

因此这不是简单的“编译结束回调”，而是插件插入了 AGP 的 class artifact 管线。

#### 5.3 插件扫描目标 class

我们通过ScanUtils，只扫描  com/alibaba/android/arouter/routes/ 这个包下的class，也就是 APT 生成的路由表类。

扫描时用 ASM 借助ClassReader 读取 class：

```kotlin
val cr = ClassReader(inputStream)
cr.accept(cv, ClassReader.EXPAND_FRAMES)
```

在 `ScanClassVisitor.visit()` 中读取字节码，查看当前 class 实现的接口：

```kotlin
interfaces?.forEach { itName ->
    if (itName == ext.interfaceName) {
        ext.classList.add(name)
    }
}
```

它关注三个接口：

```text
IRouteRoot
IInterceptorGroup
IProviderGroup
```

所以扫描结果就是：

```text
哪些类是 Root 路由表
哪些类是 Interceptor 路由表
哪些类是 Provider 路由表
```

#### 5.4 ASM 如何插桩 loadRouterMap()

插桩目标固定是：

```text
com/alibaba/android/arouter/core/LogisticsCenter.class
```

目标方法固定是：

```text
loadRouterMap()
```

任务遍历 jar 时，如果遇到 `LogisticsCenter.class`，不会直接复制原始 class，而是先把它的字节码缓存下来，最后统一插桩后再写入输出。

插桩核心流程：

```text
ClassReader 读取 LogisticsCenter.class
    ↓
ClassVisitor 找到 loadRouterMap 方法
    ↓
MethodVisitor 访问方法指令
    ↓
在 return 指令前插入 register 调用
    ↓
ClassWriter 输出修改后的 class 字节码
```

关键代码等价于：

```java
LogisticsCenter.register("com.alibaba.android.arouter.routes.ARouter$$Root$$app");
LogisticsCenter.register("com.alibaba.android.arouter.routes.ARouter$$Interceptors$$app");
LogisticsCenter.register("com.alibaba.android.arouter.routes.ARouter$$Providers$$app");
```

所以 ASM 插桩的本质是：

```text
在编译后的 LogisticsCenter.class 中，
找到 loadRouterMap()，
在 return 前插入 register("生成类名") 调用。
```

运行时执行 `loadRouterMap()` 时，就能直接注册这些生成类，而不需要再扫描 Dex。

#### 5.5 为什么任务要复制 class

`TransformAllClassesTask` 是 transform 任务。

它消费旧的 `CLASSES`，必须产出一份新的完整 `CLASSES`。

所以它不能只修改 `LogisticsCenter.class`，还必须把其他 class 原样复制到输出中：

```text
普通 class：原样复制
路由表 class：扫描后原样复制
LogisticsCenter.class：先缓存，不复制原始版本
最后：写入插桩后的 LogisticsCenter.class
```

否则后续 D8 可能拿不到完整 class，或者出现重复 entry。

#### 5.6 Java 17 / Java 21 兼容问题

插件处理的是 `.class` 字节码，不是 Java 源码。

ASM 的 `ClassReader` 读取 class 文件时，必须能识别 class 文件头里的 major version。

常见版本对应关系：

```text
Java 17 -> major version 61
Java 21 -> major version 65
```

如果插件运行时使用的 ASM 版本太旧，不认识这些 class 版本，就可能报：

```text
Unsupported class file major version 61
Unsupported class file major version 65
```

仓库中 `5e89527` 的关键修复是把 ASM 9.7 改成插件运行时依赖：

```kotlin
implementation("org.ow2.asm:asm:9.7")
implementation("org.ow2.asm:asm-commons:9.7")
implementation("org.ow2.asm:asm-tree:9.7")
```

所以根因是：

```text
旧 ASM 的 ClassReader 读不懂 Java 17 / 21 编译出来的 class 文件。
```

修复方向是：

```text
确保插件运行时真正使用支持 Java 17 / 21 class version 的 ASM 版本。
```

#### 5.7 面试话术

ARouter 的路由表加载发生在 `ARouter.init()` 阶段，最终进入 `LogisticsCenter.init()`。加载目标是把编译期生成的 Root、Provider、Interceptor 等索引类加载到 `Warehouse` 中。默认方式是运行时扫描 Dex，在 `com.alibaba.android.arouter.routes` 包下找到生成类，再通过反射创建实例并调用 `loadInto()`。其中 Root 会把 `group -> Group Class` 写入 `Warehouse.groupsIndex`。Dex 扫描比较耗时，所以 ARouter 会用 SP 缓存扫描到的类名集合，在非新版本的 Release 场景下复用结果。进一步的优化是 Gradle 插件插桩：插件在 class 进入 D8 前介入，扫描 APT 生成的路由表 class，收集实现了 `IRouteRoot`、`IInterceptorGroup`、`IProviderGroup` 的类名，然后用 ASM 修改 `LogisticsCenter.loadRouterMap()`，在 return 前插入 `LogisticsCenter.register(...)`，从而把运行时 Dex 扫描变成编译期字节码插桩。Java 17 / 21 不兼容的根因是旧 ASM 的 `ClassReader` 读不懂新版本 class 文件头，需要确保插件运行时真正使用支持新 class version 的 ASM。

## 第五节：运行时跳转主流程

本节只关注运行时跳转主线：

```text
build(path) 创建 Postcard
navigation() 触发跳转
completion() 查表并补全 Postcard
根据 type 执行最终操作
```

### 1. build(path)：创建 Postcard

用户调用：

```kotlin
ARouter.getInstance()
    .build("/user/login")
```

这一步会创建一个 `Postcard`。

此时 `Postcard` 中主要包含：

```text
path = /user/login
group = user
参数 Bundle
flags
动画等跳转配置
```

但此时它还不完整，还没有真正的目标 `Class`。

### 2. navigation()：进入跳转流程

继续调用：

```kotlin
.navigation()
```

会进入 `_ARouter.navigation()`。

这里会有预处理、降级、拦截器等流程控制，但主线是进入：

```text
LogisticsCenter.completion(postcard)
```

### 3. completion(postcard)：查表并补全 Postcard

`completion()` 会先查：

```text
Warehouse.routes[path]
```

如果找到了：

```text
/user/login -> RouteMeta(UserLoginActivity.class)
```

就把 `RouteMeta` 中的信息补全到 `Postcard`：

```text
destination = UserLoginActivity.class
type = ACTIVITY
priority
extra
参数类型信息
```

如果 `routes` 中没找到，说明对应 group 还没有加载。

这时会：

```text
从 path 中拿到 group = user
去 Warehouse.groupsIndex 找 ARouter$$Group$$user.class
反射创建 Group 实例
调用 loadInto(Warehouse.routes)
把 user 组下的 path -> RouteMeta 加载进 routes
再重新 completion()
```

所以 `completion()` 的本质是：

```text
根据 path 找 RouteMeta，并把 RouteMeta 填充到 Postcard。
```

### 4. 根据 type 执行最终操作

补全 `Postcard` 后，ARouter 会根据 `type` 决定最终操作：

```text
ACTIVITY -> 创建 Intent，放入 extras，startActivity()
FRAGMENT -> 反射创建 Fragment 实例，设置 arguments，然后返回
PROVIDER -> 获取或创建 Provider 实例
```

运行时跳转的最短链路是：

```text
Postcard(path)
    ↓
Warehouse.routes 查 RouteMeta
    ↓
找不到就通过 groupsIndex 懒加载 Group
    ↓
RouteMeta 补全 Postcard
    ↓
根据 type 跳转 / 返回实例
```

### 5. 面试话术

ARouter 运行时跳转时，`build(path)` 会先创建一个 `Postcard`。`navigation()` 后会进入 `LogisticsCenter.completion()`，根据 `path` 去 `Warehouse.routes` 查找 `RouteMeta`。如果 `routes` 中没有，就根据 group 从 `Warehouse.groupsIndex` 懒加载对应 Group，把 `path -> RouteMeta` 加载进 `routes`。拿到 `RouteMeta` 后，会把 `destination`、`type` 等信息补全到 `Postcard`。最后根据 `type`，如果是 Activity 就组装 Intent 并 `startActivity()`，如果是 Fragment 就创建实例并返回，如果是 Provider 就返回对应服务。
