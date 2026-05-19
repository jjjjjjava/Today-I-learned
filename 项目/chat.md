1. 招财猫
分为两个：【前端】【招财猫】设备管理-pad跟门店绑定。   【招财猫】MoneyKitty 接入 MQTT 并对接 DMS 平台（设备门店绑定前置能力）

feat(DMS)： 迁移Pos的DMS相关代码到本项目中
feat(DMS)： 迁移 CloudPos 的 DMS 相关代码到本项目

— 平台层 / 原生 channel —


feat: features/dms/data/datasources/device_binding_api.dart
  - 新建：POST /ovopark-device-manage/feign/yzs/getYzsDeviceStatusByMac
  - 复用 NetworkManager.instance.post，body { mac }

feat: features/dms/data/models/{sync_main_device_info, device_net_info, verify_pwd_request, ctrl_device_request, device_status_response}.dart
  - 新建心跳/请求/响应数据结构，对应 CloudPos DMSModels.kt

feat: features/dms/data/repositories/dms_repository_impl.dart
  - 整合 MQTT 客户端 + 状态机 + device_info_plus
  - startConnection 两阶段：连 redirect → 等 join_network(45s) → 切真 DMS
  - _startHeartbeat：30s 周期上报，启动后立即先发一次
  - _scheduleReconnect：指数退避 5/10/20/40/80/128s 封顶
  - _wireMqttCallbacks：自动应答 verify_pwd / ctrlDevice
  - _canSendHeartbeat：WaitingForNetworkInfo / ConnectingToDms / HeartbeatActive / Reconnecting / Error 都允许

— DMS 领域层 —

feat: features/dms/domain/entities/dms_connection_state.dart
  - 7 状态 sealed class：Idle / ConnectingToRedirect / WaitingForNetworkInfo / ConnectingToDms / HeartbeatActive / Reconnecting / Error
  - 1:1 复刻 CloudPos DMSConnectionState

feat: features/dms/domain/entities/dms_event.dart
  - 9 事件 sealed class：StartConnection / RedirectConnected / NetworkInfoReceived / DmsConnected / HeartbeatStarted / HeartbeatFailed / ConnectionLost / ConnectionFailed / ReconnectSuccess

feat: features/dms/domain/repositories/dms_repository.dart
  - 抽象接口：connectionStateStream / startConnection / stopConnection / sendHeartbeat / sendVerifyPwdAck / sendCtrlDeviceAck / dispose

feat: features/dms/domain/usecases/{start_dms_connection, stop_dms_connection, poll_device_binding}.dart
  - poll_device_binding：每 2s 调 getYzsDeviceStatusByMac，最多 180s；返回 BindingSuccess(depId, deviceName) / BindingTimeout / BindingCancelled

— DMS 状态机基础设施 —

feat: features/dms/infrastructure/dms_state_machine.dart
  - 转换矩阵 1:1 复刻 CloudPos DMSStateMachine.kt
  - 暴露 state / stream / transition / reset / dispose
  - 中文日志：「空闲 → 连接重定向服务器」「等待服务器信息 → 连接DMS服务器」等

— DMS 服务层（单例对外）—

feat: features/dms/services/dms_manager.dart
  - 新建：≈ moneykitty 的 WebSocketManager 角色
  - 单例 DmsManager.singleton(repository)，start 幂等
  - WidgetsBindingObserver：回前台若 Error/Reconnecting 则尝试拉起

— DMS 表现层 —

feat: features/dms/presentation/providers/dms_provider.dart
  - 新建：ChangeNotifier 包装 stateStream，供页面消费

feat: features/dms/presentation/providers/device_binding_provider.dart
  - 新建：BindingState 4 态（Initializing / ShowingQr / Done / Failed）
  - start：拿 mac → 生成 qrPrefix+mac → 倒计时（180s） → HTTP 轮询绑定
  - 绑定成功：写 dms_dep_id / dms_device_name 到 SharedPreferences；autoStartDmsOnSuccess 默认 true → DmsManager.start()
  - retry / cancel；dispose 取消轮询与 timer

feat: features/dms/presentation/widgets/device_qr_view.dart
  - 新建：QrImageView 简单包装

feat: features/dms/presentation/pages/device_binding_page.dart
  - 新建：4 状态 Consumer2 渲染（DeviceBindingProvider + DmsProvider）

feat: features/dms/presentation/pages/dms_demo_entry.dart
  - 新建：MultiProvider 包裹的独立调试入口（不接入主路由）

