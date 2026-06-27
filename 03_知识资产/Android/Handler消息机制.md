# Handler 消息机制面试体系

## 01. 为什么要有 MessageQueue

### 1.1 单 UI 线程模型带来的约束

MessageQueue 的产生，核心来自 Android 的 **单 UI 线程模型 + 16ms 刷新约束**。

Android 的 UI 更新由主线程统一负责。`doFrame()`、`performTraversals()`、`measure/layout/draw` 等 UI 相关流程都运行在主线程。

如果其他线程也能直接更新 UI，会带来什么问题？

```text
主线程正在更新 UI，工作线程也在更新 UI。
多个线程并发修改同一套 View 树和 UI 状态。
最终可能出现状态覆盖、读写不一致、绘制时机错乱等问题。
```

所以 Android 选择单 UI 线程模型：UI 状态统一由主线程修改，避免多个线程直接竞争同一套 UI 状态。

### 1.2 单 UI 线程模型带来的线程通信需求

但这又带来一个新问题：实际业务中经常需要网络请求、磁盘 IO、数据库读写等耗时操作。这些任务不能放在主线程执行，只能放到工作线程处理。工作线程处理完成后，又需要把结果交给主线程更新 UI。

于是问题变成：

```text
工作线程如何把结果交给主线程？
主线程如何在不被长期阻塞的情况下接收并执行这些任务？
```

### 1.3 线程通信的难点是同步和互斥

从操作系统角度看，通信可以分为进程间通信和线程间通信。

进程之间彼此隔离，拥有独立地址空间，不能直接访问对方内存，通常需要通过系统调用进入内核，由内核完成数据中转。

线程不同。多个线程属于同一进程，共享同一份进程地址空间。线程之间不是不能访问同一份数据，而是访问共享数据时必须解决：

```text
同步：控制线程之间的执行先后关系。
互斥：保护临界区，避免共享数据被并发读写破坏一致性。
```

### 1.4 为什么不能主要依赖锁

看起来，主线程和工作线程也可以通过锁来通信：工作线程写结果，主线程加锁读取结果。但这不适合作为 Android UI 线程的主要协作模型。

原因在于主线程有 16ms 左右的刷新压力。60Hz 屏幕下，1 秒刷新 60 次，一帧大约 16.67ms。主线程如果因为等待锁、IO、死锁或耗时任务长期阻塞，就会影响绘制、输入和生命周期调度，轻则掉帧卡顿，重则触发 ANR。

### 1.5 MessageQueue 的设计思路

所以 Android 需要一种更适合主线程的通信方式：

```text
工作线程不直接更新 UI。
工作线程只把结果封装成 Message/Runnable 投递到主线程的 MessageQueue。
主线程通过 Looper 从 MessageQueue 中取出任务并串行执行。
```

MessageQueue 的方案是：工作线程短暂加锁访问消息链表，把消息按执行时间插入队列；Looper 所在线程从队列中取出消息并执行。

它不是完全无锁。`enqueueMessage()` 和 `next()` 内部仍会短暂 `synchronized` 保护消息链表。但它避免了主线程和工作线程围绕业务状态长期互斥，把跨线程协作变成：

```text
工作线程短暂入队。
主线程串行取出并执行。
```

主线程的消息循环在应用进程启动时创建。应用进程由 Zygote fork 后，主线程进入 `ActivityThread.main()`，创建主线程 Looper 和 MessageQueue，并启动 `Looper.loop()`。因此主线程天然具备从 MessageQueue 中接收和处理任务的能力。

### 1.6 面试表达

面试表达：

```text
Android 需要 MessageQueue，根本原因是单 UI 线程模型和 16ms 刷新约束。UI 状态必须统一由主线程修改，避免多个线程并发更新 View 树导致状态不一致；但网络、磁盘 IO 等耗时任务又必须放到工作线程执行。直接用锁让主线程和工作线程围绕业务状态同步，可能导致主线程等待锁、掉帧甚至 ANR。MessageQueue 的方式是让工作线程只负责短暂入队，把结果封装成 Message/Runnable 投递到主线程；主线程通过 Looper 串行取出并执行，从而兼顾线程通信、UI 状态一致性和主线程响应性。
```

## 02. MessageQueue 有哪些组成部分

如果从零设计一套 Android 主线程消息队列，需要解决四个问题：

