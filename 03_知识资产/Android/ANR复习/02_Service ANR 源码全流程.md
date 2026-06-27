# 第 2 篇 · Service ANR 全流程：一颗雷的一生

> 前置知识：第 1 篇的「埋雷-拆雷-爆雷」模型；知道 Binder 跨进程调用、ActivityThread/Handler(mH) 基本概念
> 难度：进阶
> 预计阅读时间：14 分钟
> 本篇按「前言 → 代码起点 → 埋雷 → 拆雷 → 爆雷」五段组织，是你亲手重构的源码笔记。

---

## 上一篇思考题复盘

> 📝 评估你对第 1 篇思考题的回答，并给出正确答案。

### 你的回答评估

1. ✅ **正确**：你抓住了「在执行 ≠ 在响应」。
2. ✅ **正确**：拆雷由 App 发起、经 Binder 告诉系统；通道堵则必然爆雷。
3. ⚠️ **部分正确**：「子线程也可能不安全/死锁」对，但漏了「探测不到 Input ANR」这个更致命的点。

### 正确答案

**第 1 题：CPU 高为何还判 ANR？**
> 系统判的是「有时限的关键任务是否在阈值内完成回应」，跟 CPU 闲不闲、代码在不在跑无关。主线程埋头解析大 JSON 时，它没法及时处理后续的 input 事件、也没法回调"任务完成"——任务到点没回应，就 ANR。一句话：**在执行 ≠ 在响应。**

**第 2 题：拆雷由谁、经什么、告诉谁？通道堵了会怎样？**
> 由 **App 主线程**在执行完组件回调之后发起，经 **Binder** 回调到 **system_server（AMS/ActiveServices）**。如果主线程被堵、或这个 Binder 回调发不出去，拆雷动作就到不了系统 → 雷到点仍在 → 爆雷。

**第 3 题：App 自起子线程当看门狗，差在哪？**
> ① 裁判不能是选手本人：进程被冻结、降优先级、被系统 kill 时，子线程 watchdog 同样失效；② **探测不到 Input ANR**——Input 超时判定在系统侧的 InputDispatcher，不经过 App 的 MessageQueue，主线程甚至能正常处理 watchdog 消息（看着"活着"），但触摸事件 5s 没回 ACK 照样被判 ANR；③ 精度和可靠性都不如系统裁判。

---

## ??? 解答

> 💬 上一篇中没有 `???` 标注，直接进入新内容。

---

## 正文内容

### 一、前言：把模型映射到三个方法

前面我们讲了 ANR 的由来、原理（埋雷-拆雷-爆雷），以及四类 ANR。现在我们拿着这个模型，去 Service 的真实源码里把它坐实。三个方法名先记死，它们就是模型的三个落点：

```text
埋雷  → bumpServiceExecutingLocked
拆雷  → serviceDoneExecuting
爆雷  → serviceTimeout
```

接下来我们顺着系统源码流程，把 Android 里 Service ANR 的实现原理走一遍。

### 二、代码起点：从 startService 到 ActiveServices

这颗雷的埋入要追溯到用户代码里。当你调用 `startService`，它**不会**当场反射创建 Service、执行 `onCreate`——而是先把请求交给系统，由系统统一调度。具体路径：

```text
startService
  → ActivityManager.getService().startService(...)
     （getService 是个 Binder 入口：经 ServiceManager 拿到 AMS 的 proxy 对象）
  → 通过 Binder 跨进程，进入 system_server（由它的一个 Binder 线程跑进 AMS.startService）
  → AMS 只是中转，转交 ActiveServices.startServiceLocked
```

> 一个值得想的问题：**为什么用户调 startService 时不立刻反射创建并执行？** 因为不只是 Service，Activity 等四大组件都一样——它们的生命周期都必须**经手系统统一管理**（前后台、进程优先级、调度时机都由系统决定）。所以都得先通过 Binder 把请求交给 AMS，再由系统回头调度 App 执行。

这一段抓三个关键词：`getService().startService`、Binder 跨进程、`AMS → ActiveServices`。

### 三、埋雷流程：bumpServiceExecutingLocked

`startServiceLocked` 会走到 `bumpServiceExecutingLocked`，这就是埋雷。它干三件事：

