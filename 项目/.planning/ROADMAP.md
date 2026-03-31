# ROADMAP

## Milestone 1: Android 大厂面试知识体系

**Goal:** 系统覆盖字节/腾讯/阿里级别 Android 面试所需的核心原理，形成可快速复习的高质量笔记库，在 3 个月内达到大厂面试状态。
**Timeline:** ~3 months (in-employment study, ~12-15h/week)

---

### Phase 1: Android 核心原理

**Goal:** 能在白板上讲清楚 Handler/Binder/View/AMS 的原理链路，达到被追问三层也能答上的程度。

**Plans:** 5 plans

- [ ] 01-PLAN-handler.md — 撰写 Handler 消息机制面试笔记（ThreadLocal/epoll/同步屏障/IdleHandler/消息复用池）
- [ ] 01-PLAN-binder.md — 撰写 Binder IPC 原理面试笔记（mmap 一次拷贝/Stub-Proxy/ServiceManager/线程池/linkToDeath）
- [ ] 01-PLAN-view.md — 撰写 View 绘制体系面试笔记（performTraversals/MeasureSpec/Choreographer-VSYNC/DisplayList/RenderThread）
- [ ] 01-PLAN-ams.md — 撰写 AMS-WMS-PMS 及系统启动面试笔记（启动全链路/LaunchMode/Activity-Window-View/APK 安装）
- [ ] 01-PLAN-classloader.md — 撰写 ClassLoader 与热修复面试笔记（双亲委派/dexElements 前插/QZone-Tinker-Sophix/插件化 Hook AMS）

**Plan Details:**

1. 写 `01. Handler机制.md`，覆盖：ThreadLocal 保证每线程一个 Looper、MessageQueue 基于时间戳的链表结构、nativePollOnce epoll 阻塞与 nativeWake 唤醒、同步屏障 postSyncBarrier 与 Choreographer 的关系、IdleHandler 的用途与触发时机、消息复用池 Message.sPool 实现、主线程 Looper 死循环为什么不 ANR
2. 写 `02. Binder原理.md`，覆盖：为什么选 Binder 而非 socket/pipe（一次拷贝 vs 两次、安全性）、mmap 内核映射实现一次拷贝的具体机制、Client-Server-ServiceManager 三角关系、AIDL 生成的 Stub/Proxy 各自角色、Binder 线程池默认 15 线程限制、TransactionTooLargeException 根因、linkToDeath 死亡通知机制
3. 写 `03. View绘制体系.md`，覆盖：ViewRootImpl.performTraversals() 触发入口、MeasureSpec 三种模式与父子 View 测量传递、requestLayout() vs invalidate() 触发路径差异、Choreographer 接收 VSYNC 信号驱动帧调度、硬件加速下 DisplayList/RenderNode 机制、RenderThread 与 MainThread 协作流程、自定义 View wrap_content 不生效的根因
4. 写 `04. AMS-WMS-PMS及系统启动.md`，覆盖：Activity-Window-View 三者关系（DecorView/WindowManager）、AMS 通过 Binder 回调 ApplicationThread 驱动生命周期、ActivityRecord/TaskRecord/ActivityStack 数据结构、四种 LaunchMode 与 FLAG 对任务栈的影响、应用进程启动全链路（AMS → Zygote fork → ActivityThread.main()）、WMS 管理 Surface z-order、PMS APK 安装流程（解析→权限校验→dex优化→信息注册）
5. 写 `05. ClassLoader与热修复.md`，覆盖：PathClassLoader vs DexClassLoader 区别、双亲委派模型与破坏方式、BaseDexClassLoader.dexElements 数组顺序决定类加载优先级、热修复三大方案对比（QZone pre-verify 问题/Tinker 差量 patch/Sophix 方法替换）、插件化三大核心问题（类加载+资源加载+四大组件生命周期）、Hook AMS 占坑 Activity 方案原理

**Requirements:** [HANDLER-01, BINDER-01, VIEW-01, AMS-01, CLASSLOADER-01]

**Success Criteria:**
- [ ] 被问"Handler 消息机制"能不看笔记讲完整：ThreadLocal → MessageQueue 链表 → epoll 阻塞唤醒 → 同步屏障，且能回答"主线程死循环为什么不 ANR"这个追问
- [ ] 被问"Binder 为什么一次拷贝"能画出 mmap 内核映射示意图并解释 copy_from_user 的流程，能区分 Binder（一次）和共享内存（零次）
- [ ] 被问"View 绘制流程"能说出 ViewRootImpl 入口、三大流程，并追问 Choreographer/VSYNC 时能继续回答
- [ ] 被问"Activity 启动流程"能描述完整的 AMS → Zygote → ActivityThread 链路，并说出 ActivityRecord 是 AMS 侧的记录对象
- [ ] 被问"热修复原理"能说清楚 dexElements 前插方案，能对比 QZone/Tinker 的核心差异

