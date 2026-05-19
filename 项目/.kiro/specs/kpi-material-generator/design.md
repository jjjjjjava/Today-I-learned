# Design Document

## Overview

KPI 材料生成系统采用管道式架构（Pipeline Architecture），将工作日志转换为结构化 KPI 材料的过程分解为：解析（Parse）→ 分类（Classify）→ 提炼（Extract）→ 格式化（Format）四个阶段。系统使用 Python 实现，利用正则表达式、规则引擎和模板引擎完成自动化处理。

## Architecture

```
┌─────────────┐
│  chat.md    │
│ (工作日志)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Parser (解析器)                     │
│  - LineRangeParser: 按行号范围分割   │
│  - CommitParser: 解析 Git commit    │
│  - ContentParser: 提取技术细节       │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Classifier (分类器)                 │
│  - RuleEngine: 规则匹配引擎          │
│  - DimensionMapper: 维度映射器       │
│  - MultiDimensionHandler: 多维度处理 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Extractor (提炼器)                  │
│  - HighlightExtractor: 亮点提取      │
│  - MetricCalculator: 指标计算        │
│  - ValueDescriber: 价值描述生成      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Formatter (格式化器)                │
│  - TemplateEngine: 模板引擎          │
│  - StyleAdapter: 风格适配器          │
│  - MarkdownGenerator: Markdown 生成  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│ output.md   │
│ (KPI 材料)  │
└─────────────┘
```

## Components and Interfaces

### 1. Parser Module

**WorkLogParser**
```python
class WorkLogParser:
    def parse(self, file_path: str, config: ParseConfig) -> List[WorkItem]
        """解析工作日志文件"""
        
class WorkItem:
    project_name: str          # 项目名称（如"招财猫"、"CameraClaw"）
    line_range: Tuple[int, int]  # 行号范围
    commit_type: str           # feat/fix/refactor/review
    title: str                 # 标题
    description: str           # 详细描述
    technical_details: List[str]  # 技术细节列表
    timestamp: Optional[datetime]  # 时间戳
```

**CommitParser**
```python
class CommitParser:
    def parse_commit(self, line: str) -> CommitInfo
        """解析 Git commit 格式"""
        # 示例: "feat(DMS)： 迁移Pos的DMS相关代码到本项目中"
        # 返回: CommitInfo(type="feat", scope="DMS", message="...")
```

### 2. Classifier Module

**DimensionClassifier**
```python
class DimensionClassifier:
    def classify(self, work_item: WorkItem) -> List[KpiDimension]
        """将工作内容分类到 KPI 维度"""
        
class KpiDimension(Enum):
    BUSINESS_OUTPUT = "业务贡献度-产出"      # 45%
    QUALITY = "质量"                        # 20%
    AI_PERSONAL = "AI应用落地成果-个人效能"  # 5%
    AI_DEPARTMENT = "部门/产品线AI落地价值"  # 10%
    WORKLOAD = "工作饱和度"                 # 10%
    COLLABORATION = "协同性"                # 5%
    INNOVATION = "创新性"                   # 5%
```

**RuleEngine**
```python
class RuleEngine:
    rules: List[ClassificationRule]
    
    def match(self, work_item: WorkItem) -> List[KpiDimension]
        """基于规则匹配维度"""
        
class ClassificationRule:
    keywords: List[str]        # 关键词列表
    commit_types: List[str]    # commit 类型
    dimension: KpiDimension    # 目标维度
    priority: int              # 优先级
```

### 3. Extractor Module

**HighlightExtractor**
```python
class HighlightExtractor:
    def extract_highlights(self, work_items: List[WorkItem], 
                          dimension: KpiDimension) -> List[Highlight]
        """提取工作亮点"""
        
class Highlight:
    title: str                 # 亮点标题
    description: str           # 详细描述
    technical_depth: str       # 技术深度说明
    business_value: str        # 业务价值说明
    metrics: Dict[str, Any]    # 量化指标
```

**MetricCalculator**
```python
class MetricCalculator:
    def calculate_feature_count(self, work_items: List[WorkItem]) -> int
        """统计功能数量"""
        
    def calculate_bug_fix_count(self, work_items: List[WorkItem]) -> Dict[str, int]
        """统计 Bug 修复数量（按级别）"""
        
    def calculate_ai_usage(self, work_items: List[WorkItem]) -> AiUsageMetrics
        """统计 AI 使用情况"""
        
class AiUsageMetrics:
    tool_count: int            # 使用的 AI 工具数量
    scenario_count: int        # 覆盖的场景类别数
    efficiency_gain: float     # 效率提升比例
```

### 4. Formatter Module

