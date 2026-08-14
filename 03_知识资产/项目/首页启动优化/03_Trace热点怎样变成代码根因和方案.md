# 03｜这些 Trace 热点为什么会出现？

## 本篇只解决一个问题

Perfetto 已经显示 inflate、`RV OnLayout`、traversal 和 WebView 很贵。哪段代码制造了这些工作，应该先改什么？

## 为什么热点还不是根因？

优化前代表 Trace 显示：

```text
inflate：106 次，Wall 700.8ms
RV OnLayout：29 次，Wall 518.3ms
traversal：Wall 750.1ms
WebView：2 次，Wall 229.9ms
binder transaction：579 次，Wall/Self 226.3ms
```

这些数字说明启动期间工作很多，却没有指出哪个页面配置或哪段业务代码负责。

热点要成为根因，需要与三个事实对齐：它发生在项目区间内；调用关系能回到具体业务代码；出现次数能被页面结构解释。

## ViewPager2 为什么同时推高三个热点？

源码中存在类似逻辑：

```kotlin
for (index in 0..4) {
    initTab(index)
}

mContainer?.offscreenPageLimit = mListFragments.size
```

`offscreenPageLimit` 被设为全部 Fragment 数量，非首屏页面也在冷启动阶段提前创建。

每个 Fragment 又可能创建 XML、RecyclerView、Adapter 和首批 item，于是形成：

```text
多个 Fragment 提前创建
→ inflate Count 上升
→ 多个 RecyclerView 提前布局
→ RV OnLayout Count 和 Wall 上升
→ View 树变宽
→ traversal 总成本上升
```

这一条源码配置同时解释了 inflate、RecyclerView layout 和 traversal，因果链比“首页 View 很多”更完整。

## `gone` 的 WebView 为什么仍然进入启动路径？

首页 XML 静态声明 WebView：

```xml
<WebView
    android:id="@+id/web"
    android:visibility="gone" />
```

`gone` 只跳过后续布局和绘制，不阻止 LayoutInflater 创建对象。

解析 `<WebView>` 时仍会执行构造。首次创建还可能触发 Chromium、Provider、类、so 和资源初始化，因此约 230ms 的 WebView 工作进入了项目区间。

如果首页首屏并不需要 Web 内容，这段工作应该延迟到真正进入对应入口时。

## 首页模块一次加入，会发生什么？

权限数据返回后，代码一次性向容器添加 AI 助手、常用模块、待办、课程和资讯等多个复杂 View。

部分模块内部还有 RecyclerView。即使屏幕只能显示顶部区域，其他模块的对象创建和部分布局也已经发生。

它继续放大 inflate、RecyclerView layout 和 traversal。但这部分涉及页面展现节奏，回归范围比前两个根因更大，因此不作为第一批修改。

## RelativeLayout 要不要全部换掉？

深层嵌套和复杂相对约束确实可能增加 measure/layout 成本，但 XML 中出现 RelativeLayout 不能直接证明它是热点。

应先定位目标布局是否位于热点调用链，再比较层级、测量次数和修改后的 Trace。否则只是批量换控件，未必缩短启动关键路径。

`RV OnLayout` 中的 RV 指 RecyclerView，不是 RelativeLayout。两者不能混为一个问题。

## Binder 579 次为什么不是本轮 P0？

Binder 调用可能来自生命周期、PackageManager、Window 和输入通道建立，也可能来自 SDK、Provider 或服务绑定。

579 次只说明跨进程调用频繁，没有形成单一业务根因。除非继续聚合到具体接口和调用方，否则治理范围大、收益不确定。

相比之下，ViewPager2 和 WebView 已被 Trace 与源码共同证明，适合优先修改。

## 最终先做哪两个方案？

### P0：恢复 ViewPager2 懒加载

移除“缓存全部 Fragment”的配置，让首页只创建当前页和框架真正需要的相邻页面。

预期变化是非首屏 Fragment 不再提前创建，inflate、`RV OnLayout` 和 traversal 同时下降。

### P0：WebView 按需创建

从首页静态 XML 移除 WebView，先保留轻量容器。用户真正进入 Web 功能时再创建并挂载 WebView。

预期变化是首页项目区间内不再出现 WebView 初始化 Slice。

### P1：首页模块渐进构建

首屏只创建可见且必要的模块，剩余模块在首帧之后或滚动接近时创建。

它可能继续降低 inflate 和 traversal，但会改变页面加载节奏，因此需要更完整的占位、状态和交互设计。

### P2：Provider、DAG 和 Baseline Profile

本项目 `bindApplication` 约 220ms，不是第一轮最大热点。这些方向保留为候选，不计入当前已验证收益。

DAG 只是初步设计，Baseline Profile 也没有完成有无 Profile 的对照实验。详细边界见 [[附录B_机制与候选方案边界]]。

## 三个典型判断

1. WebView 设置为 `gone`：对象仍会创建，不能消除首次初始化成本。
2. Binder Count 很高：先按接口和调用方细分，不能直接把 Binder 当作单一根因。
3. DAG 设计已经完成：没有 Benchmark、Trace 和线上结果，仍不能计入项目收益。

## 常见误区

1. 看到 `doFrame` 高，就优化 Choreographer。
2. 把 `RV OnLayout` 当成 RelativeLayout。
3. 认为 WebView 设置 `gone` 就不会创建。
4. 看到 Binder Count 高，就要求把所有 Binder 清零。
5. 没有证据就把 RelativeLayout 全部替换。
6. 把 DAG、Provider 或 Baseline Profile 写成已落地成果。
7. 把任务移到后台，但首屏仍同步等待结果。

## 本篇自测

1. ViewPager2 全量预加载为什么能同时解释三个 Trace 热点？
2. WebView 为 `gone` 时为什么仍会污染启动？
3. `RV OnLayout` 与 RelativeLayout 分别代表什么？
4. Binder 579 次为什么没有直接成为 P0？
5. 哪些方案已经落地，哪些只是候选？

## 一句话总结

Trace 负责暴露工作量，源码负责解释工作量；优先修改能同时解释热点、收益明确且回归面可控的路径。
