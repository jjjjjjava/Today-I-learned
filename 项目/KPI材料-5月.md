# 5月 KPI 考核材料

## 一、业务贡献度-产出（权重：45%，自评：4.5分）

本周期按时完成所有需求交付，涵盖招财猫 DMS 设备管理、CameraClaw 8期 AI 即拍即检、ANR 稳定性治理、主线代码优化等多个方向，无 P0/P1 级线上故障。

### 1. 招财猫 - DMS 设备管理平台接入（Flutter 端主导，已上线）

**1.1 DMS 核心能力从 0 到 1 完整实现**

- **平台层 / 原生 channel**：迁移 Pos 和 CloudPos 的 DMS 相关代码到本项目，建立 Flutter 与原生的通信桥梁
- **数据层**：新建 device_binding_api.dart 接入 POST /ovopark-device-manage/feign/yzs/getYzsDeviceStatusByMac 接口；新建 5 个数据模型（sync_main_device_info、device_net_info、verify_pwd_request、ctrl_device_request、device_status_response）对应 CloudPos DMSModels.kt
- **Repository 层**：整合 MQTT 客户端 + 状态机 + device_info_plus，实现两阶段连接（连 redirect → 等 join_network(45s) → 切真 DMS）；实现 30s 周期心跳上报（启动后立即先发一次）；实现指数退避重连机制（5/10/20/40/80/128s 封顶）；自动应答 verify_pwd / ctrlDevice 指令
- **领域层**：定义 7 状态 sealed class（Idle / ConnectingToRedirect / WaitingForNetworkInfo / ConnectingToDms / HeartbeatActive / Reconnecting / Error）1:1 复刻 CloudPos DMSConnectionState；定义 9 事件 sealed class 驱动状态转换；抽象 DmsRepository 接口暴露 connectionStateStream / startConnection / stopConnection / sendHeartbeat 等核心能力
- **状态机基础设施**：DmsStateMachine 转换矩阵 1:1 复刻 CloudPos DMSStateMachine.kt，中文日志输出（「空闲 → 连接重定向服务器」「等待服务器信息 → 连接DMS服务器」）
- **服务层**：DmsManager 单例对外服务（≈ moneykitty 的 WebSocketManager 角色），start 幂等；WidgetsBindingObserver 监听应用生命周期，回前台若 Error/Reconnecting 则尝试拉起
- **表现层**：DmsProvider（ChangeNotifier 包装 stateStream）+ DeviceBindingProvider（4 态：Initializing / ShowingQr / Done / Failed）；DeviceBindingPage 实现二维码展示、180s 倒计时、HTTP 轮询绑定（每 2s 调 getYzsDeviceStatusByMac）；绑定成功写 dms_dep_id / dms_device_name 到 SharedPreferences，autoStartDmsOnSuccess 默认 true 自动拉起 DMS 连接
- **DI / 模块装配**：registerDmsModule(sl) 注册 MqttClient / BindingApi / StateMachine / Repository / 3 个 UseCase / Manager / 2 个页面级 Provider（factory）；dms.dart barrel 聚合对外导出

**1.2 DMS 完善与业务接入**

- 完善心跳设备信息 + Android 真机 MAC 回落
- DeviceSetupPage 替换式接入设备自动绑定
- 重构拦截器部分，让其可以透传白名单
- 启动流接入 DeviceSetupPage + 启动即连 redirect MQTT + 协议参数与 CloudPos 对齐
- 强制扫码绑定 + ctrlDevice reboot/restore 实际接入
- 绑定判断改为 DMS 心跳激活 + 退网改为弹窗跳转（不再 exit）
- bind_info MQTT 推送 + HomePage 门店锁定 + binding-first 导航守卫
- 修复双订阅状态分裂 + 启动/重连/退网三处并发问题
- 精简模块结构：DmsManager/DmsRepositoryImpl 合并改名为 DmsService
- DMS broker URL 跟随 NetworkConfig + 环境切换入口挂 DeviceSetupPage


### 2. CameraClaw 8期 - AI 即拍即检功能完整实现（双端协作，已上线）

**2.1 Native 层（Android）- Banner 入口与权限控制**

- **Banner UI 组件**：新增 item_ai_instant_check_banner.xml（78dp 高卡片布局：背景图 + 对勾图标 + AI 图标 + 标题 + 副标题 + 动态按钮）；bg_ai_instant_check_btn.xml（#21FFFFFF 填充，16dp 圆角，wrap_content 宽度适配长短文案）
- **门店首页接入**：Banner 作为 AppBarLayout 直接子级（CollapsingToolbarLayout 与 Tab 之间），layout_scrollFlags=scroll 随门店信息整体上滑消失
- **4 种状态控制逻辑**：枚举 AiInstantCheckBannerState（NO_CAMERA / NO_TASK / RUNNING_NO_REPORT / RUNNING_WITH_REPORT）；setAiInstantCheckBannerPermission() 由接口回调驱动整体显隐；refreshAiInstantCheckBannerState() 根据 favorShop.deviceCount 判断状态①，状态②③④ Mock 占位待接口就绪后替换；状态①点击跳转 /deviceRegistration（摄像头管理），状态②④分别跳转 /aiInstantCheck?initialTab=task/report
- **Banner 层级错位修复**：原位置在 CollapsingToolbarLayout 内导致 doOnLayout 拿到的 cl_header.bottom 偏小，Banner 覆盖地址行；改为 AppBarLayout 直接子级，随门店信息整体滚动消失，无需动态定位
- **按钮宽度适配**：固定 68dp 导致"去绑定摄像头"文字截断，改为 wrap_content + paddingStart/End 12dp，高度保持 28dp
- **Banner 吸顶问题根因排查与修复**：首次误诊以为 <include> 不传递 app:layout_scrollFlags，实测 scrollFlags=1；通过 OnOffsetChangedListener log 确认 verticalOffset 能到 -totalScrollRange(-908)，说明 AppBarLayout 整体滚动正常；真实根因：banner 作为 AppBarLayout 兄弟节点时，LinearLayout 位置基于 CTB 展开高度（~965px），AppBarLayout 上移 908px 后 banner 屏幕 Y≈57px，永远不会完全离屏；修复：将 banner 移入 CTB 内 LinearLayout，与 cl_header 共同随 CTB 折叠

