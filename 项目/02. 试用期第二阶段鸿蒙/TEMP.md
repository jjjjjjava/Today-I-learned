- 请问在这个row中，我该怎么让我的两个元素居中

  - ```
    Row() {
      // 展开/收起按钮（仅在有子项且非免打扰模式或是告警类型时显示）
      if (child.childList && child.childList.length > 0 &&
        (!this.isDisturb || child.code === 'OPERATION_ALARM')) {
        Text(this.expandedItems.has(index) ? "收起" : "展开")
          .fontSize(12)
          .fontColor('#666666')
          .margin({ right: 8 })
          .textAlign(TextAlign.Center)
    
        Image(this.expandedItems.has(index) ? $r('app.media.ico_up_arrow_gray') : $r('app.media.ico_down_arrow_gray'))
          .width(16)
          .height(16)
          .margin({ right: 8 })
      }
    }
    .width('100%')
    .padding({ left: 16, right: 16, top: 12, bottom: 12 })
    .backgroundColor('#F8F8F8')
    .onClick(() => {
      if (child.childList && child.childList.length > 0 &&
        (!this.isDisturb || child.code === 'OPERATION_ALARM')) {
        this.toggleExpanded(index)
      }
    })
    ```

- 现在会出现一个bug，二级项的Toggle点击后，有一定概率会导致三级项的Toggle不显示，但是收起再展开就能显示出来了，请问这是为什么？

  - 我找到了问题所在！这个bug是由于状态更新的时机问题导致的。当二级项Toggle被点击时：

    1. 立即更新了数据状态（child.noDisturbingFlag 或 child.receiveMessageFlag）

    1. 但UI刷新可能滞后，导致 isThirdLevelSwitchEnabled(parentChild) 判断依然基于旧状态

    1. 三级项的Toggle因此可能被禁用或不显示

  - 问题的核心在于状态更新的原子性。让我修复这个问题：

- 想要在背景图片上层添加一个白色的内容区域，这个区域只包裹实际的文本和图片内容，而不是覆盖整个背景图片。







