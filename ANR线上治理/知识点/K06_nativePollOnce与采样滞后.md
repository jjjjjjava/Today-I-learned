# K06 · nativePollOnce 与采样滞后

```text
MessageQueue.nativePollOnce
→ MessageQueue.next
→ Looper.loop
```

它通常表示采样这一刻主线程在等待新消息。

不能直接证明：

- 主线程此前没有阻塞；
- 整条 issue 一定无效；
- ANR 一定由系统负载造成。

线上采集存在发现、抓栈和上传时机差。当前主线程栈无法解释超时时，应换同聚类样本、补连续采样或系统 trace；仍无证据则归入 C 类。

## 相关

- [[../阶段/04_单点归因_有效性判断]]
- [[../../03_知识资产/Android/ANR复习/05_线上ANR监控方案原理]]