**2.2 Native 层 - Banner 状态接入真实接口**

- StoreHomeApi 新增 getAiScanConfigs 接口（调用 ovopark-agent/api/scan/configs/{storeId}，复用 httpRequestLoader.getFormParseRequest 模式）
- Banner 状态判断从 Mock 切换为真实接口：原逻辑依赖 favorShop.deviceCount（始终为 0）导致常显"去绑定摄像头"；改为先用 devices 列表本地判断有无设备，有设备则调 getAiScanConfigs：exists:false → 立即开启，exists:true → 立即查看（有报告时间则展示，无则展示"运行中，等待首份报告"）；onSuccess 的 result 为已解包的 data 内容，去掉 isError 层解析
- Banner 状态精简为三态：移除 RUNNING_NO_REPORT 枚举值，无报告/有报告均走 RUNNING_WITH_REPORT，仅副标题文案不同；日报/周报时间均为空 → "运行中，等待首份报告"
- ISO 时间戳格式化改为截取前16位：原 SimpleDateFormat 无法解析小数秒（如 .12338）导致显示原始字符串，改为 iso.substring(0, 16).replace('T', ' ') 直接格式化（"2026-04-27T14:53:06.12338+08:00" → "2026-04-27 14:53"）
- 摄像头 thumbUrl 传入 Flutter 路由参数：StoreHomeActivity.openAiInstantCheckPage 新增 thumbUrl 字段，cameras JSON 格式由 {id, name} 扩展为 {id, name, thumbUrl}，thumbUrl 取自 favorShop.devices[].thumbUrl（getShopStatus API 返回）
- 即拍即检入口添加权限控制：权限管理，无 DEVICE_NETWORK_REGIST 权限时弹 toast 拦截，有权限时正常跳转，和 StoreFunctionFragment 逻辑完全对齐

**2.3 Native 层代码审查修复**

- feat(DataManager): 新增 GET_AI_SCAN_CONFIGS URL 常量，将 "ovopark-agent/api/scan/configs/" 提取至 DataManager.Urls，与项目其他接口 URL 统一管理规范对齐
- refactor(StoreHomeApi): getAiScanConfigs 改用 DataManager.Urls 常量替换硬编码 URL 字符串，消除散落的裸字符串
- feat(strings): 新增 AI 即拍即检 Banner 字符串资源，在 lib_store_home/res/values/strings.xml 中新增 7 条 ai_banner_* 资源，含参数格式串 ai_banner_subtitle_report_generated（%s 占位）
- refactor(StoreHomeActivity): Banner 文案全部改用字符串资源，将 updateAiInstantCheckBannerState 中 7 处硬编码（含 5 处历史遗留）替换为 getString(R.string.*)，格式串改用 getString(..., lastReportTime)
- style: 调整入口显示效果，消除空隙

**2.4 Flutter 层 - 详情页框架（阶段2）**

- **Domain 层实体与仓库接口**：新建 InstantCheckHeader（含 status（running/stopped）、activeStandardCount、cameraCount，未运行时两项显示 -）；新建 Report（含 title、detectionTimeRange、cameraCount、standardCount、abnormalCount、publishStatus，移除原 summary/coverUrl）；新建 TaskConfig / Standard / CameraView 实体；新建 InstantCheckRepository 抽象接口
- **Infrastructure 层（Mock 优先）**：新建 InstantCheckApi 路径常量；新建 HeaderDto / ReportDto / TaskConfigDto / StandardDto，各含 fromJson() 与 toDomain() 映射；新建 InstantCheckRepositoryMockImpl，含符合设计稿的完整 Mock 数据；新建 InstantCheckRepositoryImpl（Dio 框架占位，联调阶段替换）
- **Cubit 状态管理（4 个模块）**：HeaderCubit / ReportCubit / TaskCubit / StandardCubit，各含 sealed State：Initial → Loading → Loaded / Error；TaskCubit 额外支持 isSaving 状态与 TaskSaveError
- **主页面与报告 Tab UI（严格还原设计稿）**：AiInstantCheckPage 无 AppBar，自定义 Header 区域；Header 含「即拍即检」大标题 + 运行状态胶囊（运行中蓝/未运行灰）+ 最新报告时间 + 活跃标准总数 / 已接入摄像头双列统计；胶囊式 TabBar：灰底 F0F0F0 大胶囊包裹三个白色选项，radius 40；ReportCard：背景图 Header（ico_ai_background）+ 三列数据（检测时间段/摄像头·标准/异常红字）+ 已发布标签 + 查看报告箭头；ReportTab：日报胶囊 + showMenu 下拉选择（日报/周报，选中蓝色 + 勾）
- **注册 Flutter 路由**：old_module.dart 新增路由 /aiInstantCheck，接收 storeId / storeName / initialTab 与 StoreHomeActivity.openAiInstantCheckPage() 参数完全对应

**2.5 Flutter 层 - 报告Tab & 任务Tab UI（阶段3/4）**

