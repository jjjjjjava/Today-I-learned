# getui_flutter 发布指南

## ✅ 已完成的工作

### 1. 项目重命名与结构调整
- ✅ 包名：`getuiflut` → `getui_flutter`
- ✅ 类名：`Getuiflut` → `GetuiFlutter`
- ✅ 版本号：`1.0.0`
- ✅ 主文件：`lib/getui_flutter.dart`
- ✅ iOS podspec：`ios/getui_flutter.podspec`
- ✅ Android group：`com.jjjjjjava.getui_flutter`

### 2. License 和版权
- ✅ LICENSE 文件包含原作者和你的版权声明
- ✅ 代码文件添加版权注释
- ✅ README 中致谢原作者

### 3. 文档完善
- ✅ README.md (11KB) - 完整的使用文档
- ✅ CHANGELOG.md - 详细的版本变更记录
- ✅ 示例代码更新
- ✅ API 文档完整

### 4. 代码质量
- ✅ `flutter analyze` - 无错误
- ✅ `flutter pub publish --dry-run` - 通过
- ✅ 所有测试文件更新

### 5. Git 仓库
- ✅ 清空原作者提交历史
- ✅ 创建全新的 initial commit
- ✅ 推送到 GitHub: https://github.com/jjjjjjava/getui_flutter

---

## 🚀 发布到 pub.dev

### 准备工作

1. **确认 pub.dev 账号**
   - 访问 https://pub.dev
   - 使用 Google 账号登录

2. **最后检查**
   ```bash
   cd D:\Develop\My_github\getuiflut
   flutter pub publish --dry-run
   ```

### 正式发布

```bash
# 1. 确保在正确的目录
cd D:\Develop\My_github\getuiflut

# 2. 发布到 pub.dev
flutter pub publish

# 3. 按照提示操作：
#    - 确认包名和版本
#    - 在浏览器中授权
#    - 等待发布完成
```

### 发布后

1. **创建 GitHub Release**
   - 访问 https://github.com/jjjjjjava/getui_flutter/releases
   - 点击 "Create a new release"
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - 复制 CHANGELOG.md 中的内容到 Release notes

2. **验证发布**
   - 访问 https://pub.dev/packages/getui_flutter
   - 检查包信息是否正确
   - 测试安装：`flutter pub add getui_flutter`

---

## 📦 版本更新流程

### 当需要发布新版本时：

1. **修改代码**
   ```bash
   git checkout -b feature/your-feature
   # 进行开发...
   git commit -m "feat: your feature"
   ```

2. **更新版本号和文档**
   ```yaml
   # pubspec.yaml
   version: 1.1.0  # 根据语义化版本规则更新
   ```
   
   ```markdown
   # CHANGELOG.md
   ## 1.1.0 - 2025-XX-XX
   
   ### Added
   - 新功能描述
   
   ### Fixed
   - Bug 修复描述
   ```

3. **测试和检查**
   ```bash
   flutter analyze
   flutter test
   flutter pub publish --dry-run
   ```

4. **提交和发布**
   ```bash
   git add .
   git commit -m "chore: bump version to 1.1.0"
   git push origin feature/your-feature
   
   # 合并到 main
   git checkout main
   git merge feature/your-feature
   git tag v1.1.0
   git push origin main --tags
   
   # 发布到 pub.dev
   flutter pub publish
   ```

---

## 🔄 同步原项目更新

### 添加上游仓库（首次）

```bash
git remote add upstream https://github.com/GetuiLaboratory/getui-flutter-plugin.git
git fetch upstream
```

### 同步更新

```bash
# 1. 获取上游更新
git fetch upstream

# 2. 创建同步分支
git checkout -b sync-upstream

# 3. 查看上游变更
git log upstream/main

# 4. 选择性合并（cherry-pick 特定 commit）
git cherry-pick <commit-hash>

# 或者合并所有更新
git merge upstream/main

# 5. 解决冲突（如果有）
# 手动编辑冲突文件...
git add .
git commit

# 6. 测试
flutter analyze
flutter test

# 7. 合并到主分支
git checkout main
git merge sync-upstream
git push origin main
```

---

## 📋 维护检查清单

### 每月
- [ ] 检查原项目是否有更新
- [ ] 处理 GitHub Issues
- [ ] 审查 Pull Requests

### 每季度
- [ ] 更新依赖版本
- [ ] 性能优化
- [ ] 文档完善

### 每年
- [ ] 重大版本规划
- [ ] 架构优化
- [ ] 社区反馈总结

---

## 🐛 常见问题

### Q: 发布失败，提示包名已存在
A: 检查 pub.dev 是否已有同名包。如果有，需要更改包名。

### Q: 如何撤回已发布的版本？
A: pub.dev 不支持删除已发布的版本。只能发布新版本修复问题。

### Q: 如何处理原作者的投诉？
A: 
1. 确保 LICENSE 文件完整保留原作者信息
2. 在 README 中明确说明这是 Fork 版本
3. 不声称是官方版本
4. 如有争议，友好沟通解决

### Q:报错

报错：(y/N)? y

Uploading... 

https://pub.flutter-io.cn package repository requested authentication!

You can provide credentials using:

    flutter pub token add https://pub.flutter-io.cn

Authentication is required, please add `authorization` header.

Authentication failed!

Failed to update packages.



根因定位：Flutter 配置使用的是中国镜像 https://pub.flutter-io.cn，但这个镜像需要认证。我们需要切换到官方的 pub.dev 进行发布。

```
PS D:\Develop\My_github\getuiflut> $env:PUB_HOSTED_URL
https://pub.flutter-io.cn
```



解决方案：临时清除环境变量

 $env:PUB_HOSTED_URL = ""; $env:FLUTTER_STORAGE_BASE_URL = ""; flutter pub publish

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/jjjjjjava/getui_flutter/issues
- **原项目**: https://github.com/GetuiLaboratory/getui-flutter-plugin
- **个推官网**: https://www.getui.com

---

## 📄 相关文档

- [Flutter Plugin 开发指南](https://flutter.dev/docs/development/packages-and-plugins/developing-packages)
- [pub.dev 发布指南](https://dart.dev/tools/pub/publishing)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [MIT License 说明](https://opensource.org/licenses/MIT)
