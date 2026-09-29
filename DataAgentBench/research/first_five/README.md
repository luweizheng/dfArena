# 前五个 DataAgentBench 目录：迁入记录与待确认材料

2026-09-23，在老师 `d8278e1` 基线上准备首批五个目录，共 17 道原始任务、11 张 Parquet 表。

| 数据集 | 任务数 | 数据表数 | 本次处理 |
|---|---:|---:|---|
| bookreview | 3 | 2 | 核心资产与旧版及老师 Git 原文一致，保留现有文件 |
| stockindex | 3 | 2 | 核心资产与旧版及老师 Git 原文一致，保留现有文件 |
| music_brainz_20k | 3 | 2 | 迁入 metadata、context、data、tasks |
| googlelocal | 4 | 2 | 迁入 metadata、context、data、tasks |
| agnews | 4 | 3 | 迁入 metadata、context、data、tasks |

这些表已在源 SQL／SQLite／DuckDB／BSON 与 Parquet 之间完成全量核对：441,968 行、2,277,261 个单元格一致。迁入后又检查文件指纹、清单、行列数及任务标识。`import-manifest.json` 提供逐文件来源和核验指纹；两个已存在目录的工作区文本可能使用 CRLF，但老师 Git 原文与旧项目字节一致。

GoogleLocal 第三题的评分器保留旧项目已经确认的星期区间全称／缩写兼容修复；这一项属于明确的历史修改，不能声称其与最初 DataAgentBench 评分器完全相同。其参考答案与原始数据未改。

## 澄清草稿：研究端材料，尚未成为本轮实验输入

`clarification_drafts/` 保存 4 份当前 revision 与 8 份当前澄清 task.json。它们按原数据集名组织，不带 metadata/data/answer，因此不构成额外正式数据集。草稿及其来源记录供研究者逐题复核，不应将这个研究目录挂载给解题 agent 或 simulator。

- bookreview：task1。
- stockindex：task1–3；task1、task2 已有 hints 覆盖，后续合并时检查重复。
- googlelocal：task3。
- agnews：task2–4；保存的是当前重新确认的文本，不恢复 CHANGES.md 中已替代或撤销的旧版本。
- music_brainz_20k：此前没有创建已批准的语义澄清版，后续仍按题复核。

revision 中可能引用旧运行目录；旧结果仍留在 dfArena-main 中追溯，本次没有复制或重新执行。没有迁入旧的 analysis/output、旧 runner、环境或认证配置。

## 当前约定与后续步骤

正式流程采用生成＋评分，时间统计解题 agent 的探索、写代码、自测和修复，排除 Docker 启动与清理。独立重放不接回正式主流程。原始任务与 hints 在本次迁入中保持原样。

接下来先逐题确认并去重合并 hints 与必要澄清：存在多种合理解释、且导致不同结果时才补充业务口径。完整需求 S0 使用确认后的材料；不完整需求 S0 仅直接提供数据与原任务，通过 simulator 获取澄清。simulator 的协议与入口仍待接入，现有 generator 会直接挂载 context，不能直接冒充不完整需求组运行。S1 留待 S0 开发结果后讨论。

本次只完成材料迁入和文件核对，没有启动实验，也没有创建提交或上传 GitHub。首批五目录的新流程完成后，再按用户约定整理协作交付。
