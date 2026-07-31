# Android 串口面试资源

## Knowledge

- [Android Developers：USB Host overview](https://developer.android.com/develop/connectivity/usb/host)
  Android 普通应用连接 USB 转串口设备时的官方 API 流程：枚举、授权、Interface、Endpoint 和数据传输。
- [AOSP：SerialManager](https://android.googlesource.com/platform/frameworks/base/+/android14-qpr2-s1-release/core/java/android/hardware/SerialManager.java)
  Android 系统串口服务源码；用于确认该 API 为隐藏系统 API，以及系统定制设备的串口打开方式。
- [AOSP：New Serial Manager API](https://android.googlesource.com/platform/frameworks/base/+/8b3b98d)
  说明系统串口依赖端口白名单、设备节点权限及平台配置。
- [Linux Kernel：TTY documentation](https://www.kernel.org/doc/html/v5.16/driver-api/serial/tty.html)
  Linux TTY、termios 与串口驱动关系的底层参考。

## Wisdom (Communities)

- [Stack Overflow：Android USB](https://stackoverflow.com/questions/tagged/android-usb)
  用于查询具体 USB 转串口芯片、设备兼容性和权限问题；答案需要结合官方文档验证。
