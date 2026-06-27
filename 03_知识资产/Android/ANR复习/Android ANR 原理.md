# Android ANR 核心机制与实战治理笔记

## 模块结构

```text
Android ANR 核心机制与实战治理
├─ 第 1 章：ANR 基础概念
├─ 第 2 章：Service ANR 源码全流程
├─ 第 3 章：四类 ANR 差异对比
├─ 第 4 章：traces 实战分析
└─ 第 5 章：线上 ANR 监控方案
```

## 第 1 章：ANR 基础概念

```text
第 1 章：ANR 基础概念
├─ 1. ANR 是什么，为什么需要它
├─ 2. 如果让我们设计，ANR 检测机制该怎么做
└─ 3. 除了 Input，还有哪些场景也需要 ANR 检测
```

### 1. ANR 是什么，为什么需要它

ANR 全称是 `Application Not Responding`，也就是应用无响应。

如果没有 ANR 机制，当 App 长时间处理不了用户点击、滑动等关键事件时，用户只能被动等待，或者手动强制结束进程。系统无法统一判断这个 App 是“只是慢了一点、不跟手”，还是“已经卡死、无法响应”；开发者也拿不到当时的线程堆栈和现场信息，不知道问题发生在哪里。

所以 ANR 的意义是：系统需要一套约定机制来判断应用是否处于无响应状态。当关键任务超时未完成时，系统可以弹窗让用户选择继续等待或关闭应用，同时记录线程堆栈等现场信息，帮助开发者定位问题。

一句话压缩：

```text
ANR 是系统用来识别 App 关键任务超时无响应、提示用户并记录现场的机制。
```

### 2. 如果让我们设计，ANR 检测机制该怎么做

如果让我们自己设计一个 ANR 检测机制，可以参考看门狗模型：

```text
我给你一个任务；
我开始计时；
你完成后告诉我；
如果超时还没有告诉我，我就认为出问题了。
```

对应到 ANR，就是“埋雷 - 拆雷 - 爆雷”模型。

```text
埋雷：
系统调度 App 开始执行一个有时限的任务，同时系统自己设置一个超时检测。

拆雷：
App 执行完任务后，通过 Binder 回调系统，告诉系统这个任务已经完成，
系统移除对应的超时检测。

爆雷：
规定时间到了，系统发现这个任务还没有完成，也就是雷还没有被拆掉，
于是判定 App 发生 ANR。
```

这个模型的关键点是：计时和判定应该由 App 外部的系统进程负责，而不是完全依赖 App 自己。因为 App 主线程一旦卡死，App 内部的检测逻辑也可能无法可靠运行。

基础阶段先用这个模型理解大多数组件类 ANR。Input ANR 比较特殊，不完全是发送炸弹消息的模型，后面在“四类 ANR 差异对比”章节单独展开。

### 3. 除了 Input，还有哪些场景也需要 ANR 检测

最容易理解的是 Input ANR：

```text
用户点击或滑动后，App 没有及时消费输入事件，系统认为应用无响应。
```

但 ANR 不只发生在输入事件上。常见 ANR 包括：

```text
Input ANR：
用户输入事件没有及时消费。

Service ANR：
Service 生命周期回调没有及时执行完成。

Broadcast ANR：
BroadcastReceiver.onReceive 没有及时返回。

ContentProvider ANR：
ContentProvider 初始化或发布没有及时完成。
```

因此，基础概念阶段要形成的核心认知是：

```text
ANR 不是单纯等“主线程卡不卡”，
而是系统在等待 App 完成某个有时限的关键任务。
不同任务对应不同类型的 ANR。
```

## 第 2 章：Service ANR 源码全流程

```text
第 2 章：Service ANR 源码全流程
├─ 1. App 如何发起 startService
├─ 2. ActiveServices 如何给 Service 埋雷
├─ 3. system_server 如何通知 App 执行 Service
├─ 4. App 执行完成后如何拆雷
└─ 5. 超时后 serviceTimeout 如何判定 ANR
```

### 1. App 如何发起 startService

当 Activity 中调用 `startService`，本质上是通过：

```text
ActivityManager.getService().startService
```

这次 Binder 调用进入 `system_server` 进程中的 `AMS.startService`。

AMS 接收到请求后，会转交给 `ActiveServices.startServiceLocked`。后续 Service 的启动、埋雷、调度 App 执行、拆雷、超时检测，主要都在 `ActiveServices` 中完成。

这一段只需要抓住三个关键词：

```text
ActivityManager.getService().startService
Binder 跨进程
AMS -> ActiveServices
```

### 2. ActiveServices 如何给 Service 埋雷

系统准备让 App 执行 Service 生命周期回调前，会调用 `bumpServiceExecutingLocked` 进行埋雷。

