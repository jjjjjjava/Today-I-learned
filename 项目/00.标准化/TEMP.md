[toc]

## 01.功能概述

- **功能ID**：`  refactor-20250619-001`  

- **功能名称**：弹窗管理系统

- **目标版本**：v0.2.0

- **提交人**：@panruiqi  

- **状态**：

  - [x] ⌛ 设计中 /
  - [ ] ⌛ 开发中 / 
  - [ ] ✅ 已完成 / 
  - [ ] ❌ 已取消  

- **价值评估**：  

  - [x] ⭐⭐⭐⭐⭐ 核心业务功能  
  - [ ] ⭐⭐⭐⭐ 用户体验优化  
  - [ ] ⭐⭐⭐ 辅助功能增强  
  - [ ] ⭐⭐ 技术债务清理  

- **功能描述** 

  - POS机系统内部包含Toast，提示，dialog三种类型的弹窗，我们缺乏统一的管理，使用起来混乱不堪

    - 其中Toast包括：呼叫成功，加购物商品，也就是toast_add_product_error，toast_add_product_success，toast_callforhelp_failed，toast_callforhelp_success

    - dialog包括：dialog_cancel_deal_confirm, dialog_clear_cart_confirm, dialog_delete_product_confirm,

    - 还有提示，也就是复用toast_add_product_error.xml这种的

    - ```
      LogManager.e("价格计算失败: $it")
      showAddProductErrorPopup("价格计算失败: $it")
      ```

  - 现在有如下要求：

    - 管理Main和Payment页面的弹窗。
    - Dialog出来时要求这个Dialog外整个屏幕要有遮罩效果，同时其他位置不可以点击
    - Toast可以被同类别的Toast抢占，也就是呼叫成功，加购物商品
    - 提示优先级比较低，弱于上面两个
    - Dialog优先级最高，在他显示期间，除了和他交互，没法做任何其他处理。
    - 优化

## 02.需求分析

### 2.1 用户场景

- **主要场景**：  
  - 弹窗分为：提示，Toast，Dialog
  - 
  - 
- **边界场景**：  

### 2.2 功能范围

- ✅ 包含：
- ❌ 不包含：



## 03.技术方案

### 3.1 方案一

- 实现思路：
  - 我设置一个PausableCountDownTimer定时器，onTick的时候设置文字。onCreate时启动它。
  - 去覆写BaseScannerActivity中的onKeyDown方法，每次出发，就reset定时器。
  - 去复写onTouchEvents方法，每次触发，就reset定时器。

### 3.2 方案二

- 实现思路：



## 04.实现规划

### 4.1 技术选型

### 4.2 任务拆解

| 模块   | 任务         | 预估工时 | 负责人 |
| :----- | :----------- | :------- | :----- |
| UI层   | 布局文件编写 | 2h       | @A     |
| 逻辑层 | 业务逻辑实现 | 4h       | @B     |
| 数据层 | 本地存储实现 | 3h       | @C     |

### 4.3 代码路径

- **新增文件**：
  `app/src/main/java/.../NewFeature.kt`
- **修改文件**：
  `ExistingClass.kt`（方法扩展）
- **资源文件**：
  `res/layout/new_feature.xml`

## 05.兼容性设计

### 5.1 设备适配

- **屏幕尺寸**：小屏设备折叠布局方案
- **系统版本**：

### 5.2 冲突检查

| 现有功能 | 冲突风险     | 解决方案 |
| :------- | :----------- | :------- |
| 功能A    | 接口参数变更 | 版本隔离 |

## 06.测试方案

### 6.1 核心用例

### 6.2 性能指标

| 指标       | 预期值 | 实测值 |
| :--------- | :----- | :----- |
| 内存增量   | <1MB   | -      |
| 渲染帧率   | >55fps | -      |
| 冷启动延迟 | <100ms | -      |

## 07.发布计划

### 7.1 阶段发布

| 阶段  | 范围     | 验证重点 |
| :---- | :------- | :------- |
| Alpha | 内部测试 | 核心流程 |
| Beta  | 5%用户   | 崩溃率   |
| GA    | 全量用户 | 性能指标 |

### 7.2 回滚方案

- 热修复开关：
- 动态配置：





## 08.文档记录

### 8.1 技术文档

- [架构设计文档](https://xn--gzu811i/)
- [接口API文档](https://xn--gzu811i/)

### 8.2 用户文档

- 功能引导页设计
- 错误代码对照表

### 8.3 监控埋点

```
// analytics_events.json
{
  "new_feature_used": {
    "params": ["screen_size", "os_version"]
  }
}
```

