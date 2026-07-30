# K08 · vector 到 argc/argv

参数跨两层边界：

```text
ArkTS string[]
→ AKI
→ vector<string>
→ 项目适配
→ char **argv
→ exe_ffmpeg_cmd
```

第一层解决跨语言类型，第二层恢复 fftools 命令模型。必须保证字符串生命周期覆盖命令执行。

## 自检

1. 为什么需要两次转换？
2. `argc/argv` 属于哪层接口？
3. 指针生命周期为什么重要？
