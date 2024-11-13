## Android知识体系框架

### 1. 基础组件

- **Activity**：生命周期、启动模式、Intent 和数据传递。
- **Service**：服务的生命周期、前台服务、绑定服务、IntentService。
- **BroadcastReceiver**：广播的注册和接收，发送广播和权限管理。
- **ContentProvider**：数据共享机制，ContentResolver 和 Uri 的使用。
- **Intent 和 IntentFilter**：Intent 的基本使用、隐式和显式 Intent 的区别、IntentFilter 的作用。
- **Application**：Application 类的使用，生命周期管理，全局状态的保存。
- **Context**：Context 的作用、应用场景及不同类型（ApplicationContext 和 Activity Context）的区别。

### 2. IPC（进程间通信）机制

- **AIDL**：Android Interface Definition Language，跨进程通信的定义和使用。
- **Messenger**：通过 Messenger 进行简单的进程间通信。
- **Binder 机制**：Android 的核心 IPC 机制，Binder 的工作原理。
- **ContentProvider 作为 IPC 手段**：通过 ContentProvider 共享数据。
- **其他 IPC 手段**：例如 Broadcast、Intent 等实现进程间通信。

### 3. 消息机制

- **Handler**：Handler 的基本使用，post 和 sendMessage 的区别。
- **Looper**：消息循环机制，主线程和子线程的 Looper 区别。
- **MessageQueue**：消息队列的实现原理。
- **HandlerThread**：用于在子线程中处理消息的线程类。

### 4. View 原理

- **View 树的构建**：View 的基本结构，父子视图关系。
- **测量、布局、绘制流程**：View 的 measure、layout 和 draw 的原理。
- **自定义 View**：如何创建自定义 View，重写 onDraw、onMeasure 方法。
- **事件分发机制**：事件的传递过程，包括 onTouchEvent、onInterceptTouchEvent。

### 5. 事件分发机制

- **事件分发、拦截和消费**：事件在 ViewGroup 和子 View 之间的传递顺序。
- **触摸事件**：MotionEvent 的使用，多点触控和手势识别。
- **滑动冲突**：常见滑动冲突的处理方法。

### 6. Window 管理

- **Window 和 WindowManager**：窗口的概念及其管理。
- **Activity 和 Window 的关系**：Activity 如何通过 WindowManager 管理视图。
- **Dialog 和 Toast**：Dialog 和 Toast 的基本使用及其窗口管理。

### 7. 复杂控件

- **RecyclerView**：RecyclerView 的使用和自定义，Adapter 和 ViewHolder 模式。
- **ViewPager**：ViewPager 的基本使用，PagerAdapter 和 FragmentPagerAdapter。
- **CoordinatorLayout**：高级布局，包括滑动事件的协调。
- **其他 UI 组件**：如 ScrollView、ListView 等高级使用。

### 8. 流行框架

- **网络请求框架**：如 Retrofit、OkHttp。
- **图片加载框架**：如 Glide、Picasso。
- **依赖注入框架**：如 Dagger、Hilt。
- **响应式编程框架**：如 RxJava、LiveData。
- **数据库框架**：Room 数据库、SQLite 的封装和使用。