— DI / 模块装配 —

feat: features/dms/di/dms_module.dart
  - registerDmsModule(sl) 注册 MqttClient / BindingApi / StateMachine / Repository / 3 个 UseCase / Manager / 2 个页面级 Provider（factory）

feat: di/service_locator.dart
  - init() 顶部加 registerDmsModule(sl)，独立 feature 装配

feat: features/dms/dms.dart
  - barrel：聚合对外导出（不暴露 internals）

— 依赖 —

feat: pubspec.yaml
  - 新增 mqtt_client: ^10.0.0（其余 qr_flutter / crypto / device_info_plus / package_info_plus / shared_preferences 复用既有）




  feat(DMS)：完善心跳设备信息 + Android 真机 MAC 回落： panruiqi 5/7/2026 8:22 PM

  feat(DMS)：DeviceSetupPage 替换式接入设备自动绑定 panruiqi 5/7/2026 8:22 PM


  feat(DMS)：重构拦截器部分，让其可以透传白名单 panruiqi 5/9/2026 10:09 AM

  feat(DMS)：启动流接入 DeviceSetupPage + 启动即连 redirect MQTT + 协议参数与 CloudPos 对齐 panruiqi 5/9/2026 11:05 AM


  feat(DMS)：强制扫码绑定 + ctrlDevice reboot/restore 实际接入 panruiqi 5/11/2026 3:30 PM


  feat(DMS)：绑定判断改为 DMS 心跳激活 + 退网改为弹窗跳转（不再 exit） panruiqi 5/11/2026 4:33 PM

  feat(DMS)：bind_info MQTT 推送 + HomePage 门店锁定 + binding-first 导航守卫 panruiqi 5/12/2026 11:07 AM

  fix(DMS): 双订阅状态分裂 + 启动/重连/退网三处并发 panruiqi 5/12/2026 2:07 PM

  refactor(DMS): 精简模块结构 + DmsManager/DmsRepositoryImpl 合并改名为 DmsService panruiqi 5/12/2026 2:27 PM

  feat(DMS)：DMS broker URL 跟随 NetworkConfig + 环境切换入口挂 DeviceSetupPage panruiqi 5/12/2026 4:56 PM






2. CamClaw
4.22
CamerClaw需求评审
3. fix(AI_视频分析助手)：解决双端内容解析差异的问题
4. fix(AI_视频分析助手)：解决编译问题
5. fix(AI_视频分析助手)：文件侧同步兼容Android List 格式和 iOS Map 格式。
6. fix(AI_视频分析助手): 修复 iOS 图片选择结果解析失败问题

问题：
iOS 侧选图后图片 URL 无法附加到输入框，Android 正常。

根因：
NativeBridgeService._parseSystemResourceResult 已将原生返回的
{datas: [items]} 扁平化为 List<item>，但 _handleImageSelectResult
仍按 params[0]['datas'] 取值，导致 iOS 路径取到 null。
Android 走 addEventListener 路径时手动 images.add(map) 包了一层，
恰好凑上 buggy 的取值逻辑，属巧合并非正确实现。

修复：
- _handleImageSelectResult 直接遍历 params 取 url，去掉多余的
  params[0]['datas'] 层级
- addEventListener 回调改为复用 parseSystemResourceResult 做归一化，
  去掉手动 images.add 包装
- 两条回传路径（onResult / addEventListener）统一走同一份解析逻辑

原生侧无需改动，{datas: [...]} 契约保持不变。

{datas: [items]} 扁平化成了 List<item>，每个 item 是 {url, isVideo, type, ...}

7. 和仇老板以及IOS（李长恩）同步问题解决

同步一下刚才AI视频分析助手的图片选择问题的处理：

先说一个判断问题：
根本原因不在于 handler 收的是 List 和 iOS 原生传的 Map 不匹配。
因为 iOS 原生传的 {datas: [...]} Map，在 Dart 侧 NativeBridgeService._parseSystemResourceResult 已经被统一归一化成了 List<item>（每个 item 形如 {url, isVideo, type, ...}），onResult 回调拿到的永远是 List<item>，双端一致，这一层是没问题的。

真正的根因：_handleImageSelectResult 里按 params[0]['datas'] 取值，多剥了一层——_parseSystemResourceResult 已经把 datas 外壳拆掉了，handler 还在按旧结构取，iOS 路径必然拿到 null。Android 没暴露问题是因为走的是 addEventListener 另一条路径，那边手动 images.add(map) 包了一层，恰好凑上了这个 bug，属于巧合。

