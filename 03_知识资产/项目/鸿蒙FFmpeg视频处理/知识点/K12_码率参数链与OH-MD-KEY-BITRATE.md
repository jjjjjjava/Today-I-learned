# K12 · 码率参数链与 OH_MD_KEY_BITRATE

```text
-b:v
→ fftools
→ format_->bit_rate
→ SetCodecFormat
→ OH_AVFormat
→ OH_MD_KEY_BITRATE
→ OH_VideoEncoder_Configure
```

确认前半段已有值，就能把怀疑点下移到平台编码器封装。项目缺陷是最后配置前漏写码率字段。

## 自检

1. 怎样排除命令位置？
2. 怎样证明 fftools 已解析参数？
3. 参数链具体断在哪里？
