# Phase 1: Android 核心原理 - Research

**Researched:** 2026-03-31
**Domain:** Android Framework internals — Handler/Binder/View/AMS/ClassLoader
**Confidence:** HIGH (based on pre-existing domain research files CORE_ANDROID.md + INTERVIEW_STRATEGY.md, cross-validated against project context)

---

## Summary

Phase 1 produces five markdown knowledge notes targeting 大厂 Android 面试 (字节/腾讯/阿里/美团). The notes are not software — they are structured interview-prep artifacts. The primary challenge is not *what* to write but *how deeply* and *in what structure* to write it, so that oral recall under adversarial questioning ("追问三层") is achievable.

The existing project research files (`.planning/research/CORE_ANDROID.md` and `INTERVIEW_STRATEGY.md`) already provide verified, high-quality domain knowledge: question lists, depth tiers, and priority matrices. This research phase's job is to synthesize those into a planning blueprint: per-note structure, 追问 trap catalogue, existing-note inventory, and testable quality criteria.

The project has an existing note template in `00.标准化/02. study文件模板.md` that uses a "学习链条" format (概念→原理→思考→总结→底层→应用). The Phase 1 notes should **adapt but not slavishly follow** this template — interview-prep notes require an additional layer: "面试话术/开场句" and "追问预案" that the generic study template lacks. The recommended approach is to extend the template with these two interview-specific sections.

**Primary recommendation:** Each note must pass a "three-layer drill test" — write the note, then ask three increasingly deep follow-up questions about the core concept. If you cannot answer from memory after writing the note, the note is incomplete.

---

## Standard Stack

> This phase produces markdown files, not compiled software. "Standard stack" here means authoritative sources and structural conventions.

### Authoritative Sources per Topic

| Topic | Primary Source | Secondary Source | Source Quality |
|-------|---------------|-----------------|----------------|
| Handler/Looper/MessageQueue | Android AOSP source: `frameworks/base/core/java/android/os/` | 深入理解 Android 卷一 (Innost) | HIGH |
| Binder IPC | AOSP `frameworks/native/libs/binder/` + kernel driver `drivers/android/binder.c` | 深入理解 Android 卷一 第6章 | HIGH |
| View 绘制体系 | AOSP `frameworks/base/core/java/android/view/ViewRootImpl.java` + `View.java` | Android 开发艺术探索 第4章 | HIGH |
| AMS/WMS/PMS + 系统启动 | AOSP `frameworks/base/services/core/java/com/android/server/` | 深入理解 Android 卷二/三 | HIGH |
| ClassLoader + 热修复 | AOSP `libcore/dalvik/src/main/java/dalvik/system/` | Tinker GitHub wiki / QZone 美团技术博客 | HIGH |

### Online References (MEDIUM confidence — verified against project research files)

| Topic | Recommended Articles |
|-------|---------------------|
| Handler/epoll | 掘金「Android消息机制——Handler/Looper/MessageQueue源码解析」; gityuan.com/2015/12/26/handler-message-framework |
| Binder mmap | gityuan.com/2015/10/31/binder-prepare | 一次拷贝详解 |
| View 绘制 | 腾讯 WeTest「Android View体系深入分析」 |
| AMS 进程启动 | gityuan.com/2016/03/26/app-process-create |
| 热修复对比 | 美团技术团队「Android热修复方案对比与演进」 |

---

## Note Structure Recommendation

### Universal Template for All 5 Notes

This structure is derived from combining the project's existing `study文件模板.md` pattern with the interview-specific requirements identified in `INTERVIEW_STRATEGY.md`.

```markdown
# [XX. 技术点名称]

> 一句话总结（面试开场句，控制在30字以内）

## 一、核心原理链路

[原理流程图 / 关键调用链 — 这是白板讲解的骨架]

## 二、关键机制详解

[每个子概念独立小节，含数据结构图 + 关键源码片段 + 设计原因]

### 2.1 [子概念A]
### 2.2 [子概念B]
...

## 三、为什么这么设计（追问准备）

[必须包含"为什么不用方案X"的对比分析]

## 四、高频面试问法 & 答题要点

| 问法 | 答题要点（关键词） | 易错点 |
|------|-----------------|-------|
| Q: ... | A: ... | ... |

## 五、追问陷阱与反脆弱

[每个追问陷阱单独列出：陷阱描述 + 正确答案 + 记忆锚点]

## 六、关联知识点

[指向其他笔记文件的链接 + 关联说明]

## 七、参考资料

[AOSP 源码路径 + 权威博客链接]
```

