# 性能优化 & 音视频面试考点调研

**调研对象**: 字节跳动 / 腾讯 / 阿里 / 美团 / 滴滴 Android 岗
**调研日期**: 2026-03-31
**适用背景**: 有音视频（FFmpeg）实战经验的 Android 开发者备战大厂
**置信度说明**: 基于训练数据中的大量面经整理，标注 HIGH/MEDIUM/LOW

---

## 性能优化考点

### 1. 启动优化（冷启动/热启动）

- **考察频率**: 极高（几乎每家大厂必问，字节/美团出现率 >80%）
- **置信度**: HIGH

- **典型问题**:
  1. 冷启动 vs 热启动 vs 温启动的区别，各自的流程是什么？
  2. Application.onCreate() 执行在主线程，但为什么它卡顿不会触发 ANR？（考察 5s ANR 计时起点）
  3. 你们 App 的冷启动耗时是多少？怎么测量的？用了哪些优化手段？
  4. 启动白屏/黑屏如何消除？SplashScreen API 和旧方案有什么区别？
  5. MultiDex 对启动速度的影响，如何优化？（字节 ByteX 方案）
  6. 类加载耗时怎么分析？如何做类预加载？
  7. ContentProvider 为什么会拖慢启动？三方 SDK 的 ContentProvider 如何治理？
  8. 启动任务依赖图（有向无环图）如何设计？App Startup 和自研方案对比？
  9. Zygote 预热机制是什么？ART 的 AOT/JIT/Profile-guided 编译对启动的影响？
  10. 如何区分 ttid（首帧时间）和 ttfd（完全可交互时间）？

- **深度要求**:
  - 必须能画出：用户点击图标 → Launcher → AMS → Zygote fork → ActivityThread.main() → Application → Activity.onCreate() → View 测量/布局/绘制 → 首帧 Vsync 的完整链路
  - 必须知道每个阶段的耗时卡点和对应工具（Systrace / Perfetto / adb shell am start-activity -W）
  - 大厂要求：说出你在项目中实际将冷启动从 X ms 优化到 Y ms 的具体操作

- **实战加分**:
  - 你已有冷启动优化实战经验（见 `启动优化_01.启动优化其一.md`），重点整理**数据**：优化前后耗时对比
  - 深挖 AttachBaseContext → MultiDex 初始化时机（你们用异步方案还是主 dex 瘦身方案？）
  - 字节面试特别喜欢追问：如何在不改业务代码的情况下做 SDK 懒加载（字节 Booster/Lancet 插桩方案）

---

### 2. 内存优化（OOM / 内存泄漏 / LeakCanary）

- **考察频率**: 高（大厂几乎必问，偏实战）
- **置信度**: HIGH

- **典型问题**:
  1. Java 内存模型中的堆区划分（新生代/老年代/方法区），垃圾回收算法是什么？
  2. Android 中 OOM 的本质是什么？堆内存 vs native 内存 vs 图形内存？
  3. 内存泄漏的常见场景：静态引用 Activity、Handler 内部类、单例持有 Context、WebView 泄漏，如何逐一排查？
  4. LeakCanary 的实现原理：WeakReference + ReferenceQueue + ObjectWatcher，如何判断对象未被回收？
  5. 大图加载 OOM 怎么处理？BitmapFactory.Options.inSampleSize / Glide 的内存缓存策略？
  6. 如何分析一个 OOM crash？MAT / Android Studio Memory Profiler 的使用流程？
  7. Bitmap 内存在哪里分配？Android 8.0 前后的变化（Bitmap pixels 从 Java 堆迁移到 native 堆）？
  8. 什么是 trimMemory？应用应该在哪些回调中释放内存？
  9. 内存抖动（Memory Churn）是什么？如何定位和消除？
  10. 线上内存监控方案如何设计？（采样 hprof / native hook / 字节 Koom 方案）

- **深度要求**:
  - 能说清楚 LeakCanary 的完整工作流：注册 ActivityLifecycleCallbacks → onDestroy 后放入 watch 队列 → 触发 GC → 检查 ReferenceQueue → dump hprof → 解析引用链
  - Bitmap 内存问题是大厂必追的点，要知道 Android 8.0 之后 `Bitmap.createBitmap()` 的实际内存位置
  - 能区分 VSS / RSS / PSS / USS 的含义（ART runtime 内存统计）

