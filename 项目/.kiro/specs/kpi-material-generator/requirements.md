# Requirements Document

## Introduction

本系统旨在自动化生成月度 KPI 考核材料，通过解析工作日志（chat.md）并按照公司 KPI 考核维度进行智能分类、提炼和格式化输出。系统需要理解技术工作内容的业务价值，并以符合考核标准的语言风格呈现。

## Glossary

- **System**: KPI 材料生成系统
- **WorkLog**: 工作日志文件（chat.md），包含本月所有工作内容的原始记录
- **KpiDimension**: KPI 考核维度，共 7 个维度（业务贡献度、质量、AI应用等）
- **MaterialOutput**: 格式化的 KPI 材料输出，符合公司考核表风格
- **ContentClassifier**: 内容分类器，将工作内容映射到对应的 KPI 维度
- **HighlightExtractor**: 亮点提取器，从技术细节中提炼业务价值
- **QuantitativeMetric**: 量化指标，如完成数量、效率提升比例等

## Requirements

### Requirement 1

**User Story:** 作为 Android 开发人员，我希望系统能够解析我的工作日志，以便自动识别不同类型的工作内容

#### Acceptance Criteria

1. WHEN 用户提供工作日志文件路径 THEN THE System SHALL 读取并解析文件内容
2. WHEN 解析工作日志 THEN THE System SHALL 识别工作内容的行号范围（如 1-115 是招财猫）
3. WHEN 识别工作内容 THEN THE System SHALL 提取项目名称、功能模块、技术细节和时间信息
4. WHEN 工作内容包含 Git commit 信息 THEN THE System SHALL 解析 commit 类型（feat/fix/refactor/review）和描述
5. WHEN 工作内容包含问题描述 THEN THE System SHALL 识别问题根因、修复方案和影响范围

### Requirement 2

**User Story:** 作为 Android 开发人员，我希望系统能够将工作内容自动分类到对应的 KPI 维度，以便快速生成考核材料

#### Acceptance Criteria

1. WHEN 识别到新功能开发 THEN THE System SHALL 归类到"业务贡献度-产出"维度
2. WHEN 识别到架构设计或重构 THEN THE System SHALL 归类到"质量"维度
3. WHEN 识别到 ANR/Crash 问题定位与修复 THEN THE System SHALL 同时归类到"业务贡献度"和"质量"维度
4. WHEN 识别到 AI 工具使用记录 THEN THE System SHALL 归类到"AI应用落地成果"维度
5. WHEN 识别到跨部门协作内容 THEN THE System SHALL 归类到"协同性"维度
6. WHEN 识别到创新性技术方案 THEN THE System SHALL 归类到"创新性"维度
7. WHEN 一项工作内容符合多个维度 THEN THE System SHALL 支持多维度归类

### Requirement 3

**User Story:** 作为 Android 开发人员，我希望系统能够提炼工作亮点，以便突出业务价值和技术深度

#### Acceptance Criteria

1. WHEN 提炼业务贡献 THEN THE System SHALL 强调按时交付、提前交付和无故障上线
2. WHEN 提炼技术质量 THEN THE System SHALL 突出架构设计能力、问题定位能力和代码优化
3. WHEN 提炼 AI 应用 THEN THE System SHALL 量化效率提升比例（如 50-60%）
4. WHEN 提炼创新性 THEN THE System SHALL 描述技术方案的独特性和可复用性
5. WHEN 描述问题修复 THEN THE System SHALL 包含根因分析、方案选型和影响范围
6. WHEN 描述功能开发 THEN THE System SHALL 包含技术难点、实现方案和业务价值

### Requirement 4

**User Story:** 作为 Android 开发人员，我希望系统输出的材料符合公司 KPI 考核表的风格，以便直接用于绩效评估

#### Acceptance Criteria

1. WHEN 生成材料 THEN THE System SHALL 使用专业、简洁的技术语言
2. WHEN 描述功能 THEN THE System SHALL 采用"完成XX功能，具体如下："的格式
3. WHEN 列举子项 THEN THE System SHALL 使用"- "开头的列表格式
4. WHEN 描述技术细节 THEN THE System SHALL 包含关键技术点（如状态机、MQTT、异步释放）
5. WHEN 描述业务价值 THEN THE System SHALL 使用"支撑XX业务"、"提升XX效率"等表述
6. WHEN 描述问题修复 THEN THE System SHALL 包含"根因定位"、"方案选型"、"改造落地"三段式结构
7. WHEN 输出材料 THEN THE System SHALL 保持与参考 CSV 文件相同的语言风格和专业度

### Requirement 5

**User Story:** 作为 Android 开发人员，我希望系统能够生成量化指标，以便客观评估工作成果

#### Acceptance Criteria

1. WHEN 统计功能开发 THEN THE System SHALL 计算完成的功能模块数量
2. WHEN 统计问题修复 THEN THE System SHALL 计算修复的 ANR/Bug 数量和级别
3. WHEN 统计 AI 使用 THEN THE System SHALL 计算使用的 AI 工具数量和场景覆盖类别
4. WHEN 评估效率提升 THEN THE System SHALL 估算 AI 辅助带来的效率提升比例
5. WHEN 统计代码产出 THEN THE System SHALL 计算涉及的文件数量和代码行数（可选）
6. WHEN 统计协作 THEN THE System SHALL 识别跨部门协作的次数和对象

### Requirement 6

**User Story:** 作为 Android 开发人员，我希望系统支持自定义配置，以便适应不同月份的工作内容特点

#### Acceptance Criteria

1. WHEN 配置行号范围 THEN THE System SHALL 支持用户指定不同项目的行号区间
2. WHEN 配置项目名称 THEN THE System SHALL 支持用户自定义项目名称映射
3. WHEN 配置权重 THEN THE System SHALL 支持调整不同维度的重要性权重
4. WHEN 配置输出格式 THEN THE System SHALL 支持 Markdown 和纯文本两种格式
5. WHEN 配置语言风格 THEN THE System SHALL 支持调整专业度和详细程度

### Requirement 7

**User Story:** 作为 Android 开发人员，我希望系统输出结构清晰的材料，以便快速复制到 KPI 考核表

#### Acceptance Criteria

1. WHEN 输出材料 THEN THE System SHALL 按 7 个 KPI 维度分段输出
2. WHEN 输出每个维度 THEN THE System SHALL 包含标题、权重、自评分和详细内容
3. WHEN 输出详细内容 THEN THE System SHALL 使用二级标题区分不同项目或主题
4. WHEN 输出列表 THEN THE System SHALL 使用统一的缩进和符号格式
5. WHEN 输出完成 THEN THE System SHALL 在文件末尾生成总结和建议