```text
任务本身是什么？
任务存在哪里？
谁负责不断取任务并分发？
谁负责发送任务和处理任务？
```

Android 中分别对应 `Message`、`MessageQueue`、`Looper`、`Handler`。

### 2.1 首先需要一个 Message：表示任务本身

`Message` 是消息机制中的任务单元，可以理解为对一次待执行任务的封装。

关键字段：

```text
when：消息应该在什么时候执行。
target：消息最终应该交给哪个 Handler 处理。
callback：Runnable，对应 Handler.post(Runnable)。
what/arg1/arg2/obj：业务消息字段，对应 sendMessage(Message)。
flags：消息标记，例如是否是异步消息。
next：链表指针，用于把多个 Message 串成队列。
```

这里有两个后续高级机制会用到的点：

```text
msg.target == null：表示同步屏障。
msg.isAsynchronous() == true：表示异步消息。
```

所以 `Message` 不只是一个 `what`，它同时描述了：

```text
这是什么任务。
什么时候执行。
由谁处理。
是否具备异步调度属性。
在链表中的下一个节点是谁。
```

### 2.2 需要一个存放 Message 的地方：MessageQueue

`MessageQueue` 用来保存 Message。它在 Java 层的核心不是数组队列，而是一个按 `when` 排序的单链表：

```text
mMessages：链表头节点。
Message.next：下一个节点。
Message.when：排序依据。
```

MessageQueue 不是普通 FIFO。因为 Handler 同时支持立即消息和延迟消息，如果只按入队顺序处理，先入队的延迟消息可能挡住后入队的立即消息。

因此 MessageQueue 按 `when` 从小到大维护链表：

```text
when 越早，越靠近队头。
when 到期，MessageQueue.next() 才能取出执行。
```

入队和取消息都需要短暂 `synchronized` 保护链表结构。这里的锁只保护消息队列本身，避免多个线程同时插入或取出破坏链表，不是让主线程和工作线程围绕业务状态长期互斥。

### 2.3 需要一个管理者：Looper

有了 Message 和 MessageQueue，还需要有人不断从队列中取消息，并把消息分发出去，这就是 `Looper`。

`Looper.loop()` 的核心职责：

```text
不断调用 MessageQueue.next()。
取出当前应该执行的 Message。
通过 msg.target.dispatchMessage(msg) 分发给目标 Handler。
```

Looper 本身不处理业务逻辑。它只负责循环、取消息、分发消息。

主线程的 Looper 在应用启动时由 `ActivityThread.main()` 创建并启动。普通线程默认没有 Looper，如果要让普通线程具备消息循环能力，需要主动调用：

```text
Looper.prepare()
Looper.loop()
```

### 2.4 需要一个发送者和处理者：Handler

`Handler` 既是消息发送者，也是消息处理者。

作为发送者，它通过：

```text
post(Runnable)
sendMessage(Message)
```

把任务投递到绑定 Looper 的 MessageQueue 中。

发送时，Handler 会设置：

```text
msg.target = this
msg.when = uptimeMillis
```

作为处理者，当 Looper 从 MessageQueue 取出消息后，会调用：

```java
msg.target.dispatchMessage(msg);
```

这里的 `target` 就是发送这条消息的 Handler。最终消息会回到这个 Handler，由它决定执行 `msg.callback`、`Handler.Callback`，还是 `handleMessage()`。

### 2.5 四者关系总结

```text
Message：任务本身。
MessageQueue：存放 Message 的按时间排序链表。
Looper：消息队列管理者，负责循环取消息并分发。
Handler：消息发送者和处理者。
```

绑定关系：

```text
一个线程最多一个 Looper。
一个 Looper 持有一个 MessageQueue。
一个 Looper 可以对应多个 Handler。
一个 Handler 绑定一个 Looper。
每条 Message 通过 target 记录最终处理它的 Handler。
```

Java 层 MessageQueue 保存 Java Message 链表。Native 层通过 `mPtr` 关联 `NativeMessageQueue`，配合 `epoll/eventfd` 完成阻塞和唤醒；Native 层不保存 Java Message。

## 03. MessageQueue 的 Java 层如何运行

### 3.1 主线程消息循环如何启动

应用进程由 Zygote fork 后，主线程进入 `ActivityThread.main()`。主线程会创建 Looper 和 MessageQueue，并启动消息循环：