- **实战加分**:
  - 如果你们项目有图片展示（视频封面等），重点准备 Glide 内存缓存 LRU 策略 + 大图降采样的实战
  - WebView 内存泄漏是很多业务 App 的痛点，单独整理一份 WebView 内存治理方案
  - 线上 OOM 监控：能说出"在主进程 OOM 前如何拿到当时的 hprof 快照"这类实战方案（字节 Koom 思路）

---

### 3. 卡顿优化（Systrace / Choreographer / 帧率）

- **考察频率**: 高（大厂高频，字节/腾讯尤其重视）
- **置信度**: HIGH

- **典型问题**:
  1. Android 渲染流水线是什么？Vsync 信号的作用？16ms 的由来？
  2. Choreographer 的工作原理：FrameCallback 注册 → Vsync 信号回调 → 执行 Input/Animation/Traversal 三类任务
  3. 什么是掉帧（Jank）？如何定义一帧卡顿？（>16ms / >32ms 的区别）
  4. 如何用 Systrace / Perfetto 分析卡顿？看哪些 track？
  5. 主线程耗时任务的常见来源：SharedPreferences 同步写、数据库主线程查询、Binder 调用耗时
  6. RecyclerView 卡顿优化：onBindViewHolder 的耗时控制、prefetch 机制、异步预加载
  7. 布局优化：ConstraintLayout vs LayoutInflater 耗时、ViewStub、AsyncLayoutInflater
  8. 如何监控线上卡顿？字节的 matrix-trace、腾讯的 Matrix 方案原理是什么？
  9. RenderThread 和 MainThread 是如何协作的？硬件加速的渲染流水线？
  10. ANR 和卡顿的本质区别是什么？（卡顿 = 帧耗时过长，ANR = 消息长时间未处理）

- **深度要求**:
  - 必须能描述：App 主线程 → Choreographer.postFrameCallback → Vsync → doFrame → measure/layout/draw → RenderThread → GPU 的完整帧渲染链路
  - 能用 Systrace 定位出"某帧为什么掉帧"——这是大厂实操面试题
  - 字节特别关注：如何设计一个线上卡顿监控 SDK（Looper 消息监控 / Choreographer 帧率监控）

- **实战加分**:
  - 如果你们有视频播放场景，视频解码与 UI 渲染的线程协作是加分项
  - 能结合 OpenGL/SurfaceView 谈渲染线程与主线程的关系（你们 FFmpeg 解码 + OpenGL 渲染的架构天然符合这个加分点）

---

### 4. ANR 分析与解决

- **考察频率**: 高（基本每轮面试必问，考察系统原理深度）
- **置信度**: HIGH

- **典型问题**:
  1. ANR 的四种触发类型及其超时时间？（Activity 5s / BroadcastReceiver 前台 10s 后台 60s / Service 前台 20s 后台 200s / ContentProvider 10s）
  2. ANR 的触发机制：AMS 发送埋伏炸弹（postDelayed），消息处理完成后解除，超时则 dump traces
  3. 如何分析 /data/anr/traces.txt？关键字段是什么？waiting to lock / at xxx 的含义？
  4. 线上 ANR 如何监控？FileObserver 监听 traces 文件 vs Looper 消息耗时监控的区别？
  5. Input 超时 ANR（5s 无响应触摸事件）和 Service ANR 的触发流程有什么不同？
  6. 主线程 Binder 调用超时如何导致 ANR？如何检测 Binder 调用耗时？
  7. 死锁导致的 ANR 如何分析和预防？
  8. WorkerThread 的异常是否会导致 ANR？（考察对 crash vs ANR 的理解）
  9. 你在项目中遇到过哪些 ANR？是如何定位和解决的？
  10. SIGQUIT 信号在 ANR dump 中的作用？

