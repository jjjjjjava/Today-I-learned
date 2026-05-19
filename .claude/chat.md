1. 可以省略，这个起到提高效率的步骤  
2.kotlin的==是调用equals，Java的== 在kotlin中是===
3. 很简单
 override fun equals(other: Any?): Boolean {
        // 步骤1: 引用相等检查
        if (this === other) return true
        
        // 步骤2: 类型检查（Kotlin的智能转换）
        if (other !is Point) return false
        
        // 步骤3: 字段比较（不需要手动转换！）
        return x == other.x && y == other.y
    }


1. 不清楚，但是不重要
2. 不该包含
3. 好问题，我们把它放入到map中，理论上其已经正确放入hashcode对应的桶中了，但是现在我们修改了他，此时？他会被自动移动到对应的哈希桶中？
所以会输出自己在哈希桶中的地址？

4. 但是说实话，我发现一个问题，我的项目开发中Android项目中，压根没遇到过这个重写hashCode的啊