- **报告 Tab**：report_tab.dart 日报/周报胶囊选择器，showMenu 弹出下拉列表，选中项蓝色高亮 + ico_duigou_yellow 勾号图标；report_card.dart 卡片三段结构（Header 66dp：ico_ai_background.webp 渐变底 + ico_ai_report.webp + 标题(semibold 14sp) + 时间(11sp)；Content：检测时间段 / 摄像头&标准 / 异常 三列，0.5dp rgba(229,229,229,1) 竖向分割线，异常数>0 显红色；Footer：已发布绿色 badge + 查看报告 + ico_ai_arrow_right.webp）
- **任务 Tab**：task_tab.dart _TaskCard 执行频率行(44dp) + 0.5dp 分割线 + 开关行(44dp)；_CustomHoursRow 选自定义时展开，距卡片左169dp，50×32 灰底(F0F0F0)数字输入框 + 62×32 灰底"小时"标签；_EnableRow Switch activeTrackColor rgba(255,153,0,1)；_RemarksSection 左16dp 与卡片对齐，ico_ai_about + 13sp 灰色备注；_FrequencyBottomSheet 220dp 高，上圆角16dp，rgba(247,247,247,0.95) 底色，Stack Positioned 精确布局，标题行用 Row 保证 clock/文字/X 三者垂直居中对齐，X 按钮直接 20×20 Image 无容器包裹，内容白色卡片 top53/bottom32，item 垂直 padding 10 修复 5px overflow，选中项橙色 semibold + ico_duigou_yellow，未选中灰色 normal
- **更新 domain/infrastructure 实体与 DTO**：TaskConfig 频率枚举改为 hourly/twoHourly/custom（原 daily/weekly/custom），label 同步更新；TaskConfigDto 序列化字符串对应更新；Mock 返回 CheckFrequency.hourly，customFrequencyHours 默认24
- **更新顶部信息区样式**：运行中状态 rgba(32,139,238,0.06) 底色 + 蓝色文字；停止状态 rgba(0,0,0,0.03) 底色 + rgba(178,178,178,1) 文字；未运行时 activeStandardCount / cameraCount 显示 -；PillTabBar 灰色 rgba(240,240,240,1) 胶囊，选中白色，圆角40

**2.6 Flutter 层 - 标准Tab UI（阶段5）**

- **标准Tab 双视图（按摄像头 / 按门店汇总）**：_SubTabBar 65×44dp 两个子标签，选中态 semibold 13sp + 橙色下划线 26×2dp（rgba(255,153,0,1)），未选中 normal 灰色
- **按摄像头视图（_CameraGroupItem）**：收起 343×71dp，白卡 radius 12，ico_ai_device_a1 + 摄像头名 + 视角位置/标准数小字 11sp 灰色；展开 343×432dp，同收起内容 + 视频区（left:42 right:16 height:176dp，WDZPlayerWidget 懒初始化，点击 ico_ai_video_play 后播放）+ 标准条目列表（top:236起）；默认全部收起
- **按门店汇总视图（_StoreCategoryGroupItem）**：同结构无视频，副标题改为"涉及N个摄像头 | M条标准"；默认全部收起
- **_StandardItem（两个视图共用）**：ico_ai_standard_item(18×18) + name(14sp) + tag 胶囊(4dp圆角, 0.5dp rgba(151,151,151,0.3)边框, 11sp) + 描述(11sp 灰) + 可选来源/最近执行(同行)；按摄像头视图 tag=categoryName；按门店视图 tag=cameraName
- **扩展 Standard 实体与 DTO**：新增字段 categoryName, cameraPosition, source?, lastExecutedTime?, videoUrl?；StandardDto.fromJson 同步新增字段解析
- **更新 StandardCubit / StandardState**：新增 StandardViewMode 枚举（byCamera / byStore）；StandardLoaded 携带 viewMode 字段 + copyWithView() 方法；StandardCubit 新增 switchView(mode) 方法
- **更新 Mock 数据**：2个摄像头（收银台主视角/进店门口视角）× 各2条标准，覆盖 categoryName、cameraPosition、source、lastExecutedTime 字段；前端按 cameraId / categoryName 自行聚合分组

**2.7 Flutter 层 - 全局UI优化（阶段6）**

- **调整顶部 Header 布局**：返回按钮 IconButton(系统图标) → ico_ai_back.webp (24×24dp)，top:31dp within SafeArea ≈ 55dp 绝对位置；返回按钮与"即拍即检"标题间距：默认贴紧 → 26dp gap ≈ 标题在 105dp 绝对位置
- **主 TabBar 切换时背景变暗问题**：移除 Material TabBar 默认 ink 效果（splashFactory: NoSplash.splashFactory，overlayColor: WidgetStateProperty.all(Colors.transparent)）
- **标准Tab 子 Tab 文案"按门店汇总"换行**：_SubTab 固定宽度 65 → 80，加 maxLines: 1 防止 5 字符汉字超出 65dp 后被截断换行
- **报告Tab 日报/周报 切换交互**：移除 showMenu 弹出菜单逻辑及 _buildMenuItem，胶囊点击改为直接切换到另一类型（日报↔周报）

**2.8 Flutter 层 - 接口对接与完整实现（阶段7）**

- **report_dto.dart 字段全量重映射**：report_id/report_type/published_at/window_start/window_end/total_*/view_url；publishStatus 本地化（published→已发布）；detectionTimeRange 由 window_start/window_end 派生
- **task_config_dto.dart 频率互转与 config_id 缓存**：frequency_seconds ↔ CheckFrequency（3600/7200/other）；内部缓存 config_id，供 updateTaskConfig PUT 使用；toUpdateBody() 静态方法生成更新请求体
- **standard_dto.dart 字段重命名与来源本地化**：standard_id/category/camera_id/updated_at 字段对齐后端；source: auto_generated→AI生成，manual→手动添加；cameraName 由外部注入的 cameraNames Map 解析
- **instant_check_repository_impl.dart 全量重写**：使用 NetworkManager.instance 替换 Mock；构造时注入 storeId/cameraIds/cameraNames；updateTaskConfig：_configId==null → POST 创建，否则 PUT 频率 + PUT toggle；getStandards：展平 groups Map 为平铺列表；store_id POST 字段强制转 int（int.tryParse(_storeId)）
- **report_card.dart 接入 WebViewPreviewPage**："查看报告" 按钮跳转 WebViewPreviewPage(fileUrl: viewUrl, reportMode: true)；viewUrl 为空时禁用点击
- **ai_instant_check_page.dart 解析路由参数**：fromParams() 解析 cameras JSON → cameraIds + cameraNames；构造 InstantCheckRepositoryImpl 时传入 storeId/cameraIds/cameraNames
- **toggle 后消除重复 GET /configs 请求**：updateTaskConfig 改为返回 TaskConfig，直接解析 toggle 接口返回结果；task_cubit 用返回值更新状态，删除冗余的 getTaskConfig 验证调用；task_tab 改调 HeaderCubit.updateEnabled() 而非重新拉接口；header_cubit 新增 updateEnabled(bool) 直接更新状态，无网络请求；instant_check_header 新增 copyWith(status) 方法
- **WebViewPreviewPage 新增 keepTopSafeArea 参数**：默认 false 保持原有行为（向后兼容）；true 时不移除 top SafeArea，避免 AI 报告页贴系统状态栏