```java
public static void main(String[] args) {
    Looper.prepareMainLooper();

    ActivityThread thread = new ActivityThread();
    thread.attach(false);

    Looper.loop();
}
```

从这之后，主线程长期运行在 `Looper.loop()` 中，通过 MessageQueue 接收系统调度、生命周期、输入、绘制和应用自己投递的任务。

### 3.2 Handler 如何把任务送入 MessageQueue

`post(Runnable)` 和 `sendMessage(Message)` 最终都会变成 Message 入队。

`post(Runnable)` 会把 Runnable 放入 `msg.callback`：

```java
public final boolean post(Runnable r) {
    return sendMessageDelayed(getPostMessage(r), 0);
}

private static Message getPostMessage(Runnable r) {
    Message m = Message.obtain();
    m.callback = r;
    return m;
}
```

发送前，Handler 会设置两个关键字段：

```java
msg.target = this;
msg.when = uptimeMillis;
queue.enqueueMessage(msg, uptimeMillis);
```

含义：

```text
target：这条消息最终由哪个 Handler 处理。
when：这条消息应该在什么时候执行。
```

`enqueueMessage()` 会在 `synchronized (this)` 中按 `when` 插入链表：

```java
boolean enqueueMessage(Message msg, long when) {
    synchronized (this) {
        msg.when = when;

        Message p = mMessages;
        if (p == null || when < p.when) {
            msg.next = p;
            mMessages = msg;
        } else {
            Message prev;
            for (;;) {
                prev = p;
                p = p.next;
                if (p == null || when < p.when) {
                    break;
                }
            }
            msg.next = p;
            prev.next = msg;
        }
    }
    return true;
}
```

入队后，如果新消息需要让阻塞中的 Looper 提前醒来，MessageQueue 会调用 `nativeWake()`。

### 3.3 Looper 如何取出并分发消息

`Looper.loop()` 的核心是一个无限循环：

```java
public static void loop() {
    final Looper me = myLooper();
    final MessageQueue queue = me.mQueue;

    for (;;) {
        Message msg = queue.next();
        if (msg == null) {
            return;
        }

        msg.target.dispatchMessage(msg);
        msg.recycleUnchecked();
    }
}
```

关键链路：

```text
Handler.post/sendMessage
  -> Message
  -> MessageQueue.enqueueMessage()
  -> Looper.loop()
  -> MessageQueue.next()
  -> msg.target.dispatchMessage(msg)
```

`dispatchMessage()` 的执行优先级：

```java
public void dispatchMessage(Message msg) {
    if (msg.callback != null) {
        msg.callback.run();
    } else if (mCallback != null) {
        if (mCallback.handleMessage(msg)) {
            return;
        }
    } else {
        handleMessage(msg);
    }
}
```

顺序是：

```text
Message.callback
  -> Handler.Callback
  -> Handler.handleMessage()
```

### 3.4 postDelayed 为什么不需要新线程或定时器

`postDelayed()` 本质还是发送 Message，只是把执行时间设置到未来：

```text
msg.when = SystemClock.uptimeMillis() + delayMillis
```

然后 MessageQueue 按 `when` 插入链表。`MessageQueue.next()` 取消息时，如果队头消息还没到时间，就计算：

```text
nextPollTimeoutMillis = msg.when - now
```

再传给 `nativePollOnce()`，让线程最多睡到这个时间点。期间如果有更早的新消息入队，会通过 `nativeWake()` 提前唤醒，重新检查队列。

所以延迟消息依赖的是：

```text
when + 按时间排序的链表 + nativePollOnce(timeout)
```

不是每个延迟任务创建一个线程或定时器。

## 04. MessageQueue 的 Native 层如何运行

Native 层主要负责主线程的阻塞睡眠和唤醒，用于提高 CPU 的使用效率：没有可执行消息时让主线程睡眠，避免空转；有新消息需要处理时再把主线程唤醒。

### 4.1 为什么阻塞

`Looper.loop()` 是死循环，但主线程不能一直空转检查队列。没有可执行消息时，`MessageQueue.next()` 会进入 Native 层等待，让线程让出 CPU，降低空转和功耗。

### 4.2 在哪里阻塞

阻塞链路：