埋雷核心做三件事：

```text
1. 记录开始执行时间 executingStart
   后面 serviceTimeout 会用它判断这个 Service 是否真的超过 20s / 200s。

2. 把 ServiceRecord 加入进程维度的 mExecutingServices
   表示这个进程当前有 Service 回调正在执行，系统需要观察。

3. 发送 Service 超时消息
   这个消息是进程维度的超时检测，不是每个 Service 都无脑发送一颗独立的雷。
```

第 3 点的判断关键是：

```text
如果这个进程的 mExecutingServices 是从空变为非空，
说明这是该进程当前第一个正在执行的 Service，
需要 scheduleServiceTimeoutLocked 发送 Service 超时消息。

如果 mExecutingServices 里已经有 Service 正在执行，
说明这个进程维度的超时检测已经存在，
不需要为每个 Service 重复发送一颗雷。
```

这里要区分两个概念：

```text
mExecutingServices：
进程维度，表示这个进程里当前有哪些 ServiceRecord 正在执行回调。

executeNesting：
单个 ServiceRecord 内部的执行嵌套计数，
表示这个 Service 当前还有几层 in-flight 回调没有完成。
它不是炸弹数量。
```

一句话压缩：

```text
bumpServiceExecutingLocked 埋雷时，会记录 Service 的 executingStart，
把 ServiceRecord 放入进程的 mExecutingServices；
如果这是该进程第一个正在执行的 Service，才发送进程维度的 Service 超时消息。
```

### 3. system_server 如何通知 App 执行 Service

雷埋好后，`ActiveServices` 会找到目标 App 进程的 `ApplicationThread` Binder 代理对象，调用：

```text
ApplicationThread.scheduleCreateService
```

通知 App 创建 Service。

这个 Binder 调用到达 App 进程后，先由 App 的 Binder 线程池接收。`ApplicationThread` 不会在 Binder 线程里直接执行 `Service.onCreate`，而是把请求封装成 `CREATE_SERVICE` 消息，发送给 `ActivityThread` 的 `mH`。

App 主线程 Looper 取出 `CREATE_SERVICE` 消息后，进入 `handleCreateService`，再反射创建 Service 实例，执行 `Service.onCreate`。

核心链路：

```text
AMS / ActiveServices
→ ApplicationThread.scheduleCreateService
→ App Binder 线程池接收
→ 发送 CREATE_SERVICE 到 ActivityThread.mH
→ App 主线程 handleCreateService
→ 反射创建 Service
→ 执行 Service.onCreate
```

关键认知：

```text
Binder 线程只负责接收系统调度请求并投递消息；
Service 生命周期回调最终在 App 主线程执行。
```

### 4. App 执行完成后如何拆雷

App 主线程执行完 `Service.onCreate` / `onStartCommand` 等 Service 回调后，会调用 `serviceDoneExecuting`，通过 Binder 回调 `system_server` 中的 AMS / ActiveServices，告诉系统这次 Service 执行已经完成。

拆雷逻辑分两层：

```text
第一层：ServiceRecord 维度
找到对应 ServiceRecord 后，将 executeNesting--。
如果 executeNesting 变成 0，说明这个 Service 当前没有未完成的执行回调，
就把它从进程的 mExecutingServices 中移除。

第二层：进程维度
如果这个进程的 mExecutingServices 已经空了，
说明该进程当前没有任何正在执行的 Service 回调，
于是移除这个进程对应的 Service 超时消息。
```

关键认知：

```text
executeNesting 决定单个 ServiceRecord 是否完成；
mExecutingServices 是否为空决定这个进程的 Service 雷能不能拆掉。
```

### 5. 超时后 serviceTimeout 如何判定 ANR

Service 超时消息到期后，`serviceTimeout` 不会立刻等同于 ANR。

更准确地说：

```text
Service 超时消息只是检查触发器，不是最终判定器。
```

进入 `serviceTimeout` 后，系统先排除两类情况：

```text
1. 进程已经死亡 / killed
2. mExecutingServices 已经为空
```

如果进程已经死了，或者集合已经空了，说明不需要再报 ANR，直接 return。

如果集合不为空，系统会遍历 `mExecutingServices`，根据每个 `ServiceRecord.executingStart` 判断是否真的超时：

```text
maxTime = 当前时间 - Service 超时阈值

如果某个 ServiceRecord.executingStart < maxTime，
说明这个 Service 从开始执行到现在已经超过 20s / 200s，
这个 Service 才是真的超时。
```

如果找到了真正超时的 Service：

```text
serviceTimeout
→ appNotResponding
→ 收集 traces / CPU / DropBox 等现场
→ 前台进程由 system_server 的 UiThread 弹出 ANR Dialog
→ 后台进程可能直接杀掉
```