**2.9 Flutter 层 - 标准 Tab 视频区改为图片区并新增编辑入口**

- **standard.dart 新增 thumbUrl? 字段**：用于在摄像头分组 item 中展示摄像头缩略图
- **standard_dto.dart toDomain 新增 cameraThumbUrls 参数**：接收 Map<String, String> 并映射 cameraId → thumbUrl
- **instant_check_repository_impl.dart 新增 _cameraThumbUrls**：构造函数接收 cameraThumbUrls 并传给 StandardDto.toDomain()
- **ai_instant_check_page.dart fromParams 解析 thumbUrl**：从 cameras JSON 提取 thumbUrl 构建 cameraThumbUrls Map，透传给 InstantCheckRepositoryImpl
- **standard_tab.dart 视频区改为摄像头截图区**：尺寸改为 285×160dp（left:42 right:16 padding）；thumbUrl 有值：FadeInImage 加载 OSS 缩略图（+resize,w_500 参数）；thumbUrl 为空：显示占位图 with_out_pic_4.png；仅 thumbUrl 不为空时在图片上叠加 ico_ai_video_play.webp（48×48 居中）；点击播放按钮预留空回调（待后续接入播放页）；移除 WDZPlayerManager / WDZPlayerWidget 依赖
- **standard_tab.dart 展开 item 底部新增分割线与编辑入口**：0.5dp 分割线（rgba(229,229,229,1)，左右各 16dp 边距）；ico_ai_edit.webp + "编辑" 文字居中排列，底部 17dp 间距；点击预留空回调（待后续接入编辑页）

**2.10 Flutter 层 - 标准 Tab 新增播放页入口并实现摄像头实时播放页**

- **presentation/widgets/standard_item_card.dart 新增（提取公共 widget）**：将 standard_tab.dart 中的 _StandardItem → StandardItemCard；将 _TagCapsule → StandardTagCapsule，供标准 Tab 和播放页共用
- **presentation/pages/camera_play_page.dart 新增播放页**：接收 cameraId / cameraName / thumbUrl? / standards 四个参数；顶部 AppBar 展示摄像头名称；视频区 343×193dp：WDZPlayerWidget 实时播放，封面图占位（thumbUrl 或 with_out_pic_4.png），播放状态三态覆盖层（未播→播放按钮 / 连接中→loading / 播放中→透出画面）；下方白色圆角卡片（12dp）：摄像头信息头（图标+名称+N条标准）+ 标准列表全展开 + 编辑 footer（预留 onTap）
- **修复播放按钮不显示问题**：初始 playState=idle 导致 loading 一直显示、播放按钮从未出现；新增 _playRequested 标志区分「初始未播(idle)」与「连接中(idle)」
- **presentation/tabs/standard_tab.dart 接入播放页跳转**：图片区 onTap 填入 Navigator.push → CameraPlayPage；两处 _StandardItem 替换为 StandardItemCard；删除已迁移的 _StandardItem / _TagCapsule 类定义

**2.11 Flutter 层 - 新增标准编辑页，支持批量编辑/排序/删除**

- 新增标准编辑页，支持批量编辑/排序/删除
- 标准编辑页保存逻辑优化
- 标准编辑页开放新增功能并引入 configId 透传
- 修复自定义频率输入键盘收起及标准总数未刷新，执行频率范围限制，编辑新增删除标准后接口刷新
- 视频播放页视频吸顶 & 标准编辑页新增条目自动跳底
- issue12：在首次post后尝试进行toggle，获取正确状态
- Flutter 层代码审查修复
- UI修改 + 跳转自定义执行频率的接口调用
- 拆分配置频率和开启toggle的接口
- 任务 Tab 接口拆分与 iOS 键盘修复：refactor(_CustomHoursRow) 自定义频率输入改为失焦提交，删除 dart:async / Timer / 防抖逻辑，输入框视为"草稿区"，避免用户删空准备重输时被 500ms 防抖回退覆盖
- 首次创建：POST 创建，直接使用返回的 enabled（标准异步生成中，不再额外 toggle）
- 任务开关由二态 Switch 升级为 4 态状态机按钮
- 修复即拍即检执行频率不一致

**2.12 双端协作与问题修复**

- 解决双端内容解析差异的问题
- 解决编译问题
- 文件侧同步兼容Android List 格式和 iOS Map 格式
- 修复 iOS 图片选择结果解析失败问题：根因：NativeBridgeService._parseSystemResourceResult 已将原生返回的 {datas: [items]} 扁平化为 List<item>，但 _handleImageSelectResult 仍按 params[0]['datas'] 取值，导致 iOS 路径取到 null；修复：_handleImageSelectResult 直接遍历 params 取 url，去掉多余的 params[0]['datas'] 层级；addEventListener 回调改为复用 parseSystemResourceResult 做归一化，去掉手动 images.add 包装；两条回传路径（onResult / addEventListener）统一走同一份解析逻辑
- 和仇老板以及IOS（李长恩）同步问题解决