```text
MessageQueue.next()
  -> nativePollOnce(mPtr, nextPollTimeoutMillis)
  -> Native Looper.pollOnce()
  -> epoll_wait()
```

`nextPollTimeoutMillis` 有三种取值：

```text
0：不阻塞，立刻返回。
正数：最多阻塞指定时间，通常是队头延迟消息的 msg.when - now。
-1：无限等待，直到 fd 事件到来或被唤醒。
```

### 4.3 谁来唤醒

其他线程或主线程自己通过 Handler 入队新消息时，如果这条消息需要让 Looper 提前处理，`MessageQueue.enqueueMessage()` 会触发：

```java
nativeWake(mPtr);
```

不是每次入队都一定唤醒。只有当前 Looper 可能正在阻塞，且新消息需要更早处理时才需要唤醒。

### 4.4 怎么唤醒

Native 层会创建一个 `eventfd` 并注册到 epoll。唤醒时向 eventfd 写入数据：

```cpp
eventfd_write(wakeEventFd, 1);
```

eventfd 变为可读后，`epoll_wait()` 返回，主线程从 Native 层回到 Java `MessageQueue.next()`，重新检查 Java 消息链表。

完整链路：

```text
Handler.post/sendMessage()
  -> MessageQueue.enqueueMessage()
  -> nativeWake()
  -> eventfd_write()
  -> epoll_wait() 返回
  -> nativePollOnce() 返回
  -> MessageQueue.next() 重新检查链表
  -> 取出到期 Message
  -> Looper 分发
```

面试表达：

```text
Java 层 MessageQueue 负责维护 Message 链表；Native Looper 负责让线程在没有消息时阻塞在 epoll_wait 上。新消息需要提前处理时，Java 层调用 nativeWake，Native 层写 eventfd，eventfd 触发 epoll_wait 返回，主线程回到 MessageQueue.next() 重新取消息。
```

## 05. MessageQueue 中的高级机制

### 5.1 同步屏障与异步消息

同步屏障是一条特殊 Message：

```text
msg.target == null
```

异步消息通过 `Message.flags` 标记：

```java
msg.setAsynchronous(true);
msg.isAsynchronous();
```

当 `MessageQueue.next()` 发现队头是同步屏障时，不会执行这条屏障消息，而是从屏障后面向后查找第一条异步消息：

```java
Message prevMsg = null;
Message msg = mMessages;

if (msg != null && msg.target == null) {
    do {
        prevMsg = msg;
        msg = msg.next;
    } while (msg != null && !msg.isAsynchronous());
}
```

例如：

```text
同步屏障 -> 同步消息 A -> 同步消息 B -> 异步消息 C
```

此时 `next()` 会返回异步消息 C，同步消息 A、B 被暂时挡住。同步屏障需要插入方通过 token 调用 `removeSyncBarrier()` 移除，否则后面的同步消息会一直无法执行。

它改变的是“下一次从队列取消息的顺序”，不能抢占当前正在执行的耗时消息。

### 5.2 Choreographer、VSYNC 与 UI 刷新链路

View 请求刷新后，关键调度入口是 `ViewRootImpl.scheduleTraversals()`：

```java
void scheduleTraversals() {
    if (!mTraversalScheduled) {
        mTraversalScheduled = true;

        mTraversalBarrier =
            mHandler.getLooper().getQueue().postSyncBarrier();

        mChoreographer.postCallback(
            Choreographer.CALLBACK_TRAVERSAL,
            mTraversalRunnable,
            null
        );
    }
}
```

这一步做了两件事：

```text
1. 向 MessageQueue 插入同步屏障。
2. 把 traversal 任务交给 Choreographer，等待下一次 VSYNC。
```

VSYNC 到来后，Choreographer 会通过 Handler 发送异步 doFrame 消息：

```java
Message msg = Message.obtain(mHandler, this);
msg.setAsynchronous(true);
mHandler.sendMessageAtTime(msg, timestampMillis);
```

由于 doFrame 是异步消息，所以 `MessageQueue.next()` 遇到同步屏障时，可以跳过前面的普通同步消息，优先取出 doFrame。

doFrame 中会按阶段执行一帧回调：

```text
doCallbacks(CALLBACK_INPUT)
doCallbacks(CALLBACK_ANIMATION)
doCallbacks(CALLBACK_TRAVERSAL)
doCallbacks(CALLBACK_COMMIT)
```