修复方案：
Handler 保持 List<item> 签名不变，去掉 params[0]['datas']，直接遍历 params 每项取 url
addEventListener 回调复用 parseSystemResourceResult 做统一归一化，去掉多余的 images.add 包装

两条路径走同一份解析逻辑，原生侧无需改动，已提交git到远端并和 iOS 同学对齐。    



feat(CameraClaw)：AI 即拍即检 Banner 入口 - 阶段1 Native 实现，具体如下：

feat: 新增 AI 即拍即检 Banner UI 组件

  新建 item_ai_instant_check_banner.xml，78dp 高卡片布局：
  背景图（fitXY）+ 对勾图标 + AI 图标 + 标题 + 副标题 + 动态按钮
  新建 bg_ai_instant_check_btn.xml：#21FFFFFF 填充，16dp 圆角
  按钮 wrap_content 宽度 + 12dp 左右 padding，适配长短文案

feat: 在门店首页（StoreHomeActivity）接入 Banner

  Banner 作为 AppBarLayout 直接子级（CollapsingToolbarLayout 与 Tab 之间），
  layout_scrollFlags=scroll，随门店信息整体上滑消失，宽度自然 match_parent

feat: Banner 4 种状态控制逻辑

  枚举 AiInstantCheckBannerState：NO_CAMERA / NO_TASK /
  RUNNING_NO_REPORT / RUNNING_WITH_REPORT
  setAiInstantCheckBannerPermission()：由接口回调驱动整体显隐（预留接口）
  refreshAiInstantCheckBannerState()：根据 favorShop.deviceCount 判断状态①，
  状态②③④ Mock 占位，待 AI 服务接口就绪后替换
  状态①点击跳转 /deviceRegistration（摄像头管理），
  状态②④分别跳转 /aiInstantCheck?initialTab=task/report

fix: Banner 层级错位修复，移至 AppBarLayout 直接子级

  原位置在 CollapsingToolbarLayout 内，doOnLayout 拿到的
  cl_header.bottom 在动态数据加载前偏小，导致 Banner 覆盖地址行
  改为 AppBarLayout 直接子级（CollapsingToolbarLayout 与 Tab 之间），
  随门店信息整体滚动消失，宽度自然 match_parent，无需动态定位

refactor: 移除动态定位逻辑，简化 Banner 状态控制

  删除 positionBannerBelowHeader() 方法
  移除 FrameLayout / doOnLayout / updateLayoutParams 三个 import
  updateAiInstantCheckBannerState() 开头统一设置 visibility = VISIBLE，
  各状态分支只负责文案和点击逻辑

fix: 按钮宽度改为 wrap_content 适配长文案

  固定 68dp 导致"去绑定摄像头"文字截断
  改为 wrap_content + paddingStart/End 12dp，高度保持 28dp
  左侧文字区通过 constraintEnd_toStartOf 约束自动收窄，不会重叠

fix(CameraClaw): Banner 吸顶问题根因排查与修复

  排查过程：
  - 首次误诊：以为 <include> 不传递 app:layout_scrollFlags，
    实测 scrollFlags=1，方向错误
  - 通过 OnOffsetChangedListener log 确认 verticalOffset 能到
    -totalScrollRange(-908)，说明 AppBarLayout 整体滚动正常
  - 真实根因：banner 作为 AppBarLayout 兄弟节点时，
    LinearLayout 位置基于 CTB 展开高度（~965px），
    AppBarLayout 上移 908px 后 banner 屏幕 Y≈57px，
    永远不会完全离屏
  修复：将 banner 移入 CTB 内 LinearLayout，与 cl_header
  共同随 CTB 折叠，从根本上解决位置计算问题

feat(CameraClaw_8期)：AI 即拍即检 - Banner 状态接入真实接口，具体如下：

feat: StoreHomeApi 新增 getAiScanConfigs 接口
  调用 ovopark-agent/api/scan/configs/{storeId}
  复用 httpRequestLoader.getFormParseRequest 模式

fix: Banner 状态判断从 Mock 切换为真实接口
  原逻辑依赖 favorShop.deviceCount（始终为 0）导致常显"去绑定摄像头"
  改为：先用 devices 列表本地判断有无设备
  有设备则调 getAiScanConfigs：exists:false → 立即开启
  exists:true → 立即查看（有报告时间则展示，无则展示"运行中，等待首份报告"）
  onSuccess 的 result 为已解包的 data 内容，去掉 isError 层解析

