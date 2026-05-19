本文你可以了解到
本文将结合前面系列文中介绍的MediaCodec、OpenGL、EGL、FBO、MediaMuxer等知识，实现对一个视频的解码，编辑，编码，最后保存为新视频的流程。

终于到了本篇章的最后一篇文章，前面的一系列文章中，围绕OpenGL，介绍了如何使用OpenGL来实现视频画面的渲染和显示，以及如何对视频画面进行编辑，有了以上基础以后，我们肯定想把编辑好的视频保存下来，实现整个编辑流程的闭环，本文就把最后一环补上。

一、MediaCodec编码器封装
在【音视频硬解码流程：封装基础解码框架】这篇文章中，介绍了如何使用Android原生提供的硬编解码工具MediaCodec，对视频进行解码。同时，MediaCodec也可以实现对音视频的硬编码。

还是先来看看官方的编解码数据流图
解码流程
在解码的时候，通过 dequeueInputBuffer 查询到一个空闲的输入缓冲区，在通过 queueInputBuffer 将 未解码 的数据压入解码器，最后，通过 dequeueOutputBuffer 得到 解码好 的数据。

编码流程
其实，编码流程和解码流程基本是一样的。不同在于压入 dequeueInputBuffer 输入缓冲区的数据是 未编码 的数据， 通过 dequeueOutputBuffer 得到的是 编码好 的数据。

依葫芦画瓢，仿照封装解码器的流程，来封装一个基础编码器 BaseEncoder 。

1. 定义编码器变量
完整代码请查看 BaseEncoder

abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {

    private val TAG = "BaseEncoder"

    // 目标视频宽，只有视频编码的时候才有效
    protected val mWidth: Int = width

    // 目标视频高，只有视频编码的时候才有效
    protected val mHeight: Int = height

    // Mp4合成器
    private var mMuxer: MMuxer = muxer

    // 线程运行
    private var mRunning = true

    // 编码帧序列
    private var mFrames = mutableListOf<Frame>()

    // 编码器
    private lateinit var mCodec: MediaCodec

    // 当前编码帧信息
    private val mBufferInfo = MediaCodec.BufferInfo()

    // 编码输出缓冲区
    private var mOutputBuffers: Array<ByteBuffer>? = null

    // 编码输入缓冲区
    private var mInputBuffers: Array<ByteBuffer>? = null

    private var mLock = Object()

    // 是否编码结束
    private var mIsEOS = false

    // 编码状态监听器
    private var mStateListener: IEncodeStateListener? = null
    
    // ......
}
首先，这是一个 abstract 抽象类，并且继承 Runnable ，上面先定义需要用到的内部变量。基本和解码类似。

要注意的是这里的宽高只对视频有效，MMuxer 是之前在【Mp4重打包】的是时候定义的Mp4封装工具。还有一个缓存队列mFrames，用来缓存需要编码的帧数据。

关于如何把数据写入到mp4中，本文不再重述，请查看【Mp4重打包】。

其中一帧数据定义如下：
class Frame {
    //未编码数据
    var buffer: ByteBuffer? = null

    //未编码数据信息
    var bufferInfo = MediaCodec.BufferInfo()
    private set

    fun setBufferInfo(info: MediaCodec.BufferInfo) {
        bufferInfo.set(info.offset, info.size, info.presentationTimeUs, info.flags)
    }
}
编码流程相对于解码流程来说比较简单，分为3个步骤：

初始化编码器
将数据压入编码器
从编码器取出数据，并压入mp4
2. 初始化编码器
abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {

    //省略其他代码......
    
    init {
        initCodec()
    }
    
    /**
     * 初始化编码器
     */
    private fun initCodec() {
        mCodec = MediaCodec.createEncoderByType(encodeType())
        configEncoder(mCodec)
        mCodec.start()
        mOutputBuffers = mCodec.outputBuffers
        mInputBuffers = mCodec.inputBuffers
    }
    
    
    /**
     * 编码类型
     */
    abstract fun encodeType(): String

    /**
     * 子类配置编码器
     */
    abstract fun configEncoder(codec: MediaCodec)
    
    // .......
}
这里定义了两个虚函数，子类必须实现。一个用于配置音频和视频对应的编码类型，如视频编码为h264对应的编码类型为："video/avc" ；音频编码为AAC对应的编码类型为："audio/mp4a-latm" 。

