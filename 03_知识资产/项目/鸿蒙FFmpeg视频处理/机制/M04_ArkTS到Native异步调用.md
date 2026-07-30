# M04 · ArkTS 到 Native 异步调用

```text
import libffmpegutils.so
→ Addon初始化
→ 绑定函数进入exports
→ ArkTS调用包装函数
→ AKI做类型转换
→ PFUNCTION提交非JS线程
→ vector<string>转argc/argv
→ exe_ffmpeg_cmd
```

## 三个边界

- `.d.ts`：编译期类型；
- Addon/`exports`：运行时模块与函数；
- `JSBIND_PFUNCTION`：Promise、参数适配和非 JS 线程执行。

`P` 不等于每次新建线程，只保证长任务不直接占用 JS 线程。

## 相关

- [[../阶段/05_ArkTS与Native双向通信]]
- [[../知识点/K06_Addon-exports与dts]]
- [[../知识点/K07_JSBIND-PFUNCTION异步语义]]
- [[../知识点/K08_vector到argc-argv]]
