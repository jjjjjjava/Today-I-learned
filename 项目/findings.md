# Findings — ANR 学习模块

> 本文件记录学习过程中的研究资料、关键发现、踩坑记录。正式知识沉淀到 `04. 学习_性能优化/ANR_*.md` 原始笔记和 `states/active/*.yaml` 卡片。

## 现有初稿盘点（2026-04-10）

### ANR_01.基础概念.md（1346 行）覆盖度

| 章节 | 内容 | 可拆卡片 |
|------|------|---------|
| §01 学习概述 | 知识分类、目标 | - |
| §02 核心概念 | ANR 定义、埋雷-拆雷-爆雷模型、观测者跨线程原因、整体流程 | 部分 → 030 |
| §03 源码分析_埋雷过程 | `realStartServiceLocked` → `bumpServiceExecutingLocked` → `scheduleServiceTimeoutLocked` | → 031 |
| §04 源码分析_拆雷过程 | APP 端 `handleCreateService` → AMS `serviceDoneExecuting` → `serviceDoneExecutingLocked` | → 031 |
| §05 源码分析_爆雷过程 | `MainHandler.handleMessage` → `serviceTimeout` → `appNotResponding` + 边界情况 | → 031 |
| §05 深度思考（重号） | 仅章节标题，无内容 | 待补 |
| §06 实践验证 | 空壳 | 待补（→ 034） |
| §07 应用场景 | 空壳（最佳实践/禁忌） | 待补（→ 034） |
| §08 总结提炼 | 空壳 | 待补 |

### 现有笔记未覆盖的内容（需要新学）

| 主题 | 面试权重 | 对应卡片 |
|------|---------|---------|
| Activity/Input ANR 触发机制（5s 无响应触摸事件） | 高 | 030 |
| BroadcastReceiver ANR（前台 10s / 后台 60s） | 中高 | 030 |
| ContentProvider ANR（10s） | 中 | 030 |
| traces.txt 文件结构和关键字段 | 高 | 032 |
| DropBoxManager 取 traces 方案 | 高 | 033 |
| FileObserver 监听 /data/anr/ 方案 | 中高 | 033 |
| Looper 消息耗时监控（Printer 方案） | 中高 | 033 |
| Signal Handler（SIGQUIT）捕获方案 | 中 | 033 |
| 主线程 Binder 超时检测 | 中高 | 034 |
| 死锁导致 ANR 的分析方法 | 高 | 034 |
| WorkerThread 异常与 ANR 的区别 | 中 | 034 |

## 待补研究来源
- [ ] AOSP 源码：`frameworks/base/services/core/java/com/android/server/am/` 下 ANR 相关触发类
- [ ] Matrix（腾讯）和 BlockCanary 源码 — 线上监控方案
- [ ] 字节 ByteX / 抖音基础技术博客 — ANR 监控实战
- [ ] Android Developer 官方文档 ANR 部分

## 学习过程中的新发现

### 阶段 1 研究（2026-04-10）：030 ANR 原理

#### 来源 A：Android 官方 developer.android.com/topic/performance/vitals/anr
- ANR 定义：应用 UI 线程阻塞过长，前台应用会弹对话框
- 官方明确列出的超时：
  - **Input dispatching timed out: 5 秒**
  - `startForegroundService()` 后 5 秒内未调用 `startForeground()`
  - **BroadcastReceiver（前台）5 秒**（⚠️ 见下面分歧）
  - Service `onCreate/onStartCommand/onBind`：官方仅说"几秒"（未给具体值）
  - JobScheduler `onStartJob/onStopJob`：几秒
- 官方推荐诊断工具：Android vitals / Traceview / StrictMode / ApplicationExitInfo（API 30+）/ adb bugreport
- Play Console 坏行为阈值：整体 ≥0.47% DAU 感知 ANR；单设备 ≥8%

#### 来源 B：Gityuan gityuan.com/2016/07/02/android-anr
- 四类 ANR 完整超时表：

  | 类型 | 前台超时 | 后台超时 | 触发场景 |
  |------|--------|--------|--------|
  | Service | 20s | 200s | onCreate/onStartCommand 未完成 |
  | Broadcast | 10s | 60s | `onReceive` 执行超时 |
  | ContentProvider | 10s | - | Provider 发布超时（attach 阶段） |
  | Input | 5s | - | 输入事件分发超时 |

