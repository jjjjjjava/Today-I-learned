override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
}

override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
}

override fun onDrawFrame(gl: GL10?) {
}


const val FLAG_RECORDABLE = 0x01

private const val EGL_RECORDABLE_ANDROID = 0x3142

class EGLCore {

    private val TAG = "EGLCore"

    // EGL相关变量
    private var mEGLDisplay: EGLDisplay = EGL14.EGL_NO_DISPLAY
    private var mEGLContext = EGL14.EGL_NO_CONTEXT
    private var mEGLConfig: EGLConfig? = null

    /**
     * 初始化EGLDisplay
     * @param eglContext 共享上下文
     */
    fun init(eglContext: EGLContext?, flags: Int) {
        if (mEGLDisplay !== EGL14.EGL_NO_DISPLAY) {
            throw RuntimeException("EGL already set up")
        }

        val sharedContext = eglContext ?: EGL14.EGL_NO_CONTEXT

        // 1，创建 EGLDisplay
        mEGLDisplay = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY)
        if (mEGLDisplay === EGL14.EGL_NO_DISPLAY) {
            throw RuntimeException("Unable to get EGL14 display")
        }

        // 2，初始化 EGLDisplay
        val version = IntArray(2)
        if (!EGL14.eglInitialize(mEGLDisplay, version, 0, version, 1)) {
            mEGLDisplay = EGL14.EGL_NO_DISPLAY
            throw RuntimeException("unable to initialize EGL14")
        }

