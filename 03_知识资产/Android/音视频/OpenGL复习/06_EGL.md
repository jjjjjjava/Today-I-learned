# EGL 与上屏：桥接 · Context/TLS · 双三缓冲

> 前置知识：第①②篇（Surface、BufferQueue、FBO）
> 难度：进阶（复习）
> 预计阅读时间：8 分钟

---

## 上一篇思考题复盘（04 篇）

| 题 | 答案 |
|---|---|
| 1 1000×500 进 1080×1920 | videoRatio=2 > screenRatio=0.56 → 视频更扁 → **压高度，黑边在上下** |
| 2 不开 BLEND 为何失效 | 不开混合，src 直接覆盖 dst。开后 α=0.5：`final = src×0.5 + dst×0.5` |
| 3 平移量为何再乘 m[5] | 平移在**世界坐标**算，但矩阵第 4 列作用在 **NDC**；m[5] 把世界压进 NDC，平移量要同步压才对得上手指 |

> 第 3 题是你总结里唯一没提的点（你只说「改第四列」），是这一节的关键陷阱，记一下。

## ??? 解答

> 上一篇无 `???`，跳过。

---

## 正文内容

OpenGL 只管「指挥 GPU 出图」，**不知道结果放哪、给谁显示**。EGL 就是补这个缺口的。

### 一、EGL 的双重职责 + 四大对象

> OpenGL 跨平台，窗口系统平台特定 → 中间必须有 EGL 适配。它有**两个**职责，不只一个：

| 职责 | 对象 | 一句话 |
|---|---|---|
| ① 桥接窗口系统 | **EGLDisplay** | 显示设备抽象，本质是 App↔SurfaceFlinger 的 IPC 连接 |
| | **EGLConfig** | 渲染格式（RGBA 位数、深度位数…） |
| | **EGLSurface** | 渲染目标，封装原生 Surface → 给 OpenGL 一个平台无关的口 |
| ② 替 OpenGL 管 Context | **EGLContext** | OpenGL 的**状态 + 资源池**，不是桥，是 OpenGL 自身需求，EGL 代管 |

> 关键纠偏：很多人以为 EGL 只是「告诉 OpenGL 渲染放哪、给谁显示」（前三个对象）。其实 **EGLContext 是第二条线**——OpenGL 的状态和资源（着色器、纹理、FBO）必须隔离管理，但 OpenGL 自己没法跨平台管，所以由 EGL 代管。

### 二、eglMakeCurrent + TLS：无参数的 glDrawArrays 怎么知道画到哪

`glDrawArrays()` 没有任何参数说「画到哪个 Surface」，它怎么不画错？靠 **TLS（线程局部存储）**：

```
eglMakeCurrent(display, draw, read, context)
 → 把 (display, context, draw/read surface) 存进【当前线程】的 TLS
 → 之后任何 GL API：先从 TLS 取 context → 拿到它的状态/资源/渲染目标
```

这一步解释两件事：

| 现象 | 原因 |
|---|---|
| 两个 GLSurfaceView 不画错 | 各自渲染线程的 TLS 存着各自的 {context, surface}，互不干扰 |
| **GL API 必须在 GL 线程调** | 别的线程 TLS 为空 → 找不到 context → 找不到资源 → 出错/崩溃 |

> 一句话：**eglMakeCurrent 把「渲染环境」绑到当前线程；GL API 全靠当前线程的 TLS 找目标和资源。**

### 三、eglSwapBuffers + 双 / 三缓冲 + VSync

- **eglSwapBuffers 作用**：把后缓冲（刚渲染好的 GraphicBuffer）提交，Binder 通知 SurfaceFlinger 消费上屏，再拿一个空闲 buffer 给 GPU 接着画。

| 机制 | 解决什么 |
|---|---|
| **双缓冲** | 前缓冲显示 + 后缓冲渲染，交换。避免**画面撕裂**（否则显示器读到半旧半新） |
| **三缓冲** | 双缓冲下「前缓冲没释放、后缓冲已用完」会**阻塞 GPU** → 加一个备用 buffer，GPU 不空等 |
| **VSync** | 显示器扫完一帧发的同步信号；swap 等 VSync 再交换，进一步防撕裂 |

