# 附录 A｜一条冷启动怎样走到首屏？

## 本篇只解决一个问题

用户点击图标后，系统、应用主线程和渲染系统分别做了什么？

```text
1. system_server 请求创建进程
2. Zygote 孵化应用进程，ActivityThread 建立主线程
3. Application、ContentProvider 初始化
4. Activity、Window 和 View 树创建
5. measure / layout / draw，最终合成显示
```

## 第一阶段：应用进程从哪里来？

```text
Launcher 发起启动
→ system_server 检查目标进程
→ 通过 Zygote socket 请求孵化
→ Zygote fork 应用进程
→ 进入 ActivityThread.main
```

Zygote 已预加载常用类和资源，应用进程通过 fork 继承这些只读内存页，减少每个应用单独初始化的成本。

本项目区间从 `bindApplication` 开始，因此用户点击、system_server 调度、Zygote fork 等时间没有进入项目指标，但仍属于完整启动体验。

## 第二阶段：系统怎样通知应用启动？

`ActivityThread.main()` 准备主 Looper、创建 ActivityThread、连接 system_server，最后进入 `Looper.loop()`。

`ActivityThread` 不是 Java `Thread` 子类，而是应用主线程侧的框架控制器。

应用通过系统服务代理主动调用 system_server；system_server 则通过应用的 `ApplicationThread` Binder 接口反向发送 bind、Activity 生命周期和 Service 等事务。

Binder 线程接收事务后，通常再把生命周期工作交回主线程。跨进程交接发生在 Binder，应用生命周期和 UI 工作仍主要由主线程串行执行。

## 第三阶段：为什么 Provider 早于 `Application.onCreate()`？

```text
handleBindApplication
→ 准备 LoadedApk、ClassLoader、Resources
→ 创建并 attach Application
→ 安装 ContentProvider
→ ContentProvider.onCreate
→ Application.onCreate
```

不同 Android 版本内部细节会变化，但 Provider 通常在 `Application.onCreate()` 前初始化。

三方 SDK 可以借助 Manifest Provider 自动启动。即使业务没有主动调用 SDK，Provider 的类加载、IO 或数据库工作也可能进入主线程关键路径。

本项目 `bindApplication` 阶段约 220ms，不是第一轮 P0。机制存在不等于当前项目应该优先治理。

## 第四阶段：`setContentView()` 做了什么？

system_server 将 Activity 启动事务交给应用后，主线程创建 Activity、绑定 `PhoneWindow` 并调用生命周期。

```text
Activity.attach：创建或绑定 PhoneWindow
→ setContentView：安装 DecorView、解析 XML、创建 View 树
→ WindowManager.addView：创建 ViewRootImpl
```

`setContentView()` 返回时，View 对象和层级已经建立，但通常还没完成 measure/layout，宽高仍可能是 0。

ViewPager2 全量预加载、首页模块一次性添加和静态 XML WebView 都发生在这一阶段，因此会增加 View 创建和布局成本。

## 第五阶段：`addView()` 后为什么还没显示？

```text
WindowManager.addView
→ ViewRootImpl.requestLayout / scheduleTraversals
→ Choreographer 等待 VSYNC
→ doFrame
→ performTraversals
→ measure / layout / draw
→ RenderThread / GPU
→ Buffer 提交
→ SurfaceFlinger 合成显示
```

硬件加速场景下，主线程 draw 主要记录绘制命令，后面仍有 RenderThread、GPU 和 SurfaceFlinger 的处理。

`doFrame` Wall 高而 Self 低，说明成本位于它调度的 traversal 或业务回调。`addView()`、`onResume()` 和主线程 draw 都不能单独等同于像素已经显示。

项目 marker 等到权限模块加入 View 树后的下一次 draw，比数据返回或立即 `addView()` 更接近首页框架可见，但仍不是官方 TTFD。

## 五个阶段怎样解释本项目？

| 阶段 | 解释的问题 |
|---|---|
| 进程创建 | 为什么项目区间不从用户点击开始 |
| 主线程与 Binder | 为什么生命周期和 UI 工作回到主线程 |
| Application / Provider | 为什么 SDK 自动初始化可能进入启动路径 |
| Activity / View 树 | 为什么 ViewPager2 和 XML WebView推高 inflate |
| 渲染 | 为什么要等 draw，以及 `doFrame` 为什么还要下钻 |

## 常见误区

1. `ActivityThread` 是一个 Java Thread 子类。
2. Binder 线程直接执行全部 Activity 生命周期和 UI 工作。
3. 业务没调用 Provider，所以它不会影响启动。
4. `setContentView()` 返回时 View 已完成布局。
5. `onResume()` 或 `addView()` 等于首帧已经显示。

## 本篇自测

1. system_server 怎样让应用执行生命周期？
2. Provider 与 `Application.onCreate()` 的常见顺序是什么？
3. PhoneWindow、DecorView、ViewRootImpl 分别承担什么？
4. 从 `addView()` 到显示还缺哪些步骤？
5. 哪个阶段解释了本项目的 ViewPager2 和 WebView 热点？

## 一句话总结

冷启动不是一个方法，而是一条跨越 system_server、应用主线程和渲染系统的连续关键路径。