### 3. 线上稳定性专项治理 - ANR 问题定位与修复

**3.1 IjkPlayView.openVideo() 同步调用 reset() 导致主线程阻塞 ANR（问题ID：B128B3C0CA45AAB053975F020BC81545）**

- **根因定位**：IjkMediaPlayer.reset() 内部通过 pthread_join 等待解码线程退出，属于阻塞操作。openVideo() 在网络回调（主线程）中被调用，导致主线程长时间等待，触发 ANR
- **修复方案**：新增 releasePlayerAsync() 方法，将旧播放器的 reset()/release() 移至后台线程 "ijk-release-thread" 执行，主线程仅同步完成：清空所有 listener（防止后台 reset 期间触发 UI 回调）、setDisplay(null)（立即断开 Surface，供新播放器使用）、状态重置与音频焦点释放
- **内存安全保障**：sReleasingPlayers 持有强引用防止 GC 提前回收，30s 超时兜底防止解码线程死锁导致内存泄漏
- **后续优化**：解决ANR修复后的网络问题

### 4. 主线代码优化与稳定性提升

**4.1 修复 RTSP 设备播放超时报错 - 主流含音频时跳过从流请求**

- **问题背景**：货架类摄像头（accessType=3）不支持从流，但系统仍会发起 startNewMediaPlay(isSlave:1) 请求，导致 16 秒 comm_timeout 超时，播放失败
- **修复方案**：PlayerPlatformView 从 Flutter play 数据中读取 aenabled 字段（startNewMediaPlay(isSlave:0) 返回 aenabled=true 表示主流已含音频），提取该字段作为 skipQueryToken 传入 play()，透传至 startPlay()；FlutterVideoPlayView.startPlay 两个重载新增 skipQueryToken 参数，直播分支（videoFlag==OTHER）当 skipQueryToken=true 时直接调用 startPlay2 播放主流 URL，跳过 queryKeyAccessToken，避免对不支持从流的 RTSP 设备发起从流请求
- **业务价值**：消除货架类摄像头 16 秒超时导致的播放失败问题，提升用户体验

### 5. 协助测试与工具支持

**5.1 添加 Flutter 和主线提交信息，协助测试判断是否是最新的包**

- 在 About 页面添加 Flutter 和主线的 Git commit 信息展示
- 方便测试同学快速判断当前包的版本是否为最新，提升测试效率

### 6. 主线需求支持

**6.1 【安卓】【商户端】店主自值守—店主值守期间进店事件推送消息中心**

- 实现店主值守期间进店事件推送到消息中心的功能
- 支持店主实时接收进店通知，提升店主值守体验

---

**本周期整体交付情况总结**：所有需求均按时交付，其中招财猫 DMS 设备管理和 CameraClaw 8期 AI 即拍即检均已上线运行；迭代周期内无 P0/P1 级线上故障。



## 二、质量（权重：20%，自评：4.5分）

### 1. 架构设计能力

**1.1 DMS 状态机架构设计（招财猫项目）**

- 设计并实现 7 状态 sealed class 状态机（Idle / ConnectingToRedirect / WaitingForNetworkInfo / ConnectingToDms / HeartbeatActive / Reconnecting / Error），1:1 复刻 CloudPos 成熟方案
- 定义 9 事件 sealed class 驱动状态转换，确保状态流转的可预测性和可维护性
- 实现指数退避重连机制（5/10/20/40/80/128s 封顶），提升网络异常场景下的稳定性
- 设计两阶段连接流程（连 redirect → 等 join_network(45s) → 切真 DMS），解决设备入网时序问题

**1.2 AI 即拍即检 Flutter 端架构设计（CameraClaw 8期）**

- 采用 Clean Architecture 分层设计：Domain（实体+仓库接口）→ Infrastructure（DTO+Repository实现）→ Presentation（Cubit状态管理+UI）
- 设计 4 个独立 Cubit（HeaderCubit / ReportCubit / TaskCubit / StandardCubit），各自管理独立状态，避免状态耦合
- 实现 Mock 优先开发策略：先用 InstantCheckRepositoryMockImpl 完成 UI 开发，后期无缝切换到 InstantCheckRepositoryImpl 真实接口，降低前后端并行开发的阻塞
- 设计 StandardViewMode 枚举（byCamera / byStore）支持双视图切换，提升代码可扩展性

**1.3 ANR 异步释放机制设计（稳定性治理）**

- 识别 IjkMediaPlayer.reset() 内部 pthread_join 的阻塞特性，设计异步释放机制
- 主线程仅同步完成关键操作（清空 listener、断开 Surface、状态重置），耗时的 reset()/release() 移至后台线程
- 设计 sReleasingPlayers 强引用池 + 30s 超时兜底机制，平衡内存安全与泄漏风险

### 2. 代码质量主动优化

**2.1 DMS 模块结构精简（招财猫项目）**

- 主动发起重构：将 DmsManager 和 DmsRepositoryImpl 合并改名为 DmsService，消除不必要的抽象层
- 修复双订阅状态分裂问题：识别启动/重连/退网三处并发导致的状态不一致，统一状态管理入口
- 重构拦截器部分，让其可以透传白名单，提升代码灵活性

**2.2 AI 即拍即检接口优化（CameraClaw 8期）**

- 消除重复 GET /configs 请求：updateTaskConfig 改为返回 TaskConfig，直接解析 toggle 接口返回结果，task_cubit 用返回值更新状态，删除冗余的 getTaskConfig 验证调用
- 拆分配置频率和开启 toggle 的接口，提升接口职责单一性
- 首次创建优化：POST 创建后直接使用返回的 enabled（标准异步生成中，不再额外 toggle），减少不必要的网络请求

**2.3 Native 层代码规范化（CameraClaw 8期）**

