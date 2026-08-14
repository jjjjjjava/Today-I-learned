# 03｜怎样让 ARouter 不再运行时扫描 Dex？

## 本篇只解决一个问题

第一轮根因已经确定：编译期注册失效，运行时回退 Dex 扫描。应该怎样恢复快速路径，并证明它真的生效？

## 三个方案应该选哪个？

### 异步初始化

异步只能把扫描移到其他线程，不能消除打开 Dex 和遍历类名的成本。

如果业务在初始化完成前发起路由，还要增加等待、失败或降级逻辑。耗时仍然存在，路由可用时机反而变得复杂。

### 更换路由框架

更换框架可以绕开当前实现，但项目大量使用页面路由、Provider、Interceptor 和多模块路由。迁移范围与功能回归成本都很高。

### 恢复编译期注册

ARouter 已经预留 `loadRouterMap()` 插件入口。恢复兼容新 AGP 的编译期注册，可以直接切断运行时发现成本，同时保持现有路由语义。

因此第一轮选择接入基于 AGP Artifacts API 的兼容插件。

## APT 和 ASM 分别发生在什么时候？

整个构建链可以分成四段：

```text
配置阶段：插件为目标 variant 注册 Class 处理任务
→ 源码编译：APT 生成路由表源码并编译成 Class
→ 字节码处理：插件扫描 Class，ASM 修改 LogisticsCenter
→ Dex 与打包：D8 将处理后的 Class 转成 Dex
```

APT 处理注解、Element 和源码，负责生成路由表类。ASM 处理已经编译完成的 `.class`，负责把注册调用写入初始化入口。

APT 不修改 `LogisticsCenter.class`，ASM 也不重新扫描业务源码中的 `@Route`。

## Artifacts API 给插件什么输入？

兼容插件从目标 variant 的 `ScopedArtifact.CLASSES` 管线取得：

```text
allDirectories：目录形式的 Class
allJars：Jar 形式的 Class
```

任务消费原 Class 集合后，必须输出一份完整的新集合给 D8。

因此插件不仅要修改目标 Class，还要复制其余所有 Class。漏复制会让 D8 缺少产物；同时输出原始和修改后的 `LogisticsCenter.class`，则可能产生重复 Entry。

## 插件怎样识别路由表 Class？

遍历 Jar Entry 或目录 Class 时，先按路径缩小候选范围：

```text
com/alibaba/android/arouter/routes/
```

候选类再交给 ASM：

```text
ClassReader
→ ScanClassVisitor.visit(..., name, ..., interfaces)
→ 根据实现接口分类
```

插件关注三个接口：

| 接口 | 收集结果 |
|---|---|
| `IRouteRoot` | Root 类名 |
| `IProviderGroup` | Provider 类名 |
| `IInterceptorGroup` | Interceptor 类名 |

运行时 Dex 扫描按类全限定名和生成类名前缀分类；编译期插件先按 Entry 路径筛选，再根据实现接口分类。两种方式不要混写。

Group 实现 `IRouteGroup`，但不加入直接注册列表。Root 已保存 `group → Group Class`，具体 Group 继续在首次访问时加载。

## 为什么不能遇到 `LogisticsCenter` 就立即插桩？

Class 遍历顺序不确定，可能先遇到 `LogisticsCenter.class`，后遇到一部分 Root、Provider 或 Interceptor。

如果立即修改，只能写入当时已经收集到的类名，后续生成类会静默漏注册。

正确过程分两阶段：

```text
阶段一：扫描全部 Class
├── 收集完整 Root / Provider / Interceptor 类名
├── 缓存 LogisticsCenter 原始字节码
└── 复制其他 Class

阶段二：修改 LogisticsCenter.class
├── 使用完整类名集合插入 register()
└── 输出修改后的 Class
```

这里暂存 `LogisticsCenter` 是为了等待完整输入信息，不是运行时缓存优化。

## ASM 怎样把 `register()` 写进去？

修改链如下：

