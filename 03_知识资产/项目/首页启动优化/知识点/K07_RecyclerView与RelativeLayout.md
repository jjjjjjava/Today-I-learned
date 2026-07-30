# K07 · RecyclerView 与 RelativeLayout

- Trace中的`RV OnLayout`：RecyclerView布局成本。
- RelativeLayout：相对布局容器，可能因子View依赖产生额外测量。

两者不是同一控件。

本项目`RV OnLayout`高，主要因为多个非首屏Fragment及其RecyclerView被提前创建和布局；不能用“RelativeLayout双重测量”解释全部RecyclerView成本。

检索题：

1. `RV OnLayout`中的RV是什么？
2. RelativeLayout的问题是什么？
3. 本项目RecyclerView成本为什么高？
