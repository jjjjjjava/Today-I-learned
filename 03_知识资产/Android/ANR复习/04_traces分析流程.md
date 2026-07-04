# 第 4 篇 · 用 Bugly 分析 trace 定位 ANR：从 trace 怎么来，到怎么读

> 前置知识：前三篇的 ANR 触发机制（埋雷-拆雷-爆雷、四类阈值、SIGQUIT dump）
> 难度：进阶（实战核心篇）
> 预计阅读时间：16 分钟
> 本篇按你的思路组织：先讲 trace 怎么产生（Bugly 原理）→ 再讲 trace 的特殊性 → 最后讲三步分析法。三步法是你亲手推导的，替代通用"六步 SOP"。

---

## 上一篇思考题复盘

> 📝 你选择直接继续，未提交作答。下面给出第 3 篇三题的正确答案，对照自检。

**第 1 题：同样前台 5s，Broadcast 的 5s 和 Input 的 5s 计时方式有何本质区别？**
> - **Broadcast 是埋雷模型**：从"系统开始把广播派给这个接收者、埋下超时消息"那一刻起算，到点查 `onReceive` 有没有返回。计时起点 = **系统调度该任务的时刻**。
> - **Input 是流式模型**：从 **eventTime（事件产生时刻）**起算，系统侧排队 + 分发 + 等 ACK 全程都算进去。
> - 本质区别：一个从"**系统派任务时**"起算，一个从"**事件诞生时**"起算（且含系统侧排队）。

**第 2 题：为什么 Provider 超时直接杀进程、Service 超时弹框？**
> 看进程处于哪个阶段。Provider 超时时进程还卡在**启动初始化**（连 Application 都没起来），等于"启动失败"，杀掉重来代价小又合理；Service 超时时进程**已经在正常运行**、只是这次回调卡了，贸然杀会丢现场，所以给"等待/关闭"弹框让用户选。核心：**"还没起来" vs "已在运行"。**

**第 3 题：App 主线程只花 1s 却仍 Input ANR，中间发生了什么？对排查的启发？**
> 5s 从 eventTime 起算：事件可能在系统侧 mInboundQueue 排了很久队、或**前一个事件长期占着 waitQueue 头部一直没 ACK**（历史欠账），把后面的拖超时。启发：**排查 Input ANR 不能只盯 App 自己这一帧的耗时**，要结合 eventTime 和系统侧排队。

---

## ??? 解答

> 💬 上一篇无 `???` 标注，直接进入新内容。

---

## 正文内容

我们已经把 ANR 的概念和源码吃透了。这一篇换个落点：**线上拿到一份 Bugly 的 trace，怎么分析 ANR？** 顺序是——先搞清这份 trace 怎么来的，再认清它的特殊性，最后才是分析流程。

### 一、Bugly 的 trace 文件是怎么产生的？

要会分析，先懂它的来源。Bugly 核心依赖**三个组件**：

```text
1. FileObserver       —— 观测系统 trace 文件
2. 错误状态轮询       —— ActivityManager.getProcessesInErrorState() 定性确认
3. Bugly 线程（Watchdog）—— 主动探活 + 抓栈，监控核心
```

**① FileObserver：观测系统 trace 文件**
`appNotResponding` 被调用后，系统会自己 dump 堆栈写入系统 trace 文件。Bugly 用 FileObserver 监听这个文件的写入，一旦有写入，就能拿到"系统判定的 ANR 原因"。
> ⚠️ 但随着 Android 版本权限收紧（11+ 起 SELinux 收紧 `/data/anr/`），普通 App 基本读不到了——**这条路在高版本已基本失效**，最多算兜底。

**② 错误状态轮询：定性确认**
⚠️ 系统对第三方 App **没有 ANR 广播/回调**（这点和 crash 不同）。真实定性手段是轮询 `ActivityManager.getProcessesInErrorState()`：爆雷后 AMS 把进程标为 `NOT_RESPONDING`，轮询到即可确认"**确实发生了系统 ANR**"；返回的 `ProcessErrorStateInfo` 还带 shortMsg/longMsg——平台 issue 标题里的 reason（如 "Input dispatching timed out"）正是从这里来的。

