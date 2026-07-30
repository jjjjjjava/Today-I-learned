# K10 · `openDexFileNative`成本

ARouter只想找少量生成类，但默认路径必须：

```text
找到所有Dex
→ 逐个打开
→ 枚举全部类名
→ 再做包名与生成类前缀筛选
```

真正昂贵的是打开Dex和遍历大量类名，不是`startsWith()`字符串判断。

检索题：

1. `openDexFileNative`为什么出现在ARouter链路？
2. 默认扫描为何随项目体量放大？
3. 真正昂贵的是哪部分？
