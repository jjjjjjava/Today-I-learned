---
phase: 01-android
plan: 04
type: execute
wave: 2
depends_on: [01, 02]
files_modified:
  - "04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md"
autonomous: true
requirements: [AMS-01]

must_haves:
  truths:
    - "笔记覆盖 Activity-Window-View 三者关系（Activity 持有 PhoneWindow，PhoneWindow 持有 DecorView）"
    - "笔记包含 AMS 通过 Binder 回调 ApplicationThread 驱动生命周期的机制"
    - "笔记包含完整的应用进程启动链路：AMS -> Zygote fork -> ActivityThread.main()"
    - "笔记覆盖四种 LaunchMode 及对任务栈的影响，明确 singleTask 是 Task 内唯一而非全局单例"
    - "笔记包含 APK 安装流程（PMS：解析 -> 权限校验 -> dex 优化 -> 信息注册）"
  artifacts:
    - path: "04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md"
      provides: "AMS/WMS/PMS 及系统启动完整面试笔记"
      contains: "Zygote"
      min_lines: 250
  key_links:
    - from: "04. AMS-WMS-PMS及系统启动.md"
      to: "01. Handler机制.md"
      via: "ActivityThread.main() 中创建主线程 Looper"
      pattern: "Looper.prepareMainLooper"
    - from: "04. AMS-WMS-PMS及系统启动.md"
      to: "02. Binder原理.md"
      via: "AMS 通过 Binder IPC 调用 ApplicationThread"
      pattern: "ApplicationThread.*Binder"
---

<objective>
撰写 `04. AMS-WMS-PMS及系统启动.md` 面试笔记，覆盖 Activity 管理、窗口管理、包管理三大系统服务及应用启动完整链路。

Purpose: AMS/WMS/PMS 是大厂 P6+ 必问考点，尤其是"Activity 启动流程"和"Activity-Window-View 三者关系"。本笔记是 Phase 1 中覆盖范围最广的笔记，需要能描述完整的 AMS -> Zygote -> ActivityThread 链路，并说出 ActivityRecord 是 AMS 侧的记录对象。
Output: 一篇结构化的面试准备笔记文件 `04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md`
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

# 依赖前序笔记的概念（Handler + Binder），但不需要读取前序 SUMMARY——本笔记内容自包含
# 这里引用的是 RESEARCH.md 中的 Topic 4 部分，已包含完整的链路图和子概念表
</context>

<tasks>

