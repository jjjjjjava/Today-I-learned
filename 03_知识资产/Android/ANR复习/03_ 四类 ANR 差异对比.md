# 第 3 篇 · 四类 ANR 差异对比：两大类，与两个"非典型"

> 前置知识：第 2 篇的 Service 埋雷-拆雷-爆雷链路与 executingStart 判据
> 难度：进阶
> 预计阅读时间：14 分钟

---

## 上一篇思考题复盘

> 📝 你选择直接继续，未提交作答。下面给出三题的正确答案，请对照自检——尤其第 3 题，它是模块二的收口。

**第 1 题：同进程 ServiceA、ServiceB 都在跑，`mExecutingServices` 几个元素？发几颗雷？**
> 集合里 **2 个**元素（两个 ServiceRecord）；但只发了 **1 颗**雷。因为雷只在集合「**从空 → 非空**」时发：ServiceA 进来时空→非空，发了 1 颗；ServiceB 进来时集合已非空，复用、不再发。**一颗进程级雷监控整条主线程**。

**第 2 题：`serviceTimeout` 触发但没人真超时，怎么办？雷是什么角色？**
> 不报 ANR。根据还在执行的 Service 的到期时间，**重新 post 下一次 `serviceTimeout`** 继续轮询。这说明雷只是**轮询触发器**，不是判决书——真正判据是各 `ServiceRecord.executingStart`。

**第 3 题（收口题）：ServiceA 的 onCreate 卡 25s，第 22s 时同进程 ServiceB 正常完成触发 `serviceDoneExecuting`，会不会顺手把 ServiceA 该爆的雷拆掉、导致漏报？**
> **不会。** 拆雷两层逻辑：
> - 第一层：ServiceB 的 `executeNesting--` 归 0，只把 **ServiceB 自己**移出 `mExecutingServices`；
> - 第二层：检查集合是否为空——但 **ServiceA 还占着集合**，集合非空，所以**不会撤掉进程的超时消息**。
>
> 雷依旧在。到点 `serviceTimeout` 遍历时，ServiceA 的 `executingStart`（25s 前）< `maxTime`（now − 20s），照样判它 ANR。
> 🔑 题眼：**撤不撤雷看"集合空不空"，而 ServiceA 占着集合，所以 ServiceB 的完成救不了 ServiceA。** 这正是"进程级一颗雷 + 逐个核对 executingStart"设计的精妙：拆雷不会误伤别的 Service。

---

## ??? 解答

> 💬 上一篇无 `???` 标注，直接进入新内容。

---

## 正文内容

上面我们把 Service 这条线吃透了，但它其实只是**一个大类的代表**。这一篇横向把四类 ANR 摆在一起对比：先归两大类，再排耗时，最后讲清两个"非典型"——ContentProvider 和 Input。

### 一、两个大类

针对 Service、ContentProvider、Broadcast、Input 这四类，按**检测方式**可以归成两个大类：

```text
时间触发型（被动等时间到）
   典型就是 Service：系统先埋入一个超时消息，被动地等时间到来，
   再把消息取出、检测有没有真超时、决定爆不爆——是"等闹钟响"的被动模型。
   Service / Broadcast / ContentProvider 都属于这一类。

主动触发式（流式循环里主动查）
   典型是 Input：不埋炸弹，而是在每一轮事件分发循环里【主动】检测有没有超时。
   只有 Input 属于这一类。
```

一句话定调：**Service/Broadcast/Provider 是同一个"埋雷"模型的三个实例；Input 是另一套主动检测的世界观。**

### 二、四类 ANR 的耗时

先把四类的超时阈值排清楚：

```text
Service          前台 20s   后台 200s
Broadcast        前台 5s    后台 60s
ContentProvider  只有前台 10s（没有后台一说）
Input            只有前台 5s
```

> 速记：**用户能直接感知的（Input/Broadcast 前台）给得最严，都是 5s；Service 是后台任务，宽到 20s；Provider 是启动期一次性的，10s；切到后台再 ×N 倍放宽（Service 200s、Broadcast 60s）。**


### 三、差异其一：ContentProvider

注意到 ContentProvider 只有前台 10s——它很特殊：**是在应用进程"启动过程中"就埋下的雷。**

