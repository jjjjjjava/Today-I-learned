[toc]

## 01. Android分类

- **Android应用开发工程师**
  - **核心技能**：
    - 语言：Kotlin（Google官方推荐）与Java双核心，2023年Google Play新应用中Kotlin使用率超85%
    - 架构：MVVM+Clean Architecture，Jetpack组件（ViewModel/LiveData/DataBinding）
    - UI体系：Jetpack Compose（2023年主流厂商新项目采用率超60%）与传统XML布局
    - 异步处理：Coroutines+Flow深度应用
    - 性能优化：启动速度（App Startup）、内存管理（LeakCanary）、渲染优化（Profile GPU Rendering）
  - **进阶要求**：
    - 动态化框架：App Bundles、Dynamic Delivery
    - 响应式编程：RxJava向Kotlin Flow迁移策略
    - 安全机制：SSL Pinning、数据加密（Android Keystore System）
- **Android系统开发工程师**
  - **关键技术栈**：
    - AOSP源码编译体系（Soong/Build系统）
    - HAL层开发（HIDL/AIDL）
    - Linux内核定制（Binder驱动/SELinux策略）
    - 系统级性能调优（systrace/perfetto）
  - **典型场景**：
    - ROM定制（OEM厂商需求）
    - 车载系统（Android Automotive OS 13适配）
    - IoT设备系统移植（内存<512MB设备优化）

- **车载Android开发**
  - **特殊要求**：
    - Android Automotive OS API（CarService/CarUXR）
    - 车辆网络协议（CAN总线/SOME/IP）
    - 驾驶安全规范（ASIL等级管控）

## 02.应用开发详细分析

- 广东六鲟科技有限公司
  - 要求
    - 3年及以上Android应用开发经验，熟悉Java，熟练使用Android SDK进行应用的开发与调试; 
    - 熟悉Android系统，熟悉Android软件的开发、测试、分发流程; 
    - 精通Android开发平台及框架原理，以及 Android控件的使用，熟练掌握Android界面和交互开发; 
    - 熟悉Flutter框架为加分项,能维护现有的程序;
  - 分析：
    - 要有Android软件开发经验。
    - 精通Android开发平台及框架原理
      - 熟悉系统架构、核心组件的工作原理，如Activity生命周期、Binder机制、Handler消息循环等。
      - 还需要提到常见的开发框架，如Jetpack组件，以及是否要了解源码。
    -  Android控件的使用：
      - 这部分应该包括内置控件的熟练使用，比如RecyclerView、ViewPager，以及自定义控件的开发能力。可能需要解释如何处理复杂布局和性能优化。
    - “界面和交互开发”可能涉及UI设计的实现能力，比如动画、触摸事件处理，
    - 会Flutter
- 战歌科技：
  - 要求
    - 3年以上android开发经验（实际年龄25岁以上），熟悉安卓系统运行机制及各底层框架并运用到应用中
    - 精通java/kotlin，熟练使用OkHttp、Retrofit、Glide等常用框架
    - 熟悉Jetpack中常用组件，并在项目中有过实际经验
    - 熟悉组件化开发，熟悉MVVM架构
    - 熟练安卓性能优化，app瘦身、启动优化等
    - 有车联类APP开发经验优先
  - 分析
    - 熟悉安卓系统运行机制及各底层框架并运用到应用中：
      - Binder跨进程通信（AIDL接口定义与实现）
      - Handler消息机制（Looper/MessageQueue源码级理解）
      - 四大组件工作原理（如Activity启动流程与Task栈管理）
    - 熟练使用OkHttp、Retrofit、Glide等常用框架
      - 但是
    - Jetpack
    - MVVM
    - Android性能优化。
- 中软国际：
  - 要求：
    - 5年以上Android开发经验，熟悉面向对象设计的基本原则、常用的设计模式及算法 
    - 扎实的编程功底，良好的编程习惯和一定的架构设计能力 
    - 对自定义View，事件分发机制，动画机制， 并发，跨进程通信有较为深入的理解并能灵活运用 
    - 对APP性能优化，业务解耦，APP安全有一定的经验和理解 
    - 有良好的团队合作意识和良好的英文文档阅读能力，对新技术报有学习热情 
    - 有IoT 产品经验者优先，有RN/H5开发经验者优先；有音视频开发经验者优先
  - 分析
    - 算法，设计模式，面向对象。
    - 自定义View，事件分发机制，动画机制， 并发，跨进程通信
    - APP性能优化。
- 斯沃德科技
  - 要求：
    - 统招本科以上学历，1-3年Android开发经验。
    - 具备扎实的Java和kotlin语言基础。
    - 熟悉Android的网络通信机制，对多线程通信、Socket、TCP、UDP、Http有一定的理解和实践。
    - 熟练掌握Android的API，熟悉常见应用实现机制，理解Android的体系结构。
  - 分析：
    - Android网络通信机制，网络通信各个层次。
- 三星电子
  - 要求
    - 熟练掌握 Java/Kotlin 等编程语言和常用的设计模式 (MVC/MVVM 等)； 
    - 熟练掌握数据结构与算法，熟悉 DFS、BFS 等算法；
- 酷麦科技：
  - 要求
    - 能熟悉使用C/C++、java、kotlin 编程语言，有独立分析和解决问题的能力； 
    - 熟悉Android系统体系结构、框架、机制，熟悉Android平台UI设计； 
    - 熟悉网络编程，对网络交互有较深的理解； 
    - 熟悉流媒体开发更佳； 
    - 具有良好的沟通能力、团队合作精神、能承担工作压力。

## 03.我的优点和不足

- 具备的专业技能：
  - 熟悉安卓系统运行机制及各底层框架
    - Binder，Handler，四大组件等
    - 底层框架是指整个的Android启动流程
  - 属性自定义View，事件分发机制，动画机制， 并发，跨进程通信
    - 动画机制是指：Animation
    - 并发还是有所缺少
  - 
- 不足：
  - Jetpack
  - MVVM
  - APP性能优化
  - 并发。
  - OkHttp，Retrofit，RxJava
  - Kotlin的简单问题。
  - Android网络编程

- 目前的关键点，按照顺序：
  - Android网络编程
  - 

## 04.后续规划

- 找工作步骤：
  - 岗位分析（自身的专业技能欠缺和不足）
  - 简历优化（内容充实，丰富经历）
  - 沟通过程优化
    - 常用语
    - 各种情况应对方案
- 期望的最后的专业技能：
  - 熟悉安卓系统运行机制及各底层框架
    - Binder，Handler，四大组件等
    - Android启动流程
  - 熟悉自定义View，事件分发机制，动画机制， 并发，跨进程通信
  - 熟悉APP性能优化（初步搞定）
  - 熟悉Jetpack（初步搞定）
  - 熟悉MVVM（欠缺）
  - 熟悉OkHttp，Retrofit，RxJava。（思路）
  - 熟悉Android网络编程（思路，网络协议层次今天搞定）
  - 动画（思路）





- 算法补全：耗时长
- 专业技能补全，一周时间
- 八股文补全：两天。