---
phase: 01-android
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - "04. 学习_Android核心原理/02. Binder原理.md"
autonomous: true
requirements: [BINDER-01]

must_haves:
  truths:
    - "笔记明确写出 Binder 是一次拷贝（copy_from_user），不是零拷贝，并与共享内存做对比"
    - "笔记包含 mmap 内核映射机制的 ASCII 图解"
    - "笔记区分了 Stub（Server端）和 Proxy（Client端）的职责"
    - "笔记包含 Binder 线程池 15 线程限制和 TransactionTooLargeException 1MB 缓冲区限制"
    - "笔记包含 linkToDeath 死亡通知机制"
  artifacts:
    - path: "04. 学习_Android核心原理/02. Binder原理.md"
      provides: "Binder IPC 通信机制完整面试笔记"
      contains: "copy_from_user"
      min_lines: 200
  key_links:
    - from: "02. Binder原理.md"
      to: "ServiceManager"
      via: "0号Binder注册查询服务"
      pattern: "ServiceManager.*0号"
---

<objective>
撰写 `02. Binder原理.md` 面试笔记，完整覆盖 Binder IPC 通信机制原理。

Purpose: Binder 是大厂面试极高频考点（字节 P7+ 必考），需要达到原理级理解，能画出 mmap 一次拷贝示意图并解释 copy_from_user 流程，能区分 Binder（一次拷贝）和共享内存（零拷贝）。
Output: 一篇结构化的面试准备笔记文件 `04. 学习_Android核心原理/02. Binder原理.md`
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
  <name>Task 1: 撰写 Binder 原理面试笔记</name>
  <files>04. 学习_Android核心原理/02. Binder原理.md</files>
  <read_first>
    - .planning/phases/01-android/01-RESEARCH.md（Topic 2: Binder 原理部分，含核心链路图和子概念表）
    - .planning/research/CORE_ANDROID.md（Binder 考点详情：典型问题、深度档次、陷阱）
    - .planning/research/INTERVIEW_STRATEGY.md（笔记模板结构）
  </read_first>
  <action>
    确保目录 `04. 学习_Android核心原理/` 存在。

    撰写 `02. Binder原理.md`，使用以下结构：

    **# 02. Binder 原理**

    **> 一句话总结（面试开场句）：** Binder 是 Android 特有的 IPC 机制，通过 mmap 让接收方用户空间与内核缓冲区共享物理页，实现一次拷贝（copy_from_user），兼顾安全性（内核鉴权 UID/PID）和性能。

    **## 一、核心原理链路**
    绘制 ASCII 流程图，必须包含 Client / 内核空间(Binder驱动) / Server 三列布局：
    ```
    Client进程                    内核空间                    Server进程
                               Binder驱动
    Proxy.transact()
      -> ioctl(BC_TRANSACTION)
        -> copy_from_user()     [唯一一次数据拷贝]
        -> 找到目标进程的
          mmap 映射区域
          (内核缓冲区 <-> Server
           用户空间 共享物理页)  [零拷贝到达Server]
                                  -> BR_TRANSACTION
                                    -> Stub.onTransact()
                                        -> 实际服务逻辑
    ```

    **## 二、关键机制详解**

    ### 2.1 为什么选 Binder 而非 socket/pipe/共享内存
    用对比表格：
    | IPC方式 | 拷贝次数 | 安全性 | 适用场景 |
    - Binder: 1次拷贝，内核鉴权 UID/PID（不可伪造），C/S 架构
    - Socket: 2次拷贝（用户->内核->用户），无身份验证
    - Pipe: 2次拷贝，半双工，只适合父子进程
    - 共享内存: 0次拷贝，但无内置同步机制，安全性差
    - 结论：Binder 是性能（一次拷贝）和安全性（内核鉴权）的最佳平衡点

    ### 2.2 mmap 一次拷贝机制（重点，必须有图）
    - 绘制 ASCII 图解，包含用户空间/内核空间/物理内存三层
    - 接收方进程启动时，Binder 驱动通过 mmap() 将一块物理内存同时映射到：
      (1) 内核虚拟地址空间（内核缓冲区）
      (2) 接收方用户虚拟地址空间
    - 发送方调用 copy_from_user() 将数据从发送方用户空间拷贝到内核缓冲区（第一次也是唯一一次拷贝）
    - 因为内核缓冲区和接收方用户空间指向同一物理页，接收方直接可读（零拷贝到达）
    - 对比传统 IPC：发送方 copy_from_user -> 内核缓冲区 -> copy_to_user 接收方 = 两次拷贝
    - **明确写出：Binder 是一次拷贝，不是零拷贝。共享内存（Ashmem）才是零拷贝。**

    ### 2.3 Client-Server-ServiceManager 三角关系
    - ServiceManager 是 0 号 Binder，通过 BINDER_SET_CONTEXT_MGR 向驱动注册
    - Server 通过 addService() 向 ServiceManager 注册服务
    - Client 通过 getService() 从 ServiceManager 查询服务，获得 BinderProxy
    - 类比 DNS：ServiceManager = DNS 服务器，服务名 = 域名，BinderProxy = IP 地址

    ### 2.4 AIDL 生成的 Stub / Proxy 角色
    - Stub（Server 端）：继承 Binder，实现 onTransact()，反序列化参数并调用实际实现
    - Proxy（Client 端）：持有 BinderProxy，实现接口方法，序列化参数并发送 transact()
    - Stub.asInterface(IBinder)：如果同进程返回 Stub 本身（直调），跨进程返回 Proxy
    - 画出 AIDL 生成代码结构图

    ### 2.5 Binder 线程池
    - 默认上限 DEFAULT_MAX_BINDER_THREADS = 15 个（通过 BINDER_SET_MAX_THREADS 设置）
    - 主线程不在 Binder 线程池内
    - 线程池满时，新的 Binder 请求会等待直到有空闲线程
    - oneway 修饰的方法是异步调用，不会阻塞调用方

    ### 2.6 TransactionTooLargeException 根因
    - Binder 事务缓冲区总大小 1MB（所有进程共享）
    - 单次事务实际可用约 512KB（扣除头部开销）
    - 常见触发场景：Intent 传递大 Bitmap、Bundle 过大、SavedInstanceState 过大
    - 解决方案：大数据用 ContentProvider/文件/Ashmem 传递

    ### 2.7 linkToDeath 死亡通知机制
    - IBinder.linkToDeath(DeathRecipient, 0) 注册死亡通知
    - Server 进程死亡时，Binder 驱动通知 Client，回调 DeathRecipient.binderDied()
    - 用途：Server 崩溃后 Client 重连（ServiceConnection.onServiceDisconnected 底层就是 linkToDeath）

    **## 三、为什么这么设计（追问准备）**
    - 为什么不用共享内存？虽然零拷贝但无内置安全鉴权、无 C/S 架构约束
    - 为什么内核能鉴权 UID/PID？因为 UID/PID 由内核填入 transaction 结构体，用户空间无法伪造
    - 为什么 Binder 缓冲区只有 1MB？防止恶意应用占用过多共享资源

    **## 四、高频面试问法 & 答题要点**
    表格格式，至少 8 个问题，来源于 CORE_ANDROID.md：
    - Binder 为什么一次拷贝
    - mmap 的角色
    - ServiceManager 是什么
    - AIDL Stub/Proxy 对应什么角色
    - Binder 线程池多少线程
    - TransactionTooLargeException 根因
    - Intent 数据大小限制
    - ContentProvider 底层是不是 Binder

    **## 五、追问陷阱与反脆弱**
    - 陷阱1：说 Binder 是零拷贝 -> 锚点：一次拷贝（copy_from_user），共享内存才是零拷贝
    - 陷阱2：线程池包含主线程 -> 锚点：主线程不在池内，DEFAULT_MAX_BINDER_THREADS=15 不含主线程
    - 陷阱3：AIDL 跨进程一定走 Binder -> 锚点：Stub.asInterface 同进程直调，跨进程才走 Proxy
    - 陷阱4：Binder 传输无限制 -> 锚点：1MB 缓冲区，单事务约 512KB

    **## 六、关联知识点**
    - AMS 与 Activity 的 Binder 通信（ApplicationThread）-> 04. AMS 笔记
    - Intent/Bundle 大小限制 -> TransactionTooLargeException
    - ContentProvider 底层 Binder 实现
    - 插件化 Hook AMS 的 Binder 代理

    **## 七、参考资料**
    - AOSP: frameworks/native/libs/binder/, drivers/android/binder.c
    - gityuan.com/2015/10/31/binder-prepare

    内容要求：
    1. mmap 一次拷贝 ASCII 图解必须清晰展示三层（用户空间/内核空间/物理内存）
    2. 明确对比 Binder vs 共享内存 vs Socket vs Pipe
    3. 关键数字必须准确：15 线程、1MB 缓冲区、0 号 Binder
    4. 总字数控制在 3000-5000 字
  </action>
  <verify>
    <automated>
      grep -c "copy_from_user" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "一次拷贝" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "mmap" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "ServiceManager" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "Stub" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "Proxy" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "TransactionTooLargeException" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md" &&
      grep -c "linkToDeath\|DeathRecipient\|binderDied" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md"
    </automated>
  </verify>
  <acceptance_criteria>
    - grep "copy_from_user" 返回 >= 2
    - grep "一次拷贝" 返回 >= 2（必须明确区分与零拷贝的差异）
    - grep "mmap" 返回 >= 3
    - grep "ServiceManager" 返回 >= 2
    - grep "Stub" 返回 >= 3
    - grep "Proxy" 返回 >= 3
    - grep "TransactionTooLargeException" 返回 >= 1
    - grep "linkToDeath|DeathRecipient|binderDied" 返回 >= 1
    - 文件包含七个大章节（一~七）
    - 包含 mmap 三层 ASCII 图解
    - 包含 IPC 方式对比表格
    - 包含面试问法表格（至少 8 行）
    - 包含追问陷阱章节（至少 4 个陷阱）
  </acceptance_criteria>
  <done>
    02. Binder原理.md 文件存在，包含完整七个章节，mmap 一次拷贝 ASCII 图解清晰，明确标注"一次拷贝不是零拷贝"，所有 grep 检查项通过。
  </done>
</task>

</tasks>

<verification>
1. 文件存在：`ls "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md"`
2. 关键词检查：所有 8 个 grep 检查全部返回 >= 1
3. 结构检查：`grep -c "^## " "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/02. Binder原理.md"` >= 7
4. 行数检查：`wc -l` >= 200
</verification>

<success_criteria>
- Binder 原理笔记覆盖 ROADMAP 全部考点：一次拷贝 vs 零拷贝、mmap 机制、ServiceManager、Stub/Proxy、线程池 15 线程、TransactionTooLargeException、linkToDeath
- 能根据笔记画出 mmap 内核映射示意图并解释 copy_from_user 流程
- 能区分 Binder（一次拷贝）和共享内存（零拷贝）
</success_criteria>

<output>
After completion, create `.planning/phases/01-android/01-02-SUMMARY.md`
</output>
