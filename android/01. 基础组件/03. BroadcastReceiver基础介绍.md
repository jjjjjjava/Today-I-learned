[toc]

## 01. Broadcast介绍

### 1.1 什么是广播

在 Android 系统中，广播（Broadcast）是一种用于Android系统不同组件间的通信机制。

当其为全局广播，进行跨进程组件通信时，其使用Binder机制实现。

当其为本地广播，进行进程内部组件通信时，依赖于进程内部的消息机制实现。



这里比较困惑了，不是有Binder机制，消息机制吗？为什么还需要一个广播来进行通信啊。很简单啊，你可以看作它是对这些机制的封装，提供更高级的通信。

**BroadcastReceiver** 则是对发送出来的**Broadcast**进行过滤、接受和响应的组件。

### 1.2 广播执行流程

发送-匹配-接收和响应

首先将要发送的消息和用于过滤的信息（Action，Category）装入一个 **Intent**对象，然后通过调用**Context.sendBroadcast()**、**sendOrderBroadcast()** 方法把 Intent 对象以广播形式发送出去。 

广播发送出去后，所以已注册的 BroadcastReceiver 会检查注册时的 **IntentFilter** 是否与发送的 Intent 相匹配，若匹配则会调用 BroadcastReceiver 的 **onReceiver()** 方法进行接收和响应。

### 1.3 广播分类

- Android中的广播分为两种类型，标准广播和有序广播
  - 标准广播：标准广播是一种完全异步执行的广播，在广播发出后所有的广播接收器会在同一时间接收到这条广播，之间没有先后顺序，效率比较高，且无法被截断。
  - 有序广播：有序广播是一种同步执行的广播，在广播发出后同一时刻只有一个广播接收器能够接收到， 优先级高的广播接收器会优先接收，当优先级高的广播接收器的 onReceiver() 方法运行结束后，广播才会继续传递，且前面的广播接收器可以选择截断广播，这样后面的广播接收器就无法接收到这条广播了。

当然也可以分为全局广播和本地广播。

## 02. 案例演示

**静态注册的接收器**是在 `AndroidManifest.xml` 中声明的，即使应用未启动，甚至应用没有运行过，只要广播发出，静态注册的接收器就能响应并处理广播。当广播到达并匹配时，系统会自动创建广播接收器的实例，并调用其 `onReceive()` 方法。完成接收处理后被销毁。

**动态注册的接收器**只有在应用运行并通过代码（通常在 `Activity` 或 `Service` 中）调用 `registerReceiver()` 后，才能接收到广播。它的实例在注册时就已经创建好。而静态的只有匹配成功时才创建。



### 2.1 静态注册广播接收器

要首先在 `AndroidManifest.xml` 文件中声明，然后代码中给出对应的类，内部重写 `onReceive()`即可。

当广播事件发生时，Android 系统会检查该广播的 `Intent` 是否与任何静态注册的 `BroadcastReceiver` 的 `intent-filter` 匹配。如果匹配成功，Android 系统会根据 `<receiver>` 标签中的 `android:name` 属性自动创建对应类的 `BroadcastReceiver` 实例。

当广播匹配时，系统会调用该接收器的 `onReceive()` 方法，并将广播的 `Intent` 传递给它。一旦 `onReceive()` 方法执行完毕，接收器实例会被系统自动销毁，不再占用资源。



**案例演示如下**：

**1. 静态注册 `BroadcastReceiver` 的定义与配置**：

- 使用 `<receiver>` 标签声明。
- 使用 `<intent-filter>` 标签来设置接收器的过滤器，使接收器能够接收到特定的广播事件。

```xml
<application>
    <receiver android:name=".NormalReceiver">
        <intent-filter>
            <action android:name="com.example.normal.receiver" />
        </intent-filter>
    </receiver>
</application>
```

**2. 标准广播的发送与接收**：

- **标准广播**：使用 `sendBroadcast(Intent)` 发送普通广播。
- 广播接收器必须在 `AndroidManifest.xml` 中声明，且配置与广播匹配的 `action` 属性。

**Receiver 的定义**：

