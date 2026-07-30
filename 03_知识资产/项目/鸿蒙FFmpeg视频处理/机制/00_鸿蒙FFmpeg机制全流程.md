# 鸿蒙 FFmpeg · 机制全流程

```text
ArkTS命令数组
→ Native Addon exports
→ AKI异步参数转换
→ vector<string>
→ argc/argv
→ exe_ffmpeg_cmd
→ fftools编排libav*
→ OpenHarmony硬件编码
→ 返回码 / C函数指针
→ C++桥接
→ AKI调度ArkTS回调
```

## 六段机制

1. [[M01_FFmpeg媒体处理与fftools编排]]
2. [[M02_OpenHarmony交叉编译与单so产物]]
3. [[M03_fftools嵌入式生命周期]]
4. [[M04_ArkTS到Native异步调用]]
5. [[M05_Native到ArkTS回调]]
6. [[M06_硬件编码与码率参数链]]

## 外部前置

- [[../../../Android/音视频/01. 音视频_音视频基础_01.音视频基础]]
- [[../../../Android/音视频/01. 音视频_音视频基础_02.重封装和解码]]

## 综合自检

1. ArkTS 函数怎样落到 fftools？
2. fftools 的命令行生命周期如何变成 App 内函数生命周期？
3. 进度和结果怎样反向回到 ArkTS？
4. 编码参数怎样进入系统硬件编码器？