`CALLBACK_TRAVERSAL` 最终执行 `ViewRootImpl.doTraversal()`：

```java
void doTraversal() {
    if (mTraversalScheduled) {
        mTraversalScheduled = false;

        mHandler.getLooper().getQueue()
            .removeSyncBarrier(mTraversalBarrier);

        performTraversals();
    }
}
```

完整链路：

```text
View.requestLayout()/invalidate()
  -> ViewRootImpl.scheduleTraversals()
  -> postSyncBarrier()
  -> Choreographer.postCallback(CALLBACK_TRAVERSAL, mTraversalRunnable, null)
  -> VSYNC 到来
  -> Choreographer 发送异步 doFrame 消息
  -> MessageQueue.next() 越过同步屏障取出异步消息
  -> doFrame()
  -> doCallbacks(CALLBACK_TRAVERSAL)
  -> ViewRootImpl.doTraversal()
  -> removeSyncBarrier(mTraversalBarrier)
  -> performTraversals()
  -> measure/layout/draw
```

这套机制的目的，是让 input、animation、traversal 等一帧相关任务在 VSYNC 到来后尽快被主线程取出执行，减少它们被普通同步消息继续拖延的概率。

但它不能保证一定不卡顿：

```text
1. 同步屏障不能中断当前正在执行的耗时消息。
2. doFrame、performTraversals、measure/layout/draw 本身也可能耗时。
```

### 5.3 Handler 延迟消息导致 Activity 泄漏

典型引用链：

```text
MessageQueue
  -> Message
  -> target Handler
  -> Activity
```

如果 Handler 是 Activity 的非静态内部类，它会隐式持有外部 Activity。延迟消息还没执行时，Message 会长时间留在 MessageQueue 中；Message 持有 `target Handler`，Handler 又持有 Activity，导致 Activity `finish()` 后仍可能无法及时回收。

解决方式：

```text
1. 静态内部类 Handler + WeakReference<Activity>。
2. 在 onDestroy() 中调用 removeCallbacksAndMessages(null)。
3. 现代场景优先使用 lifecycleScope 等生命周期感知方案。
```

### 5.4 两分钟面试整合

```text
Android Handler 消息机制本质上是主线程的任务调度模型。由于 Android 采用单 UI 线程模型，后台线程不能直接更新 UI，而主线程又不能被锁和耗时任务长期阻塞，所以需要一套任务投递和串行执行机制。

核心角色有四个：Message 表示任务，MessageQueue 保存 Message 并按 when 排序，Looper 在线程中循环取消息并分发，Handler 负责发送和处理消息。一个线程最多一个 Looper，一个 Looper 持有一个 MessageQueue，但可以对应多个 Handler；每条 Message 通过 target 找到最终处理它的 Handler。

Java 层流程是：Handler.post/sendMessage 最终都会变成 Message。post 会把 Runnable 放进 msg.callback；发送前 Handler 设置 msg.target 和 msg.when，再把消息放入绑定 Looper 的 MessageQueue。MessageQueue 按 when 维护链表。Looper.loop() 不断调用 MessageQueue.next() 取出到期消息，再通过 msg.target.dispatchMessage(msg) 分发给 Handler。dispatchMessage 的优先级是 msg.callback、Handler.Callback、handleMessage。

Native 层解决阻塞唤醒问题。MessageQueue.next() 在没有可执行消息时调用 nativePollOnce()，底层阻塞在 epoll_wait；新消息入队后如果需要唤醒 Looper，会通过 nativeWake() 写 eventfd，使 epoll_wait 返回，主线程再回到 MessageQueue.next() 重新检查链表。

高级机制上，postDelayed 依赖 msg.when、按时间排序的链表和 nativePollOnce(timeout)，不是新开线程计时；同步屏障是 target 为空的特殊 Message，异步消息通过 FLAG_ASYNCHRONOUS 标记，可以越过同步屏障优先执行。ViewRootImpl 请求刷新时插入同步屏障，Choreographer 等 VSYNC 到来后发送异步 doFrame 消息，最终回到 ViewRootImpl.doTraversal，移除屏障并执行 performTraversals。Handler 泄漏通常来自 MessageQueue 中未执行的 Message 持有 Handler，而非静态 Handler 又持有 Activity。
```