根据获取到的编码类型，就可以初始化得到一个编码器。

接着，调用 configEncoder 在子类中配置具体的编码参数，这里暂不细说，定义音视频编码子类的时候再说。

2. 开启编码循环
abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {
    // 省略其他代码......
    
    override fun run() {
        loopEncode()
        done()
    }
    
    /**
     * 循环编码
     */
    private fun loopEncode() {
        while (mRunning && !mIsEOS) {
            val empty = synchronized(mFrames) {
                mFrames.isEmpty()
            }
            if (empty) {
                justWait()
            }
            if (mFrames.isNotEmpty()) {
                val frame = synchronized(mFrames) {
                    mFrames.removeAt(0)
                }

                if (encodeManually()) {
                    //【1. 数据压入编码】
                    encode(frame)
                } else if (frame.buffer == null) { // 如果是自动编码（比如视频），遇到结束帧的时候，直接结束掉
                    // This may only be used with encoders receiving input from a Surface
                    mCodec.signalEndOfInputStream()
                    mIsEOS = true
                }
            }
            //【2. 拉取编码好的数据】
            drain()
        }
    }
    
    // ......
}
循环编码放在 Runnable 的 run 方法中。

在 loopEncode 中，将前面提到的 2（压数据） 和 3（取数据） 合并在一起。逻辑也比较简单。

判断未编码的缓存队列是否为空，是则线程挂起，进入等待；否则编码数据，和取出数据。

有2点需要注意：

音频和视频的编码流程稍微有点区别
音频编码 需要我们自己将数据压入编码器，实现数据的编码。

视频编码 的时候，可以通过将 Surface 绑定给 OpenGL ，系统自动从 Surface 中去数据，实现自动编码。也就是说，不需要用户自己手动压入数据，只需从输出缓冲中取数据就可以了。

因此，这里定义一个虚函数，由子类控制是否需要手动压入数据，默认为true：手动压入。

下文中，将这两种形式分别叫做：手动编码 和 自动编码

abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {

    // 省略其他代码......
    
    /**
     * 是否手动编码
     * 视频：false 音频：true
     *
     * 注：视频编码通过Surface，MediaCodec自动完成编码；音频数据需要用户自己压入编码缓冲区，完成编码
     */
    open fun encodeManually() = true
    
    
    // ......
}
结束编码
在编码过程中，如果发现 Frame 中 buffer 为 null ，就认为编码已经完成了，没有数据需要压入了。这时，有两种方法告诉编码器结束编码。

第一种，通过 queueInputBuffer 压入一个空数据，并且将数据类型标记设置为 MediaCodec.BUFFER_FLAG_END_OF_STREAM 。具体如下：

mCodec.queueInputBuffer(index, 0, 0,
    frame.bufferInfo.presentationTimeUs,
    MediaCodec.BUFFER_FLAG_END_OF_STREAM)
第二种，通过 signalEndOfInputStream 发送结束信号。

我们已经知道，视频是自动编码，所以无法通过第一种结束编码，只能通过第二种方式结束编码。

音频是手动编码，可以通过第一种方式结束编码。

一个坑
测试发现，视频结束编码的时候 signalEndOfInputStream 之后，在获取编码数据输出的时候，并没有得到结束编码标记的数据，所以，上面的代码中，如果是自动编码，在判断到 Frame 的 buffer 为空时，直接将 mIsEOF 设置为 true 了，退出了编码流程。