如果集合不为空，但没有任何 Service 真正超时：

```text
说明这次超时消息只是醒早了；
系统会根据还在执行的 Service 的到期时间，
重新 post 下一次 Service timeout。
```

这里最重要的一句话：

```text
雷只是轮询触发器，真正的 ANR 判定依据是 ServiceRecord.executingStart。
```

### appNotResponding 后续流程

当 `serviceTimeout` 判定确实发生 ANR 后，会进入 `AMS.appNotResponding`。

后续流程可以按这个顺序理解：

```text
1. system_server 给 ANR 进程发送 SIGQUIT
   App 进程中的 Signal Catcher 线程负责 dump 本进程所有线程堆栈，
   写入 /data/anr/traces.txt。

2. system_server 也可能给 system_server 等相关进程发送 SIGQUIT
   用来辅助判断是不是系统侧进程拖住了 App。

3. 收集 CPU、内存、DropBox 等现场信息。

4. 根据进程状态决定处理方式：
   前台进程：通过 system_server 的 UiThread 弹出 ANR 对话框。
   后台进程：可能直接杀掉。
```

两个易错点：

```text
traces.txt 里的 App Java 堆栈主要是 App 自己的 Signal Catcher dump 出来的；
ANR 弹框不是 App 自己画的，而是 system_server 的 UiThread 画的。
```

## 第 2 章收束

```text
Service ANR =
App 通过 Binder 调 AMS.startService；
AMS 转交 ActiveServices；
ActiveServices 在调度 Service 回调前调用 bumpServiceExecutingLocked 埋雷；
system_server 通过 ApplicationThread 通知 App；
App Binder 线程转发消息给 ActivityThread.mH；
App 主线程执行 Service.onCreate / onStartCommand；
执行完成后 serviceDoneExecuting Binder 回调拆雷；
如果超时消息触发时仍有 ServiceRecord 的 executingStart 超过阈值，
则进入 appNotResponding，收集现场并弹框或杀进程。
```

## 第 3 章：四类 ANR 差异对比

```text
第 3 章：四类 ANR 差异对比
├─ 1. 当前 ANR 的四个小类、两个大类
├─ 2. 四类 ANR 总览表
├─ 3. ContentProvider ANR 为什么是异类
└─ 4. Input ANR 为什么是独立王国
```

### 1. 当前 ANR 的四个小类、两个大类

当前 ANR 主要可以分成四个小类：

```text
Service ANR
Broadcast ANR
ContentProvider ANR
Input ANR
```

如果按检测方式继续抽象，可以分成两个大类：

```text
时间触发型：
Service / Broadcast / ContentProvider

它们更接近系统设置一个超时检测，
到时间后检查 App 是否完成了对应任务。

流式触发型：
Input

Input 不是传统炸弹消息模型，
而是在 InputDispatcher 的事件分发循环中持续主动检测。
```

所以第 3 章的核心不是单纯背四个超时时间，而是先建立分类框架：

```text
四个小类：Service / Broadcast / ContentProvider / Input
两个大类：时间触发型 / 流式触发型
```

### 2. 四类 ANR 总览表

四类 ANR 可以先用一张表建立整体印象：

```text
| 类型            | 前台超时 | 后台超时 | 埋雷 / 检测方式               | 爆雷处理            |
|-----------------|----------|----------|-------------------------------|---------------------|
| Service         | 20s      | 200s     | scheduleServiceTimeoutLocked  | appNotResponding    |
| Broadcast       | 5s       | 60s      | setBroadcastTimeoutLocked     | appNotResponding    |
| ContentProvider | 10s      | —        | attachApplicationLocked       | removeProcessLocked |
| Input           | 5s       | —        | 无炸弹，dispatchOnce 主动检测 | appNotResponding    |
```

这里要先抓住三个判断：

```text
Service / Broadcast 是比较标准的时间触发型 ANR；
ContentProvider 也属于时间触发型，但爆雷处理很特殊；
Input 是流式触发型，是四类 ANR 里机制最特殊的一类。
```

### 3. ContentProvider ANR 为什么是异类

ContentProvider ANR 的特殊点不在于有没有超时检测，而在于它的埋雷时机和爆雷处理都和 Service / Broadcast 不一样。

埋雷时机：

```text
ContentProvider 不是 App 查询 Provider 的时候才开始计时，
而是在进程 attach 阶段，也就是 AMS.attachApplicationLocked 中设置超时检测。
```

拆雷过程：

```text
App 完成 Provider 初始化并发布后，
通过 AMS.publishContentProviders 告诉系统 Provider 已经准备好。
```

