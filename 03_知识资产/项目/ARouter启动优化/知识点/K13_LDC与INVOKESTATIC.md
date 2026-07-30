# K13 · `LDC`与`INVOKESTATIC`

插件在`loadRouterMap()`的`RETURN`前插入：

```text
LDC "生成类全限定名"
INVOKESTATIC LogisticsCenter.register
```

`LDC`把String压入操作数栈；`INVOKESTATIC`消费该参数调用静态方法。

描述符：

```text
(Ljava/lang/String;)V
```

表示接收一个String，返回void。

检索题：

1. 两条指令分别做什么？
2. 为什么插在`RETURN`前？
3. 方法描述符怎样解读？