3. 手动编码
abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {
    
    // 省略其他代码......
    
    /**
     * 编码
     */
    private fun encode(frame: Frame) {

        val index = mCodec.dequeueInputBuffer(-1)

        /*向编码器输入数据*/
        if (index >= 0) {
            val inputBuffer = mInputBuffers!![index]
            inputBuffer.clear()
            if (frame.buffer != null) {
                inputBuffer.put(frame.buffer)
            }
            if (frame.buffer == null || frame.bufferInfo.size <= 0) { // 小于等于0时，为音频结束符标记
                mCodec.queueInputBuffer(index, 0, 0,
                    frame.bufferInfo.presentationTimeUs, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
            } else {
                mCodec.queueInputBuffer(index, 0, frame.bufferInfo.size,
                    frame.bufferInfo.presentationTimeUs, 0)
            }
            frame.buffer?.clear()
        }
    }
    
    // ......
}
和解码一样，先查询到一个可用的输入缓冲索引，接着把数据压入输入缓冲。

这里，先判断是否结束编码，是则往输入缓冲压入编码结束标志

4. 拉取数据
把一帧数据压入编码器后，进入 drain 方法，顾名思义，我们要把编码器输出缓冲中的数据，全部抽干。所以这里是一个while循环，直到输出缓冲没有数据 MediaCodec.INFO_TRY_AGAIN_LATER ，或者编码结束 MediaCodec.BUFFER_FLAG_END_OF_STREAM 。

abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {
    
    // 省略其他代码......
    
    /**
     * 榨干编码输出数据
     */
    private fun drain() {
        loop@ while (!mIsEOS) {
            val index = mCodec.dequeueOutputBuffer(mBufferInfo, 0)
            when (index) {
                MediaCodec.INFO_TRY_AGAIN_LATER -> break@loop
                MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> {
                    addTrack(mMuxer, mCodec.outputFormat)
                }
                MediaCodec.INFO_OUTPUT_BUFFERS_CHANGED -> {
                    mOutputBuffers = mCodec.outputBuffers
                }
                else -> {
                    if (mBufferInfo.flags == MediaCodec.BUFFER_FLAG_END_OF_STREAM) {
                        mIsEOS = true
                        mBufferInfo.set(0, 0, 0, mBufferInfo.flags)
                    }

                    if (mBufferInfo.flags == MediaCodec.BUFFER_FLAG_CODEC_CONFIG) {
                        // SPS or PPS, which should be passed by MediaFormat.
                        mCodec.releaseOutputBuffer(index, false)
                        continue@loop
                    }

                    if (!mIsEOS) {
                        writeData(mMuxer, mOutputBuffers!![index], mBufferInfo)
                    }
                    mCodec.releaseOutputBuffer(index, false)
                }
            }
        }
    }
    
    
    /**
     * 配置mp4音视频轨道
     */
    abstract fun addTrack(muxer: MMuxer, mediaFormat: MediaFormat)

    /**
     * 往mp4写入音视频数据
     */
    abstract fun writeData(muxer: MMuxer, byteBuffer: ByteBuffer, bufferInfo: MediaCodec.BufferInfo)
    
    // ......
}
很重要的一点
当 mCodec.dequeueOutputBuffer 返回的是 MediaCodec.INFO_OUTPUT_FORMAT_CHANGED 时，说明编码参数格式已经生成（比如视频的码率，帧率，SPS/PPS帧信息等），需要把这些信息写入到mp4对应媒体轨道中（这里通过 addTrack 在子类中配置音视频对应的编码格式），之后才能开始将编码完成的数据，通过MediaMuxer写入到相应媒体通道中。

5. 退出编码，释放资源
abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {
    
    // 省略其他代码......

    /**
     * 编码结束，是否资源
     */
    private fun done() {
        try {
            release(mMuxer)
            mCodec.stop()
            mCodec.release()
            mRunning = false
            mStateListener?.encoderFinish(this)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    /**
     * 释放子类资源
     */
    abstract fun release(muxer: MMuxer)
    
    // ......
}
调用子类中的虚函数 release ，子类需要根据自己的媒体类型，释放对应mp4中的媒体通道。

6. 一些外部调用的方法
abstract class BaseEncoder(muxer: MMuxer, width: Int = -1, height: Int = -1) : Runnable {
    
    // 省略其他代码......
    
    /**
     * 将一帧数据压入队列，等待编码
     */
    fun encodeOneFrame(frame: Frame) {
        synchronized(mFrames) {
            mFrames.add(frame)
            notifyGo()
        }
        // 延时一点时间，避免掉帧
        Thread.sleep(frameWaitTimeMs())
    }

    /**
     * 通知结束编码
     */
    fun endOfStream() {
        Log.e("ccccc","endOfStream")
        synchronized(mFrames) {
            val frame = Frame()
            frame.buffer = null
            mFrames.add(frame)
            notifyGo()
        }
    }
    
    /**
     * 设置状态监听器
     */
    fun setStateListener(l: IEncodeStateListener) {
        this.mStateListener = l
    }
    
    
    /**
     * 每一帧排队等待时间
     */
    open fun frameWaitTimeMs() = 20L
    
    // ......
}

这里有点需要注意，在把数据压入排队队列之后，做了一个默认 20ms 的延时，同时子类可以通过重写 frameWaitTimeMs 方法修改时间。

一个是为了避免音频解码过快，导致数据堆积太多，音频在子类中重新设置等待为5ms，具体见子类 AudioEncoder 代码。

另一个是因为由于视频是系统自动获取Surface数据，如果解码数据刷新太快，可能会导致漏帧，这里使用默认的20ms。

因此这里做了一个简单粗暴的延时，但并非最好的解决方式。

二、视频编码器
有了基础封装，写一个视频编码器还不是so easy的事吗？

反手就贴出一个视频编码器：

const val DEFAULT_ENCODE_FRAME_RATE = 30

class VideoEncoder(muxer: MMuxer, width: Int, height: Int): BaseEncoder(muxer, width, height) {

    private val TAG = "VideoEncoder"
    
    private var mSurface: Surface? = null

    override fun encodeType(): String {
        return "video/avc"
    }

    override fun configEncoder(codec: MediaCodec) {
        if (mWidth <= 0 || mHeight <= 0) {
            throw IllegalArgumentException("Encode width or height is invalid, width: $mWidth, height: $mHeight")
        }
        val bitrate = 3 * mWidth * mHeight
        val outputFormat = MediaFormat.createVideoFormat(encodeType(), mWidth, mHeight)
        outputFormat.setInteger(MediaFormat.KEY_BIT_RATE, bitrate)
        outputFormat.setInteger(MediaFormat.KEY_FRAME_RATE, DEFAULT_ENCODE_FRAME_RATE)
        outputFormat.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 1)
        outputFormat.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface)

        try {
            configEncoderWithCQ(codec, outputFormat)
        } catch (e: Exception) {
            e.printStackTrace()
            // 捕获异常，设置为系统默认配置 BITRATE_MODE_VBR
            try {
                configEncoderWithVBR(codec, outputFormat)
            } catch (e: Exception) {
                e.printStackTrace()
                Log.e(TAG, "配置视频编码器失败")
            }
        }

        mSurface = codec.createInputSurface()
    }

    private fun configEncoderWithCQ(codec: MediaCodec, outputFormat: MediaFormat) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            // 本部分手机不支持 BITRATE_MODE_CQ 模式，有可能会异常
            outputFormat.setInteger(
                MediaFormat.KEY_BITRATE_MODE,
                MediaCodecInfo.EncoderCapabilities.BITRATE_MODE_CQ
            )
        }
        codec.configure(outputFormat, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
    }

    private fun configEncoderWithVBR(codec: MediaCodec, outputFormat: MediaFormat) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            outputFormat.setInteger(
                MediaFormat.KEY_BITRATE_MODE,
                MediaCodecInfo.EncoderCapabilities.BITRATE_MODE_VBR
            )
        }
        codec.configure(outputFormat, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
    }

    override fun addTrack(muxer: MMuxer, mediaFormat: MediaFormat) {
        muxer.addVideoTrack(mediaFormat)
    }

    override fun writeData(
        muxer: MMuxer,
        byteBuffer: ByteBuffer,
        bufferInfo: MediaCodec.BufferInfo
    ) {
        muxer.writeVideoData(byteBuffer, bufferInfo)
    }

    override fun encodeManually(): Boolean {
        return false
    }

    override fun release(muxer: MMuxer) {
        muxer.releaseVideoTrack()
    }

    fun getEncodeSurface(): Surface? {
        return mSurface
    }
}
继承了 BaseEncoder 实现所有的虚函数就可以了。