爆雷过程：

```text
如果 Provider 发布超时，
会走 processContentProviderPublishTimedOutLocked，
最终 removeProcessLocked 直接移除进程。
```

处理结果：

```text
不弹 ANR 框；
不走 appNotResponding；
直接杀进程。
```

为什么这么处理：

```text
Provider 初始化失败，说明这个进程还没有正常启动完成。
这种情况下继续等待意义不大，
所以系统直接移除进程，
而不是像前台 Service / Input 那样给用户弹等待或关闭的选择。
```

一句话压缩：

```text
ContentProvider ANR 是时间触发型，但它是异类：
埋雷发生在进程 attach 阶段，
超时后直接 removeProcessLocked 杀进程，
不弹框，也不走 appNotResponding。
```

### 4. Input ANR 为什么是独立王国

Input ANR 的特殊点是：

```text
它不是 Handler 定时炸弹模型，
而是 InputDispatcher 在事件分发循环中主动检测。
```

#### 为什么需要 IMS 和独立线程

Input 事件高频，而且对响应时间非常敏感。

如果输入事件也依赖 AMS Handler 这类通用任务队列，就可能被 Service、Broadcast、Provider 等其他系统任务拖慢。

所以 Android 引入 `InputManagerService`，并在 `system_server` 中用独立的 `InputReader` 线程和 `InputDispatcher` 线程处理输入事件。

#### 为什么用 Socket 而不是 Binder

Binder 线程池有上限。高频输入事件如果走 Binder，可能打满 App 的 Binder 线程池，影响 App 和系统之间其他 Binder 通信。

InputChannel 使用 socket pair：

```text
一端交给 system_server 里的 InputDispatcher；
一端交给 App 主线程，通过 epoll 监听。
```

Socket 更适合这种高频、低延迟、双向 ACK 的输入通信。

#### Input 完整流程

Input 事件从用户触摸到 App 消费完成，大致可以按这条链路理解：

```text
用户触摸
→ 内核事件
→ InputReader
→ mInboundQueue
→ InputDispatcher 取出事件
→ 找到焦点窗口对应的 Connection
→ 放入 outboundQueue
→ 通过 InputChannel socket 发送给 App 主线程
→ 移入 Connection.waitQueue，表示已发送、等待 App 确认
```

App 侧接收事件：

```text
App 主线程 Looper 原本就在 epoll_wait 中等待事件；
ViewRootImpl 创建 WindowInputEventReceiver 时，
会把 InputChannel 的 socket fd 注册进同一个 epoll。

InputDispatcher 往 socket 写入事件后，
App 主线程 epoll 被唤醒，
进入 InputEventReceiver.dispatchInputEvent。

之后走 ViewRootImpl InputStage 链，
最终到 View.dispatchTouchEvent。
```

App 消费完成后：

```text
App 调用 finishInputEvent；
通过 socket 写回 ACK；
InputDispatcher 收到 ACK 后，
把事件从 Connection.waitQueue 中移除。
```

#### Input ANR 检测

Input 没有传统炸弹消息。

`InputDispatcher` 每轮 `dispatchOnce` 都会检查焦点窗口 `Connection` 的 `waitQueue` 头部事件：

```text
elapsed = now - waitQueue.front().eventTime

如果 elapsed >= 5s，
就触发 onANRLocked。
```

这里的关键口径是：

```text
Input ANR 的计时起点是事件产生时刻 eventTime，
不是 App 收到事件的时刻。

也就是说，事件在系统侧排队、分发、等待 App ACK 的时间，
都可能被计入这 5s。
```

一句话压缩：

```text
Input ANR 是流式触发型：
InputDispatcher 在事件分发循环中持续检查 waitQueue 头部事件，
如果从 eventTime 到当前已经超过 5s 仍未收到 App ACK，
就触发 Input ANR。
```

## 第 4 章：traces 实战分析

```text
第 4 章：traces 实战分析
├─ 1. traces 是什么，能看什么，不能看什么
├─ 2. ANR 根因三分类：A / B / C
├─ 3. 六步诊断 SOP
├─ 4. 锁链追踪方法
├─ 5. 高频陷阱
└─ 6. 根因速查卡
```

### 1. traces 是什么，能看什么，不能看什么

`traces.txt` 不是卡顿全过程录像，而是 ANR 触发附近的一次线程快照。

它能帮助我们看到：

```text
ANR 现场这一刻，各个线程分别卡在哪里；
主线程当时是什么状态；
有没有锁竞争、死锁、Binder 等待、IO、计算、CPU 饥饿等证据。
```

但它不能直接保证回答：

```text
整个卡顿过程从什么时候开始；
每一步耗时多少；
根因一定就在当前主线程栈顶。
```