**③ Bugly 线程（Watchdog）：监控核心**
这是 Bugly 工作的核心，一个死循环探活：

```text
循环：
  1. 把自身标记位置为 false
  2. post 一个消息到主线程（这个消息执行时会把标记位改回 true）
  3. 自己阻塞 sleep 5s
  4. 醒来检查标记位：
       仍是 false → 说明主线程 5s 内没处理到这个消息 → 大概率卡了
                  → 抓所有线程堆栈暂存（但先不上报）
  5. 只有轮询 getProcessesInErrorState() 查到 NOT_RESPONDING、确认不是误报，才把暂存的堆栈上报
```

关于 Watchdog 抓的栈，记两个限制：

```text
· 它用 Thread.getAllStackTraces()，只有【Java 栈】，看不到 Native 层
  （这正是它不如 xCrash / Matrix 的地方，下一篇对比）
```

Watchdog 这套"旁观探活"也带来**两个固有缺陷**：

```text
· 误报：主线程在跑合法长任务、还没到系统 ANR 阈值，Watchdog 5s 一到就先以为卡了。
· 漏报 Input ANR：Input 超时判定在系统侧 waitQueue、不经过 MessageQueue。
        主线程可能照常处理 Watchdog 的探活消息（看着"活着"），
        但触摸 5s 没回 ACK 照样被系统判 ANR —— Watchdog 探不到。
        （正好呼应第 1 篇思考题 3：App 自检探不到 Input ANR）
```

> 小结：**系统 trace 是 `appNotResponding` 时由 SignalCatcher 收 SIGQUIT 一次性 dump 的；Bugly 则靠 Watchdog 每 5s 探活抓 Java 栈、再轮询错误状态定性确认才上报。**

### 二、trace 文件的特殊性

理解了来源，就能理解它两个"坑"：

```text
1. 它只是一个【快照】，不记录 ANR 前后的过程（没有时间轴）。
2. 它有【滞后性】。
```

滞后有两个来源，别混：

```text
· 系统侧：SignalCatcher 在 ANR 判定那一刻一次性 dump，但那时卡顿可能已结束。
· Bugly 侧：Watchdog 固定 5s 采一次样，精度低，更容易错过爆发瞬间。
```

所以经常出现这种现象：

```text
明明报了 ANR，trace 里主线程却是 Native 态趴在 nativePollOnce / epoll_wait（MessageQueue.next 的空闲等待，消息队列没消息；注意 state 是 Native 不是 Sleeping）——
一个很"干净"的状态。这多半是抓到了 ANR 前后、而非发生时的现场。
这种帧基本作废，得换样本或看聚合，绝不能据此说"主线程没问题"。
```

### 三、trace 文件的分析流程（三步法）

懂了来源和特殊性，再叠加前几篇的 ANR 原理，分析思路就出来了——分三步。

#### 第一步 · 确定 ANR 的类型

ANR 是系统对四类重要任务的超时判定，四类时限不同：

```text
Service          前台 20s   后台 200s
Broadcast        前台 5s    后台 60s
ContentProvider  前台 10s
Input            前台 5s
```

先搞清类型，才知道"**主线程本该在哪个时间段内、完成什么任务**"。
> 类型（Reason）来自 ActivityManager 的 ANR 日志，**不在线程 trace 里**，要去 logcat / 平台 issue 信息里拿。

#### 第二步 · 锁定观测对象：主线程

四类 ANR 的流程都一样：**系统下发任务 → 主线程在给定时间内处理 → 处理完经 Binder 拆雷**。所以核心永远收敛成一句：

```text
这段时间，主线程为什么没在给定时间内完成任务？
```

（理论上也可能是系统 Binder 能力被打满、调用过不去，但绝大多数是主线程自身的问题，先不考虑那种小概率。）

#### 第三步 · 分层观测：主线程为何没执行完

