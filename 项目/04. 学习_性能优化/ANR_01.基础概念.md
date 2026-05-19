[toc]

## 前言

> 学习要符合如下的标准化链条：了解概念->探究原理->深入思考->总结提炼->底层实现->延伸应用"

## 01.学习概述

- **学习主题**：
- **知识类型**：
  - [ ] ✅Android/ 
    - [ ] ✅01.基础组件与机制 
      - [ ] ✅四大组件
      - [ ] ✅IPC机制
      - [ ] ✅消息机制
      - [ ] ✅事件分发机制
      - [ ] ✅View与渲染体系（含Window、复杂控件、动画）
      - [ ] ✅存储与数据安全（SharedPreferences/DataStore/Room/Scoped Storage）
    - [ ] ✅02. 架构与工程化
      - [ ] ✅架构模式（MVC/MVP/MVVM/MVI）
      - [ ] ✅依赖注入（Koin/Hilt/Dagger）
      - [ ] ✅路由与模块化（ARouter、Navigation）
      - [ ] ✅Gradle与构建优化
      - [ ] ✅插件化与动态化
      - [ ] ✅插桩与监控框架
    - [ ] ✅03.性能优化与故障诊断
      - [ ] ✅ANR分析与优化
      - [ ] ✅启动耗时优化
      - [ ] ✅内存泄漏监控
      - [ ] ✅监控与诊断工具
    - [ ] ✅04.Jetpack与生态框架
      - [ ] ✅Room
      - [ ] ✅Paging
      - [ ] ✅WorkManager
      - [ ] ✅Compose
    - [ ] ✅05.Framework与系统机制
      - [ ] ✅ActivityManagerService (含ANR触发机制)
      - [ ] ✅Binder机制
  - [ ] ✅音视频开发/
    - [ ] ✅01.基础知识
    - [ ] ✅02.OpenGL渲染视频
    - [ ] ✅03.FFmpeg音视频解码
  - [ ] ✅ Java/
    - [ ] ✅01.基础知识
    - [ ] ✅02.集合框架
    - [ ] ✅03.异常处理
    - [ ] ✅04.多线程与并发
    - [ ] ✅06.JVM
  - [ ] ✅ Kotlin/
    - [ ] ✅01.基础语法
    - [ ] ✅02.高阶扩展
    - [ ] ✅03.协程和流
  - [ ] ✅ Flutter/
    - [ ] ✅01.基础知识
      - [ ] ✅Dart 语言基础
      - [ ] ✅Widget 基础与生命周期
      - [ ] ✅Flutter 基础组件
      - [ ] ✅布局与约束
      - [ ] ✅绘制与渲染体系
      - [ ] ✅状态管理
      - [ ] ✅事件处理与手势系统
      - [ ] ✅原生通信
    - [ ] ✅02.路由与导航
    - [ ] ✅03.性能优化与故障诊断
    - [ ] ✅04.异步编程
    - [ ] ✅05.项目经验与案例沉淀
  - [ ] ✅ 自我管理/
    - [ ] ✅01.内观
  - [ ] ✅ 项目经验/
    - [ ] ✅01.启动逻辑
    - [ ] ✅02.云值守
    - [ ] ✅03.智控平台
    - [ ] ✅04.视频巡店
- **学习来源**：
- **重要程度**：⭐⭐⭐⭐⭐
- **学习日期**：2025.
- **记录人**：@panruiqi

### 1.1 学习目标

- 了解概念->探究原理->深入思考->总结提炼->底层实现->延伸应用"

### 1.2 前置知识

- [ ] 

## 02.核心概念

### 2.1 ANR 是什么？

ANR = Application Not Responding（应用无响应）

简单说：系统给你的代码设定了一个执行时间限制，超时了就认为你"卡死"了。

有一个很形象的生活场景可以帮助我们理解这个：

- ```
  角色：
  - 老师（观测者）
  - 学生（被观测者）
  - 作业（任务）
  - 10分钟（超时时间）
  
  流程：
  1. 老师布置作业，说"10分钟后我来检查"
  2. 老师设了个闹钟，10分钟后响
  3. 学生开始写作业
  4. 情况A：学生5分钟写完了 → 主动告诉老师 → 老师取消闹钟
  5. 情况B：闹钟响了，学生还没写完 → 老师记名字（惩罚）
  
  ```


### 2.2 埋雷-拆雷-爆雷模型

ANR的本质就是埋雷-拆雷-爆雷模型

- | 步骤 | 含义                           | 对应操作                                      |
  | ---- | ------------------------------ | --------------------------------------------- |
  | 埋雷 | 开始计时，设置一个延时检测任务 | 发送一个延时 Message 到主线程消息队列         |
  | 拆雷 | 任务完成，取消检测             | 从主线程消息队列中移除该延时 Message          |
  | 爆雷 | 超时了，检测任务被触发         | 延时 Message 被执行，判定主线程阻塞，上报 ANR |

### 2.3 为什么观测者和被观测者必须在不同线程

如果老师和学生是同一个人（同一个线程）：

