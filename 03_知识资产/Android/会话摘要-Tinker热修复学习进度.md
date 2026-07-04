# 热修复与ANR治理学习 · 会话摘要（用于导入新对话续接）

## 背景

- 用户是Android开发者，准备大厂面试，主题：ANR治理 + Tinker热修复。
- 学习方式：先用`grilling` skill压力测试工程设计决策，再用`bloom:bloom-tutor` skill做苏格拉底式逐篇教学（一次一篇文档，读完反馈才出下一篇）。
- 笔记库位置：`/Users/wdz/develop/interest/Today-I-learned/Android-Interview/03_知识资产/Android/`（用户的真实知识库，所有学习产出应放这里，不要留在代码仓库里）。
- 参考代码仓库：`/Users/wdz/develop/work/Android/tinker-official-clean`（Tinker官方开源仓库，可直接读源码作为学习素材）。

## 一、grill阶段敲定的工程设计（两个原始面试问题的完整答案框架）

原始面试问题：
1. ANR治理后，如何将热修复代码推给用户？
2. 如何和灰度一起，控制部分用户执行修复代码，用Bugly看ANR是否收敛，判断是否解决问题，最终发全量包？

敲定的完整链路（六步，已在课程1里逐步讲透）：

1. **修复**：ANR定位后，用Tinker生成基于当前基准包版本的差分补丁（dex/so/资源级）。
2. **推送（Q1）**：补丁上传到分发服务；分发服务=补丁托管+灰度决策两层解耦；客户端（`SamplePatchListener.patchCheck()`）只做安全兜底熔断（空间/内存/崩溃次数超限），不参与灰度圈选。
3. **灰度圈选（Q2上半）**：服务端按Bugly上issue的机型/系统/地域分布决策——分布集中（单一机型或低端机）用定向灰度，分布均匀用随机比例灰度；同期预留不下发补丁的对照组。
4. **收敛判断（Q2下半）**：用"影响设备数/组内活跃设备数"的比率对比（灰度组vs对照组同期），不用绝对数；判定收敛需三条件同时满足：最小样本量、最短观察窗口（如7天覆盖完整周期）、比率下降幅度达标。
5. **止血**：未达标/恶化时两级处理——先停止扩量（服务端灰度比例打回0），严重时（新增崩溃/白屏等）才主动回滚（下发清除补丁指令）；Tinker客户端熔断只防崩溃不防ANR恶化，ANR止血必须服务端灰度监控主动触发。
6. **全量收口**：灰度100%+确认收敛后，补丁只解决存量用户；源码改动必须走代码评审合并回主干，随下次全量发布，否则新装用户/下次全量包依然带bug。

## 二、课程1：ANR热修复灰度发布策略（已完成，5篇全部学完）

**路径**：`/Users/wdz/develop/interest/Today-I-learned/Android-Interview/03_知识资产/Android/ANR热修复灰度发布策略/`（已从代码仓库迁移到笔记库）
**文件**：`syllabus.md` + `01.md`~`05.md`（评估篇），12项掌握项全部勾选完成`[x]`

模块内容速览：

- **模块一（01.md）分发架构与职责边界**：签到流程（客户端上报设备id/版本/机型系统地域 → 服务端匹配灰度规则 → 返回补丁地址或无）；补丁托管vs灰度决策两层解耦；服务端圈人做决策+客户端`patchCheck()`做实时熔断的分工；Bugly热更新控制台 vs 自建对照表。
- **模块二（02.md）灰度圈选策略**：先做"聚合分诊"判断ANR根因类型——分布均匀→代码问题→随机灰度；集中低端机型→性能临界→定向低端；集中单一机型→厂商定制冲突→定向该机型；集中地域→代码分支问题→定向该地域。定向vs随机本质是"有效曝光密度"问题（数字例子：大盘0.1%受影响，90%集中在占大盘2%的机型上，该机型内发生率4.5%=45倍大盘均值，定向比随机能用小50倍的曝光量拿到同等样本量）。对照组必须同期+同来源，排除时间混淆变量。
- **模块三（03.md）收敛判断度量方法论**：比率而非绝对数（灰度组vs对照组体量不对等，尤其灰度组还在放量扩大，正确例子是同一观察窗口内2万台/150命中=0.75% vs 2000台/30命中=1.5%，不能用灰度组自己跨周的纵向数字）。收敛三条件：最小样本量（防偶然波动）、最短观察窗口（防周期性误判）、比率下降阈值（防"降一点就算数"）。
- **模块四（04.md）止血回滚与全量收口**：停止扩量（只影响未签到新设备，已生效设备不受影响）vs 主动回滚（已生效设备下次冷启动退回基准版本，有代价），选择依据是"止血代价"vs"放任代价"哪个更大。Tinker客户端熔断（`fastCrashCount`/`ERROR_PATCH_CRASH_LIMIT`）只针对`UncaughtExceptionHandler`捕获的崩溃，ANR走系统Watchdog检测，完全不同链路，客户端框架感知不到，止血必须服务端主导。全量收口：补丁只是阶段性止血，代码必须走评审合并回主干进入下次全量包。
- **评估篇（05.md）**：完整链路复述范文，可直接用于面试。