重点来看 configEncoder 这个方法。

i. 配置了码率 KEY_BIT_RATE。

计算公式源自【MediaCodec编码OpenGL速度和清晰度均衡】

Biterate = Width * Height * FrameRate * Factor 

Factor: 0.1~0.2
ii. 配置帧率 KEY_FRAME_RATE ，这里为30帧/秒
iii. 配置关键帧出现频率 KEY_I_FRAME_INTERVAL ，这里为1帧/秒
iv. 配置数据来源 KEY_COLOR_FORMAT ，为 COLOR_FormatSurface，既来自 Surface 。
v. 配置码率模式 KEY_BITRATE_MODE

- BITRATE_MODE_CQ 忽略用户设置的码率，由编码器自己控制码率，并尽可能保证画面清晰度和码率的均衡  
- BITRATE_MODE_CBR 无论视频的画面内容如果，尽可能遵守用户设置的码率  
- BITRATE_MODE_VBR 尽可能遵守用户设置的码率，但是会根据帧画面之间运动矢量  
（通俗理解就是帧与帧之间的画面变化程度）来动态调整码率，如果运动矢量较大，则在该时间段将码率调高，如果画面变换很小，则码率降低。 
优先选择 BITRATE_MODE_CQ ，如果编码器不支持，切换回系统默认的 BITRATE_MODE_VBR

