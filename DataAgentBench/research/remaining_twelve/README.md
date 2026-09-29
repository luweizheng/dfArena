# 后续十二个数据集

从保留的 dfArena-main/DataAgentBench 迁入 12 个目录、87 题。
metadata、context、全部 Parquet、任务、标准答案、评分器及共用评分辅助文件逐字节复制并校验 SHA-256；没有覆盖老师现有文件。
import-manifest.json 记录逐文件来源与核验值。

本次证明新旧 Parquet 及任务资产一致；十二个目录从最初 SQL/数据库到 Parquet 的全值核验仍待逐一补做，不将文件一致性等同于转换正确性。
这些任务未启动模型实验。语义澄清在独立研究材料中审阅，暂不改写原任务、hints、标准答案或评分器。
AG News 仍暂缓。未提交或推送 GitHub。
