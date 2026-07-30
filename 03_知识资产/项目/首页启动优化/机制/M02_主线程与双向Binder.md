# 机制二 · 主线程与双向 Binder

## 主链路

```text
Binder线程池初始化
→ ActivityThread.main
→ prepareMainLooper
→ new ActivityThread
→ attach(false)
→ Looper.loop
```

## 双向通道

`ActivityThread.attach(false)` 获取 AMS 代理，再把应用侧 `ApplicationThread` Binder stub 交给 AMS。

- App 持 AMS 代理：应用主动请求系统。
- AMS 持 ApplicationThread 代理：系统反向通知应用。

AMS 调用 `bindApplication` 时，应用 Binder 线程接收事务并封装 `H.BIND_APPLICATION` 消息；真正生命周期工作由主线程 `mH` 串行执行。

## 边界

Binder 线程负责跨进程交接，不承担应用启动重活。生命周期、UI和大部分框架初始化仍回到主线程。

## 复习检查

1. `ActivityThread.main`做哪几步？
2. 双向Binder通道两端各持有什么？
3. `bindApplication`为什么最终回到主线程？
4. 为什么不能把Binder线程当启动工作线程？