```text
1. 在这个 Service 的 ServiceRecord 上记录 executingStart（开始执行时间）
   ← 后面爆雷时，就靠它判断这个 Service 是否真的超时
2. 把 ServiceRecord 加入它所属进程的 mExecutingServices 集合
   ← 表示"这个进程当前有 Service 回调在执行，得盯着"
3. 视情况发送一个 Service 类型的超时延时消息，到 AMS 的消息队列（这才是真正"埋雷"）
```

第 3 步**是有条件的**，不是每个 Service 都无脑发一颗：

```text
只有 mExecutingServices 从【空 → 非空】时，才 scheduleServiceTimeoutLocked 发雷。
也就是说：对于一个进程，AMS 的消息队列里同一时刻只会有【一颗】Service 类型的雷。
```

> 为什么这么设计？如果每个 Service 都发一颗雷，消息队列会膨胀、雷的数量爆炸。而本质上一个进程的所有 Service 回调都排在**同一条主线程**上跑——主线程卡了就全堵。所以**一颗进程级的雷就足够监控整条主线程**。这是个很精巧的省法，下一节拆雷你会看到它是怎么用一颗雷管住整个进程所有 Service 的。

### 四、拆雷流程：scheduleCreateService → 主线程执行 → serviceDoneExecuting

埋雷之后，系统回调 App 进程 `ApplicationThread` 这个 proxy 的 `scheduleCreateService`，经 Binder 走到 App 的 **Binder 线程池**。注意 Binder 线程**不直接执行** `onCreate`，它只是把请求封装成 `CREATE_SERVICE` 消息，发到主线程的消息队列：

```text
ActiveServices
  → ApplicationThread.scheduleCreateService（Binder）
  → App Binder 线程池接收
  → 封装 CREATE_SERVICE 消息 → 发到主线程 MessageQueue
  → 主线程 Looper 取出，分发给 ActivityThread 的 mH（绑定主线程的 Handler）
  → handleCreateService → 反射创建 Service 实例 → 执行 Service.onCreate
  → 完成后，经 Binder 调 AMS.serviceDoneExecuting —— 开始拆雷
```

到这里我们就看清了**怎么用一颗雷管住整个进程所有 Service**。拆雷走 `serviceDoneExecuting`，分两层：

```text
第一层（单个 Service）：
   在 mExecutingServices 里找到对应 ServiceRecord，executeNesting--
   若 executeNesting == 0 → 这个 Service 没有未完成回调了 → 把它从 mExecutingServices 移除

第二层（整个进程）：
   检查 mExecutingServices 是否为空
   若已空 → 这个进程没有任何在执行的 Service 回调了
          → removeMessages 撤掉这个进程的 Service 超时消息（真正拆雷，遍历 MsgQueue 把那颗雷移走）
```

这里务必掰清两个**最容易混的计数**：

```text
mExecutingServices ── 进程维度的集合：这个进程有哪些 ServiceRecord 在执行回调。
                      作用：决定进程级的雷【发不发 / 拆不拆】（看它空↔非空的边界）。

executeNesting     ── 单个 ServiceRecord 内部的嵌套层数：这一个 Service 还有几层回调没收尾。
                      作用：决定【这个 Service 自己完没完】。
                      ⚠️ 它不是雷的数量！onCreate 没收尾又来 onStartCommand → nesting=2，
                         但雷始终只有进程级那一颗。
```

> 一句话：**executeNesting 决定"单个 Service 完没完"，mExecutingServices 空不空决定"进程的雷能不能拆"。** 两层都满足，雷才真正撤掉。

### 五、爆雷流程：serviceTimeout

如果时间到了，App 仍没调 `serviceDoneExecuting` 拆雷，AMS 的 Looper 就会从消息队列取出这颗雷，进入 `serviceTimeout`。但**它不会立刻等于 ANR**，先排除两种非法情况：

```text
1. 进程不存在（已被杀）  → return：进程都没了，爆雷无意义。
2. mExecutingServices 为空 → return：没有在执行的 Service，雷只是没清干净的残留。
```

如果集合非空，就**遍历**它，找出**执行最久、即 executingStart 最早**的那个，核对是否真超时：

```text
maxTime = now - 超时阈值        # 前台 Service 20s，后台 200s
若 某 ServiceRecord.executingStart < maxTime：
    说明它从开始执行到现在已超过阈值 → 这才是真超时 → 报 ANR
（注意方向：executingStart 越早 = 跑得越久 = 越该爆；不是"最近的"那个）
```

