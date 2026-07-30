# Flutter 核心与 MethodChannel 综合面试笔记

## 00. 总模型

Flutter 是声明式 UI：

```text
UI = f(state)
```

状态变化后，Flutter 重新生成 Widget 配置，再比较新旧配置，复用仍可复用的 Element 和 RenderObject，只执行必要更新。

```text
修改 State
setState() 标记 Element 为 dirty
下一帧执行 build()
生成新 Widget
比较新旧 Widget
更新或替换 Element
必要时更新 RenderObject
必要时 layout / paint
```

必须区分：

```text
rebuild != 整页重新创建
rebuild != 必然 layout
rebuild != 必然 paint
```

---

## 01. StatelessWidget 与 StatefulWidget

### 1.1 StatelessWidget

`StatelessWidget` 没有独立可变状态。UI 由构造参数和外部依赖决定。

父组件传入新参数时，框架创建新的 Widget 配置，不会修改旧 Widget。

### 1.2 StatefulWidget

`StatefulWidget` 本身也不可变，但会创建独立 `State` 保存可变状态。

```text
StatefulWidget：不可变配置
State：可变数据
StatefulElement：把 Widget 和 State 挂在树里的长期节点
```

```dart
class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    return Text('$count');
  }
}
```

### 1.3 setState() 做什么

```dart
setState(() {
  count++;
});
```

`setState()`：

```text
同步执行回调，修改 State
标记对应 Element 为 dirty
等待下一帧重新 build
```

它不直接重绘，也不销毁整个页面。

面试表达：

> `setState()` 先同步修改 State，再把对应 Element 标记为 dirty。下一帧重新执行 `build()`，框架比较新旧 Widget，尽量复用 Element 和 RenderObject；只有渲染属性变化时，才继续触发必要的 layout 或 paint。

### 1.4 State 生命周期

```text
createState
initState
didChangeDependencies
build
didUpdateWidget
deactivate
dispose
```

- `initState()`：一次性初始化、创建 Controller、注册订阅。
- `didChangeDependencies()`：依赖的 Theme、Locale、InheritedWidget 等变化。
- `build()`：根据当前参数和状态生成 Widget。
- `didUpdateWidget()`：节点身份没变，但父组件传入新配置。
- `deactivate()`：暂时离树，仍可能重新插入。
- `dispose()`：永久销毁，取消订阅并释放资源。

异步结果回来时，State 可能已经销毁：

```dart
final data = await loadData();

if (!mounted) return;

setState(() {
  result = data;
});
```

`mounted` 表示 State 是否仍挂在 Element 树中。

---

## 02. Widget、Element、RenderObject

### 2.1 三者职责

```text
Widget：不可变 UI 配置
Element：Widget 在树中的长期实例
RenderObject：真正负责布局和绘制
```

Widget 描述：

```text
组件类型
构造参数
子组件
```

Element 保存：

```text
节点位置和父子关系
当前 Widget
生命周期
BuildContext
State
```

RenderObject 负责：

```text
测量
布局
绘制
命中测试
```

不是每个 Widget 都对应 RenderObject。`StatelessWidget`、`StatefulWidget` 主要组合配置；底层 `RenderObjectWidget` 才创建或更新 RenderObject。

记忆：

```text
Widget：施工图纸
Element：现场工位和身份记录
RenderObject：真正测量、摆放、绘制的工人
```

### 2.2 新旧 Widget 如何匹配

同一位置主要根据：

```text
runtimeType + key
```

匹配：

```text
复用 Element
Element 持有新 Widget
必要时更新 RenderObject
```

不匹配：

```text
移除旧 Element
创建新 Element
重新创建相关 State 或 RenderObject
```

标题变化时，会创建新 `Text` Widget，但通常可复用原 Element 和底层 RenderObject，只更新文字相关属性。

### 2.3 Key

没有 Key，列表主要按类型和兄弟位置匹配。

```text
原位置 0：张三的 Element + 输入状态
插入后位置 0：王五的 Widget
```

旧 Element 可能直接接收王五的新 Widget，但仍保留张三的 State，造成状态串位。

```dart
UserItem(
  key: ValueKey(user.id),
  user: user,
)
```

此时 State 跟随 `user.id`，不再跟随列表位置。

Key 首要解决身份正确性，不是提高性能。

