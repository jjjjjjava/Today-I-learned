1. 多个颜色附着点（GL_COLOR_ATTACHMENT0、GL_COLOR_ATTACHMENT1...）
2. 一个深度附着点（GL_DEPTH_ATTACHMENT）
3. 一个模板附着点（GL_STENCIL_ATTACHMENT）

fun createFBOTexture(width: Int, height: Int): IntArray {
    // 新建纹理ID
    val textures = IntArray(1)
    GLES20.glGenTextures(1, textures, 0)
    
    // 绑定纹理ID
    GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textures[0])
    
    // 根据颜色参数，宽高等信息，为上面的纹理ID，生成一个2D纹理
    GLES20.glTexImage2D(GLES20.GL_TEXTURE_2D, 0, GLES20.GL_RGBA, width, height,
        0, GLES20.GL_RGBA, GLES20.GL_UNSIGNED_BYTE, null)
        
    // 设置纹理边缘参数
    GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_NEAREST.toFloat())
    GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER,GLES20.GL_LINEAR.toFloat())
    GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S,GLES20.GL_CLAMP_TO_EDGE.toFloat())
    GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T,GLES20.GL_CLAMP_TO_EDGE.toFloat())
    
    // 解绑纹理ID
    GLES20.glBindTexture(GLES20.GL_TEXTURE_2D,0)
    return textures
}


fun createFrameBuffer(): Int {
    val fbs = IntArray(1)
    GLES20.glGenFramebuffers(1, fbs, 0)
    return fbs[0]
}

fun bindFBO(fb: Int, textureId: Int) {
    GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, fb)
    GLES20.glFramebufferTexture2D(GLES20.GL_FRAMEBUFFER, GLES20.GL_COLOR_ATTACHMENT0,
        GLES20.GL_TEXTURE_2D, textureId, 0)
}

fun unbindFBO() {
    GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, GLES20.GL_NONE)
    GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, 0)
}

fun deleteFBO(frame: IntArray, texture:IntArray) {
    //删除Frame Buffer
    GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, GLES20.GL_NONE)
    GLES20.glDeleteFramebuffers(1, frame, 0)
    //删除纹理
    GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, 0)
    GLES20.glDeleteTextures(1, texture, 0)
}

object OpenGLTools {
    fun createFBOTexture(width: Int, height: Int): IntArray {
        // 新建纹理ID
        val textures = IntArray(1)
        GLES20.glGenTextures(1, textures, 0)
        
        // 绑定纹理ID
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textures[0])
        
        // 根据颜色参数，宽高等信息，为上面的纹理ID，生成一个2D纹理
        GLES20.glTexImage2D(GLES20.GL_TEXTURE_2D, 0, GLES20.GL_RGBA, width, height,
            0, GLES20.GL_RGBA, GLES20.GL_UNSIGNED_BYTE, null)
            
        // 设置纹理边缘参数
        GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_NEAREST.toFloat())
        GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER,GLES20.GL_LINEAR.toFloat())
        GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S,GLES20.GL_CLAMP_TO_EDGE.toFloat())
        GLES20.glTexParameterf(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T,GLES20.GL_CLAMP_TO_EDGE.toFloat())
        
        // 解绑纹理ID
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D,0)
        return textures
    }
    
    fun createFrameBuffer(): Int {
        val fbs = IntArray(1)
        GLES20.glGenFramebuffers(1, fbs, 0)
        return fbs[0]
    }
    
    fun bindFBO(fb: Int, textureId: Int) {
        GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, fb)
        GLES20.glFramebufferTexture2D(GLES20.GL_FRAMEBUFFER, GLES20.GL_COLOR_ATTACHMENT0,
            GLES20.GL_TEXTURE_2D, textureId, 0)
    }
    
    fun unbindFBO() {
        GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, GLES20.GL_NONE)
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, 0)
    }
    
    fun deleteFBO(frame: IntArray, texture:IntArray) {
        //删除Frame Buffer
        GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, GLES20.GL_NONE)
        GLES20.glDeleteFramebuffers(1, frame, 0)
        //删除纹理
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, 0)
        GLES20.glDeleteTextures(1, texture, 0)
    }
}


