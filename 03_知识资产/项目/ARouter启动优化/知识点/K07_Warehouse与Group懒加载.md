# K07 · Warehouse与Group懒加载

```text
groupsIndex：group → Group Class
routes：path → RouteMeta
```

初始化先加载Root，得到Group Class索引；首次访问某个group时，再执行该Group的`loadInto(routes)`。

因此插件注册Root、Provider、Interceptor，不全量注册Group。

检索题：

1. `groupsIndex`与`routes`分别保存什么？
2. Group何时进入`routes`？
3. 为什么插件不直接注册全部Group？