**Why this structure works for interview prep:**
- Section 1 (原理链路) trains the opening answer — the thing you say in the first 60 seconds
- Section 3 (为什么这么设计) directly addresses "追问第一层": "为什么不用 X?"
- Section 4 (面试问法) acts as a quick-review cheat sheet before the interview
- Section 5 (追问陷阱) is the most valuable section — it documents the *wrong* intuitions that candidates carry

---

## Architecture Patterns

### Topic 1: Handler 机制 (`01. Handler机制.md`)

**Core chain to nail (white-board flow):**
```
Thread.start()
  → Looper.prepare()  [ThreadLocal<Looper> 存入当前线程]
  → new MessageQueue() [native层创建 epoll fd + pipe fd]
  → Looper.loop()
      → MessageQueue.next()
          → nativePollOnce(fd, timeoutMillis)  [epoll_wait 阻塞]
          → 返回到期的 Message
      → msg.target.dispatchMessage(msg)
          → Handler.handleMessage()
  → [发送消息时] Handler.sendMessage()
      → MessageQueue.enqueueMessage() [按时间戳插入链表]
      → nativeWake(fd)  [write 到 pipe → epoll_wait 返回]
```

**Key sub-concepts to cover:**

| Sub-concept | The "why" that matters | 追问层 |
|-------------|----------------------|--------|
| ThreadLocal | 每个线程独立 Looper 的实现机制，不是全局变量 | 层1 |
| MessageQueue 链表排序 | 按 `when` 字段升序插入，不是 FIFO | 层1 |
| nativePollOnce / epoll | 真正阻塞在 native epoll_wait，不占 CPU | 层2 |
| 同步屏障 postSyncBarrier | 插入 target==null 的 Message，跳过普通消息，只发异步消息 | 层2 |
| Choreographer 与同步屏障 | 每帧开始前插屏障 → VSYNC 回调是异步消息 → 优先被处理 | 层3 |
| IdleHandler | MessageQueue 空闲时调用，用于延迟初始化，不保证执行时机 | 层2 |
| Message.sPool 复用池 | 链表实现的对象池（MAX_POOL_SIZE=50），obtain()/recycle() | 层2 |
| 主线程不 ANR | 阻塞在 epoll，等待消息；ANR 是"消息处理超时"不是"没有消息时超时" | 层1 |

---

### Topic 2: Binder 原理 (`02. Binder原理.md`)

**Core chain to nail (white-board flow):**
```
Client进程                    内核空间                    Server进程
                           Binder驱动
Proxy.transact()
  → ioctl(BC_TRANSACTION)
    → copy_from_user()     [唯一一次数据拷贝]
    → 找到目标进程的
      mmap 映射区域
      (内核缓冲区 ↔ Server
       用户空间 共享物理页)  [零拷贝到达Server]
                              → BR_TRANSACTION
                                → Stub.onTransact()
                                    → 实际服务逻辑
```

**Key sub-concepts to cover:**

| Sub-concept | The "why" that matters | 追问层 |
|-------------|----------------------|--------|
| 为什么选 Binder | 安全性（UID/PID鉴权）+ 性能（1次拷贝 vs pipe 2次） | 层1 |
| mmap 一次拷贝机制 | 接收方用户空间 ↔ 内核缓冲区共享物理页，发送方 copy_from_user 一次写入即到达 | 层2 |
| ServiceManager | 0号Binder，注册/查询服务的目录，自身通过 BINDER_SET_CONTEXT_MGR 注册 | 层2 |
| Stub/Proxy | Stub 在 Server 端 onTransact() 反序列化并调用实现；Proxy 在 Client 端序列化并发 transact() | 层1 |
| 线程池 15 线程 | DEFAULT_MAX_BINDER_THREADS=15，主线程不在池内，超过等待 | 层2 |
| TransactionTooLargeException | Binder 缓冲区 1MB 限制（实际约 512KB per transaction），超大 Bitmap 或序列化对象 | 层1 |
| linkToDeath | IBinder.DeathRecipient，Server 进程死亡时 binderDied() 回调，底层 Binder 驱动通知机制 | 层2 |