- ```
  // 单线程版本
  void 检测任务() {
      设置闹钟(10秒后检查)  // 1. 埋雷
      执行任务()            // 2. 如果这里死循环...
      取消闹钟()            // 3. 永远执行不到！
  }
  ```

问题在于：如果"执行任务"陷入死循环，那么"取消闹钟"永远不会执行，但"闹钟响"也永远不会执行，因为它们在同一个线程的消息队列里排队！

- ```
  消息队列：[执行任务(死循环)] → [闹钟响] → ...
                  ↑
              卡在这里，后面的消息永远处理不到
  ```

所以 ANR 的设计必须满足：观测者和被观测者在不同的线程（甚至不同的进程）。

### 2.4 ANR的整体流程

关键理解：ANR 检测是 system_server 对 App 进程的监控，不是 App 内部的自我监控。

整体流程如下：

- ```
  时序：
  ┌─────────────────────────────────────────────────────────┐
  │  观测者A（system_server）                                │
  │                                                         │
  │  1. 埋雷（自己给自己发一个延时消息）                       │
  │  2. 调用B去执行任务 ──────────────────→                  │
  │  3. 等待...                            │                │
  │  4. 收到B的完成通知 ←──────────────────┼────            │
  │  5. 拆雷（移除延时消息）                │    │           │
  │                                        │    │           │
  │  如果第4步没发生，延时消息就会触发：     │    │           │
  │  → 爆雷（检测ANR）                      │    │           │
  └────────────────────────────────────────┼────┼───────────┘
                                           │    │
                                           ↓    │
  ┌────────────────────────────────────────────────────────┐
  │  被观测者B（App进程）                       │           │
  │                                            │           │
  │  收到调用 ←─────────────────────────────────           │
  │  执行任务...                                           │
  │  完成后通知A ──────────────────────────────────────────│
  └────────────────────────────────────────────────────────┘
  ```

## 03.源码分析_埋雷过程

### 3.1 整体流程

当你在 App 中调用 context.startService(intent) 时，这个调用会经历一段旅程：

关键点：startService 的调用最终会跨进程到达 system_server，在那里进行 ANR 检测的"埋雷"。

```
你的 App 进程                              system_server 进程
     │                                           │
     │  context.startService(intent)             │
     │                                           │
     ▼                                           │
ContextImpl.startService()                       │
     │                                           │
     ▼                                           │
ActivityManager.getService()                     │
     .startService(...)                          │
     │                                           │
     │ ═══════ Binder IPC ═══════════════════════▶
     │                                           │
     │                              ActivityManagerService
     │                                    .startService()
     │                                           │
     │                                           ▼
     │                              ActiveServices
     │                                    .startServiceLocked()
     │                                           │
     │                                           ▼
     │                              ActiveServices
     │                                    .realStartServiceLocked()
     │                                           │
     │                                    ┌──────┴──────┐
     │                                    │   埋雷！    │
     │                                    └─────────────┘

```

### 3.2 入口函数：realStartServiceLocked()

#### 1.入口方法

这是埋雷的入口，位于 ActiveServices 类中（这个类在 system_server 进程里）：

- ```
  private final void realStartServiceLocked(
          ServiceRecord r,      // 要启动的 Service 的记录
          ProcessRecord app,    // Service 所属的进程
          boolean execInFg      // 是否是前台执行
  ) throws RemoteException {
      
      // ══════════════════════════════════════════════════════════
      // 第一步：埋雷
      // ══════════════════════════════════════════════════════════
      bumpServiceExecutingLocked(r, execInFg, "create");
      
      try {
          // ══════════════════════════════════════════════════════
          // 第二步：跨进程调用 App 去创建 Service
          // ══════════════════════════════════════════════════════
          app.thread.scheduleCreateService(
              r,                           // ServiceRecord
              r.serviceInfo,               // ServiceInfo
              mAm.compatibilityInfoForPackage(r.serviceInfo.applicationInfo),
              app.getReportedProcState()
          );
      } catch (DeadObjectException e) {
          throw e;
      }
  }
  
  ```

#### 2.代码执行顺序

这段代码的执行顺序很重要！

```
时间线：
────────────────────────────────────────────────────────────────►

    │                    │                              │
    ▼                    ▼                              ▼
 埋雷完成            Binder调用发出              App收到调用
(定时器启动)        (通知App创建Service)         (开始执行onCreate)

    ├────────────────────┼──────────────────────────────┤
    │      这段时间       │         这段时间              │
    │   几乎是瞬间完成    │    取决于App的执行速度         │

```

为什么要先埋雷再调用？

- 假如先调用再埋雷，如果 scheduleCreateService 这个 Binder 调用本身就卡住了（比如 App 进程已经卡死），那么 bumpServiceExecutingLocked 永远不会执行，雷就埋不上了！

### 3.3 埋雷的核心：bumpServiceExecutingLocked()