```
import { HttpRequestClient, ApiResponse } from '@ohos/common/src/main/ets/http/HttpRequestClient'
import { MessageConfigBean, MessageConfigResponse, UpdateMessageConfigParams, RequestData } from '../model/MessageConfigModel'
import { AxiosRequestConfig } from '@ohos/axios'

// 自定义错误类，用于替代任意类型的throw
class MessageConfigError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'MessageConfigError'
  }
}

// API端点接口
interface ApiEndpoints {
  GET_USER_MESSAGE_CONFIG: string
  UPDATE_USER_MESSAGE_CONFIG: string
  GET_SINGLE_MESSAGE_CONFIG: string
}

// 消息配置服务类，对应Android中的MessageApi和相关Presenter
export class MessageConfigService {
  private static instance: MessageConfigService
  private httpClient: HttpRequestClient = HttpRequestClient.instance()

  // API端点常量，对应Android中的DataManager.MessageConfig
  private static readonly API_ENDPOINTS: ApiEndpoints = {
    GET_USER_MESSAGE_CONFIG: '/messagehub-manage/userMessageConfig/getUserMessageConfigList',
    UPDATE_USER_MESSAGE_CONFIG: '/messagehub-manage/userMessageConfig/updateUserMessageConfig',
    GET_SINGLE_MESSAGE_CONFIG: '/messagehub-manage/userMessageConfig/getUserMessageConfig'
  }

  public static getInstance(): MessageConfigService {
    if (!MessageConfigService.instance) {
      MessageConfigService.instance = new MessageConfigService()
    }
    return MessageConfigService.instance
  }

  // 获取消息配置列表，对应Android中的getMessageConfig
  async getMessageConfig(): Promise<MessageConfigBean[]> {
    try {
      console.debug('MessageConfigService: 开始获取消息配置列表')

      const config: AxiosRequestConfig = {
        url: MessageConfigService.API_ENDPOINTS.GET_USER_MESSAGE_CONFIG,
        method: 'GET'
      }

      // 调用HTTP请求
      const response = await this.httpClient.get<ApiResponse<MessageConfigBean[]>>(config)
      
      if (response.isError) {
        throw new MessageConfigError(response.message || '获取消息配置失败')
      }

      console.debug(`MessageConfigService: 获取消息配置成功，共${response.data?.length || 0}条数据`)
      return response.data || []

    } catch (error) {
      console.error(`MessageConfigService: 获取消息配置失败: ${error}`)
      throw new MessageConfigError(error instanceof Error ? error.message : '获取消息配置失败')
    }
  }

  // 更新消息配置，对应Android中的updateMessageConfig  
  async updateMessageConfig(params: UpdateMessageConfigParams): Promise<boolean> {
    try {
      console.debug(`MessageConfigService: 开始更新消息配置: ${JSON.stringify(params)}`)

      // 构建请求数据，对应Android中的JSONObject构建逻辑
      const requestData: RequestData = {
        messageTypeId: params.messageTypeId
      }

      // 只添加非空的参数，对应Android中的条件判断
      if (params.noDisturbingFlag !== undefined) {
        requestData.noDisturbingFlag = params.noDisturbingFlag
      }
      if (params.receiveMessageFlag !== undefined) {
        requestData.receiveMessageFlag = params.receiveMessageFlag
      }
      if (params.importanceFlag !== undefined) {
        requestData.importanceFlag = params.importanceFlag
      }

      const config: AxiosRequestConfig = {
        url: MessageConfigService.API_ENDPOINTS.UPDATE_USER_MESSAGE_CONFIG,
        method: 'POST',
        data: requestData,
        headers: {
          'Content-Type': 'application/json'
        }
      }

      // 调用HTTP请求
      const response = await this.httpClient.post<ApiResponse<string>>(config)
      
      if (response.isError) {
        throw new MessageConfigError(response.message || '更新消息配置失败')
      }

      console.debug('MessageConfigService: 更新消息配置成功')
      return true

    } catch (error) {
      console.error(`MessageConfigService: 更新消息配置失败: ${error}`)
      throw new MessageConfigError(error instanceof Error ? error.message : '更新消息配置失败')
    }
  }

  // 批量更新消息配置
  async batchUpdateMessageConfig(paramsList: UpdateMessageConfigParams[]): Promise<boolean> {
    try {
      console.debug(`MessageConfigService: 开始批量更新消息配置，共${paramsList.length}个请求`)

      // 串行执行所有更新请求，确保顺序执行
      for (const params of paramsList) {
        await this.updateMessageConfig(params)
        // 添加小延迟，避免服务器压力过大
        await new Promise<void>(resolve => setTimeout(resolve, 10))
      }

      console.debug('MessageConfigService: 批量更新消息配置成功')
      return true

    } catch (error) {
      console.error(`MessageConfigService: 批量更新消息配置失败: ${error}`)
      throw new MessageConfigError(error instanceof Error ? error.message : '批量更新消息配置失败')
    }
  }

  // 获取单个消息配置，对应Android中的getSingleMessageConfig
  async getSingleMessageConfig(msgTypeCode: string): Promise<MessageConfigBean> {
    try {
      console.debug(`MessageConfigService: 开始获取单个消息配置: ${msgTypeCode}`)

      const config: AxiosRequestConfig = {
        url: MessageConfigService.API_ENDPOINTS.GET_SINGLE_MESSAGE_CONFIG,
        method: 'GET',
        params: {
          msgTypeCode: msgTypeCode
        }
      }

      // 调用HTTP请求
      const response = await this.httpClient.get<ApiResponse<MessageConfigBean>>(config)
      
      if (response.isError) {
        throw new MessageConfigError(response.message || '获取单个消息配置失败')
      }

      console.debug('MessageConfigService: 获取单个消息配置成功')
      return response.data as MessageConfigBean

    } catch (error) {
      console.error(`MessageConfigService: 获取单个消息配置失败: ${error}`)
      throw new MessageConfigError(error instanceof Error ? error.message : '获取单个消息配置失败')
    }
  }
} 
```