尤其是线上平台抓 trace 时，可能存在快照滞后：

```text
ANR 发生时主线程卡住；
但抓 trace 的时候卡顿已经结束；
于是你看到 main 线程在 MessageQueue.next() WAITING。
```

这种 trace 不能直接说明“主线程没问题”，也不能直接把 `MessageQueue WAITING` 当根因。它只能说明：当前这份快照没有抓到真正卡住的现场，需要结合 logcat、CPU、ANR reason、业务日志继续交叉验证。

一句话压缩：

```text
traces 是 ANR 现场附近的线程快照，不是卡顿过程录像；
诊断时要用它找证据，但不能把没有证据的猜测写成根因。
```

### 2. ANR 根因三分类：A / B / C

ANR 根因可以先分成三类。

A 类：主线程自己在忙。

```text
主线程在做 IO、网络、数据库、大计算、复杂布局等耗时操作。

典型表现：
main 线程 RUNNABLE；
栈顶或业务包名帧能看到耗时代码；
如果 App CPU 也高，更支持这个判断。
```

B 类：主线程被困住。

```text
主线程不是自己忙，而是在等别人。

常见原因：
锁竞争；
死锁；
wait / notify；
同步 Binder 调用卡住。

典型表现：
main 线程 BLOCKED；
或者 WAITING 在业务对象上；
或者卡在 BinderProxy.transact 这类同步 Binder 调用。
```

C 类：主线程想跑但抢不到 CPU。

```text
主线程处于 RUNNABLE，
但系统 CPU 被打满，
调度器不给它足够时间片。

典型表现：
main 线程 RUNNABLE；
堆栈本身不一定有明显业务耗时代码；
系统 CPU 很高。
```

几个易错点：

```text
WAITING 不是 C 类。
WAITING 表示线程主动放弃执行权，在等某个条件或对象。

C 类只有一种核心含义：
线程可运行，但调度器没有给它足够 CPU 时间片。

B 类通常 App CPU 低，
但“CPU 低”不能单独当作 B 类结论。
它只是启发式标记，最终还要靠堆栈证据确认。

MessageQueue.next() WAITING 是特殊陷阱。
它通常表示主线程当前空闲，不是根因本身。
```

一句话压缩：

```text
ANR 根因可以先分三类：
A 类是主线程自己忙；
B 类是主线程被锁、等待、Binder 等困住；
C 类是主线程可运行但抢不到 CPU。
最终结论必须由线程状态、堆栈和 CPU 快照共同支撑。
```

### 3. 六步诊断 SOP

收到 ANR trace 后，可以按六步走。

第一步：读元信息头。

```text
确认 ANR 类型：Input / Service / Broadcast / ContentProvider。
确认超时阈值：Input 5s，前台 Service 20s，前台 Broadcast 5s 等。
确认 Cmd line 是不是自己的进程。
```

第二步：读 CPU 快照。

```text
App CPU 高：
标记“可能 A 类”，主线程可能在做计算或 IO。

系统 CPU 高：
标记“可能 C 类”，主线程可能抢不到时间片。

iowait 高：
标记“可能 A 类 IO”。

App CPU 和系统 CPU 都低：
标记“可能 B 类”，主线程可能在等锁、等通知、等 Binder。

注意：
这里只是初步标记，不能直接下结论。
最终仍然要看堆栈证据。
```

第三步：找主线程，读线程状态。

```text
BLOCKED：
搜 waiting to lock <地址>；
再全文搜 locked <地址>；
找到持锁线程，看它是不是也在等锁。

WAITING：
如果是 waiting on MessageQueue，进入空闲态陷阱处理；
如果是 waiting on 业务对象，搜 waiting on <地址>，
找应该 notify 但被卡住的线程。

RUNNABLE：
如果栈顶是 IO / 网络 / 数据库，按 A 类 IO 查；
如果栈顶是业务计算代码，按 A 类计算查；
如果堆栈看起来正常，再结合 CPU 判断 C 类风险。
```

第四步：交叉验证其他线程。

```text
多个线程是否卡在同一方法？
可能是计算密集，或者 A 类和 C 类叠加。

持锁线程是否也在等锁？
如果互相等待，可能是死锁。

是否有 BinderProxy.transact？
可能是同步 Binder 调用超时，需要看 system_server 状态。

Finalizer / HeapTaskDaemon 是否 RUNNABLE？
RUNNABLE 才能作为 GC 压力证据；
WAITING 通常只是空闲。
```

第五步：处理特殊情况。

