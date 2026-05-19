# C 与 ArkTS 通信机制 - 从 Android JNI 视角理解

> **教学目标**：从您熟悉的 Android JNI 出发，理解鸿蒙的 C/C++ 与 ArkTS 通信机制

---

## 📚 第一课：回顾 Android JNI 机制（您已经熟悉的）

### Android 中 Java 调用 Native 的流程

```
┌─────────────────────────────────────────────────────────────┐
│ Java 层                                                      │
│                                                               │
│  public class FFmpegUtils {                                  │
│      static {                                                 │
│          System.loadLibrary("ffmpeg-jni");  // 1️⃣ 加载库      │
│      }                                                        │
│                                                               │
│      public native int executeFFmpeg(String[] cmds);  // 2️⃣声明│
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │ JNI 桥
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C/C++ 层 (ffmpeg-jni.cpp)                                    │
│                                                               │
│  JNIEXPORT jint JNICALL                                       │
│  Java_com_example_FFmpegUtils_executeFFmpeg(                 │
│      JNIEnv* env,                                             │
│      jobject thiz,                                            │
│      jobjectArray cmds) {  // 3️⃣ 实现                         │
│                                                               │
│      // 4️⃣ 转换 Java String[] 为 C char**                     │
│      char** argv = convertJavaStringArray(env, cmds);        │
│                                                               │
│      // 5️⃣ 调用 C 函数                                        │
│      int result = exe_ffmpeg_cmd(argc, argv);                │
│                                                               │
│      return result;                                           │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C 层 (ffmpeg.c)                                              │
│                                                               │
│  int exe_ffmpeg_cmd(int argc, char** argv) {                 │
│      // 执行 FFmpeg 逻辑                                      │
│  }                                                            │
└─────────────────────────────────────────────────────────────┘
```

**关键点**：
- JNI = Java Native Interface（Java 原生接口）
- 需要手写 `JNIEnv*` 的参数转换
- 使用 `System.loadLibrary()` 加载

---

## 📚 第二课：鸿蒙的 aki::JSBind 机制（类似但更简单）

### 鸿蒙中 ArkTS 调用 Native 的流程

```
┌─────────────────────────────────────────────────────────────┐
│ ArkTS 层 (FFMpegUtils.ets)                                   │
│                                                               │
│  import libAddon from 'libffmpegutils.so'  // 1️⃣ 导入库        │
│                                                               │
│  export class FFMpegUtils {                                  │
│      static executeFFmpegCommand(options) {                  │
│          // 2️⃣ 直接调用 C++ 函数                              │
│          libAddon.executeFFmpegCommandAPP(uuid, cmds);       │
│      }                                                        │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │ aki::JSBind 自动桥接
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C++ 层 (napi_ffmpeg.cpp)                                     │
│                                                               │
│  // 3️⃣ 使用 JSBind 宏自动注册                                 │
│  JSBIND_ADDON(ffmpegutils)                                   │
│  JSBIND_GLOBAL() {                                            │
│      JSBIND_PFUNCTION(executeFFmpegCommandAPP);              │
│  }                                                            │
│                                                               │
│  // 4️⃣ 实现函数（参数自动转换！）                             │
│  int executeFFmpegCommandAPP(                                │
│      std::string uuid,              // ✅ 自动从 ArkTS 转换   │
│      int cmdLen,                                             │
│      std::vector<std::string> argv  // ✅ 自动转换数组！      │
│  ) {                                                          │
│      // 5️⃣ 转换为 C 格式                                      │
│      char** argv_c = vector_to_argv(argv);                   │
│                                                               │
│      // 6️⃣ 调用 C 函数                                        │
│      int ret = exe_ffmpeg_cmd(cmdLen, argv_c);               │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C 层 (ffmpeg.c)                                              │
│                                                               │
│  int exe_ffmpeg_cmd(int argc, char** argv) {                 │
│      // 执行 FFmpeg 逻辑                                      │
│  }                                                            │
└─────────────────────────────────────────────────────────────┘
```

**对比 Android JNI**：