---

### Topic 3: View 绘制体系 (`03. View绘制体系.md`)

**Core chain to nail (white-board flow):**
```
VSYNC 信号
  → Choreographer.doFrame()
      → 插入同步屏障（postSyncBarrier）
      → 发送异步消息（traversal runnable）
      → ViewRootImpl.performTraversals()
          → performMeasure() → View.measure() → onMeasure()
          → performLayout()  → View.layout()  → onLayout()
          → performDraw()    → View.draw()    → onDraw()
              [硬件加速路径]
              → updateDisplayListIfDirty()
              → RenderNode.beginRecording() [记录绘制指令]
              → Canvas 操作序列化为 DisplayList
              → RenderThread 提交到 GPU
```

**Key sub-concepts to cover:**

| Sub-concept | The "why" that matters | 追问层 |
|-------------|----------------------|--------|
| ViewRootImpl 入口 | 不是 Activity，不是 View；是 WindowManager.addView() 时创建的 | 层1 |
| MeasureSpec 三种模式 | EXACTLY/AT_MOST/UNSPECIFIED；父View通过 getChildMeasureSpec() 合成子View的spec | 层1 |
| requestLayout() vs invalidate() | requestLayout 走 measure+layout+draw；invalidate 只走 draw（标脏向上传播）| 层1 |
| 同步屏障在 Choreographer 中的作用 | 确保 VSYNC 触发的 traversal 消息优先于其他普通消息 | 层3 |
| DisplayList/RenderNode | 绘制指令的序列化缓存，硬件加速专有；View 变化时 invalidate 只重录变化的 RenderNode | 层2 |
| RenderThread 协作 | MainThread 录制 DisplayList → RenderThread 异步提交 GPU，两线程并行 | 层2 |
| wrap_content 不生效根因 | onMeasure 默认实现将 AT_MOST 当 EXACTLY 处理，需重写 onMeasure 自行计算 | 层2 |

---

### Topic 4: AMS-WMS-PMS 及系统启动 (`04. AMS-WMS-PMS及系统启动.md`)

**Core chain to nail (white-board flow — 应用进程启动):**
```
用户点击图标
  → Launcher 调用 startActivity()
  → AMS (ActivityManagerService, system_server 进程)
      → 检查目标进程是否存在
      → 不存在: socket 发消息给 Zygote
          → Zygote.forkAndSpecialize()
          → 新进程: ActivityThread.main()
              → Looper.prepareMainLooper()
              → new ActivityThread()
              → thread.attach(false) [Binder 回调给 AMS]
              → Looper.loop()
  → AMS 通过 Binder 调用 ApplicationThread (IApplicationThread)
      → scheduleLaunchActivity()
          → Handler H 发 LAUNCH_ACTIVITY 消息
          → handleLaunchActivity()
              → Activity.onCreate()
```

**Key sub-concepts to cover:**

| Sub-concept | The "why" that matters | 追问层 |
|-------------|----------------------|--------|
| Activity-Window-View 三者关系 | Activity 持有 Window(PhoneWindow)，Window 持有 DecorView，DecorView 是 View 树根 | 层1 |
| ActivityRecord/TaskRecord/ActivityStack | AMS 侧的纯数据结构，对应客户端的 Activity/Back Stack/Task | 层2 |
| AMS 回调 ApplicationThread | 不是直接调 Activity，而是通过 Binder 调 ApplicationThread，再 Handler 切到主线程 | 层2 |
| LaunchMode 四种 | standard/singleTop/singleTask/singleInstance；singleTask 是 Task 内唯一，非全局 | 层1 |
| Zygote fork 优势 | Copy-on-Write + 预加载 Android 类库，避免重复加载 | 层2 |
| WMS Surface z-order | Window 有 type 值决定层级（Toast > Dialog > Activity），WMS 通过 SurfaceFlinger 合成 | 层2 |
| APK 安装流程 | 解析 Manifest → 权限校验 → 文件复制到 /data/app → dex2oat 优化 → PMS 注册到 packages.xml | 层1 |

