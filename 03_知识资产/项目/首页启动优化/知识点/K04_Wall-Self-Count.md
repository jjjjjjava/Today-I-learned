# K04 · Wall / Self / Count

- Wall：Slice总时长，包含子Slice。
- Self：扣除子Slice后的自身时长。
- Count：出现次数。

组合：

- Wall高、Self高、Count少：单个重任务。
- Wall高、Self高、Count多：高频重任务。
- Wall高、Self低：外层容器，继续下钻。
- Wall约等于Self且Count多：高频直接成本。

聚合Wall存在嵌套与重叠，不能相加当作总TTFD。

检索题：

1. 三个指标各回答什么？
2. Wall高、Self低意味着什么？
3. 为什么聚合Wall不能直接相加？
