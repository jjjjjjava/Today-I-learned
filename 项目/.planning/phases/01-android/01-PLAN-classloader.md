---
phase: 01-android
plan: 05
type: execute
wave: 1
depends_on: []
files_modified:
  - "04. 学习_Android核心原理/05. ClassLoader与热修复.md"
autonomous: true
requirements: [CLASSLOADER-01]

must_haves:
  truths:
    - "笔记区分 PathClassLoader 和 DexClassLoader 的用途差异"
    - "笔记解释双亲委派模型及其破坏方式"
    - "笔记包含 dexElements 数组顺序决定类加载优先级的原理"
    - "笔记对比 QZone/Tinker/Sophix 三大热修复方案核心差异，且标注 pre-verify 仅 Dalvik"
    - "笔记覆盖插件化三大核心问题（类加载 + 资源加载 + 四大组件生命周期）"
    - "笔记包含 Hook AMS 占坑 Activity 方案原理"
  artifacts:
    - path: "04. 学习_Android核心原理/05. ClassLoader与热修复.md"
      provides: "ClassLoader 与热修复/插件化完整面试笔记"
      contains: "dexElements"
      min_lines: 200
  key_links:
    - from: "05. ClassLoader与热修复.md"
      to: "AMS"
      via: "Hook AMS 占坑 Activity 实现插件化"
      pattern: "Hook.*AMS.*占坑"
---

<objective>
撰写 `05. ClassLoader与热修复.md` 面试笔记，覆盖 ClassLoader 机制、热修复原理和插件化核心问题。