**埋雷时机：进程 attach 阶段。**

```text
进程启动走到 attachApplication，把 ApplicationThread 传给系统、
建立"系统 ↔ 进程"双向 Binder 通信链路的那一刻
（AMS.attachApplicationLocked），就埋下了这颗 Provider 超时雷。
```

**一个很反直觉的执行顺序**（也是面试爱挖的点）：

```text
进程初始化时，并不是"先把 MyApplication 反射创建 + 调 onCreate"，
而是 —— 修正版精确顺序 ——
  1. 先 new Application 实例 + attachBaseContext（Application 对象此时已存在）
  2. 再反射创建 ContentProvider 并执行 ContentProvider.onCreate
  3. 最后才执行 Application.onCreate
```

也就是说 **`ContentProvider.onCreate` 比 `Application.onCreate` 更早执行**（但并不比 Application 对象本身的创建早）。这正是 LeakCanary、Firebase 等库用一个"空 Provider"实现**免初始化自动注册**的原理。Provider 初始化完、发布后，通过 `AMS.publishContentProviders` 回调系统拆雷。

**爆雷处理：直接杀进程，不弹框。**

```text
超时 → processContentProviderPublishTimedOutLocked → removeProcessLocked
结果：不弹 ANR 框、不走 appNotResponding、直接移除进程。
```

为什么这么狠？

> 因为 ContentProvider 是 App 启动后**必须具备的能力**，它发布超时基本等于**这个进程根本没正常启动起来**——可以视作"启动失败"。对一个连初始化都没走完的进程，继续等、或弹个"等待/关闭"框让用户选都没意义，直接杀掉重来更合理。"给用户选择"的礼遇，是留给"已经在正常运行、只是这次卡了"的进程（前台 Service / Input）的。

> 一句话压缩：**ContentProvider 是时间触发型里的异类——埋雷在进程 attach 阶段，onCreate 抢在 Application.onCreate 前跑，超时直接 removeProcessLocked 杀进程，不弹框也不走 appNotResponding。**

### 四、非典型之二：Input 为何是"独立王国"

Input 机制最特殊，平铺着讲很容易糊成一团。我们分**四层**看，每层只回答一个问题：

```text
第 1 层：谁在哪一侧？      —— 先把空间边界画清楚
第 2 层：为什么这么搭？    —— 两个设计决策
第 3 层：事件住在哪？      —— 三个队列
第 4 层：一颗事件的一生？  —— 埋-拆-爆流水线（每步标侧别）
```

#### 第 1 层 · 三个角色：先认清空间边界

整条链跨**三个空间**，看流程时心里始终要清楚"现在站在哪一侧"：

```text
【内核】              产生原始事件，写到 /dev/input/eventX
【system_server / IMS】
   InputReader 线程      读内核原始事件 → 加工成标准 InputEvent
   InputDispatcher 线程  分发事件 + 检测超时（Input ANR 就在这判）
【App 进程·主线程】
   epoll 唤醒 → InputEventReceiver → ViewRootImpl → View.dispatchTouchEvent
```

> ⚠️ 名字别串：**系统侧是 Reader / Dispatcher，App 侧是 Receiver。** `InputDispatcher` 永远在 system_server，不会"跨进程"跑进 App；App 侧负责接收的是 `InputEventReceiver`。

#### 第 2 层 · 两个设计决策：为什么不复用现成机制

**① 为什么用独立线程（不挤 AMS 的 Handler 队列）？**
输入**高频 + 对延迟极敏感**。若挤进 AMS 那条通用 Handler 队列，会被 Service/Broadcast/Provider 等任务拖慢。所以单独起 `InputManagerService`，用**独立的 InputReader / InputDispatcher 线程**专职处理。

**② 为什么用 Socket（不走 Binder）？**
Binder 线程池**有上限**。高频输入若走 Binder，会打满 App 的 Binder 线程池，连累其它跨进程通信。所以 InputChannel 用 **socket pair**：一端给系统侧 InputDispatcher，一端给 App 主线程、注册进主线程 Looper 的 **同一个 epoll**（主线程本就 epoll_wait 等消息，把 input 的 socket fd 也塞进去）。socket 天然适合这种**高频、低延迟、双向 ACK**的通信。

