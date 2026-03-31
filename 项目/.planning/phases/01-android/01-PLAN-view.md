---
phase: 01-android
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - "04. 学习_Android核心原理/03. View绘制体系.md"
autonomous: true
requirements: [VIEW-01]

must_haves:
  truths:
    - "笔记明确 ViewRootImpl.performTraversals() 是 View 绘制的触发入口"
    - "笔记覆盖 MeasureSpec 三种模式（EXACTLY/AT_MOST/UNSPECIFIED）及父子 View 测量传递"
    - "笔记区分 requestLayout() 和 invalidate() 的触发路径差异"
    - "笔记包含 Choreographer VSYNC 信号驱动帧调度的机制"
    - "笔记包含硬件加速下 DisplayList/RenderNode 和 RenderThread 机制"
    - "笔记解释了自定义 View wrap_content 不生效的根因"
  artifacts:
    - path: "04. 学习_Android核心原理/03. View绘制体系.md"
      provides: "View 绘制体系完整面试笔记"
      contains: "performTraversals"
      min_lines: 200
  key_links:
    - from: "03. View绘制体系.md"
      to: "Choreographer"
      via: "VSYNC 信号触发 doFrame 进而触发 performTraversals"
      pattern: "VSYNC.*performTraversals"
---

<objective>
撰写 `03. View绘制体系.md` 面试笔记，完整覆盖 View 绘制三大流程及相关机制。

