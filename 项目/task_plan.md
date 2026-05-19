# Task Plan — 学习模块：ANR 分析与解决

## 目标
系统掌握 Android ANR 的原理、源码、分析工具和线上监控方案，面试场景下能完整回答 [PERFORMANCE_AV.md §4](.planning/research/PERFORMANCE_AV.md) 列出的 10 道高频题，并在实战中能定位和修复真实 ANR。

## 交付物
- [ ] 原始笔记：`04. 学习_性能优化/ANR_01.基础概念.md` 补齐 + 按需新增 `ANR_02/03/04.md`
- [ ] YAML cards：5 张（id 030-034），放入 `00. learning/learning-behavior-system/states/active/`
- [ ] 模块收尾：`/gsd:note` 留档

## 知识点清单

| 卡 id | 知识点 | 对应面试考点 | 笔记现状 | sub_points 预估 |
|------|--------|------------|---------|---------------|
| 030 | ANR 原理：四类触发 + 埋雷-拆雷-爆雷模型 | 4 种超时值 / 为什么观测者和被观测者要跨线程 | 🟡 仅 Service 触发部分 | 5 |
| 031 | Service ANR 源码全流程 | AMS 埋雷-拆雷-爆雷完整时序（手写级） | ✅ 已完整（1346 行） | 6 |
| 032 | traces.txt 结构与解读 | waiting to lock / Native Blocked / 死锁识别 | ❌ 空白 | 4 |
| 033 | 线上 ANR 监控三方案 | FileObserver / Looper 耗时 / Signal(SIGQUIT)+DropBox 对比 | ❌ 空白 | 5 |
| 034 | ANR 实战案例集 | 主线程 Binder / 死锁 / WorkerThread 认知误区 | ❌ 空壳章节 | 4 |

## 阶段

学习顺序：按面试优先级 **030 → 031 → 032 → 033 → 034**（用户选项 2）

### 阶段 1：030 ANR 原理
- status: pending
- 任务：
  - [ ] 读材料：补 Activity/Input、BroadcastReceiver、ContentProvider 三类触发机制
  - [ ] 补写到 `ANR_01.基础概念.md` §2.x（或按需新建 `ANR_02.四类触发对比.md`）
  - [ ] 创建 YAML card 030（5 个 sub_points）
  - [ ] 校验入池

### 阶段 2：031 Service ANR 源码
- status: pending
- 任务：
  - [ ] 笔记已有（`ANR_01.基础概念.md` §3-5），直接拆卡
  - [ ] 创建 YAML card 031（6 个 sub_points）
  - [ ] 校验入池

### 阶段 3：032 traces.txt 解读
- status: pending
- 任务：
  - [ ] 读材料：traces.txt 文件结构、关键字段、死锁识别方法
  - [ ] 写笔记 `ANR_02.traces解读.md`（或续写 ANR_01）
  - [ ] 创建 YAML card 032（4 个 sub_points）
  - [ ] 校验入池

### 阶段 4：033 线上 ANR 监控
- status: pending
- 任务：
  - [ ] 读材料：FileObserver / Looper 耗时 / Signal+DropBoxManager 三方案 + 对比
  - [ ] 写笔记 `ANR_03.线上监控.md`
  - [ ] 创建 YAML card 033（5 个 sub_points）
  - [ ] 校验入池

### 阶段 5：034 ANR 实战案例
- status: pending
- 任务：
  - [ ] 读材料 + 构造案例：主线程 Binder 超时、锁顺序死锁、WorkerThread 异常不导致 ANR
  - [ ] 写笔记 `ANR_04.实战案例.md`（补齐原稿 §06-08）
  - [ ] 创建 YAML card 034（4 个 sub_points）
  - [ ] 校验入池

### 阶段 6：模块收尾
- status: pending
- 任务：
  - [ ] 校验 5 张卡的 `related_cards` 互相关联
  - [ ] 运行 `/gsd:note` 留档

