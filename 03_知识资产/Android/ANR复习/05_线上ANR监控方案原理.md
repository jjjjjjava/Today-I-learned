# 第 5 篇 · 如果让你设计一个线上 ANR 监控方案？

> 前置知识：第 4 篇的 Bugly 旁观者模式与 trace 分析；知道 ANR 后系统会 dump traces
> 难度：进阶（信号机制 + 监控原理）
> 预计阅读时间：15 分钟
> 本篇按你的"设计视角"组织：从系统侧流程出发，劈出被动观测 / 主动介入两条路，与第 1 篇"如果让你设计 ANR 检测机制"首尾呼应。

---

## 上一篇思考题复盘

> 📝 你选择直接继续，未提交作答。下面给出第 4 篇三题的正确答案，对照自检。

**第 1 题：Bugly 的"5s 抓一次" vs 系统 SignalCatcher 的 dump，触发时机有何不同？为什么 Bugly 常抓到"干净帧"？**
> - **系统 SignalCatcher**：在 `appNotResponding` 判定 ANR 那一刻收 SIGQUIT、**一次性** dump，时机精准对齐 ANR 点。
> - **Bugly Watchdog**：每 **5s** 固定采样，精度低、采样点和 ANR 爆发点不对齐。常常等它采到时卡顿已结束、主线程恢复空闲，于是抓到主线程趴在 `MessageQueue.next` 的"干净帧"。

**第 2 题：为什么 Bugly Watchdog 漏报 Input ANR？**
> Input 超时判定在系统侧 InputDispatcher 的 waitQueue，**不经过 App 的 MessageQueue**。Watchdog 探活是往 MessageQueue post 消息——主线程可能照常处理这条探活消息（标记位被改回 true，Watchdog 以为"活着"），但触摸事件在 waitQueue 里 5s 没回 ACK，照样被系统判 Input ANR。

**第 3 题：main BLOCKED 在锁，追到持锁线程也在 `waiting to lock` 主线程持有的另一把锁，是什么情况？修复方向？**
> 典型 **AB-BA 死锁**。main 等的锁被死锁线程持有、永远等不到。修复：**统一全局加锁顺序**破循环等待、缩小锁粒度、持锁期间别做 IO/Binder/耗时操作。

---

## ??? 解答

> 💬 上一篇无 `???` 标注，直接进入新内容。

---

## 正文内容

第 1 篇我们问过"如果让你设计 ANR 的**检测机制**"。这一篇换成下游问题：**如果让你设计一个线上 ANR 监控方案，你会怎么做？** 设计的锚点，是先看清系统侧自己已经做了什么。

### 一、先回顾：系统侧 appNotResponding 做了什么

```text
AMS 判定某进程 ANR → 进入 appNotResponding：
  1. 给 App 进程发 SIGQUIT（信号 3）
  2. App 进程收到信号，dump 自身所有线程堆栈，写入 /data/anr/traces.txt
  3. AMS 继续收集 CPU 使用率等现场，前台进程弹框（让用户等待/关闭），后台可能直接杀
```

我们要做的监控，无非是**想办法拿到第 2 步那份现场（线程栈）+ 第 3 步的定性（确实 ANR 了）**。围绕"要不要去碰系统的 SIGQUIT 流程"，就分出两条设计路线。

### 二、两种设计思路：被动观测 vs 主动介入

```text
被动观测式：不碰系统的 SIGQUIT 流程，在旁边自己探活 + 借系统产物/广播定性。  代表：Bugly
主动介入式：注册 SIGQUIT handler，抢先拦截信号、自己 dump，再把信号补发回系统。 代表：xCrash / Matrix
```

### 三、被动观测式：Bugly（旁观者）

Bugly 不介入信号流程，靠**三个组件**协作（细节见第 4 篇，这里作为"被动派"代表回顾）：

```text
1. FileObserver     —— 监听系统 trace 文件的写入，拿系统判定的 ANR 现场。
                       但 Android 高版本 SELinux 收紧 /data/anr/，基本失效，只能兜底。
2. 错误状态轮询    —— 轮询 ActivityManager.getProcessesInErrorState()，查到 NOT_RESPONDING 即【定性】确实发生了 ANR（系统对第三方 App 没有 ANR 广播）。
3. Bugly 线程(Watchdog)—— 核心：死循环每 5s post 一个消息到主线程改标记位、再 sleep 5s；
                       醒来若标记位没被改，说明主线程没及时处理 → 大概率卡了 → 抓栈暂存；
                       但先不上报，等收到 ANR 广播确认非误报，才上报。
```

被动式的代价：**误报**（合法长任务未到阈值就被 Watchdog 当卡顿）、**漏报 Input ANR**（不经过 MessageQueue）、采样精度低、且只有 Java 栈。胜在**安全**——完全不碰系统流程，没有把系统 ANR 搞坏的风险。

### 四、主动介入式：先打通"信号"这一关

主动派的出发点：系统是靠 **SIGQUIT** 来触发 dump 的，那我能不能**自己注册一个 SIGQUIT 的 handler**，信号一来先归我处理、自己 dump？