| 特性 | Android JNI | 鸿蒙 aki::JSBind |
|------|------------|-----------------|
| 加载库 | `System.loadLibrary()` | `import from '.so'` |
| 函数注册 | 手动命名规则 | `JSBIND_PFUNCTION` 宏 |
| 参数转换 | 手动 `JNIEnv*` | **自动**！|
| 数组转换 | `GetArrayLength`, `GetObjectArrayElement` | **自动转 `std::vector`**！|
| 字符串 | `GetStringUTFChars` | **自动转 `std::string`**！|

**最大优势**：aki::JSBind **自动处理类型转换**！

---

## 📚 第三课：回调机制（从 C 调用回 ArkTS）

### 这是最难理解的部分，我用三步讲解

#### Step 1: Android 中的回调（您熟悉的方式）

```java
// Java 层
public interface FFmpegCallback {
    void onProgress(int progress);
}

public void executeFFmpeg(String[] cmds, FFmpegCallback callback) {
    nativeExecute(cmds, callback);  // 传递回调对象
}

// Native 层
JNIEXPORT void JNICALL Java_xxx_nativeExecute(
    JNIEnv* env, jobject thiz, jobjectArray cmds, jobject callback) {
    
    // 保存全局引用
    jobject globalCallback = env->NewGlobalRef(callback);
    
    // 在需要的时候调用
    jclass cls = env->GetObjectClass(globalCallback);
    jmethodID mid = env->GetMethodID(cls, "onProgress", "(I)V");
    env->CallVoidMethod(globalCallback, mid, 50);  // 调用 onProgress(50)
}
```

**问题**：需要大量 JNI 样板代码！

---

#### Step 2: 鸿蒙的回调机制（更优雅）

**核心思想**：使用 UUID + 函数绑定

```typescript
// ArkTS 层
export class FFMpegUtils {
  static executeFFmpegCommand(options: FFmpegCommandOptions) {
    // 1️⃣ 生成唯一 UUID
    let uuid = "abc123";
    
    // 2️⃣ 绑定回调函数（关键！）
    libAddon.JSBind.bindFunction(
      uuid + "_onFFmpegProgress",      // 键名
      options.onFFmpegProgress          // 函数
    );
    
    // 3️⃣ 将 UUID 传给 C++
    libAddon.executeFFmpegCommandAPP(uuid, cmds);
  }
}
```

```cpp
// C++ 层
int executeFFmpegCommandAPP(std::string uuid, ...) {
    // 4️⃣ 通过 UUID 获取之前绑定的函数
    auto progressFunc = aki::JSBind::GetJSFunction(uuid + "_onFFmpegProgress");
    
    // 5️⃣ 保存到全局变量
    g_callbackInfo.onFFmpegProgress = progressFunc;
    
    // 6️⃣ 在需要的时候调用
    if (g_callbackInfo.onFFmpegProgress) {
        g_callbackInfo.onFFmpegProgress->Invoke<void>(50);  // 传递参数 50
    }
}
```

**类比理解**：
```
UUID = 钥匙串上的标签
bindFunction = 把钥匙挂在钥匙串上
GetJSFunction = 用标签找到钥匙
Invoke = 使用钥匙打开门
```

---

#### Step 3: 完整的回调流程图

```
┌─────────────────────────────────────────────────────────────┐
│ ArkTS 层                                                      │
│                                                               │
│  FFMpegUtils.executeFFmpegCommand({                          │
│      cmds: ['-i', 'input.mp4', 'output.mp4'],               │
│      onFFmpegProgress: (progress) => {       // A. 定义回调   │
│          console.log(`进度: ${progress}%`);                   │
│      }                                                        │
│  });                                                          │
│                                                               │
│  uuid = "abc123"                                             │
│  JSBind.bindFunction("abc123_onFFmpegProgress", A)  // B. 绑定│
│  executeFFmpegCommandAPP("abc123", cmds)            // C. 调用│
└───────────────────────────┬─────────────────────────────────┘
                            │ (C. 传递 UUID)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C++ 层                                                        │
│                                                               │
│  int executeFFmpegCommandAPP(string uuid, ...) {             │
│      // D. 用 UUID 获取函数                                   │
│      auto func = GetJSFunction("abc123_onFFmpegProgress");  │
│                                                               │
│      g_callbackInfo.onFFmpegProgress = func;  // E. 保存      │
│                                                               │
│      // F. 构建 C 回调                                        │
│      Callbacks callbacks = {                                 │
│          .onFFmpegProgress = onFFmpegProgress_Bridge         │
│      };                                                       │
│                                                               │
│      exe_ffmpeg_cmd(..., &callbacks);  // G. 传递给 C         │
│  }                                                            │
│                                                               │
│  void onFFmpegProgress_Bridge(int progress) {  // H. 桥接函数 │
│      g_callbackInfo.onFFmpegProgress->Invoke<void>(progress);│
│      // ↑ 这里调用了 ArkTS 的函数 A！                         │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │ (G. 传递 C 函数指针)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ C 层                                                          │
│                                                               │
│  int exe_ffmpeg_cmd(..., Callbacks* callbacks) {             │
│      g_callbacks = callbacks;  // I. 保存指针                 │
│                                                               │
│      // 在 FFmpeg 执行过程中...                               │
│      if (g_callbacks->onFFmpegProgress) {                    │
│          g_callbacks->onFFmpegProgress(50);  // J. 调用桥接   │
│      }                                                        │
│  }                                                            │
└─────────────────────────────────────────────────────────────┘
```