- 提取 URL 常量到 DataManager.Urls，消除散落的硬编码字符串
- 提取 Banner 文案到字符串资源文件，替换 7 处硬编码（含 5 处历史遗留）
- 统一使用 getString(R.string.*) 和参数化格式串，提升国际化支持和可维护性

### 3. 问题定位能力

**3.1 ANR 根因定位（稳定性治理）**

- 通过 ANR trace 分析，精准定位 IjkMediaPlayer.reset() 内部 pthread_join 的阻塞根因
- 识别 openVideo() 在网络回调（主线程）中被调用的调用链路
- 定位问题 ID：B128B3C0CA45AAB053975F020BC81545

**3.2 RTSP 设备播放超时问题定位（主线优化）**

- 定位货架类摄像头（accessType=3）不支持从流，但系统仍会发起 startNewMediaPlay(isSlave:1) 请求，导致 16 秒 comm_timeout 超时
- 识别主流含音频时无需请求从流的优化点
- 设计 skipQueryToken 机制跳过从流请求，消除超时问题

**3.3 双端内容解析差异问题定位（CameraClaw 8期）**

- 定位 iOS 图片选择结果解析失败根因：NativeBridgeService._parseSystemResourceResult 已将 {datas: [items]} 扁平化为 List<item>，但 _handleImageSelectResult 仍按 params[0]['datas'] 取值
- 识别 Android 走 addEventListener 路径时手动 images.add(map) 包了一层，恰好凑上 buggy 的取值逻辑，属巧合并非正确实现
- 统一两条回传路径（onResult / addEventListener）走同一份解析逻辑，消除平台差异

**3.4 Banner 吸顶问题根因排查（CameraClaw 8期）**

- 首次误诊：以为 <include> 不传递 app:layout_scrollFlags，实测 scrollFlags=1，方向错误
- 通过 OnOffsetChangedListener log 确认 verticalOffset 能到 -totalScrollRange(-908)，说明 AppBarLayout 整体滚动正常
- 真实根因：banner 作为 AppBarLayout 兄弟节点时，LinearLayout 位置基于 CTB 展开高度（~965px），AppBarLayout 上移 908px 后 banner 屏幕 Y≈57px，永远不会完全离屏
- 修复：将 banner 移入 CTB 内 LinearLayout，与 cl_header 共同随 CTB 折叠

### 4. 提测质量说明

本周期 Android 侧交付需求提测质量稳定，**无 P0/P1 级 Bug**。招财猫 DMS 设备管理和 CameraClaw 8期 AI 即拍即检均已上线运行，线上稳定。



## 三、AI应用落地成果-个人效能（权重：5%，自评：4.0分）

### 1. AI 工具使用全景

本周期深度使用 **Claude Code、Cursor、Kiro、豆包、DeepSeek、通义千问** 共 6 款 AI 工具，覆盖评分标准定义的 4 类使用场景，形成工具矩阵化应用：

- **Claude Code / Cursor / Kiro**：主力承担 IDE 内编程辅助与重构任务
- **豆包 / DeepSeek / 通义千问**：承担独立问题咨询、方案对比、快速查询等轻量场景，按问题类型做工具选型分流

### 2. 场景一：AI 辅助编程（高频使用）

**2.1 代码生成与智能补全**

- **招财猫 DMS 设备管理**：MQTT 客户端集成、状态机转换逻辑、心跳上报机制、指数退避重连算法等核心代码由 AI 辅助生成，显著降低样板代码编写耗时
- **CameraClaw 8期 AI 即拍即检**：Flutter 端 Domain/Infrastructure/Presentation 三层架构代码、4 个 Cubit 状态管理、DTO 映射逻辑、UI 组件（ReportCard、TaskTab、StandardTab）等大量业务代码由 AI 辅助生成
- **Native 层 UI 组件**：Banner 布局 XML、状态控制逻辑、接口调用代码等由 AI 辅助完成

**2.2 代码重构与优化**

- **DMS 模块结构精简**：借助 AI 完成 DmsManager 和 DmsRepositoryImpl 合并的重构方案设计，再人工校正业务细节
- **AI 即拍即检接口优化**：AI 辅助完成 updateTaskConfig 返回值优化、消除重复请求的代码重构
- **Native 层代码规范化**：AI 辅助提取 URL 常量、字符串资源化、格式串参数化等重构工作

### 3. 场景二：AI 辅助排查问题（深度使用）

**3.1 ANR 根因定位**

- 借助 AI 分析 ANR trace，快速识别 IjkMediaPlayer.reset() 内部 pthread_join 的阻塞链路
- AI 辅助对比异步释放方案的优劣（后台线程 vs 线程池 vs 协程），形成技术选型依据
- AI 辅助设计 sReleasingPlayers 强引用池 + 超时兜底机制

**3.2 RTSP 设备播放超时问题定位**

- AI 辅助分析 startNewMediaPlay(isSlave:1) 超时日志，快速定位货架类摄像头不支持从流的根因
- AI 辅助设计 skipQueryToken 机制，提供多种实现方案对比

**3.3 双端内容解析差异问题定位**

- AI 辅助分析 NativeBridgeService._parseSystemResourceResult 的数据流转逻辑
- AI 辅助识别 Android 和 iOS 两条回传路径的差异，提供统一解析方案

**3.4 Banner 吸顶问题定位**

- AI 辅助分析 AppBarLayout 滚动机制和 OnOffsetChangedListener 日志
- AI 辅助推导 banner 位置计算逻辑，快速锁定根因

### 4. 场景三：AI 辅助文档整理

**4.1 技术方案文档**

- DMS 状态机设计文档：AI 辅助完成状态转换矩阵、事件定义、重连机制等技术方案的结构化输出
- ANR 异步释放方案文档：AI 辅助完成根因分析、方案选型对比、改造落地说明等技术文档
- AI 即拍即检架构设计文档：AI 辅助完成 Clean Architecture 分层设计、Cubit 状态管理、Mock 优先开发策略等文档