<task type="auto">
  <name>Task 1: 撰写 AMS-WMS-PMS 及系统启动面试笔记</name>
  <files>04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md</files>
  <read_first>
    - .planning/phases/01-android/01-RESEARCH.md（Topic 4: AMS-WMS-PMS 部分，含应用启动链路图和子概念表）
    - .planning/research/CORE_ANDROID.md（AMS/WMS/PMS 考点详情 + Activity/Fragment 生命周期考点 + APK 安装流程考点）
    - .planning/research/INTERVIEW_STRATEGY.md（笔记模板结构）
  </read_first>
  <action>
    确保目录 `04. 学习_Android核心原理/` 存在。

    撰写 `04. AMS-WMS-PMS及系统启动.md`，使用以下结构：

    **# 04. AMS-WMS-PMS 及系统启动**

    **> 一句话总结（面试开场句）：** AMS/WMS/PMS 均运行在 system_server 进程，通过 Binder 对外提供服务。AMS 管理 Activity 和进程生命周期，WMS 管理窗口 Surface 和 Z-order，PMS 管理 APK 安装和包信息。应用启动全链路：AMS -> Zygote fork -> ActivityThread.main() -> Looper.loop()。

    **## 一、核心原理链路（应用进程启动全链路）**
    绘制 ASCII 流程图，内容必须包含：
    ```
    用户点击图标
      -> Launcher 调用 startActivity()
      -> AMS (system_server 进程)
          -> 检查目标进程是否存在
          -> 不存在: socket 发消息给 Zygote
              -> Zygote.forkAndSpecialize()
              -> 新进程: ActivityThread.main()
                  -> Looper.prepareMainLooper()
                  -> new ActivityThread()
                  -> thread.attach(false) [Binder 注册给 AMS]
                  -> Looper.loop()
      -> AMS 通过 Binder 调用 ApplicationThread (IApplicationThread)
          -> scheduleLaunchActivity()
              -> Handler H 发 LAUNCH_ACTIVITY 消息
              -> handleLaunchActivity()
                  -> performLaunchActivity()
                      -> Instrumentation.newActivity() [反射创建 Activity]
                      -> Activity.attach() [创建 PhoneWindow]
                      -> Activity.onCreate()
    ```

    **## 二、关键机制详解**

    ### 2.1 Activity-Window-View 三者关系
    - Activity 持有 Window（实现类是 PhoneWindow）
    - PhoneWindow 持有 DecorView（FrameLayout 子类，View 树的根节点）
    - DecorView 包含 TitleBar + ContentView（我们 setContentView 的容器）
    - WindowManager.addView(DecorView) 时创建 ViewRootImpl
    - 画出层级关系图：Activity -> PhoneWindow -> DecorView -> (TitleBar + ContentView)
    - getApplicationContext() 没有 Window，不能直接 show Dialog

    ### 2.2 AMS 通过 Binder 回调 ApplicationThread 驱动生命周期
    - AMS 不直接调用 Activity 方法
    - AMS 持有每个应用进程的 IApplicationThread Binder 代理
    - AMS 通过 Binder IPC 调用 ApplicationThread.scheduleLaunchActivity() 等方法
    - ApplicationThread 是 ActivityThread 的内部类，实现了 IApplicationThread
    - ApplicationThread 收到调用后，通过 Handler H 切到主线程执行生命周期方法
    - 关键点：Binder 线程 -> Handler H -> 主线程，这就是为什么依赖 Handler 机制

    ### 2.3 ActivityRecord / TaskRecord / ActivityStack
    - ActivityRecord：AMS 侧记录一个 Activity 实例的数据结构（包含 token、intent、taskAffinity 等）
    - TaskRecord：一个任务栈，包含多个 ActivityRecord（对应用户感知的一个"任务"）
    - ActivityStack：管理多个 TaskRecord（前台栈/后台栈）
    - 注意 Android 12+ 改名：ActivityRecord -> ActivityRecord、TaskRecord -> Task、ActivityStack -> TaskDisplayArea

    ### 2.4 四种 LaunchMode 与 FLAG
    用表格 + 栈变化图示：
    | LaunchMode | 行为 | 栈变化 |
    - standard：每次创建新实例，压入当前 Task 栈顶
    - singleTop：栈顶已有则 onNewIntent，否则新建
    - singleTask：**Task 内唯一**（不是全局唯一！），如已存在则 clearTop 到该 Activity 并 onNewIntent
    - singleInstance：独占一个 Task，整个系统该 Task 只有这一个 Activity
    - 常用 FLAG：FLAG_ACTIVITY_NEW_TASK（相当于 singleTask）、FLAG_ACTIVITY_CLEAR_TOP
    - **明确写出：singleTask 是 Task 内唯一，不同 affinity 的 Task 可各有一个实例**

    ### 2.5 Zygote fork 优势
    - Zygote 进程预加载了 Android 核心类库和资源（preloadClasses/preloadResources）
    - fork 出的子进程通过 Copy-on-Write 共享这些预加载的内存页
    - 好处：(1) 启动快（不需重新加载 framework 类）(2) 省内存（共享物理页）
    - 为什么用 socket 通信而不是 Binder？Binder 涉及多线程，fork 多线程进程可能产生死锁

    ### 2.6 WMS 管理 Surface Z-order
    - WMS (WindowManagerService) 管理 Window（Surface），不直接管 View
    - 每个 Window 有 type 值决定 Z-order 层级：
      - APPLICATION_WINDOW (1-99)：Activity 窗口
      - SUB_WINDOW (1000-1999)：Dialog、PopupWindow
      - SYSTEM_WINDOW (2000+)：Toast、StatusBar、SystemAlert
    - type 值越大越在上层
    - SurfaceFlinger 最终根据 Z-order 合成所有 Surface 到屏幕

    ### 2.7 PMS APK 安装流程
    绘制流程图：
    ```
    点击安装 APK
      -> PackageInstaller 调用 PMS.installPackage()
      -> 解析 AndroidManifest.xml（提取包名、权限、四大组件信息）
      -> 签名验证（V1/V2/V3，V2 对整个 APK 签名更安全）
      -> 文件复制到 /data/app/{package}/
      -> dex2oat 将 dex 编译为 oat（Android 7.0+ JIT+AOT 混合）
      -> 注册包信息到 /data/system/packages.xml
      -> 发送 ACTION_PACKAGE_ADDED 广播
    ```
    - dex2oat 是最耗时步骤（大 APK 安装慢的原因）
    - Android 7.0+ 改为 JIT+AOT 混合：安装时不全量编译，运行时 JIT 记录热点方法 profile，后台 AOT 编译

    **## 三、为什么这么设计（追问准备）**
    - 为什么 AMS 不直接调用 Activity？跨进程，只能通过 Binder IPC
    - 为什么 Zygote 用 socket 不用 Binder？fork 多线程进程可能死锁
    - 为什么 Window type 用数值分层？简单高效的 Z-order 管理
    - 为什么 singleTask 不是全局唯一？通过 taskAffinity 控制所属 Task

    **## 四、高频面试问法 & 答题要点**
    表格格式，至少 10 个问题（本笔记覆盖范围最广）：
    - Activity 启动流程（完整链路）
    - Activity-Window-View 三者关系
    - AMS 的职责是什么
    - 四种 LaunchMode 区别
    - 应用进程如何启动
    - WMS 如何管理窗口层级
    - PMS 安装 APK 做了什么
    - getSystemService 如何工作
    - A 跳 B 两个 Activity 生命周期顺序
    - onSaveInstanceState 调用时机

    **## 五、追问陷阱与反脆弱**
    - 陷阱1：singleTask 全局单例 -> 锚点：Task 内唯一，不同 affinity 可各有一个
    - 陷阱2：AMS 直接调 Activity 方法 -> 锚点：通过 Binder 调 ApplicationThread，再 Handler 切主线程
    - 陷阱3：安装时 dex 全量编译 -> 锚点：Android 7.0+ JIT+AOT 混合
    - 陷阱4：getApplicationContext 可以 show Dialog -> 锚点：没有 Window，需要 SYSTEM_ALERT_WINDOW 权限
    - 陷阱5：onSaveInstanceState 在 onPause 之后 -> 锚点：Android P 之后明确为 onStop 之后调用

    **## 六、关联知识点**
    - Handler 机制（ActivityThread Handler H 驱动生命周期）-> 01. Handler 笔记
    - Binder IPC（AMS 与应用进程的通信方式）-> 02. Binder 笔记
    - View 绘制（WindowManager.addView 创建 ViewRootImpl）-> 03. View 笔记
    - 插件化 Hook AMS 占坑 Activity -> 05. ClassLoader 笔记
    - 启动优化（冷启动链路分析）-> Phase 2 性能优化

    **## 七、参考资料**
    - AOSP: frameworks/base/services/core/java/com/android/server/am/
    - gityuan.com/2016/03/26/app-process-create

    内容要求：
    1. 应用启动全链路 ASCII 图必须从"用户点击"一直到"Activity.onCreate()"
    2. Activity-Window-View 层级关系必须有图解
    3. LaunchMode 必须有栈变化示例
    4. APK 安装流程必须区分 Android 7.0 前后差异
    5. 本笔记范围最广，总字数控制在 4000-6000 字
  </action>
  <verify>
    <automated>
      grep -c "Zygote" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "ActivityThread.main" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "ApplicationThread" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "ActivityRecord" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "singleTask" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "DecorView\|PhoneWindow" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "dex2oat\|packages.xml" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md" &&
      grep -c "fork" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md"
    </automated>
  </verify>
  <acceptance_criteria>
    - grep "Zygote" 返回 >= 3
    - grep "ActivityThread.main" 返回 >= 1
    - grep "ApplicationThread" 返回 >= 2
    - grep "ActivityRecord" 返回 >= 2
    - grep "singleTask" 返回 >= 2（且明确标注 Task 内唯一）
    - grep "DecorView|PhoneWindow" 返回 >= 2
    - grep "dex2oat|packages.xml" 返回 >= 1
    - grep "fork" 返回 >= 2
    - 文件包含七个大章节（一~七）
    - 包含应用启动全链路 ASCII 图
    - 包含 Activity-Window-View 层级图
    - 包含 LaunchMode 表格
    - 包含 APK 安装流程图
    - 包含面试问法表格（至少 10 行）
    - 包含追问陷阱章节（至少 5 个陷阱）
  </acceptance_criteria>
  <done>
    04. AMS-WMS-PMS及系统启动.md 文件存在，覆盖应用启动全链路、Activity-Window-View 三者关系、LaunchMode 四种模式、WMS Z-order、PMS APK 安装流程，所有 grep 检查项通过。
  </done>
</task>

</tasks>

<verification>
1. 文件存在：`ls "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/04. AMS-WMS-PMS及系统启动.md"`
2. 关键词检查：所有 8 个 grep 检查全部返回 >= 1
3. 结构检查：`grep -c "^## " file` >= 7
4. 行数检查：`wc -l` >= 250
</verification>

<success_criteria>
- AMS-WMS-PMS 笔记覆盖 ROADMAP 全部考点：Activity-Window-View 三者关系、AMS 驱动生命周期、ActivityRecord/TaskRecord、LaunchMode + FLAG、应用启动全链路、WMS Z-order、PMS APK 安装
- 能根据笔记描述完整的 AMS -> Zygote -> ActivityThread 链路
- 能说出 ActivityRecord 是 AMS 侧的记录对象
- singleTask 明确标注为 Task 内唯一
</success_criteria>

<output>
After completion, create `.planning/phases/01-android/01-04-SUMMARY.md`
</output>