- **深度要求**:
  - 必须能手写 AMS 的 ANR 触发时序：`scheduleTimeoutLocked()` → `postDelayed()` → `appNotResponding()` → `dumpStackTraces()`
  - 能看懂 traces.txt 文件，识别 deadlock / waiting on lock / Native Blocked 等状态
  - 字节/腾讯会追问：如何在线上不 root 的情况下拿到 ANR 的 traces？（利用 DropBoxManager 或 signal handler）

- **实战加分**:
  - 你的 `ANR_01.基础概念.md` 已有基础，需要补充线上监控方案和 traces 解读实例
  - 准备一个你实际遇到的 ANR 案例（哪怕是构造的）：traces 关键信息 → 定位原因 → 修复方案

---

### 5. 包体积优化

- **考察频率**: 中（字节/阿里较关注，其他公司中低频）
- **置信度**: MEDIUM

- **典型问题**:
  1. APK 的组成结构：classes.dex / resources.arsc / res/ / assets/ / lib/ / META-INF/ 各占多大？
  2. 如何分析 APK 体积？Android Studio APK Analyzer / Matrix ApkChecker
  3. 资源优化：WebP 替换 PNG/JPG、res/raw 音频压缩、无用资源移除（`shrinkResources`）
  4. 代码优化：R8 混淆 vs ProGuard、`minifyEnabled` 的内部机制
  5. so 库体积优化：只保留 arm64-v8a vs 全 ABI 的权衡，strip debug symbol
  6. App Bundle（AAB）vs APK 的区别？Dynamic Feature Module 如何按需下载？
  7. 字节码插桩减包：冗余代码删除、Kotlin 内联函数的 bytecode 膨胀问题
  8. 资源混淆（AndResGuard）的原理？
  9. 包体积监控如何接入 CI/CD？
  10. `resources.arsc` 的结构，为什么它在国内 App 中占比很大？

- **深度要求**:
  - 了解 R8 full mode 和兼容 mode 的区别，知道常见混淆 keep 规则为何必须保留
  - 能说出实际减包效果数据（"从 XX MB 降到 XX MB，核心手段是..."）

- **实战加分**:
  - 如果你们项目有 FFmpeg .so 库，这是天然加分：so 库按 ABI 拆分、利用 App Bundle 按设备架构下发
  - 鸿蒙方向可额外补充：HAR vs HSP 包的体积管理方式

---

### 6. 电量优化

- **考察频率**: 中低（大厂偶发，通常不是必考项，但字节抖音类产品会问）
- **置信度**: MEDIUM

- **典型问题**:
  1. 电量消耗的主要来源：CPU 密集计算、网络请求、屏幕亮度、GPS、音视频解码
  2. Battery Historian 的使用：如何导出并分析 wakelock、alarm、network 等维度？
  3. WakeLock 的类型和持有不释放的后果？
  4. Doze 模式和 App Standby 的机制？如何在 Doze 下仍能收到推送？
  5. WorkManager 在电量优化中的作用？JobScheduler 的底层实现？
  6. 网络请求合并与批处理（batching）策略
  7. 前台 Service vs 后台 Service 的电量影响？
  8. 视频播放的电量优化：硬解 vs 软解、屏幕常亮 FLAG 的管理

- **深度要求**:
  - 了解 Doze 模式的分级（Light Doze / Deep Doze）以及 WindowManager 的相关 API
  - 能用 Battery Historian 分析一个具体的耗电问题

- **实战加分**:
  - 你们有视频播放业务，MediaCodec 硬解对 CPU/电量的优势是具体加分项
  - 音视频解码时的后台行为管理（MediaSession、后台播放保活策略）

---

## 音视频考点

### 7. 音视频基础（编解码 / 容器格式 / H264 / H265 / AAC）

- **考察频率**: 极高（针对音视频岗位，字节抖音/腾讯视频/快手基本全问）
- **置信度**: HIGH

