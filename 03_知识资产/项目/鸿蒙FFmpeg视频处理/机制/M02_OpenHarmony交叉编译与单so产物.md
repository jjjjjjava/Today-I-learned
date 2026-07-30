# M02 · OpenHarmony 交叉编译与单 `.so` 产物

```text
FFmpeg适配源码
→ HPKBUILD声明配置
→ Lycium组织下载、配置与构建
→ OpenHarmony SDK/NDK的Clang/LLVM实际编译
→ 链接libav*、fftools、平台适配
→ 单一Native Addon .so
```

构建配置决定最终产物拥有哪些协议、滤镜和 codec。命令里写了 codec 名，不代表 `.so` 已包含它。

单一 `.so` 简化 ArkTS 加载与依赖分发，但不改变各库内部职责。

## 相关

- [[../阶段/03_OpenHarmony交叉编译与fftools嵌入]]
- [[../知识点/K02_Lycium与编译工具链]]
- [[../知识点/K11_codec不存在与构建能力]]