## 关键参考
- 规划总览：[规划.md](规划.md)
- ANR 面试考点：[PERFORMANCE_AV.md §4](.planning/research/PERFORMANCE_AV.md)
- 模块工作流：[new-module-workflow.md](00. learning/learning-behavior-system/new-module-workflow.md)
- 间隔规则：[interval-rules.md](00. learning/learning-behavior-system/interval-rules.md)
- 子知识点规则：[sub-points-rules.md](00. learning/learning-behavior-system/sub-points-rules.md)
- 现有初稿：[ANR_01.基础概念.md](04. 学习_性能优化/ANR_01.基础概念.md)

## 遇到的错误
（暂无）

---

# Task Plan — 学习模块：Android 启动优化

## 目标
系统掌握 Android 启动优化的测量口径、全流程时序、Systrace 解读、主线程瓶颈识别与优化策略决策，面试场景下能完整回答启动优化高频题，并能在实战中建立基线、定位瓶颈、防止劣化。

## 交付物
- [ ] 原始笔记：`04. 学习_性能优化/启动优化_0N.md`（按轮次拆文件）
- [ ] YAML cards：6 张（id 036-041），放入 `states/active/`
- [ ] 模块收尾：`/gsd:note` 留档

## 知识点清单

| 卡 id | 知识点 | 轮次 | 核心考点 | sub_points 预估 |
|-------|--------|------|---------|----------------|
| 036 | 启动类型与测量口径 | 1 | 冷/温/热定义、TTID vs TTFD、双端口径错位（起点+终点）、选型原则 | 5 |
| 037 | 启动全流程时序 | 2 | Zygote→attachBaseContext→ContentProvider→onCreate→首帧，各阶段耗时特征 | 6 |
| 038 | Systrace/Perfetto 解读 | 3 | lane 含义（UI/RenderThread/Binder/JIT/GC）、找瓶颈路径（仅解读，不含采集） | 5 |
| 039 | 主线程瓶颈五类 Pattern | 4 | ①同步IO ②类加载&反射 ③Inflate过深 ④锁/Binder同步 ⑤主线程任务堆积 | 5 |
| 040 | 优化策略全景与 ROI 取舍 | 5 | 真实性能vs感知性能根分叉、App Startup编排、冷转温策略、各手段落地成本与进程级代价 | 5 |
| 041 | 实战 SOP + 工具采集 + 防劣化 | 6 | am start -W / Perfetto采集 / CI基线 / 回归检测，与 ANR 链路对照 | 4 |

## 阶段

学习顺序：**036 → 037 → 038 → 039 → 040 → 041**（按轮次递进，Claude教授→提问确认→创建YAML卡片）

### 阶段 1：轮次 1 — 启动类型与测量口径
- status: complete
- 任务：
  - [x] Claude 教授：冷/温/热启动、TTID/TTFD、双端口径错位
  - [x] 提问确认理解（逐题交互）
  - [x] 写笔记 `04. 学习_性能优化/启动优化_02.测量与指标.md`
  - [x] 创建 YAML card 036
  - [x] 校验入池

### 阶段 2：轮次 2 — 启动全流程时序
- status: complete
- 任务：
  - [x] Claude 教授：Zygote fork → attachBaseContext → ContentProvider → onCreate → 首帧
  - [x] 提问确认理解（via 精读 5 阶段）
  - [x] 笔记复用 `04. 学习_性能优化/启动优化_03.启动流程.md`
  - [x] 创建 YAML card 037
  - [x] 校验入池

### 阶段 3：轮次 3 — Systrace/Perfetto 解读
- status: complete
- 任务：
  - [x] Claude 教授：lane 结构、关键事件、找瓶颈路径（纯解读视角）
  - [x] 提问确认理解（对着真实 App trace 实操）
  - [ ] 写笔记 `04. 学习_性能优化/启动优化_04.Systrace解读.md`（待补）
  - [ ] card 038：知识点稀薄，与轮次6实战合并记录
  - [ ] 校验入池

### 阶段 4：轮次 4 — 主线程瓶颈五类 Pattern
- status: in_progress (2026-05-10)
- 任务：
  - [ ] Claude 教授：五类瓶颈识别方法 + 修复方向（框架级，每类讲"怎么识别+怎么修"两点）
  - [ ] 提问确认理解
  - [ ] 写笔记 `04. 学习_性能优化/启动优化_05.主线程瓶颈.md`
  - [ ] 创建 YAML card 039
  - [ ] 校验入池