- **典型问题**:
  1. I 帧 / P 帧 / B 帧各自的含义、编码方式、解码依赖关系？
  2. H.264 的 NALU 结构：SPS / PPS / IDR / Slice 的作用？
  3. H.264 vs H.265 vs AV1：压缩率、计算复杂度、专利授权的区别？
  4. AAC 的编码规格：AAC-LC / HE-AAC / HE-AAC v2 的区别？
  5. MP4 容器格式：moov box 的位置对流媒体播放的影响（faststart 优化）？
  6. FLV 格式与 RTMP 协议的关系？为什么直播常用 FLV+RTMP？
  7. PCM 是什么？采样率 / 位深 / 声道数的含义，以及 AudioTrack 如何播放 PCM？
  8. 音视频同步的几种策略：以音频为基准（Audio Clock）/ 以视频为基准 / 以外部时钟为基准？
  9. 时间戳：PTS vs DTS 的区别？B 帧为什么会导致 PTS != DTS？
  10. 关键帧间隔（GOP）对直播延迟和随机 seek 的影响？
  11. 码率控制模式：CBR / VBR / CRF 的区别和适用场景？
  12. YUV 格式：Y/U/V 的含义，YUV420P / NV12 / NV21 的内存排布有何不同？

- **深度要求**:
  - 你已有 `02. 音视频_音视频基础_01.音视频基础.md`，需要达到能默写 NALU 结构、能画出 YUV420 内存布局的程度
  - H.264 Profile 层级（Baseline/Main/High）对解码兼容性的影响，这是实际项目问题
  - 字节会深挖：B 帧导致的 PTS/DTS 不一致如何处理？在 FFmpeg 中如何重排序？

- **实战加分**:
  - 你有 FFmpeg 解码 + 音视频同步的实战经验（见 `02. 音视频_音视频基础_03.音视频同步.md`），这是极大加分项
  - 准备具体数字：你的项目用什么编码参数，码率是多少，延迟是多少？
  - 封装生成 MP4 的实战（见 `02. 音视频_音视频基础_04.音视频封装生成一个mp4.md`）——能说清楚 muxer 的 write header/write packet/write trailer 流程

---

### 8. FFmpeg 架构与使用

- **考察频率**: 高（音视频岗位专项，有 FFmpeg 经验者必被深挖）
- **置信度**: HIGH

- **典型问题**:
  1. FFmpeg 的核心模块有哪些？libavformat / libavcodec / libavutil / libswscale / libswresample / libavfilter 各自的职责？
  2. FFmpeg 解码的完整流程：avformat_open_input → avformat_find_stream_info → 循环 av_read_frame → avcodec_send_packet → avcodec_receive_frame？
  3. AVPacket 和 AVFrame 的关系？一个 Packet 可能对应几个 Frame？
  4. FFmpeg 的 Filter Graph（滤镜图）是什么？如何串联多个 filter？
  5. FFmpeg 的线程模型：解复用线程 / 解码线程 / 渲染线程 如何协作？你们是怎么设计的？
  6. FFmpeg 如何与 Android 集成：JNI 调用、so 库编译参数、NDK 版本兼容？
  7. FFmpeg 的内存管理：av_packet_ref / av_packet_unref / av_frame_ref 的正确使用，如何避免内存泄漏？
  8. FFmpeg 硬件加速解码（MediaCodec decoder）如何启用？与纯软解的 API 差异？
  9. 实时流（RTMP/HLS）的拉流延迟如何用 FFmpeg 参数控制？（超时设置、缓冲区大小）
  10. FFmpeg 转码（transcode）的流程：解码 → 滤镜处理 → 重新编码 vs 直接 stream copy 的区别和性能差异？

- **深度要求**:
  - 这是你的核心竞争力领域。不能只说"我用过 FFmpeg"，要能讲清楚内存管理（引用计数机制）、线程安全问题、错误码处理
  - 必须能解释你的 FFmpegUtil 架构设计：为什么这样设计线程模型？处理了哪些边界情况？
  - 深挖点：AVCodecContext 的 thread_count 参数对帧间解码的影响？slice 级并行 vs 帧级并行？

- **实战加分**:
  - 你有 FFmpegUtil（见项目文件），准备好讲解：设计了几个线程？队列用的什么数据结构？如何处理 seek？
  - 你有鸿蒙 FFmpeg 编译经验（见 `.so库 - 分步指令.pdf`），跨平台编译经验是高级加分项
  - 你有语音对讲功能实战（采集 PCM → 编码 → 发送），这属于音频采集链路的完整经验