**第一层 · 环境（→ C 类）：系统给不给 CPU**
主线程没干完不一定是你代码的问题——也可能是别的进程把 CPU 打满了，主线程拿不到时间片。**看主线程 CPU 使用率：如果它很低、而系统整体 CPU 很高，大概率是环境问题（没时间片资源）。**

**第二层 · 主线程自身状态：它当时在干嘛**

```text
RUNNABLE + 栈顶是 IO 等耗时任务   → A 类：自己太忙，在执行耗时代码
WAITING / BLOCKED + 栈顶在等锁    → B 类：被别人困住了
Native 态趴在 nativePollOnce（MessageQueue.next 空闲等待）→ 抓到无用帧了，换样本分析
```

**第三层 · 追堆栈 + 锁链：定性到根**

```text
· RUNNABLE：追主线程堆栈，看到 IO / OkHttp 之类 → 基本确定方向：主线程在做耗时 IO/网络。
· BLOCKED：看它 waiting 在哪个锁（trace 记了锁地址）
     → 全局搜这个锁地址，找到持锁线程，看它在干嘛、为何不释放：
         它在执行耗时任务            → 它拖累了主线程
         它反过来又等主线程持有的锁  → 互相死锁
```

> 🔧 真实案例（B 类死锁 · 完整锁链）：登录页走"极验"onelogin 一键登录，它内部调联通 `cuGetToken`，并把这个**带锁的任务 post 到了主线程**。按第三层锁链追踪，一环环追下去：
>
> ```text
> main  BLOCKED，waiting to lock A(0x0fd09ed5)
>   └ 全局搜 → A 被 tid58 持有；tid58 又 waiting to lock B(0x0a0157b6)
>        └ 全局搜 → B 被 tid54 持有；tid54 又 waiting to lock A
>             └ 58 ⇄ 54 形成 AB-BA 死锁，谁都不释放
>   ⇒ main 要的锁 A 攥在死锁线程 tid58 手里 → 永远等不到 → 一直 BLOCKED → ANR
> ```
>
> **根因**：联通的两个线程加锁顺序相反（一个 A→B、一个 B→A）凑成 AB-BA 死锁；极验又把这个"带锁任务"post 到主线程，把主线程一起拖死。
> **结论**：闭源三方库的根因，**定位得到 ≠ 改得了**——只能反馈或弃用。这也反向印证了修复方向：**统一全局加锁顺序**正是用来破这种 AB-BA 循环等待的。

#### 收口

核心还是：**先用"环境 + 主线程状态"判断大方向，再顺着 trace 里的线程堆栈一步步查细节。** 实战里很多并不难查，多是写代码粗心——比如主线程做 `saveToAlbum` 存图到相册、主线程等子线程的网络 IO；也有真没法解决的，比如上面那种闭源三方 SDK 的死锁。

### 附 · 根因速查卡（定性后对号入座）

```text
RUNNABLE + 栈顶 IO/网络/数据库      → A 类 IO     → 异步化、移出主线程
RUNNABLE + App CPU 高 + 业务计算    → A 类计算    → 拆分任务、限制复杂度
BLOCKED + waiting to lock           → B 类锁竞争  → 追持锁线程、统一加锁顺序
两线程互相 waiting to lock          → B 类死锁    → 统一加锁顺序、破循环等待
WAITING 在业务对象 + 工作线程被卡   → B 类等通知  → 排查 notify 链路与状态机
卡在 BinderProxy.transact           → B 类同步Binder→ 减少主线程同步 Binder、查远端/system_server
RUNNABLE + 堆栈平平 + 系统 CPU 爆满 → C 类 CPU 饥饿→ 限并发、降后台压力
WAITING + MessageQueue + CPU 正常   → 当前 trace 可能无效 → 结合 logcat/reason/聚合再查
```

### 附 · 真实案例速览（按类对号入座）

> 项目里真实修过的 ANR，都是按上面"环境 → 主线程状态 → 追堆栈/锁链"套路定位后归类。保留 Issue ID 便于回查平台聚合。

**A 类 · 主线程自己太忙（耗时 / IO / 同步调用）**