        // 3，初始化EGLConfig，EGLContext上下文
        if (mEGLContext === EGL14.EGL_NO_CONTEXT) {
            val config = getConfig(flags, 2) ?: throw RuntimeException("Unable to find a suitable EGLConfig")
            val attr2List = intArrayOf(EGL14.EGL_CONTEXT_CLIENT_VERSION, 2, EGL14.EGL_NONE)
            val context = EGL14.eglCreateContext(
                mEGLDisplay, config, sharedContext,
                attr2List, 0
            )
            mEGLConfig = config
            mEGLContext = context
        }
    }

    /**
     * 获取EGL配置信息
     * @param flags 初始化标记
     * @param version EGL版本
     */
    private fun getConfig(flags: Int, version: Int): EGLConfig? {
        var renderableType = EGL14.EGL_OPENGL_ES2_BIT
        if (version >= 3) {
            // 配置EGL 3
            renderableType = renderableType or EGLExt.EGL_OPENGL_ES3_BIT_KHR
        }

        // 配置数组，主要是配置RAGA位数和深度位数
        // 两个为一对，前面是key，后面是value
        // 数组必须以EGL14.EGL_NONE结尾
        val attrList = intArrayOf(
            EGL14.EGL_RED_SIZE, 8,
            EGL14.EGL_GREEN_SIZE, 8,
            EGL14.EGL_BLUE_SIZE, 8,
            EGL14.EGL_ALPHA_SIZE, 8,
            //EGL14.EGL_DEPTH_SIZE, 16,
            //EGL14.EGL_STENCIL_SIZE, 8,
            EGL14.EGL_RENDERABLE_TYPE, renderableType,
            EGL14.EGL_NONE, 0, // placeholder for recordable [@-3]
            EGL14.EGL_NONE
        )
        //配置Android指定的标记
        if (flags and FLAG_RECORDABLE != 0) {
            attrList[attrList.size - 3] = EGL_RECORDABLE_ANDROID
            attrList[attrList.size - 2] = 1
        }
        val configs = arrayOfNulls<EGLConfig>(1)
        val numConfigs = IntArray(1)

        //获取可用的EGL配置列表
        if (!EGL14.eglChooseConfig(mEGLDisplay, attrList, 0,
                configs, 0, configs.size,
                numConfigs, 0)) {
            Log.w(TAG, "Unable to find RGB8888 / $version EGLConfig")
            return null
        }
        
        //使用系统推荐的第一个配置
        return configs[0]
    }

    /**
     * 创建可显示的渲染缓存
     * @param surface 渲染窗口的surface
     */
    fun createWindowSurface(surface: Any): EGLSurface {
        if (surface !is Surface && surface !is SurfaceTexture) {
            throw RuntimeException("Invalid surface: $surface")
        }

        val surfaceAttr = intArrayOf(EGL14.EGL_NONE)

        val eglSurface = EGL14.eglCreateWindowSurface(
                                        mEGLDisplay, mEGLConfig, surface,
                                        surfaceAttr, 0)

        if (eglSurface == null) {
            throw RuntimeException("Surface was null")
        }

        return eglSurface
    }

    /**
     * 创建离屏渲染缓存
     * @param width 缓存窗口宽
     * @param height 缓存窗口高
     */
    fun createOffscreenSurface(width: Int, height: Int): EGLSurface {
        val surfaceAttr = intArrayOf(EGL14.EGL_WIDTH, width,
                                                 EGL14.EGL_HEIGHT, height,
                                                 EGL14.EGL_NONE)

        val eglSurface = EGL14.eglCreatePbufferSurface(
                                        mEGLDisplay, mEGLConfig,
                                        surfaceAttr, 0)

        if (eglSurface == null) {
            throw RuntimeException("Surface was null")
        }

        return eglSurface
    }

    /**
     * 将当前线程与上下文进行绑定
     */
    fun makeCurrent(eglSurface: EGLSurface) {
        if (mEGLDisplay === EGL14.EGL_NO_DISPLAY) {
            throw RuntimeException("EGLDisplay is null, call init first")
        }
        if (!EGL14.eglMakeCurrent(mEGLDisplay, eglSurface, eglSurface, mEGLContext)) {
            throw RuntimeException("makeCurrent(eglSurface) failed")
        }
    }

    /**
     * 将当前线程与上下文进行绑定
     */
    fun makeCurrent(drawSurface: EGLSurface, readSurface: EGLSurface) {
        if (mEGLDisplay === EGL14.EGL_NO_DISPLAY) {
            throw RuntimeException("EGLDisplay is null, call init first")
        }
        if (!EGL14.eglMakeCurrent(mEGLDisplay, drawSurface, readSurface, mEGLContext)) {
            throw RuntimeException("eglMakeCurrent(draw,read) failed")
        }
    }

    /**
     * 将缓存图像数据发送到设备进行显示
     */
    fun swapBuffers(eglSurface: EGLSurface): Boolean {
        return EGL14.eglSwapBuffers(mEGLDisplay, eglSurface)
    }

    /**
     * 设置当前帧的时间，单位：纳秒
     */
    fun setPresentationTime(eglSurface: EGLSurface, nsecs: Long) {
        EGLExt.eglPresentationTimeANDROID(mEGLDisplay, eglSurface, nsecs)
    }

    /**
     * 销毁EGLSurface，并解除上下文绑定
     */
    fun destroySurface(elg_surface: EGLSurface) {
        EGL14.eglMakeCurrent(
            mEGLDisplay, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_SURFACE,
            EGL14.EGL_NO_CONTEXT
        )
        EGL14.eglDestroySurface(mEGLDisplay, elg_surface);
    }

    /**
     * 释放资源
     */
    fun release() {
        if (mEGLDisplay !== EGL14.EGL_NO_DISPLAY) {
            // Android is unusual in that it uses a reference-counted EGLDisplay.  So for
            // every eglInitialize() we need an eglTerminate().
            EGL14.eglMakeCurrent(
                mEGLDisplay, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_SURFACE,
                EGL14.EGL_NO_CONTEXT
            )
            EGL14.eglDestroyContext(mEGLDisplay, mEGLContext)
            EGL14.eglReleaseThread()
            EGL14.eglTerminate(mEGLDisplay)
        }

        mEGLDisplay = EGL14.EGL_NO_DISPLAY
        mEGLContext = EGL14.EGL_NO_CONTEXT
        mEGLConfig = null
    }
}


class EGLSurfaceHolder {

    private val TAG = "EGLSurfaceHolder"

    private lateinit var mEGLCore: EGLCore

    private var mEGLSurface: EGLSurface? = null

    fun init(shareContext: EGLContext? = null, flags: Int) {
        mEGLCore = EGLCore()
        mEGLCore.init(shareContext, flags)
    }

    fun createEGLSurface(surface: Any?, width: Int = -1, height: Int = -1) {
        mEGLSurface = if (surface != null) {
            mEGLCore.createWindowSurface(surface)
        } else {
            mEGLCore.createOffscreenSurface(width, height)
        }
    }

    fun makeCurrent() {
        if (mEGLSurface != null) {
            mEGLCore.makeCurrent(mEGLSurface!!)
        }
    }

    fun swapBuffers() {
        if (mEGLSurface != null) {
            mEGLCore.swapBuffers(mEGLSurface!!)
        }
    }

    fun destroyEGLSurface() {
        if (mEGLSurface != null) {
            mEGLCore.destroySurface(mEGLSurface!!)
            mEGLSurface = null
        }
    }

