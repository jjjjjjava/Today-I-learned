# 机制三 · Application 与 ContentProvider

## 主链路

```text
handleBindApplication
→ 创建 LoadedApk
→ makeApplication
→ Instrumentation.newApplication
→ Application.attach / attachBaseContext
→ installContentProviders
→ ContentProvider.onCreate
→ callApplicationOnCreate
→ Application.onCreate
```

## 精确点

- `ContentProvider.onCreate` 先于 `Application.onCreate`。
- Provider 与 Application 创建都在启动主链路中。
- Instrumentation 是 ActivityThread 调用应用代码的统一入口之一。
- 三方库通过独立 Provider 自动初始化，会增加启动期对象创建与同步工作。

## 治理边界

- 移除不必要的自动初始化 Provider。
- 可延迟组件改为显式或懒初始化。
- 有依赖关系的初始化显式建模，不靠偶然调用顺序。
- 首屏强依赖且要求主线程的工作不能盲目异步。

本项目该阶段约 220ms，不是 P0 主矛盾；机制存在，不代表本项目应优先治理。

## 关联知识

- [[../知识点/K09_ContentProvider初始化]]
- [[../知识点/K10_DAG初始化编排]]
- [[../知识点/K11_Baseline-Profile]]

## 复习检查

1. Provider与Application谁先？
2. `handleBindApplication`主链路是什么？
3. 为什么异步初始化有天花板？
4. 为什么本项目把Application治理排P2？