lass SoulVideoDrawer : IDrawer {

    // ......
    
    // 省略和VideoDrawer一样成员变量
    
    // ......

//-------------灵魂出窍相关的变量--------------

    /**上下颠倒的顶点矩阵*/
    private val mReserveVertexCoors = floatArrayOf(
        -1f, 1f,
        1f, 1f,
        -1f, -1f,
        1f, -1f
    )

    private val mDefVertexCoors = floatArrayOf(
        -1f, -1f,
        1f, -1f,
        -1f, 1f,
        1f, 1f
    )

    // 顶点坐标
    private var mVertexCoors = mDefVertexCoors
    
    // 灵魂帧缓冲
    private var mSoulFrameBuffer: Int = -1

    // 灵魂纹理ID
    private var mSoulTextureId: Int = -1

    // 灵魂纹理接收者
    private var mSoulTextureHandler: Int = -1

    // 灵魂缩放进度接收者
    private var mProgressHandler: Int = -1

    // 是否更新FBO纹理
    private var mDrawFbo: Int = 1

    // 更新FBO标记接收者
    private var mDrawFobHandler: Int = -1

    // 一帧灵魂的时间
    private var mModifyTime: Long = -1
    
    override fun draw() {
        if (mTextureId != -1) {
            initDefMatrix()
            //【步骤1: 创建、编译并启动OpenGL着色器】
            createGLPrg()
            
            // -------【步骤2:新增FBO部分】-----
            //【步骤2.1: 更新灵魂纹理】
            updateFBO()
            //【步骤2.2: 激活灵魂纹理单元】
            activateSoulTexture()
            // ---------------------------
            
            //【步骤3: 激活并绑定纹理单元】
            activateDefTexture()
            //【步骤4: 绑定图片到纹理单元】
            updateTexture()
            //【步骤5: 开始渲染绘制】
            doDraw()
        }
    }
    
    // ......
}\


步骤2: 新增FBO部分
- 2.1: 更新灵魂纹理【updateFBO】
- 2.2: 激活灵魂纹理单元【activateSoulTexture】


class SoulVideoDrawer : IDrawer {

    // ......
    
    private fun updateFBO() {
        //【1，创建FBO纹理】
        if (mSoulTextureId == -1) {
            mSoulTextureId = OpenGLTools.createFBOTexture(mVideoWidth, mVideoHeight)
        }
        // 【2，创建FBO】
        if (mSoulFrameBuffer == -1) {
            mSoulFrameBuffer = OpenGLTools.createFrameBuffer()
        }
        // 【3，渲染到FBO】
        if (System.currentTimeMillis() - mModifyTime > 500) {
            mModifyTime = System.currentTimeMillis()
            // 绑定FBO
            OpenGLTools.bindFBO(mSoulFrameBuffer, mSoulTextureId)
            // 配置FBO窗口
            configFboViewport()
            
//--------执行正常画面渲染，画面将渲染到FBO上--------------

            // 激活默认的纹理
            activateDefTexture()
            // 更新纹理
            updateTexture()
            // 绘制到FBO
            doDraw()
            
//---------------------------------------------------

            // 解绑FBO
            OpenGLTools.unbindFBO()
            // 恢复默认绘制窗口
            configDefViewport()
        }
    }