---

### Topic 5: ClassLoader 与热修复 (`05. ClassLoader与热修复.md`)

**Core chain to nail (white-board flow — 热修复 dexElements 前插):**
```
BaseDexClassLoader.findClass(name)
  → DexPathList.findClass(name)
      → 遍历 dexElements[] 数组（顺序敏感！）
          → dexElements[0].findClass() [补丁dex]
          → 找到: 返回（不再继续）
          → 找不到: dexElements[1].findClass() [原始dex]
热修复原理: 将补丁.dex 插入 dexElements[0] 位置
```

**Key sub-concepts to cover:**

| Sub-concept | The "why" that matters | 追问层 |
|-------------|----------------------|--------|
| PathClassLoader vs DexClassLoader | PathClassLoader 加载已安装 APK；DexClassLoader 加载任意路径 dex（热修复/插件化用） | 层1 |
| 双亲委派 | findClass 先委托 parent，parent 找不到才自己找；防止核心类被替换 | 层1 |
| dexElements 前插 | QZone/Tinker 核心：反射修改 DexPathList.dexElements 将补丁 dex 排在首位 | 层1 |
| QZone pre-verify 问题 | Dalvik 对同 dex 的类做 pre-verify 优化；跨 dex 引用会导致 CLASS_ISPREVERIFIED 校验失败 | 层2 |
| Tinker 差量 patch | bsdiff/bspatch 算法对 dex 做差量生成新 dex；服务器下发 patch，客户端合并 | 层2 |
| Sophix 方法替换 | 修改 ArtMethod 结构体指针实现方法级替换，无需重启；兼容性依赖 ART 版本稳定性 | 层2 |
| 插件化三问题 | 类加载（DexClassLoader）+ 资源加载（addAssetPath）+ 四大组件生命周期（Hook AMS 占坑） | 层1 |
| Hook AMS 占坑 Activity | 将真实 PluginActivity 替换为已注册的 StubActivity 发给 AMS，AMS 通知后再换回来（Handler H 拦截）| 层3 |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 原理流程图 | 用文字描述替代图 | ASCII 流程图 + Mermaid | 文字难以在面试中口述，图形帮助建立肌肉记忆 |
| 追问预案 | 临时想 | 写入笔记 Section 5（追问陷阱） | 追问是可预测的，必须提前写下正确答案 |
| 源码引用 | 直接拷贝大段源码 | 只保留关键方法签名和关键变量名 | 笔记不是源码镜像，关键符号（epoll_wait / dexElements）即可触发记忆 |
| 重新调研 | 每次写笔记重新 Google | 引用 AOSP 路径 + gityuan.com 系列 | gityuan.com 是公认最权威的 AOSP 中文解析，已被 CORE_ANDROID.md 验证 |

---

## Common Pitfalls

### Pitfall 1: 把"原理"写成了"API 列表"
**What goes wrong:** 笔记里只有 `Handler.sendMessage()`, `Looper.loop()` 等 API 介绍，没有解释 *为什么* epoll 在 native 层、*为什么* MessageQueue 用链表而非队列。
**Why it happens:** 习惯了工作中写使用说明，不习惯写设计原因。
**How to avoid:** 每个子概念都要回答"为什么这么设计，而不是用 X 替代"这个问题。
**Warning signs:** 如果一个 Section 没有"因为/原因/本质"等词，说明该 Section 停留在 API 层。

### Pitfall 2: 追问陷阱未预置
**What goes wrong:** 笔记写完，面试被问"主线程 Looper 死循环为什么不 ANR"时仍然说不清楚。
**Why it happens:** 这个问法反直觉 — 死循环直觉上应该卡死，但 epoll 阻塞不耗 CPU 这个关键知识点没有单独强调。
**How to avoid:** Section 5（追问陷阱）必须专门列出这类反直觉问题，并且用一句话记忆锚点固化。
**Warning signs:** 写笔记时只验证"我能写出来"，没有验证"我能口述回答"。

