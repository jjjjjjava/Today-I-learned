# 03｜ArkTS 怎样执行 FFmpeg，又怎样收到进度？

## 本篇只解决一个问题

ArkTS 页面怎样把一组 FFmpeg 参数交给 Native 长任务，并在执行过程中收到进度、成功和失败？

## 一次调用包含哪两个方向？

```text
去程：ArkTS 命令数组
→ AKI / NAPI
→ C++ 函数
→ argc / argv
→ fftools

回程：fftools
→ C 函数指针
→ C++ 桥接
→ AKI
→ ArkTS 回调
```

去程解决参数和线程切换，回程解决 C、C++ 与 ArkTS 三层之间的回调传递。

## 为什么普通 `.so` 不能直接被 ArkTS 调用？

动态库中存在 C++ 函数，不代表 ArkTS 模块系统知道如何初始化它、导出什么名称、怎样转换参数和返回值。

项目通过 NAPI 建立运行时桥梁，并使用 AKI 减少手写绑定代码。

```cpp
JSBIND_ADDON(ffmpegutils)
```

它把动态库注册为 Native Addon。ArkTS 导入 `libffmpegutils.so` 时，运行时执行 Addon 初始化，并得到模块的 `exports`。

`.d.ts` 只向 ArkTS 编译器声明函数名、参数和返回类型。真正让函数在运行时存在的是 Addon 初始化和 `exports`。

## `JSBIND_PFUNCTION` 做了什么？

```cpp
JSBIND_GLOBAL() {
    JSBIND_PFUNCTION(executeFFmpegCommandAPP);
}
```

它为 C++ 函数生成 ArkTS 包装，包括函数导出、参数转换、Promise 创建、Native 任务执行和结果转换。

`P` 表示 Promise 异步函数。ArkTS 调用后先得到 Promise，FFmpeg 长任务在非 JS 线程执行，不会直接占用页面的 JS 线程。

它不表示每次创建一条新线程。项目仍通过单任务队列保证只有一条 FFmpeg 命令实际执行。

## ArkTS 数组怎样变成 `argc / argv`？

ArkTS 发起调用：

```typescript
libAddon.executeFFmpegCommandAPP(cmds.length, cmds)
```

AKI 先根据 C++ 签名完成第一层转换：

```text
ArkTS number   → int cmdLen
ArkTS string[] → std::vector<std::string> args
```

C++ 再完成第二层转换：

```text
std::vector<std::string>
→ char **argv
→ exe_ffmpeg_cmd(argc, argv)
```

第一层跨越 ArkTS 与 C++，第二层把 C++ 友好容器还原为 fftools 的命令行参数模型。

## ArkTS 回调为什么不能直接变成 C 函数地址？

ArkTS 函数是 JS 虚拟机管理的对象，不是稳定的 C 函数指针。Native 需要先通过 AKI 获得可调用的 JSFunction 句柄。

C++ 为当前队列任务保存进度、成功和失败三个函数句柄。由于任务按队列顺序执行，回调只需对应当前任务。

但 fftools 主要是 C 代码，不认识 AKI 的 JSFunction，因此中间还需要一层纯 C 回调协议：

```c
typedef struct Callbacks {
    void (*onFFmpegProgress)(int progress);
    void (*onFFmpegFail)(int code, const char *message);
    void (*onFFmpegSuccess)(void);
} Callbacks;
```

C++ 把签名兼容的桥接函数放入该结构，再传给 `exe_ffmpeg_cmd()`。

## fftools 怎样上报进度？

fftools 根据已处理时间戳和总时长计算百分比，然后调用 C 函数指针：

```c
int progress = pts * 100 / total_duration;

if (callbacks && callbacks->onFFmpegProgress) {
    callbacks->onFFmpegProgress(progress);
}
```

站在 fftools 视角，它只执行普通 C 函数。C++ 桥接函数再找到当前任务的 JSFunction，并调用：

```cpp
jsProgressFunction->Invoke<void>(progress);
```

AKI 把 JS 函数执行调度回 JS 线程。Native 调用线程可能等待这次 JS 调用完成，因此回调只更新必要状态，不能执行重计算或同步 IO。

## 成功和失败为什么不走进度链？

进度发生在命令执行过程中，由 fftools 主动上报。

最终结果发生在 `exe_ffmpeg_cmd()` 返回以后，由 C++ 根据返回码决定：

```cpp
int ret = exe_ffmpeg_cmd(argc, argv, &callbacks);

if (ret == 0) {
    successFunction->Invoke<void>();
} else {
    failFunction->Invoke<void>(ret, errorMessage);
}
```

```text
执行期间：fftools → C 回调 → C++ → ArkTS progress
执行结束：return code → C++ → ArkTS success / failed
```

## 完整双向链路

```text
ArkTS 导入 Native Addon
→ 调用 Promise 函数并提交命令数组
→ AKI 转换为 C++ 参数
→ C++ 转成 argc / argv
→ 单任务队列执行 exe_ffmpeg_cmd
→ fftools 驱动 libav*
→ C 函数指针上报进度
→ C++ 桥接调用 AKI JSFunction
→ JS 线程更新页面状态
→ 命令返回后回调成功或失败
```

## 三个典型判断

1. `.d.ts` 中有函数声明：只能证明编译期类型存在，不能证明 Native 运行时已经导出。
2. 使用 `JSBIND_PFUNCTION`：长任务不直接运行在 JS 线程，但仍受单任务队列约束。
3. 进度回调能执行：不代表可以在回调中进行耗时文件操作。

## 常见误区

1. 把 `.d.ts` 当成 Native 模块注册代码。
2. 认为 Promise 函数的主体仍在 JS 线程执行。
3. 把 `std::vector<std::string>` 直接当作 fftools 的 `argv`。
4. 让 C 代码直接持有 ArkTS 函数对象。
5. 在进度回调中执行重计算，反向拖慢 Native 任务。
6. 底层只允许单任务，却从多个入口同时提交执行。

## 本篇自测

1. `.d.ts`、Addon 和 `exports` 分别解决什么？
2. `JSBIND_PFUNCTION` 怎样避免 FFmpeg 占用 JS 线程？
3. ArkTS 命令数组经过哪两层转换？
4. 为什么 fftools 与 ArkTS 回调之间需要 C++ 桥接？
5. 进度与最终成功、失败为什么来自不同位置？

## 一句话总结

AKI 把 ArkTS 命令异步送入单任务 Native 队列，再用 C 函数指针和 C++ 桥把 fftools 的进度与结果送回 JS 线程。