**4.2 接口文档与注释**

- AI 辅助生成 DMS 相关接口的注释和文档
- AI 辅助生成 AI 即拍即检相关 DTO 的字段说明和映射逻辑注释

### 5. 场景四：AI 辅助 UI/UX 分析

**5.1 设计稿还原**

- AI 辅助分析设计稿尺寸、颜色、间距等细节，生成对应的 Flutter/Android 布局代码
- AI 辅助识别设计稿中的组件复用点，提取公共 widget（如 StandardItemCard、StandardTagCapsule）

**5.2 UI 问题定位**

- AI 辅助分析 Banner 吸顶问题、TabBar 背景变暗问题、文案换行问题等 UI 异常
- AI 辅助提供多种 UI 修复方案对比

### 6. 效率提升评估与记录佐证

**6.1 综合效率提升**

本周期 AI 工具参与深度与广度较以往显著提升，综合评估核心工作场景 **效率提升约 50~60%**：

- **复杂排查类任务**（ANR 根因定位、RTSP 超时定位、双端解析差异）：原本需 0.5~1 天的排查工作，AI 辅助后 2~4 小时内可定位，提升约 60%
- **业务功能类代码**（DMS 设备管理、AI 即拍即检）：中高度复用场景（如状态机、Cubit、DTO 映射）提升约 50%
- **文档产出类任务**（技术方案文档、接口文档）：结构化文档提升约 50~60%

**6.2 使用记录可追溯**

- Claude Code、Cursor、Kiro 的 IDE 内对话会话与代码变更历史完整保留
- DeepSeek、豆包、通义千问的独立咨询记录可回溯
- 核心产出物（DMS 状态机设计、ANR 异步释放方案、AI 即拍即检架构设计）均可作为 AI 协同产出佐证材料



## 四、部门/产品线AI落地价值（权重：10%，自评：4.5分）

### 1. 项目概述

本周期深度参与公司核心 AI 产品 **CameraClaw（AI 视频分析助手）8期 - AI 即拍即检功能** 的研发落地，作为 Android 端和 Flutter 端核心开发，承担 Native 层 Banner 入口、Flutter 端完整详情页（报告Tab、任务Tab、标准Tab）、摄像头实时播放页、标准编辑页等关键模块交付。项目以端侧 AI 交互能力为核心，将 AI 视频分析能力融入门店巡检与业务管理场景，当前已完成核心功能开发并上线运行。

### 2. AI 能力落地产出

**2.1 AI 交互架构落地**

- 完成 Native 层 Banner 入口的 4 种状态控制逻辑（NO_CAMERA / NO_TASK / RUNNING_NO_REPORT / RUNNING_WITH_REPORT），支撑 AI 即拍即检功能的入口展示与状态流转
- 完成 Flutter 端 Clean Architecture 分层架构（Domain / Infrastructure / Presentation），为后续 AI 能力扩展提供可复用的前端架构底座
- 实现 4 个独立 Cubit 状态管理（HeaderCubit / ReportCubit / TaskCubit / StandardCubit），支撑 AI 即拍即检功能的复杂状态管理

**2.2 AI 业务场景功能交付**

深度参与以下 AI 业务场景的端侧能力落地：

- **AI 报告管理**：日报/周报切换、报告卡片展示（检测时间段、摄像头数、标准数、异常数）、查看报告跳转 WebView
- **AI 任务配置**：执行频率选择（每小时/每2小时/自定义）、自定义小时数输入、任务开关（4 态状态机按钮）
- **AI 标准管理**：按摄像头/按门店汇总双视图、标准列表展示（标准名称、分类、来源、最近执行时间）、标准编辑（批量编辑/排序/删除/新增）
- **摄像头实时播放**：摄像头实时视频播放、播放状态三态覆盖层（未播→播放按钮 / 连接中→loading / 播放中→透出画面）、标准列表全展开

**2.3 AI 产品权限控制与入口优化**

- 完成 AI 即拍即检入口的权限控制（无 DEVICE_NETWORK_REGIST 权限时弹 toast 拦截）
- 完成 Banner 状态接入真实接口（getAiScanConfigs），从 Mock 切换为真实业务逻辑
- 完成摄像头 thumbUrl 传入 Flutter 路由参数，支撑摄像头缩略图展示

### 3. 落地进展与价值佐证

**3.1 项目进展**

- AI 即拍即检功能已完成开发并上线运行
- 已完成 Native 层 Banner 入口、Flutter 端完整详情页、摄像头实时播放页、标准编辑页等关键模块交付
- 已完成双端协作与问题修复（iOS 图片选择结果解析失败、双端内容解析差异等）

**3.2 初步价值体现**

- **功能覆盖度**：AI 即拍即检功能已覆盖报告管理、任务配置、标准管理、摄像头实时播放 4 大核心业务场景
- **架构复用性**：Clean Architecture 分层架构、Cubit 状态管理、Mock 优先开发策略等具备高复用性，可标准化复用于后续 AI 类功能接入
- **用户体验**：通过 Banner 入口、报告卡片、任务配置、标准管理等功能，为用户提供完整的 AI 即拍即检体验闭环

**3.3 佐证材料**

- 代码产出：AI 即拍即检相关代码已全部合入主干，可追溯
- 上线记录：AI 即拍即检功能已上线运行，可在门店首页查看 Banner 入口
- 双端协作记录：与 iOS 同学（李长恩）、后端同学（仇老板）的协作记录可追溯



## 五、工作饱和度-JIRA填写（权重：10%，自评：4.5分）

每日按时更新工时，颗粒度合理，精确到 1 小时，可准确反映实际工作内容与投入。

本月工时主要分布在以下板块：