refactor: Banner 状态精简为三态
  移除 RUNNING_NO_REPORT 枚举值
  无报告/有报告均走 RUNNING_WITH_REPORT，仅副标题文案不同
  日报/周报时间均为空 → "运行中，等待首份报告"

fix: ISO 时间戳格式化改为截取前16位
  原 SimpleDateFormat 无法解析小数秒（如 .12338）导致显示原始字符串
  改为 iso.substring(0, 16).replace('T', ' ') 直接格式化
  "2026-04-27T14:53:06.12338+08:00" → "2026-04-27 14:53"

feat(CameraClaw_8期)：AI 即拍即检 - 摄像头 thumbUrl 传入 Flutter 路由参数，具体如下：

feat: StoreHomeActivity.openAiInstantCheckPage 新增 thumbUrl 字段
  cameras JSON 格式由 {id, name} 扩展为 {id, name, thumbUrl}
  thumbUrl 取自 favorShop.devices[].thumbUrl（getShopStatus API 返回）

feat(CameraClaw_8期)：即拍即检入口添加权限控制

feat(CameraClaw_8期)：权限管理，无 DEVICE_NETWORK_REGIST 权限时弹 toast 拦截，有权限时正常跳转，和 StoreFunctionFragment 逻辑完全对齐

review(CameraClaw_8期)：Native 层代码审查修复，具体如下：

- feat(DataManager): 新增 GET_AI_SCAN_CONFIGS URL 常量，将 "ovopark-agent/api/scan/configs/" 提取至 DataManager.Urls，与项目其他接口 URL 统一管理规范对齐

- refactor(StoreHomeApi): getAiScanConfigs 改用 DataManager.Urls 常量
替换硬编码 URL 字符串，消除散落的裸字符串

- feat(strings): 新增 AI 即拍即检 Banner 字符串资源
在 lib_store_home/res/values/strings.xml 中新增 7 条 ai_banner_*
资源，含参数格式串 ai_banner_subtitle_report_generated（%s 占位）

- refactor(StoreHomeActivity): Banner 文案全部改用字符串资源
将 updateAiInstantCheckBannerState 中 7 处硬编码（含 5 处历史遗留）
替换为 getString(R.string.*)，格式串改用 getString(..., lastReportTime)

style(CameraClaw_8期)：调整入口显示效果，消除空隙

feat(CameraClaw_8期)：AI 即拍即检 - 阶段2 Flutter 详情页框架，具体如下：

feat: 新增 domain 层实体与仓库接口

  新建 InstantCheckHeader：含 status（running/stopped）、
  activeStandardCount、cameraCount，未运行时两项显示 -
  新建 Report：含 title、detectionTimeRange、cameraCount、
  standardCount、abnormalCount、publishStatus，移除原 summary/coverUrl
  新建 TaskConfig / Standard / CameraView 实体
  新建 InstantCheckRepository 抽象接口

feat: 新增 infrastructure 层（Mock 优先）

  新建 InstantCheckApi 路径常量
  新建 HeaderDto / ReportDto / TaskConfigDto / StandardDto，
  各含 fromJson() 与 toDomain() 映射
  新建 InstantCheckRepositoryMockImpl，含符合设计稿的完整 Mock 数据
  新建 InstantCheckRepositoryImpl（Dio 框架占位，联调阶段替换）

feat: 新增 Cubit 状态管理（4 个模块）

  HeaderCubit / ReportCubit / TaskCubit / StandardCubit
  各含 sealed State：Initial → Loading → Loaded / Error
  TaskCubit 额外支持 isSaving 状态与 TaskSaveError

feat: 新增主页面与报告 Tab UI（严格还原设计稿）

  AiInstantCheckPage：无 AppBar，自定义 Header 区域
  Header：「即拍即检」大标题 + 运行状态胶囊（运行中蓝/未运行灰）
  + 最新报告时间 + 活跃标准总数 / 已接入摄像头双列统计
  胶囊式 TabBar：灰底 F0F0F0 大胶囊包裹三个白色选项，radius 40
  ReportCard：背景图 Header（ico_ai_background）+ 三列数据
  （检测时间段/摄像头·标准/异常红字）+ 已发布标签 + 查看报告箭头
  ReportTab：日报胶囊 + showMenu 下拉选择（日报/周报，选中蓝色 + 勾）