    fun release() {
        mEGLCore.release()
    }
}


class CustomerGLRenderer : SurfaceHolder.Callback {

    //OpenGL渲染线程
    private val mThread = RenderThread()

    //页面上的SurfaceView弱引用
    private var mSurfaceView: WeakReference<SurfaceView>? = null

    //所有的绘制器
    private val mDrawers = mutableListOf<IDrawer>()

    init {
        //启动渲染线程
        mThread.start()
    }
    
    /**
     * 设置SurfaceView
     */
    fun setSurface(surface: SurfaceView) {
        mSurfaceView = WeakReference(surface)
        surface.holder.addCallback(this)

        surface.addOnAttachStateChangeListener(object : View.OnAttachStateChangeListener{
            override fun onViewDetachedFromWindow(v: View?) {
                mThread.onSurfaceStop()
            }

            override fun onViewAttachedToWindow(v: View?) {
            }
        })
    }

    /**
     * 添加绘制器
     */
    fun addDrawer(drawer: IDrawer) {
        mDrawers.add(drawer)
    }

    override fun surfaceCreated(holder: SurfaceHolder?) {
        mThread.onSurfaceCreate()
    }

    override fun surfaceChanged(holder: SurfaceHolder?, format: Int, width: Int, height: Int) {
        mThread.onSurfaceChange(width, height)
    }

    override fun surfaceDestroyed(holder: SurfaceHolder?) {
        mThread.onSurfaceDestroy()
    }
}

/**
 * 渲染状态
 */
enum class RenderState {
    NO_SURFACE, //没有有效的surface
    FRESH_SURFACE, //持有一个未初始化的新的surface
    SURFACE_CHANGE, // surface尺寸变化
    RENDERING, //初始化完毕，可以开始渲染
    SURFACE_DESTROY, //surface销毁
    STOP //停止绘制
}


inner class RenderThread: Thread() {
    
    // 渲染状态
    private var mState = RenderState.NO_SURFACE
    
    private var mEGLSurface: EGLSurfaceHolder? = null

    // 是否绑定了EGLSurface
    private var mHaveBindEGLContext = false

    //是否已经新建过EGL上下文，用于判断是否需要生产新的纹理ID
    private var mNeverCreateEglContext = true

    private var mWidth = 0
    private var mHeight = 0

    private val mWaitLock = Object()

//------------第1部分：线程等待与解锁-----------------

    private fun holdOn() {
        synchronized(mWaitLock) {
            mWaitLock.wait()
        }
    }

    private fun notifyGo() {
        synchronized(mWaitLock) {
            mWaitLock.notify()
        }
    }

//------------第2部分：Surface声明周期转发函数------------

    fun onSurfaceCreate() {
        mState = RenderState.FRESH_SURFACE
        notifyGo()
    }

    fun onSurfaceChange(width: Int, height: Int) {
        mWidth = width
        mHeight = height
        mState = RenderState.SURFACE_CHANGE
        notifyGo()
    }

    fun onSurfaceDestroy() {
        mState = RenderState.SURFACE_DESTROY
        notifyGo()
    }

    fun onSurfaceStop() {
        mState = RenderState.STOP
        notifyGo()
    }

//------------第3部分：OpenGL渲染循环------------

    override fun run() {
        // 【1】初始化EGL
        initEGL()
        while (true) {
            when (mState) {
                RenderState.FRESH_SURFACE -> {
                    //【2】使用surface初始化EGLSurface，并绑定上下文
                    createEGLSurfaceFirst()
                    holdOn()
                }
                RenderState.SURFACE_CHANGE -> {
                    createEGLSurfaceFirst()
                    //【3】初始化OpenGL世界坐标系宽高
                    GLES20.glViewport(0, 0, mWidth, mHeight)
                    configWordSize()
                    mState = RenderState.RENDERING
                }
                RenderState.RENDERING -> {
                    //【4】进入循环渲染
                    render()
                }
                RenderState.SURFACE_DESTROY -> {
                    //【5】销毁EGLSurface，并解绑上下文
                    destroyEGLSurface()
                    mState = RenderState.NO_SURFACE
                }
                RenderState.STOP -> {
                    //【6】释放所有资源
                    releaseEGL()
                    return
                }
                else -> {
                    holdOn()
                }
            }
            sleep(20)
        }
    }

//------------第4部分：EGL相关操作------------

    private fun initEGL() {
        mEGLSurface = EGLSurfaceHolder()
        mEGLSurface?.init(null, EGL_RECORDABLE_ANDROID)
    }

    private fun createEGLSurfaceFirst() {
        if (!mHaveBindEGLContext) {
            mHaveBindEGLContext = true
            createEGLSurface()
            if (mNeverCreateEglContext) {
                mNeverCreateEglContext = false
                generateTextureID()
            }
        }
    }

    private fun createEGLSurface() {
        mEGLSurface?.createEGLSurface(mSurfaceView?.get()?.holder?.surface)
        mEGLSurface?.makeCurrent()
    }

    private fun destroyEGLSurface() {
        mEGLSurface?.destroyEGLSurface()
        mHaveBindEGLContext = false
    }

    private fun releaseEGL() {
        mEGLSurface?.release()
    }
    
//------------第5部分：OpenGL ES相关操作-------------

    private fun generateTextureID() {
        val textureIds = OpenGLTools.createTextureIds(mDrawers.size)
        for ((idx, drawer) in mDrawers.withIndex()) {
            drawer.setTextureID(textureIds[idx])
        }
    }

    private fun configWordSize() {
        mDrawers.forEach { it.setWorldSize(mWidth, mHeight) }
    }

    private fun render() {
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT or GLES20.GL_DEPTH_BUFFER_BIT)
        mDrawers.forEach { it.draw() }
        mEGLSurface?.swapBuffers()
    }
}

