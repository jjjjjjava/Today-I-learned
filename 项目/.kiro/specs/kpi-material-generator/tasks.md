# Implementation Plan

- [ ] 1. 搭建项目基础结构
  - 创建 Python 项目目录结构（src/parser, src/classifier, src/extractor, src/formatter）
  - 配置 pyproject.toml 和依赖（pytest, hypothesis, pyyaml）
  - 创建配置文件模板（config.yaml）
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 2. 实现 Parser 模块
- [ ] 2.1 实现 WorkLogParser 核心类
  - 实现文件读取和编码检测（UTF-8/GBK/GB2312）
  - 实现行号范围解析（根据配置分割文件）
  - 实现 WorkItem 数据类
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 2.2 编写 Property 测试：文件解析完整性
  - **Property 1: 文件解析完整性**
  - **Validates: Requirements 1.1**

- [ ]* 2.3 编写 Property 测试：行号范围覆盖完整性
  - **Property 2: 行号范围覆盖完整性**
  - **Validates: Requirements 1.2**

- [ ] 2.4 实现 CommitParser 类
  - 实现 Git commit 格式解析（type/scope/message）
  - 支持多种 commit 格式（feat/fix/refactor/review/style）
  - _Requirements: 1.4_

- [ ]* 2.5 编写 Property 测试：Git commit 解析正确性
  - **Property 4: Git commit 解析正确性**
  - **Validates: Requirements 1.4**

- [ ] 2.6 实现 ContentParser 类
  - 提取项目名称（从标题或配置映射）
  - 提取技术细节列表（识别技术关键词）
  - 提取时间戳（解析日期格式）
  - _Requirements: 1.3_

- [ ]* 2.7 编写 Property 测试：信息提取完整性
  - **Property 3: 信息提取完整性**
  - **Validates: Requirements 1.3**

- [ ] 3. 实现 Classifier 模块
- [ ] 3.1 实现 RuleEngine 和分类规则
  - 定义 ClassificationRule 数据类
  - 实现关键词匹配逻辑
  - 实现 commit 类型匹配逻辑
  - 实现规则优先级排序
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 3.2 实现 DimensionClassifier 类
  - 实现单维度分类逻辑
  - 实现多维度归类支持
  - 实现分类置信度计算
  - _Requirements: 2.7_

- [ ]* 3.3 编写 Property 测试：功能开发分类正确性
  - **Property 5: 功能开发分类正确性**
  - **Validates: Requirements 2.1**

- [ ]* 3.4 编写 Property 测试：重构内容分类正确性
  - **Property 6: 重构内容分类正确性**
  - **Validates: Requirements 2.2**

- [ ]* 3.5 编写 Property 测试：ANR/Crash 多维度分类
  - **Property 7: ANR/Crash 多维度分类**
  - **Validates: Requirements 2.3**

- [ ]* 3.6 编写 Property 测试：AI 工具使用分类正确性
  - **Property 8: AI 工具使用分类正确性**
  - **Validates: Requirements 2.4**

- [ ]* 3.7 编写 Property 测试：多维度归类完整性
  - **Property 11: 多维度归类完整性**
  - **Validates: Requirements 2.7**

- [ ] 4. 实现 Extractor 模块
- [ ] 4.1 实现 HighlightExtractor 类
  - 实现业务贡献亮点提取（按时交付、提前交付、无故障）
  - 实现技术质量亮点提取（架构设计、问题定位、代码优化）
  - 实现 AI 应用亮点提取（工具使用、效率提升）
  - 实现创新性亮点提取（技术方案独特性）
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 4.2 实现问题修复描述生成
  - 生成"根因分析"段落
  - 生成"方案选型"段落
  - 生成"影响范围"段落
  - _Requirements: 3.5_

- [ ]* 4.3 编写 Property 测试：问题修复描述结构完整性
  - **Property 13: 问题修复描述结构完整性**
  - **Validates: Requirements 3.5**

- [ ] 4.4 实现功能开发描述生成
  - 生成"技术难点"段落
  - 生成"实现方案"段落
  - 生成"业务价值"段落
  - _Requirements: 3.6_

- [ ]* 4.5 编写 Property 测试：功能开发描述结构完整性
  - **Property 14: 功能开发描述结构完整性**
  - **Validates: Requirements 3.6**

- [ ] 4.6 实现 MetricCalculator 类
  - 实现功能数量统计（feat commit 计数）
  - 实现 Bug 修复统计（fix commit 计数，按级别分类）
  - 实现 AI 工具使用统计（工具数量、场景覆盖）
  - 实现效率提升估算（基于 AI 使用场景）
  - 实现协作次数统计（协作关键词计数）
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6_

- [ ]* 4.7 编写 Property 测试：功能数量统计准确性
  - **Property 20: 功能数量统计准确性**
  - **Validates: Requirements 5.1**

- [ ]* 4.8 编写 Property 测试：Bug 修复统计准确性
  - **Property 21: Bug 修复统计准确性**
  - **Validates: Requirements 5.2**

- [ ]* 4.9 编写 Property 测试：AI 工具数量统计准确性
  - **Property 22: AI 工具数量统计准确性**
  - **Validates: Requirements 5.3**

- [ ]* 4.10 编写 Property 测试：效率提升量化范围
  - **Property 12: 效率提升量化范围**
  - **Validates: Requirements 5.4**