**Dependencies:** None

---

### Phase 2: 性能优化

**Goal:** 能结合实战数据讲清楚启动/内存/卡顿/ANR 的完整优化链路，做到"说出具体数字 + 原理 + 工具"的三段式回答。

**Plans:**

1. 整理并升级 `01. 启动优化.md`（基于已有的 `启动优化_01.启动优化其一.md`），补充：冷启动完整链路（用户点击 → Launcher → AMS → Zygote fork → Application → Activity.onCreate() → 首帧 Vsync）各阶段耗时卡点与对应工具（Systrace/Perfetto/am start-activity -W）、ContentProvider 拖慢启动的机制与治理、启动任务 DAG 有向无环图设计（App Startup vs 自研）、ttid vs ttfd 区别、务必补入实际优化数据（从 X ms → Y ms，核心手段列表）
2. 写 `02. 内存优化.md`，覆盖：Java 堆分区与 GC 算法基础、Android OOM 本质（Java堆 vs native堆 vs 图形内存）、内存泄漏五大场景（静态引用/Handler内部类/单例持有Context/WebView/未注销监听器）、LeakCanary 完整工作流（ActivityLifecycleCallbacks → WeakReference+ReferenceQueue → 触发GC → dump hprof → 解析引用链）、Bitmap 内存在 Android 8.0 前后的位置变化（Java堆 → native堆）、VSS/RSS/PSS/USS 含义区分、线上 OOM 监控方案（字节 Koom 的主进程监控思路）
3. 写 `03. 卡顿优化.md`，覆盖：Android 渲染流水线（App主线程 → Choreographer → Vsync → doFrame → measure/layout/draw → RenderThread → GPU）、Choreographer 帧回调三类任务（Input/Animation/Traversal）执行顺序、掉帧定义（>16ms/32ms 的区别）、用 Systrace/Perfetto 分析卡顿的具体操作步骤（看哪些 track/哪些关键字）、主线程耗时来源（SP同步写/数据库主线程/Binder调用）、线上卡顿监控 SDK 设计（Looper消息耗时监控 vs Choreographer帧率监控）、RecyclerView 卡顿优化（onBindViewHolder 耗时控制/prefetch机制）
4. 写 `04. ANR分析.md`，覆盖：四种 ANR 触发类型和超时时间（Activity 5s/BroadcastReceiver 前台10s后台60s/Service 前台20s后台200s）、AMS 埋伏炸弹机制（scheduleTimeoutLocked → postDelayed → appNotResponding → dumpStackTraces）、traces.txt 关键字段解读（waiting to lock/at xxx/SIGQUIT）、线上 ANR 监控两种方案对比（FileObserver 监听 traces vs Looper 消息耗时监控）、Binder 调用超时导致 ANR 的机制与检测、补充一个具体 ANR 案例（traces关键信息 → 定位 → 修复）

**Success Criteria:**
- [ ] 被问"你们 App 冷启动耗时多少，怎么优化的"能说出具体数字和手段（不能答"大约几秒"）
- [ ] 被问"内存泄漏如何排查"能描述 LeakCanary 完整工作流，并举出至少 3 个具体泄漏场景和修复方案
- [ ] 被问"如何分析卡顿"能描述 Systrace 操作流程，并说出"看 Choreographer doFrame 耗时 + RenderThread 耗时 + 找主线程长消息"这三步
- [ ] 被问"ANR 原理"能手写 AMS 触发 ANR 的时序，能说出 traces.txt 中 waiting to lock 的含义

**Dependencies:** Phase 1（ANR 分析依赖 Handler/AMS 原理，卡顿分析依赖 Choreographer/View 绘制体系）

---

### Phase 3: 音视频 & OpenGL

**Goal:** 将已有的 FFmpeg/OpenGL/EGL 实战积累转化为面试可讲的体系化知识，形成差异化竞争优势，能深度回答"你的音视频项目是怎么设计的"。

**Plans:**