feat: 注册 Flutter 路由 /aiInstantCheck

  old_module.dart 新增路由，接收 storeId / storeName / initialTab
  与 StoreHomeActivity.openAiInstantCheckPage() 参数完全对应


feat(CameraClaw_8期)：AI 即拍即检 - 阶段3/4 报告Tab & 任务Tab UI，具体如下：

feat: 新增 报告 Tab（阶段3）

  新建 report_tab.dart：日报/周报胶囊选择器，showMenu 弹出
  下拉列表，选中项蓝色高亮 + ico_duigou_yellow 勾号图标
  新建 report_card.dart：卡片三段结构
    Header 66dp：ico_ai_background.webp 渐变底 + ico_ai_report.webp
    + 标题(semibold 14sp) + 时间(11sp)
    Content：检测时间段 / 摄像头&标准 / 异常 三列，
    0.5dp rgba(229,229,229,1) 竖向分割线，异常数>0 显红色
    Footer：已发布绿色 badge + 查看报告 + ico_ai_arrow_right.webp

feat: 新增 任务 Tab（阶段4）

  新建 task_tab.dart：
    _TaskCard：执行频率行(44dp) + 0.5dp 分割线 + 开关行(44dp)
    _CustomHoursRow：选自定义时展开，距卡片左169dp，
    50×32 灰底(F0F0F0)数字输入框 + 62×32 灰底"小时"标签
    _EnableRow：Switch activeTrackColor rgba(255,153,0,1)
    _RemarksSection：左16dp 与卡片对齐，ico_ai_about + 13sp 灰色备注
    _FrequencyBottomSheet：220dp 高，上圆角16dp，
    rgba(247,247,247,0.95) 底色，Stack Positioned 精确布局
    标题行用 Row 保证 clock/文字/X 三者垂直居中对齐
    X 按钮直接 20×20 Image，无容器包裹
    内容白色卡片 top53/bottom32，item 垂直 padding 10 修复 5px overflow
    选中项橙色 semibold + ico_duigou_yellow，未选中灰色 normal

feat: 更新 domain/infrastructure 实体与 DTO

  TaskConfig 频率枚举改为 hourly/twoHourly/custom
  （原 daily/weekly/custom），label 同步更新
  TaskConfigDto 序列化字符串对应更新
  Mock 返回 CheckFrequency.hourly，customFrequencyHours 默认24

feat: 更新 顶部信息区样式（ai_instant_check_page）

  运行中状态：rgba(32,139,238,0.06) 底色 + 蓝色文字
  停止状态：rgba(0,0,0,0.03) 底色 + rgba(178,178,178,1) 文字
  未运行时 activeStandardCount / cameraCount 显示 -
  PillTabBar：灰色 rgba(240,240,240,1) 胶囊，选中白色，圆角40

feat(CameraClaw_8期)：AI 即拍即检 - 阶段5 标准Tab UI，具体如下：

feat: 新增 标准Tab 双视图（按摄像头 / 按门店汇总）

  _SubTabBar：65×44dp 两个子标签，选中态 semibold 13sp + 橙色
  下划线 26×2dp（rgba(255,153,0,1)），未选中 normal 灰色

  按摄像头视图（_CameraGroupItem）：
    收起：343×71dp，白卡 radius 12，ico_ai_device_a1 + 摄像头名
    + 视角位置/标准数小字 11sp 灰色
    展开：343×432dp，同收起内容 + 视频区（left:42 right:16
    height:176dp，WDZPlayerWidget 懒初始化，点击 ico_ai_video_play
    后播放）+ 标准条目列表（top:236起）
    默认全部收起

  按门店汇总视图（_StoreCategoryGroupItem）：
    同结构无视频，副标题改为"涉及N个摄像头 | M条标准"
    默认全部收起

  _StandardItem（两个视图共用）：
    ico_ai_standard_item(18×18) + name(14sp) + tag 胶囊
    (4dp圆角, 0.5dp rgba(151,151,151,0.3)边框, 11sp)
    + 描述(11sp 灰) + 可选来源/最近执行(同行)
    按摄像头视图 tag=categoryName；按门店视图 tag=cameraName

feat: 扩展 Standard 实体与 DTO

  新增字段：categoryName, cameraPosition, source?,
  lastExecutedTime?, videoUrl?
  StandardDto.fromJson 同步新增字段解析