Purpose: View 绘制体系是大厂面试极高频考点（每家必问），追问硬件加速和 Choreographer 是区分"用过"和"懂原理"的分水岭。需要能说出 ViewRootImpl 入口、三大流程，追问 Choreographer/VSYNC 时能继续回答。
Output: 一篇结构化的面试准备笔记文件 `04. 学习_Android核心原理/03. View绘制体系.md`
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
  <name>Task 1: 撰写 View 绘制体系面试笔记</name>
  <files>04. 学习_Android核心原理/03. View绘制体系.md</files>
  <read_first>
    - .planning/phases/01-android/01-RESEARCH.md（Topic 3: View 绘制体系部分，含核心链路图和子概念表）
    - .planning/research/CORE_ANDROID.md（View 绘制考点详情：典型问题、深度档次、陷阱）
    - .planning/research/INTERVIEW_STRATEGY.md（笔记模板结构）
  </read_first>
  <action>
    确保目录 `04. 学习_Android核心原理/` 存在。

    撰写 `03. View绘制体系.md`，使用以下结构：

    **# 03. View 绘制体系**

    **> 一句话总结（面试开场句）：** View 绘制由 ViewRootImpl.performTraversals() 触发，经过 measure（确定大小）-> layout（确定位置）-> draw（绘制内容）三大流程，由 Choreographer 接收 VSYNC 信号驱动帧调度，硬件加速下绘制指令记录到 DisplayList 由 RenderThread 异步提交 GPU。

    **## 一、核心原理链路**
    绘制 ASCII 流程图，内容必须包含：
    ```
    VSYNC 信号到来
      -> Choreographer.doFrame()
          -> postSyncBarrier（同步屏障，保证绘制优先）
          -> 发送异步消息（traversal runnable）
          -> ViewRootImpl.performTraversals()
              -> performMeasure()
                  -> View.measure() -> onMeasure()
              -> performLayout()
                  -> View.layout() -> onLayout()
              -> performDraw()
                  -> View.draw() -> onDraw()
                      [硬件加速路径]
                      -> updateDisplayListIfDirty()
                      -> RenderNode.beginRecording()
                      -> Canvas 操作序列化为 DisplayList
                      -> RenderThread 提交到 GPU
    ```

    **## 二、关键机制详解**

    ### 2.1 ViewRootImpl 是绘制入口
    - ViewRootImpl 不是 View，不是 Activity，而是 View 树和 WindowManager 之间的桥梁
    - WindowManager.addView() 时创建 ViewRootImpl，setView() 建立与 DecorView 的关联
    - performTraversals() 是整个绘制流程的入口方法
    - checkThread() 检查的是"创建 ViewRootImpl 的线程"，不是严格的"主线程"（可在子线程创建 Window+Looper 绕过）

    ### 2.2 MeasureSpec 三种模式
    用表格格式：
    | 模式 | 含义 | 对应场景 |
    - EXACTLY：精确大小，match_parent 或固定 dp 值
    - AT_MOST：最大不超过父容器剩余空间，wrap_content
    - UNSPECIFIED：无限制，ScrollView 子 View / RecyclerView 子 View
    - 父 View 通过 getChildMeasureSpec(parentSpec, padding, childDimension) 合成子 View 的 MeasureSpec
    - MeasureSpec = specMode (高2位) | specSize (低30位)，用一个 int 压缩存储

    ### 2.3 requestLayout() vs invalidate()
    用对比表格：
    | 方法 | 触发路径 | 标记 | 适用场景 |
    - requestLayout()：向上传播 PFLAG_FORCE_LAYOUT -> 触发 measure + layout + draw 全流程
    - invalidate()：标记脏区域 PFLAG_DIRTY -> 只触发 draw（硬件加速下只重录变化的 RenderNode）
    - invalidate(Rect)：标记特定矩形区域为脏
    - postInvalidateOnAnimation()：下一帧 VSYNC 时 invalidate
    - 何时用哪个：大小/位置变化用 requestLayout，仅外观变化用 invalidate

    ### 2.4 Choreographer 与 VSYNC 信号
    - Choreographer 是单例，每个线程一个（通过 ThreadLocal）
    - 注册 VSYNC 信号监听：requestNextVsync() -> SurfaceFlinger 发 VSYNC
    - VSYNC 到达 -> doFrame() -> 按顺序执行三类回调：
      (1) CALLBACK_INPUT（输入事件）
      (2) CALLBACK_ANIMATION（动画）
      (3) CALLBACK_TRAVERSAL（measure/layout/draw）
    - 帧率由 VSYNC 驱动（60Hz = 16.6ms/帧）
    - 如果 doFrame 内的操作超过 16.6ms，当前帧来不及绘制 -> 掉帧

    ### 2.5 硬件加速 DisplayList / RenderNode
    - 软件绘制：CPU 直接在 Bitmap 上 draw -> Surface -> SurfaceFlinger
    - 硬件加速：Canvas 操作记录到 DisplayList（绘制指令缓存）-> RenderThread 提交 GPU 执行
    - RenderNode：每个 View 对应一个 RenderNode，持有 DisplayList
    - View 变化时 invalidate -> 只重录变化的 RenderNode 的 DisplayList，而非整棵 View 树
    - View.setLayerType(LAYER_TYPE_HARDWARE)：将 View 渲染到 GPU 纹理缓存

    ### 2.6 RenderThread 与 MainThread 协作
    - MainThread：录制 DisplayList（measure/layout/record display list）
    - RenderThread：提交 DisplayList 到 GPU 执行绘制（dequeue buffer -> draw -> swap buffer）
    - 两线程并行：MainThread 录制下一帧时，RenderThread 可能还在绘制上一帧
    - syncFrameState()：MainThread 与 RenderThread 的同步点

    ### 2.7 wrap_content 不生效根因
    - View.onMeasure() 默认实现调用 getDefaultSize()
    - getDefaultSize() 对 AT_MOST 和 EXACTLY 返回相同值 = specSize（父容器剩余空间）
    - 因此自定义 View 不重写 onMeasure 时，wrap_content 效果等同于 match_parent
    - 解决：重写 onMeasure，在 AT_MOST 模式下计算实际内容大小并调用 setMeasuredDimension()

    **## 三、为什么这么设计（追问准备）**
    - 为什么三大流程必须按 measure -> layout -> draw 顺序？size 决定 position 决定 paint
    - 为什么要用 MeasureSpec 而不是直接传 int 大小？需要同时传递 mode（约束类型）和 size
    - 为什么硬件加速下用 DisplayList 而不是直接 draw？DisplayList 可缓存不变的绘制指令，增量更新
    - 为什么 View 刷新要在"创建 ViewRootImpl 的线程"？ViewRootImpl.checkThread() 是为了保证 UI 操作单线程化，避免并发 crash

    **## 四、高频面试问法 & 答题要点**
    表格格式，至少 8 个问题：
    - View 绘制流程从哪里开始触发
    - MeasureSpec 三种模式的区别
    - requestLayout 和 invalidate 的区别
    - 硬件加速下 DisplayList 是什么
    - Choreographer 如何与 VSYNC 协作
    - 为什么 View 刷新要在主线程
    - 自定义 View wrap_content 不生效的原因
    - View.draw() 的绘制步骤

    **## 五、追问陷阱与反脆弱**
    - 陷阱1：说"View 只能在主线程更新" -> 锚点：是"创建 ViewRootImpl 的线程"，checkThread() 的实际逻辑
    - 陷阱2：onMeasure 只调用一次 -> 锚点：可能多次调用（LinearLayout weight 会两次 measure）
    - 陷阱3：invalidate 触发 measure -> 锚点：只触发 draw，不走 measure/layout
    - 陷阱4：硬件加速所有操作都支持 -> 锚点：Canvas 部分方法不支持硬件加速（如 drawBitmapMesh）

    **## 六、关联知识点**
    - 事件分发机制（dispatchTouchEvent / onInterceptTouchEvent / onTouchEvent）
    - Choreographer VSYNC 掉帧分析 -> 卡顿优化笔记（Phase 2）
    - RecyclerView 四级缓存（Scrap/Cache/ViewCacheExtension/RecycledViewPool）
    - 自定义 View 实战经验

    **## 七、参考资料**
    - AOSP: frameworks/base/core/java/android/view/ViewRootImpl.java, View.java
    - Android 开发艺术探索 第 4 章

    内容要求：
    1. ASCII 流程图展示完整的 VSYNC -> performTraversals -> 三大流程路径
    2. 对比表格清晰展示 requestLayout vs invalidate 差异
    3. 硬件加速路径必须区分 MainThread 和 RenderThread 的职责
    4. wrap_content 根因分析必须包含 getDefaultSize() 源码行为
    5. 总字数控制在 3000-5000 字
  </action>
  <verify>
    <automated>
      grep -c "performTraversals" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "EXACTLY\|AT_MOST\|UNSPECIFIED" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "requestLayout" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "invalidate" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "Choreographer" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "VSYNC" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "DisplayList\|RenderNode" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md" &&
      grep -c "wrap_content\|getDefaultSize" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md"
    </automated>
  </verify>
  <acceptance_criteria>
    - grep "performTraversals" 返回 >= 2
    - grep "EXACTLY|AT_MOST|UNSPECIFIED" 返回 >= 3（三种模式都出现）
    - grep "requestLayout" 返回 >= 2
    - grep "invalidate" 返回 >= 2
    - grep "Choreographer" 返回 >= 3
    - grep "VSYNC" 返回 >= 3
    - grep "DisplayList|RenderNode" 返回 >= 2
    - grep "wrap_content|getDefaultSize" 返回 >= 2
    - 文件包含七个大章节（一~七）
    - 包含 ASCII 流程图
    - 包含 requestLayout vs invalidate 对比
    - 包含面试问法表格（至少 8 行）
    - 包含追问陷阱章节（至少 4 个陷阱）
  </acceptance_criteria>
  <done>
    03. View绘制体系.md 文件存在，覆盖 ViewRootImpl 入口、三大流程、MeasureSpec、requestLayout/invalidate 差异、Choreographer/VSYNC、硬件加速、wrap_content 根因，所有 grep 检查项通过。
  </done>
</task>

</tasks>

<verification>
1. 文件存在：`ls "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/03. View绘制体系.md"`
2. 关键词检查：所有 8 个 grep 检查全部返回 >= 1
3. 结构检查：`grep -c "^## " file` >= 7
4. 行数检查：`wc -l` >= 200
</verification>

<success_criteria>
- View 绘制笔记覆盖 ROADMAP 全部考点：ViewRootImpl 入口、MeasureSpec 三种模式、requestLayout vs invalidate、Choreographer VSYNC、DisplayList/RenderNode、RenderThread、wrap_content 根因
- 能根据笔记说出 performTraversals 三段式，追问 Choreographer/VSYNC 时能继续回答
</success_criteria>

<output>
After completion, create `.planning/phases/01-android/01-03-SUMMARY.md`
</output>