```
import { router } from '@kit.ArkUI'
import { MessageConfigBean } from '../model/MessageConfigModel'
import { MessageConfigService } from '../service/MessageConfigService'

@Entry({ routeName: 'ReceiveMessageSettingPage' })
@Preview
@Component
struct ReceiveMessageSettingPage {
  @State isDisturb: boolean = false
  @State pageTitle: string = "接收消息设置"
  @State tipText: string = "关闭后将无法接收消息，错过的消息无法恢复"
  @State messageConfigList: MessageConfigBean[] = []
  @State isLoading: boolean = true
  @State errorMessage: string = ""
  @State showRetryButton: boolean = false
  private messageService = MessageConfigService.getInstance()

  aboutToAppear() {
    // 获取传递的参数
    const params = router.getParams() as Record<string, Object>
    if (params && typeof params.isDisturb === 'boolean') {
      this.isDisturb = params.isDisturb
    }
    
    // 根据参数设置页面标题和提示文字
    if (this.isDisturb) {
      this.pageTitle = "免打扰设置"
      this.tipText = "打开「开关」,将不再收到APP通知栏推送,但不影响消息中心留存"
    } else {
      this.pageTitle = "接收消息设置"
      this.tipText = "关闭「开关」,将不再收到新消息,且关闭期间错过的消息无法恢复"
    }

    // 加载消息配置数据
    this.loadMessageConfig()
  }

  onPageShow() {
    // 页面显示时重新加载数据（对应Android的onResume）
    this.loadMessageConfig()
  }

  // 加载消息配置数据
  async loadMessageConfig() {
    try {
      this.isLoading = true
      this.errorMessage = ""
      this.showRetryButton = false
      
      // 使用真实API获取数据，对应Android中的presenter.getUserMessageConfig(this)
      this.messageConfigList = await this.messageService.getMessageConfig()
      
    } catch (error) {
      console.error('加载消息配置失败:', error)
      this.errorMessage = error instanceof Error ? error.message : "加载失败，请检查网络连接"
      this.showRetryButton = true
    } finally {
      this.isLoading = false
    }
  }

  // 重试加载数据
  onRetryClick() {
    this.loadMessageConfig()
  }

  // 处理列表项点击事件
  onMessageItemClick(item: MessageConfigBean, index: number) {
    // 对应Android中的callback(position)逻辑
    // 跳转到二级设置页面
    router.pushUrl({
      url: '@bundle:com.ovopark.wdz/lib_msg_setting/ets/pages/SecondReceiveMessageSettingPage',
      params: {
        isDisturb: this.isDisturb,
        messageConfig: item
      }
    }).catch((error: Error) => {
      console.error('跳转到二级设置页面失败:', error)
    })
  }

  @Builder
  MessageItemBuilder(item: MessageConfigBean, index: number) {
    Row() {
      Text(item.name)
        .fontColor($r('app.color.color_FF333333'))
        .fontSize(15)
        .layoutWeight(1)

      Image($r('app.media.icon_forward'))
        .width(18)
        .height(18)
    }
    .width('100%')
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(12)
    .margin({ top: index === 0 ? 16 : 8 })
    .onClick(() => {
      this.onMessageItemClick(item, index)
    })
  }

  @Builder
  LoadingBuilder() {
    Column() {
      LoadingProgress()
        .width(40)
        .height(40)
        .color($r('app.color.color_FF4285F4'))
      
      Text("加载中...")
        .fontColor('#999999')
        .fontSize(14)
        .margin({ top: 8 })
    }
    .width('100%')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
    .layoutWeight(1)
  }

  @Builder
  EmptyBuilder() {
    Column() {
      Text("暂无消息设置")
        .fontColor('#999999')
        .fontSize(16)
    }
    .width('100%')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
    .backgroundColor(Color.White)
    .margin({ top: 16 })
    .borderRadius(12)
    .padding(60)
  }

  @Builder
  ErrorBuilder() {
    Column() {
      Text("😔")
        .fontSize(32)
        .margin({ bottom: 8 })
      
      Text(this.errorMessage)
        .fontColor('#FF6B6B')
        .fontSize(14)
        .textAlign(TextAlign.Center)
        .margin({ bottom: 16 })
        .maxLines(3)

      if (this.showRetryButton) {
        Button("重试")
          .fontSize(14)
          .backgroundColor($r('app.color.color_FF4285F4'))
          .fontColor(Color.White)
          .borderRadius(8)
          .padding({ left: 24, right: 24, top: 8, bottom: 8 })
          .onClick(() => {
            this.onRetryClick()
          })
      }
    }
    .width('100%')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
    .backgroundColor(Color.White)
    .margin({ top: 16 })
    .borderRadius(12)
    .padding(40)
  }

  build() {
    Column() {
      // 顶部标题栏
      RelativeContainer() {
        Image($r('app.media.icon_back'))
          .width(22)
          .height(22)
          .alignRules({
            left: { anchor: '__container__', align: HorizontalAlign.Start },
            center: { anchor: '__container__', align: VerticalAlign.Center }
          })
          .margin({ left: 16 })
          .onClick(() => {
            router.back()
          })

        Text(this.pageTitle)
          .fontColor($r('app.color.color_FF333333'))
          .fontSize(17)
          .fontWeight(FontWeight.Bold)
          .alignRules({
            center: { anchor: '__container__', align: VerticalAlign.Center },
            middle: { anchor: '__container__', align: HorizontalAlign.Center }
          })
      }
      .width('100%')
      .height(44)
      .backgroundColor(Color.White)

      // 提示文字
      Text(this.tipText)
        .width('100%')
        .padding({ left: 16, right: 16, top: 16, bottom: 16 })
        .fontColor('#7F7F7F')
        .fontSize(11)
        .textAlign(TextAlign.Center)
        .backgroundColor($r('app.color.color_F4F4F6'))

      // 消息设置列表
      if (this.isLoading) {
        this.LoadingBuilder()
      } else if (this.errorMessage !== "") {
        this.ErrorBuilder()
      } else if (this.messageConfigList.length === 0) {
        this.EmptyBuilder()
      } else {
        List() {
          ForEach(this.messageConfigList, (item: MessageConfigBean, index: number) => {
            ListItem() {
              this.MessageItemBuilder(item, index)
            }
          })
        }
        .listDirection(Axis.Vertical)
        .scrollBar(BarState.Auto)
        .backgroundColor($r('app.color.color_F4F4F6'))
        .layoutWeight(1)
        .padding({ left: 16, right: 16, bottom: 16 })
        .edgeEffect(EdgeEffect.Spring)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor($r('app.color.color_F4F4F6'))
  }
}
```





