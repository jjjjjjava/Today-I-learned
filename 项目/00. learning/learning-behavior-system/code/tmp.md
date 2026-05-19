ANR traces 实战诊断 · 核心知识总结

一、ANR 本质

主线程的消息循环（Looper/MessageQueue）在规定时间内没有处理完任务。

超时阈值：
Input 事件（点击/滑动）    5秒
前台 Service              20秒
后台 Service             200秒
BroadcastReceiver 前台    10秒
BroadcastReceiver 后台    60秒

二、三大根因分类
A类  主线程自己在做耗时操作（IO / 网络 / 重计算）
B类  主线程被困住（锁竞争 / 死锁 / 等notify / Binder超时）
C类  主线程抢不到CPU时间片（系统CPU被打满）
线程状态与分类对应：
RUNNABLE + 栈顶IO/计算       → A类
BLOCKED                      → B类（抢锁失败）
WAITING + 业务对象            → B类（等notify）
WAITING + MessageQueue        → ⚠️陷阱，主线程空闲，见第五节
RUNNABLE + 堆栈正常 + CPU爆满 → C类
易错点：
WAITING ≠ C类
WAITING = B类（主动放弃执行权，等其他线程notify）

C类只有一种：RUNNABLE 但调度器不分配时间片
B类CPU使用率通常很低，不能用"CPU低"推断C类

三、诊断三板斧（顺序不能乱）
Step 1  读元信息头
        → ANR类型（Input/Service/Broadcast）
        → 确认是自己的进程（Cmd line）

Step 2  读CPU快照
        → App CPU > 60%    标记"可能A类"
        → 系统CPU > 90%    标记"可能C类"
        → iowait高         标记"可能A类IO"
        → 两者都低         标记"可能B类"
        （此时只是标记，看完堆栈再确认）

Step 3  找主线程堆栈
        → 看状态（BLOCKED/WAITING/RUNNABLE）
        → 看栈顶系统调用
        → 找首个包名帧（根因代码位置）
        → 找锁地址（- waiting to lock / - waiting on）

四、锁链追踪方法
BLOCKED → 搜 "waiting to lock <0xXXXX>"
           再全文搜 "locked <0xXXXX>"
           → 找到持锁线程
           → 看持锁线程是否也在 waiting to lock（判断死锁）

WAITING → 搜 "waiting on <0xXXXX>"
           → 找应该调用notify但被卡住的工作线程
死锁识别口诀：
A 持有 X，等待 Y
B 持有 Y，等待 X
→ 互相等待，永远不释放

修复：全局统一加锁顺序（所有线程按同一顺序获取多把锁）
找不到 locked<地址> 时：
可能1：持锁线程在trace文件其他位置，看完整trace
可能2：持锁线程是native线程，看native堆栈
可能3：持锁者已释放，结合logcat交叉验证
→ 没有证据不下结论

五、两个高频陷阱
陷阱1：MessageQueue + WAITING
"main" WAITING
  at MessageQueue.next()
  - waiting on <地址> (a android.os.MessageQueue)

这是主线程空闲的正常状态，不是根因。

正确动作：
  → 回头看CPU快照
  → 系统CPU爆满          → C类
  → 搜 InputDispatcher   → 被卡住则是系统层问题
  → 都正常               → trace快照时机问题，结合logcat
陷阱2：Finalizer/HeapTaskDaemon WAITING
这两个线程处于 WAITING = GC空闲，不是GC正在发生的证据
只有它们处于 RUNNABLE 才说明GC有压力
→ 没有证据不推断GC根因

六、特殊Pattern
Binder超时：
"main" BLOCKED
  at BinderProxy.transactNative(Native Method)
  at BinderProxy.transact(...)

主线程同步调用系统服务（AMS/WMS），对方没有及时响应
→ 不是你的代码bug
→ 去trace里找system_server进程的Binder线程池状态
→ 修复：减少主线程的同步Binder调用
多线程同跑同一方法：
主线程    → ImageProcessor.applyFilter()
子线程1   → ImageProcessor.applyFilter()
子线程2   → ImageProcessor.applyFilter()

= A类（主线程做重计算）+ C类风险（子线程并发把CPU打满）
修复：主线程移出计算 + 限制子线程并发数

七、根因速查卡
现象组合                              结论           修复方向
──────────────────────────────────────────────────────────────
RUNNABLE + 栈顶IO + 包名帧            A类IO          移出主线程
RUNNABLE + App CPU高 + 业务计算       A类计算         移出主线程
BLOCKED + waiting to lock            B类锁竞争       统一加锁顺序
BLOCKED + 两线程互相等                B类死锁         统一加锁顺序
WAITING + 业务对象 + 工作线程被卡     B类等通知       排查通知链路
BLOCKED + BinderProxy                B类Binder超时   减少同步Binder调用
RUNNABLE + 堆栈正常 + 系统CPU爆满     C类CPU饥饿      提优先级/限并发
WAITING + MessageQueue + CPU正常      trace无效       结合logcat
多线程同跑同一计算方法                 A+C叠加         移出主线程+限并发

八、诊断原则（最重要）
1. trace 是 ANR 触发瞬间的快照，不是卡顿过程的录像
2. 没有证据的结论不写进根因
3. trace 看不出来的，结合 logcat 交叉验证
4. CPU低是B类的标配，不是C类的证据
5. 先追锁链，再下结论，不要靠猜