```text
main 线程 MessageQueue WAITING：
这是主线程当前空闲的正常状态，不是根因本身。

可能 1：
trace 快照时机问题。
ANR 卡顿过程已经结束，抓 trace 时主线程恰好空闲。
这份 trace 对根因帮助有限，需要结合 logcat。

可能 2：
C 类 CPU 饥饿。
主线程想执行但抢不到时间片，状态看起来像空闲。
需要 CPU 快照确认。

可能 3：
系统层问题。
InputDispatcher 或 system_server 侧异常，
需要看系统日志。
```

第六步：输出结论。

```text
ANR 类型；
根因分类：A / B / C；
根因描述；
根因代码位置；
证据链；
修复方向。
```

### 4. 锁链追踪方法

如果主线程是 `BLOCKED`，重点追锁链：

```text
main BLOCKED
→ 找 waiting to lock <0xXXXX>
→ 全文搜 locked <0xXXXX>
→ 找到持锁线程
→ 看持锁线程是否也在 waiting to lock
→ 判断是否死锁
```

典型死锁：

```text
线程 A 持有锁 X，等待锁 Y；
线程 B 持有锁 Y，等待锁 X；
双方互相等待，永远不释放。
```

修复方向：

```text
统一全局加锁顺序；
缩小锁粒度；
避免持锁期间做 IO、Binder、复杂计算等不可控操作。
```

如果主线程是 `WAITING` 在业务对象上：

```text
搜 waiting on <0xXXXX>；
找到它在等哪个对象；
再找应该 notify / notifyAll 的线程；
看通知线程为什么没有执行到通知逻辑。
```

### 5. 高频陷阱

陷阱一：`MessageQueue.next()` + `WAITING`。

```text
"main" WAITING at MessageQueue.next()
```

这通常表示主线程当前空闲，不是根因本身。

常见解释：

```text
1. trace 快照时机问题：
   ANR 卡顿过程已经结束，抓 trace 时主线程恰好空闲。

2. C 类 CPU 饥饿：
   主线程想跑，但抢不到 CPU 时间片。

3. 系统侧问题：
   InputDispatcher 或 system_server 异常，
   App 侧 trace 不一定能直接看出根因。
```

陷阱二：`Finalizer` / `HeapTaskDaemon` 是 `WAITING`。

```text
WAITING 通常表示 GC 相关线程空闲，
不是 GC 压力证据。

只有 Finalizer / HeapTaskDaemon RUNNABLE，
才更值得怀疑 GC 压力。
```

陷阱三：看到 CPU 低就直接说 C 类。

```text
这是反的。

C 类是主线程 RUNNABLE 但抢不到 CPU，
通常需要系统 CPU 高来支撑。

App CPU 低更常见于 B 类，
但也不能只靠 CPU 低下结论。
```

### 6. 根因速查卡

```text
RUNNABLE + 栈顶 IO / 网络 / 数据库
→ A 类 IO
→ 修复：移出主线程，异步化，减少同步等待。

RUNNABLE + App CPU 高 + 业务计算
→ A 类计算
→ 修复：移出主线程，拆分任务，限制复杂度。

BLOCKED + waiting to lock
→ B 类锁竞争
→ 修复：追持锁线程，统一加锁顺序，缩小锁粒度。

BLOCKED + 两个线程互相等锁
→ B 类死锁
→ 修复：统一加锁顺序，避免循环等待。

WAITING + 业务对象 + 工作线程被卡
→ B 类等通知
→ 修复：排查 notify 链路和状态机。

BLOCKED / RUNNABLE + BinderProxy.transact
→ B 类同步 Binder 等待
→ 修复：减少主线程同步 Binder 调用，检查 system_server 或远端服务。

RUNNABLE + 堆栈正常 + 系统 CPU 爆满
→ C 类 CPU 饥饿
→ 修复：限并发，降低后台线程压力，优化系统负载。

WAITING + MessageQueue + CPU 正常
→ 当前 trace 可能无效
→ 修复：结合 logcat、业务日志、ANR reason 继续查。

多线程同跑同一计算方法
→ A 类和 C 类可能叠加
→ 修复：主线程移出计算，同时限制子线程并发数。
```

## 第 5 章：线上 ANR 监控方案

```text
第 5 章：线上 ANR 监控方案
├─ 1. 线上 ANR 监控的分类框架
├─ 2. ANR 后系统做了什么
├─ 3. 信号机制前置知识
├─ 4. Bugly：旁观者模式
├─ 5. xCrash：链式拦截模式
├─ 6. Matrix：委托线程模式
└─ 7. 三方案对比与核心结论
```

### 1. 线上 ANR 监控的分类框架

线上 ANR 监控方案可以按“是否主动参与 ANR 信号流程”分成两类。

第一类：旁观者。