- `ValueKey`：根据稳定业务 ID 匹配，最常用。
- `ObjectKey`：根据对象身份匹配。
- `UniqueKey`：每次都不同，强制不复用旧节点。
- `GlobalKey`：全树唯一，可获取 State 和 BuildContext；成本较高，避免滥用。

面试表达：

> 列表插入、删除、排序时，稳定 Key 能让 Element 和 State 跟随业务对象，而不是跟随兄弟位置，避免输入框、动画等状态串位。

---

## 03. Dart 异步

### 3.1 Isolate 与事件循环

每个 Isolate 具有：

```text
独立内存
单线程执行模型
自己的事件循环
自己的任务队列
```

同一 Isolate 同一时刻只能执行一段 Dart 代码。

可用 Android `Handler + Looper` 辅助理解，但有区别：

```text
Android 线程可共享进程内存
不同 Isolate 不共享可变内存，主要通过消息通信
```

### 3.2 await 不创建线程

```dart
Future<void> load() async {
  print('A');
  final data = await request();
  print('C');
}

load();
print('B');
```

执行：

```text
打印 A
request() 返回 Future
await 保存函数后半段并交出执行权
load() 返回未完成 Future
当前调用栈继续，打印 B
request 完成
事件循环恢复 await 后半段
打印 C
```

结果：

```text
A
B
C
```

准确理解：

> `await` 暂停当前 async 函数，把执行权交还事件循环；Future 完成后，再恢复函数后半段。它本身不会创建线程。

### 3.3 两个异步队列

优先级：

```text
当前同步代码
microtask queue
event queue
```

```dart
print('A');
Future(() => print('event'));
Future.microtask(() => print('microtask'));
print('B');
```

输出：

```text
A
B
microtask
event
```

同步代码先跑完。调用栈清空后，先清空微任务，再处理普通事件。

### 3.4 I/O 与 CPU 任务

网络、文件等 I/O 任务主要等待外部结果：

```dart
final response = await dio.get(url);
```

大 JSON 解析属于 CPU 密集任务：

```dart
final result = jsonDecode(hugeJson);
```

它会持续占用 UI Isolate：

```text
调用栈不空
事件循环不能处理新任务
点击、动画、绘制无法及时执行
```

下面写法仍在同一个 Isolate：

```dart
Future(() => jsonDecode(hugeJson));
```

轮到它执行时仍会卡 UI。

真正隔离 CPU 工作：

```dart
final result = await Isolate.run(
  () => jsonDecode(hugeJson),
);
```

Flutter 也可使用：

```dart
compute(parseJson, hugeJson);
```

面试口诀：

```text
I/O 等待：async/await
CPU 重活：Isolate.run() 或 compute()
```

---

## 04. 状态管理

### 4.1 setState

适合单个页面内的小范围状态：

```text
计数器
按钮选中
展开/收起
局部加载状态
```

`setState()` 本身通常不是性能问题。常见问题是状态放得太高，导致大片子树 rebuild，或者在 `build()` 中执行耗时任务。

### 4.2 Provider

Provider 的主要能力：

```text
依赖注入：沿 Widget 树提供对象
状态监听：变化后通知依赖它的 Widget rebuild
```

`ChangeNotifier` 使用观察者模式：

```text
ChangeNotifier 保存监听回调
Widget 通过 watch/select 建立监听
业务修改状态
调用 notifyListeners()
Provider 通知监听者
相关 Element 进入 rebuild 流程
```

不能简单说“Provider 调用其他 Widget 的 `setState()`”。准确说法：

> `notifyListeners()` 通知已注册监听者，Provider 让依赖该状态的 Element 进入重建流程。

常见链路：

```text
接口或原生回调
Repository 处理数据
ChangeNotifier 修改状态
notifyListeners()
监听状态的 Widget rebuild
```

读取方式：

```dart
context.read<UserModel>();
```

只读取，不监听。

```dart
context.watch<UserModel>();
```

监听整个对象。

```dart
context.select<UserModel, String>(
  (model) => model.name,
);
```

只监听选中字段，减少无关 rebuild。

### 4.3 Riverpod

Riverpod 可理解成独立状态容器和响应式依赖图：

```text
Provider：状态或计算节点
ref.watch：建立响应式依赖
ref.read：只读取当前值
ref.listen：监听变化并执行副作用
```

