---
phase: 01-android
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - "04. 学习_Android核心原理/01. Handler机制.md"
autonomous: true
requirements: [HANDLER-01]

must_haves:
  truths:
    - "笔记包含完整的消息机制原理链路：ThreadLocal -> Looper -> MessageQueue -> Handler 的协作关系"
    - "笔记解释了 epoll 在 native 层的阻塞唤醒机制，包括 nativePollOnce 和 nativeWake"
    - "笔记解释了主线程 Looper 死循环为什么不 ANR"
    - "笔记包含同步屏障与 Choreographer 的关系"
    - "笔记包含 IdleHandler 和 Message.sPool 消息复用池"
  artifacts:
    - path: "04. 学习_Android核心原理/01. Handler机制.md"
      provides: "Handler 消息机制完整面试笔记"
      contains: "epoll"
      min_lines: 200
  key_links:
    - from: "01. Handler机制.md"
      to: "Choreographer"
      via: "同步屏障 postSyncBarrier 确保 VSYNC 异步消息优先处理"
      pattern: "postSyncBarrier.*Choreographer"
---

<objective>
撰写 `01. Handler机制.md` 面试笔记，完整覆盖 Android 消息机制原理。

Purpose: Handler/Looper/MessageQueue 是大厂面试必考（字节/腾讯/阿里/美团 100% 考察率），需要达到源码级理解深度，能不看笔记完整讲述原理链路并应对三层追问。
Output: 一篇结构化的面试准备笔记文件 `04. 学习_Android核心原理/01. Handler机制.md`
</objective>