```
import { router } from '@kit.ArkUI'
import { MessageConfigBean, Child, UpdateMessageConfigParams, MessageIconHelper, GrandChildState } from '../model/MessageConfigModel'
import { MessageConfigService } from '../service/MessageConfigService'
import { ToastUtils } from '@ohos/common'

@Entry({ routeName: 'SecondReceiveMessageSettingPage' })
@Component
struct SecondReceiveMessageSettingPage {
  @State isDisturb: boolean = false
  @State pageTitle: string = "接收消息设置"
  @State tipText: string = "关闭后将无法接收消息，错过的消息无法恢复"
  @State messageConfig: MessageConfigBean | null = null
  @State mainSwitchEnabled: boolean = false
  @State showMainSwitch: boolean = true
  @State isUpdating: boolean = false
  @State updateErrorMessage: string = ""
  @State expandedItems: Set<number> = new Set() // 记录展开的项目索引
  @State uiRefreshTrigger: number = 0 // 用于强制UI刷新的触发器
  private messageService = MessageConfigService.getInstance()

  aboutToAppear() {
    // 获取传递的参数
    const params = router.getParams() as Record<string, Object>
    if (params) {
      if (typeof params.isDisturb === 'boolean') {
        this.isDisturb = params.isDisturb
      }
      if (params.messageConfig) {
        this.messageConfig = params.messageConfig as MessageConfigBean
      }
    }
    
    // 根据参数设置页面标题和提示文字
    if (this.isDisturb) {
      this.pageTitle = "免打扰设置"
      this.tipText = "关闭后通知栏将不会推送消息，但消息接收不受影响"
      this.mainSwitchEnabled = this.messageConfig?.noDisturbingFlag === 1
      this.showMainSwitch = false // 对应Android中的visibility = View.GONE
    } else {
      this.pageTitle = "接收消息设置"  
      this.tipText = "关闭后将无法接收消息，错过的消息无法恢复"
      this.mainSwitchEnabled = this.messageConfig?.receiveMessageFlag === 1
      this.showMainSwitch = true
    }
  }

  // 显示成功提示
  showSuccessToast(message: string) {
    ToastUtils.showToast(message)
  }

  // 显示错误提示
  showErrorToast(message: string) {
    ToastUtils.showToast(`操作失败: ${message}`)
  }

  // 主开关状态变化
  async onMainSwitchChange(isOn: boolean) {
    if (this.isUpdating || !this.messageConfig) return
    
    // 第一步：立即更新UI状态，模仿Android的做法
    this.mainSwitchEnabled = isOn
    
    // 更新所有子项的本地状态（仅UI状态，不调用API）
    this.messageConfig.childList.forEach((child: Child) => {
      if (this.isDisturb) {
        child.noDisturbingFlag = isOn ? 1 : 0
        child.childList?.forEach((grandChild: Child) => {
          grandChild.noDisturbingFlag = isOn ? 1 : 0
        })
      } else {
        child.receiveMessageFlag = isOn ? 1 : 0
        child.childList?.forEach((grandChild: Child) => {
          grandChild.receiveMessageFlag = isOn ? 1 : 0
        })
      }
    })

    // 强制触发UI重新渲染
    this.forceUIUpdate()

    // 第二步：异步调用单个API更新主项（模仿Android）
    this.updateMainConfigAsync(isOn)
  }

  // 异步更新主配置，避免阻塞UI
  private async updateMainConfigAsync(isOn: boolean) {
    if (!this.messageConfig) return
    
    try {
      this.isUpdating = true
      this.updateErrorMessage = ""
      
      // 只更新主项，模仿Android的策略
      const mainParam: UpdateMessageConfigParams = {
        messageTypeId: this.messageConfig.messageTypeId
      }
      
      if (this.isDisturb) {
        mainParam.noDisturbingFlag = isOn ? 1 : 0
        this.messageConfig.noDisturbingFlag = isOn ? 1 : 0
      } else {
        mainParam.receiveMessageFlag = isOn ? 1 : 0
        this.messageConfig.receiveMessageFlag = isOn ? 1 : 0
      }

      // 调用单个API更新主配置
      await this.messageService.updateMessageConfig(mainParam)
      
      // 显示成功提示
      this.showSuccessToast(isOn ? "已开启" : "已关闭")
      
    } catch (error) {
      console.error('更新主开关失败:', error)
      this.updateErrorMessage = error instanceof Error ? error.message : "更新失败"
      
      // 恢复原状态
      this.mainSwitchEnabled = !isOn
      if (this.messageConfig) {
        if (this.isDisturb) {
          this.messageConfig.noDisturbingFlag = !isOn ? 1 : 0
        } else {
          this.messageConfig.receiveMessageFlag = !isOn ? 1 : 0
        }
        
        // 恢复子项状态
        this.messageConfig.childList.forEach((child: Child) => {
          if (this.isDisturb) {
            child.noDisturbingFlag = !isOn ? 1 : 0
            child.childList?.forEach((grandChild: Child) => {
              grandChild.noDisturbingFlag = !isOn ? 1 : 0
            })
          } else {
            child.receiveMessageFlag = !isOn ? 1 : 0
            child.childList?.forEach((grandChild: Child) => {
              grandChild.receiveMessageFlag = !isOn ? 1 : 0
            })
          }
        })
      }
      
      this.showErrorToast(this.updateErrorMessage)
      
    } finally {
      this.isUpdating = false
    }
  }

  // 二级项开关状态变化
  async onSecondLevelSwitchChange(child: Child, isOn: boolean, index: number) {
    if (this.isUpdating) return
    
    // 保存原始状态用于回滚
    const originalChildFlag = this.isDisturb ? child.noDisturbingFlag : child.receiveMessageFlag
    const originalGrandChildStates: GrandChildState[] = child.childList?.map((grandChild: Child): GrandChildState => {
      return {
        id: grandChild.messageTypeId,
        flag: this.isDisturb ? grandChild.noDisturbingFlag : grandChild.receiveMessageFlag
      }
    }) || []
    
    // 第一步：立即更新UI状态
    if (this.isDisturb) {
      child.noDisturbingFlag = isOn ? 1 : 0
    } else {
      child.receiveMessageFlag = isOn ? 1 : 0
    }

    // 更新所有三级子项状态
    child.childList?.forEach((grandChild: Child) => {
      if (this.isDisturb) {
        grandChild.noDisturbingFlag = isOn ? 1 : 0
      } else {
        grandChild.receiveMessageFlag = isOn ? 1 : 0
      }
    })

    // 强制触发UI重新渲染，确保三级项状态正确更新
    this.forceUIUpdate()

    // 第二步：异步调用API
    this.updateSecondLevelConfigAsync(child, isOn, index, originalChildFlag, originalGrandChildStates)
  }

  // 强制UI更新的辅助方法
  private forceUIUpdate() {
    // 通过更新刷新触发器来强制UI重新渲染
    // 这样可以确保所有依赖状态的UI组件都会重新计算
    this.uiRefreshTrigger = this.uiRefreshTrigger + 1
  }

  // 异步更新二级配置
  private async updateSecondLevelConfigAsync(
    child: Child, 
    isOn: boolean, 
    index: number,
    originalChildFlag: number,
    originalGrandChildStates: GrandChildState[]
  ) {
    try {
      this.isUpdating = true
      this.updateErrorMessage = ""
      
      // 只更新当前二级项，让服务端处理子项更新
      const childParam: UpdateMessageConfigParams = {
        messageTypeId: child.messageTypeId
      }
      
      if (this.isDisturb) {
        childParam.noDisturbingFlag = child.noDisturbingFlag
      } else {
        childParam.receiveMessageFlag = child.receiveMessageFlag
      }

      // 调用API更新配置
      await this.messageService.updateMessageConfig(childParam)

      // 检查是否需要关闭父级开关
      if (!isOn && this.messageConfig) {
        const hasEnabledChild = this.messageConfig.childList.some((item: Child) => {
          return this.isDisturb ? item.noDisturbingFlag === 1 : item.receiveMessageFlag === 1
        })
        
        if (!hasEnabledChild && this.mainSwitchEnabled) {
          this.mainSwitchEnabled = false
          if (this.isDisturb) {
            this.messageConfig.noDisturbingFlag = 0
          } else {
            this.messageConfig.receiveMessageFlag = 0
          }
          // 异步更新主配置，不等待
          this.updateMainConfigAsync(false)
        }
      }
      
      // 显示成功提示
      this.showSuccessToast(`${child.name} ${isOn ? "已开启" : "已关闭"}`)
      
    } catch (error) {
      console.error('更新二级项开关失败:', error)
      this.updateErrorMessage = error instanceof Error ? error.message : "更新失败"
      
      // 恢复原状态
      if (this.isDisturb) {
        child.noDisturbingFlag = originalChildFlag
      } else {
        child.receiveMessageFlag = originalChildFlag
      }
      
      // 恢复三级子项状态
      child.childList?.forEach((grandChild: Child) => {
        const originalState = originalGrandChildStates.find(state => state.id === grandChild.messageTypeId)
        if (originalState) {
          if (this.isDisturb) {
            grandChild.noDisturbingFlag = originalState.flag
          } else {
            grandChild.receiveMessageFlag = originalState.flag
          }
        }
      })
      
      this.showErrorToast(`${child.name} 设置失败`)
      
    } finally {
      this.isUpdating = false
    }
  }

  // 三级项开关状态变化
  async onThirdLevelSwitchChange(grandChild: Child, parentChild: Child, isOn: boolean) {
    if (this.isUpdating) return
    
    // 保存原始状态用于回滚
    const originalFlag = this.isDisturb ? grandChild.noDisturbingFlag : grandChild.receiveMessageFlag
    
    // 第一步：立即更新UI状态
    if (this.isDisturb) {
      grandChild.noDisturbingFlag = isOn ? 1 : 0
    } else {
      grandChild.receiveMessageFlag = isOn ? 1 : 0
    }

    // 第二步：异步调用API
    this.updateThirdLevelConfigAsync(grandChild, parentChild, isOn, originalFlag)
  }

  // 异步更新三级配置
  private async updateThirdLevelConfigAsync(
    grandChild: Child, 
    parentChild: Child, 
    isOn: boolean,
    originalFlag: number
  ) {
    try {
      this.isUpdating = true
      this.updateErrorMessage = ""
      
      // 更新三级项状态
      const updateParam: UpdateMessageConfigParams = {
        messageTypeId: grandChild.messageTypeId
      }
      
      if (this.isDisturb) {
        updateParam.noDisturbingFlag = grandChild.noDisturbingFlag
      } else {
        updateParam.receiveMessageFlag = grandChild.receiveMessageFlag
      }

      // 调用API更新配置
      await this.messageService.updateMessageConfig(updateParam)

      // 检查是否需要级联关闭父级开关
      if (!isOn) {
        this.checkAndUpdateParentStates(parentChild)
      }
      
      // 显示成功提示
      this.showSuccessToast(`${grandChild.name} ${isOn ? "已开启" : "已关闭"}`)
      
    } catch (error) {
      console.error('更新三级项开关失败:', error)
      this.updateErrorMessage = error instanceof Error ? error.message : "更新失败"
      
      // 恢复原状态
      if (this.isDisturb) {
        grandChild.noDisturbingFlag = originalFlag
      } else {
        grandChild.receiveMessageFlag = originalFlag
      }
      
      this.showErrorToast(`${grandChild.name} 设置失败`)
      
    } finally {
      this.isUpdating = false
    }
  }

  // 检查并更新父级状态（不阻塞UI）
  private async checkAndUpdateParentStates(parentChild: Child) {
    if (!parentChild.childList || !this.messageConfig) return

    // 检查是否需要关闭二级父项开关
    const hasEnabledGrandChild = parentChild.childList.some((item: Child) => {
      return this.isDisturb ? item.noDisturbingFlag === 1 : item.receiveMessageFlag === 1
    })
    
    if (!hasEnabledGrandChild) {
      // 更新二级父项状态
      if (this.isDisturb) {
        parentChild.noDisturbingFlag = 0
      } else {
        parentChild.receiveMessageFlag = 0
      }
      
      // 异步更新二级父项，不等待
      const parentParam: UpdateMessageConfigParams = {
        messageTypeId: parentChild.messageTypeId
      }
      if (this.isDisturb) {
        parentParam.noDisturbingFlag = 0
      } else {
        parentParam.receiveMessageFlag = 0
      }
      
      try {
        await this.messageService.updateMessageConfig(parentParam)
      } catch (error) {
        console.error('更新二级父项失败:', error)
        // 恢复状态但不影响UI
        if (this.isDisturb) {
          parentChild.noDisturbingFlag = 1
        } else {
          parentChild.receiveMessageFlag = 1
        }
      }

      // 检查是否需要关闭主开关
      const hasEnabledChild = this.messageConfig.childList.some((item: Child) => {
        return this.isDisturb ? item.noDisturbingFlag === 1 : item.receiveMessageFlag === 1
      })
      
      if (!hasEnabledChild && this.mainSwitchEnabled) {
        this.mainSwitchEnabled = false
        if (this.isDisturb) {
          this.messageConfig.noDisturbingFlag = 0
        } else {
          this.messageConfig.receiveMessageFlag = 0
        }
        // 异步更新主配置，不等待
        this.updateMainConfigAsync(false)
      }
    }
  }

  // 切换展开/收起状态
  toggleExpanded(index: number) {
    const newExpandedItems = new Set(this.expandedItems)
    if (newExpandedItems.has(index)) {
      newExpandedItems.delete(index)
    } else {
      newExpandedItems.add(index)
    }
    this.expandedItems = newExpandedItems
  }

  // 判断二级项的开关是否可用
  isSecondLevelSwitchEnabled(): boolean {
    if (this.isDisturb) {
      return true // 免打扰模式下总是可用
    } else {
      return this.mainSwitchEnabled // 接收消息模式下依赖主开关
    }
  }

  // 判断三级项的开关是否可用
  isThirdLevelSwitchEnabled(parentChild: Child): boolean {
    const parentEnabled = this.isDisturb ? parentChild.noDisturbingFlag === 1 : parentChild.receiveMessageFlag === 1
    if (this.isDisturb) {
      return parentEnabled
    } else {
      return this.mainSwitchEnabled && parentEnabled
    }
  }

  @Builder
  ThirdLevelItemBuilder(grandChild: Child, parentChild: Child) {
    Row() {
      Text(grandChild.name)
        .fontColor($r('app.color.color_FF333333'))
        .fontSize(14)
        .layoutWeight(1)
        .margin({ left: 20 }) // 增加缩进表示层级

      Toggle({ type: ToggleType.Switch, isOn: this.isDisturb ? grandChild.noDisturbingFlag === 1 : grandChild.receiveMessageFlag === 1 })
        .width(44)
        .height(24)
        .switchPointColor(Color.White)
        .selectedColor('#4285F4')
        .onChange((isOn: boolean) => {
          this.onThirdLevelSwitchChange(grandChild, parentChild, isOn)
        })
        .enabled(this.isThirdLevelSwitchEnabled(parentChild) && !this.isUpdating)
        .key(`third_toggle_${grandChild.messageTypeId}_${this.uiRefreshTrigger}`) // 使用key强制重新渲染
    }
    .width('100%')
    .padding({ left: 16, right: 16, top: 12, bottom: 12 })
    .backgroundColor('#F8F8F8')
    .opacity(this.isThirdLevelSwitchEnabled(parentChild) ? 1.0 : 0.5)
    .key(`third_item_${grandChild.messageTypeId}_${this.uiRefreshTrigger}`) // 整个行也使用key
  }

  @Builder
  SecondLevelItemBuilder(child: Child, index: number) {
    Column() {
      // 二级项主体
      Row() {
        Row() {
          // 添加消息类型图标
          Image(MessageIconHelper.getIcon(child.code))
            .width(20)
            .height(20)
            .margin({ right: 8 })

          Text(child.name)
            .fontColor($r('app.color.color_FF333333'))
            .fontSize(15)
            .layoutWeight(1)
        }
        .layoutWeight(1)
        .onClick(() => {
          if (child.childList && child.childList.length > 0 && 
              (!this.isDisturb || child.code === 'OPERATION_ALARM')) {
            this.toggleExpanded(index)
          }
        })

        Toggle({ type: ToggleType.Switch, isOn: this.isDisturb ? child.noDisturbingFlag === 1 : child.receiveMessageFlag === 1 })
          .width(44)
          .height(24)
          .switchPointColor(Color.White)
          .selectedColor('#4285F4')
          .onChange((isOn: boolean) => {
            this.onSecondLevelSwitchChange(child, isOn, index)
          })
          .enabled(this.isSecondLevelSwitchEnabled() && !this.isUpdating)
          .key(`second_toggle_${child.messageTypeId}_${this.uiRefreshTrigger}`) // 使用key强制重新渲染
      }
      .width('100%')
      .padding(16)
      .backgroundColor(Color.White)
      .borderRadius(12)
      .opacity(this.isSecondLevelSwitchEnabled() ? 1.0 : 0.5)

      Row() {
        // 展开/收起按钮（仅在有子项且非免打扰模式或是告警类型时显示）
        if (child.childList && child.childList.length > 0 &&
          (!this.isDisturb || child.code === 'OPERATION_ALARM')) {
          Text(this.expandedItems.has(index) ? "收起" : "展开")
            .fontSize(12)
            .fontColor('#666666')
            .margin({ right: 8 })
            .textAlign(TextAlign.Center)

          Image(this.expandedItems.has(index) ? $r('app.media.ico_up_arrow_gray') : $r('app.media.ico_down_arrow_gray'))
            .width(16)
            .height(16)
            .margin({ right: 8 })
        }
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 12, bottom: 12 })
      .backgroundColor('#F8F8F8')
      .justifyContent(FlexAlign.Center) // 核心居中属性
      .alignItems(VerticalAlign.Center) // 垂直居中
      .onClick(() => {
        if (child.childList && child.childList.length > 0 &&
          (!this.isDisturb || child.code === 'OPERATION_ALARM')) {
          this.toggleExpanded(index)
        }
      })

      // 三级子项列表（展开时显示）
      if (this.expandedItems.has(index) && child.childList && child.childList.length > 0) {
        Column() {
          ForEach(child.childList, (grandChild: Child) => {
            this.ThirdLevelItemBuilder(grandChild, child)
          })
        }
        .width('100%')
        .margin({ top: 4 })
        .borderRadius(12)
        .clip(true)
      }
    }
    .width('100%')
    // .margin({ top: index === 0 ? 16 : 8 })
  }

  build() {
    Column() {
      // 顶部标题栏
      RelativeContainer() {
        Image($r('app.media.icon_back'))
          .width(22)
          .height(22)
          .alignRules({
            left: { anchor: '__container__', align: HorizontalAlign.Start },
            center: { anchor: '__container__', align: VerticalAlign.Center }
          })
          .margin({ left: 16 })
          .onClick(() => {
            router.back()
          })

        Text(this.pageTitle)
          .fontColor($r('app.color.color_FF333333'))
          .fontSize(17)
          .fontWeight(FontWeight.Bold)
          .alignRules({
            center: { anchor: '__container__', align: VerticalAlign.Center },
            middle: { anchor: '__container__', align: HorizontalAlign.Center }
          })
      }
      .width('100%')
      .height(44)
      .backgroundColor(Color.White)

      // 提示文字
      Text(this.tipText)
        .width('100%')
        .padding({ left: 16, right: 16, top: 16, bottom: 16 })
        .fontColor('#7F7F7F')
        .fontSize(11)
        .textAlign(TextAlign.Center)
        .backgroundColor($r('app.color.color_F4F4F6'))

      // 错误提示（如果有的话）
      if (this.updateErrorMessage !== "") {
        Row() {
          Text(`⚠️ ${this.updateErrorMessage}`)
            .fontColor('#FF6B6B')
            .fontSize(12)
            .layoutWeight(1)
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 8, bottom: 8 })
        .backgroundColor('#FFF5F5')
        .border({ width: 1, color: '#FFE6E6' })
      }
      //接收消息对应子视图
      if (!this.isDisturb && this.messageConfig) {
        Row() {
          Text(this.messageConfig.name)
            .fontColor($r('app.color.color_FF333333'))
            .fontSize(15)
            .fontWeight(FontWeight.Bold)
            .layoutWeight(1)

          if (this.isUpdating) {
            LoadingProgress()
              .width(20)
              .height(20)
              .color('#4285F4')
          } else if (this.showMainSwitch){  // 主设置项（系统通知页中的总开关，也就是系统级别的开关控制）
            Toggle({ type: ToggleType.Switch, isOn: this.mainSwitchEnabled })
              .width(44)
              .height(24)
              .switchPointColor(Color.White)
              .selectedColor('#4285F4')
              .onChange((isOn: boolean) => {
                this.onMainSwitchChange(isOn)
              })
              .enabled(!this.isUpdating)
          }
        }
        .width('100%')
        .padding(16)
        .backgroundColor(Color.White)
        .borderRadius(12)
        .margin({ left: 16, right: 16, top: 16 })
      }else if (this.isDisturb && this.messageConfig) {
        Row() {
          Text(this.messageConfig.name)
            .fontColor($r('app.color.color_FF333333'))
            .fontSize(15)
            .fontWeight(FontWeight.Bold)
            .layoutWeight(1)
        }
        .width('100%')
        .padding(16)
        .backgroundColor(Color.White)
        .borderRadius(12)
        .margin({ left: 16, right: 16, top: 16 })
      }

      // 二级设置项列表
      if (this.messageConfig && this.messageConfig.childList.length > 0) {
        List() {
          ForEach(this.messageConfig.childList, (child: Child, index: number) => {
            ListItem() {
              this.SecondLevelItemBuilder(child, index)
            }
          })
        }
        .listDirection(Axis.Vertical)
        .scrollBar(BarState.Auto)
        .backgroundColor($r('app.color.color_F4F4F6'))
        .layoutWeight(1)
        .padding({ left: 16, right: 16, bottom: 16 })
        .edgeEffect(EdgeEffect.Spring)
      } else {
        // 无子项时显示空状态
        Column() {
          Text("暂无子设置项")
            .fontColor('#999999')
            .fontSize(16)
        }
        .width('100%')
        .justifyContent(FlexAlign.Center)
        .alignItems(HorizontalAlign.Center)
        .backgroundColor(Color.White)
        .margin({ left: 16, right: 16, top: 16 })
        .borderRadius(12)
        .padding(60)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor($r('app.color.color_F4F4F6'))
  }
} 
```