```text
ClassReader
→ ClassVisitor
→ MethodVisitor
→ ClassWriter
```

`ClassVisitor` 找到无参、返回 void 的：

```text
loadRouterMap()V
```

`MethodVisitor` 遍历到 `Opcodes.RETURN` 时，在返回前为每个生成类写入两条关键指令。

第一条使用 `LDC` 把类名字符串压入操作数栈：

```kotlin
methodVisitor.visitLdcInsn(className)
```

第二条使用 `INVOKESTATIC` 调用：

```kotlin
methodVisitor.visitMethodInsn(
    Opcodes.INVOKESTATIC,
    "com/alibaba/android/arouter/core/LogisticsCenter",
    "register",
    "(Ljava/lang/String;)V",
    false
)
```

描述符表示接收一个 String、返回 void。`ClassWriter` 最后输出修改后的字节码，再交给 D8。

## 编译成功了，为什么启动还没有变快？

首次接入兼容插件后，项目可以编译，但启动耗时没有明显变化，构建日志中也没有目标 variant 的插桩记录。

继续补充日志并检查任务注册，最终发现项目 variant 使用驼峰命名，原插件的匹配逻辑没有正确覆盖，目标变体没有执行预期插桩。

修复 variant 命名后，`loadRouterMap()` 才真正出现完整 `register()`，运行时也不再进入 Dex 扫描。

这说明“插件成功应用”和“项目构建成功”都不是最终证据，必须检查目标 variant 的处理产物。

## 怎样证明第一轮修复有效？

先做 ABC 对照：

| 版本 | 构建环境 | 插件状态 |
|---|---|---|
| A | 旧 Gradle/AGP | 插件正常 |
| B | 新 Gradle/AGP | 插桩失效 |
| C | 新 Gradle/AGP | 插桩修复 |

`B → C` 保持新 AGP 不变，主要比较插桩是否生效，用于隔离 ARouter 修复收益。`A → C` 用于检查构建升级后是否还有其他剩余差异。

还要同时确认：

- 目标 variant 的 `loadRouterMap()` 含完整 `register()`；
- 运行时 `registerByPlugin=true`；
- 不再进入 `ClassUtils.getFileNameByPackageName()`；
- Profiler 中原有 `openDexFileNative` 大块消失；
- 页面、Provider、Interceptor 和多模块路由正常。

本地结果：

| 指标 | 修复前 | 修复后 |
|---|---:|---:|
| ARouter 初始化 | 约 7.84s | 100ms 以内 |
| 整段冷启动 | 约 9.4s | 约 1.54s |

这些是本地低端机数据，不能直接替代线上 P90。

## 三个典型判断

1. 插件可以编译：只能证明构建链未报错，不能证明目标 variant 已插桩。
2. `loadRouterMap()` 被调用：方法本来就存在，必须确认内部包含并执行 `register()`。
3. 启动变快：还要检查调用路径和功能，才能把收益归因给插件恢复。

## 常见误区

1. 用异步线程包装 Dex 扫描，就称为根治。
2. 把 APT 和 ASM 描述成同一阶段。
3. 插件按 `ARouter$$Root$$` 类名前缀完成最终分类。
4. 遇到 `LogisticsCenter` 就立即插桩。
5. 构建成功后不检查目标 variant 的最终产物。
6. 用本地 7.84s 的降幅直接描述线上收益。

## 本篇自测

1. 为什么恢复插件比异步初始化更贴近根因？
2. APT 与 ASM 的职责边界是什么？
3. 插件怎样识别 Root、Provider 和 Interceptor？
4. 为什么必须完成全部扫描后再修改 `LogisticsCenter`？
5. `LDC` 与 `INVOKESTATIC` 分别做什么？
6. ABC 对照怎样隔离 ARouter 修复收益？

## 一句话总结

插件把路由表发现前移到编译期；真正的修复证据是目标产物含完整注册、运行时跳过 Dex 扫描，并且性能与路由功能同时恢复。
