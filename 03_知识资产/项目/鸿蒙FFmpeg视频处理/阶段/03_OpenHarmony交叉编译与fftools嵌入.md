# 03 · OpenHarmony 交叉编译与 fftools 嵌入

## 目标

把桌面 `ffmpeg main(argc, argv)` 变成鸿蒙 App 可调用的 `.so` 函数。

```text
适配源码
→ Lycium/HPKBUILD组织构建
→ OpenHarmony SDK/NDK工具链交叉编译
→ 聚合libav*与fftools
→ 单一.so
→ exe_ffmpeg_cmd(argc, argv)
```

Lycium 是构建组织框架，不是编译器；LLVM、Clang、链接器负责实际编译。

## 三类改造

1. 打开 RTSP、封装、滤镜、编解码所需配置；
2. 把进程入口 `main` 改为函数入口 `exe_ffmpeg_cmd`；
3. 把退出码、日志与进度改造成 App 可接收的返回与回调。

## 自检

1. Lycium、HPKBUILD、SDK/NDK各自负责什么？
2. 为什么需要单一聚合 `.so`？
3. 从 `main` 到函数入口改变了什么运行模型？

## 相关

- [[../机制/M02_OpenHarmony交叉编译与单so产物]]
- [[04_fftools结束宿主进程问题]]
