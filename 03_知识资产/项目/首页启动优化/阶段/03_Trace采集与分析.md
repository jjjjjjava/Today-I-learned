# 阶段三 · Trace 采集与分析

> 回答：怎样从业务区间得到可复现的系统证据。
> 事实源：[[../启动优化笔记#2. 工具选型：为什么是 Perfetto + 一个业务终点 marker]]

## 工具分工

```text
业务 marker：定义终点
Perfetto：观察区间内系统与应用 Slice
Benchmark：证明受控环境前后是否稳定变化
```

`-a 包名` 用于采集应用自定义 Trace section；非 debuggable 包需要正确配置 `profileable`。

## 计算

用 SQL：

1. `slice` 关联线程与进程；
2. 限定目标进程；
3. 找 `bindApplication` 与 `TTFD_HomeWorkDesk`；
4. 时间戳相减；
5. ns 除以 `1,000,000` 得 ms。

优化前代表 Trace 约 2790ms。

## 下钻方法

- Wall：含子 Slice 的总时长。
- Self：扣除子 Slice 后自身时长。
- Count：出现次数。

聚合 Wall 存在嵌套和重叠，不能直接相加等于 TTFD。

## 知识链接

- [[../知识点/K04_Wall-Self-Count]]
- [[../知识点/K05_doFrame为何不是根因]]

## 复习检查

1. Perfetto、marker、Benchmark各解决什么问题？
2. SQL为什么必须限定进程？
3. Wall、Self、Count如何组合判断？
4. 为什么不能把聚合 Wall 相加？
