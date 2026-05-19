# Progress: 011 升Level 评估会话

## 2026-04-10 会话 1

### 已完成
- 读取 011.yaml 当前状态（Level 2, consecutive_success: 7）
- 读取 feedback_level_up.md 升级协议
- 读取 feedback_levelup_scope.md 选题范围约束
- 更新 feedback_level_up.md（合并范围约束，整合协议）
- 建立规划文件（task_plan.md / findings.md / progress.md）
- 初步网络搜索（音视频同步 + MediaExtractor 面试题）→ 写入 findings.md

### 当前状态
- 阶段 1-2 完成：6 道网络真题确认，进入阶段 3 逐题提问

### 题目顺序（按卡片结构排序）
1. 何为音视频同步，音视频同步是什么标准？
2. DTS 与 PTS 共同点？
3. 播放器暂停、快进快退、seek、逐帧、变速怎么实现？
4. mediaExtractor 中音频和视频数据是如何排列的？
5. mediaExtractor.getSampleTrackIndex() 是随机返回音频和视频轨道的 index 吗？
6. readSampleData 方法中 offset 有什么用？

### 评分记录（逐题）
| # | 题目 | 评分 | 备注 |
|---|------|------|------|
| 1 | 何为音视频同步，同步标准？ | excellent | 初答good（音频基准方案），追问后答出系统时间=解耦的本质（独立判断 vs 视频强耦合音频），升级为excellent |
| 2 | DTS 与 PTS 共同点？ | good | 初答偏题（答了差异+IBP编解码顺序+串联Baseline Profile），追问后答出共同点：都是时间戳标记处理顺序、无B帧时相等 |
| 3 | 暂停/seek/变速怎么实现？ | ok | 切到音频时间基准答题：seek流程（flush+IDR+更新PTS）答对，变速答简化。用户明确表示系统时间校准"记公式即可"→列入weak_points |
| 4 | MediaExtractor 中音视频数据如何排列？ | good | 卡片scope内答全（交替/moov+mdat/轨道描述+帧映射表/查表读取）；描述了AVCC读取流程（读长度前缀+帧数据）。超出scope的延伸有3处小偏差（MP4存raw AAC非ADTS / MediaExtractor不解析NAL header / 交织是chunk-based时间块）→记入findings新知识 |
| 5 | getSampleTrackIndex 是否随机返回？ | 跳过（out of scope） | 题目考察"单MediaExtractor多track"架构下的API使用，但011 notes记录的是"双MediaExtractor单track"架构，此API在项目中用不到。筛题失误，不计入升级判定 |
| 6 | readSampleData 的 offset 有什么用？ | good | 答对：写入 ByteBuffer 的起始偏移位置。简洁准确 |
