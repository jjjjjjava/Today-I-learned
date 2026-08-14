# 02｜fftools 命令结束，为什么整个 App 也退出了？

## 本篇只解决一个问题

fftools 在桌面上正常结束命令，为什么编进鸿蒙 `.so` 后会直接关闭整个 App？

## 同一个 `exit()`，为什么结果不同？

桌面终端会为 `ffmpeg` 启动独立进程：

```text
Shell
→ ffmpeg 独立进程
→ fftools
→ exit(ret)
→ 只结束 ffmpeg 进程
```

项目把 fftools 编入动态库后，它与 ArkTS 页面运行在同一个应用进程：

```text
ArkTS
→ Native .so
→ exe_ffmpeg_cmd
→ fftools
→ exit(ret)
→ 整个 App 进程结束
```

这不是普通业务崩溃，而是运行模型冲突。命令行工具认为“任务结束”等于“进程结束”，宿主应用只希望结束当前命令。

## 为什么不能把所有 `exit_program()` 改成 `return`？

退出点分散在参数解析、输入打开、滤镜初始化、编码和封装等深层调用中。

某个深层函数执行 `return`，只能返回上一层，不能直接回到 `exe_ffmpeg_cmd()`。若逐层修改返回值和错误传递，需要侵入大量上游代码，也容易漏掉分支。

更稳定的改动位置是统一的 `exit_program()`，让所有正常结束和异常退出都回到同一个命令入口。

## `setjmp` 怎样记录返回点？

项目把桌面 `main()` 改造成可调用函数，并在入口记录跳转点：

```c
int exe_ffmpeg_cmd(int argc, char **argv, Callbacks *callbacks)
{
    int jumped = setjmp(exit_point);

    if (jumped == 0) {
        run_ffmpeg(argc, argv, callbacks);
    }

    return command_result;
}
```

第一次执行 `setjmp()` 时返回 0，继续进入 fftools。深层发生退出后，控制流重新回到这里，并从非零分支继续返回。

## `longjmp` 怎样替代进程退出？

统一退出函数不再调用系统 `exit()`：

```c
void exit_program(int ret)
{
    command_result = ret;
    longjmp(exit_point, 1);
}
```

于是完整链路变成：

```text
fftools 正常完成或发生错误
→ exit_program(ret)
→ 保存命令返回码
→ longjmp 回到 exe_ffmpeg_cmd
→ return ret
→ App 继续运行
```

“优雅退出”不是取消错误，而是把“终止宿主进程”改造成“结束当前 Native 命令并返回状态”。

## 为什么任务队列只能同时执行一条命令？

fftools 底层不支持项目需要的多命令并发模型，因此上层使用单任务队列：

```text
任务 A 入队并同步执行
→ A 返回成功或失败
→ 任务 B 才开始执行
```

队列保证任意时刻只有一条 fftools 命令进入 Native 执行区，上一条命令返回后才会执行下一条。

## 返回码怎样到达业务层？

C++ 桥接层读取 `exe_ffmpeg_cmd()` 的返回值：

```cpp
int ret = exe_ffmpeg_cmd(argc, argv, &callbacks);

if (ret == 0) {
    on_success();
} else {
    on_failed(ret);
}
```

进度在命令执行期间持续回传；最终成功或失败，则由命令返回码决定。

## 三个典型判断

1. `exit(0)`：在命令行中表示正常结束，嵌入 App 后仍会结束宿主进程。
2. 深层函数改成 `return`：只能退出当前函数，不能自动回到统一 Native 入口。
3. 使用 `longjmp`：改变的是命令退出边界，不会把多任务执行变成并发安全。

## 常见误区

1. 把 App 被关闭描述成普通 JavaScript 异常。
2. 认为只有非零 `exit()` 才会结束进程。
3. 逐处替换 `return`，却没有统一错误返回路径。
4. 捕获 `exit()` 后不把原返回码交给上层。
5. 底层只能单任务执行，却让多个页面同时进入 fftools。

## 本篇自测

1. 为什么同一个 `exit()` 在桌面与 App 内的影响不同？
2. 普通 `return` 为什么不能替代深层统一退出？
3. `setjmp()` 第一次和被跳回时分别返回什么？
4. `longjmp()` 怎样让宿主进程继续存活？
5. 单任务队列约束的是什么？

## 一句话总结

fftools 从独立进程搬进 App 后，必须把进程级 `exit()` 改造成一次命令的返回，并由单任务队列串行进入 Native 执行区。
