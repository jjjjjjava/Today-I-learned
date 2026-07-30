# K01 · libav 与 fftools 职责边界

`libavformat/libavcodec/libavfilter` 提供底层媒体能力；fftools 解析命令参数并编排输入、滤镜、编码和输出流程。

fftools 不是编解码器，也不是 `libav*` 的替代品。

## 自检

1. `libavformat`、`libavcodec`、`libavfilter` 各做什么？
2. fftools 额外解决什么？
3. 直接调用 `libav*` 要自行管理哪些状态？