它不依赖 `BuildContext` 查找状态。Provider 之间也能通过 `ref.watch` 建立依赖。

```dart
class Counter extends Notifier<int> {
  @override
  int build() => 0;

  void increment() {
    state++;
  }
}

final counterProvider =
    NotifierProvider<Counter, int>(Counter.new);
```

UI 监听：

```dart
final count = ref.watch(counterProvider);
```

事件中修改：

```dart
ref.read(counterProvider.notifier).increment();
```

状态链路：

```text
修改 state
Riverpod 更新 Provider 节点
通知依赖者
相关 UI 或下游 Provider 重新计算
```

异步状态通常用 `AsyncValue` 表示：

```text
AsyncLoading
AsyncData
AsyncError
```

### 4.4 Provider 与 Riverpod

```text
Provider + ChangeNotifier
- 通常依赖 Widget 树和 BuildContext
- 修改字段后手动 notifyListeners()
- 使用 context.read/watch/select

Riverpod
- 状态存于独立容器
- 不依赖 BuildContext 读取
- 使用 ref.read/watch/listen
- 自动维护 Provider 依赖图
- 异步状态和组合计算能力更完整
```

面试表达：

> Provider 常通过 `ChangeNotifier + notifyListeners()` 实现观察者模式，并依托 Widget 树完成依赖注入。Riverpod 把状态建模为独立容器中的响应式节点，通过 `ref.watch` 跟踪依赖，不依赖 BuildContext，对异步状态和状态组合支持更完整。

---

## 05. getui_flutter 与 MethodChannel

### 5.1 项目问题

现象：

```text
Android 个推 SDK 收到完整 payload
Flutter 只拿到插件暴露的部分字段
自定义业务数据缺失
```

逐层检查：
打断点的，发现Android SDK可以拿到，但是不传

定位结果：

```text
Android SDK 原始数据完整
插件传给 Flutter 的 Map 字段不完整
```

根因是插件 Android 层的跨端字段映射不完整。

修复：

```text
读取原生回调完整 payload
把复杂原生对象转成 Map/List/基础类型
统一字段名和空值规则
通过 MethodChannel 发送
Dart 统一解析和分发
修改后的插件作为内部依赖维护
```

表面问题是字段缺失，本质是 Flutter 插件定义的跨端数据协议不完整。

### 5.2 MethodChannel 原理

MethodChannel 是 Dart 与 Android/iOS 之间的异步方法消息通道。

它不是 Dart 直接调用 Kotlin：

```text
Dart invokeMethod()
MethodCodec 编码方法名和参数
BinaryMessenger 发送消息
Flutter Engine 跨端传递
Android MethodCallHandler 处理
result.success / error / notImplemented
结果编码返回
Dart Future 完成
```

即使原生立即返回，Dart 侧拿到的仍是 `Future`。

可用 Android Handler 类比：

```text
方法名 ≈ Message.what
参数 ≈ Message.obj
MethodCallHandler ≈ Handler.handleMessage
Result ≈ 异步结果回调
```

区别是 MethodChannel 消息需要编解码，并穿过 Flutter Engine。

### 5.3 Android 调 Dart

Android：

```kotlin
private val channel = MethodChannel(
    flutterEngine.dartExecutor.binaryMessenger,
    "getui_bridge"
)

fun sendPayload(payload: Map<String, Any?>) {
    channel.invokeMethod("onReceivePayload", payload)
}
```

Dart：

```dart
const channel = MethodChannel('getui_bridge');

Future<void> initChannel() async {
  channel.setMethodCallHandler((call) async {
    if (call.method == 'onReceivePayload') {
      final payload =
          Map<String, dynamic>.from(call.arguments);
      handlePayload(payload);
    }
  });
}
```

两端必须保证：

```text
Channel 名称一致
方法名一致
Codec 兼容
参数类型受 Codec 支持
```

### 5.4 支持的数据类型

常见类型：

```text
null
bool
int
double
String
字节数组
List
Map
```

复杂 Kotlin SDK 对象不能直接发送，必须先转成 Map 或 JSON。

部分字段缺失常见原因：

```text
原生转 Map 时漏字段
两端字段名不一致
复杂对象没有转换
Dart 解析类型错误
```

整条调用失败常见原因：

```text
Channel 名称不一致
方法名不一致
Handler 未注册
Codec 不一致
```

### 5.5 为什么使用 MethodChannel

