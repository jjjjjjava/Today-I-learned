# 阶段三 · Profiler归因与根因假设

> 回答：为什么紧急定位选Profiler；它把问题推进到哪一步。
> 事实源：[[../ARouter启动优化笔记#0.5 为什么紧急定位选择 AS Profiler]]

## 工具选择

线上已把范围缩到`arouter.init`，且异常接近8秒。第一目标是快速回答：

> ARouter内部是否存在秒级重量级调用栈？

因此使用AS CPU Profiler Sampling，采样间隔约1000μs。Profiler适合快速找主调用栈；不用于证明精细线上收益。

## 调用栈

```text
ARouter.init
→ LogisticsCenter.init
→ ClassUtils.getFileNameByPackageName
→ DexFile.openDexFile
→ openDexFileNative
```

关键观察：

- 整体本地Trace约9.74s；
- `openDexFileNative`聚合约7.603s；
- 耗时属于ARouter路由表发现路径。

## 形成的假设

```text
编译期register链可能失效
→ loadRouterMap没有完成注册
→ registerByPlugin=false
→ 运行时回退Dex扫描
```

Profiler只能支持“正在扫描Dex”；完整根因还需要源码条件、构建产物和修复反证。

## 复习检查

1. 为什么先用Profiler，不先用Perfetto？
2. Sampling数据能证明什么，不能证明什么？
3. `openDexFileNative`怎样归属于ARouter？
4. 从调用栈到完整根因还缺什么？