- **招财猫 DMS 设备管理**（行号 1-115）：Flutter 端从 0 到 1 完整实现 DMS 核心能力，包含平台层、数据层、Repository 层、领域层、状态机基础设施、服务层、表现层、DI 模块装配等全栈开发
- **CameraClaw 8期 AI 即拍即检**（行号 121-569）：Native 层 Banner 入口与权限控制、Flutter 端完整详情页（报告Tab、任务Tab、标准Tab）、摄像头实时播放页、标准编辑页、接口对接与完整实现、双端协作与问题修复等
- **ANR 稳定性治理**（行号 573-589）：IjkPlayView.openVideo() 同步调用 reset() 导致主线程阻塞 ANR 的根因定位与修复
- **协助测试**（行号 595-597）：添加 Flutter 和主线提交信息，协助测试判断是否是最新的包
- **主线代码优化与稳定性提升**（行号 601-613）：修复 RTSP 设备播放超时报错 - 主流含音频时跳过从流请求
- **主线需求支持**（行号 617-618）：店主自值守—店主值守期间进店事件推送消息中心

工时分布与实际工作重点高度一致，覆盖业务需求交付、架构设计、稳定性治理、跨项目支持等多维度工作，能够客观反映本周期实际投入饱和度。

## 六、协同性（权重：5%，自评：3.0分）

### 1. 跨端协作

**1.1 CameraClaw 8期 AI 即拍即检双端协作**

- 与 iOS 同学（李长恩）同步问题解决：iOS 图片选择结果解析失败问题、双端内容解析差异问题
- 统一两条回传路径（onResult / addEventListener）走同一份解析逻辑，消除平台差异
- 和仇老板（后端）同步 AI 即拍即检接口对接、字段映射、数据结构等问题

**1.2 招财猫 DMS 设备管理跨端对齐**

- 1:1 复刻 CloudPos 成熟方案（状态机、事件定义、重连机制等），确保 Flutter 端与原生端行为一致
- 协议参数与 CloudPos 对齐，确保设备管理能力的一致性

### 2. 协助测试

- 添加 Flutter 和主线提交信息到 About 页面，方便测试同学快速判断当前包的版本是否为最新
- 提供 Charles 抓包能力支持（AI 即拍即检 debug 模式下手机数据转发方案），降低测试门槛，提升联调效率

### 3. 需求沟通前置参与

- 参与 CameraClaw 8期需求评审（4.22），提前识别技术风险点
- 主动与后端同学沟通接口字段映射、数据结构等问题，推动整体排期决策

## 七、创新性（权重：5%，自评：3.0分）

### 1. DMS 状态机架构设计

针对招财猫 DMS 设备管理的复杂状态流转需求，自主设计并落地基于状态机模型的架构方案：

- **7 状态 sealed class**（Idle / ConnectingToRedirect / WaitingForNetworkInfo / ConnectingToDms / HeartbeatActive / Reconnecting / Error），以显式状态流转替代隐式时间等待逻辑
- **9 事件 sealed class** 驱动状态转换，确保状态流转的可预测性和可维护性
- **指数退避重连机制**（5/10/20/40/80/128s 封顶），提升网络异常场景下的稳定性
- **两阶段连接流程**（连 redirect → 等 join_network(45s) → 切真 DMS），解决设备入网时序问题

方案已上线运行，彻底解决设备入网、心跳上报、断线重连等复杂场景的状态管理问题，为后续设备管理类功能的演进提供了可复用的架构基础。

### 2. ANR 异步释放机制设计

针对 IjkMediaPlayer.reset() 内部 pthread_join 的阻塞特性，自主设计并落地异步释放机制：

- **主线程仅同步完成关键操作**（清空 listener、断开 Surface、状态重置），耗时的 reset()/release() 移至后台线程 "ijk-release-thread" 执行
- **sReleasingPlayers 强引用池 + 30s 超时兜底机制**，平衡内存安全与泄漏风险
- **立即断开 Surface**，供新播放器使用，避免 Surface 资源竞争

方案已上线运行，彻底解决 openVideo() 在网络回调（主线程）中被调用导致的 ANR 问题，提升播放器切换场景的稳定性。

### 3. AI 即拍即检 Clean Architecture 分层架构

针对 AI 即拍即检功能的复杂业务逻辑，自主设计并落地 Clean Architecture 分层架构：

- **Domain 层**（实体+仓库接口）：定义业务实体和仓库接口，确保业务逻辑与技术实现解耦
- **Infrastructure 层**（DTO+Repository实现）：实现 DTO 映射和 Repository 接口，支持 Mock 优先开发策略
- **Presentation 层**（Cubit状态管理+UI）：实现 4 个独立 Cubit（HeaderCubit / ReportCubit / TaskCubit / StandardCubit），各自管理独立状态，避免状态耦合

方案已上线运行，为后续 AI 类功能接入提供了可复用的架构基础，显著降低新功能开发的复杂度和维护成本。

---

## 月度绩效总分值

**综合得分：4.33分**

**等级：优秀**

---

## 总结与建议

### 本月工作亮点

1. **业务贡献突出**：按时完成招财猫 DMS 设备管理、CameraClaw 8期 AI 即拍即检、ANR 稳定性治理等多个方向的需求交付，无 P0/P1 级线上故障
2. **架构设计能力强**：DMS 状态机架构、AI 即拍即检 Clean Architecture 分层架构、ANR 异步释放机制等设计方案均已上线运行，具备高复用性
3. **问题定位能力强**：ANR 根因定位、RTSP 设备播放超时问题定位、双端内容解析差异问题定位、Banner 吸顶问题定位等均快速定位并修复
4. **AI 工具使用深度高**：深度使用 6 款 AI 工具，覆盖编程、排查、文档、UI 分析 4 类场景，效率提升约 50~60%
5. **代码质量高**：提测质量稳定，无 P0/P1 级 Bug，代码规范化程度高

### 改进方向

1. **协同性可进一步提升**：可主动参与更多跨部门协作，提升沟通效率
2. **创新性可进一步拓展**：可探索更多创新性技术方案，提升技术影响力