    /**
     * 配置FBO窗口
     */
    private fun configFboViewport() {
        mDrawFbo = 1
        // 将变换矩阵回复为单位矩阵（将画面拉升到整个窗口大小，设置窗口比例和FBO纹理比例一致，画面刚好可以正常绘制到FBO纹理上）
        Matrix.setIdentityM(mMatrix, 0)
        // 设置颠倒的顶点坐标
        mVertexCoors = mReserveVertexCoors
        //重新初始化顶点坐标
        initPos()
        GLES20.glViewport(0, 0, mVideoWidth, mVideoHeight)
        //设置一个颜色状态
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 0.0f)
        //使能颜色状态的值来清屏
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT)
    }

    /**
     * 配置默认显示的窗口
     */
    private fun configDefViewport() {
        mDrawFbo = 0
        mMatrix = null
        // 恢复顶点坐标
        mVertexCoors = mDefVertexCoors
        initPos()
        initDefMatrix()
        // 恢复窗口
        GLES20.glViewport(0, 0, mWorldWidth, mWorldHeight)
    }

    private fun activateDefTexture() {
        activateTexture(GLES11Ext.GL_TEXTURE_EXTERNAL_OES, mTextureId, 0, mTextureHandler)
    }

    private fun activateSoulTexture() {
        activateTexture(GLES11.GL_TEXTURE_2D, mSoulTextureId, 1, mSoulTextureHandler)
    }

    private fun activateTexture(type: Int, textureId: Int, index: Int, textureHandler: Int) {
        //激活指定纹理单元
        GLES20.glActiveTexture(GLES20.GL_TEXTURE0 + index)
        //绑定纹理ID到纹理单元
        GLES20.glBindTexture(type, textureId)
        //将激活的纹理单元传递到着色器里面
        GLES20.glUniform1i(textureHandler, index)
        //配置边缘过渡参数
        GLES20.glTexParameterf(type, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR.toFloat())
        GLES20.glTexParameterf(type, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR.toFloat())
        GLES20.glTexParameteri(type, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE)
        GLES20.glTexParameteri(type, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE)
    }
    
    // ......
}

if (System.currentTimeMillis() - mModifyTime > 500) {
    // 记录时间
    mModifyTime = System.currentTimeMillis()
    // 绑定FBO
    OpenGLTools.bindFBO(mSoulFrameBuffer, mSoulTextureId)
    // 配置FBO窗口
    configFboViewport()
//--------执行正常画面渲染，画面将渲染到FBO上--------------
    // 激活默认的纹理
    activateDefTexture()
    // 更新纹理
    updateTexture()
    // 绘制到FBO
    doDraw()
//---------------------------------------------------
    // 解绑FBO
    OpenGLTools.unbindFBO()
    // 恢复默认绘制窗口
    configDefViewport()
}

private fun configFboViewport() {
    mDrawFbo = 1
    // 将变换矩阵恢复为单位矩阵
    //（将画面拉升到整个窗口大小，
    // 设置窗口宽高和FBO纹理宽高一致，
    // 画面刚好可以正常绘制到FBO绑定的纹理上）
    Matrix.setIdentityM(mMatrix, 0)
    // 设置颠倒的顶点坐标
    mVertexCoors = mReserveVertexCoors
    //重新初始化顶点坐标
    initPos()
    // 设置窗口大小
    GLES20.glViewport(0, 0, mVideoWidth, mVideoHeight)
    //设置一个颜色状态
    GLES20.glClearColor(0.0f, 0.0f, 0.0f, 0.0f)
    //使能颜色状态的值来清屏
    GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT)
}

override fun draw() {
    if (mTextureId != -1) {
        //【步骤1: 创建、编译并启动OpenGL着色器】
        // -------【步骤2:新增FBO部分】-----
        //【步骤2.1: 更新灵魂纹理】
        //【步骤2.2: 激活灵魂纹理单元】
        activateSoulTexture()
        // ---------------------------
        
        //【步骤3: 激活并绑定纹理单元】
        activateDefTexture()
        //【步骤4: 绑定图片到纹理单元】
        updateTexture()
        //【步骤5: 开始渲染绘制】
        doDraw()
    }
}

private fun activateSoulTexture() {
    activateTexture(GLES11.GL_TEXTURE_2D, mSoulTextureId, 1, mSoulTextureHandler)
}

private fun activateTexture(type: Int, textureId: Int, index: Int, textureHandler: Int) {
    //激活指定纹理单元
    GLES20.glActiveTexture(GLES20.GL_TEXTURE0 + index)
    //绑定纹理ID到纹理单元
    GLES20.glBindTexture(type, textureId)
    //将激活的纹理单元传递到着色器里面
    GLES20.glUniform1i(textureHandler, index)
    //配置边缘过渡参数
    GLES20.glTexParameterf(type, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR.toFloat())
    GLES20.glTexParameterf(type, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR.toFloat())
    GLES20.glTexParameteri(type, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE)
    GLES20.glTexParameteri(type, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE)
}

private fun activateDefTexture() {
    activateTexture(GLES11Ext.GL_TEXTURE_EXTERNAL_OES, mTextureId, 0, mTextureHandler)
}