### Pitfall 3: 混淆"Binder 一次拷贝"与"共享内存零拷贝"
**What goes wrong:** 面试说"Binder 是零拷贝"，被面试官追问后越陷越深。
**Why it happens:** Binder 的 mmap 让人联想到"零拷贝"，但实际上发送方 → 内核仍需 copy_from_user 一次。
**How to avoid:** Binder 笔记必须明确写出"一次拷贝（copy_from_user），不是零拷贝（共享内存才是）"，并解释为何 mmap 只减少了内核→接收方这一次拷贝。
**Warning signs:** 笔记中没有对比 Binder vs 共享内存的章节。

### Pitfall 4: singleTask 误解为"全局单例"
**What goes wrong:** 说 singleTask Activity 在整个系统中只有一个实例。
**Why it happens:** 名字叫 "single Task" 容易理解为系统级唯一。
**How to avoid:** 笔记必须明确：singleTask 在同一 **Task（任务栈）** 内唯一，但不同 Task 可以各有一个实例（除非指定了相同 affinity）。
**Warning signs:** LaunchMode 章节没有举具体的 Task 栈变化例子。

### Pitfall 5: pre-verify 问题的适用范围
**What goes wrong:** 解释热修复时说 QZone 的 pre-verify 问题在 Android 5.0+ 仍然存在。
**Why it happens:** 这个问题只在 Dalvik 虚拟机存在，ART（Android 5.0+）取消了这个优化。
**How to avoid:** 热修复章节必须标注"pre-verify 仅 Dalvik（Android < 5.0）"，说明 QZone 方案的历史局限性。
**Warning signs:** 笔记中没有注明 Dalvik/ART 版本差异。

### Pitfall 6: ViewRootImpl checkThread() 误解
**What goes wrong:** 说"View 更新只能在主线程"。
**Why it happens:** 99% 的情况确实只在主线程更新，但限制实际是"创建 ViewRootImpl 的线程"。
**How to avoid:** 笔记注明 checkThread() 的实际实现，并举子线程更新 View 的 workaround（在子线程创建 Window + Looper）。
**Warning signs:** 笔记没有引用 ViewRootImpl.checkThread() 源码逻辑。

---

## Existing Notes Inventory

### Notes That Can Be Referenced (no reuse needed, just cross-reference)

| Existing File | Location | Relevance to Phase 1 | Action |
|--------------|----------|---------------------|--------|
| `ANR_01.基础概念.md` | `04. 学习_性能优化/` | ANR 触发机制关联 Handler/AMS 原理 | Phase 1 笔记写完后添加 `→ 见 ANR 原理笔记` 的关联指针 |
| `启动优化_01.启动优化其一.md` | `04. 学习_性能优化/` | 包含 AMS/Zygote 启动链路背景 | Phase 1 的 AMS 笔记可引用此文件中的启动链路图 |
| `02. 音视频_音视频基础_01.md` — OpenGL 系列 | `04. 学习_音视频/` | View 绘制体系 + SurfaceView/TextureView | View 绘制笔记完成后，在 Phase 3 中升级为 OpenGL 渲染关联 |

### Notes That Do NOT Exist Yet (must be created from scratch)

| File to Create | Estimated effort | Dependencies |
|---------------|-----------------|--------------|
| `01. Handler机制.md` | 中 (原理清晰，结构化需时间) | 无 |
| `02. Binder原理.md` | 高 (mmap 机制需要图解) | 无 |
| `03. View绘制体系.md` | 高 (硬件加速部分细节多) | 无 |
| `04. AMS-WMS-PMS及系统启动.md` | 高 (覆盖范围最广) | Handler + Binder 笔记最好先完成 |
| `05. ClassLoader与热修复.md` | 中 (热修复对比是重点) | 无 |

**Recommended writing order:** 01 → 02 → 03 → 04 → 05
(Handler 和 Binder 是 AMS 笔记的前置，先写可建立概念基础)

---

## Note Placement

The 5 note files should be placed in a new directory at the repo root level to match the project's existing `04. 学习_*` pattern. Based on INTERVIEW_STRATEGY.md's suggested structure:

