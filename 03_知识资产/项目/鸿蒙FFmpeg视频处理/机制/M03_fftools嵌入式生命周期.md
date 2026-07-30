# M03 · fftools 嵌入式生命周期

## 运行模型转换

```text
桌面：main → fftools → exit → 独立进程销毁
App：exe_ffmpeg_cmd → fftools → return → 宿主继续运行
```

## 退出控制

入口 `setjmp` 保存返回点；深层 `exit_program` 使用 `longjmp` 回入口。回到入口后先保存返回码，再清理 fftools 全局状态。

## 重复执行

独立进程结束会自然清理全局状态；App 内连续调用不会，因此每次命令必须显式 reset。

## 并发

`__thread` 隔离跳转缓冲区，不隔离 fftools 的全部全局状态。调度层仍串行执行。

## 相关

- [[../阶段/04_fftools结束宿主进程问题]]
- [[../知识点/K03_setjmp与longjmp]]
- [[../知识点/K04_返回码与状态重置顺序]]
- [[../知识点/K05_线程局部状态不等于并发安全]]
