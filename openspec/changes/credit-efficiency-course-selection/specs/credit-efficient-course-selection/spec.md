## Purpose

根据课程页面公开的播放时长和可计学时，持续选择满足当前类别缺口的最短总播放时间课程组合，同时保持平台正常播放、完成确认和已完成课程排除规则。

## ADDED Requirements

### Requirement: Capture credit-bearing course metadata

课程目录 SHALL 保存每门课程的播放时长、可计学时、课程类别、稳定标识和页面定位信息。可计学时 SHALL 来自课程卡片或详情页的明确字段，不得根据视频时长推测。

#### Scenario: Card exposes both values
- **WHEN** 课程卡片同时显示有效播放时长和可计学时
- **THEN** 系统 SHALL 将两个数值写入目录，并记录字段来源为卡片

#### Scenario: Detail page provides authoritative value
- **WHEN** 课程卡片和详情页都提供可计学时但数值不一致
- **THEN** 系统 SHALL 使用详情页数值作为最终值，更新目录并记录一次字段冲突诊断

#### Scenario: Credit value is unavailable
- **WHEN** 课程卡片和详情页均未提供可解析的可计学时
- **THEN** 系统 SHALL 将课程标记为学时未知，不得把未知值当作零学时或用于最优组合，并按配置的降级策略处理

### Requirement: Select the shortest feasible course combination

对于选定课程类别，系统 SHALL 根据当前剩余学时缺口选择累计可计学时达到缺口的课程组合，并以组合的总播放分钟数最小为首要目标。已完成和本次运行失败的课程 SHALL 被排除。

#### Scenario: Exact combination exists
- **WHEN** 候选课程中存在累计学时恰好覆盖缺口的组合
- **THEN** 系统 SHALL 选择总播放时长最短的该组合

#### Scenario: Overshoot is necessary
- **WHEN** 没有组合能恰好覆盖缺口但存在可覆盖缺口的组合
- **THEN** 系统 SHALL 在满足缺口的组合中最小化总播放时长，并以超出学时更少作为次级排序条件

#### Scenario: No feasible known-credit combination
- **WHEN** 已知学时课程的总和不足以覆盖缺口
- **THEN** 系统 SHALL 学习当前可行候选并报告剩余缺口，不得宣称类别已达标

### Requirement: Recalculate after each confirmed course

系统 SHALL 在每门课程真实播放完成并完成现有确认流程后，使用最新可读的已完成学时重新计算类别缺口和后续课程选择。课程本地记录只有在既有播放完成条件满足后才能写入。

#### Scenario: Completion changes the optimal choice
- **WHEN** 一门课程完成后服务端学时到账，使剩余缺口改变
- **THEN** 系统 SHALL 丢弃旧组合计划并按新缺口重新选择

#### Scenario: Credit dashboard is temporarily stale
- **WHEN** 播放完成后学时面板暂未反映新增学时
- **THEN** 系统 SHALL 保留课程完成记录，等待下一次配置的学时刷新，不得重复选择同一课程或把旧缺口当作已确认的新数据

### Requirement: Preserve normal playback and compatibility

课程选择优化 SHALL 不改变视频的真实 1 倍速播放、在线确认、完成弹窗处理、失败重试和页面生命周期规则。旧版仅含播放时长的课程目录 SHALL 可被读取，并在无法补全学时字段时按明确降级策略运行。

#### Scenario: Existing catalog lacks credit metadata
- **WHEN** 加载到旧版目录条目且条目没有可计学时
- **THEN** 系统 SHALL 保留条目但将其标记为待补全，不得静默赋予默认学时

#### Scenario: Playback behavior remains unchanged
- **WHEN** 系统根据新排序进入课程
- **THEN** 系统 SHALL 仍要求视频以正常速度真实播放到结束，并沿用现有完成确认和持久化规则