> 🔧 `store` 等取任务锁，锁内又卡在网络　`ID: D4D11C8A…`
> **根因**：主线程执行 store 时等 `processNextTask` 的锁，而**这把锁内部还在阻塞等网络结果**——锁被网络 IO 拖长。
> **解决**：网络请求移到锁外，**锁内只做"取任务"**，缩短持锁时间。

> 🔧 `onDetachedFromWindow` 同步 release 播放器　`ID: 5046EA3D…`
> **根因**：主线程 `onDetachedFromWindow` 直接调到 `IjkMediaPlayer.release()`，同步释放耗时。
> **解决**：①引用先存局部变量 ②立即置空防重复调用 ③异步执行 `stop()/release()`。

> 🔧 `EasyDataStore` 主线程 `runBlocking`　`ID: FAF55E8F… / 5832C3F5…`
> **根因**：`putData/clearData` 在主线程 `runBlocking` 同步等协程，直接卡死主线程。
> **解决**：去掉 runBlocking，改异步写入。

> 🔧 `IjkPlayView.openVideo()` 内同步 `reset()`　`ID: B128B3C0…`
> **根因**：`openVideo()` 同步调用 `reset()`，主线程阻塞。
> **解决**：reset 异步化 / 移出主线程。

> 🔧 `CameraClickActivity` 存相册走主线程 I/O　`ID: 2848AFD7…`
> **根因**：保存本地相册的文件 I/O 放在主线程（即收口里说的 `saveToAlbum` 那类）。
> **解决**：I/O 移出主线程。

**B 类 · 被别人困住（同步 Binder / 锁竞争）**

> 🔧 主线程同步 Binder 打到系统 `MediaProvider`　`ID: EECF74B4…`
> **根因**：主线程经 Binder 与系统 MediaProvider 进程通信，**对端进程繁忙**时主线程卡在 transact。
> **解决**：查询移到协程，完成后再回主线程处理。

> 🔧 APNG 后台解码线程抢 `MessageQueue` 锁 → Input 类型 ANR　`ID: AD8CD1F1… / F5FC358B…`
> **现象**：打开 `CameraClickActivity` 触发 ANR，主线程卡在 `MessageQueue.next()` 超 5s（Input 类型）。
> **追踪**：trace 里 `FrameDecoderExecutor-3` 持 MessageQueue 锁正在 `enqueueMessage`，其余解码线程与主线程同等这把锁 → 全局搜 `APNGDrawable` 使用者、排除三方 SDK 后定位 `DragFloatActionNew2Button`（`BaseActivity.onCreate()` 构造，每实例 2 个常驻解码线程；回退栈存活 2 个 BaseActivity ⇒ 4 个 `FrameDecoderExecutor`，与 trace 线程数吻合）。
> **根因**：`onStop()` 没暂停 APNG 解码线程，它们以帧率频率狂 `Handler.post() → enqueueMessage()` 抢锁，**回退栈越深竞争越凶**，卡死主线程 `next()`。
> **解决**：Button 加 `pause/resumeApngAnimations()`（调两个 drawable 的 `stop()/start()`）；`onStop()` 暂停、`onStart()` 恢复——**不可见即停解码线程**，消除后台锁竞争。

---

## 思考题

1. Bugly Watchdog 的"5s 抓一次"，和系统 SignalCatcher 的 dump，触发时机有什么不同？为什么 Bugly 常抓到主线程趴在 `MessageQueue.next` 的"干净帧"？
2. 为什么 Bugly Watchdog 会**漏报 Input ANR**？请结合 Input 的检测机制（不经过 MessageQueue）说明。
3. 主线程 `BLOCKED` 在锁 `0x123`，你按锁链追到持锁线程，发现它**也在** `waiting to lock` 主线程持有的另一把锁。这是什么情况？修复方向是什么？

## 你的反馈

> 在这里写下你的问题、感悟、不理解的地方，或希望下一篇深入的方向。
> 文中任意位置可用 `???你的困惑` 就地标注，我下一篇优先解答。
> 读完回我「继续」或写下思考题答案，我据此生成下一篇（模块四深入：xCrash / Matrix 的深度介入模式 + sigaction vs sigwait）。