- 四类的**埋雷-拆雷-爆雷**源码路径（补齐现有初稿只覆盖 Service 的空白）：
  - **Service**：
    - 埋雷：`ActiveServices.realStartServiceLocked()` → `bumpServiceExecutingLocked()` → `scheduleServiceTimeoutLocked()` 发 `SERVICE_TIMEOUT_MSG`
    - 拆雷：`ActivityThread.handleCreateService()` → `serviceDoneExecuting()`
    - 爆雷：`MainHandler.handleMessage` → `AS.serviceTimeout()` → `appNotResponding()`
  - **Broadcast**：
    - 埋雷：`BroadcastQueue.processNextBroadcast()` → `setBroadcastTimeoutLocked()` 发 `BROADCAST_TIMEOUT_MSG`
    - 拆雷：`cancelBroadcastTimeoutLocked()`
    - 爆雷：`BroadcastHandler.handleMessage` → `broadcastTimeoutLocked()` → `AppNotResponding.run()`
  - **ContentProvider**：
    - 埋雷：`AMS.attachApplicationLocked()` 发 `CONTENT_PROVIDER_PUBLISH_TIMEOUT_MSG`
    - 拆雷：`AMS.publishContentProviders()`
    - 爆雷：`MainHandler` → `processContentProviderPublishTimedOutLocked()` → `removeProcessLocked()` **直接杀进程**（与 Service/Broadcast 弹对话框不同！）
  - **Input**（详见下方 Input ANR 专项）

- **为什么观测者必须在 system_server（不同进程）**：
  - 若在应用进程内，应用主线程卡顿时自身无法发起超时检测
  - AMS 运行在 system_server，拥有独立的 ActivityManager Handler 线程持续计时
  - 通过 Binder 跨进程验证应用响应状态

- **统一汇聚点**：Service/Broadcast 最终都汇聚到 `AMS.appNotResponding()` 收集信息 + 弹对话框；ContentProvider 走另一条路径直接杀进程

#### ⚠️ 分歧点处理：BroadcastReceiver 前台超时

| 来源 | 值 |
|------|---|
| 官方 developer.android.com | **5 秒**（前台） |
| Gityuan 2016 博客 | 10 秒（前台） |
| PERFORMANCE_AV.md §4 | 10 秒（前台） |

**决策（用户选项 c）**：**采用官方文档的 5 秒**。Gityuan 和 PERFORMANCE_AV 的 10s 可能是旧版本 AOSP 的值，官方文档是最新权威来源。

**面试答题策略**：
- 前台：**5 秒**（基于最新官方文档）
- 后台：**60 秒**（Gityuan 值，官方未列明后台时间）
- 补一句"历史版本前台为 10s，近年官方调整为 5s"作为展示深度的补充

#### Input ANR 专项（来源 C：gityuan.com/2017/01/01/input-anr）

**超时计时起点**：从事件的 `eventTime`（事件产生时刻）开始计时，**不是**从分发开始。
- `dispatchLatency = (currentTime - eventTime) * 0.000001f`
- `waitDuration = (currentTime - waitStartTime) * 0.000001f`

**完整调用链**（InputDispatcher 线程）：
```
dispatchOnce()
  → dispatchOnceInnerLocked()                    [生成 DispatchEntry 入 outboundQueue]
  → findFocusedWindowTargetsLocked()             [埋雷：记录 ANR 时间点]
  → handleTargetsNotReadyLocked()                [检测超时 5s]
  → onANRLocked()                                [拆雷：命令加入 mCommandQueue]
  → runCommandsLockedInterruptible()             [爆雷：执行 ANR 命令]
  → doNotifyANRLockedInterruptible()
  → NativeInputManager::notifyANR()              [JNI 过桥]
  → InputManagerService.notifyANR()              [Java 层]
  → InputMonitor.notifyANR()
  → AMS.inputDispatchingTimedOut()
  → appNotResponding()                            [最终汇聚点]
```

**Input 事件的三层队列**：
| 队列 | 位置 | 作用 |
|------|------|------|
| `mInboundQueue` | InputDispatcher | InputReader → InputDispatcher 的原始事件入口 |
| `outboundQueue` | Connection | 待发往应用的 DispatchEntry |
| `waitQueue` | Connection | 已发送但未收到 `finishInputEvent()` 确认的事件 |

**无响应检测的三种判定**：
1. `outboundQueue` 拥堵："Waiting because the [targetType] window's input channel is full"
2. **非按键事件**等待队列头部超过 500ms（预警阈值，非 ANR 阈值）
3. **按键事件**：outboundQueue 或 waitQueue 不为空即判定

**Input ANR 的埋雷-拆雷-爆雷**：
| 阶段 | 方法 | 说明 |
|------|------|------|
| 埋雷 | `findFocusedWindowTargetsLocked()` | 记录 eventTime 作为计时起点 |
| 拆雷 | `handleTargetsNotReadyLocked() + onANRLocked()` | 检测到 5s 超时，生成 ANR 命令入队 |
| 爆雷 | `doNotifyANRLockedInterruptible()` | 在下一轮 `dispatchOnce` 执行 |

