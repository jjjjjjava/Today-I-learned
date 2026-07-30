# K14 · Java 21与ASM三层修复

Java 21 Class major version为65。旧ASM `ClassReader`读取文件头时不支持该版本，因此在Visitor执行前失败。

修复三层：

1. 完整ASM依赖族升级到9.7；
2. Visitor API调整为ASM9；
3. 确认插件运行时classpath真正解析到新版ASM。

只改API常量，不能让旧ClassReader支持major 65。

检索题：

1. major version 65代表什么？
2. 异常发生在Visitor之前还是之后？
3. 三层修复为什么缺一不可？