当前场景：

```text
推送事件低频、离散
Dart 要调用原生初始化
Dart 要获取 ClientId
原生要通知单次 payload
```

MethodChannel 同时支持双向方法调用，结构简单。

```text
MethodChannel：一次调用，对应一次结果
EventChannel：建立订阅，持续发送多个事件
```

传感器、定位、下载进度等持续数据流更适合 EventChannel。

### 5.6 项目面试表达

> 项目使用个推 Flutter 插件接入推送。排查时发现 Android SDK 原始回调中的 payload 完整，但插件传入 MethodChannel 的参数 Map 丢失了部分自定义字段。我沿原生回调、插件映射、Channel 参数和 Dart Handler 逐层定位，最终补全 Android 层字段映射，将复杂对象统一转换为 Flutter Codec 支持的类型，并在 Dart 层集中解析和分发。修复后的插件作为内部依赖维护，避免各业务重复适配。

---

## 06. 高频错误

```text
错误：setState() 直接重绘
正确：setState() 标记 Element dirty，RenderObject 必要时绘制

错误：rebuild 等于整页销毁
正确：Widget 配置常新建，Element 和 RenderObject 可复用

错误：Key 主要提高性能
正确：Key 主要保证 State 与业务身份正确对应

错误：await 开启线程
正确：await 暂停 async 函数，把执行权交给事件循环

错误：Future 包装 CPU 任务就不会卡
正确：同一 Isolate 中执行仍会卡，CPU 重活需要其他 Isolate

错误：Provider 调用其他 Widget 的 setState()
正确：Provider 通知监听者，让相关 Element 进入 rebuild 流程

错误：MethodChannel 是 Dart 直接调用 Kotlin
正确：调用被编码为消息，经 Flutter Engine 跨端传输
```

---

## 07. 一分钟综合回答

> Flutter 是声明式 UI。Widget 是不可变配置，Element 是 Widget 在树中的长期实例，保存节点身份、生命周期和 State，RenderObject 负责测量、布局、绘制和命中测试。调用 `setState()` 时，Flutter 修改 State 并把对应 Element 标记为 dirty，下一帧重新 `build()`。框架根据 `runtimeType + key` 比较新旧 Widget，尽量复用 Element 和 RenderObject，所以 rebuild 不等于整页重建，也不一定触发 layout 和 paint。
>
> 列表默认主要按类型和位置匹配。插入、删除、排序后，State 可能跟错业务数据；稳定的 `ValueKey` 能让 State 跟随业务 ID。Dart 的 `async/await` 不创建线程，`await` 只是暂停当前 async 函数，把执行权交回事件循环；Future 完成后再恢复后半段。I/O 任务直接 await，CPU 密集任务需要使用 `Isolate.run()` 或 `compute()`。
>
> 状态管理本质是 `UI = f(state)`。局部状态使用 `setState`；Provider 常通过 `ChangeNotifier + notifyListeners()` 通知依赖该状态的 Widget rebuild；Riverpod 使用独立容器和响应式依赖图，通过 `ref.watch` 跟踪依赖。
>
> MethodChannel 不是 Dart 直接调用 Kotlin，而是 MethodCodec 编码方法名和参数，通过 BinaryMessenger 和 Flutter Engine 发送到原生 Handler，再把结果编码返回 Dart Future。getui_flutter 项目中，Android SDK 原始 payload 完整，但插件传给 MethodChannel 的 Map 字段不全。我沿原生回调、插件映射、Channel 参数和 Dart Handler 定位，补全跨端字段映射并统一 Dart 分发，解决了自定义推送数据丢失问题。

---

## 08. 自测题

1. `setState()` 到屏幕变化，中间经过哪些对象？谁真正负责绘制？
2. Widget rebuild 为什么不等于整页重新创建？
3. 列表排序后，State 为什么会串位？Key 修复什么？
4. `await` 如何暂停和恢复函数？为什么它不创建线程？
5. 为什么 `Future(() => jsonDecode(hugeJson))` 仍可能卡 UI？
6. microtask queue 与 event queue 谁先执行？
7. Provider 为什么不能理解成调用其他组件的 `setState()`？
8. Riverpod 比 `Provider + ChangeNotifier` 多了什么？
9. MethodChannel 的完整链路是什么？
10. getui_flutter 字段缺失问题如何逐层定位？
