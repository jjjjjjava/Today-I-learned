# 04 · fftools 结束宿主进程问题

## 触发

桌面 fftools 运行在独立进程，调用 `exit(ret)` 合理；嵌入 App 的 `.so` 后，`exit()` 会结束整个宿主进程。

## 根因

命令行程序假设与嵌入式运行环境冲突：fftools 想结束进程，App 只希望结束本次命令。

## 方案

```text
exe_ffmpeg_cmd入口setjmp
→ 深层exit_program
→ longjmp回入口
→ 保存返回码
→ reset_ffmpeg_state
→ return给C++桥
```

不能简单逐处改 `return`：退出点分布在深层调用链，侵入上游且容易遗漏。

`__thread` 只隔离跳转现场；fftools 的全局状态仍要求上层串行执行。

## 自检

1. 为什么 `exit()` 会杀掉 App？
2. `setjmp/longjmp` 怎样重建退出边界？
3. 为什么先保存返回码再重置状态？
4. TLS 为什么不代表可以并发？

## 相关

- [[../机制/M03_fftools嵌入式生命周期]]
- [[05_ArkTS与Native双向通信]]