```
项目/
└── 04. 学习_Android核心原理/    ← 新建目录
    ├── 01. Handler机制.md
    ├── 02. Binder原理.md
    ├── 03. View绘制体系.md
    ├── 04. AMS-WMS-PMS及系统启动.md
    └── 05. ClassLoader与热修复.md
```

**Alternative:** Place directly under `项目/` root as `Android核心原理/`. The `04. 学习_*` convention is used for all topic-based learning notes — this is the correct pattern to follow.

---

## State of the Art

| Topic | Historically Common Mistake | Current Correct Answer |
|-------|---------------------------|----------------------|
| Binder 拷贝次数 | "零拷贝" | 一次拷贝（copy_from_user）；零拷贝是共享内存 |
| PathClassLoader 8.0+ | "只能加载安装包" | Android 8.0+ 可加载外部 dex，但 DexClassLoader 仍是热修复/插件化标准 |
| pre-verify 问题 | "QZone 方案 Android 5.0+ 也有问题" | pre-verify 仅 Dalvik，ART 无此问题（但 QZone 方案仍有 dex 分包问题） |
| ART 编译策略 | "安装时全量编译" | Android 7.0+ 改为 JIT+AOT 混合：JIT 运行时热点方法记录 profile，后台 AOT 编译 |
| singleTask | "全局唯一实例" | Task 内唯一，不同 affinity 的 Task 可各有一个实例 |

---

## Open Questions

1. **项目笔记放置路径**
   - What we know: 现有 `04. 学习_音视频/` `04. 学习_Flutter/` `04. 学习_性能优化/` 等目录存在
   - What's unclear: 新建 `04. 学习_Android核心原理/` 还是用其他命名（如 `01. Android核心原理/`）？
   - Recommendation: 跟随现有 `04. 学习_*` 命名约定，建 `04. 学习_Android核心原理/`

2. **笔记模板是否沿用 `study文件模板.md`**
   - What we know: 现有模板有详细的学习分类 checklist，格式较重
   - What's unclear: Phase 1 笔记是否需要完整的 `学习概述` metadata block？
   - Recommendation: 保留 `##一句话总结` (面试开场句) 和 `##参考资料`，去掉大部分 checklist boilerplate——面试笔记以快速复习为主，不需要完整 metadata

3. **Binder mmap 图解工具**
   - What we know: markdown 中可用 ASCII 图或 Mermaid diagram
   - What's unclear: 项目是否有 Mermaid 渲染支持（Obsidian/Typora）
   - Recommendation: 使用 ASCII art 作为主要图解方式（100% 兼容），Mermaid 作为可选附加

---

## Validation Architecture

> `workflow.nyquist_validation` is `true` in config.json — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual review checklist (no automated test runner — this is a markdown notes project) |
| Config file | This section defines the checklist |
| Quick run command | Open note file, run mental "追问 3 层" drill |
| Full suite command | Read all 5 notes, attempt to answer all Success Criteria from ROADMAP.md without looking at notes |

### Per-Note Testable Criteria

#### Note 01: Handler机制.md

| Check ID | Criterion | Type | Pass Condition |
|----------|-----------|------|----------------|
| H-01 | 包含 "epoll" 关键词 | content | 文件中存在 `epoll` |
| H-02 | 解释主线程死循环不 ANR 的原因 | content | 笔记中存在"阻塞在 native" 或 "epoll_wait 不占 CPU" 的描述 |
| H-03 | 包含 MessageQueue 链表排序说明 | content | 笔记中有 `when` 字段或"按时间戳排序"的描述 |
| H-04 | 覆盖同步屏障与 Choreographer 的关系 | content | 笔记中同时出现 `postSyncBarrier` 和 `Choreographer` |
| H-05 | 包含 IdleHandler 用途与触发时机 | content | 笔记中有 IdleHandler + 触发条件说明 |
| H-06 | 包含 Message.sPool 复用池 | content | 笔记中有 `sPool` 或 `obtain()` + 复用池描述 |
| H-07 | 口述验证：不看笔记能从 ThreadLocal 讲到 epoll | manual | 能完整口述原理链路 ≥ 3 分钟 |

