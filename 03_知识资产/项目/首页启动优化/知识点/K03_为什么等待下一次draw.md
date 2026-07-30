# K03 · 为什么等待下一次 draw

接口返回、View构造、`addView`都不等于用户已经看到像素。

```text
addView
→ ViewRootImpl
→ requestLayout
→ 等待VSYNC
→ performTraversals
→ measure/layout/draw
→ 提交渲染
```

本项目在首页模块加入View树并经历下一次draw后打marker，避免漏算等待VSYNC和完整traversal。

检索题：

1. `addView`后还缺什么？
2. 立即打marker会漏算哪段？
3. 等draw能否证明页面已经完全可交互？
