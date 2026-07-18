# ARouter 启动增量劣化治理 · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：深入
> 文档数量因人而异，但掌握内容不打折扣。
> 计划产出：引子、一轮优化、二轮优化、收束四篇面试笔记。
> 内容原则：项目治理是叙事主线，ARouter 与 Gradle 插件原理完整进入正文，不作为零散补充材料。

## 核心掌握项

完成本课题后，你将能够：

### 模块一 · 识别并定位启动增量劣化

- [x] 能区分“存量启动偏慢”和“版本增量劣化”，并用两轮因果链概括本项目：AGP 升级使插桩失效，Java 21 升级又使旧 ASM 无法读取 Class。
- [x] 能讲清线上 `stage_app_init → task_arouter.init` 的下钻过程，并准确表达“P90 相对历史版本新增约 8.3 秒”，不把增量说成绝对耗时。
- [x] 能复述线下复现口径、低端机选择理由，以及为何用 1000 μs Sampling 快速寻找秒级调用栈，同时说清 Profiler 数据与线上 P90 的边界。

### 模块二 · 第一轮：ARouter 完整原理与 Dex 扫描治理

- [x] 能完整解释 ARouter 如何用 `path` 间接寻址，并串起 `build()`、`Postcard`、`navigation()`、`completion()`、`RouteMeta` 和最终跳转。
- [x] 能解释 `Warehouse.routes`、`groupsIndex` 与 Group 懒加载，说明 Root、Group、Provider、Interceptor 各自在运行时承担什么职责。
- [x] 能从 `@Route` 开始，完整复述 `RouteProcessor → RoundEnvironment → Element → RouteMeta → JavaPoet` 生成路由表的编译期链路。
- [x] 能对比运行时 Dex 扫描与插件注册两条加载路径，准确说明类名筛选、反射 `loadInto()`、SP 缓存，以及 `openDexFileNative` 为什么昂贵。
- [x] 能比较异步初始化、更换路由框架、恢复插件注册三种方案，并用根因、时序风险、改造成本解释最终选择。
- [x] 能用同口径 Benchmark、Profiler 和灰度数据证明第一轮修复有效，并区分线上增量指标与本地诊断数据。

### 模块三 · 第二轮：插件完整原理与 Java 21 兼容修复

- [x] 能复述 Android 构建四阶段，明确 APT 生成路由表 Class、AGP Artifacts API 接管 Class、ASM 修改 Class、D8 生成 Dex 的职责边界。
- [x] 能解释插件如何遍历 `allDirectories` 与 `allJars`，先按 Class Entry 路径筛选候选类，再按实现接口识别 Root、Provider、Interceptor。
- [x] 能完整复述插件为何先收集全部路由表、缓存 `LogisticsCenter.class`，再通过 `ClassReader → ClassVisitor → MethodVisitor → ClassWriter` 修改 `loadRouterMap()`。
- [x] 能解释在 `RETURN` 前插入 `LDC + INVOKESTATIC`、方法描述符 `(Ljava/lang/String;)V`，以及 `registerByPlugin` 如何让运行时跳过 Dex 扫描。
- [x] 能从 Class 文件 major version 解释 Java 21 构建失败，说明 ASM 9.7、`ASM9`、运行时依赖解析、自维护发布及上游回馈的修复闭环。

### 模块四 · 面试表达与治理收束

- [x] 能在 2～3 分钟内按“背景 → 证据 → 根因 → 两轮修复 → 验证 → 防线”完整讲述项目，并能从项目主线自然下钻到全部原理。
- [x] 能把个案抽象为增量劣化治理流程，并提出首次安装/升级首启、目标 variant 插桩、产物校验和 Java/AGP/ASM 兼容矩阵等防复发措施。

## 不在本课题范围内

- ARouter 拦截器的优先级、异步链式调度及降级策略完整源码。
- `@Autowired` 参数注入、Provider 生命周期与依赖注入完整实现。
- AGP 全部任务生命周期、ASM 完整指令集和 Class 文件格式规范；只深入本插件真实使用的部分。
- 首屏裁剪、布局渲染、ContentProvider 治理等其他存量启动优化手段。

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 模块一全部：增量劣化定义、灰度下钻、复现口径、Profiler Sampling 与两轮问题地图 | 2026-07-16 |
| 02.md | 模块二全部：ARouter 运行时跳转、编译期生成、Warehouse 懒加载、两条初始化路径、Dex 扫描根因、方案取舍与三层验证 | 2026-07-16 |
| 03.md | 模块三全部：构建四阶段、Artifacts API、候选类与接口识别、两阶段扫描插桩、ASM 指令、Java 21/ASM 修复及上游闭环 | 2026-07-16 |
| 04.md | 模块四全部：2～3 分钟面试主线、追问导航、证据分层、增量治理闭环与 CI/构建/功能防复发矩阵 | 2026-07-16 |