1. 整理并升级 `01. 音视频基础.md`（基于已有笔记），补充到面试标准：H.264 NALU 结构（SPS/PPS/IDR/Slice 作用）、I/P/B 帧编解码依赖关系、PTS vs DTS 区别与 B 帧导致 PTS≠DTS 的处理（FFmpeg 重排序）、YUV420P/NV12/NV21 内存布局对比（能手画）、音视频同步三种策略（以音频时钟为基准的实现细节）、MP4 moov box 位置对流媒体的影响（faststart 优化）、实际项目编码参数和延迟数据
2. 整理并升级 `02. FFmpeg核心.md`（基于已有 FFmpegUtil 实战），达到可讲清楚架构的程度：六大模块职责（libavformat/libavcodec/libavutil/libswscale/libswresample/libavfilter）、完整解码流程（avformat_open_input → find_stream_info → av_read_frame → send_packet → receive_frame）、AVPacket/AVFrame 内存管理（av_packet_ref/unref 引用计数机制，避免泄漏）、你的 FFmpegUtil 线程模型设计（几个线程/队列数据结构/seek 处理/边界情况）、FFmpeg 与 MediaCodec 硬解的混合使用对比（延迟/CPU/兼容性取舍）
3. 整理并升级 `03. OpenGL渲染管线.md`（基于已有 OpenGL 01~05 系列笔记），升级到面试标准：完整渲染管线（顶点着色器→图元装配→光栅化→片段着色器→测试混合→帧缓冲输出）、GLSL 变量类型（attribute/varying/uniform 含义与生命周期）、YUV→RGB 在 shader 中的转换矩阵（BT.601 系数）、FBO 离屏渲染完整流程与 Filter Chain 多 FBO 链式处理、SurfaceTexture.updateTexImage() 为什么只能在 GL 线程调用
4. 写 `04. EGL与SurfaceView体系.md`（基于已有 EGL 笔记 + TextureView/SurfaceView 实战），整合：EGL 完整初始化流程（eglGetDisplay→eglInitialize→eglChooseConfig→eglCreateContext→eglCreateWindowSurface→eglMakeCurrent）、EGLContext 共享机制（解码线程上传纹理→渲染线程使用纹理的线程协作）、SurfaceView vs TextureView 核心区别（独立 Surface 层 vs HardwareLayer，耗电差异）、MediaCodec 与 OpenGL 联动完整链路（MediaCodec 输出 SurfaceTexture → updateTexImage() → 绘制到 FBO → eglSwapBuffers）

**Success Criteria:**
- [ ] 被问"H.264 的 NALU 结构"能不看资料画出 SPS/PPS/IDR 的关系，并解释为什么 MediaCodec 第一包必须包含 SPS/PPS（CSD）
- [ ] 被问"你的 FFmpeg 项目是怎么设计的"能讲清楚线程模型（几个线程/队列/同步机制）、内存管理（引用计数/泄漏防范）、seek 处理，回答时长 3-5 分钟不卡壳
- [ ] 被问"OpenGL 渲染 YUV 视频"能在白板上写出 shader 中 YUV→RGB 的核心代码（Y/U/V 分量采样 + BT.601 矩阵转换）
- [ ] 被问"SurfaceView 和 TextureView 的区别"能说出独立 Surface 层 vs HardwareLayer 的本质区别，并能说出 TextureView 额外耗电的原因（纹理拷贝）

**Dependencies:** Phase 1（OpenGL/SurfaceTexture 与 View 体系关联，EGL 与 Binder/Surface 关联）

---

### Phase 4: Kotlin & 语言基础

**Goal:** 能讲清楚 Kotlin 协程的 CPS 变换原理、Flow 与 LiveData 的设计差异，做到 Kotlin 高阶特性问题不失分。

**Plans:**

1. 写 `01. Kotlin协程原理.md`，覆盖：suspend 函数的 CPS（Continuation-Passing Style）变换过程（能手写状态机伪代码）、Continuation 是什么/挂起如何不阻塞线程、四种 Dispatcher 的线程池实现（Main主线程/IO弹性64线程/Default核心数/Unconfined）、结构化并发（CoroutineScope-Job 父子关系：父取消→子取消，子异常→传播父）、coroutineScope vs supervisorScope 异常传播行为差异、launch vs async 选用原则、协程取消的协作式机制（isActive/ensureActive/yield）、CoroutineExceptionHandler 的作用域
2. 写 `02. Kotlin高阶特性.md`，覆盖：扩展函数编译为静态方法的本质（不能访问私有成员的原因）、inline 函数消除 lambda 对象分配（字节码层面的内联展开）、reified 类型参数为什么普通泛型不能用（JVM 类型擦除 vs inline 内联后类型保留）、crossinline vs noinline 区别、by lazy 委托属性的线程安全实现（SYNCHRONIZED/PUBLICATION/NONE 三种模式）、Kotlin 数据类 copy() 的浅拷贝陷阱
3. 写 `03. Flow-LiveData-Jetpack.md`，覆盖：Flow vs LiveData vs RxJava 三方对比（冷流vs热流、背压处理、生命周期感知）、StateFlow vs SharedFlow 的区别和选用场景、Flow 操作符（collect/map/filter/flatMapLatest/combine）的使用和陷阱（在 Activity 中用 lifecycleScope.launchWhenStarted 还是 repeatOnLifecycle 的区别）、ViewModel 旋转存活原理（ActivityThread 中 NonConfigurationInstances 保留机制）、LiveData 的 postValue vs setValue 线程差异