private fun getVertexShader(): String {
    return "attribute vec4 aPosition;" +
            "precision mediump float;" +
            "uniform mat4 uMatrix;" +
            "attribute vec2 aCoordinate;" +
            "varying vec2 vCoordinate;" +
            "attribute float alpha;" +
            "varying float inAlpha;" +
            "void main() {" +
            "    gl_Position = uMatrix*aPosition;" +
            "    vCoordinate = aCoordinate;" +
            "    inAlpha = alpha;" +
            "}"
}

private fun getFragmentShader(): String {
    //一定要加换行"\n"，否则会和下一行的precision混在一起，导致编译出错
    return "#extension GL_OES_EGL_image_external : require\n" +
            "precision mediump float;" +
            "varying vec2 vCoordinate;" +
            "varying float inAlpha;" +
            "uniform samplerExternalOES uTexture;" +
            "uniform float progress;" +
            "uniform int drawFbo;" +
            "uniform sampler2D uSoulTexture;" +
            "void main() {" +
                // 透明度[0,0.4]
                "float alpha = 0.6 * (1.0 - progress);" +
                // 缩放比例[1.0,1.5]
                "float scale = 1.0 + (1.5 - 1.0) * progress;" +

                // 放大纹理坐标
                "float soulX = 0.5 + (vCoordinate.x - 0.5) / scale;\n" +
                "float soulY = 0.5 + (vCoordinate.y - 0.5) / scale;\n" +
                "vec2 soulTextureCoords = vec2(soulX, soulY);" +
                // 获取对应放大纹理坐标下的像素(颜色值rgba)
                "vec4 soulMask = texture2D(uSoulTexture, soulTextureCoords);" +

                "vec4 color = texture2D(uTexture, vCoordinate);" +

                "if (drawFbo == 0) {" +
                    // 颜色混合 默认颜色混合方程式 = mask * (1.0-alpha) + weakMask * alpha
                "    gl_FragColor = color * (1.0 - alpha) + soulMask * alpha;" +
                "} else {" +
                "   gl_FragColor = vec4(color.r, color.g, color.b, inAlpha);" +
                "}" +
            "}"
}

// 动画进度
uniform float progress;
// 是否绘制到FBO
uniform int drawFbo;
// 一帧固定的纹理
uniform sampler2D uSoulTexture;

if (drawFbo == 0) {
    // 颜色混合 默认颜色混合方程式 = mask * (1.0-alpha) + weakMask * alpha
    gl_FragColor = color * (1.0 - alpha) + soulMask * alpha;" +
} else {
   gl_FragColor = vec4(color.r, color.g, color.b, inAlpha);
}

// 透明度[0,0.4]
float alpha = 0.6 * (1.0 - progress);
// 缩放比例[1.0,1.5]
float scale = 1.0 + (1.5 - 1.0) * progress;

// 放大纹理坐标
float soulX = 0.5 + (vCoordinate.x - 0.5) / scale;
float soulY = 0.5 + (vCoordinate.y - 0.5) / scale;
vec2 soulTextureCoords = vec2(soulX, soulY);

// 获取对应放大纹理坐标下的像素(颜色值rgba)
vec4 soulMask = texture2D(uSoulTexture, soulTextureCoords);

gl_FragColor = color * (1.0 - alpha) + soulMask * alpha;


class SoulPlayerActivity: AppCompatActivity() {
    val path = Environment.getExternalStorageDirectory().absolutePath + "/mvtest.mp4"
    lateinit var drawer: IDrawer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_opengl_player)
        initRender()
    }

    private fun initRender() {
        // 使用“灵魂出窍”渲染器
        drawer = SoulVideoDrawer()
        drawer.setVideoSize(1920, 1080)
        drawer.getSurfaceTexture {
            initPlayer(Surface(it))
        }
        gl_surface.setEGLContextClientVersion(2)
        val render = SimpleRender()
        render.addDrawer(drawer)
        gl_surface.setRenderer(render)
    }

    private fun initPlayer(sf: Surface) {
        val threadPool = Executors.newFixedThreadPool(10)

        val videoDecoder = VideoDecoder(path, null, sf)
        threadPool.execute(videoDecoder)

        val audioDecoder = AudioDecoder(path)
        threadPool.execute(audioDecoder)

        videoDecoder.goOn()
        audioDecoder.goOn()
    }
}