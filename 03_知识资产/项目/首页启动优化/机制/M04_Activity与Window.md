# 机制四 · Activity 与 Window

## Activity 创建

```text
LAUNCH_ACTIVITY
→ performLaunchActivity
→ createContext
→ Instrumentation.newActivity
→ Activity.attach
→ setTheme
→ onCreate
```

`attach` 创建并绑定 PhoneWindow。

## Window 三层

```text
Activity
→ PhoneWindow：应用侧窗口策略容器
→ DecorView：顶层View
→ ViewRootImpl：View树与系统渲染连接点
```

创建时机：

- `Activity.attach`：PhoneWindow。
- `setContentView`：安装 DecorView并inflate内容。
- `WindowManager.addView`：ViewRootImpl。

## `setContentView`

```text
installDecor
→ LayoutInflater解析XML
→ 反射构造View并解析属性
→ 挂入内容区域
```

返回时View树已构造，但还没完成measure/layout；此时宽高可能仍为0。

## 项目关联

ViewPager2全量预加载、首页一次性添加模块、静态XML WebView都发生在Activity与View构建路径，直接推高inflate和layout成本。

## 复习检查

1. `performLaunchActivity`做什么？
2. PhoneWindow、DecorView、ViewRootImpl何时创建？
3. `setContentView`返回时为何不代表已上屏？
4. 本项目三个代码根因怎样落在该阶段？
