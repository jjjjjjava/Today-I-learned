# Android 音视频 OpenGL · 复习总结

> 主线一句话：**解码出的帧，如何经 GPU 渲染/处理，最终上屏。**
> 本总结按「业务场景 → 引出的概念 → 处理逻辑」组织——每一节都是一个真实问题逼出一组概念。

---

## 知识图谱：5 个业务场景串起全部概念

### 场景 1 · 把一帧画到屏幕上

| 引出的概念 | 处理逻辑 |
|---|---|
| 为什么是 GPU | 渲染本质 = 逐像素算 RGB（YUV→RGB 是加减乘除）。1080p×60fps 上亿次简单运算，是 GPU（数千核并行）的主场，不是 CPU 的 |
| OpenGL ES | CPU 指挥 GPU 的跨平台 API；GLSL = 写着色器的语言；着色器 = 跑在 GPU 上的程序 |
| 渲染管线（骨架） | 顶点处理 → 图元装配（三角形）→ **光栅化（切片元 + 插值算纹理坐标）** → 片元着色器（采样取色）→ 测试混合 → 写帧缓冲 → 上屏 |
| 三大坐标系 | 屏幕(左上/Y下/像素)、NDC(中心/Y上/[-1,1])、纹理([0,1])。顶点坐标定「画哪」，纹理坐标定「取什么色」，光栅化插值把两者逐像素对应 |
| 三类变量 | attribute（逐顶点）、uniform（全局常量）、varying（顶点→片元，自动插值） |

> 核心洞察：**少量顶点 + 一张纹理 + 光栅化插值**，就能填满百万像素——这是 GPU 的价值，也是「不能逐像素存死颜色」的原因。

### 场景 2 · 渲染的不是单图，而是视频流

| 引出的概念 | 处理逻辑 |
|---|---|
| 性能墙 | 视频帧 8MB×60fps，每帧 `texImage2D` 拷贝会吃光 16ms 预算 → 必须零拷贝 |
| 零拷贝三件套 | **BufferQueue**（共享图形内存）+ **SurfaceTexture**（consumer 端，挂到纹理 ID）+ **OES 外部纹理**（接 YUV/私有格式） |
| 数据流 | 纹理ID → SurfaceTexture(consumer) → Surface(producer) → config 给 MediaCodec → 解码 dequeue/queueBuffer → onFrameAvailable → `updateTexImage` **换指针**指向最新帧 |
| 输出侧 | GLSurfaceView 的 Surface 承接 RGB 后处理结果 → SurfaceFlinger（Binder 通知）→ HWC 合成上屏 |

> 核心洞察：`updateTexImage` ≠ `texImage2D`——前者**换指向**（零拷贝），后者**搬数据**。

### 场景 3 · 视频别拉伸，还要能拖、缩、叠

| 引出的概念 | 处理逻辑 |
|---|---|
| 拉伸根因 | NDC 无脑铺满，OpenGL 不知道视频原始比例 |
| 正交矩阵摆正 | 比 videoRatio 与 screenRatio：更扁压高度、更高压宽度（正交矩阵本质=缩放矩阵，m[0]/m[5]） |
| 矩阵 CPU→GPU | CPU 算矩阵 → glUniformMatrix4fv 当 uniform 上传 → 顶点着色器 `gl_Position = uMatrix * aPosition` |
| 缩放/平移 | 缩放改对角（累乘）；平移改第 4 列，**平移量要乘投影系数 m[5]**（世界坐标→NDC 同步压缩） |
| 半透明 | 不开混合则上层全覆盖；`glEnable(GL_BLEND)` + blendFunc，公式 `final = src×α + dst×(1−α)`；绘制顺序=层叠顺序 |

### 场景 4 · 多级滤镜 / 离屏后处理

| 引出的概念 | 处理逻辑 |
|---|---|
| FBO 本质 | 一组**附件挂载点**（关键是颜色附件），自身不存像素 |
| FBO0 vs 自定义 FBO | FBO0 颜色附件=Surface（上屏，不可再采样）；自定义 FBO 颜色附件=纹理（离屏，可当下道输入） |
| 多级原理 | 把上一次渲染结果存成纹理，喂给下一次 → 滤镜串成流水线 |
| 纹理系统底层 | 纹理对象（存数据）/ 纹理 id（句柄，当 fd）/ 纹理单元（GPU 工位，有限）/ 纹理类型（2D vs OES，数据结构不同）。GPU 从「单元的某类型槽」取，实际取到的是绑定的纹理对象 |

