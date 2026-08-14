# 02｜系统为什么判定这次 ANR？

> 掌握状态：`0/4`。这里只学习单点归因需要的最小原理。

## 本篇只解决一个问题

代表 issue 已经选出。系统当时在等待什么，为什么会判定超时？

## 主线程还在运行，为什么也会 ANR？

某条 Service ANR 中，主线程正在解析大型 JSON，状态是 `RUNNABLE`，CPU 也有占用。代码没有死锁，但 Service 回调迟迟没有完成，系统仍然会判定 ANR。

系统判断的不是 CPU 高低，也不是线程有没有运行，而是一项有时限的关键职责有没有按时完成。

```text
系统交付关键任务
→ 开始等待完成信号
→ 截止时间前收到：任务完成
→ 截止时间后仍未收到：进入 ANR 处理
```

因此 `RUNNABLE`、`BLOCKED`、`WAITING` 和 native 调用只是“为什么没有完成”的线索，不是 ANR 的统一定义。

## 用“埋雷、拆雷、爆雷”理解组件超时

Service 最适合用来建立这个模型：

```text
埋雷：system_server 记录 Service 开始执行，并安排超时检查
拆雷：应用完成生命周期回调，经 Binder 通知系统收尾
爆雷：检查触发时，任务仍处于超时未完成状态
```

最小调用链如下：

```text
startService
→ AMS / ActiveServices
→ bumpServiceExecutingLocked
→ ApplicationThread.scheduleCreateService
→ ActivityThread 主线程执行 Service 回调
→ serviceDoneExecuting
```

超时消息只是检查时机。真正关键的是：Service 已开始执行、完成信号还没回来，并且执行时间已经超过期限。

计时和判定放在 `system_server`，是因为应用可能主线程阻塞、进程冻结或长期得不到调度。裁判不能与被检测对象一起失去响应。

## Service、Broadcast、Provider 怎样检测？

它们都符合“开始等待—完成信号—超时检查”，但等待的职责不同。

| 场景 | 系统等待什么 | 什么表示完成 |
|---|---|---|
| Execute Service | Service 生命周期回调 | `serviceDoneExecuting` |
| Broadcast | Receiver 处理广播 | `onReceive()` 返回或 `PendingResult.finish()` |
| Provider 发布 | 新进程发布 Provider | `publishContentProviders` |
| Provider 查询 | 远程 Provider 返回结果 | Binder 调用返回 |

Provider 发布超时与远程 Provider 查询无响应不是同一件事。前者等待应用启动期间完成发布；后者是调用方等待远程调用返回。

不要背一张跨版本通用秒数表。Service 的 AOSP 常见默认值是前台执行 20 秒、后台执行 200 秒；Broadcast 还受 Intent 标志、Android 版本、CPU starvation 和 OEM 实现影响。

线上分析应先读 ANR 的 `reason/subject`，再对照目标系统版本确认具体阈值与源码。

## Input 为什么是另一套机制？

Input 有独立的读取、分发和确认链路：

```text
内核产生事件
→ InputReader 标准化
→ InputDispatcher 选择目标窗口
→ 事件经 InputChannel 交付应用
→ 主线程分发到 View 树
→ finishInputEvent
→ ACK 返回 InputDispatcher
```

系统可能还没找到可接收事件的窗口，也可能已经交付事件、正在等待 ACK。前者常见于 No focused window；后者表现为目标连接的等待队列长期没有完成。

## `eventTime`、`deliveryTime` 和 `timeoutTime` 有什么区别？

`eventTime` 是事件产生时间，可用于理解用户感受到的完整延迟。

现代 AOSP 会在交付事件时记录 `deliveryTime`，再结合窗口的 `dispatchingTimeout` 形成 `timeoutTime`。InputDispatcher 检查等待队列中最老条目是否超过它自己的截止时间。

所以“事件产生到 ACK 的完整生命周期”与“某版本源码采用的 ANR 计时起点”不能写成同一个概念。

## 四个场景判断

1. 主线程持续进行 JSON 解析，Service 回调没按时结束：仍可能发生 ANR。
2. Receiver 使用 `goAsync()`：`onReceive()` 返回不等于完成，还要等待 `PendingResult.finish()`。
3. 应用没主动调用某 Provider：不代表启动阶段不会执行 Provider 发布。
4. 主线程栈是 `nativePollOnce`：只能说明采样时正在等消息，不能推翻此前发生过超时。

## 常见误区

1. 主线程还在运行，所以不应该发生 ANR。
2. 所有 ANR 都是主线程固定 5 秒未响应。
3. Broadcast 的“前台”就是应用有前台 Activity。
4. Provider 发布超时与远程查询无响应是同一检测。
5. 所有 Android 版本都从原始 `eventTime` 使用同一固定阈值。
6. 超时检查一触发，就一定不再复核任务状态。

## 本篇自测

1. 主线程正在执行代码，为什么仍可能发生 Service ANR？
2. “埋雷、拆雷、爆雷”分别对应什么？
3. Service、Broadcast、Provider 与 Input 的完成信号有什么不同？
4. `eventTime`、`deliveryTime` 与 `timeoutTime` 为什么不能混用？

## 一句话总结

ANR 判定的是限时职责没有完成；线程状态只负责解释它为什么没完成。
