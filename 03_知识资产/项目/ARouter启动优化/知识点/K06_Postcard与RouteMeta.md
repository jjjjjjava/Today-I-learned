# K06 · Postcard与RouteMeta

- Postcard：一次路由请求，初始保存path、group、参数和flags。
- RouteMeta：路由定义，保存destination、type、path、group等。

`completion(postcard)`按path查RouteMeta，再补全Postcard；之后才能按Activity、Fragment、Provider类型执行。

检索题：

1. Postcard与RouteMeta分别是什么？
2. `build()`后Postcard还缺什么？
3. `completion()`完成什么？