vi. 最后，通过编码器 codec.createInputSurface() 新建一个 Surface ，用于 EGL 的窗口绑定。视频解码得到的画面都将渲染到这个 Surface 中，MediaCodec自动从里面取出数据，并编码。

三、音频编码器
音频编码器则更加简单。

// 编码采样率率
val DEST_SAMPLE_RATE = 44100
// 编码码率
private val DEST_BIT_RATE = 128000

class AudioEncoder(muxer: MMuxer): BaseEncoder(muxer) {

    private val TAG = "AudioEncoder"

    override fun encodeType(): String {
        return "audio/mp4a-latm"
    }

    override fun configEncoder(codec: MediaCodec) {
        val audioFormat = MediaFormat.createAudioFormat(encodeType(), DEST_SAMPLE_RATE, 2)
        audioFormat.setInteger(MediaFormat.KEY_BIT_RATE, DEST_BIT_RATE)
        audioFormat.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, 100*1024)
        try {
            configEncoderWithCQ(codec, audioFormat)
        } catch (e: Exception) {
            e.printStackTrace()
            try {
                configEncoderWithVBR(codec, audioFormat)
            } catch (e: Exception) {
                e.printStackTrace()
                Log.e(TAG, "配置音频编码器失败")
            }
        }
    }

    private fun configEncoderWithCQ(codec: MediaCodec, outputFormat: MediaFormat) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            // 本部分手机不支持 BITRATE_MODE_CQ 模式，有可能会异常
            outputFormat.setInteger(
                MediaFormat.KEY_BITRATE_MODE,
                MediaCodecInfo.EncoderCapabilities.BITRATE_MODE_CQ
            )
        }
        codec.configure(outputFormat, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
    }

    private fun configEncoderWithVBR(codec: MediaCodec, outputFormat: MediaFormat) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            outputFormat.setInteger(
                MediaFormat.KEY_BITRATE_MODE,
                MediaCodecInfo.EncoderCapabilities.BITRATE_MODE_VBR
            )
        }
        codec.configure(outputFormat, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
    }

    override fun addTrack(muxer: MMuxer, mediaFormat: MediaFormat) {
        muxer.addAudioTrack(mediaFormat)
    }

    override fun writeData(
        muxer: MMuxer,
        byteBuffer: ByteBuffer,
        bufferInfo: MediaCodec.BufferInfo
    ) {
        muxer.writeAudioData(byteBuffer, bufferInfo)
    }

    override fun release(muxer: MMuxer) {
        muxer.releaseAudioTrack()
    }
}
可以看到，configEncoder 实现也比较简单：

i. 设置音频比特率 MediaFormat.KEY_BIT_RATE，这里设置为 128000
ii. 设置输入缓冲区大小 KEY_MAX_INPUT_SIZE ，这里设置为 100*1024
四、整合
音频和视频的编码工具已经完成，接下来就来看看，如何把解码器、OpenGL、EGL、编码器串联起来，实现视频编辑功能。

改造EGL渲染器
开始之前，需要改造一下【深入了解OpenGL之EGL】 这篇文章中定义的EGL渲染器。