---

### 9. MediaCodec 硬件编解码

- **考察频率**: 高（字节/腾讯/快手音视频岗必问，考察是否了解 Android 平台特性）
- **置信度**: HIGH

- **典型问题**:
  1. MediaCodec 的工作模式：同步模式 vs 异步模式（回调模式）？
  2. MediaCodec 的生命周期状态机：Uninitialized → Configured → Executing（Flushed/Running/End of Stream）→ Released
  3. MediaCodec 的 InputBuffer / OutputBuffer 的申请与释放机制？
  4. MediaCodec 输出 Surface 模式（直接渲染到 SurfaceTexture）vs ByteBuffer 模式的区别和使用场景？
  5. MediaCodec 解码 H.264 时，为什么第一个包必须包含 SPS/PPS？（CSD - Codec Specific Data）
  6. MediaCodec 硬解 vs FFmpeg 软解的性能对比：延迟、CPU 占用、电量、兼容性的取舍？
  7. MediaMuxer 如何配合 MediaCodec 进行录制？
  8. MediaCodec 的 KEY_FRAME_RATE / KEY_BIT_RATE / KEY_I_FRAME_INTERVAL 等参数的作用？
  9. 如何处理 MediaCodec 的 INFO_OUTPUT_FORMAT_CHANGED 事件？
  10. CameraX / Camera2 的编码输出如何送入 MediaCodec？InputSurface 的使用？

- **深度要求**:
  - 能手画 MediaCodec 状态机图（这是大厂面试经典题）
  - 理解 Surface 模式的好处：零拷贝，GPU 直接输出到纹理，避免 YUV → RGBA 的 CPU 转换
  - 重要区分：MediaCodec 编码器的 Input 是 Surface（来自 Camera / OpenGL）还是 ByteBuffer？

- **实战加分**:
  - 你有 FFmpeg + MediaCodec 混合使用的项目背景，能对比两者的实际差异是强加分
  - MediaCodec 与 OpenGL 纹理（SurfaceTexture）结合：这在直播/视频编辑中非常重要，你的 OpenGL 背景直接支撑这道题

---

### 10. OpenGL ES 渲染管线

- **考察频率**: 中高（音视频岗目标公司专项，非音视频岗低频）
- **置信度**: HIGH

- **典型问题**:
  1. OpenGL ES 渲染管线的完整流程：顶点着色器 → 图元装配 → 光栅化 → 片段着色器 → 测试混合 → 帧缓冲输出
  2. VBO（顶点缓冲对象）/ VAO（顶点数组对象）/ EBO（索引缓冲对象）的作用和区别？
  3. 纹理（Texture）的绑定、采样、Mipmap 的原理？
  4. shader 中 `varying` / `uniform` / `attribute` 的含义和生命周期？（OpenGL ES 2.0）
  5. 如何使用 OpenGL 渲染一帧 YUV 视频画面？（分离 Y/U/V 分量，在 shader 中做 YUV→RGB 转换）
  6. FBO（帧缓冲对象）的作用？离屏渲染流程？（见你的 `03. 音视频_OpenGL_05.OpenGL FBO数据缓冲区.md`）
  7. GLSurfaceView 的 Renderer 接口三个方法的调用时机和 OpenGL 线程关系？
  8. SurfaceTexture 的 updateTexImage() 方法为什么只能在 GL 线程调用？
  9. 多 FBO 链式处理（Filter Chain）如何实现？
  10. OpenGL 渲染错误如何调试？`glGetError()` 的局限性？

- **深度要求**:
  - 你已有 `03. 音视频_OpenGL_01~05` 系列笔记，包括 FBO，这是高质量基础
  - 必须掌握：在 GLSL shader 中写 YUV→RGB 转换矩阵（不同色彩空间的转换系数，如 BT.601 vs BT.709）
  - 深挖点：一张纹理的 wrap mode（GL_CLAMP_TO_EDGE vs GL_REPEAT）和 filter mode（GL_LINEAR vs GL_NEAREST）对画质的影响