```
private final void bumpServiceExecutingLocked(
        ServiceRecord r,    // 要启动的 Service
        boolean fg,         // 是否前台
        String why          // 原因（用于调试日志）
) {
    // ... 省略一些日志和统计代码 ...
    
    // ══════════════════════════════════════════════════════════
    // 关键操作1：记录开始时间
    // ══════════════════════════════════════════════════════════
    long now = SystemClock.uptimeMillis();
    if (r.executeNesting == 0) {
        r.executingStart = now;  // 记录这个 Service 开始执行的时间戳
    }
    
    // ══════════════════════════════════════════════════════════
    // 关键操作2：将 Service 加入"正在执行"集合
    // ══════════════════════════════════════════════════════════
    r.app.executingServices.add(r);
    
    // ══════════════════════════════════════════════════════════
    // 关键操作3：启动定时检测
    // ══════════════════════════════════════════════════════════
    scheduleServiceTimeoutLocked(r.app);
    
    // ... 省略其他代码 ...
}
```

这里有三个关键操作

#### 1.记录开始时间

```
if (r.executeNesting == 0) {
    r.executingStart = now;
}
```

executeNesting 是什么？

- 这是一个嵌套计数器。一个 Service 可能会被多次"执行"：
  - onCreate() 是一次执行
  - onStartCommand() 是一次执行
  - onBind() 是一次执行

- ```
  class ServiceRecord {
      int executeNesting;    // 嵌套层数
      long executingStart;   // 开始时间（只在第一次进入时记录）
  }
  ```

为什么这样设计？

- ANR 检测的是"从第一次开始到现在的总时间"，而不是"每次操作的单独时间"。通过这个确保只记录第一次操作的时间，不进行覆写更新

- ```
  场景：连续调用 startService 两次
  
  第一次 startService:
    executeNesting: 0 → 1
    executingStart = now  ← 记录时间
  
  第二次 startService（第一次还没完成）:
    executeNesting: 1 → 2
    executingStart 不变  ← 保持第一次的时间
  
  第一次完成:
    executeNesting: 2 → 1
    
  第二次完成:
    executeNesting: 1 → 0
  ```

#### 2.加入 executingServices 集合

```
r.app.executingServices.add(r);
```

这里涉及两个数据结构：

- ```
  // ServiceRecord：代表一个 Service
  class ServiceRecord extends Binder {
      ProcessRecord app;        // 所属进程
      long executingStart;      // 开始执行时间
      int executeNesting;       // 嵌套计数
      ComponentName name;       // Service 的类名
      // ...
  }
  
  // ProcessRecord：代表一个进程
  class ProcessRecord {
      IApplicationThread thread;  // 与 App 进程通信的 Binder 接口
      
      // 这个进程中正在执行的所有 Service
      final ArraySet<ServiceRecord> executingServices = new ArraySet<>();
      
      // 是否有前台服务在执行
      boolean execServicesFg;
      // ...
  }
  
  ```

#### 3. 启动定时检测

这是埋炸弹的核心了，发送一个延时消息

- ```
  void scheduleServiceTimeoutLocked(ProcessRecord proc) {
      // 防御性检查：如果没有正在执行的服务，或者进程已死，就不需要检测
      if (proc.executingServices.size() == 0 || proc.thread == null) {
          return;
      }
      
      // 构建消息
      Message msg = mAm.mHandler.obtainMessage(
          ActivityManagerService.SERVICE_TIMEOUT_MSG  // 消息类型
      );
      msg.obj = proc;  // 携带 ProcessRecord
      
      // 发送延时消息
      mAm.mHandler.sendMessageDelayed(
              msg,
          proc.execServicesFg ? SERVICE_TIMEOUT : SERVICE_BACKGROUND_TIMEOUT
      );
  }
  
  // 超时时间常量
  static final int SERVICE_TIMEOUT = 20 * 1000;            // 前台：20秒
  static final int SERVICE_BACKGROUND_TIMEOUT = 200 * 1000; // 后台：200秒
  
  ```

这里有几个细节

- 细节1：为什么前台 20s，后台 200s？

  - 前台服务：用户可见，卡顿会被用户感知，所以要求更严格
  - 后台服务：用户不可见，可以给更多时间执行

- 细节2：mAm.mHandler 是什么？

  - 这个 Handler 运行在 system_server 进程的主线程，所有的 ANR 检测都在这里触发。

  - ```
    // 在 ActivityManagerService 中
    final MainHandler mHandler;
    
    class MainHandler extends Handler {
        public MainHandler(Looper looper) {
            super(looper, null, true);  // 运行在 system_server 的主线程
        }
        
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case SERVICE_TIMEOUT_MSG:
                    // 爆雷！
                    mServices.serviceTimeout((ProcessRecord) msg.obj);
                    break;
                // ... 其他消息处理
            }
        }
    }
    
    ```

- 细节3：如果连续启动多个 Service 会怎样？

  - ```
    // 第一个 Service 启动
    scheduleServiceTimeoutLocked(proc);  // 发送消息1，20s后触发
    
    // 第二个 Service 启动（假设在 5s 后）
    scheduleServiceTimeoutLocked(proc);  // 发送消息2，20s后触发
    ```

  - 会导致消息队列里有多个 SERVICE_TIMEOUT_MSG：

  - ```
    消息队列：
    [消息1: T=20触发] [消息2: T=25触发] ...
    ```

