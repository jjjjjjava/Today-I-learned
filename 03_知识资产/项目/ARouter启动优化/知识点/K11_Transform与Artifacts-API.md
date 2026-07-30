# K11 · Transform与Artifacts API

旧`arouter-register`依赖AGP旧Transform接入。AGP 8移除旧方式后，插件不能继续按原路径处理Class产物。

兼容插件改用Artifacts API取得当前variant的Class/Jar产物，再执行扫描与改写。

边界：使用Artifacts API只说明有能力接入新构建链；仍需证明目标variant真正执行、扫描完整、产物被改写。

检索题：

1. 第一轮构建变化是什么？
2. Artifacts API提供什么能力？
3. 为什么接入新API不等于插件已经生效？