**调用链**：
```
C 层调用 → C++ 桥接函数 → Invoke ArkTS 函数 → 执行用户回调
```

---

## 📚 第四课：为什么需要三层？

### 类比：快递配送系统

```
┌──────────────┐
│ 客户 (ArkTS) │  "我要寄快递"
└──────┬───────┘
       │
       ↓ 下单（TypeScript）
┌──────────────┐
│ 快递公司     │  "收到订单，转交给仓库"
│ (C++ 层)     │  - 翻译订单格式
│              │  - 分配快递员
└──────┬───────┘
       │
       ↓ 派单（函数指针）
┌──────────────┐
│ 仓库工人     │  "开始打包、运输"
│ (C 层 FFmpeg)│  - 实际执行FFmpeg
└──────┬───────┘
       │
       ↓ 进度通知
┌──────────────┐
│ 快递公司     │  "通知客户进度"
│ (C++ 层)     │  - 50% 已打包
└──────┬───────┘  - 100% 已送达
       │
       ↓ 推送消息
┌──────────────┐
│ 客户 (ArkTS) │  "收到通知"
└──────────────┘
```

### 每一层的职责

| 层 | 作用 | 类比 |
|----|------|------|
| **ArkTS** | 提供易用的 API | 客户下单界面 |
| **C++** | 类型转换、回调桥接 | 快递公司中转站 |
| **C** | 执行实际逻辑 | 仓库工人 |

**为什么不直接 ArkTS → C？**
- C 不支持面向对象（没有 `std::string`）
- C 不支持函数对象（只有函数指针）
- ArkTS 不能直接调用 C 函数

---

## 📚 第五课：手把手代码走读

### 场景：用户调用视频转换

#### 1️⃣ 用户代码（ArkTS）

```typescript
// 用户写的代码
FFMpegUtils.executeFFmpegCommand({
  cmds: ['-i', 'input.mp4', '-c:v', 'libx264', 'output.mp4'],
  
  onFFmpegProgress: (progress) => {
    console.log(`进度: ${progress}%`);
  },
  
  onFFmpegSuccess: () => {
    console.log('成功！');
  }
});
```

**发生了什么**：
1. 生成 UUID: `"f7a8b2c1"`
2. 绑定函数: 
   - `"f7a8b2c1_onFFmpegProgress"` → `(progress) => console.log(...)`
   - `"f7a8b2c1_onFFmpegSuccess"` → `() => console.log('成功')`
3. 调用 Native: `executeFFmpegCommandAPP("f7a8b2c1", 5, [...])`

---

#### 2️⃣ C++ 层接收（napi_ffmpeg.cpp）

