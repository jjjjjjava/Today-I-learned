# K10 · NATIVE 栈的四种方向

`NATIVE` 是平台展示或栈形态，不是独立的 Java `Thread.State`。需要按具体栈顶分类：

1. `nativePollOnce`：当前主线程在等消息，通常信息量低；
2. `transactNative`：同步 Binder 等待对端；
3. `read/write/fsync`：文件或设备 IO；
4. `futex/pthread_mutex/pthread_join`：锁或线程依赖。

判断时同时读取：

```text
native 栈顶：主线程具体在 poll、transact、IO 还是等待？
Java 调用链：哪段业务把主线程带入 native？
```

## 相关

- [[../阶段/05_单点归因_主线程与堆栈状态]]
