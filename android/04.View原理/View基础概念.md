[toc]

## 01. View的介绍

### 1.1 什么是View

view是 Android 中所有 UI 组件的基类。`View` 代表了一个矩形区域，可以用来显示内容或响应用户的交互。所有可见的 UI 元素，像 `Button`、`TextView`、`ImageView` 等，都是 `View` 的子类。

### 1.2 常见的View的子类

`View` 是抽象类，具体的 UI 组件是它的子类。常见的 `View` 类型包括：

- **TextView**：用于显示文本内容。
- **Button**：一个可点击的按钮。
- **ImageView**：用于显示图片。
- **EditText**：一个可以输入文本的编辑框。
- **CheckBox**：一个带勾选框的选择项。

### 1.3 View和ViewGroup

**`ViewGroup`** 是 `View` 的子类，他很特殊，不像Button那些子类一样用来显示内容，他用来充当一个 **容器**，他内部可以包含多个子 `View` 或子 `ViewGroup`，以此来实现复杂的 UI 布局。他们两个共同实现了view树，如下图：

![image-20241111162334182](D:\Files\Develop\Today-I-learned\android\_pic_\image-20241111162334182.png)

![image-20241111162417079](D:\Files\Develop\Today-I-learned\android\_pic_\image-20241111162417079.png)

同时`ViewGroup` 也是 Android 中布局控件的父类，所有布局类（如 `LinearLayout`、`RelativeLayout`、`FrameLayout`）都继承自 `ViewGroup`。以下是一些常见的 `ViewGroup` 子类及其功能：

- **LinearLayout**：线性布局，以水平或垂直的顺序排列子视图。
- **RelativeLayout**：相对布局，根据子视图之间的相对位置进行排列。
- **FrameLayout**：帧布局，子视图会堆叠显示，适合显示单一子视图。
- **ConstraintLayout**：约束布局，可以通过约束关系自由定位子视图，适合构建复杂的布局。
- **RecyclerView**：用于显示大量数据的高性能列表，可以实现复杂的列表布局。



## 02. View 的生命周期

`View` 的生命周期主要包括测量、布局、绘制等步骤。

- **onMeasure()**：测量 `View` 的宽度和高度。
- **onLayout()**：确定 `View` 的位置，尤其在 `ViewGroup` 中更为重要。
- **onDraw()**：绘制 `View` 的内容。

