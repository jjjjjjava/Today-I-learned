https://blog.csdn.net/u013488266/article/details/135640677

### 一、属性兼容性分析

| **属性**        | **布局阶段** | **功能定位**                 | **优先级** |
| --------------- | ------------ | ---------------------------- | ---------- |
| `.alignRules()` | 基础定位阶段 | 确定组件相对于锚点的基准位置 | 高优先级   |
| `.margin()`     | 微调阶段     | 在基准位置基础上添加偏移量   | 低优先级   |

```
import { router } from '@kit.ArkUI'

@Entry
@Preview
@Component
export struct MessageSettingPage {  //命名为MessageSettingPage，而非NotificationSettingPage，这是为了与安卓开发的命名保持一致
  build() {
    Column() {
      RelativeContainer() { //顶部导航栏
        Image($r('app.media.icon_back'))
          .width($r('app.float.size_22'))
          .height($r('app.float.size_22'))
          .alignRules({
            left: {
              anchor: '__container__',
              align: HorizontalAlign.Start
            },
            center : {
              anchor : '__container__',
              align : VerticalAlign.Center
            }
          })
          .margin({left : $r('app.float.size_16')})
          .onClick(() => {
            router.back()
          });
        Text($r('app.string.message_setting'))
          .width('wrap')
          .height('wrap')
          .fontColor($r('app.color.color_FF333333'))
          .fontSize($r('app.float.size_text_17'))
          .fontWeight(FontWeight.Bold)
          .alignRules({
            center : {
              anchor : '__container__',
              align : VerticalAlign.Center
            },
            middle: {
              anchor: '__container__',
              align: HorizontalAlign.Center
            }
          });
      }
      .width('100%')
      .height($r('app.float.size_44'));

      Row() { //系统通知UI
        RelativeContainer() {
          Text($r('app.string.system_notification'))
            .id('tv_notification_head')
            .width('wrap')
            .height('wrap')
            .fontColor($r('app.color.color_FF333333'))
            .fontSize($r('app.float.size_text_15'))
            .margin({left : $r('app.float.size_15')})

          Text($r('app.string.message_loss_warning'))
            .id('tv_loss_warning')
            .width('wrap')
            .height('wrap')
            .fontColor($r('app.color.color_FFFF1111'))
            .fontSize($r('app.float.size_text_9'))
            .margin({top : $r('app.float.size_5')})
            .alignRules({  // 相对于第一个Text的定位规则
              top: { anchor: 'tv_notification_head', align: VerticalAlign.Bottom },
              left: { anchor: 'tv_notification_head', align: HorizontalAlign.Start }
            })

        }
        .width('40%')
        .height($r('app.float.size_60'))
        .padding({
          top : $r('app.float.size_15'),
          left : $r('app.float.size_15'),
        })
        // .backgroundColor($r('app.color.color_FFFFFFFF'))

        Row() {
          Text($r('app.string.open_system_notification'))
            .width('wrap')
            .height('wrap')
            .fontColor($r('app.color.color_FF333333'))
            .fontSize($r('app.float.size_text_15'))
            .margin({
              left : $r('app.float.size_110'),
              bottom : $r('app.float.size_9'),
            })

          Image($r('app.media.icon_forward'))
            .width($r('app.float.size_14'))
            .height($r('app.float.size_14'))
            .margin({
              bottom : $r('app.float.size_9'),
              right : $r('app.float.size_1'),
            })
        }
        // .backgroundColor($r('app.color.black'))
        .width('60%')
        .height($r('app.float.size_60'))
        // .backgroundColor($r('app.color.color_FFFFFFFF'))
      }
      .alignItems(VerticalAlign.Top)   // 垂直方向顶部对齐
      .width('90%')
      .height('180')
      .backgroundImage($r('app.media.icon_notification_status_diable'))
      .margin({
        top: $r('app.float.size_16'),
        bottom: $r('app.float.size_8')
      });

      Text($r('app.string.open_tips'))
        .fontColor($r('app.color.color_FF7F7F7F'))
        .fontSize($r('app.float.size_text_12'))
        .alignRules({
          middle: {
            anchor: '__container__',
            align: HorizontalAlign.Center
          }
        });
    }
    .size({ width: '100%', height: '100%' })
    .backgroundColor($r('app.color.color_FFF0F0F0'));
  }
}
```