i. 在之前定义的渲染器中，只支持设置一个SurfaceView，并绑定到 EGL 显示窗口中。这里需要让它支持设置一个Surface，接收来自 VideoEncoder 中创建的Surface作为渲染窗口。

ii. 由于是要对窗口的画面进行编码，所以无需在渲染器中不断的刷新画面，只要在视频解码器解码出一帧的时候，刷新一下画面即可。同时把当前帧的时间戳传递给OpenGL。

完整代码如下，已经将新增的部分标记出来：


class CustomerGLRenderer : SurfaceHolder.Callback {

    private val mThread = RenderThread()

    private var mSurfaceView: WeakReference<SurfaceView>? = null

    private var mSurface: Surface? = null

    private val mDrawers = mutableListOf<IDrawer>()

    init {
        mThread.start()
    }

    fun setSurface(surface: SurfaceView) {
        mSurfaceView = WeakReference(surface)
        surface.holder.addCallback(this)

        surface.addOnAttachStateChangeListener(object : View.OnAttachStateChangeListener{
            override fun onViewDetachedFromWindow(v: View?) {
                stop()
            }

            override fun onViewAttachedToWindow(v: View?) {
            }
        })
    }

//-------------------新增部分-----------------

    // 新增设置Surface接口
    fun setSurface(surface: Surface, width: Int, height: Int) {
        mSurface = surface
        mThread.onSurfaceCreate()
        mThread.onSurfaceChange(width, height)
    }

    // 新增设置渲染模式 RenderMode见下面
    fun setRenderMode(mode: RenderMode) {
        mThread.setRenderMode(mode)
    }

    // 新增通知更新画面方法
    fun notifySwap(timeUs: Long) {
        mThread.notifySwap(timeUs)
    }
/----------------------------------------------

    fun addDrawer(drawer: IDrawer) {
        mDrawers.add(drawer)
    }

    fun stop() {
        mThread.onSurfaceStop()
        mSurface = null
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        mSurface = holder.surface
        mThread.onSurfaceCreate()
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        mThread.onSurfaceChange(width, height)
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        mThread.onSurfaceDestroy()
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

        private var mCurTimestamp = 0L

        private var mLastTimestamp = 0L

        private var mRenderMode = RenderMode.RENDER_WHEN_DIRTY

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

        fun setRenderMode(mode: RenderMode) {
            mRenderMode = mode
        }

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

        fun notifySwap(timeUs: Long) {
            synchronized(mCurTimestamp) {
                mCurTimestamp = timeUs
            }
            notifyGo()
        }

        override fun run() {
            initEGL()
            while (true) {
                when (mState) {
                    RenderState.FRESH_SURFACE -> {
                        createEGLSurfaceFirst()
                        holdOn()
                    }
                    RenderState.SURFACE_CHANGE -> {
                        createEGLSurfaceFirst()
                        GLES20.glViewport(0, 0, mWidth, mHeight)
                        configWordSize()
                        mState = RenderState.RENDERING
                    }
                    RenderState.RENDERING -> {
                        render()
                        
                        //新增判断：如果是 `RENDER_WHEN_DIRTY` 模式，渲染后，把线程挂起，等待下一帧
                        if (mRenderMode == RenderMode.RENDER_WHEN_DIRTY) {
                            holdOn()
                        }
                    }
                    RenderState.SURFACE_DESTROY -> {
                        destroyEGLSurface()
                        mState = RenderState.NO_SURFACE
                    }
                    RenderState.STOP -> {
                        releaseEGL()
                        return
                    }
                    else -> {
                        holdOn()
                    }
                }
                if (mRenderMode == RenderMode.RENDER_CONTINUOUSLY) {
                    sleep(16)
                }
            }
        }

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
                    GLES20.glClearColor(0f, 0f, 0f, 0f)
                    //开启混合，即半透明
                    GLES20.glEnable(GLES20.GL_BLEND)
                    GLES20.glBlendFunc(GLES20.GL_SRC_ALPHA, GLES20.GL_ONE_MINUS_SRC_ALPHA)
                    generateTextureID()
                }
            }
        }

        private fun createEGLSurface() {
            mEGLSurface?.createEGLSurface(mSurface)
            mEGLSurface?.makeCurrent()
        }

        private fun generateTextureID() {
            val textureIds = OpenGLTools.createTextureIds(mDrawers.size)
            for ((idx, drawer) in mDrawers.withIndex()) {
                drawer.setTextureID(textureIds[idx])
            }
        }

        private fun configWordSize() {
            mDrawers.forEach { it.setWorldSize(mWidth, mHeight) }
        }

