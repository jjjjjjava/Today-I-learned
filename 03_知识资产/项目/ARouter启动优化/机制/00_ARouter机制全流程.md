# ARouter机制全流程

> 学习顺序：跳转 → 生成 → 加载。
> 因果执行顺序：生成 → 加载 → 跳转。

## 三阶段

### 1. 路由跳转

```text
build(path)
→ Postcard
→ navigation
→ LogisticsCenter.completion
→ Warehouse查RouteMeta
→ 按Activity/Fragment/Provider类型执行
```

入口：[[M01_路由跳转]]

### 2. 路由生成

```text
@Route
→ RouteProcessor
→ RoundEnvironment / Element
→ RouteMeta
→ JavaPoet
→ Root / Group / Provider Class
```

入口：[[M02_路由生成]]

### 3. 路由加载

```text
编译期插件注册 或 运行时Dex扫描
→ 找到Root/Provider/Interceptor
→ loadInto Warehouse
→ Root索引Group
→ Group按需加载具体RouteMeta
```

入口：[[M03_路由加载]]

## 项目中的故障点

项目7～8秒劣化发生在“加载”阶段：

```text
编译期注册失效
→ 运行时为了发现路由表打开并遍历Dex
```

Java 21故障也发生在“加载”阶段的编译期插件：

```text
旧ASM无法读取major version 65
→ 插件无法完成Class扫描与插桩
```

## 综合评分

1. 三阶段职责清楚。
2. 能区分编译期、初始化期、导航期。
3. 能解释Root与Group懒加载。
4. 能解释插件消除“发现成本”，不删除`loadInto()`。
5. 能把两轮事故定位到加载阶段的不同位置。