```java
public class NormalReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String msg = intent.getStringExtra("Msg");
        Log.i("NormalReceiver", "接收到消息: " + msg);
    }
}
```

**发送广播**：

```java
public void sendBroadcast(View view) {
    Intent intent = new Intent("com.example.normal.receiver");
    intent.putExtra("Msg", "Hello");
    sendBroadcast(intent);
}
```

**3. 有序广播的发送与接收**：

- **有序广播**：通过 `sendOrderedBroadcast(Intent, String)` 方法发送广播，可以指定接收的顺序。
- 不同的 `BroadcastReceiver` 可以设置不同的优先级（`priority` 属性），优先级高的接收器先接收到广播并可以传递数据给下一个接收器。

**有序广播接收器定义**：

```java
public class OrderReceiver_1 extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.e("OrderReceiver_1", "收到消息");
        String msg = intent.getStringExtra("Msg");
        Bundle bundle = new Bundle();
        bundle.putString("Data", "(Data from OrderReceiver_1)");
        setResultExtras(bundle);
    }
}

public class OrderReceiver_2 extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.e("OrderReceiver_2", "收到消息");
        String data = getResultExtras(true).getString("Data");
        Bundle bundle = new Bundle();
        bundle.putString("Data", "(Data from OrderReceiver_2)");
        setResultExtras(bundle);
    }
}

public class OrderReceiver_3 extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.e("OrderReceiver_3", "收到消息");
        String data = getResultExtras(true).getString("Data");
    }
}
```

**发送有序广播**：

```java
public void sendOrderBroadcast(View view) {
    Intent intent = new Intent("com.example.order.receiver");
    intent.putExtra("Msg", "Hello");
    sendOrderedBroadcast(intent, null);
}
```

**在清单文件中配置**：

```xml
<receiver android:name=".OrderReceiver_1">
    <intent-filter android:priority="100">
        <action android:name="com.example.order.receiver" />
    </intent-filter>
</receiver>

<receiver android:name=".OrderReceiver_2">
    <intent-filter android:priority="99">
        <action android:name="com.example.order.receiver" />
    </intent-filter>
</receiver>

<receiver android:name=".OrderReceiver_3">
    <intent-filter android:priority="98">
        <action android:name="com.example.order.receiver" />
    </intent-filter>
</receiver>
```

### 2.2 动态注册广播接收器

要在代码中调用`registerReceiver()` 注册并调用`unregisterReceiver`销毁

**案例演示**：

**在 `Service` 中动态注册 `BroadcastReceiver`：**

```java
public class BroadcastService extends Service {

    private BroadcastReceiver receiver;
    private final String TAG = "BroadcastService";

    @Override
    public void onCreate() {
        // 创建 IntentFilter，指定要监听的广播事件
        IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(MainActivity.ACTION);
        
        // 动态创建 BroadcastReceiver 实例并实现 onReceive() 方法
        receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                Log.e(TAG, "BroadcastService 接收到广播");
            }
        };
        
        // 注册 BroadcastReceiver
        registerReceiver(receiver, intentFilter);
        Log.e(TAG, "BroadcastService 注册了接收器");
        super.onCreate();
    }

    @Override
    public void onDestroy() {
        // 取消注册 BroadcastReceiver，避免内存泄漏
        unregisterReceiver(receiver);
        Log.e(TAG, "BroadcastService 取消注册接收器");
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
```

**在 `Activity` 中启动、停止 `Service` 及发送广播：**

```java
public class MainActivity extends AppCompatActivity {

    public final static String ACTION = "com.example.receiver";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    // 启动服务
    public void startService(View view) {
        Intent intent = new Intent(this, BroadcastService.class);
        startService(intent);
    }

    // 发送广播
    public void sendBroadcast(View view) {
        Intent intent = new Intent(ACTION);
        sendBroadcast(intent);
    }

    // 停止服务
    public void stopService(View view) {
        Intent intent = new Intent(this, BroadcastService.class);
        stopService(intent);
    }
}
```



**补充：activity内部注册广播接收器的时机**：