// ---------------------修改部分代码------------------------
        // 根据渲染模式和当前帧的时间戳判断是否需要重新刷新画面
        private fun render() {
            val render = if (mRenderMode == RenderMode.RENDER_CONTINUOUSLY) {
                true
            } else {
                synchronized(mCurTimestamp) {
                    if (mCurTimestamp > mLastTimestamp) {
                        mLastTimestamp = mCurTimestamp
                        true
                    } else {
                        false
                    }
                }
            }

            if (render) {
                GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT or GLES20.GL_DEPTH_BUFFER_BIT)
                mDrawers.forEach { it.draw() }
                mEGLSurface?.setTimestamp(mCurTimestamp)
                mEGLSurface?.swapBuffers()
            }
        }
        
//------------------------------------------------------

        private fun destroyEGLSurface() {
            mEGLSurface?.destroyEGLSurface()
            mHaveBindEGLContext = false
        }

        private fun releaseEGL() {
            mEGLSurface?.release()
        }
    }

    /**
     * 渲染状态
     */
    enum class RenderState {
        NO_SURFACE, //没有有效的surface
        FRESH_SURFACE, //持有一个未初始化的新的surface
        SURFACE_CHANGE, //surface尺寸变化
        RENDERING, //初始化完毕，可以开始渲染
        SURFACE_DESTROY, //surface销毁
        STOP //停止绘制
    }

//---------新增渲染模式定义------------
    enum class RenderMode {
        // 自动循环渲染
        RENDER_CONTINUOUSLY,
        // 由外部通过notifySwap通知渲染
        RENDER_WHEN_DIRTY
    }
//-------------------------------------
}
新增部分已经标出来，也不复杂，主要是新增了设置Surface，区分了两种渲染模式，请大家看代码即可。

改造解码器
还记得之前的文章中提到，音视频要正常播放，需要对音频和视频进行音视频同步吗？

而由于编码的时候，并不需要把视频画面和音频播放出来，所以可以把音视频同步去掉，加快编码速度。

修改也很简单，在 BaseDecoder 中新增一个变量 mSyncRender ，如果 mSyncRender == false ，就把音视频同步去掉。

这里，只列出修改的部分，完整代码请看 BaseDecoder

abstract class BaseDecoder(private val mFilePath: String): IDecoder {
    
    // 省略无关代码......
    
    // 是否需要音视频渲染同步
    private var mSyncRender = true
    
    
    final override fun run() {
        //省略无关代码...
        
        while (mIsRunning) {
            // ......
            
            // ---------【音视频同步】-------------
            if (mSyncRender && mState == DecodeState.DECODING) {
                sleepRender()
            }
            
            if (mSyncRender) {// 如果只是用于编码合成新视频，无需渲染
                render(mOutputBuffers!![index], mBufferInfo)
            }
            
            // ......
        }
        //
    }
    
    override fun withoutSync(): IDecoder {
        mSyncRender = false
        return this
    }
    
    //......
}
整合
class SynthesizerActivity: AppCompatActivity(), MMuxer.IMuxerStateListener {

    private val path = Environment.getExternalStorageDirectory().absolutePath + "/mvtest_2.mp4"
    private val path2 = Environment.getExternalStorageDirectory().absolutePath + "/mvtest.mp4"

    private val threadPool = Executors.newFixedThreadPool(10)

    private var renderer = CustomerGLRenderer()

    private var audioDecoder: IDecoder? = null
    private var videoDecoder: IDecoder? = null

    private lateinit var videoEncoder: VideoEncoder
    private lateinit var audioEncoder: AudioEncoder

