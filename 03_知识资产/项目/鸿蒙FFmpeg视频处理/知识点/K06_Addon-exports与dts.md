# K06 · Addon、exports 与 `.d.ts`

| 层 | 职责 |
|---|---|
| Native Addon | 建立动态库模块初始化入口 |
| `exports` | 运行时暴露可调用函数 |
| `.d.ts` | 编译期声明类型 |

只有 `.d.ts`，运行时不会自动出现 Native 函数。

## 自检

1. ArkTS `import` 时发生什么？
2. 哪一层让函数真正可见？
3. `.d.ts` 缺失与 Addon 缺失分别表现为什么？