```cpp
int executeFFmpegCommandAPP(
    std::string uuid,                    // "f7a8b2c1"
    int cmdLen,                          // 5
    std::vector<std::string> argv        // ["-i", "input.mp4", ...]
) {
    // 步骤 1: 获取 ArkTS 函数
    g_callbackInfo.onFFmpegProgress = 
        aki::JSBind::GetJSFunction("f7a8b2c1_onFFmpegProgress");
    
    g_callbackInfo.onFFmpegSuccess = 
        aki::JSBind::GetJSFunction("f7a8b2c1_onFFmpegSuccess");
    
    // 步骤 2: 转换参数
    char** argv_c = vector_to_argv(argv);
    // argv_c[0] = "-i"
    // argv_c[1] = "input.mp4"
    // ...
    
    // 步骤 3: 构建 C 回调结构
    Callbacks callbacks = {
        .onFFmpegProgress = onFFmpegProgress,  // 函数指针
        .onFFmpegSuccess = onFFmpegSuccess
    };
    
    // 步骤 4: 调用 C 函数
    int ret = exe_ffmpeg_cmd(5, argv_c, &callbacks);
    
    return ret;
}
```

---

#### 3️⃣ C 层执行（ffmpeg.c）

```c
int exe_ffmpeg_cmd(int argc, char** argv, Callbacks* callbacks) {
    g_callbacks = callbacks;  // 保存回调指针
    
    // ... 初始化 ...
    
    // 开始转码
    transcode();
}

// 在转码过程中
void print_report(...) {
    // 计算进度
    int progress = (current_time * 100) / total_duration;
    // progress = 50
    
    // 调用回调
    if (g_callbacks && g_callbacks->onFFmpegProgress) {
        g_callbacks->onFFmpegProgress(50);  // ← 调用 C++ 函数
    }
}
```

---

#### 4️⃣ C++ 桥接函数（napi_ffmpeg.cpp）

```cpp
void onFFmpegProgress(int progress) {  // ← C 层调用到这里
    if (g_callbackInfo.onFFmpegProgress) {
        // 调用 ArkTS 函数
        g_callbackInfo.onFFmpegProgress->Invoke<void>(progress);
        //                                              ↑
        //                                          传递 50
    }
}
```

---

#### 5️⃣ 回到 ArkTS（用户代码）

```typescript
onFFmpegProgress: (progress) => {  // ← 这个函数被调用了！
    console.log(`进度: ${progress}%`);
    // 输出: 进度: 50%
}
```

---

## 🎯 总结：关键概念

### 1. UUID 机制

```
UUID 就像一个临时的"通话频道"

ArkTS: "我在频道 abc123 等着，有进度就告诉我"
C++:   "好的，我记住了 abc123"
C++:   (执行到 50%) "喂？abc123 频道吗？进度 50% 了"
ArkTS: "收到！"
```

### 2. JSBind vs JNI

| 对比项 | JNI (Android) | JSBind (鸿蒙) |
|--------|--------------|--------------|
| 学习曲线 | 陡峭 ⛰️ | 平缓 📈 |
| 类型转换 | 手动写 😓 | 自动 ✅ |
| 回调机制 | GlobalRef + MethodID 😵 | UUID + Invoke 😊 |
| 代码量 | 多 📚 | 少 📄 |

### 3. 三层职责清晰

```
ArkTS:  UI 友好，Promise 风格
   ↕️
C++:    类型翻译官 + 回调中转站
   ↕️
C:      执行实际工作（FFmpeg）
```

---

## ✅ 检查理解

**问题 1**：为什么需要 UUID？

<details>
<summary>答案</summary>

因为可能有多个并发调用，每个调用都有自己的回调函数。UUID 确保回调不会混淆。

类比：多个客户同时寄快递，需要订单号区分。
</details>

**问题 2**：`vector_to_argv` 做什么用？

<details>
<summary>答案</summary>

将 C++ 的 `std::vector<std::string>` 转换为 C 的 `char**`。

因为 FFmpeg 是 C 代码，不认识 C++ 类型。
</details>

**问题 3**：回调是同步还是异步？

<details>
<summary>答案</summary>

在我们的实现中是**同步**的。

C 层调用 → C++ → ArkTS，整个过程阻塞等待。

如果需要异步，可以在 C++ 层创建新线程。
</details>

---

## 🎓 课后作业

1. 阅读 `napi_ffmpeg.cpp` 中的 `executeFFmpegCommandAPP` 函数
2. 找出函数中的这几步：
   - 获取 JSFunction
   - 转换参数
   - 调用 C 函数
   - 调用回调
3. 尝试添加一个新的回调：`onFFmpegLog(string message)`

---

**还有哪里不清楚的吗？** 我可以用更多的例子或图示来解释！