#### Note 02: Binder原理.md

| Check ID | Criterion | Type | Pass Condition |
|----------|-----------|------|----------------|
| B-01 | 明确写出"一次拷贝，不是零拷贝" | content | 笔记中存在对比 Binder vs 共享内存的描述 |
| B-02 | 包含 mmap 内核映射机制图解 | content | 笔记中有 `copy_from_user` + mmap 机制说明（ASCII图或文字） |
| B-03 | 覆盖 Stub/Proxy 各自角色 | content | 笔记中有 Stub（Server端）和 Proxy（Client端）的职责区分 |
| B-04 | 包含线程池 15 线程限制 | content | 笔记中有 `DEFAULT_MAX_BINDER_THREADS` 或 "15" 的说明 |
| B-05 | 包含 TransactionTooLargeException 根因 | content | 笔记中有 1MB 缓冲区限制说明 |
| B-06 | 包含 linkToDeath 机制 | content | 笔记中有 `DeathRecipient` 或 `binderDied()` 说明 |
| B-07 | 口述验证：能画出 mmap 一次拷贝示意图 | manual | 能在白纸上画出 Client/内核/Server 三层 + 箭头标注拷贝次数 |

#### Note 03: View绘制体系.md

| Check ID | Criterion | Type | Pass Condition |
|----------|-----------|------|----------------|
| V-01 | 明确 ViewRootImpl 作为绘制入口 | content | 笔记中有 `ViewRootImpl.performTraversals()` |
| V-02 | 覆盖 MeasureSpec 三种模式 | content | 笔记中有 EXACTLY/AT_MOST/UNSPECIFIED 三者的条件描述 |
| V-03 | 区分 requestLayout() 和 invalidate() 的触发路径 | content | 笔记中有两者的路径差异对比 |
| V-04 | 包含 Choreographer/VSYNC 驱动帧调度说明 | content | 笔记中同时出现 `Choreographer` 和 `VSYNC` |
| V-05 | 包含硬件加速 DisplayList/RenderNode 机制 | content | 笔记中有 `DisplayList` 或 `RenderNode` 的说明 |
| V-06 | 解释 wrap_content 不生效根因 | content | 笔记中有 AT_MOST 与 onMeasure 默认实现的关联说明 |
| V-07 | 口述验证：能说出 performTraversals 三段式 | manual | 能口述 measure → layout → draw 的入口方法链 |

#### Note 04: AMS-WMS-PMS及系统启动.md

| Check ID | Criterion | Type | Pass Condition |
|----------|-----------|------|----------------|
| A-01 | 覆盖 Activity-Window-View 三者关系 | content | 笔记中有 DecorView/PhoneWindow/WindowManager 的层级说明 |
| A-02 | 包含 AMS 通过 ApplicationThread Binder 回调驱动生命周期 | content | 笔记中有 `ApplicationThread` 和 Binder 回调的说明 |
| A-03 | 包含 ActivityRecord 是 AMS 侧记录对象 | content | 笔记中有 `ActivityRecord` 的说明 |
| A-04 | 覆盖应用进程启动全链路（AMS→Zygote→ActivityThread.main()） | content | 笔记中同时出现 `Zygote` + `fork` + `ActivityThread.main()` |
| A-05 | 覆盖四种 LaunchMode 与任务栈影响 | content | 笔记中有 singleTask 的 Task 内唯一（非全局）的描述 |
| A-06 | 包含 APK 安装流程（PMS） | content | 笔记中有 dex2oat + packages.xml 的说明 |
| A-07 | 口述验证：能从 AMS 讲到 Activity.onCreate() 完整链路 | manual | 能口述完整启动链路 ≥ 3 分钟，包含 Zygote fork 步骤 |

#### Note 05: ClassLoader与热修复.md