在 `Activity` 中，建议在 `onResume()` 方法中注册广播接收器，在 `onPause()` 方法中注销广播接收器。这是因为当 `Activity` 不可见时，接收广播没有意义，onResume和onPause相对应，可以正确释放，防止内存泄漏。

## 03. 本地广播

之前发送和接收到的广播全都是属于系统全局广播，即发出的广播可以被其他应用接收到，而且也可以接收到其他应用发送出的广播，这样可能会有不安全因素

因此，在某些情况下可以采用本地广播机制，使用这个机制发出的广播只能在应用内部进行传递，而且广播接收器也只能接收本应用内自身发出的广播。本地广播需要借助LocalBroadcastManager进行管理注册和销毁。同时发送时也要借助localBroadcastManager进行发送

即：进程间通信改为同一进程内部线程间通信，底层的通信机制也由Binder改为事件机制。

### **3.1 API**：

| 函数                                                         | 作用               |
| ------------------------------------------------------------ | ------------------ |
| `LocalBroadcastManager.getInstance(this).registerReceiver(BroadcastReceiver, IntentFilter)` | 注册本地广播接收器 |
| `LocalBroadcastManager.getInstance(this).unregisterReceiver(BroadcastReceiver)` | 注销本地广播接收器 |
| `LocalBroadcastManager.getInstance(this).sendBroadcast(Intent)` | 发送异步本地广播   |
| `LocalBroadcastManager.getInstance(this).sendBroadcastSync(Intent)` | 发送同步本地广播   |

### **3.2  本地广播的使用步骤**：

1. **创建广播接收器**：

   - 创建一个继承自 `BroadcastReceiver` 的接收器类，用于处理本地广播。

   ```java
   public class LocalReceiver extends BroadcastReceiver {
       private final String TAG = "LocalReceiver";
   
       @Override
       public void onReceive(Context context, Intent intent) {
           Log.e(TAG, "接收到了本地广播");
       }
   }
   ```

2. **注册与解除注册本地广播**：

   - 在 `Activity` 或 `Service` 中，通过 `LocalBroadcastManager` 注册和解除注册广播接收器。

   ```java
   private LocalBroadcastManager localBroadcastManager;
   private LocalReceiver localReceiver;
   private final String LOCAL_ACTION = "com.example.local.receiver";
   
   @Override
   protected void onCreate(Bundle savedInstanceState) {
       super.onCreate(savedInstanceState);
       setContentView(R.layout.activity_main);
   
       // 获取 LocalBroadcastManager 实例
       localBroadcastManager = LocalBroadcastManager.getInstance(this);
       
       // 创建并注册本地广播接收器
       localReceiver = new LocalReceiver();
       IntentFilter filter = new IntentFilter(LOCAL_ACTION);
       localBroadcastManager.registerReceiver(localReceiver, filter);
   }
   
   @Override
   protected void onDestroy() {
       super.onDestroy();
       // 注销本地广播接收器
       localBroadcastManager.unregisterReceiver(localReceiver);
   }
   ```

3. **发送本地广播**：

   - 使用 `sendBroadcast(Intent)` 方法发送本地广播。

   ```java
   public void sendLocalBroadcast(View view) {
       Intent intent = new Intent(LOCAL_ACTION);
       localBroadcastManager.sendBroadcast(intent);
   }
   ```

### 3.3. 注意事项：

1. **无法静态注册**：
   - 本地广播不能通过 `AndroidManifest.xml` 中静态注册的方式接收，因为静态注册的目的是在应用未启动时接收广播，而本地广播发送时，应用本身一定是处于运行状态，因此没有必要通过静态注册接收。
2. **本地广播只能在应用内部传递**：
   - `LocalBroadcastManager` 发送的广播不会离开应用进程，不能跨进程或跨应用传递，因此其他应用无法接收到本地广播。



## 04. 限制广播发送范围（私有权限）

上面的广播存在一个问题，对于全局广播虽然只有匹配到才能接收广播，但是它可以监听到任何应用发送的广播。

