# AI Agent V2 · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：深入
> 文档数量因人而异，但掌握内容不打折扣。
> 配套源码：`/Users/wdz/develop/work/Android/ovopark/@flutterMode/FlutterBoostExample/flutter_module/lib/ai_agent_v2`
> 参考表达：同级目录 `首页启动优化`，采用「项目骨架 + 机制注脚 + 面试话术」的组织方式。
> 本课目标：把 `ai_agent_v2` 从“我参与了一个 AI 聊天页”升级成面试里可讲清楚的项目资产：能讲业务目标、架构分层、SSE 流式状态机、用户确认 interrupt、历史恢复、工程取舍和可追问细节。

## 核心掌握项

完成本课题后，你将能够：

### 模块一 · 项目口径与主链路
- [x] 能用 2 分钟讲清 AI Agent V2 的业务背景：门店 AI 助手、流式对话、多模态附件、定时任务、检测报告和人工确认闭环
- [x] 能画出 FlutterBoost 路由进入后的主链路：`old_module` -> `AgentPageFactory` -> `ServiceLocatorV2` -> `AgentChatPageV3`
- [x] 能解释 `core / application / infrastructure / presentation` 四层各自职责，并说明为什么这个模块从旧 MVI 简化成事件驱动架构

### 模块二 · AGUI/SSE 流式协议与状态机
- [ ] 能讲清发送消息的完整链路：UI -> `ChatController` -> `AguiClient` -> `/ovopark-agent/run` -> SSE -> `EventParser` -> 时间线 UI
- [ ] 能解释 `RUN_STARTED / TEXT_MESSAGE_* / TOOL_CALL_* / CUSTOM on_interrupt / MESSAGES_SNAPSHOT` 这些事件如何映射成前端状态
- [ ] 能说明为什么要用 `ChatItem` sealed class 表达时间线，而不是直接用 Map 或一个大 message model
- [ ] 能解释流式文本、工具调用状态、思考中占位符、消息数量裁剪这几个细节的工程价值

### 模块三 · Interrupt 人机协作与业务卡片
- [ ] 能讲清 interrupt 的本质：后端 agent 执行到高风险/需确认节点时暂停，由前端渲染确认卡片并 resume
- [ ] 能解释 `InterruptCard + InterruptStrategyFactory + strategies/*` 的策略模式，为什么适合任务创建、任务删除、标准增删改等多种确认场景
- [ ] 能讲清 `StoreDeviceSelectorCard` 如何把后端推荐、默认绑定、本地门店设备接口组合成可操作的绑定卡片

### 模块四 · 历史消息恢复、任务列表与跨端集成
- [ ] 能讲清历史恢复链路：`getConversations` 找最新 thread -> `connectToThread` -> 首个 `MESSAGES_SNAPSHOT` -> `MessageSnapshotConverter`
- [ ] 能解释定时任务列表/执行历史为什么走 REST repository，而实时对话为什么走 AGUI SSE client
- [ ] 能说明 Flutter 与 Native 的图片/文件选择、路由参数、token/header、语言参数如何协同

### 模块五 · 面试表达与追问防守
- [ ] 能用「背景 -> 难点 -> 架构 -> 链路 -> 取舍 -> 结果」讲出一版完整项目经历
- [ ] 能稳接高频追问：为什么不用 WebSocket、为什么只发送当前消息、断流/超时怎么处理、如何避免流式 UI 频繁全量刷新、策略模式是否过度设计
- [ ] 能把该项目迁移表达成通用能力：复杂前端状态建模、事件驱动 UI、AI agent 人机协作闭环、FlutterBoost 混合栈集成

## 不在本课题范围内

- 后端大模型 agent 的内部规划、工具执行和 prompt 设计细节
- SSE 协议服务端实现细节，只讨论 Flutter 端消费和状态建模
- Flutter 渲染管线、Element 树 diff、平台线程模型的完整源码
- 旧版 `ai_agent` MVI 模块的完整复盘，只在需要解释 V2 重构取舍时对比引用
- UI 视觉稿还原细节，本课重点是面试中的架构与工程表达

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 模块一全部：项目背景、入口链路、四层职责、主数据流、2 分钟面试表达骨架 | 2026-06-29 |
