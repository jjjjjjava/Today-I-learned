# 阶段五 · 第二轮：Java 21与ASM兼容修复

> 本轮完整包含触发、根因、修复、验证与上游回馈。
> 事实源：[[../ARouter启动优化笔记#第二轮：项目升级 Java 21，插件再次不兼容]]

## 1. 触发

项目从Java 17升级到Java 21，插件处理Class产物时构建失败：

```text
Unsupported class file major version 65
```

该故障发生在构建期，不是运行时路由失败，也不是第二次启动性能劣化。

## 2. 根因

- Java 17 Class major version：61。
- Java 21 Class major version：65。
- 旧ASM `ClassReader`读取文件头时不认识65。
- 异常发生在进入`ClassVisitor`、`MethodVisitor`和D8之前。

根因：

> 插件运行时使用的旧ASM无法解析Java 21生成的Class文件。

## 3. 修复

1. `asm`、`asm-commons`、`asm-tree`统一升级到9.7。
2. Visitor API从ASM7调整到ASM9。
3. 确认Gradle插件运行时classpath实际解析到新版ASM。
4. 修复Debug/debug等variant匹配。
5. 发布自维护插件版本。

只改`Opcodes.ASM9`不能让旧`ClassReader`自动支持major 65。

## 4. 验证

### 解析层

Java 21 Class能被`ClassReader`读取。

### 收集与产物层

- Root、Provider、Interceptor集合完整；
- Group没有被错误全量注册；
- `loadRouterMap()`含完整`register()`；
- 修改后的Class可继续交给D8。

### 运行与功能层

- 升级首启、缓存失效时走插件路径；
- 页面、Provider、Interceptor、多模块路由正常；
- Release、Benchmark和目标variant构建通过。

## 5. 工程闭环

- 自维护插件发布到JitPack。
- 项目接入自维护版本。
- Java 21修复提交上游PR并被接受。

## 复习检查

1. major version 65在哪个阶段失败？
2. ClassReader版本、Visitor API、运行时classpath有什么区别？
3. 为什么构建成功不足以证明插件修复完成？
4. 第二轮四层验证是什么？
5. 上游回馈为什么属于工程闭环？