**与 Service/Broadcast 的三大差异**：
1. **Handler 不同**：Input 走 InputDispatcher 自己的 Looper + `mCommandQueue`；Service/Broadcast 走 AMS Handler
2. **计时起点不同**：Input 从事件产生时刻计时；Service/Broadcast 从开始处理时计时
3. **处理时机不同**：Input 的 ANR 命令要等下一轮 `dispatchOnce` 才执行；Service/Broadcast 的延时消息到点立即触发

**为什么 Input 独立走 InputDispatcher 而不复用 AMS Handler**：
- Input 事件时间敏感性极高（用户感知），必须独立线程实时监测
- InputDispatcher 是 Framework 层输入分发中枢，无需走 AMS 重型流程
- 命令队列机制保证顺序执行且开销小

**`resetANRTimeoutsLocked()` 的 5 个重置时机**：
- `resetAndDropEverythingLocked`（系统冻结）
- `releasePendingEventLocked`（释放待处理事件）
- `setFocusedApplication`（焦点应用变更）
- `dispatchOnceInnerLocked`（下一轮分发开始）
- `setInputDispatchMode`（分发模式变更）

**汇聚点总结**（所有 ANR 最终都走 `appNotResponding()`，除 Provider 异类）：
```
Service    ─┐
Broadcast  ─┼→ AMS.appNotResponding() → 弹对话框
Input      ─┘
Provider   → removeProcessLocked()    → 直接杀进程（不弹框）
```

#### 阶段 1 笔记要落地的要点清单
- [ ] 补 `ANR_01.基础概念.md` 新增 §2.5 四类 ANR 触发对比（表格 + 超时值 + 对应 AOSP 类/方法）
- [ ] 新增 §2.6 为什么观测者在 system_server（跨进程/跨线程）
- [ ] 新增 §2.7 埋雷-拆雷-爆雷在四类 ANR 中的共性与差异（Provider 直接杀进程是异类）
- [ ] 新增 §2.8 Input ANR 专项：InputDispatcher 独立 Looper + 三层队列 + 计时起点差异
- [ ] 采用官方 5s 作为 Broadcast 前台超时值，注记历史 10s 值作为深度补充

---

# Findings — 启动流程精读（启动优化_03.启动流程.md）

## 文件概况（2026-04-20）
- 总行数：1030 行，16 个阶段，7 章节
- 质量分级：阶段 1-12 已推导校准（高可信），阶段 13-16 标注 [未推导]（需对话校准）

## [未推导] 节点清单
需要通过对话推导校准后删除标签：
- §二 阶段 13：ViewRootImpl 介入（onResume 返回后 → WindowManager.addView → requestLayout）
- §二 阶段 14：Choreographer + vsync 机制
- §二 阶段 15：performTraversals（measure/layout/draw）
- §二 阶段 16：RenderThread + SurfaceFlinger + 首帧上屏

## 11 个易错校准点速查
| 编号 | 核心结论 |
|------|---------|
| 校准 1 | fork 返回值：0=子进程（新生儿），>0=父进程持有的子 pid |
| 校准 2 | 代理在调用方，本体在被调用方 |
| 校准 3 | ApplicationThread 在 `new ActivityThread()` 构造时创建，不是 attach 时 |
| 校准 4 | `bindApplication`=AMS 下发指令；`Application.onCreate`=其中最后一个子步骤 |
| 校准 5 | ActivityThread / ApplicationThread 都不是线程 |
| 校准 6 | onResume 返回 ≠ 启动完成，还要等 measure→draw→RenderThread→SurfaceFlinger |
| 校准 7 | setContentView 不跑 measure，view.width 在 onCreate/onResume 里永远是 0 |
| 校准 8 | onCreate/onStart/onResume 同一条消息处理，中间 Looper 不取新消息 |
| 校准 9 | 四大组件+Application 必须有无参构造（系统反射创建） |
| 校准 10 | ContentProvider.onCreate 先于 Application.onCreate，串行在主线程 |
| 校准 11 | 用户点击后看到的是 Starting Window，不是你的 Activity |

## 启动优化关键切入点
来自 §六 优化切入表：
- ★ ContentProvider.onCreate（主线程串行）= 启动优化第一金矿
- Starting Window 主题 = 感知性能最便宜的优化（改 XML 一个属性）
- App Startup 的价值是"合并 Provider"，不是让启动更快
- setContentView inflate 层级过深 = 主线程耗时大头之一