对于本地广播，虽然限制了发送范围在本地，但是不够灵活。我们需要一种更灵活的方式，帮助我们精确限制广播发送的范围，而不是全局可以接收或者仅限于本地。

这里我们的方法是给全局广播设置权限。

### **4.1 定义权限**

首先，我们要为广播创建一个自定义权限，这个权限用于限制谁可以发送或接收广播。

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.broadcast">

    <permission android:name="com.example.broadcast.SEND_BROADCAST"
        android:protectionLevel="signature" />

    <application>
        <!-- 广播接收器 -->
        <receiver android:name=".MyReceiver">
            <intent-filter>
                <action android:name="com.example.broadcast.MY_ACTION" />
            </intent-filter>
            <meta-data android:name="android:exported" android:value="false"/>
        </receiver>
    </application>
</manifest>

```

- `protectionLevel="signature"` 的意思是，**只有和声明这个权限的应用签名相同的应用**，才能使用这个权限（即发送或接收广播）。

通常会用到两种保护级别：

- **normal**：普通权限，只要在安装时声明即可，通常用于较低风险的功能。
- **signature**：签名权限，只允许由相同证书签名的应用才能使用。

### **4.2 发送广播时限定权限**

在代码中，发送广播时使用 `sendBroadcast(Intent, String)` 方法，第二个参数是你刚刚定义的自定义权限。这个权限限制了**只有拥有这个权限的接收器**才能接收到广播。

```java
private final String PERMISSION_PRIVATE = "com.example.permission.receiver";

public void sendPermissionBroadcast(View view) {
    // 发送广播时使用自定义权限，只有具备该权限的应用能接收到广播
    sendBroadcast(new Intent("Hi"), PERMISSION_PRIVATE);
}
```

这样，只有拥有 `com.example.permission.receiver` 权限的应用，才能接收到这个广播。

### **4.3 动态注册广播接收器时声明权限**

在注册广播接收器时，你可以通过 `registerReceiver()` 来声明该接收器可以接收的广播范围。

```java
private final String PERMISSION_PRIVATE = "com.example.permission.receiver";
private PermissionReceiver permissionReceiver;

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    // 创建 IntentFilter 用于匹配广播
    IntentFilter intentFilter = new IntentFilter("Hi");
    permissionReceiver = new PermissionReceiver();

    // 使用自定义权限注册广播接收器
    registerReceiver(permissionReceiver, intentFilter, PERMISSION_PRIVATE, null);
}
```

在这个例子中，只有发送广播时带有 `com.example.permission.receiver` 权限的广播，才能被这个接收器接收。





## 05. 广播发送的原理

Android中的广播底层基于Binder机制，借助AMS进行消息的存储转发。

### 4.1 消息模型

- 模型中有3个角色：
  - 1.消息订阅者（广播接收者）
  - 2.消息发布者（广播发布者）
  - 3.消息中心（`AMS`，即`Activity Manager Service`）
  - [![img](https://camo.githubusercontent.com/f402cd17b184773e353e6381c534a0212ce8c5b881d92c4c9ac80f880cc696b7/687474703a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f3934343336352d303839366261386439313535313430652e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)](https://camo.githubusercontent.com/f402cd17b184773e353e6381c534a0212ce8c5b881d92c4c9ac80f880cc696b7/687474703a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f3934343336352d303839366261386439313535313430652e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)

### 4.2 原理描述

- 原理描述：

  1. 广播接收者 通过 `Binder`机制在 `AMS` 注册

  2. 广播发送者 通过 `Binder` 机制向 `AMS` 发送广播

  3. AMS根据 广播发送者 要求，在已注册列表中，寻找合适的广播接收者寻找依据：`IntentFilter / Permission`

  4. `AMS`将广播发送到合适的广播接收者相应的消息循环队列中；

  5. 广播接收者通过 消息循环 拿到此广播，并回调 `onReceive()`

  

**特别注意**：默认情况下，广播接收器运行在UI线程，因此，onReceive方法不能执行耗时操作，否则将导致ANR。那如果我非要执行耗时操作呢？建议开启一个 IntentService 将耗时操作交给 Service