**Success Criteria:**
- [ ] 被问"suspend 函数原理"能不看笔记口述 CPS 变换的过程，并用伪代码描述状态机的 label 跳转机制
- [ ] 被问"Flow 和 LiveData 的区别"能说清楚冷流/热流的本质区别，StateFlow/SharedFlow 的场景选择，以及 repeatOnLifecycle 相比 launchWhenStarted 修复了什么问题
- [ ] 被问"inline/reified"能解释 JVM 类型擦除为什么导致泛型无法获取类型，以及 inline 是如何绕过这个限制的

**Dependencies:** Phase 1（协程 Dispatchers.Main 依赖主线程 Handler 机制理解；LiveData 粘性事件与 Observer 注册机制依赖 Activity 生命周期原理）

---

### Phase 5: 跨平台（Flutter & HarmonyOS）

**Goal:** 能深度讲解 Flutter 三棵树渲染原理和 MethodChannel 底层实现，能介绍 HarmonyOS ArkUI 的核心模型，将已有实战积累转化为架构层面的差异化回答。

**Plans:**

1. 整理并升级 Flutter 笔记为 `01. Flutter渲染原理.md`（基于已有 Flutter 入门篇和进阶篇），达到面试标准：三棵树（Widget/Element/RenderObject）各自职责与协作关系（Widget 不可变蓝图→Element 状态持有与 reconciliation→RenderObject 真正 layout/paint）、setState() 调用后的完整路径（标记 dirty Element → WidgetsBinding.drawFrame() → build() → reconciliation → 仅更新必要 RenderObject）、帧渲染六阶段（Animate/Build/Layout/Compositing/Paint/Composite）、Key 的作用与 Element 复用判断条件（runtimeType + key 双匹配）、Skia vs Impeller 的核心差异（着色器 JIT vs AOT，首帧卡顿问题）、Flutter 为什么性能比 RN 旧架构好（绕过 JS Bridge，完全自绘不依赖原生控件）
2. 整理并升级 MethodChannel 笔记为 `02. Flutter通信机制.md`（基于已有 MethodChannel.md），补充底层实现：三种 Channel 对比（MethodChannel 请求响应/EventChannel 持续推送/BasicMessageChannel 双向自定义）、StandardMessageCodec 序列化支持的类型（不能直接传 Parcelable 的原因）、Platform Channel 的线程安全（注册和回调必须在主线程，耗时操作如何切线程后切回）、Pigeon 代码生成工具相比手写 Channel 的优势、FFI（dart:ffi）适用场景（调用 C/C++ .so，性能比 MethodChannel 高，不能调 Java 代码）
3. 写 `03. HarmonyOS基础.md`，覆盖：ArkTS 与 TypeScript 的关系及限制（禁止 any/动态属性/eval，原因是支持 AOT 静态优化）、ArkUI 状态装饰器体系（@State/@Prop/@Link/@Observed/@StorageProp 各自的数据流向）、Stage 模型 UIAbility 生命周期（vs FA 模型已废弃）、ArkUI 声明式 UI 与 Flutter Widget/Jetpack Compose 的横向对比、HarmonyOS NEXT 与原 Android 兼容层的区别（纯鸿蒙概念）、flutter-ohos 鸿蒙 Flutter 支持现状

**Success Criteria:**
- [ ] 被问"Flutter 三棵树"能不看笔记描述三棵树各自的职责，并解释为什么 Widget rebuild 不等于 RenderObject rebuild（Element reconciliation 的作用）
- [ ] 被问"MethodChannel 底层是什么"能说出 StandardMessageCodec 序列化、线程调度要求（必须主线程回调），以及为什么 FFI 比 MethodChannel 性能高
- [ ] 被问"有没有鸿蒙开发经验"能介绍 ArkTS 的设计约束原因，以及 @State/@Prop/@Link 的数据流差异，不会完全卡壳

