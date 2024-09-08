[toc]

## 01.什么是ActivityThread

一旦新的进程被 `Zygote` 创建，该进程的入口点是 `ActivityThread.main()` 方法。这个方法由反射机制调用，正式进入应用的启动流程。

```java
public static void main(String[] args) {
        //....

        //创建Looper和MessageQueue对象，用于处理主线程的消息
        Looper.prepareMainLooper();

        //创建ActivityThread对象
        ActivityThread thread = new ActivityThread(); 

        //建立Binder通道 (创建新线程)
        thread.attach(false);

        Looper.loop(); //消息循环运行
        throw new RuntimeException("Main thread loop unexpectedly exited");
    }
```

尽管名字叫做 `ActivityThread`，但它本身并不是一个 `Thread` 类，也没有继承 `Thread`。而是 `ActivityThread` 类的 `main()` 方法运行在 Android 应用的主线程上。

- **主线程/UI 线程**：每个 Android 应用都有一个主线程（即 UI 线程），负责处理与用户交互相关的操作，比如渲染 UI 和处理用户输入。`ActivityThread.main()` 是该主线程的入口方法，所有应用的生命周期事件、UI 事件都在这个线程上处理。



在 `ActivityThread.main()` 方法中，`attach()` 方法是非常关键的，它负责与 `ActivityManagerService` 进行绑定，并通过 Binder 通信与系统进程交互。这一步使得 `ActivityThread` 能够接收来自系统的指令，比如启动 Activity、启动 Service 等。

`Looper` 是消息驱动的机制，`ActivityThread` 通过它接收和处理 AMS 发送的生命周期事件，比如启动 Activity、销毁 Activity 等。这也是为什么我们说 Android 的主线程是消息循环驱动的。

## 02.main()函数

```java
public static void main(String[] args) {
        //....

        //创建Looper和MessageQueue对象，用于处理主线程的消息
        Looper.prepareMainLooper();

        //创建ActivityThread对象
        ActivityThread thread = new ActivityThread(); 

        //建立Binder通道 (创建新线程)
        thread.attach(false);

        Looper.loop(); //消息循环运行
        throw new RuntimeException("Main thread loop unexpectedly exited");
    }
```

## 03.looper初始化





new一个looper如果 是主线程，那么创建一个不可停止的looper，否则是可以停止的looper。然后将其暴露出来

new一个ActivityThread对象，此时因为：final H mH = new H();，因此创建了mh，可以通过getHandler获取mh。

## Attach

**`ActivityThread`** 通过 `attach()` 方法创建了一个 **`ApplicationThread`**，并将它注册到 **`ActivityManagerService (AMS)`**。

**`ApplicationThread`** 作为 **`ActivityThread`** 的代理，用于与 **AMS** 进行通信。

一旦 `ActivityThread` 完成了注册，它会**进入消息循环（`Looper.loop()`）**，这是一种消息驱动的模型，类似于事件循环。这个消息循环不断监听和处理来自 **AMS** 的请求。

然后，AMS会调用    // 向 ActivityThread 的消息队列中投递一条消息，启动 Activity    sendMessage(H.LAUNCH_ACTIVITY, r);

这个方法会将启动 `Activity` 的消息发送给 `ActivityThread` 的主线程，主线程收到这个消息后会处理并启动对应的 `Activity`。

在 `ActivityThread` 的主线程中，有一个专门的 `Handler`，叫做 **`H`**，它负责接收并处理 `AMS` 发来的各种请求。启动 `Activity` 的消息被发送到消息队列后，`H` 会处理这个消息，调用 `performLaunchActivity()` 方法启动 `Activity`。

```
java复制代码// ActivityThread.java
private void handleLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    // 1. 创建 Activity 实例
    Activity a = performLaunchActivity(r, customIntent);
    
    if (a != null) {
        // 2. 调用 onStart 和 onResume 生命周期
        handleResumeActivity(r.token, false, r.isForward, !r.activity.mFinished);
    }
}
```

- **`performLaunchActivity()`** 方法会创建一个新的 `Activity` 实例，并调用其 `onCreate()` 生命周期方法。
- 然后，`handleResumeActivity()` 会调用 `Activity` 的 `onStart()` 和 `onResume()` 方法，使 `Activity` 显示在屏幕上并开始和用户交互。

### 5. **生命周期管理**

一旦 `Activity` 启动后，`AMS` 继续管理该 `Activity` 的生命周期。当 `AMS` 需要暂停、停止、或销毁该 `Activity` 时，它会向 `ApplicationThread` 发送相应的指令，`ActivityThread` 会根据这些指令调用对应的生命周期方法（如 `onPause()`、`onStop()` 和 `onDestroy()`）。

### 总结：

- **`ActivityThread` 注册 `ApplicationThread` 到 `AMS` 后**，`ActivityThread` 进入消息循环模式，等待 `AMS` 的指令。
- **`AMS` 负责发送指令**，如启动 `Activity`、暂停 `Activity`，这些请求通过 **Binder** 通道传递到 `ApplicationThread`。
- **`ActivityThread` 接收并处理这些请求**，通过调用相应的生命周期方法（如 `onCreate()`、`onResume()`、`onPause()` 等）来执行 `Activity` 的生命周期管理。

  

`ActivityThread` 的 `attach()` 方法通过 `ApplicationThread` 与 `AMS` 建立连接。

事件循环，等待AMS的指令进行初始化



提问：

请问什么是Handler？什么是这个h？

什么是looper对象，什么是Handler对象？

ActivityThread整个过程到底要做什么？ 注册+听从AMS的指令进行初始化？
