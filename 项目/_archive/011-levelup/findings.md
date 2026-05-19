# Findings: 011 升Level 面试题收集

## 前次错误记录（诚实复盘）
之前写在这里的"搜索发现的网络真实面试题"，其实是我根据搜索摘要**自己改写**的，不是页面原文。已删除重新收集。

## 真实访问过的页面清单
| URL | 结果 |
|-----|------|
| blog.csdn.net/zhying719/.../105852309 | 0 道相关题 |
| blog.csdn.net/fishmai/.../77680216 | 0 道相关题 |
| blog.csdn.net/nonmarking/.../78745646 | 0 道（正文付费墙） |
| blog.csdn.net/u012124438/.../129339850 | 3 道 ✅ |
| juejin.cn/post/7447094734684127243 | 0 道（叙述性文章） |
| github.com/JeffMony/AVInterview | README 空 |
| github.com/0voice/ffmpeg_develop_doc | 3 道 ✅ |
| blog.csdn.net/KQe397773106/.../136260832 | 0 道 |
| jianshu.com/p/3160cd496be9 | 0 道（1道修辞问句，不算） |
| JsonChao/Awesome-Android-Interview | 0 道（有知识点但非题目格式） |

## 从网页上提取到的真实面试题原文（共 6 道）

### 来源 1: CSDN「全面了解Android MediaExtractor」
1. readSampleData 方法中 offset 有什么用？
2. mediaExtractor.getSampleTrackIndex() 是随机返回音频和视频轨道的 index 吗？
3. mediaExtractor 中音频和视频数据是如何排列的？

### 来源 2: GitHub「0voice/ffmpeg_develop_doc」
4. DTS 与 PTS 共同点？（原题27）
5. 何为音视频同步，音视频同步是什么标准？（原题47）
6. 播放器暂停、快进快退、seek、逐帧、变速怎么实现？（原题48）

## 发现总结
- MediaExtractor 专项真题在国内面试题合集中极少（Android 特定 API，冷门）
- 音视频同步真题相对较多，但大多围绕 PTS/DTS 概念层
- 「代码封装结构」方向**完全没有**找到对应真题（这是用户项目代码结构，不是面试考点）
- 结论：网络真题 6 道已是相对全面的结果，再扩大搜索也难有新增

## 评估中的新收获（超出原 notes 范围）

### 1. 变速场景下的同步机制
- 快放 2x 的专业做法：音频 SoundTouch 变速不变调 → audioPTS 推进天然加倍 → 视频自动跟上
- 关键原理：**音频是同步的心跳，变速的本质是让心跳变快/变慢**
- 业余做法（音频不变速只丢视频帧）会导致音画不同步
- 系统时间基准下变速困难（需手动调整 mStartTimeForSync 增长速率）

### 2. 系统时间 vs 音频 PTS 的真正权衡
| 维度 | 系统时间 | 音频 PTS |
|------|---------|---------|
| 实现透明度 | 高（纯算术可打印） | 低（依赖黑盒 API） |
| 纯视频/无音频场景 | 直接适用 | 需 fallback 代码 |
| 变速支持 | 复杂 | 天然支持 |
| 生产项目采用率 | 低 | 高（ffplay/ijkplayer/ExoPlayer 默认） |
| 学习项目适合度 | 高 | 低 |
- 结论：011 项目选系统时间合理（学习型 demo），但生产播放器应选音频 PTS
- 用户判断"音频 PTS 更简单更好"是对的（在正常场景下）

## 下一步
- [x] 用户确认接受 6 道真题
- 进行到 Q4（MediaExtractor 方向第 1 题）