- **实战加分**:
  - 你有视频画中画渲染的实战经验（见 `03. 音视频_OpenGL_03.使用OpenGL渲染画中画.md`），这是进阶功能
  - 能描述：多路视频流在 OpenGL 中如何合成到一个 FBO，然后编码输出——这覆盖了 MediaCodec + OpenGL 联动

---

### 11. TextureView vs SurfaceView

- **考察频率**: 高（音视频岗几乎必问，考察 Android 渲染体系理解）
- **置信度**: HIGH

- **典型问题**:
  1. SurfaceView 和普通 View 的根本区别是什么？为什么 SurfaceView 有独立的绘制线程？
  2. TextureView 是如何通过 SurfaceTexture 把 GL 纹理融合进 View 层级的？
  3. SurfaceView 为什么在 View 层级中会"穿孔"（透明挖洞）？
  4. TextureView 支持动画/Transform，SurfaceView 不支持，背后的技术原因是什么？
  5. 哪些场景只能用 SurfaceView？哪些场景只能用 TextureView？
  6. SurfaceHolder.Callback 的三个回调方法什么时候触发？
  7. TextureView.SurfaceTextureListener 的 `onSurfaceTextureAvailable` 回调后能做什么？
  8. GLSurfaceView 和 TextureView 的区别？什么时候用哪个？
  9. SurfaceView 的 z-order：`setZOrderOnTop()` / `setZOrderMediaOverlay()` 的作用？
  10. 直播推流场景选 TextureView 还是 SurfaceView？理由？

- **深度要求**:
  - 核心考点：SurfaceView 拥有独立 Surface（属于 SurfaceFlinger 的独立图层），TextureView 是 View 体系中的一个 HardwareLayer
  - 必须能回答：TextureView 为什么比 SurfaceView 耗电更多（额外的纹理拷贝）
  - 字节常问：同一个 Camera 预览，用 SurfaceView 还是 TextureView，为什么？

- **实战加分**:
  - 你有 FFmpeg 解码后用 OpenGL 渲染的经验，直接对应"自定义渲染用 GLSurfaceView"的实践
  - 如果你们的业务有视频贴纸/滤镜需求，TextureView + EGL 离屏渲染的方案是加分点

---

### 12. EGL 环境

- **考察频率**: 中（大厂音视频岗进阶考点，了解即可，能深讲是加分）
- **置信度**: HIGH

- **典型问题**:
  1. EGL 的作用是什么？它在 OpenGL ES 和 Android Surface 之间扮演什么角色？
  2. EGL 的核心对象：EGLDisplay / EGLContext / EGLSurface（WindowSurface / OffscreenSurface / PbufferSurface）的含义？
  3. 创建 EGL 环境的步骤：eglGetDisplay → eglInitialize → eglChooseConfig → eglCreateContext → eglCreateWindowSurface → eglMakeCurrent？
  4. 为什么每个 OpenGL 渲染线程都需要独立的 EGLContext？
  5. 两个 EGLContext 之间如何共享纹理？（`eglCreateContext` 的 `share_context` 参数）
  6. EGLSurface 与 Android 的 Surface / SurfaceTexture / SurfaceHolder 如何对应？
  7. 离屏渲染时 PbufferSurface 的使用场景？
  8. EGL Fence / Sync 机制在多线程渲染中的作用？
  9. `eglSwapBuffers` 的作用：将 EGLSurface 的后缓冲提交给 SurfaceFlinger？

- **深度要求**:
  - 你已有 `03. 音视频_OpenGL_04.EGL.md`，需要能画出 EGL 完整的初始化流程图
  - 重点：Context 共享机制，这在"解码线程上传纹理 → 渲染线程使用纹理"的场景中是必须理解的点
  - 深挖：为什么 `eglMakeCurrent` 是线程绑定的？（GL 上下文绑定到当前线程的 TLS）

- **实战加分**:
  - 你在视频解码 + OpenGL 渲染项目中，如果自己管理了 EGL 环境（而不是依赖 GLSurfaceView），这是极强的加分项
  - 能描述"解码线程 MediaCodec 输出 SurfaceTexture → 渲染线程 updateTexImage() → 绘制到 FBO → eglSwapBuffers"这条完整链路

