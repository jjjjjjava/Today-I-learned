# 鸿蒙 FFmpeg 三方库（ffmpeg_tools）· 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 学习深度：标准
> 文档数量因人而异，但掌握内容不打折扣。
> 课题定位：讲清楚 `ffmpeg_tools` 这个鸿蒙三方库解决的工程核心问题，只到 fftools 使用层面，不深入 FFmpeg 底层源码。
> 全局原理：本质是借助 **fftools（FFmpeg 命令行工具层）连接底层 libav* 库**，像 cmd 调 ffmpeg 一样拼命令交给它执行。

## 主线（三篇）

完成本课题后，你将能够：

### 第一篇（01）：进程被 exit 退出宿主的问题（核心）
- [x] 能说出根因：fftools 内部以 `exit()` 结束，作为库嵌入时会**杀掉整个宿主 App 进程**
- [x] 能解释 `setjmp` / `longjmp` 如何把「退出进程」改成「退出本次命令、返回调用方」
- [x] 能说清「优雅退出」=不退进程、把返回码 return 给调用者，调用者据此回调 `onSuccess`/`onFailed`
- [x] 能说明跳转后为什么必须 `reset_ffmpeg_state`，以及 `ex_buf__` 为何要线程局部（`__thread`）

### 第二篇（02）：我们如何调用到 native 的 fftools，fftools 又如何回调我们
- [x] **问题一（去程）**：能讲清 AKI 宏注册 + ArkTS 调用 + `JSBIND_PFUNCTION` 开 worker 线程（参数经方舟编译器转 native、立即返回 Promise 不阻塞 UI）→ 转 argv → `exe_ffmpeg_cmd`
- [x] **问题二（回程）**：能讲透两跳透传（`napi_ref` 强引用寄存 / `Callbacks` C 函数指针 / `g_callbacks` 与 `g_currentCallback` 两个全局）、C 带不了上下文靠 `g_currentCallback` 暗接头、`Invoke` 跨线程投递回主线程消息循环
- [x] 能说明结束时按返回码回调 `onSuccess`/`onFailed`；uuid + 线程局部做回调隔离，但 fftools 因全局变量须上层串行

### 第三篇（03）：后续优化
- [x] 鸿蒙下 FFmpeg 如何启用硬件加速（`h264_ohosavcodec` + 支持硬解的 `.so` + 零拷贝何时根本不需要硬件）
- [x] 码率设置为何失效（真实根因：OHOS 版 FFmpeg 的 `ohosvideoencoder.cpp::SetCodecFormat()` 漏写 `bit_rate`，硬件编码器配置丢掉了 `-b:v`；解法是改 native 源码补 `OH_MD_KEY_BITRATE` 并重编 `.so`，已向 OpenHarmony 提 Issue/MR）

## 收尾交付
- [ ] 把以上内容整理成仓库可收录的文档

## 不在本课题范围内

- FFmpeg 底层源码 / libav* C 级 API 编写、编解码算法
- ffmpeg_tools 的基础用法 API 清单（executeFFmpegCommand / Factory / Builder 怎么调）
- 录像下载、缩放、裁剪、拼接等具体命令清单
- 鸿蒙 .so 交叉编译与 CMake 构建细节

## 学习进度

> 2026-06-30 重构为三篇：原 02（双向通信）与 03（透传原理）合并为新 02，回答「如何调用 + 如何回调」两个问题；原 04（优化）顺延为 03。

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
| 01.md | 第一篇全部（exit 杀进程根因、setjmp/longjmp、优雅退出=返回码、reset 与线程局部）✅ | 2026-06-29 |
| 02.md | 第二篇全部（去程：AKI 注册/PFUNCTION worker 线程；回程：两跳透传/g_currentCallback 暗接头/跨线程投递/onSuccess·onFailed）✅ | 2026-06-30 |
| 03.md | 第三篇全部（鸿蒙硬件加速 h264_ohosavcodec；码率失效真实根因 ohosvideoencoder.cpp 漏写 bit_rate）✅ | 2026-06-29 |