- **找到真超时的** → 进入 `appNotResponding`：
  ```text
  1. 先收集现场：向【应用进程】发 SIGQUIT，dump 各线程堆栈写入 trace；
     也向【system_server 等系统进程】发 SIGQUIT —— 为了判断是不是系统侧拖住了 App
     （比如 Binder 响应不及时）。再收集 CPU / DropBox 等。
  2. 再处理：前台进程由 system_server 的 UiThread post 一个弹框消息
     （就是用户看到的"应用无响应，等待 / 关闭"框）；后台进程可能直接被杀。
  3. 还会发出 ANR 相关广播。
  ```
- **集合非空但没人真超时**（雷"醒早了"）：根据还在跑的 Service 的到期时间，**重新 post 下一次 serviceTimeout** 继续轮询。

> 🔑 本篇金句：**雷只是一个轮询触发器，不是判决书；真正的 ANR 判据是 `ServiceRecord.executingStart`。** 进程级只有一颗雷，雷发出的时刻和某个 Service 的真实超时点不一定对齐（中途可能有 Service 完成、又有新的开始），所以"到点"只触发"检查"，报不报得逐个核对每个 Service 各自的起跑时间。

> 📌 顺带埋个钩子：这里的 SIGQUIT 和广播，正是线上 ANR 监控三方案的基础——**Matrix / xCrash 基于 SIGQUIT 信号、Bugly 基于广播 + Watchdog**。这部分留到模块五展开。

### 六、把整条链串起来（背诵骨架）

```text
App: ActivityManager.getService().startService
  → AMS.startService → ActiveServices.startServiceLocked
  → bumpServiceExecutingLocked 埋雷（记 executingStart / 进 mExecutingServices / 空→非空才发雷）
  → ApplicationThread.scheduleCreateService（Binder）
  → App Binder 线程 → CREATE_SERVICE → ActivityThread.mH
  → 主线程 handleCreateService → Service.onCreate/onStartCommand
  → serviceDoneExecuting 拆雷（executeNesting-- → 归0移出集合 → 集合空则 removeMessages 撤雷）
  → 若超时消息触发时仍有 ServiceRecord.executingStart 超阈值（20s/200s）
  → appNotResponding → 先收集现场(SIGQUIT/trace) → 弹框 / 杀进程
```

---

## 思考题

1. 同一个进程里先后启动了 ServiceA 和 ServiceB，回调都在跑。此时系统的 `mExecutingServices` 里有几个元素？发了**几颗**超时雷？为什么？
2. `serviceTimeout` 触发时，发现 `mExecutingServices` 非空，但遍历后没有任何 Service 的 `executingStart` 超过阈值。系统会怎么做？这种情况说明了"雷"扮演的是什么角色？
3. 假设 ServiceA 的 `onCreate` 卡了 25s（前台阈值 20s），但就在第 22s 时，恰好同进程的 ServiceB 正常执行完触发了一次 `serviceDoneExecuting`。ServiceB 的拆雷动作，会不会"顺手"把 ServiceA 该爆的雷给拆掉、导致漏报？用第四、五节的两层逻辑解释。

## 你的反馈

> 你提交了一遍完整复述（埋雷-拆雷-爆雷三段映射 + 起点/埋雷/拆雷/爆雷全流程），整体掌握度高，最难的几个点都咬住了。本篇正文已按你的五段思路重排，并把以下纠正点焊进对应小节：
>
> 1. **超时阈值**：Service 前台 **20s**、后台 **200s**。（你当时不确定，错记成了 5s/10s/120s；5s 是 Broadcast 前台/Input、10s 是 ContentProvider。）
> 2. **executeNesting ≠ 多次埋雷**：雷始终是进程级那一颗。executeNesting 只是单个 ServiceRecord 内部回调的嵌套层数（onCreate 未收尾又来 onStartCommand → nesting=2），管"这个 Service 完没完"，与雷的数量无关。
> 3. **爆雷找"最早"不是"最近"**：真正会爆的是 executingStart 最早、执行最久的那个（elapsed 最大）。
> 4. 小口误：起点是 `startService`（非 startActivity）；system_server 里是 Binder 线程跑进 AMS（无专门"AM 线程"）；appNotResponding 里先收集现场（SIGQUIT/dump）再弹框。
>
> 已答疑：你问的「市面上三种 ANR 线上监控原理（Matrix/xCrash 基于 SIGQUIT，Bugly 基于广播+Watchdog）」——这是大纲模块五的内容，会在后续篇章专门展开。
>
> 后续若有新疑问，继续写在这里，或用 `???你的困惑` 就地标注。