<execution_context>
@d:/.claude/get-shit-done/workflows/execute-plan.md
@d:/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-android/01-RESEARCH.md
@.planning/research/CORE_ANDROID.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: 创建目录并撰写 Handler 机制面试笔记</name>
  <files>04. 学习_Android核心原理/01. Handler机制.md</files>
  <read_first>
    - .planning/phases/01-android/01-RESEARCH.md（Topic 1: Handler 机制部分，含核心链路图和子概念表）
    - .planning/research/CORE_ANDROID.md（Handler 考点详情：典型问题、深度档次、陷阱）
    - .planning/research/INTERVIEW_STRATEGY.md（笔记模板结构）
  </read_first>
  <action>
    首先创建目录 `04. 学习_Android核心原理/`（如果不存在）。

    然后撰写 `01. Handler机制.md`，使用以下结构（来自 01-RESEARCH.md 推荐模板）：

    **# 01. Handler 消息机制**

    **> 一句话总结（面试开场句）：** Handler 通过 ThreadLocal 保证线程私有 Looper，Looper 从 MessageQueue（按时间戳排序的链表）循环取消息，底层通过 epoll 实现无消息时阻塞不占 CPU、有消息时即时唤醒。

    **## 一、核心原理链路**
    绘制 ASCII 流程图，内容必须包含：
    ```
    Thread.start()
      -> Looper.prepare()  [ThreadLocal<Looper> 存入当前线程]
      -> new MessageQueue() [native层创建 epoll fd + pipe fd]
      -> Looper.loop()
          -> MessageQueue.next()
              -> nativePollOnce(fd, timeoutMillis)  [epoll_wait 阻塞]
              -> 返回到期的 Message
          -> msg.target.dispatchMessage(msg)
              -> Handler.handleMessage()
      -> [发送消息时] Handler.sendMessage()
          -> MessageQueue.enqueueMessage() [按 when 时间戳插入链表]
          -> nativeWake(fd)  [write 到 pipe -> epoll_wait 返回]
    ```

    **## 二、关键机制详解**

    必须包含以下子章节，每个子章节都要回答"为什么这么设计"：

    ### 2.1 ThreadLocal 保证线程隔离
    - ThreadLocal 是线程局部变量，每个线程有独立副本
    - Looper.prepare() 通过 ThreadLocal.set() 存入，Looper.myLooper() 通过 ThreadLocal.get() 取出
    - 为什么不用全局 Map<Thread, Looper>？避免并发同步开销，ThreadLocal 是无锁设计

    ### 2.2 MessageQueue 链表结构
    - 不是 FIFO 队列，而是按 Message.when 时间戳升序排列的单链表
    - enqueueMessage() 按 when 插入合适位置
    - 为什么用链表不用 PriorityQueue？频繁的插入删除操作，链表 O(n) 插入但无需扩容

    ### 2.3 nativePollOnce / epoll 阻塞唤醒
    - nativePollOnce(ptr, timeoutMillis) 底层调用 epoll_wait
    - timeoutMillis: -1 永久阻塞 / 0 立即返回 / >0 超时等待
    - nativeWake(ptr) 底层 write(mWakeEventFd) 触发 epoll_wait 返回
    - 关键：阻塞在 epoll_wait 时不消耗 CPU 时间片（让出 CPU 给其他线程）

    ### 2.4 同步屏障 postSyncBarrier
    - 同步屏障是 target == null 的特殊 Message
    - MessageQueue.next() 遇到屏障时，跳过所有同步消息，只取异步消息（isAsynchronous=true）
    - Choreographer 每帧开始前插入同步屏障 -> VSYNC 回调是异步消息 -> 确保 UI 绘制优先
    - removeSyncBarrier() 移除屏障后恢复正常消息处理

    ### 2.5 Choreographer 与同步屏障的关系
    - Choreographer.scheduleVsyncLocked() 注册 VSYNC 信号回调
    - VSYNC 到来时 -> Choreographer.doFrame() -> performTraversals()
    - 利用同步屏障保证绘制消息优先于其他普通消息（如 Handler.post 的延迟任务）

    ### 2.6 IdleHandler 用途与触发时机
    - 在 MessageQueue 没有消息或所有消息都是延迟消息（还未到时间）时触发
    - 用途：延迟初始化、GC、Activity 空闲时上报数据
    - 不保证执行时机：如果主线程持续忙碌，IdleHandler 永远不会执行
    - queueIdle() 返回 false 则自动移除，返回 true 则保留下次空闲再调用

    ### 2.7 Message.sPool 消息复用池
    - 链表实现的对象池，最大容量 MAX_POOL_SIZE = 50
    - Message.obtain() 从池头取出复用，Message.recycle() 清空数据放回池头
    - 为什么用链表不用 ArrayList？消息池只需 O(1) 头部操作，链表最合适
    - 注意：recycle() 后不能再使用该 Message 对象

    ### 2.8 主线程 Looper 死循环为什么不 ANR
    - Looper.loop() 确实是死循环 for(;;)
    - 但阻塞在 MessageQueue.next() 的 nativePollOnce (epoll_wait)
    - 此时线程处于 WAITING 状态，不占 CPU（与 while(true){} 本质不同）
    - ANR 定义：消息处理超时（如 Activity 5s 未响应），不是"没有消息时等待超时"
    - 没有消息时阻塞等待是正常行为；有消息处理太慢才导致 ANR

    **## 三、为什么这么设计（追问准备）**
    - 为什么不用 Java 的 wait/notify 而用 native epoll？性能更好，且能同时监听文件描述符（如 Input 事件、VSYNC 信号）
    - 为什么每个线程只能有一个 Looper？确保消息顺序处理，多 Looper 会导致消息乱序
    - 为什么 Message 要用对象池而不是每次 new？减少 GC 压力，主线程频繁创建 Message 会导致内存抖动

    **## 四、高频面试问法 & 答题要点**
    用表格格式列出至少 8 个典型问题（从 CORE_ANDROID.md 的典型问题列表）：
    | 问法 | 答题要点（关键词） | 易错点 |
    包含但不限于：
    - Handler 消息机制整体流程
    - 一个线程几个 Looper 几个 Handler
    - Handler 内存泄漏原因及解法
    - sendMessageDelayed 延迟实现
    - 主线程 Looper 为什么不 ANR
    - IdleHandler 适合做什么
    - 同步屏障是什么

    **## 五、追问陷阱与反脆弱**
    每个陷阱单独列出：陷阱描述 + 正确答案 + 一句话记忆锚点：
    - 陷阱1：Looper.loop() 死循环不占 CPU -> 锚点：epoll_wait 让出 CPU
    - 陷阱2：MessageQueue 是队列 -> 锚点：按 when 排序的链表，不是 FIFO
    - 陷阱3：Handler 延迟消息的精度 -> 锚点：SystemClock.uptimeMillis 不含深度睡眠，有队列排队延迟
    - 陷阱4：同步屏障可以手动调用 -> 锚点：@hide API，应用层不能直接调用

    **## 六、关联知识点**
    - ANR 原理（Handler 消息处理超时 -> AMS 检测）
    - Choreographer 帧调度（VSYNC + 同步屏障）
    - 线程通信方式对比（Handler vs AsyncTask vs RxJava vs Coroutine）
    - LeakCanary 检测（利用 IdleHandler 时机检测泄漏）

    **## 七、参考资料**
    - AOSP 源码路径：frameworks/base/core/java/android/os/Handler.java, Looper.java, MessageQueue.java
    - gityuan.com/2015/12/26/handler-message-framework

    内容要求：
    1. 所有原理解释必须回答"为什么这么设计"
    2. ASCII 流程图必须清晰可读
    3. 关键源码只标注方法签名和关键变量名，不要大段粘贴源码
    4. 每个关键概念用粗体标注记忆锚点
    5. 总字数控制在 3000-5000 字（过长影响复习效率）
  </action>
  <verify>
    <automated>
      grep -c "epoll" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "ThreadLocal" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "nativePollOnce" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "postSyncBarrier" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "IdleHandler" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "sPool" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "Choreographer" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md" &&
      grep -c "ANR" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md"
    </automated>
  </verify>
  <acceptance_criteria>
    - grep "epoll" 返回 >= 3（多处提及 epoll 机制）
    - grep "ThreadLocal" 返回 >= 2
    - grep "nativePollOnce" 返回 >= 1
    - grep "postSyncBarrier" 返回 >= 1
    - grep "IdleHandler" 返回 >= 2
    - grep "sPool" 返回 >= 1
    - grep "Choreographer" 返回 >= 2
    - grep "ANR" 返回 >= 2
    - 文件包含七个大章节（一~七）
    - 包含 ASCII 流程图
    - 包含面试问法表格（至少 8 行）
    - 包含追问陷阱章节（至少 4 个陷阱）
  </acceptance_criteria>
  <done>
    01. Handler机制.md 文件存在于 04. 学习_Android核心原理/ 目录下，包含完整的七个章节结构，所有 grep 检查项通过，ASCII 流程图可读，面试问法表格不少于 8 行，追问陷阱不少于 4 条。
  </done>
</task>

</tasks>

<verification>
1. 文件存在：`ls "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md"`
2. 关键词检查：所有 8 个 grep 检查全部返回 >= 1
3. 结构检查：`grep -c "^## " "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md"` >= 7
4. 行数检查：`wc -l "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/01. Handler机制.md"` >= 200
</verification>

<success_criteria>
- Handler 消息机制笔记覆盖 ROADMAP 中列出的全部考点：ThreadLocal、MessageQueue 链表、epoll 阻塞唤醒、同步屏障、IdleHandler、Message.sPool、主线程死循环不 ANR
- 笔记结构符合面试准备格式（开场句 + 原理链路 + 机制详解 + 追问准备 + 面试问法 + 陷阱 + 关联 + 参考）
- 写完后能根据笔记内容从 ThreadLocal 一路讲到 epoll 阻塞唤醒再到同步屏障，达到"追问三层也能答上"
</success_criteria>

<output>
After completion, create `.planning/phases/01-android/01-01-SUMMARY.md`
</output>