### 3.4 埋雷过程的完整时序图

```
system_server 进程                              App 进程
      │                                            │
      │  realStartServiceLocked()                  │
      │         │                                  │
      │         ▼                                  │
      │  bumpServiceExecutingLocked()              │
      │         │                                  │
      │         ├─► r.executingStart = now         │
      │         │   (记录开始时间)                  │
      │         │                                  │
      │         ├─► executingServices.add(r)       │
      │         │   (加入集合)                      │
      │         │                                  │
      │         ├─► scheduleServiceTimeoutLocked() │
      │         │         │                        │
      │         │         ▼                        │
      │         │   handler.sendMessageDelayed()   │
      │         │   (20s后触发检测)                 │
      │         │                                  │
      │  ◄──────┘                                  │
      │                                            │
      │  app.thread.scheduleCreateService() ═══════▶
      │  (Binder调用，通知App创建Service)           │
      │                                            │
      │                                            ▼
      │                                   handleCreateService()
      │                                            │
      │                                            ▼
      │                                   service.onCreate()
      │                                   (你的代码在这里执行)
      │                                            │
      │                                            │
      ▼                                            │
 ┌─────────────────┐                               │
 │ 20s 定时器等待中 │                               │
 └─────────────────┘                               │
      │                                            │
      │  如果 App 在 20s 内完成 ◄══════════════════│
      │  → 拆雷（下一讲）                           │
      │                                            │
      │  如果 App 超过 20s 还没完成                 │
      │  → 爆雷（第四讲）                           │

```

## 04.源码分析_拆雷过程

### 4.1 回顾：雷埋在哪里了？

在上一讲中，我们知道埋雷做了三件事：

```
// 在 system_server 进程中
r.executingStart = now;              // 1. 记录开始时间
r.app.executingServices.add(r);      // 2. 加入集合（标记）
handler.sendMessageDelayed(msg, 20s); // 3. 启动定时器（雷）
```

所以拆雷需要做的就是逆向操作：

- 从集合中移除
- 取消定时器

但问题是：谁来触发拆雷？从哪里触发？是应用进程发送msg到system_server进程的msgqueue中吗？

### 4.2 整体流程

让我们跟踪 Service 创建的完整流程：

```
system_server 进程                              App 进程
      │                                            │
      │  埋雷完成                                   │
      │                                            │
      │  app.thread.scheduleCreateService() ═══════▶
      │                                            │
      │                                   ApplicationThread
      │                                     .scheduleCreateService()
      │                                            │
      │                                            ▼
      │                                   sendMessage(H.CREATE_SERVICE)
      │                                            │
      │                                            ▼
      │                                   H.handleMessage()
      │                                            │
      │                                            ▼
      │                                   ActivityThread
      │                                     .handleCreateService()
      │                                            │
      │                                   ┌────────┴────────┐
      │                                   │ 你的代码在这里！ │
      │                                   │ service.onCreate()│
      │                                   └────────┬────────┘
      │                                            │
      │                                            ▼
      │  ◄═══════════════════════════════ serviceDoneExecuting()
      │                                   (Binder回调，通知完成)
      │                                            │
      │  拆雷！                                     │
      │                                            │

```

关键：所以拆雷就是通过Binder回调，让system_server进程自己处理

### 4.3 APP端_handleCreateService()

这是 App 进程中处理 Service 创建的代码，位于 ActivityThread 类：关键就是调用service的onCreate，处理完后再执行Binder调用

```
private void handleCreateService(CreateServiceData data) {
    // ══════════════════════════════════════════════════════════
    // 第一步：准备工作
    // ══════════════════════════════════════════════════════════
    
    // 暂停 GC，避免创建过程中被 GC 打断
    unscheduleGcIdler();
    
    // 获取 APK 信息
    LoadedApk packageInfo = getPackageInfoNoCheck(
        data.info.applicationInfo, 
        data.compatInfo
    );
    
    Service service = null;
    
    try {
        // ══════════════════════════════════════════════════════
        // 第二步：通过反射创建 Service 实例
        // ══════════════════════════════════════════════════════
        
        // 创建 Context
        ContextImpl context = ContextImpl.createAppContext(this, packageInfo);
        
        // 获取或创建 Application
        Application app = packageInfo.makeApplication(false, mInstrumentation);
        
        // 获取 ClassLoader
        java.lang.ClassLoader cl = packageInfo.getClassLoader();
        
        // 反射创建 Service 实例！
        service = packageInfo.getAppFactory()
            .instantiateService(cl, data.info.name, data.intent);
        
        // ══════════════════════════════════════════════════════
        // 第三步：初始化 Service
        // ══════════════════════════════════════════════════════
        
        context.setOuterContext(service);
        
        // 调用 service.attach()，保存 context 等信息
        service.attach(
            context, 
            this,                           // ActivityThread
            data.info.name,                 // Service 类名
            data.token,                     // IBinder token
            app,                            // Application
            ActivityManager.getService()    // AMS 的 Binder 代理
        );
        
        // ══════════════════════════════════════════════════════
        // 第四步：回调 onCreate()
        // 这里就是你写的代码执行的地方！
        // ══════════════════════════════════════════════════════
        service.onCreate();
        
        // 保存到本地的 Service 列表
        mServices.put(data.token, service);
        
        // ══════════════════════════════════════════════════════
        // 第五步：通知 system_server 完成了！（拆雷的触发点）
        // ══════════════════════════════════════════════════════
        try {
            ActivityManager.getService().serviceDoneExecuting(
                data.token,                    // Service 的 token
                SERVICE_DONE_EXECUTING_ANON,   // 完成类型
                0,                             // startId
                0                              // res
            );
        } catch (RemoteException e) {
            throw e.rethrowFromSystemServer();
        }
        
    } catch (Exception e) {
        // 异常处理...
    }
}

```