## 三、课程2：tinker热修复原理（进行中，仅完成01.md）

**路径**：`/Users/wdz/develop/work/Android/tinker-official-clean/tinker热修复原理/`（**尚未迁移到笔记库**，仍在代码仓库里，需要时可以照课程1的方式`mv`过去）
**文件**：`syllabus.md` + `01.md`

大纲（标准深度，4模块12项）：

- 模块一：整体架构与补丁生效时机（01.md已完成，3项已勾选`[x]`）
- 模块二：Dex补丁与ClassLoader替换机制（待学）
- 模块三：So库与资源补丁（待学）
- 模块四：差分算法与安全边界（待学）

01.md已讲内容：
- Android启动时序矛盾（`attachBaseContext()`早于`onCreate()`，补丁必须在业务代码接触自身类之前完成环境替换）
- `TinkerApplication`（壳）+ `ApplicationLike`（业务，通过字符串`delegateClassName`反射构造实现编译期解耦）的设计
- `tryLoad()`在`attachBaseContext()`里通过反射调用`loaderClassName`（默认`TinkerLoader`）完成加载
- "合并"（后台`:patch`独立进程一次性完成dex diff+merge+dexopt预编译）和"加载"（下次冷启动`tryLoad()`轻量接入）拆成两阶段两进程的设计原因

**不在范围内**（已在syllabus声明）：灰度分发工程设计（已在课程1覆盖）、ArkHot等其他厂商方案、差分算法代码级实现走读、非Android平台。

关键源码位置（供后续模块参考，均在`tinker-official-clean`仓库内）：
- `tinker-android/tinker-android-loader/src/main/java/com/tencent/tinker/loader/`下核心类：
  - `TinkerApplication.java`、`TinkerLoader.java`、`AbstractTinkerLoader.java`（已读，模块一素材）
  - `TinkerDexLoader.java`、`TinkerClassLoader.java`、`SystemClassLoaderAdder.java`、`NewClassLoaderInjector.java`、`TinkerDexOptimizer.java`（模块二素材）
  - `TinkerSoLoader.java`（模块三素材-so库）
  - `TinkerResourceLoader.java`、`TinkerResourcePatcher.java`、`TinkerResourcesKey.java`（模块三素材-资源）
  - `ShareBsDiffPatchInfo.java`、`ShareDexDiffPatchInfo.java`、`ShareOatUtil.java`、`ShareSecurityCheck.java`（模块四素材-差分算法与安全校验）
- `tinker-sample-android/app/src/main/java/tinker/sample/android/reporter/SamplePatchListener.java`（`patchCheck()`熔断逻辑，课程1和课程2都引用过）
- 仓库最近commit `c3b6597c`/`5388f207`提到"resource id misaligned check"的修复——与模块三"资源id对齐问题"直接相关，值得作为真实案例参考

## 四、下一步学习计划（用户已确认）

1. 继续把`tinker热修复原理`剩余三个模块（Dex补丁/So库资源补丁/差分算法安全边界）学完。
2. **新增学习目标**：补丁构建阶段的工程细节（尚未纳入任何课程大纲，需要新建大纲条目或作为`tinker热修复原理`的扩展模块）——内容方向包括：`tinker-patch-cli`/`tinker-patch-gradle-plugin`的构建流程、两次打包必须基于同一份基准（baseApk/mapping.txt）对齐要求、ProGuard混淆映射一致性、多渠道包处理注意事项。相关源码在`tinker-build/tinker-patch-cli`和`tinker-build/tinker-patch-gradle-plugin`模块（尚未探索）。
3. （已讨论、优先级较低、可选，未要求学习）Tinker与AndFix/Sophix/Robust等其他热修复方案的横向对比，仅作为已识别的可选延伸方向记录。

## 五、学习方式偏好（供新对话沿用）

- 使用bloom skill的标准流程：一次一篇文档，读完反馈后才生成下一篇；续篇必须先复盘上一篇思考题+解答`???`再进新内容。
- 用户喜欢先自己组织内容结构/给出理解，再让我校对补充（例如课程1的01.md、02.md都是用户提出重排结构后由我合并进正文），不是单向灌输。
- 用户会认真核对内容里的数字/逻辑推导，发现错误会当场指出（如03.md最初的"绝对数vs比率"例子用了不恰当的纵向对比，被用户指出后修正为同期灰度组vs对照组的正确例子）——生成教学内容时数字例子要经得起推敲，举例论证要自洽，不能违反课程自己强调的原则。
- 默认学习深度：标准（3-4模块，10-12项掌握项）。