feat: 更新 StandardCubit / StandardState

  新增 StandardViewMode 枚举（byCamera / byStore）
  StandardLoaded 携带 viewMode 字段 + copyWithView() 方法
  StandardCubit 新增 switchView(mode) 方法

feat: 更新 Mock 数据

  2个摄像头（收银台主视角/进店门口视角）× 各2条标准
  覆盖 categoryName、cameraPosition、source、
  lastExecutedTime 字段
  前端按 cameraId / categoryName 自行聚合分组

涉及文件：
- lib/ai_instant_check/domain/entities/standard.dart
- lib/ai_instant_check/infrastructure/api/dto/standard_dto.dart
- lib/ai_instant_check/presentation/bloc/standard_state.dart
- lib/ai_instant_check/presentation/bloc/standard_cubit.dart
- lib/ai_instant_check/infrastructure/repositories/instant_check_repository_mock_impl.dart
- lib/ai_instant_check/presentation/tabs/standard_tab.dart



feat(CameraClaw_8期)：AI 即拍即检 - 阶段6 全局UI优化，具体如下：

fix: 调整顶部 Header 布局

  返回按钮：IconButton(系统图标) → ico_ai_back.webp
  (24×24dp)，top:31dp within SafeArea ≈ 55dp 绝对位置
  返回按钮与"即拍即检"标题间距：默认贴紧 → 26dp gap
  ≈ 标题在 105dp 绝对位置

fix: 主 TabBar 切换时背景变暗问题

  移除 Material TabBar 默认 ink 效果：
  splashFactory: NoSplash.splashFactory
  overlayColor: WidgetStateProperty.all(Colors.transparent)

fix: 标准Tab 子 Tab 文案"按门店汇总"换行

  _SubTab 固定宽度 65 → 80，加 maxLines: 1 防止 5 字符
  汉字超出 65dp 后被截断换行

fix: 报告Tab 日报/周报 切换交互

  移除 showMenu 弹出菜单逻辑及 _buildMenuItem
  胶囊点击改为直接切换到另一类型（日报↔周报）


feat: report_dto.dart 字段全量重映射

  report_id/report_type/published_at/window_start/window_end/total_*/view_url
  publishStatus 本地化（published→已发布）
  detectionTimeRange 由 window_start/window_end 派生

feat: task_config_dto.dart 频率互转与 config_id 缓存

  frequency_seconds ↔ CheckFrequency（3600/7200/other）
  内部缓存 config_id，供 updateTaskConfig PUT 使用
  toUpdateBody() 静态方法生成更新请求体

feat: standard_dto.dart 字段重命名与来源本地化

  standard_id/category/camera_id/updated_at 字段对齐后端
  source: auto_generated→AI生成，manual→手动添加
  cameraName 由外部注入的 cameraNames Map 解析

feat: instant_check_repository_impl.dart 全量重写

  使用 NetworkManager.instance 替换 Mock
  构造时注入 storeId/cameraIds/cameraNames
  updateTaskConfig：_configId==null → POST 创建，否则 PUT 频率 + PUT toggle
  getStandards：展平 groups Map 为平铺列表
  store_id POST 字段强制转 int（int.tryParse(_storeId)）

feat: report_card.dart 接入 WebViewPreviewPage

  "查看报告" 按钮跳转 WebViewPreviewPage(fileUrl: viewUrl, reportMode: true)
  viewUrl 为空时禁用点击

feat: ai_instant_check_page.dart 解析路由参数

  fromParams() 解析 cameras JSON → cameraIds + cameraNames
  构造 InstantCheckRepositoryImpl 时传入 storeId/cameraIds/cameraNames

feat(CameraClaw_8期)：AI 即拍即检 Flutter 端完整实现，具体如下：

feat: Domain / DTO / Repository 层搭建
  InstantCheckRepository 接口定义（getHeader/getReports/getTaskConfig/updateTaskConfig/getStandards）
  HeaderDto 解析 exists + enabled + last_daily_report_at，以 enabled 判断运行态
  ReportDto 解析 view_url → viewUrl，_resolveUrl 拼接 baseUrl 处理相对路径
  StandardDto 解析 updatedAt → lastExecutedTime，_formatIso 格式化时间
  InstantCheckRepositoryImpl 构造参数 storeId / cameraIds / cameraNames
    updateTaskConfig: _configId==null 时 POST 创建，否则 PUT 频率 + PUT toggle
    toggle 直接解析返回结果更新状态，不再发额外 GET /configs