```text
代表：Bugly

特点：
不介入 SIGQUIT 信号流程；
等系统完成 ANR 处理后，
再观察系统产物或结合自身 Watchdog 结果上报。
```

第二类：深度介入者。

```text
代表：xCrash / Matrix

特点：
在 native 层注册 sigaction handler；
主动拦截 SIGQUIT；
在系统处理 ANR 的同时，自己 dump 线程栈。
```

一句话压缩：

```text
Bugly 是旁观者，不抢 SIGQUIT；
xCrash / Matrix 是深度介入者，会注册 sigaction handler 拦截 SIGQUIT。
```

### 2. ANR 后系统做了什么

系统判定 ANR 后，大致流程是：

```text
AMS 判定目标进程发生 ANR
→ 给目标 App 进程发送 SIGQUIT，也就是信号 3
→ App 进程中的 ART SignalCatcher 线程通过 sigwait 等待并接收 SIGQUIT
→ SignalCatcher dump 本进程所有线程栈
→ 写入 /data/anr/traces.txt
→ AMS 继续收集 CPU / DropBox 等现场
→ 前台进程弹 ANR 对话框，后台进程可能直接杀掉
```

这里要注意：

```text
ART 指 Android Runtime 本身；
不是某个叫 ART 的线程。

真正接收 SIGQUIT 并 dump 线程栈的是 App 进程里的 SignalCatcher 线程。
```

### 3. 信号机制前置知识

理解 xCrash 和 Matrix 前，要先区分 `sigaction` 和 `sigwait`。

`sigaction` 模式：

```text
内核主动打断线程，
跳转执行注册好的 handler 函数。

它是被动接收：
信号来了，内核推送给 handler。
```

`sigwait` 模式：

```text
线程主动阻塞等待某个信号，
信号来了以后，线程自己取走并处理。

ART SignalCatcher 就是这种模式。
```

核心冲突：

```text
同一个信号只能被消费一次。

如果 sigaction handler 先消费了 SIGQUIT，
SignalCatcher 的 sigwait 就等不到这个信号。

POSIX 明确不建议同一进程对同一信号混用 sigaction 和 sigwait，
否则属于 undefined behavior。
```

所以深度介入型方案的关键问题是：

```text
既要自己感知 SIGQUIT 并 dump；
又要保证 ART SignalCatcher 最终还能收到 SIGQUIT，
让系统原本的 ANR 流程继续走完。
```

### 4. Bugly：旁观者模式

Bugly 的本质是旁观者模式：不介入 SIGQUIT，主要靠 Watchdog 主线程探活，再结合系统 ANR 广播做定性确认。

Watchdog 核心流程：

```text
Watchdog 线程循环执行：

1. 把标记位置为 false。
2. post 一个普通消息到主线程 MessageQueue。
   这个消息执行时会把标记位置为 true。
3. Watchdog 自己 sleep 5s。
4. 醒来后检查标记位。
5. 如果仍然是 false，说明主线程 MessageQueue 没有及时处理这个消息。
6. 调 Thread.getAllStackTraces() 抓所有线程 Java 栈并暂存。
```

系统 ANR 广播：

```text
系统真正判定 ANR 后，会发 ACTION_ANR_OCCURRED 广播。
Bugly 收到广播后，把它作为“确实发生系统 ANR”的定性确认，
再结合 Watchdog 暂存的堆栈上报。
```

`FileObserver` 监听 `/data/anr/`：

```text
Android 11+ 后 SELinux 收紧，
普通 App 基本无法读取 /data/anr/ 目录内容。

所以 FileObserver 监听 traces 文件的方案已经基本失效，
最多只能算兜底备选。
```

Bugly Watchdog 的缺陷：

```text
1. 可能误报：
   主线程执行合法长任务，但还没达到系统 ANR 阈值，
   Watchdog 也可能先认为主线程卡住。

2. 可能漏报 Input ANR：
   InputDispatcher 超时不一定经过 MessageQueue。
   主线程可能还能正常处理 Watchdog post 的消息，
   但触摸事件 5s 没有返回 ACK，
   系统仍然会判 Input ANR。

3. 采样精度低：
   Watchdog 通常按 5s 周期探活，
   抓到的栈不一定是系统 ANR 爆发的精确瞬间。

4. 只有 Java 栈：
   Thread.getAllStackTraces() 看不到 Native 层堆栈。
```

一句话压缩：

```text
Bugly 不介入系统 SIGQUIT 流程，
核心靠 Watchdog 探测主线程 MessageQueue 是否卡住，
再用 ANR 广播做定性确认；
优点是安全，缺点是可能误报、漏报 Input ANR，且堆栈不够精确。
```

### 5. xCrash：链式拦截模式

