注解处理器原理：

- 在编译时，编译器会检查 AbstractProcessor 的子类，并调用 AbstractProcessor 的子类的 process() 方法，然后把添加了注解的元素都传到 process() 方法中，这样我们就可以在 process() 函数中生成新的 Java 类文件。



这和字节码插桩有什么关系？

- 注解处理器是在编译期、源码到字节码（.java/.kt → .class）之前执行的。

- 流程：

  1. 源码 → 注解处理器（APT，生成新源码） → 新源码加入编译队列

  1. 所有源码（原始+新生成） → 编译成 .class 字节码

- 字节码插桩

  - 字节码插桩是在源码编译成 .class 文件之后，打包成 dex 之前执行的。

  - 在 Android 项目中，字节码插桩通常通过 Gradle Transform API 或 ASM 实现。

  - 插桩可以修改、增强、分析 .class 文件，比如自动注册路由表、插入埋点、性能监控等

- 流程：

  1. 所有源码 → 编译成 .class 文件

  1. Transform/ASM 插桩：对 .class 文件做字节码修改

  1. 插桩后的 .class 文件 → 打包成 dex → APK



ARouter中两者皆有：

- ARouter 注解处理器：在编译期生成路由表类（如 ARouter$$Group$$xxx）。

- ARouter Register 插件（Transform/ASM）：在编译后、打包前，扫描所有 .class 文件，把所有路由表类名自动注册到初始化代码中（如 LogisticsCenter.loadRouterMap()），实现“免 Dex 扫描”





Transform/ASM是什么？