fix: toggle 后消除重复 GET /configs 请求
  updateTaskConfig 改为返回 TaskConfig，直接解析 toggle 接口返回结果
  task_cubit 用返回值更新状态，删除冗余的 getTaskConfig 验证调用
  task_tab 改调 HeaderCubit.updateEnabled() 而非重新拉接口
  header_cubit 新增 updateEnabled(bool) 直接更新状态，无网络请求
  instant_check_header 新增 copyWith(status) 方法

feat: Presentation 层 - Header / Task / Report / Standard Tab
  HeaderCubit / TaskCubit 状态管理，BlocConsumer 监听保存完成刷新 Banner
  TaskTab: 执行频率选择底部弹框、自定义小时数输入、开关 toggle
  ReportCard: "查看报告" 跳转 WebViewPreviewPage(reportMode:true, keepTopSafeArea:true)
  StandardTab: 摄像头副标题 Padding(left:26) 对齐；来源/最近执行改 \n 换行

feat: WebViewPreviewPage 新增 keepTopSafeArea 参数
  默认 false 保持原有行为（向后兼容）
  true 时不移除 top SafeArea，避免 AI 报告页贴系统状态栏

feat(CameraClaw_8期)：AI 即拍即检 - 标准 Tab 视频区改为图片区并新增编辑入口，具体如下：

feat: standard.dart 新增 thumbUrl? 字段
  用于在摄像头分组 item 中展示摄像头缩略图

feat: standard_dto.dart toDomain 新增 cameraThumbUrls 参数
  接收 Map<String, String> 并映射 cameraId → thumbUrl

feat: instant_check_repository_impl.dart 新增 _cameraThumbUrls
  构造函数接收 cameraThumbUrls 并传给 StandardDto.toDomain()

feat: ai_instant_check_page.dart fromParams 解析 thumbUrl
  从 cameras JSON 提取 thumbUrl 构建 cameraThumbUrls Map
  透传给 InstantCheckRepositoryImpl

feat: standard_tab.dart 视频区改为摄像头截图区
  - 尺寸改为 285×160dp（left:42 right:16 padding）
  - thumbUrl 有值：FadeInImage 加载 OSS 缩略图（+resize,w_500 参数）
  - thumbUrl 为空：显示占位图 with_out_pic_4.png
  - 仅 thumbUrl 不为空时在图片上叠加 ico_ai_video_play.webp（48×48 居中）
  - 点击播放按钮预留空回调（待后续接入播放页）
  移除 WDZPlayerManager / WDZPlayerWidget 依赖

feat: standard_tab.dart 展开 item 底部新增分割线与编辑入口
  - 0.5dp 分割线（rgba(229,229,229,1)，左右各 16dp 边距）
  - ico_ai_edit.webp + "编辑" 文字居中排列，底部 17dp 间距
  - 点击预留空回调（待后续接入编辑页）

feat(CameraClaw_8期)：AI 即拍即检 - 标准 Tab 新增播放页入口并实现摄像头实时播放页，具体如下：

feat: presentation/widgets/standard_item_card.dart 新增（提取公共 widget）
  将 standard_tab.dart 中的 _StandardItem → StandardItemCard
  将 _TagCapsule → StandardTagCapsule，供标准 Tab 和播放页共用

feat: presentation/pages/camera_play_page.dart 新增播放页
  接收 cameraId / cameraName / thumbUrl? / standards 四个参数
  顶部 AppBar 展示摄像头名称
  视频区 343×193dp：WDZPlayerWidget 实时播放，封面图占位（thumbUrl
  或 with_out_pic_4.png），播放状态三态覆盖层（未播→播放按钮 /
  连接中→loading / 播放中→透出画面）
  下方白色圆角卡片（12dp）：摄像头信息头（图标+名称+N条标准）+
  标准列表全展开 + 编辑 footer（预留 onTap）

fix: presentation/pages/camera_play_page.dart 修复播放按钮不显示问题
  初始 playState=idle 导致 loading 一直显示、播放按钮从未出现；
  新增 _playRequested 标志区分「初始未播(idle)」与「连接中(idle)」

feat: presentation/tabs/standard_tab.dart 接入播放页跳转
  图片区 onTap 填入 Navigator.push → CameraPlayPage
  两处 _StandardItem 替换为 StandardItemCard
  删除已迁移的 _StandardItem / _TagCapsule 类定义


feat(CameraClaw_8期)：AI 即拍即检 - 新增标准编辑页，支持批量编辑/排序/删除，具体如下： panruiqi 4/29/2026 1:23 PM

