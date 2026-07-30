# 05 · ArkTS 与 Native 双向通信

## 去程

```text
ArkTS import
→ Native Addon初始化exports
→ JSBIND_PFUNCTION
→ AKI转换参数并提交非JS线程
→ vector<string>
→ argc/argv
→ exe_ffmpeg_cmd
```

`.d.ts` 只提供编译期类型；Addon 初始化与 `exports` 才提供运行时函数。

## 回程

```text
ArkTS按UUID注册回调
→ C++取得JSFunction
→ C函数指针交给fftools
→ C++桥接
→ AKI Invoke调度JS线程
```

`g_callbacks` 保存 C++ 桥函数地址；`g_currentCallback` 保存当前任务的 JS 函数上下文。二者职责不同。

AKI 从 Native 线程调用 JS 时会调度 JS 线程，并可能让 Native 调用线程等待，因此回调必须轻量。

## 并发边界

UUID、`thread_local` 与 TLS 解决身份和现场隔离，不解决 fftools 全局状态并发安全；任务调度器工作线程数保持 `1`。

## 自检

1. Addon、exports、`.d.ts` 如何分工？
2. 为什么 `JSBIND_PFUNCTION` 不阻塞 JS 线程？
3. UUID、`g_callbacks`、`g_currentCallback` 各解决什么？
4. 为什么仍要串行？

## 相关

- [[../机制/M04_ArkTS到Native异步调用]]
- [[../机制/M05_Native到ArkTS回调]]
