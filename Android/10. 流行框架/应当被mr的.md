## 🎯 应该包含在MR中的文件（核心功能）：

### 1. 新增lib_msg_setting模块

```
Feature/lib_msg_setting/（整个目录）
├── .gitignore
├── Index.ets
├── build-profile.json5
├── hvigorfile.ts
├── obfuscation-rules.txt
├── oh-package.json5
├── src/main/ets/pages/MessageSettingPage.ets  ⭐ 核心页面
├── src/main/module.json5
├── src/main/resources/（资源文件）
└── src/main/resources/base/profile/main_pages.json
```

### 2. 路由配置

```
Library/common/src/main/ets/constants/RouteMap.ts
（添加MSG_SETTING路由常量）
```

### 3. 系统设置页面集成

```
entry/src/main/ets/pages/main/mine/systemsetting/SystemSettingPage.ets
（添加通知设置入口）
```

### 4. 项目配置

```
build-profile.json5
（添加lib_msg_setting模块配置）

entry/oh-package.json5
（添加lib_msg_setting依赖）
```

### 5. 字符串资源（）

```
AppScope/resources/base/element/string.json
entry/src/main/resources/base/element/string.json
（仅包含新增的消息设置相关字符串）
```

### 6. 图片等资源