xCrash 属于深度介入模式。它通过 `sigaction` 注册比较重的 SIGQUIT handler，SIGQUIT 到来时先由自己处理。

大致流程：

```text
SIGQUIT 到来
→ xc_trace_handler 拦截
→ handler 内完整 dump 所有线程栈
→ 注销自身 handler
→ raise(SIGQUIT) 补发信号
→ 期望 ART SignalCatcher 的 sigwait 能继续收到 SIGQUIT
```

核心问题是时序竞态：

```text
注销 handler 和 raise(SIGQUIT) 之间存在时间窗口。

如果 handler 还没有完全卸载，
补发的 SIGQUIT 可能又被 xCrash 自己消费。

这样 ART SignalCatcher 就收不到 SIGQUIT，
系统原本的 ANR dump 流程可能被破坏。
```

所以 xCrash 的补发更接近 best-effort，不是可靠保证。

另一个问题是信号上下文限制：

```text
sigaction handler 运行在信号上下文，
只能调用 async-signal-safe 的函数。

如果在 handler 里做 malloc、mutex、fprintf、复杂 IO、Java 调用等重操作，
都可能违反 async-signal-safe 约束，
属于 undefined behavior 风险。
```

一句话压缩：

```text
xCrash 在 SIGQUIT handler 里做完整 dump，
再卸载 handler 并补发 SIGQUIT；
问题是信号上下文不适合做重活，
而且卸载和补发存在竞态，SignalCatcher 不一定能稳定收到补发信号。
```

### 6. Matrix：委托线程模式

Matrix 也是深度介入模式，但它把 handler 做得极轻，只负责感知信号，不在信号上下文里做重活。

核心流程：

```text
SIGQUIT 到来
→ sigaction handler 被触发
→ handler 只做一件事：write(pipe_fd, "1", 1)
→ handler 立即返回
→ dump 线程阻塞在 read(pipe_fd)，被唤醒
→ dump 线程在普通线程上下文中完整 dump 所有线程栈
→ dump 线程注销自身 sigaction handler
→ kill(getpid(), SIGQUIT) 补发信号
→ ART SignalCatcher 的 sigwait 稳定收到 SIGQUIT
```

为什么 Matrix 更稳定：

```text
xCrash：
卸载 handler 和补发 SIGQUIT 都发生在信号上下文里，
时序不可控，存在竞态。

Matrix：
handler 只负责 write pipe；
dump、卸载 handler、补发 SIGQUIT 都在普通线程中执行，
顺序完全可控。

补发 SIGQUIT 时 handler 已经卸载，
所以 SignalCatcher 可以稳定收到这个信号。
```

Matrix 的本质贡献：

```text
把“感知信号”和“处理信号”彻底解耦。

handler 只负责感知：
write pipe。

普通线程负责处理：
dump 线程栈；
卸载 handler；
补发 SIGQUIT。

这样就把不可控的信号上下文，
转换成可控的普通线程上下文。
```

一句话压缩：

```text
Matrix 的关键不是也拦截 SIGQUIT，
而是 handler 极轻，只写 pipe；
真正的 dump、卸载和补发都交给普通线程完成，
因此既能自己抓栈，又能更可靠地把 SIGQUIT 交还给 SignalCatcher。
```

### 7. 三方案对比与核心结论

三种方案可以这样对比：

```text
| 方案   | 介入层面       | handler 行为 | 转发可靠性       | 主要问题                       |
|--------|----------------|--------------|------------------|--------------------------------|
| Bugly  | 不介入 SIGQUIT | 无           | 无需转发         | 可能误报 / 漏报，堆栈不够精确 |
| xCrash | sigaction 重量 | 完整 dump    | 有竞态，不可靠   | 信号上下文做重活，存在 UB 风险 |
| Matrix | sigaction 极轻 | 写 1 字节    | 时序可控，更可靠 | 实现复杂度更高                 |
```

最终核心结论：

```text
SignalCatcher 能不能收到补发的 SIGQUIT，
只取决于补发信号时 sigaction handler 是否已经完全卸载。

handler 还在：
补发信号可能再次被自己的 handler 消费，
SignalCatcher 收不到。

handler 已卸载：
SIGQUIT 可以被 SignalCatcher 的 sigwait 收到，
系统原本的 ANR 流程继续执行。
```

对三类方案的最终判断：

```text
Bugly：
最安全，因为不介入 SIGQUIT；
但只能旁观，精度和覆盖面有限。

xCrash：
能更早、更主动地抓栈；
但在信号上下文里做重活，且补发 SIGQUIT 存在竞态。

Matrix：
同样主动介入 SIGQUIT；
但通过 pipe 把重活转移到普通线程，
让卸载和补发时序可控，
因此是更稳定的深度介入方案。
```