#### 第 3 层 · 三个队列：事件的三段栖身处

事件不是一步到 App，它在系统侧先后住三个队列——记住它们，第 4 层就不会乱：

```text
mInboundQueue  全局入站      InputReader 投进来、Dispatcher 等待分发     （还没分给具体窗口）
outboundQueue  每窗口·待发送  已分给某焦点窗口、还没写进 socket           （准备发）
waitQueue      每窗口·已发待ACK 已写给 App、正等它回 ACK                 ← 爆雷只盯它的头部！
```

#### 第 4 层 · 一颗事件的一生：埋-拆-爆流水线

复用 Service 那套「埋-拆-爆」做主线，**每一步标清在哪一侧**：

```text
【埋雷 · 全程系统侧】
  内核
   →【系统侧·InputReader】读取 + 加工 → 投入 mInboundQueue
   →【系统侧·InputDispatcher】每轮 dispatchOnce 从 mInboundQueue 取队头
                              → 找焦点窗口的 Connection → 放入 outboundQueue
                              → 通过 socket 写给 App → 挪进 waitQueue（开始等 ACK）

【拆雷 · App 侧消费 → 系统侧销账】
  【App 侧·主线程】epoll 被唤醒 → InputEventReceiver.dispatchInputEvent
                  → ViewRootImpl 的 InputStage 链 → View.dispatchTouchEvent
                  → 消费完 finishInputEvent → 经 socket 回 ACK
  【系统侧·InputDispatcher】收到 ACK → 把该事件从 waitQueue 移除（这一帧拆雷成功）

【爆雷 · 系统侧】
  【系统侧·InputDispatcher】每轮 dispatchOnce 顺手查 waitQueue 头部：
        elapsed = now - waitQueue.front().eventTime
        若 elapsed >= 5s → onANRLocked → appNotResponding
```

为什么盯 **waitQueue 头部**？头部是**最早发出、却最久没被 ACK** 的那个——要么 App 主线程一直没空处理，要么处理完没回 ACK。它超时，就代表 App 对输入"无响应"。

#### 关键口径：计时从 eventTime 起算

> **Input ANR 的计时起点是「事件产生时刻 eventTime」，不是「App 收到事件的时刻」。** 上面三个队列里的排队、发送、等 ACK 时间——**全从 eventTime 起算、全计入这 5s**。所以哪怕 App 主线程处理只花 1s，只要"系统侧排队 + 传输 + 你处理 + ACK"加起来超 5s，照样 ANR。这也是排查线上 Input ANR 时不能只盯 App 自己耗时的原因。

> 一句话压缩：**Input 是流式触发型——事件在系统侧经 mInboundQueue → outboundQueue → waitQueue 三段流转，InputDispatcher 在 dispatchOnce 循环里持续盯 waitQueue 头部，从 eventTime 起算超 5s 仍无 App ACK，就触发 Input ANR。**

### 五、一句话串起全篇

```text
四小类 = 两大类 + 两非典型：
  时间触发型(埋雷模型)：Service / Broadcast 标准款，ContentProvider 异类(attach埋雷、杀进程不弹框)；
  流式触发型(循环主动查)：Input 独立王国(独立线程、socket 通信、eventTime 起点、dispatchOnce 检测)。
```

---

## 思考题

1. 同样是"前台 5s"，Broadcast 的 5s 和 Input 的 5s，计时方式有什么本质区别？（提示：一个是埋雷模型，一个从 eventTime 起算）
2. 为什么 ContentProvider 超时是「直接杀进程」，而前台 Service 超时是「弹框让用户选」？从"进程当前处于什么阶段"这个角度回答。
3. 一个 App 主线程响应触摸事件其实只花了 1s，但用户还是看到了 Input ANR。结合"eventTime 起点"，推测中间可能发生了什么？这对你排查线上 Input ANR 有什么启发？

## 你的反馈

> 在这里写下你的问题、感悟、不理解的地方，或希望下一篇深入的方向。
> 文中任意位置可用 `???你的困惑` 就地标注，我下一篇优先解答。
> 读完回我「继续」或写下思考题答案，我据此生成下一篇（进入模块三：traces 实战诊断）。