可以。但马上撞上一个绕不开的约束——

```text
sigaction（注册 handler，被动接收）：信号来了，内核打断线程、跳去执行我的 handler。
sigwait（主动领取）：线程阻塞等信号，自己取走处理。ART 的 SignalCatcher 就是这种。

核心冲突：同一个信号只能被消费一次。
  我的 handler 一旦消费了 SIGQUIT，系统的 SignalCatcher 就收不到、系统 ANR 流程被打断。
```

所以主动介入的**必答题**是：

```text
既要自己拦截 SIGQUIT、抢先 dump；
又要把 SIGQUIT 补发回去，让 ART SignalCatcher 还能收到，系统流程继续走完。
```

xCrash 和 Matrix，就是这道补发题的两种答法。

### 五、xCrash：链式拦截

```text
注册 sigaction handler
  → SIGQUIT 到来，handler 内【直接完整 dump 自身线程栈】、保存发送
  → 注销自身 handler
  → raise(SIGQUIT) 补发，期望 SignalCatcher 收到
```

两个问题：

**① 信号上下文约束（不是"系统调用"，要说准）**

```text
handler 运行在【信号上下文 signal context】，只能调 async-signal-safe 的函数。
在里面做 malloc / mutex / fprintf / 复杂 IO / Java 调用 —— 都可能违反约束、属 undefined behavior。
所以在 handler 里直接做完整 dump，既受限、又有 UB 风险。
```

**② 时序竞态（补发不可靠）**

```text
"注销 handler" 和 "raise(SIGQUIT)" 之间有时间窗口；
若 handler 还没完全卸载，补发的 SIGQUIT 可能又被 xCrash 自己消费 ——
SignalCatcher 收不到，系统 dump 流程被破坏。补发更像 best-effort。
```

### 六、Matrix：委托线程（管道 + catcher 线程）

Matrix 的改进：handler 里**什么重活都不干，只感知**。

```text
预先：建一个管道 pipe + 一个 catcher 线程，catcher 阻塞在 read(pipe)
SIGQUIT 到来
  → sigaction handler 只做一件事：write(pipe, "1", 1)，立即返回
  → catcher 线程被唤醒，【在普通线程上下文】里：
        完整 dump 所有线程栈 → 注销 handler → kill(getpid(), SIGQUIT) 补发
  → 补发时 handler 早已卸载 → SignalCatcher 的 sigwait 稳定收到
```

为什么 Matrix 解决了 xCrash 的两个问题：

```text
对问题①：dump 不在信号上下文做，而在【普通线程上下文】，不受 async-signal-safe 约束，
         能安全拿到足够丰富的信息（含 native）。
对问题②：注销 handler 和补发 SIGQUIT 都在普通线程里【顺序执行、时序可控】，
         补发那一刻 handler 一定已卸载干净 → SIGQUIT 不会再被自己消费。
```

> Matrix 的本质：**把"感知信号"和"处理信号"解耦**——handler 只 write pipe（感知），catcher 线程负责 dump/卸载/补发（处理），把不可控的信号上下文转成可控的普通线程上下文。

### 七、对比与核心结论

```text
| 方案   | 路线     | handler 行为 | 上下文       | 转发可靠性     | 主要代价                  |
|--------|----------|--------------|--------------|----------------|---------------------------|
| Bugly  | 被动观测 | 无           | —            | 无需转发       | 误报/漏报 Input、仅 Java 栈 |
| xCrash | 主动介入 | 完整 dump    | 信号上下文   | 有竞态，不可靠 | UB 风险 + 补发竞态        |
| Matrix | 主动介入 | 只写 1 字节  | 普通线程上下文 | 时序可控，可靠 | 实现复杂                  |
```

**核心结论（背这一句）：**

```text
SignalCatcher 能不能收到补发的 SIGQUIT，
只取决于【补发那一刻，sigaction handler 是否已经完全卸载】。
Matrix 更稳，不是因为 dump 得快，而是把卸载与补发挪进普通线程、做到时序可控。
```

---

## 思考题

1. 你来设计监控方案，第一步会先选"被动还是主动"。说出你的选择依据——各自最大的风险/代价是什么？
2. 主动介入为什么绕不开"补发 SIGQUIT"？不补发会怎样？
3. 有人说"Matrix 更稳是因为 catcher 线程 dump 得更快、更全"。哪一半对、哪一半不对？真正决定补发能否被 SignalCatcher 收到的是什么？

## 你的反馈

> 你这遍以"如果让你设计监控方案"的视角把 Bugly/xCrash/Matrix 串成被动 vs 主动两条路，结构很好。本篇已按此重写。两处术语已校准：
> 1. xCrash handler 的限制是**信号上下文 / async-signal-safe**（不是"系统调用"），既受限又有 UB 风险；
> 2. Matrix"SIGQUIT 不会被再次消费"的真因是**卸载与补发在普通线程顺序执行、时序可控**（不是单纯"使用宽松"，更不是"dump 更快"）。
>
> 后续若有新疑问，继续写在这里，或用 `???你的困惑` 就地标注。