fix(CameraClaw_8期)：AI 即拍即检 - 标准编辑页保存逻辑优化，具体如下： panruiqi 4/29/2026 1:47 PM
feat(CameraClaw_8期)：AI 即拍即检 - 标准编辑页开放新增功能并引入 configId 透传，具体如下： panruiqi 4/29/2026 3:08 PM
feat(CameraClaw_8期)：bug修复，具体如下： fix(CameraClaw_8期)：AI 即拍即检 - 修复自定义频率输入键盘收起及标准总数未刷新，执行频率范围限制，编辑新增删除标准后接口刷新，具体如下： panruiqi 4/30/2026 3:42 PM
feat(CameraClaw_8期)：AI 即拍即检 - 视频播放页视频吸顶 & 标准编辑页新增条目自动跳底，具体如下： panruiqi 5/7/2026 10:01 AM
feat(CameraClaw_8期)：AI 即拍即检 - issue12，在首次post后尝试进行toggle，获取正确状态 panruiqi 5/7/2026 10:29 AM
review(CameraClaw_8期)：Flutter 层代码审查修复，具体如下： panruiqi 5/8/2026 10:56 AM
feat(CameraClaw_8期)：UI修改 + 跳转自定义执行频率的接口调用 panruiqi 5/9/2026 9:40 AM
feat(CameraClaw_8期)：拆分配置频率和开启toggle的接口 panruiqi 5/9/2026 9:41 AM
fix(CameraClaw_8期)：AI 即拍即检 - 任务 Tab 接口拆分与 iOS 键盘修复，具体如下： - refactor(_CustomHoursRow): 自定义频率输入改为失焦提交，删除 dart:async / Timer / 防抖逻辑，输入框视为"草稿区"，避免用户删空准备重输时被 500ms 防抖回退覆盖 panruiqi 5/11/2026 11:06 AM
fix(CameraClaw_8期)：首次创建：POST 创建，直接使用返回的 enabled（标准异步生成中，不再额外 toggle） panruiqi 5/11/2026 4:35 PM
refactor(CameraClaw_8期)：AI 即拍即检 - 任务开关由二态 Switch 升级为 4 态状态机按钮 panruiqi 5/12/2026 4:22 PM
fix(CameraClaw_8期)：修复即拍即检执行频率不一致 panruiqi Yesterday 3:12 PM



3. ANR：
fix(ANR): IjkPlayView.openVideo() 同步调用 reset() 导致主线程阻塞，问题ID：B128B3C0CA45AAB053975F020BC81545

IjkMediaPlayer.reset() 内部通过 pthread_join 等待解码线程退出，
属于阻塞操作。openVideo() 在网络回调（主线程）中被调用，
导致主线程长时间等待，触发 ANR。

新增 releasePlayerAsync() 方法，将旧播放器的 reset()/release()
移至后台线程 "ijk-release-thread" 执行，主线程仅同步完成：
- 清空所有 listener（防止后台 reset 期间触发 UI 回调）
- setDisplay(null)（立即断开 Surface，供新播放器使用）
- 状态重置与音频焦点释放

sReleasingPlayers 持有强引用防止 GC 提前回收，
30s 超时兜底防止解码线程死锁导致内存泄漏。

2. fix(ANR): 解决ANR修复后的网络问题





4. 协助测试

feat(About)：添加flutter和主线提交信息，协助测试判断是否是最新的包



5. 主线代码优化与稳定性提升

fix(Player)：修复 RTSP 设备播放超时报错 - 主流含音频时跳过从流请求，具体如下：

fix: PlayerPlatformView 从 Flutter play 数据中读取 aenabled 字段
  startNewMediaPlay(isSlave:0) 返回 aenabled=true 表示主流已含音频
  提取该字段作为 skipQueryToken 传入 play()，透传至 startPlay()

fix: FlutterVideoPlayView.startPlay 两个重载新增 skipQueryToken 参数
  直播分支（videoFlag==OTHER）当 skipQueryToken=true 时
  直接调用 startPlay2 播放主流 URL，跳过 queryKeyAccessToken
  避免对不支持从流的 RTSP 设备（accessType=3）发起 startNewMediaPlay(isSlave:1)
  消除货架类摄像头 16 秒 comm_timeout 超时导致的播放失败问题



6. 主线：
【安卓】【商户端】店主自值守—店主值守期间进店事件推送消息中心