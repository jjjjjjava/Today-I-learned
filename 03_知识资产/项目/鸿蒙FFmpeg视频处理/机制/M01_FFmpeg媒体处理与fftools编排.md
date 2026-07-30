# M01 · FFmpeg 媒体处理与 fftools 编排

## 分层

| 层 | 职责 |
|---|---|
| `libavformat` | 协议、解复用、封装 |
| `libavcodec` | 编解码 |
| `libavfilter` | `overlay` 等滤镜 |
| `libavutil` | 时间戳、日志、公共结构 |
| fftools | 参数解析与完整流程编排 |

直接使用 `libav*` 要自行维护包、帧、上下文和状态；fftools 把它们组织成命令模型。

## 两条链

```text
录像：RTSP → demux → stream copy → MP4 mux
水印：demux → decode → overlay → encode → MP4 mux
```

## 边界

fftools 不是另一套编解码器；它是 `libav*` 上方的工具编排层。

## 相关

- [[../阶段/02_视频解码原理与FFmpeg选型]]
- [[../知识点/K01_libav与fftools职责边界]]
