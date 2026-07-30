# K05 · `doFrame` 为何不一定是根因

`Choreographer#doFrame`是每帧回调的外层调度入口，内部触发animation、traversal等工作。

本项目中：

```text
doFrame Wall约753.7ms
Self约0.3ms
```

Self极低说明自身工作少；主要耗时包含在内部`performTraversals`、inflate、layout、draw等子Slice中。

检索题：

1. `doFrame`在帧链路中是什么角色？
2. 为什么Wall高、Self低不能直接优化`doFrame`？
3. 下一步应下钻哪里？