这里有两个关键点

- onCreate() 在 serviceDoneExecuting() 之前

  - ```
    service.onCreate();                    // 先执行你的代码
    // ...
    ActivityManager.getService()
        .serviceDoneExecuting(...);        // 再通知 system_server
    ```

  - 这意味着：如果你的 onCreate() 卡住了，serviceDoneExecuting() 就永远不会被调用，雷就拆不掉

- serviceDoneExecuting 是一个 Binder 调用

  - ```
    ActivityManager.getService()  // 获取 AMS 的 Binder 代理
        .serviceDoneExecuting(...);  // 跨进程调用
    ```

  - 这个调用会从 App 进程跨越到 system_server 进程。

### 4.4  system_server 端：serviceDoneExecuting()

现在我们进入 system_server 进程，看看收到完成通知后做了什么。

#### 1. 入口：ActivityManagerService.serviceDoneExecuting()

```
// 在 ActivityManagerService 中
public void serviceDoneExecuting(
        IBinder token,    // Service 的标识
        int type,         // 完成类型
        int startId,      // 
        int res           // 
) {
    synchronized (this) {
        // ... 权限检查等 ...
        
        // 调用 ActiveServices 处理
        mServices.serviceDoneExecutingLocked(
            (ServiceRecord) token, 
            type, 
            startId, 
            res
        );
    }
}
```

#### 2. 核心：ActiveServices.serviceDoneExecutingLocked()

```
void serviceDoneExecutingLocked(
        ServiceRecord r, 
        int type, 
        int startId, 
        int res
) {
    // 检查是否正在被销毁
    boolean inDestroying = mDestroyingServices.contains(r);
    
    if (r != null) {
        // 根据不同的完成类型做不同处理
        if (type == ActivityThread.SERVICE_DONE_EXECUTING_START) {
            // onStartCommand 完成
            // ... 处理 startId 和返回值 ...
        } else if (type == ActivityThread.SERVICE_DONE_EXECUTING_STOP) {
            // onDestroy 完成
            // ... 清理工作 ...
        }
        
        // ══════════════════════════════════════════════════════
        // 关键：调用真正的拆雷函数
        // ══════════════════════════════════════════════════════
        serviceDoneExecutingLocked(r, inDestroying, inDestroying);
        
    } else {
        // ServiceRecord 为空，记录警告日志
        Slog.w(TAG, "Done executing unknown service...");
    }
}

```

#### 3. 真正的拆雷：serviceDoneExecutingLocked() 重载版本

```
private void serviceDoneExecutingLocked(
        ServiceRecord r, 
        boolean inDestroying, 
        boolean finishing
) {
    // ══════════════════════════════════════════════════════════
    // 关键操作1：减少嵌套计数
    // ══════════════════════════════════════════════════════════
    r.executeNesting--;
    
    if (r.executeNesting <= 0) {
        // 嵌套计数归零，说明这个 Service 的所有操作都完成了
        
        if (r.app != null) {
            // ══════════════════════════════════════════════════
            // 关键操作2：更新前台服务标记
            // ══════════════════════════════════════════════════
            if (r.app.executingServices.size() == 0) {
                // 如果没有其他正在执行的服务了
                r.app.execServicesFg = false;
            }
            
            // ══════════════════════════════════════════════════
            // 关键操作3：从集合中移除（拆标记）
            // ══════════════════════════════════════════════════
            r.app.executingServices.remove(r);
            
            // ══════════════════════════════════════════════════
            // 关键操作4：尝试移除定时器（拆雷）
            // ══════════════════════════════════════════════════
            if (r.app.executingServices.size() == 0) {
                // 只有当没有任何 Service 在执行时，才移除定时器
                mAm.mHandler.removeMessages(
                    ActivityManagerService.SERVICE_TIMEOUT_MSG, 
                    r.app
                );
            } else if (r.executeFg) {
                // 如果还有其他 Service 在执行，
                // 但当前完成的是前台服务，需要重新评估
                // ... 更新前台服务状态 ...
            }
            
            // ══════════════════════════════════════════════════
            // 关键操作5：更新进程优先级
            // ══════════════════════════════════════════════════
            if (inDestroying) {
                // 如果 Service 正在销毁，从销毁列表中移除
                mDestroyingServices.remove(r);
            }
            
            // 更新进程的 OOM adj 值（影响进程被杀的优先级）
            mAm.updateOomAdjLocked(r.app, true);
        }
        
        // 重置执行开始时间
        r.executingStart = 0;
    }
}
```