> 完整一帧：`glDrawArrays` 渲染进 GraphicBuffer → `eglSwapBuffers`（queueBuffer + Binder 通知）→ SurfaceFlinger 等 VSync → 合成所有 Layer → 上屏。

### 四、你的疑问：输出是 FBO 纹理，还 eglSwapBuffers 吗？

**不 swap。** `eglSwapBuffers` 只对**窗口型 EGLSurface**有意义——它把后缓冲交给 BufferQueue 的消费者。FBO 不是 EGLSurface，没有消费者。

| 输出目标 | 结果去哪 | 收尾动作 |
|---|---|---|
| 屏幕 Surface（FBO0） | BufferQueue → SurfaceFlinger | **eglSwapBuffers** 上屏 |
| 编码器 input Surface | BufferQueue → MediaCodec | **eglSwapBuffers** 提交给编码器 |
| 自定义 FBO 的纹理 | 留在 GPU 显存的纹理里 | **不 swap**；用 `glFinish`/fence 确保渲染完，再 ①当下一 pass 输入 / ②`glReadPixels` 读回 / ③最后切回 FBO0 再 swap 上屏 |

> 一句话：**swap = 把帧交给 BufferQueue 消费者；FBO 没有消费者、结果是纹理，所以不 swap。** 正好呼应你笔记那句「OpenGL 输出去哪取决于当前绑定的 framebuffer」——绑 FBO0 / input Surface 才进 BufferQueue，绑自定义 FBO 就只进纹理。

---

### 全课收口（四篇一条线）

```
解码帧 → [①管线 把帧变像素] → [②SurfaceTexture/OES 零拷贝喂纹理]
      → [③矩阵 摆正/平移/缩放 + 混合] → [④EGL 绑线程/提交/上屏] → 屏幕
```

模块四到此，大纲 12 项全部覆盖。下一篇是**评估篇**：只复盘本篇思考题、不加新内容，作为收尾确认，之后自动生成总结。

## 思考题

1. `glDrawArrays()` 不带「目标 Surface」参数，它最终画到哪由什么决定？
2. EGLContext 为什么说「不是桥，是 OpenGL 自身的需求」？它装的是什么？
3. 只有双缓冲、没有三缓冲时，什么情况会让 GPU 卡住等待？三缓冲怎么救？

## 你的反馈

> 写下问题/感悟，或用 `???你的困惑` 就地标注。读完回「我读完了」，我出评估篇收尾。
>1. 去除掉多余的代码后果然很清爽
>2. 我们只要知道：EGL的作用：egl有四大组件：eglDisplay是对显示设备的封装，eglConfig，显示配置，位数，色深。eglSurface。eglContext。egl有两大职责：1. openGL是系统无关的，win10上有，Android上也有，而win10系统和Android系统底层的窗口什么的都不一致，我们需要一个系统无关层做封装，向上层OpenGL提供统一的能力。所以这就是他的第一个作用。里面主要封装了Android系统的显示设备，Surface。以及config  第二大作用：存储openGL上下文。openGL不能自己管理自己，我们需要一个助理让我们可以在Adnroid系统中管理他。这个就是eglContext，记录：OpenGL用的着色器，纹理，Surface等资源。我们通过eglmakecurrent，将其绑定到当前线程的tls中。也就是线程本地缓存中。这也就是为什么，我们的openGL在非gl线程中执行时会崩溃，也是：为什么我们不同的gl线程直接珍惜gldrawArrays，他就知道怎么绘制，依赖的纹理是什么
>3. eglSwapBuffers。我们当前的存储是Surface的时候，通过eglSwapBuffers。我们会将其queue到BufferQueue中，然后Binder和SurfaceFlinger通信，等Vsync信号到来时，SurfaceFlinger会dequeu一个，然后acquire，将其数据交给hwc硬件混合输出，最后显示上屏，自身则是relese这个buffer。
>4. 那么如果我们不是surface，输出对象是FBO的纹理对象呢？我们还是eglSwap吗？
>