- [ ] 5. 实现 Formatter 模块
- [ ] 5.1 实现 TemplateEngine 类
  - 集成 Jinja2 模板引擎
  - 创建 KPI 材料主模板（7 个维度结构）
  - 创建各维度子模板（业务贡献、质量、AI 应用等）
  - _Requirements: 4.2, 4.3, 7.1, 7.2, 7.3, 7.4_

- [ ] 5.2 实现 StyleAdapter 类
  - 实现语言风格适配（专业度、详细程度）
  - 实现特定表述模式生成（"完成XX功能，具体如下："）
  - 实现业务价值表述生成（"支撑XX业务"、"提升XX效率"）
  - _Requirements: 4.2, 4.5_

- [ ]* 5.3 编写 Property 测试：功能描述格式一致性
  - **Property 15: 功能描述格式一致性**
  - **Validates: Requirements 4.2**

- [ ]* 5.4 编写 Property 测试：列表格式一致性
  - **Property 16: 列表格式一致性**
  - **Validates: Requirements 4.3**

- [ ]* 5.5 编写 Property 测试：业务价值表述模式
  - **Property 18: 业务价值表述模式**
  - **Validates: Requirements 4.5**

- [ ] 5.6 实现 MarkdownGenerator 类
  - 实现 Markdown 格式输出
  - 实现纯文本格式输出
  - 实现特殊字符转义
  - _Requirements: 6.4_

- [ ]* 5.7 编写 Property 测试：输出格式切换正确性
  - **Property 27: 输出格式切换正确性**
  - **Validates: Requirements 6.4**

- [ ] 5.8 实现 KpiMaterialFormatter 主类
  - 整合所有子模块
  - 实现 7 个维度的材料生成
  - 实现总结和建议生成
  - _Requirements: 7.1, 7.2, 7.5_

- [ ]* 5.9 编写 Property 测试：七维度输出完整性
  - **Property 28: 七维度输出完整性**
  - **Validates: Requirements 7.1**

- [ ]* 5.10 编写 Property 测试：维度内容结构完整性
  - **Property 29: 维度内容结构完整性**
  - **Validates: Requirements 7.2**

- [ ]* 5.11 编写 Property 测试：输出末尾总结存在性
  - **Property 32: 输出末尾总结存在性**
  - **Validates: Requirements 7.5**

- [ ] 6. 实现风格相似度评估
- [ ] 6.1 实现 StyleSimilarityCalculator 类
  - 实现 TF-IDF 向量化
  - 实现余弦相似度计算
  - 加载参考 CSV 文件作为基准
  - _Requirements: 4.7_

- [ ]* 6.2 编写 Property 测试：语言风格相似度
  - **Property 19: 语言风格相似度**
  - **Validates: Requirements 4.7**

- [ ] 6.3 实现技术关键词保留检查
  - 提取输入中的技术关键词
  - 计算输出中的保留比例
  - _Requirements: 4.4_

- [ ]* 6.4 编写 Property 测试：技术关键词保留
  - **Property 17: 技术关键词保留**
  - **Validates: Requirements 4.4**

- [ ] 7. 实现配置管理
- [ ] 7.1 实现 ConfigManager 类
  - 加载 YAML 配置文件
  - 实现行号范围配置
  - 实现项目名称映射配置
  - 实现维度权重配置
  - 实现输出格式配置
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 7.2 编写 Property 测试：行号范围配置生效
  - **Property 24: 行号范围配置生效**
  - **Validates: Requirements 6.1**

- [ ]* 7.3 编写 Property 测试：项目名称映射生效
  - **Property 25: 项目名称映射生效**
  - **Validates: Requirements 6.2**

- [ ]* 7.4 编写 Property 测试：维度权重配置生效
  - **Property 26: 维度权重配置生效**
  - **Validates: Requirements 6.3**

- [ ] 8. 实现主程序和 CLI
- [ ] 8.1 实现 KpiGenerator 主类
  - 整合 Parser、Classifier、Extractor、Formatter
  - 实现端到端处理流程
  - 实现错误处理和日志记录
  - _Requirements: 所有_

- [ ] 8.2 实现 CLI 命令行接口
  - 使用 Click 库创建命令行工具
  - 支持参数：--input, --output, --config
  - 支持 --verbose 详细日志模式
  - _Requirements: 所有_

- [ ] 9. 端到端测试和优化
- [ ] 9.1 使用真实数据测试
  - 使用本月的 chat.md 作为输入
  - 对比生成的材料与人工编写的 CSV
  - 评估质量和准确性
  - _Requirements: 所有_

- [ ] 9.2 性能优化
  - 优化正则表达式匹配
  - 优化文本相似度计算
  - 添加缓存机制（可选）
  - _Requirements: 所有_

- [ ]* 9.3 编写集成测试
  - 测试完整的端到端流程
  - 测试不同配置组合
  - 测试边界情况（空文件、单行、超长行）
  - _Requirements: 所有_

- [ ] 10. 文档和部署
- [ ] 10.1 编写用户文档
  - README.md：项目介绍和快速开始
  - CONFIG.md：配置文件说明
  - EXAMPLES.md：使用示例
  - _Requirements: 所有_

- [ ] 10.2 创建示例配置文件
  - config.example.yaml：完整的配置示例
  - 包含本月工作内容的行号范围
  - 包含项目名称映射
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 11. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户
