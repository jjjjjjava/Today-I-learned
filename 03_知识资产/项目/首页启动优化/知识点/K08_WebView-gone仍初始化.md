# K08 · WebView `gone` 仍初始化

`visibility="gone"`控制布局与绘制，不控制对象是否构造。

静态XML中存在`<WebView>`时，LayoutInflater仍会构造WebView；首次创建可能加载Provider、Chromium、so、class和资源。

因此本项目把WebView移出首页XML，改为进入Web场景时动态创建。

检索题：

1. `gone`阻止什么，不阻止什么？
2. WebView首次构造为什么重？
3. 为什么轻量占位加按需创建更合适？
