[toc]

## 01. Service介绍

### 1.1 Service是什么

service就是一种**不需要与用户交互，在后台执行长时间操作**的组件。举例：播放音乐，后台下载内容。



**怎么理解：不需要与用户交互，在后台长期运行**。

不与用户交互和后台其实就是一个意思。具体来说，不与用户交互代表其无需前台的UI界面，无需用户的点击事件，也无需响应用户。当然，这一条其实也不是绝对的，如前台 `Service` 就是与 `Notification` 界面结合使用的

### 1.2 分类

它分为两种类型，**启动服务和绑定服务**。

**启动服务**是指其它应用组件通过 `startService()` 启动一个服务，一旦启动，服务将在后台运行，直到主动调用 `stopService()` 停止。否则即使启动服务的组件（如 `Activity`）被销毁，服务也会继续运行，不受影响。

> **示例**：音乐播放器可以在后台播放，即使用户关闭了播放器的界面，音乐依然在后台播放。

**绑定服务**通过 `bindService()` 启动。绑定服务的生命周期与绑定它的组件相关联。当所有绑定到服务的组件都解绑后，服务就会销毁。绑定服务允许组件与服务交互，甚至可以通过 IPC 进行跨进程通信。

Android 还允许你创建**既可以启动又可以绑定的服务**。例如，一个服务可以通过 `startService()` 启动并在后台运行，同时允许其他组件通过 `bindService()` 绑定到它进行交互。



### 1.3 服务运行在哪

服务通常运行在主线程（UI线程）中，所以说它不能做耗时操作。

但是我们可以让其运行在一个独立的线程中，此时其就成为一个独立的服务进程。需要通过下面指定

```
<service
    android:name=".MyService"
    android:process=":myservice_process"/>
```



## 02. Service生命周期

![Service的生命周期](./../_pic_/16e2f2dcb42f7251tplv-t2oaga2asx-jj-mark3024000q75.webp)

**两种不同类型的bind生命周期不同。**

通过 `startService`，`Service` 会经历 `onCreate` 到 `onStartCommand` ，然后处于运行状态，`stopService` 的时候调用 `onDestroy` 方法。

通过 `bindService`，`Service` 会运行 `onCreate` ，然后是调用 `onBind` ， 这个时候调用者和 `Service` 绑定在一起。当所有调用者都解绑了，`Srevice` 就会调用 `onUnbind` -> `onDestroyed` 方法。



**提问：如果start和bind方式结合在一起呢？生命周期是什么样子的？**

由start包裹着bind。即可以看作start后执行bind，同时全部解绑后再destroy。

`onCreate()` → `onStartCommand()` （由 `startService()` 启动），如果有 `bindService()` 绑定到服务，会调用 `onBind()`，但不会停止服务。

当调用 `stopService()` 或 `stopSelf()` 时，服务不会立即销毁，直到所有客户端解绑。

当所有绑定客户端调用 `unbindService()` 后，服务会调用 `onUnbind()`，然后如果已经调用了 `stopService()`，则调用 `onDestroy()`。



## 03. IntentService

### 3.1 什么是IntentService

`Service` 默认运行在应用的主线程中，因此如果你在 `Service` 中执行耗时的任务，会导致主线程阻塞，最终可能引发 "Application Not Responding"（ANR）。

`IntentService` 是自带独立工作线程的Service。这些耗时的任务会在工作线程中执行。本质是

### 3.2 IntentService原理

其在OnCreate时启动HandlerThread工作线程，其内部包含Looper和MsgQueue。

当组件调用startService(intent1)来启动service时，在`onStartCommand()` 生命周期中会将每个 `Intent` 转换为一个消息 (`Message`)，并放入消息队列中。

任务线程在消息循环中取出消息任务，然后进行消息任务异步的处理。

当消息队列已空，所有任务都处理完毕时，`IntentService` 会自动调用 `stopSelf()`，停止循环，并最终停止服务。

### 3.3 IntentService案例演示

我们有一个 `IntentService`，用于执行两个独立的后台任务，比如从服务器下载数据。这两个任务通过传递不同的 `Intent` 来启动。

1. **主线程启动 `IntentService`**：

   - 应用中的 `Activity` 调用 `startService(intent1)` 来启动 `IntentService`。此时，`Intent` 对象 `intent1` 传递给 `IntentService`，包含要执行的第一个任务（如从服务器下载文件1）。
   - 紧接着，主线程又调用了 `startService(intent2)`，传递了第二个 `Intent` 对象 `intent2`，代表另一个任务（如下载文件2）。

   ```java
   // 主线程中，用户点击按钮，启动服务
   Intent intent1 = new Intent(this, MyIntentService.class);
   intent1.putExtra("task", "download_file1");
   startService(intent1);
   
   Intent intent2 = new Intent(this, MyIntentService.class);
   intent2.putExtra("task", "download_file2");
   startService(intent2);
   ```

2. **`IntentService` 开始工作（onCreate）**：

   - 当 `IntentService` 第一次启动时，`onCreate()` 被调用。此时，`IntentService` 会创建一个 `HandlerThread`，该线程会自动创建一个 `Looper`，使工作线程能够持续循环处理消息。
   - 然后，`Handler` 被创建，并与该 `Looper` 关联，用于接收传递进来的 `Intent`（作为消息的一部分）。

   ```java
   @Override
   public void onCreate() {
       super.onCreate();
       HandlerThread thread = new HandlerThread("IntentServiceThread");
       thread.start();
   
       mServiceLooper = thread.getLooper();
       mServiceHandler = new ServiceHandler(mServiceLooper);
   }
   ```

3. **Intent 被添加到消息队列中**：

   - `startService(intent1)` 和 `startService(intent2)` 被调用后，`IntentService` 的 `onStartCommand()` 方法会将每个 `Intent` 转换为一个消息 (`Message`)，并放入消息队列中。`Handler` 会处理这些消息。

   ```java
   @Override
   public int onStartCommand(Intent intent, int flags, int startId) {
       Message msg = mServiceHandler.obtainMessage();
       msg.arg1 = startId;
       msg.obj = intent;
       mServiceHandler.sendMessage(msg);
       return START_NOT_STICKY;
   }
   ```

   动态过程：

   - `intent1`（下载文件1的任务）被封装为消息1，放入消息队列中。
   - `intent2`（下载文件2的任务）被封装为消息2，放入消息队列中。

4. **`Looper` 循环读取消息队列**：

   - `Looper` 在工作线程中保持循环，它依次从消息队列中读取消息（每个 `Intent`），并通过 `Handler` 传递给 `onHandleIntent()` 方法处理。
   - 第一个消息 `intent1` 被读取，调用 `onHandleIntent()` 方法，开始处理任务1（下载文件1）。

   ```java
   @Override
   protected void onHandleIntent(Intent intent) {
       if (intent != null) {
           String task = intent.getStringExtra("task");
           if (task.equals("download_file1")) {
               // 模拟下载文件1的任务
               downloadFile("file1_url");
           } else if (task.equals("download_file2")) {
               // 模拟下载文件2的任务
               downloadFile("file2_url");
           }
       }
   }
   ```

5. **所有任务完成后，自动停止服务**：

   - 当 `Looper` 检测到消息队列已空，所有任务都处理完毕时，`IntentService` 会自动调用 `stopSelf()`，停止循环，并最终停止服务。