**Dependencies:** Phase 1（Flutter Element reconciliation 与 Android View 体系对比加深理解；HarmonyOS UIAbility 类比 Activity 生命周期）

---

### Phase 6: 面试冲刺

**Goal:** 将所有知识点转化为面试现场可直接输出的答题话术，通过模拟面试验证掌握程度，达到投递大厂简历的状态。

**Plans:**

1. 写 `01. 高频题答题模板.md`：整理 30 道最高频题目的"开场句 + 核心要点 + 加分追问预案"三段式模板，覆盖：Handler机制/Binder原理/View绘制/Activity启动/冷启动优化/内存泄漏/卡顿分析/ANR原理/协程原理/Flutter三棵树，每道题的答题时间控制在 2-3 分钟内可讲完，不需要再翻笔记
2. 写 `02. 系统设计题库.md`：整理 5-8 道大厂常考系统设计题的完整答题框架，优先覆盖与实战背景相关的方向——视频播放器 SDK 设计（必写，结合 FFmpeg/OpenGL 积累）、图片加载库设计（Glide 原理：四级缓存/Bitmap复用池/内存压缩）、线上崩溃监控 SDK 设计（Signal Handler + Java层UncaughtExceptionHandler）、推送 SDK 保活设计，每道题用"需求澄清→核心模块拆分→关键设计决策→边界情况"四步框架答题
3. 写 `03. 项目话术.md`：整理 3 个核心项目的 STAR 格式话术（Situation/Task/Action/Result），必须包含：FFmpegUtil 架构设计（线程模型/内存管理/seek处理/与MediaCodec的取舍决策）、巡店视频语音对讲功能（PCM采集→编码→发送的完整链路，延迟数据）、性能优化项目（冷启动优化数据/具体手段），每个项目准备"你们是怎么设计的"和"遇到了什么问题"两个切入角度的回答
4. 执行 3 轮自我模拟面试：第 1 轮覆盖 Phase 1 全部考点（纯口述，不看笔记，录音）、第 2 轮覆盖 Phase 2-3（加入系统设计题）、第 3 轮全量模拟一场完整面试（60分钟，涵盖八股+项目+算法复盘）

**Success Criteria:**
- [ ] 能在不看任何笔记的情况下，完整回答 Phase 1 中任意一道 P0 题目（Handler/Binder/View/Activity启动），答题时长 2-3 分钟，包含原理 + 追问预案
- [ ] 能在 15 分钟内完整输出"设计一个视频播放器 SDK"的系统设计答案，包含模块划分、关键接口设计、线程模型，能主动提出 FFmpeg/MediaCodec 的选型分析
- [ ] 录音回放模拟面试，没有"嗯……这个……"超过 5 秒的空白停顿，项目话术能精准说出具体数字（优化前后耗时/并发线程数/缓存大小等）
- [ ] 简历更新完成，FFmpeg/OpenGL/性能优化项目列为前三条，每条有量化数据支撑，达到可投递字节/腾讯/阿里 JD 要求的状态

**Dependencies:** Phase 1, Phase 2, Phase 3, Phase 4, Phase 5（冲刺阶段整合所有前序内容）

---

## Phases

- [ ] **Phase 1: Android 核心原理** — Handler/Binder/View/AMS/ClassLoader 原理体系，P0 必答题全覆盖
- [ ] **Phase 2: 性能优化** — 启动/内存/卡顿/ANR 完整链路，结合实战数据深化
- [ ] **Phase 3: 音视频 & OpenGL** — 整理并深化 FFmpeg/OpenGL/EGL 已有积累，打造差异化护城河
- [ ] **Phase 4: Kotlin & 语言基础** — 协程 CPS 原理/Flow/LiveData/Jetpack 核心机制
- [ ] **Phase 5: 跨平台** — Flutter 三棵树渲染原理/MethodChannel 底层/HarmonyOS ArkUI
- [ ] **Phase 6: 面试冲刺** — 答题模板/系统设计题库/项目话术/模拟面试验证

---

## Progress

| Phase | Notes Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Android 核心原理 | 0/5 | Planned (5 plans, 2 waves) | - |
| 2. 性能优化 | 0/4 | Not started | - |
| 3. 音视频 & OpenGL | 0/4 | Not started | - |
| 4. Kotlin & 语言基础 | 0/3 | Not started | - |
| 5. 跨平台 | 0/3 | Not started | - |
| 6. 面试冲刺 | 0/4 | Not started | - |
