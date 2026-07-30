# K11 · 主线程同步 IO

主线程同步 IO 的风险不只是“平均慢”，而是磁盘、文件大小、压缩和设备状态可能让耗时失去上界。

Camera 案例：

```text
observeOn(main)
→ Bitmap.compress
→ FileOutputStream.write
```

根因是线程边界错误。修复应让压缩、写入和媒体刷新在 IO 线程完成，再回主线程更新 UI；不要让底层同步工具方法偷偷改变异步语义。

## 相关

- [[../阶段/06_单点归因_归并处理]]
- [[K07_RUNNABLE不等于CPU繁忙]]