### 4.5 深入分析：为什么只在 size() == 0 时才移除炸弹？

这是文章中提到的一个设计细节，让我们深入理解：

- ```
  if (r.app.executingServices.size() == 0) {
      mAm.mHandler.removeMessages(SERVICE_TIMEOUT_MSG, r.app);
  }
  ```

- 大家会不会好奇一点：如果只有在size() == 0 时才移除炸弹，那加入有M1 和 M2两个service。我们M1处理完了，但是代码逻辑不移除M1。这不会导致M1的炸弹被触发，产生ANR吗？

场景分析

- 假设一个进程同时启动了两个 Service：
  - ```
    时间线：
    T=0:  启动 Service1
          - executingServices = {S1}
          - 发送定时消息 M1（T=20 触发）
    
    T=5:  启动 Service2
          - executingServices = {S1, S2}
          - 发送定时消息 M2（T=25 触发）
    
    T=10: Service1 完成
          - executingServices.remove(S1) → {S2}
          - size() == 1，不是 0
          - 不移除定时消息！
    
    T=15: Service2 完成
          - executingServices.remove(S2) → {}
          - size() == 0
          - 移除所有 SERVICE_TIMEOUT_MSG 消息（M1 和 M2 都被移除）
    
    ```

为什么不能在 Service1 完成时就移除 M1？

- 问题在于 removeMessages 的实现：

  - ```
    // Handler.removeMessages 的签名
    public final void removeMessages(int what, Object object)
    ```

- 它会移除所有满足条件的消息：

  - what == SERVICE_TIMEOUT_MSG
  - object == r.app（ProcessRecord）

- 因为 M1 和 M2 的 object 都是同一个 ProcessRecord，所以会同时移除

  - ```
    // 如果在 Service1 完成时调用
    mAm.mHandler.removeMessages(SERVICE_TIMEOUT_MSG, r.app);
    // 会同时移除 M1 和 M2！
    // 这样 Service2 的 ANR 检测就失效了！
    ```

那么他不会触发ANR吗？因为我们会最终执行到M1消息啊

- 其实执行到M1消息不代表ANR，他还要去集合中找到service A，也就是M1炸弹对应的service才行。

- 而我们这里移除了service

  - ```
      // ══════════════════════════════════════════════════
                // 关键操作3：从集合中移除（拆标记）
                // ══════════════════════════════════════════════════
                r.app.executingServices.remove(r);
    ```

看看完整的图解

- 回答上面的问题：M1会被触发，但是因为集合中没有A，所以不会触发ANR。

- ```
  T=0:  启动 Service A
        集合：{A}
        消息：[M1(proc) @T=20]
  
  T=5:  启动 Service B
        集合：{A, B}
        消息：[M1(proc) @T=20] [M2(proc) @T=25]
  
  T=10: A 完成
        集合：{B}              ← A 从集合移除
        消息：[M1(proc) @T=20] [M2(proc) @T=25]  ← 消息没动！
        
        为什么不移除 M1？
        因为 size() == 1，不是 0
        而且 removeMessages(MSG, proc) 会把 M1 和 M2 都删掉！
  
  T=20: M1 触发，执行 serviceTimeout(proc)
        遍历 executingServices = {B}
        检查 B.executingStart = 5
        maxTime = 20 - 20 = 0
        5 > 0，B 没超时
        → 没有 ANR，"检测了个寂寞"
  
  T=22: B 完成
        集合：{}               ← B 从集合移除
        消息：[M2(proc) @T=25] ← 还有一个消息
        
        size() == 0，执行 removeMessages(MSG, proc)
        消息：[]               ← M2 被移除了！
  
  T=25: M2 本该触发，但已经被移除了，什么都不会发生
  
  ```

### 4.6 拆雷过程的完整时序图

```
App 进程                                    system_server 进程
    │                                              │
    │  handleCreateService()                       │
    │         │                                    │
    │         ▼                                    │
    │  反射创建 Service                             │
    │         │                                    │
    │         ▼                                    │
    │  service.attach()                            │
    │         │                                    │
    │         ▼                                    │
    │  service.onCreate()                          │
    │  ┌──────────────────┐                        │
    │  │ 你的代码在这里执行 │                        │
    │  │ 如果这里卡住...   │                        │
    │  │ 雷就拆不掉！      │                        │
    │  └──────────────────┘                        │
    │         │                                    │
    │         ▼                                    │
    │  mServices.put(token, service)               │
    │         │                                    │
    │         ▼                                    │
    │  ActivityManager.getService()                │
    │    .serviceDoneExecuting() ══════════════════▶
    │                                              │
    │                              serviceDoneExecutingLocked()
    │                                       │
    │                                       ▼
    │                              r.executeNesting--
    │                                       │
    │                              if (executeNesting <= 0)
    │                                       │
    │                                       ▼
    │                              executingServices.remove(r)
    │                              (从集合中移除)
    │                                       │
    │                              if (size() == 0)
    │                                       │
    │                                       ▼
    │                              removeMessages(SERVICE_TIMEOUT_MSG)
    │                              (移除定时器，拆雷完成！)
    │                                       │
    │                                       ▼
    │                              updateOomAdjLocked()
    │                              (更新进程优先级)
    │                                       │
    ◄══════════════════════════════════════════════
    │  Binder 调用返回                        │
    │                                        │

```

