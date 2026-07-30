# M05 · Native 到 ArkTS 回调

## 回调链

```text
ArkTS按UUID注册JS函数
→ C++取得JSFunction句柄
→ C函数指针表传入fftools
→ fftools上报进度
→ C++桥接函数
→ thread_local当前任务上下文
→ AKI Invoke
→ JS线程执行回调
```

## 三种身份

| 对象 | 作用 |
|---|---|
| UUID | 在 JS 函数表区分任务 |
| `g_callbacks` | C 层持有桥接函数地址 |
| `g_currentCallback` | C++ 层找到当前任务 JS 句柄 |

Native 线程调用 `Invoke` 时需要跨线程调度，回调过重会反向拖慢 FFmpeg 工作线程。

## 相关

- [[../阶段/05_ArkTS与Native双向通信]]
- [[../知识点/K09_UUID与双层回调上下文]]
- [[../知识点/K10_Invoke跨线程阻塞语义]]