**KpiMaterialFormatter**
```python
class KpiMaterialFormatter:
    def format(self, classified_items: Dict[KpiDimension, List[WorkItem]],
              highlights: Dict[KpiDimension, List[Highlight]],
              metrics: Dict[str, Any]) -> str
        """格式化输出 KPI 材料"""
        
class TemplateEngine:
    def render(self, template_name: str, context: Dict) -> str
        """渲染模板"""
```

## Data Models

### WorkItem
```python
@dataclass
class WorkItem:
    id: str
    project_name: str
    line_range: Tuple[int, int]
    commit_type: str
    title: str
    description: str
    technical_details: List[str]
    timestamp: Optional[datetime]
    raw_content: str
```

### ClassifiedWorkItem
```python
@dataclass
class ClassifiedWorkItem:
    work_item: WorkItem
    dimensions: List[KpiDimension]
    confidence: float  # 分类置信度
```

### KpiMaterial
```python
@dataclass
class KpiMaterial:
    dimension: KpiDimension
    weight: float
    self_score: float
    content: str
    highlights: List[Highlight]
    metrics: Dict[str, Any]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: 文件解析完整性

*For any* 有效的工作日志文件路径，解析函数应成功返回文件内容，不抛出异常；对于无效路径，应抛出 FileNotFoundError
**Validates: Requirements 1.1**

### Property 2: 行号范围覆盖完整性

*For any* 行号范围配置和工作日志文件，解析后的所有 WorkItem 的 line_range 应完全覆盖配置中指定的范围，且不重叠
**Validates: Requirements 1.2**

### Property 3: 信息提取完整性

*For any* 包含完整信息的工作内容文本，解析后的 WorkItem 应包含非空的 project_name、title 和 description 字段
**Validates: Requirements 1.3**

### Property 4: Git commit 解析正确性

*For any* 符合 "type(scope): message" 格式的字符串，解析后的 CommitInfo 的 type、scope 和 message 应与原始字符串对应部分完全匹配
**Validates: Requirements 1.4**

### Property 5: 功能开发分类正确性

*For any* commit_type 为 "feat" 的 WorkItem，其必定被分类到 "业务贡献度-产出" 维度
**Validates: Requirements 2.1**

### Property 6: 重构内容分类正确性

*For any* commit_type 为 "refactor" 或 title 包含 "重构"、"架构" 关键词的 WorkItem，其必定被分类到 "质量" 维度
**Validates: Requirements 2.2**

### Property 7: ANR/Crash 多维度分类

*For any* title 或 description 包含 "ANR" 或 "Crash" 关键词的 WorkItem，其必定同时被分类到 "业务贡献度-产出" 和 "质量" 两个维度
**Validates: Requirements 2.3**

### Property 8: AI 工具使用分类正确性

*For any* description 包含 AI 工具名称（如 "Claude"、"Cursor"、"Kiro"）的 WorkItem，其必定被分类到 "AI应用落地成果-个人效能" 维度
**Validates: Requirements 2.4**

### Property 9: 跨部门协作分类正确性

*For any* description 包含 "协作"、"对接"、"沟通" 等关键词的 WorkItem，其必定被分类到 "协同性" 维度
**Validates: Requirements 2.5**

### Property 10: 创新技术方案分类正确性

*For any* description 包含 "状态机"、"架构设计"、"创新" 等关键词的 WorkItem，其必定被分类到 "创新性" 维度
**Validates: Requirements 2.6**

### Property 11: 多维度归类完整性

*For any* 被分类到 N 个维度的 WorkItem，在最终输出的 N 个维度材料中都应能找到该 WorkItem 的相关描述
**Validates: Requirements 2.7**

### Property 12: 效率提升量化范围

*For any* AI 使用场景的效率提升估算，输出的百分比值应在 0% 到 100% 之间
**Validates: Requirements 3.3, 5.4**

### Property 13: 问题修复描述结构完整性

*For any* 问题修复类 WorkItem 的输出描述，应包含 "根因"、"方案" 和 "影响" 三个关键词或其同义词
**Validates: Requirements 3.5, 4.6**

### Property 14: 功能开发描述结构完整性

*For any* 功能开发类 WorkItem 的输出描述，应包含 "技术"、"实现" 和 "业务" 三个关键词或其同义词
**Validates: Requirements 3.6**

### Property 15: 功能描述格式一致性

*For any* 功能开发类 WorkItem 的输出，应匹配正则表达式 ".*功能.*具体如下：" 或类似模式
**Validates: Requirements 4.2**

### Property 16: 列表格式一致性

*For any* 输出材料中的列表项，应全部以 "- " 或 "  - " 开头（支持两级缩进）
**Validates: Requirements 4.3**

### Property 17: 技术关键词保留

*For any* WorkItem 的 technical_details 中包含的技术关键词，在输出材料中应至少保留 80%
**Validates: Requirements 4.4**

### Property 18: 业务价值表述模式

*For any* 输出材料中描述业务价值的段落，应包含 "支撑"、"提升"、"优化"、"解决" 等动词之一
**Validates: Requirements 4.5**

### Property 19: 语言风格相似度

*For any* 生成的 KPI 材料，与参考 CSV 文件的文本相似度（使用 TF-IDF 余弦相似度）应 ≥ 0.7
**Validates: Requirements 4.7**

### Property 20: 功能数量统计准确性

*For any* WorkItem 列表，统计的功能数量应等于 commit_type 为 "feat" 的 WorkItem 数量
**Validates: Requirements 5.1**

### Property 21: Bug 修复统计准确性

*For any* WorkItem 列表，统计的 Bug 修复数量应等于 commit_type 为 "fix" 的 WorkItem 数量
**Validates: Requirements 5.2**

### Property 22: AI 工具数量统计准确性

*For any* WorkItem 列表，统计的 AI 工具数量应等于 description 中出现的不同 AI 工具名称的数量
**Validates: Requirements 5.3**

### Property 23: 协作次数统计准确性

*For any* WorkItem 列表，统计的协作次数应等于 description 中包含协作关键词的 WorkItem 数量
**Validates: Requirements 5.6**

### Property 24: 行号范围配置生效

*For any* 用户指定的行号范围配置，解析后的 WorkItem 应严格按照配置的范围进行分割
**Validates: Requirements 6.1**

### Property 25: 项目名称映射生效

*For any* 用户配置的项目名称映射（如 "CameraClaw" → "AI 视频助手"），输出材料中应使用映射后的名称
**Validates: Requirements 6.2**

### Property 26: 维度权重配置生效

*For any* 用户配置的维度权重，输出材料中每个维度的权重值应与配置一致
**Validates: Requirements 6.3**

### Property 27: 输出格式切换正确性

*For any* 输出格式配置（Markdown 或纯文本），生成的文件应符合对应格式的语法规范
**Validates: Requirements 6.4**

### Property 28: 七维度输出完整性

*For any* 生成的 KPI 材料，应包含所有 7 个 KPI 维度的标题，即使某个维度内容为空
**Validates: Requirements 7.1**

### Property 29: 维度内容结构完整性

*For any* 输出材料中的每个维度，应包含标题、权重、自评分和详细内容四个部分
**Validates: Requirements 7.2**

### Property 30: 二级标题使用正确性

*For any* 维度的详细内容中包含多个项目时，应使用二级标题（##）区分不同项目
**Validates: Requirements 7.3**

### Property 31: 列表缩进一致性

*For any* 输出材料中的所有列表项，同级列表项应使用相同的缩进空格数
**Validates: Requirements 7.4**

### Property 32: 输出末尾总结存在性

*For any* 生成的 KPI 材料，文件末尾应包含 "总结" 或 "建议" 关键词的段落
**Validates: Requirements 7.5**

## Error Handling

### 1. 文件读取错误
- 文件不存在：抛出 FileNotFoundError 并提示正确路径
- 编码错误：尝试 UTF-8、GBK、GB2312 三种编码，失败则提示用户
- 权限错误：提示用户检查文件权限

### 2. 解析错误
- 行号范围超出文件范围：警告并自动截断到文件末尾
- Git commit 格式不规范：降级为普通文本处理，记录警告日志
- 时间戳解析失败：设置为 None，不影响其他处理

### 3. 分类错误
- 无法匹配任何维度：归类到"业务贡献度-产出"（默认维度）
- 规则冲突：按优先级选择，记录冲突日志供用户审查

### 4. 格式化错误
- 模板渲染失败：使用简化模板降级输出
- 特殊字符转义：自动处理 Markdown 特殊字符

## Testing Strategy

### Unit Tests
- Parser 模块：测试各种 commit 格式、行号范围、特殊字符
- Classifier 模块：测试规则匹配、多维度归类、边界情况
- Extractor 模块：测试亮点提取、指标计算的准确性
- Formatter 模块：测试模板渲染、风格适配

### Property-Based Tests
- 使用 Hypothesis 库生成随机 WorkItem 数据
- 验证 Property 1-6 在大量随机输入下的正确性
- 每个 property 运行至少 100 次迭代

### Integration Tests
- 端到端测试：使用真实的 chat.md 文件
- 对比输出与人工编写的 KPI 材料，评估质量
- 测试不同配置组合的兼容性

### Test Data
- 使用本月的 chat.md 作为真实测试数据
- 创建简化的 mock 数据用于单元测试
- 创建边界情况测试数据（空文件、单行、超长行等）