class SimpleRender: GLSurfaceView.Renderer {

    private val drawers = mutableListOf<IDrawer>()

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        GLES20.glClearColor(0f, 0f, 0f, 0f)
        //开启混合，即半透明
        GLES20.glEnable(GLES20.GL_BLEND)
        GLES20.glBlendFunc(GLES20.GL_SRC_ALPHA, GLES20.GL_ONE_MINUS_SRC_ALPHA)

        val textureIds = OpenGLTools.createTextureIds(drawers.size)
        for ((idx, drawer) in drawers.withIndex()) {
            drawer.setTextureID(textureIds[idx])
        }
    }

    override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
        GLES20.glViewport(0, 0, width, height)
        for (drawer in drawers) {
            drawer.setWorldSize(width, height)
        }
    }

    override fun onDrawFrame(gl: GL10?) {
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT or GLES20.GL_DEPTH_BUFFER_BIT)
        drawers.forEach {
            it.draw()
        }
    }

    fun addDrawer(drawer: IDrawer) {
        drawers.add(drawer)
    }
}

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout
        xmlns:android="http://schemas.android.com/apk/res/android"
        android:layout_width="match_parent"
        android:layout_height="match_parent" xmlns:app="http://schemas.android.com/apk/res-auto">
    <SurfaceView
            android:id="@+id/sfv"
            app:layout_constraintTop_toTopOf="parent"
            android:layout_width="match_parent"
            android:layout_height="match_parent"/>
</android.support.constraint.ConstraintLayout>

class EGLPlayerActivity: AppCompatActivity() {
    private val path = Environment.getExternalStorageDirectory().absolutePath + "/mvtest_2.mp4"
    private val path2 = Environment.getExternalStorageDirectory().absolutePath + "/mvtest.mp4"

    private val threadPool = Executors.newFixedThreadPool(10)

    private var mRenderer = CustomerGLRenderer()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_egl_player)
        initFirstVideo()
        initSecondVideo()
        setRenderSurface()
    }

    private fun initFirstVideo() {
        val drawer = VideoDrawer()
        drawer.setVideoSize(1920, 1080)
        drawer.getSurfaceTexture {
            initPlayer(path, Surface(it), true)
        }
        mRenderer.addDrawer(drawer)
    }

    private fun initSecondVideo() {
        val drawer = VideoDrawer()
        drawer.setAlpha(0.5f)
        drawer.setVideoSize(1920, 1080)
        drawer.getSurfaceTexture {
            initPlayer(path2, Surface(it), false)
        }
        mRenderer.addDrawer(drawer)

        Handler().postDelayed({
            drawer.scale(0.5f, 0.5f)
        }, 1000)
    }

    private fun initPlayer(path: String, sf: Surface, withSound: Boolean) {
        val videoDecoder = VideoDecoder(path, null, sf)
        threadPool.execute(videoDecoder)
        videoDecoder.goOn()

        if (withSound) {
            val audioDecoder = AudioDecoder(path)
            threadPool.execute(audioDecoder)
            audioDecoder.goOn()
        }
    }

    private fun setRenderSurface() {
        mRenderer.setSurface(sfv)
    }
}