| Check ID | Criterion | Type | Pass Condition |
|----------|-----------|------|----------------|
| C-01 | 区分 PathClassLoader vs DexClassLoader | content | 笔记中有两者用途差异的对比描述 |
| C-02 | 解释双亲委派模型 | content | 笔记中有 parent ClassLoader 委托机制说明 |
| C-03 | 包含 dexElements 前插原理 | content | 笔记中有 `dexElements` + 数组顺序/前插的说明 |
| C-04 | 对比 QZone/Tinker/Sophix 三方案核心差异 | content | 笔记中有三者的对比，且注明 pre-verify 仅 Dalvik |
| C-05 | 覆盖插件化三大核心问题 | content | 笔记中同时出现类加载 + 资源加载 + 四大组件生命周期三个问题 |
| C-06 | 包含 Hook AMS 占坑 Activity 原理 | content | 笔记中有 StubActivity/占坑 + Handler H 拦截的说明 |
| C-07 | 口述验证：能说清楚 dexElements 前插为什么能修复 Bug | manual | 能口述数组遍历顺序 → 补丁 dex 优先找到修复类的逻辑 |

### Phase Gate Criteria (from ROADMAP.md Success Criteria)

All 5 manual verification checks (H-07, B-07, V-07, A-07, C-07) must pass before phase is complete:
- Handler: 不看笔记讲完整 ThreadLocal → MessageQueue → epoll → 同步屏障，能答"主线程死循环为什么不 ANR"
- Binder: 能画出 mmap 内核映射示意图，能区分 Binder（一次）和共享内存（零次）
- View: 能说出 ViewRootImpl 入口、三大流程，追问 Choreographer/VSYNC 时能继续回答
- AMS: 能描述完整 AMS → Zygote → ActivityThread 链路，说出 ActivityRecord 是 AMS 侧记录对象
- ClassLoader: 能说清楚 dexElements 前插方案，对比 QZone/Tinker 核心差异

### Automated Content Checks (grep-based, can be run after each note is written)

```bash
# H-01: epoll 存在
grep -c "epoll" "04. 学习_Android核心原理/01. Handler机制.md"

# B-01: 一次拷贝明确
grep -c "一次拷贝" "04. 学习_Android核心原理/02. Binder原理.md"

# B-02: copy_from_user
grep -c "copy_from_user" "04. 学习_Android核心原理/02. Binder原理.md"

# V-01: ViewRootImpl.performTraversals
grep -c "performTraversals" "04. 学习_Android核心原理/03. View绘制体系.md"

# A-04: Zygote fork
grep -c "Zygote" "04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md"

# C-03: dexElements
grep -c "dexElements" "04. 学习_Android核心原理/05. ClassLoader与热修复.md"
```

---

## Environment Availability

Step 2.6: SKIPPED (this is a markdown notes project — no external tool dependencies, no compilation, no runtime services required)

---

## Sources

### Primary (HIGH confidence)
- `.planning/research/CORE_ANDROID.md` — Per-topic question lists, depth tiers, priority matrix, pitfall catalogue. Verified against AOSP knowledge base.
- `.planning/research/INTERVIEW_STRATEGY.md` — Note structure recommendations, time allocation, company-specific patterns.
- `.planning/ROADMAP.md` — Phase 1 Plans section: exact topic lists per note file (authoritative for scope).
- `00.标准化/02. study文件模板.md` — Project's existing note template (authoritative for format conventions).

### Secondary (MEDIUM confidence)
- gityuan.com series — Recognized authoritative AOSP Chinese analysis (referenced in CORE_ANDROID.md)
- 美团技术团队 blog — Hot-fix comparison articles (referenced in CORE_ANDROID.md)

### Tertiary (LOW confidence — not independently verified in this research session)
- 深入理解 Android 系列 (Innost) — Book references, version currency unverified
- 掘金 Handler/Binder analysis articles — Community content, quality varies

---

## Metadata

**Confidence breakdown:**
- Note structure recommendation: HIGH — derived directly from project's own template + INTERVIEW_STRATEGY.md
- Per-topic key concepts: HIGH — sourced from CORE_ANDROID.md which lists exact question sets
- Pitfall catalogue: HIGH — explicitly documented in CORE_ANDROID.md "陷阱" sections
- Source recommendations: MEDIUM — gityuan.com reputation is well-established but not independently verified in this session
- Existing notes inventory: HIGH — verified by direct directory listing

**Research date:** 2026-03-31
**Valid until:** 2026-09-30 (Android framework internals are stable; only tool recommendations may shift)