## 05.源码分析_爆雷过程

### 5.1 回顾：雷是什么？

在第03.中，我们埋下了这个雷：

```
Message msg = mAm.mHandler.obtainMessage(SERVICE_TIMEOUT_MSG);
msg.obj = proc;  // ProcessRecord
mAm.mHandler.sendMessageDelayed(msg, 20000);  // 20秒后触发
```

20 秒后，如果这个消息没有被移除，它就会被 Handler 处理。

### 5.2 爆雷的入口：MainHandler.handleMessage()

```
// 在 ActivityManagerService 中
final class MainHandler extends Handler {
    
    @Override
    public void handleMessage(Message msg) {
        switch (msg.what) {
            
            case SERVICE_TIMEOUT_MSG: {
                // ══════════════════════════════════════════════
                // 爆雷！调用 serviceTimeout 进行检测
                // ══════════════════════════════════════════════
                mServices.serviceTimeout((ProcessRecord) msg.obj);
            } break;
            
            // ... 其他消息类型 ...
        }
    }
}

```

这里很简单，就是把 ProcessRecord 取出来，交给 ActiveServices.serviceTimeout() 处理。

### 5.3 核心检测逻辑：serviceTimeout()

这是爆雷的核心函数，让我们逐段分析：

#### 1.Debug中忽略ANR

```
void serviceTimeout(ProcessRecord proc) {
    String anrMessage = null;  // ANR 消息，如果不为 null 说明发生了 ANR
    
    synchronized(mAm) {
        // ══════════════════════════════════════════════════════════
        // 第一步：防御性检查
        // ══════════════════════════════════════════════════════════
        
        // 检查1：如果进程正在被调试，忽略 ANR
        if (proc.isDebugging()) {
            return;
        }
        
        // 检查2：如果没有正在执行的服务，或者进程已死，忽略
        if (proc.executingServices.size() == 0 || proc.thread == null) {
            return;
        }
```

为什么调试时要忽略 ANR？

- 当你用 Android Studio 调试 App 时，断点会让代码暂停执行。如果不忽略，每次断点都会触发 ANR，调试就没法进行了。

- ```
  调试场景：
  T=0:   启动 Service，埋雷
  T=5:   在 onCreate() 里打了断点，代码暂停
  T=20:  定时器触发
         → 检测到 proc.isDebugging() == true
         → 忽略，不报 ANR
  T=60:  开发者继续执行，Service 完成
         → 正常拆雷
  
  ```

#### 2.遍历查找超时的 Service

```
 // ══════════════════════════════════════════════════════════
        // 第二步：计算超时阈值
        // ══════════════════════════════════════════════════════════
        
        // 获取当前时间
        final long now = SystemClock.uptimeMillis();
        
        // 计算"最晚应该开始执行的时间点"
        // 如果某个 Service 的 executingStart 早于这个时间，说明超时了
        final long maxTime = now - (
            proc.execServicesFg 
                ? SERVICE_TIMEOUT           // 前台：20秒
                : SERVICE_BACKGROUND_TIMEOUT // 后台：200秒
        );
        // ══════════════════════════════════════════════════════════
        // 第三步：遍历查找超时的 Service
        // ══════════════════════════════════════════════════════════
        
        ServiceRecord timeout = null;  // 记录超时的 Service
        long nextTime = 0;             // 记录下一个最早的开始时间
        
        // 倒序遍历（从最新添加的开始）
        for (int i = proc.executingServices.size() - 1; i >= 0; i--) {
            ServiceRecord sr = proc.executingServices.valueAt(i);
            
            // 检查这个 Service 是否超时
            if (sr.executingStart < maxTime) {
                // 找到了超时的 Service！
                timeout = sr;
                break;  // 只报告第一个超时的
            }
            
            // 如果没超时，记录最早的开始时间（用于下一轮检测）
            if (sr.executingStart > nextTime) {
                nextTime = sr.executingStart;
            }
        }

```

怎么理解这个超时时间计算呢？

- ```
  如果 executingStart < maxTime
  即 executingStart < now - 20秒
  即 now - executingStart > 20秒
  即 Service 已经执行超过 20 秒了
  → 超时！ANR！
  ```

#### 3.根据检测结果采取行动