### 阶段 5：轮次 5 — 优化策略全景与 ROI 取舍
- status: pending
- 任务：
  - [ ] Claude 教授：决策树根分叉 + App Startup + 冷转温 + 进程级代价
  - [ ] 提问确认理解
  - [ ] 写笔记 `04. 学习_性能优化/启动优化_06.优化策略.md`
  - [ ] 创建 YAML card 040
  - [ ] 校验入池

### 阶段 6：轮次 6 — 实战 SOP + 工具采集 + 防劣化
- status: pending
- 任务：
  - [ ] Claude 教授：测量工作流 + Perfetto采集 + CI基线 + 回归检测
  - [ ] 提问确认理解
  - [ ] 写笔记 `04. 学习_性能优化/启动优化_07.实战SOP.md`
  - [ ] 创建 YAML card 041
  - [ ] 校验入池

### 阶段 7：模块收尾
- status: pending
- 任务：
  - [ ] 校验 6 张卡的 `related_cards` 互相关联
  - [ ] 运行 `/gsd:note` 留档

## 关键参考
- 规划总览：[规划.md](规划.md)
- 模块工作流：[new-module-workflow.md](00. learning/learning-behavior-system/new-module-workflow.md)
- 间隔规则：[interval-rules.md](00. learning/learning-behavior-system/interval-rules.md)
- 子知识点规则：[sub-points-rules.md](00. learning/learning-behavior-system/sub-points-rules.md)

## 遇到的错误
（暂无）

---

# Today's Plan — 2026-05-10

## 目标
学习 + 复习并行：完成昨日（2026-05-09）复习的 yaml 状态同步，创建 039 主线程瓶颈卡片，针对 037 弱点专项回炉。

## 执行顺序（已确认）

### 阶段 A：状态同步（quick admin, 10-15 分钟）
- status: complete
- 实际间隔规则采用 [interval-rules.md](00. learning/learning-behavior-system/interval-rules.md)：按 consecutive_success 查表（0/1/2/4/7/14/21/30/45/60/90），全部 result=good → cs+1
- 任务：
  - [x] 030 yaml：last_study=2026-05-09, cs 4→5, next_review=2026-05-30（+21天）
  - [x] 031 yaml：last_study=2026-05-09, cs 4→5, next_review=2026-05-30
  - [x] 032 yaml：last_study=2026-05-09, cs 2→3, next_review=2026-05-16（+7天）
  - [x] 033 yaml：last_study=2026-05-09, cs 1→2, next_review=2026-05-13（+4天）
  - [x] 034 yaml：last_study=2026-05-09, cs 4→5, next_review=2026-05-30
  - [x] 036 yaml：last_study=2026-05-09, cs 2→3, next_review=2026-05-16

### 阶段 B：创建 039 主线程瓶颈五类 Pattern（heavy, 1.5-2 小时）
- status: pending
- 任务：
  - [ ] Claude 教授五类 Pattern（框架级）：
    - ① 同步 IO：识别+修复
    - ② 类加载 & 反射：识别+修复
    - ③ Inflate 过深：识别+修复
    - ④ 锁 / Binder 同步：识别+修复
    - ⑤ 主线程任务堆积：识别+修复
  - [ ] 框架级对比表（五类的根因、识别工具、修复方向归纳）
  - [ ] 提问确认理解
  - [ ] 写笔记 `04. 学习_性能优化/启动优化_05.主线程瓶颈.md`
  - [ ] 创建 YAML card 039
  - [ ] 同步阶段 4 task_plan status → complete

### 阶段 C：037 弱点专项回炉（30-45 分钟）
- status: pending
- 任务：
  - [ ] 针对 ✗ / ⚠️ 条目选 5-7 个精准提问（main()四步, attach内部, LoadedApk术语, installContentProviders, performLaunchActivity setTheme, setContentView第3阶段表述）
  - [ ] 答对 → ✓×N 计数累加；仍错 → 保留追问

## 关键约束
- 控制单次任务量，每阶段完成后 check-in
- 复习用确认模式 + 框架题，不深究实现细节
- 弱点不删除，✓×N 计数累加

## 遇到的错误
（暂无）

---