---

## 优先级建议

> 综合考察频率、与你现有经验的匹配度、学习成本三个维度排序

| 优先级 | 考点 | 考察频率 | 你的现有基础 | 建议投入时间 | 备注 |
|-------|------|---------|------------|------------|------|
| P0 | 启动优化 | 极高 | 有实战基础 | 2天 | 补充数据和方法论，整理完整链路 |
| P0 | ANR 分析 | 高 | 有初稿笔记 | 1.5天 | 重点补 traces.txt 解读和线上监控方案 |
| P0 | 音视频基础（H264/YUV/同步） | 极高（音视频岗） | 有系统学习 | 2天 | 补充 B帧/PTS/DTS、YUV内存布局细节 |
| P0 | FFmpeg 架构与使用 | 高（音视频岗） | 有丰富实战 | 1天 | 整理成"能讲清楚设计思路"的答题模板 |
| P1 | 卡顿优化 | 高 | 基础了解 | 2天 | 重点搞清楚 Choreographer + Systrace 实操 |
| P1 | 内存优化 | 高 | 基础了解 | 2天 | 重点搞 LeakCanary 原理 + Bitmap 内存问题 |
| P1 | MediaCodec | 高（音视频岗） | 有相关背景 | 1.5天 | 重点状态机 + Surface模式 + CSD |
| P1 | TextureView vs SurfaceView | 高（音视频岗） | 有使用经验 | 1天 | 重点讲清楚底层渲染机制的区别 |
| P2 | OpenGL ES 渲染管线 | 中高（音视频岗） | 有系统笔记 | 1天 | 主要查漏补缺，准备 YUV→RGB shader |
| P2 | EGL 环境 | 中 | 有笔记基础 | 0.5天 | 重点整理 Context 共享机制 |
| P3 | 包体积优化 | 中 | 无 | 1天 | 了解主流手段，有 FFmpeg so 库可结合 |
| P3 | 电量优化 | 中低 | 无 | 0.5天 | 了解 Battery Historian 和硬解省电优势 |

---

## 面试策略建议

### 音视频岗 vs 通用 Android 岗

你有明显的音视频实战优势，强烈建议定位音视频方向岗位（抖音/剪映/腾讯视频/快手），这些岗位：
- 普通候选人几乎没有 FFmpeg 实战经验，你的差异化极为明显
- 薪酬通常高于通用 Android 岗 20%-40%
- 面试深度更聚焦，准备范围反而更窄（音视频 + 性能 + Android 基础）

### 结构化答题框架

大厂面试官期待的回答结构：概念 → 原理 → 实战案例 → 遇到的坑 → 改进方向

避免说"我用过 XXX 解决了问题"，要说：
"我们遇到了 [具体问题]，分析发现原因是 [原理层面]，我采用了 [方案] 解决，具体是 [技术细节]，最终 [量化结果]。"

### 你的独特卖点

1. FFmpeg JNI 集成全流程：从编译脚本到 JNI 封装再到上层调用，完整经验不多见
2. OpenGL + FFmpeg 联动渲染：解码 + 渲染管线的端到端理解
3. 鸿蒙跨平台编译：FFmpeg for OpenHarmony，这是 2025/2026 年的差异化加分项
4. 音视频同步实战：真实项目中做过 PTS 同步，比"知道概念"强得多

### 补充建议

- 每个考点都要准备一个"问题-原因-方案-结果"的实战故事，没有真实案例就构造一个合理的模拟场景
- 准备好被追问 5 层：面试官不会在你说完就停，会追问"为什么这样设计""还有其他方案吗""如果 X 改变了你怎么处理"
- 字节面试偏爱系统设计题：如"设计一个视频播放器"——这类题考察你能否把所有知识点串联成一个完整的架构

---

*置信度说明：本文档基于截至 2025 年 8 月的训练数据中的大量大厂面经整理，性能优化和音视频基础部分 HIGH 置信度，包体积/电量部分 MEDIUM 置信度。WebSearch 在本次调研中不可用，建议后续手动搜索 2026 年最新面经验证高频题变化。*