### 场景 5 · 渲染结果交给谁、怎么不撕裂、怎么不崩

| 引出的概念 | 处理逻辑 |
|---|---|
| EGL 双重职责 | ① 跨平台桥接窗口系统；② 替 OpenGL 管理 Context |
| 四大对象 | EGLDisplay(显示设备/IPC 连 SF)、EGLConfig(格式)、EGLSurface(封装原生 Surface)、EGLContext(OpenGL 状态+资源池) |
| makeCurrent + TLS | `eglMakeCurrent` 把环境绑进当前线程 TLS；GL API 靠 TLS 定位目标与资源 → 解释「多窗口不画错」「非 GL 线程崩溃」 |
| swap + 缓冲 | `eglSwapBuffers` 把后缓冲交给 BufferQueue 消费者；双缓冲防撕裂、三缓冲防 GPU 阻塞、VSync 同步交换 |
| 边界 | **FBO 输出是纹理、无消费者 → 不 swap**；编码器 input Surface 是窗口型 EGLSurface → 要 swap |

---

## 大纲掌握项复盘（12/12 ✅）

**模块一 · 渲染基础**：GPU/OpenGL 角色 ✅、渲染管线+光栅化插值 ✅、三大坐标系 ✅、着色器与三类变量 ✅
**模块二 · 渲染视频**：图片vs视频上传 ✅、SurfaceTexture+OES+updateTexImage 零拷贝 ✅、FBO 作用（含本质与 FBO0/自定义差异）✅
**模块三 · 矩阵与画中画**：正交矩阵摆正+判方向 ✅、矩阵 CPU→GPU ✅、半透明混合 ✅、平移/缩放矩阵+乘投影系数 ✅
**模块四 · EGL 与上屏**：双职责+四大对象 ✅、makeCurrent+TLS+GL 线程 ✅、swap+双/三缓冲+VSync（含 FBO 不 swap 边界）✅

---

## 几处关键纠偏（复习中踩过/问过的点）

1. **updateTexImage 是换指针不是上传**——零拷贝的核心，纹理对象内部指针指向最新 GraphicBuffer。
2. **sampler 里的 0 是工位号不是纹理 id**——`glUniform1i(uTexture, 0)` 指的是 0 号纹理单元。
3. **平移量要乘 m[5]**——世界坐标的平移要同步压进 NDC 才对得上手指。
4. **FBO 输出不 swap**——swap 只对窗口型 EGLSurface（屏幕/编码器 input Surface）有意义。
5. **「GL 线程」不是特殊线程**——调用过 `eglMakeCurrent` 绑了 context 的线程就是 GL 线程；`GLSurfaceView` 内部替你做了这步。

---

## 遗留与延伸方向

- **已澄清**：「什么是 GL 线程 / 怎么造 GL 线程」——见上方纠偏第 5 条；手动造 GL 线程即笔记④「手动管理 EGL」路径（建 Display/Config/Context/Surface → 自己线程 makeCurrent）。
- **可延伸（不在本课范围）**：
  - 编码端闭环：`encoder.createInputSurface()` + OpenGL 画到 input Surface → 重新编码 → MediaMuxer（加水印/转码全链路）。
  - 通用图形学：模型/视图/透视投影、光照（本课只到 2D 视频所需的正交变换）。
  - 具体滤镜算法：高斯模糊、LUT、美颜的 shader 实现与多 pass 优化。
  - OpenGL ES 3.0+：VAO/VBO、UBO、Transform Feedback。

---

> 这门课把你 4 篇笔记重构成「5 个业务场景 → 概念 → 处理逻辑」的一条主线。下一站若继续音视频，建议接 **编码端（createInputSurface 闭环）** 或 **采集端（Camera2 + OES）**，正好能复用本课的 OES/Surface/EGL 全套。