# Task Plan — 启动流程笔记精读：启动优化_03.启动流程.md

## 目标
精读并内化 `04. 学习_性能优化/启动优化_03.启动流程.md`（1030 行），掌握从 Launcher 点击到首帧上屏的完整 16 阶段时序、关键对象职责、线程地图，以及 11 个易错校准点。为 card 037 打好基础，并校准笔记中标注 `[未推导]` 的阶段 13-16。

## 交付物
- [ ] 16 阶段时序能不看笔记口述
- [ ] 11 个易错校准点全部能默写推导
- [ ] 阶段 13-16 的 [未推导] 标签通过对话校准后删除

## 阶段

### 阶段 1：进程链路（系统侧）
- status: complete
- 涵盖：笔记 §二 阶段 1~3（Launcher → ATMS/AMS → Zygote → fork）
- 关联校准点：校准 1（fork 返回值方向）
- 任务：
  - [x] 讲解+确认：Launcher → ATMS/AMS（Android 10 分家背景）
  - [x] 讲解+确认：AMS → Zygote（为什么用 socket 不用 Binder）
  - [x] 讲解+确认：fork() 父子分叉，返回值含义与原因

### 阶段 2：主线程建立 + 双向 Binder 通道，和系统建立联系
- status: complete
- 涵盖：笔记 §二 阶段 4~6（ActivityThread.main → attach → bindApplication）
- 关联校准点：校准 2（代理/本体位置）、校准 3（ApplicationThread 创建时机）、校准 5（不是线程）
- 任务：
  - [x] 讲解+确认：ActivityThread.main() 三件事
  - [x] 讲解+确认：thread.attach() 建立双向 Binder 通道
  - [x] 讲解+确认：AMS 反向调 bindApplication，Binder 线程→主线程转手机制

### 阶段 3：Application 初始化序列
- status: complete
- 涵盖：笔记 §二 阶段 7（handleBindApplication 5 步）
- 关联校准点：校准 4（bindApplication vs Application.onCreate）、校准 10（ContentProvider 先于 Application.onCreate）
- 任务：
  - [x] 讲解+确认：进程身份设置 + LoadedApk（ClassLoader 准备）
  - [x] 讲解+确认：makeApplication（为什么必须用反射）
  - [x] 讲解+确认：installContentProviders（串行主线程 + 第三方夹带问题）
  - [x] 讲解+确认：Application.onCreate 时的系统快照状态

### 阶段 4：Activity 启动 + Starting Window
- status: complete
- 涵盖：笔记 §二 阶段 8~12
- 关联校准点：校准 6（onResume ≠ 启动完成）、校准 7（setContentView 不跑 measure）、校准 8（三回调同一调用栈）、校准 9（无参构造）、校准 11（Starting Window）
- 任务：
  - [x] 讲解+确认：Starting Window 机制（Android 11 vs 12+）
  - [x] 讲解+确认：LAUNCH_ACTIVITY 消息处理路径
  - [x] 讲解+确认：performLaunchActivity（Activity.attach + PhoneWindow 诞生）
  - [x] 讲解+确认：setContentView 三阶段（DecorView + LayoutInflater + View 树）
  - [x] 讲解+确认：onCreate/onStart/onResume 同一调用栈的工程含义

### 阶段 5：渲染管线（[未推导] 节点优先校准）
- status: complete
- 涵盖：笔记 §二 阶段 13~16（全部标注 [未推导]）
- 任务：
  - [x] 推导校准：ViewRootImpl 介入时机（onResume → WindowManager.addView）
  - [x] 推导校准：Choreographer + vsync 机制
  - [x] 推导校准：performTraversals（measure/layout/draw + DisplayList）
  - [x] 推导校准：RenderThread + SurfaceFlinger + 首帧上屏（TTID 终点）
  - [x] 更新笔记：删除已校准节点的 [未推导] 标签

## 横切主题（各阶段穿插）
- **11 个易错校准点**（§五）：每阶段结束对照验证
- **关键对象卡片**（§三）：阶段 2-4 完成后集中过一遍
- **线程地图**（§四）：阶段 5 后结合渲染管线理解
- **优化切入表**（§六）：全部阶段完成后用作收尾复盘

## 遇到的错误
（暂无）