    private var muxer = MMuxer()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_synthesizer)
        muxer.setStateListener(this)
    }

    fun onStartClick(view: View) {
        btn.text = "正在编码"
        btn.isEnabled = false
        initVideo()
        initAudio()
        initAudioEncoder()
        initVideoEncoder()
    }

    private fun initVideoEncoder() {
        // 视频编码器
        videoEncoder = VideoEncoder(muxer, 1920, 1080)

        renderer.setRenderMode(CustomerGLRenderer.RenderMode.RENDER_WHEN_DIRTY)
        renderer.setSurface(videoEncoder.getEncodeSurface()!!, 1920, 1080)

        videoEncoder.setStateListener(object : DefEncodeStateListener {
            override fun encoderFinish(encoder: BaseEncoder) {
                renderer.stop()
            }
        })
        threadPool.execute(videoEncoder)
    }

    private fun initAudioEncoder() {
        // 音频编码器
        audioEncoder = AudioEncoder(muxer)
        // 启动编码线程
        threadPool.execute(audioEncoder)
    }

    private fun initVideo() {
        val drawer = VideoDrawer()
        drawer.setVideoSize(1920, 1080)
        drawer.getSurfaceTexture {
            initVideoDecoder(path, Surface(it))
        }
        renderer.addDrawer(drawer)
    }

    private fun initVideoDecoder(path: String, sf: Surface) {
        videoDecoder?.stop()
        videoDecoder = VideoDecoder(path, null, sf).withoutSync()
        videoDecoder!!.setStateListener(object : DefDecodeStateListener {
            override fun decodeOneFrame(decodeJob: BaseDecoder?, frame: Frame) {
                renderer.notifySwap(frame.bufferInfo.presentationTimeUs)
                videoEncoder.encodeOneFrame(frame)
            }

            override fun decoderFinish(decodeJob: BaseDecoder?) {
                videoEncoder.endOfStream()
            }
        })
        videoDecoder!!.goOn()

        //启动解码线程
        threadPool.execute(videoDecoder!!)
    }

    private fun initAudio() {
        audioDecoder?.stop()
        audioDecoder = AudioDecoder(path).withoutSync()
        audioDecoder!!.setStateListener(object : DefDecodeStateListener {

            override fun decodeOneFrame(decodeJob: BaseDecoder?, frame: Frame) {
                audioEncoder.encodeOneFrame(frame)
            }

            override fun decoderFinish(decodeJob: BaseDecoder?) {
                audioEncoder.endOfStream()
            }
        })
        audioDecoder!!.goOn()

        //启动解码线程
        threadPool.execute(audioDecoder!!)
    }

    override fun onMuxerFinish() {
    
        runOnUiThread {
            btn.isEnabled = true
            btn.text = "编码完成"
        }

        audioDecoder?.stop()
        audioDecoder = null

        videoDecoder?.stop()
        videoDecoder = null
    }
}
可以看到，过程很简单：初始化解码器，初始化EGL Render，初始化编码器，然后将解码得到的数据扔到编码器队列中，监听解码状态和编码状态，做相应的操作。

解码过程和使用EGL播放视频基本是一样的，只是渲染模式不同而已。

在这个代码中，只是简单的将原视频解码，渲染到OpenGL，重新编码成新的mp4，也就是说输出的视频和原视频是一模一样的。

可以实现什么？
虽然上面只是一个普通的解码和编码的过程，但是却可以衍生出无限的想象。

比如：实现视频裁剪：给解码器设置一个开始和结束的时间即可。

实现炫酷的视频画面编辑：比如将视频渲染器 VideoDrawer 换成之前写好的 SoulVideoDrawer 的话，将得到一个有 灵魂出窍 效果的视频；结合之前的画中画，可以实现视频的叠加。

视频拼接：结合多个视频解码器，将多个视频连接起来，编码成新的视频。

加水印：结合OpenGL渲染图片，加个水印超简单的。

......

只要有想象力，那都不是事！

五、结束语
啊～～～，嗨森，终于写完本系列的【OpenGL渲染视频画面篇】，到目前为止，如果你看过每一篇文章，并且动手码过代码，我相信你一定已经踏入了Android音视频开发的大门，可以去实现一些以前看起来很神秘的视频效果，然后保存成一个真正的可播放的视频。

这一系列文章每篇都很长，感谢每个能阅读到这里的读者，我觉得我们都应该感谢一下自己，坚持真的很难。

最后无比感谢每一位给文章点赞、留言、提问、鼓励的人儿，是你们让冰冷的文字充满温情，是我坚持的动力。