Purpose: ClassLoader 与热修复/插件化是美团/滴滴/字节中高级职位常考题，能说清楚 dexElements 前插方案和对比 QZone/Tinker 的核心差异是 P7 到 P8 的关键分界。
Output: 一篇结构化的面试准备笔记文件 `04. 学习_Android核心原理/05. ClassLoader与热修复.md`
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
  <name>Task 1: 撰写 ClassLoader 与热修复面试笔记</name>
  <files>04. 学习_Android核心原理/05. ClassLoader与热修复.md</files>
  <read_first>
    - .planning/phases/01-android/01-RESEARCH.md（Topic 5: ClassLoader 与热修复部分，含 dexElements 前插链路图和子概念表）
    - .planning/research/CORE_ANDROID.md（ClassLoader 考点 + 热修复/插件化考点详情）
    - .planning/research/INTERVIEW_STRATEGY.md（笔记模板结构）
  </read_first>
  <action>
    确保目录 `04. 学习_Android核心原理/` 存在。

    撰写 `05. ClassLoader与热修复.md`，使用以下结构：

    **# 05. ClassLoader 与热修复**

    **> 一句话总结（面试开场句）：** Android 通过 BaseDexClassLoader 的 dexElements 数组按顺序加载类，热修复的核心原理就是将补丁 dex 插入 dexElements[0] 使修复类优先加载；插件化则通过 DexClassLoader 加载插件 + Hook AMS 占坑实现未注册 Activity 的启动。

    **## 一、核心原理链路（热修复 dexElements 前插）**
    绘制 ASCII 流程图：
    ```
    BaseDexClassLoader.findClass(name)
      -> DexPathList.findClass(name)
          -> 遍历 dexElements[] 数组（顺序敏感！）
              -> dexElements[0].findClass()  [补丁dex]
                  -> 找到: 立即返回（不再继续遍历）
                  -> 找不到: 继续
              -> dexElements[1].findClass()  [原始dex]
                  -> 找到: 返回
                  -> 找不到: 继续...
              -> ClassNotFoundException

    热修复原理:
      反射获取 DexPathList.dexElements
      -> 创建补丁 dex 的 Element
      -> 将补丁 Element 插入 dexElements[0] 位置
      -> 修复类被优先加载，原 bug 类永远不会被加载
    ```

    **## 二、关键机制详解**

    ### 2.1 Android ClassLoader 体系
    画出继承关系图：
    ```
    ClassLoader (java.lang)
      -> BootClassLoader (加载 framework 核心类)
          -> PathClassLoader (加载已安装 APK 的 classes.dex)
          -> DexClassLoader (加载任意路径的 dex/apk/jar)
              -> InMemoryDexClassLoader (Android 8.0+，从内存加载)
    ```
    - PathClassLoader vs DexClassLoader：
      - PathClassLoader：系统用来加载已安装应用的 ClassLoader，optimizedDirectory 为 null（使用默认路径）
      - DexClassLoader：可加载任意路径的 dex/apk/jar，热修复和插件化使用
      - **注意：Android 8.0+ PathClassLoader 也能加载外部 dex（optimizedDirectory 参数已废弃），但 DexClassLoader 仍是热修复/插件化的标准用法**

    ### 2.2 双亲委派模型
    - loadClass() 流程：先委托 parent.loadClass()，parent 找不到才自己 findClass()
    - 为什么这么设计：(1) 防止核心类被替换（如 java.lang.String）(2) 避免类重复加载
    - "双亲" 是翻译误导：实际是 parent（单数），一条链而非两个父
    - 破坏双亲委派的方式：
      (1) 重写 loadClass() 跳过 parent 委托（Thread.setContextClassLoader）
      (2) OSGI 热部署
      (3) 热修复通过修改 dexElements 数组绕过（不是直接破坏委派，而是在 findClass 层面前插）

    ### 2.3 BaseDexClassLoader.dexElements 数组
    - DexPathList 持有 Element[] dexElements 数组
    - findClass() 遍历 dexElements，找到第一个包含目标类的 Element 就返回
    - **顺序决定优先级：靠前的 dex 中的类优先被加载**
    - 热修复 = 反射修改 dexElements，将补丁 dex 的 Element 插到数组最前面
    - 源码调用链：BaseDexClassLoader.findClass() -> DexPathList.findClass() -> DexFile.loadClassBinaryName()

    ### 2.4 热修复三大方案对比
    用表格对比：
    | 维度 | QZone 方案 | Tinker | Sophix |
    |------|-----------|--------|--------|
    | 核心原理 | dexElements 前插 | 差量 patch 合成新 dex | 方法替换（ArtMethod） |
    | 是否需要重启 | 是（重新加载类） | 是（合成后重启生效） | 否（方法级即时替换） |
    | 粒度 | 类级别 | dex 级别 | 方法级别 |
    | patch 体积 | 完整补丁类 | bsdiff 差量（小） | 方法维度（最小） |
    | 兼容性 | Dalvik pre-verify 问题 | 好 | 依赖 ArtMethod 结构稳定性 |

    #### QZone pre-verify 问题（仅 Dalvik）
    - Dalvik 虚拟机对同一个 dex 内所有类的引用做 pre-verify 标记
    - 如果类 A（补丁 dex）引用类 B（原始 dex），跨 dex 引用导致 CLASS_ISPREVERIFIED 校验失败
    - 绕过：在所有类的构造函数中插入对独立 hack.dex 中 AntiLazyLoad 类的引用，打破 pre-verify 条件
    - **仅 Dalvik（Android < 5.0）存在，ART 无此问题**

    #### Tinker 差量 patch
    - 使用 bsdiff 算法对旧 dex 和新 dex 做差量生成 patch 文件
    - 客户端下载 patch，用 bspatch 将旧 dex + patch 合成新 dex
    - 重启后新 dex 生效
    - 优势：patch 体积小（只传差异）

    #### Sophix 方法替换
    - 修改 ArtMethod 结构体的 entry_point_ 指针，指向新方法的地址
    - 不需要重启，即时生效
    - 风险：ArtMethod 结构体在不同 Android 版本可能不同（兼容性问题）

    ### 2.5 插件化三大核心问题
    - **问题一：类加载** — 用 DexClassLoader 加载插件 APK 中的 classes.dex
    - **问题二：资源加载** — 通过反射调用 AssetManager.addAssetPath() 将插件资源路径加入
    - **问题三：四大组件生命周期** — 未在 Manifest 注册的 Activity 无法被 AMS 认可 -> 需要 Hook

    ### 2.6 Hook AMS 占坑 Activity 方案原理
    绘制流程图：
    ```
    1. 预注册: AndroidManifest.xml 中注册多个 StubActivity（占坑）

    2. 启动插件 Activity 时:
       App 调用 startActivity(PluginActivity)
       -> Hook 点1: 替换 Intent 中的 PluginActivity 为 StubActivity
       -> AMS 校验通过（StubActivity 已注册）
       -> AMS 通知应用启动 StubActivity

    3. 拦截 AMS 回调:
       -> Hook 点2: 拦截 ActivityThread Handler H 的 LAUNCH_ACTIVITY 消息
       -> 将 StubActivity 替换回 PluginActivity
       -> 实际创建并启动 PluginActivity
    ```
    - Hook 点 1：Hook ActivityManager.getService() 返回的 IActivityManager 代理（动态代理）
    - Hook 点 2：反射替换 ActivityThread.mH 的 mCallback
    - Android 10+ 非 SDK 接口限制加强，多个旧 Hook 方案失效

    **## 三、为什么这么设计（追问准备）**
    - 为什么用数组顺序而不是版本号判断？简单高效，数组遍历顺序天然决定优先级
    - 为什么 Tinker 要合成新 dex 而不是直接前插？避免 QZone 的 pre-verify 问题和类校验问题
    - 为什么 Sophix 方法替换有兼容性问题？ArtMethod 结构体是 ART 内部实现，不同版本偏移量可能不同
    - 为什么插件化需要 Hook AMS？AMS 校验 Manifest 中是否注册了目标 Activity

    **## 四、高频面试问法 & 答题要点**
    表格格式，至少 8 个问题：
    - PathClassLoader 和 DexClassLoader 区别
    - 双亲委派模型是什么
    - 如何破坏双亲委派
    - 热修复原理（dexElements 前插）
    - QZone/Tinker/Sophix 核心差异
    - QZone pre-verify 问题
    - 插件化三大核心问题
    - Hook AMS 占坑 Activity 怎么做
    - MultiDex 中 Class.forName 为什么失败
    - Android 10+ 非 SDK 限制对插件化的影响

    **## 五、追问陷阱与反脆弱**
    - 陷阱1：pre-verify 问题在所有 Android 版本存在 -> 锚点：仅 Dalvik（Android < 5.0），ART 无此问题
    - 陷阱2：PathClassLoader 不能加载外部 dex -> 锚点：Android 8.0+ 也可以，但 DexClassLoader 仍是标准用法
    - 陷阱3：双亲委派的"双亲"是两个父 -> 锚点：parent（单数），单链条委托
    - 陷阱4：Sophix 方法替换完全无风险 -> 锚点：ArtMethod 结构体不稳定，兼容性是最大风险
    - 陷阱5：插件化在 Android 10+ 没有影响 -> 锚点：非 SDK 接口限制加强，大量 Hook 方案失效

    **## 六、关联知识点**
    - AMS 与 Activity 启动流程（Hook AMS 是在启动流程中插入代理）-> 04. AMS 笔记
    - Binder Hook（替换 IActivityManager 代理）-> 02. Binder 笔记
    - APK 安装流程中的 dex 优化 -> 04. AMS 笔记 PMS 部分
    - MultiDex 原理（类似热修复的 dexElements 操作）

    **## 七、参考资料**
    - AOSP: libcore/dalvik/src/main/java/dalvik/system/BaseDexClassLoader.java, DexPathList.java
    - Tinker GitHub wiki
    - 美团技术团队 "Android热修复方案对比与演进"

    内容要求：
    1. dexElements 前插 ASCII 流程图必须清晰展示"遍历 -> 找到即返回"的逻辑
    2. ClassLoader 继承关系图必须完整
    3. 热修复三方案对比表格必须有：核心原理、是否重启、粒度、兼容性
    4. Hook AMS 占坑两个 Hook 点必须分别说明
    5. pre-verify 问题必须标注"仅 Dalvik"
    6. 总字数控制在 3000-5000 字
  </action>
  <verify>
    <automated>
      grep -c "dexElements" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "PathClassLoader" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "DexClassLoader" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "双亲委派" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "pre-verify\|CLASS_ISPREVERIFIED" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "Tinker" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "Sophix" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md" &&
      grep -c "占坑\|StubActivity" "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md"
    </automated>
  </verify>
  <acceptance_criteria>
    - grep "dexElements" 返回 >= 3
    - grep "PathClassLoader" 返回 >= 2
    - grep "DexClassLoader" 返回 >= 2
    - grep "双亲委派" 返回 >= 2
    - grep "pre-verify|CLASS_ISPREVERIFIED" 返回 >= 1（且标注仅 Dalvik）
    - grep "Tinker" 返回 >= 2
    - grep "Sophix" 返回 >= 1
    - grep "占坑|StubActivity" 返回 >= 2
    - 文件包含七个大章节（一~七）
    - 包含 dexElements 前插 ASCII 流程图
    - 包含 ClassLoader 继承关系图
    - 包含热修复三方案对比表格
    - 包含 Hook AMS 占坑流程图
    - 包含面试问法表格（至少 8 行）
    - 包含追问陷阱章节（至少 5 个陷阱）
  </acceptance_criteria>
  <done>
    05. ClassLoader与热修复.md 文件存在，覆盖 ClassLoader 体系、双亲委派、dexElements 前插、QZone/Tinker/Sophix 三方案对比、插件化三大问题、Hook AMS 占坑，所有 grep 检查项通过。
  </done>
</task>

</tasks>

<verification>
1. 文件存在：`ls "d:/Develop/Today-I-learned/项目/04. 学习_Android核心原理/05. ClassLoader与热修复.md"`
2. 关键词检查：所有 8 个 grep 检查全部返回 >= 1
3. 结构检查：`grep -c "^## " file` >= 7
4. 行数检查：`wc -l` >= 200
</verification>

<success_criteria>
- ClassLoader 与热修复笔记覆盖 ROADMAP 全部考点：PathClassLoader vs DexClassLoader、双亲委派、dexElements 前插、QZone/Tinker/Sophix 对比、插件化三问题、Hook AMS 占坑
- 能根据笔记说清楚 dexElements 前插方案
- 能对比 QZone/Tinker 的核心差异
- pre-verify 问题明确标注仅 Dalvik
</success_criteria>

<output>
After completion, create `.planning/phases/01-android/01-05-SUMMARY.md`
</output>