```
        // ══════════════════════════════════════════════════════════
        // 第四步：根据检测结果采取行动
        // ══════════════════════════════════════════════════════════
        
        if (timeout != null && mAm.mProcessList.mLruProcesses.contains(proc)) {
            // ════════════════════════════════════════════════════
            // 分支1：发现超时，且进程还活着 → 报告 ANR
            // ════════════════════════════════════════════════════
            
            // 构建 ANR 信息
            StringWriter sw = new StringWriter();
            PrintWriter pw = new FastPrintWriter(sw, false, 1024);
            pw.println(timeout);           // 打印 ServiceRecord 信息
            timeout.dump(pw, "    ");      // 打印详细信息
            pw.close();
            
            // 构建 ANR 消息
            anrMessage = "executing service " + timeout.shortInstanceName;
            
        } else {
            // ════════════════════════════════════════════════════
            // 分支2：没有超时 → 安排下一轮检测
            // ════════════════════════════════════════════════════
            
            Message msg = mAm.mHandler.obtainMessage(SERVICE_TIMEOUT_MSG);
            msg.obj = proc;
            
            // 计算下一轮检测的时间
            // = 最早的 Service 开始时间 + 超时时间
            mAm.mHandler.sendMessageAtTime(msg, 
                proc.execServicesFg 
                    ? (nextTime + SERVICE_TIMEOUT) 
                    : (nextTime + SERVICE_BACKGROUND_TIMEOUT)
            );
        }
    }
    

    // ══════════════════════════════════════════════════════════
    // 第五步：在锁外处理 ANR（避免死锁）
    // ══════════════════════════════════════════════════════════
    
    if (anrMessage != null) {
        mAm.mAnrHelper.appNotResponding(proc, anrMessage);
    }
}

```

当检测到超时时，会构建一个 ANR 消息，包含：

- 超时的 Service 名称
- ServiceRecord 的详细信息（dump）\

同时会在 synchronized 块外处理 ANR，这是因为appNotResponding() 会做很多耗时任务

### 5.4 ANR处理：appNotResponding()

当确认发生 ANR 后，会调用 AnrHelper.appNotResponding()：

```
void appNotResponding(ProcessRecord anrProcess, String annotation) {
    // 加入 ANR 处理队列
    synchronized (mAnrRecords) {
        mAnrRecords.add(new AnrRecord(anrProcess, annotation, ...));
    }
    
    // 触发 ANR 处理线程
    startAnrConsumerIfNeeded();
}

```

ANR 的实际处理是在一个单独的线程中进行的，主要步骤：

```
ANR 处理流程：
│
├── 1. 收集信息
│   ├── 获取 CPU 使用率
│   ├── 获取所有线程的堆栈
│   └── 获取系统状态
│
├── 2. 写入文件
│   ├── /data/anr/traces.txt（堆栈信息）
│   └── 系统日志
│
├── 3. 通知用户
│   ├── 如果开启了"显示 ANR 对话框"
│   │   └── 弹出对话框让用户选择"等待"或"关闭"
│   └── 如果没开启
│       └── 直接杀死进程
│
└── 4. 上报
    └── 发送到错误收集服务（如 Bugly、Firebase Crashlytics）

```

### 5.5 爆雷过程的完整时序图

```
system_server 进程
      │
      │  T=20: 定时消息触发
      │
      ▼
MainHandler.handleMessage()
      │
      │  msg.what == SERVICE_TIMEOUT_MSG
      │
      ▼
ActiveServices.serviceTimeout(proc)
      │
      ├── 检查：proc.isDebugging()? → 是 → return
      │
      ├── 检查：executingServices.size() == 0? → 是 → return
      │
      ├── 计算：maxTime = now - 20秒
      │
      ├── 遍历 executingServices
      │   │
      │   ├── Service1.executingStart < maxTime?
      │   │   │
      │   │   ├── 是 → timeout = Service1, break
      │   │   │
      │   │   └── 否 → 记录 nextTime，继续遍历
      │   │
      │   └── ...
      │
      ├── if (timeout != null)
      │   │
      │   ├── 构建 anrMessage
      │   │
      │   └── 调用 appNotResponding()
      │         │
      │         ├── 收集堆栈信息
      │         ├── 写入 /data/anr/traces.txt
      │         ├── 弹出 ANR 对话框（如果开启）
      │         └── 可能杀死进程
      │
      └── else
          │
          └── 发送新的定时消息（下一轮检测）

```

### 5.6 边界情况

#### 1.情况1：前台服务和后台服务混合

```
final long maxTime = now - (
    proc.execServicesFg 
        ? SERVICE_TIMEOUT 
        : SERVICE_BACKGROUND_TIMEOUT
);
```

proc.execServicesFg 是进程级别的标记，表示"这个进程是否有前台服务在执行"。

如果一个进程同时有前台服务和后台服务：

- execServicesFg = true
- 所有服务都按 20 秒的标准检测

这意味着：只要有一个前台服务，整个进程的所有服务都按前台标准检测。

## 05.深度思考

### 5.1 关键问题探究



### 5.2 设计对比



## 06.实践验证

### 6.1 行为验证代码



### 6.2 性能测试





## 07.应用场景

### 7.1 最佳实践



### 7.2 使用禁忌





## 08.总结提炼

### 8.1 核心收获



### 8.2 知识图谱



### 8.3 延伸思考





## 09.参考资料

1. []()
2. []()
3. []()

## 其他介绍

### 01.关于我的博客

- csdn：http://my.csdn.net/qq_35829566

- 掘金：https://juejin.im/user/499639464759898

- github：https://github.com/jjjjjjava

- 邮箱：[934137388@qq.com]

