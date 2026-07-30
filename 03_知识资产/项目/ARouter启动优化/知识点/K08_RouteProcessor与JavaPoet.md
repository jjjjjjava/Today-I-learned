# K08 · RouteProcessor与JavaPoet

```text
@Route
→ RouteProcessor读取RoundEnvironment
→ 取得标注Element
→ 解析注解与类型
→ 构造RouteMeta
→ 按group整理
→ JavaPoet生成Root/Group/Provider源码
```

RouteProcessor负责扫描和组织；JavaPoet负责生成Java源码。

检索题：

1. RoundEnvironment和Element是什么？
2. RouteMeta从哪些信息构成？
3. RouteProcessor与JavaPoet如何分工？
