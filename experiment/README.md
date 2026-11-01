# 实验结果与分析材料

本目录整理截至2026-11-01的已有结果，没有重新运行模型、改分或修改错误分类。

| 目录 | 内容 |
|---|---|
| [01_initial_results](01_initial_results/) | 主实验结果，分DAB与PrepBench |
| [02_harness_effect](02_harness_effect/) | harness影响实验，分DAB与PrepBench |
| [03_error_analysis](03_error_analysis/) | 两套benchmark的错误分类、统计、图表和人工复核 |

## 结果范围

| 主实验 | 正式有效运行 | 通过 | 未通过并已分类 |
|---|---:|---:|---:|
| DAB | 4,992 | 3,191 | 1,801 |
| PrepBench | 10,620 | 7,196 | 3,424 |

DAB为104题×4模型×3模式×4后端，PrepBench为295题×3模型×3模式×4后端。运行数不是独立题目数。

Harness分别保留DAB的720对（30题，GLM/Kimi）和PrepBench的600对（50题，GPT-6）。两个benchmark和主实验、harness实验均分别统计。历史对照包含时间、渠道、随机性及并发变化，不能据此证明纯harness因果效应或两者等效。

## 阅读与下载

先看各目录的summary、results或paired-results，以及03_error_analysis中的报告和图表。15,612条主实验中有10条原始结果与最终裁定不同，均有此前的评分修订支持，逐条对照见[SCORE_REVISIONS.md](SCORE_REVISIONS.md)。

[完整压缩附件](https://github.com/luweizheng/dfArena/releases/tag/experiment-evidence-20261101)与本目录位于同一个私有仓库。下载experiment-index.zip与所需类别的证据ZIP，解压到同一位置，合并成experiment/，然后打开START_HERE.html。完整审阅请下载全部ZIP。独立ZIP无需特定分卷软件；全部SHA256见SHA256SUMS.txt，逐包归属见asset-index.json。

每次运行的result.json、已保存的最终程序、CLI轨迹、Codex原生JSONL/OpenCode会话文本、评分与澄清记录均可从runs.jsonl或离线入口查到。OpenCode数据库只导出session/message/part表为JSONL，转换过程有明确标记。来源路径与导出路径、原始和导出SHA256分别记录。

## 口径与省略

- 按要求不上传生成的output.csv、answer.json、workspace/outputs等答案文件；日志里原本保存的执行输出保留。错误分析若引用这些文件，保留来源路径/哈希并标记主动省略。没有重评分，因此仅凭本包不能再次执行完整表格评分。
- 结果使用已确认的正式有效尝试，已记录的网络/容量中断替换和评分修订保留来源。原始result.json内容与最终裁定不一致时，联读effective-results-with-revisions及修订记录。DAB实际预算混合600/1800秒，不能写成全量1800秒。
- Harness基线严格使用该实验当时的冻结索引，保留事后补跑、已保存答案评分裁定及运营调整；不会用主实验后来更新的成绩替换历史配对结果。
- AI分类、人工标签、抽样与修订历史保持分开；样本一致率不是总体分类准确率。源报告制作时的历史说明保留，当前有效数量以本目录汇总为准。
- 为复核保留索引和分类证据明确引用的输入表、参考表及参考程序；这些来源证据与模型生成的output答案文件分别处理。运行环境、镜像、私密认证配置及密钥不包含在交付中。日志内凭据字符串只在导出副本中脱敏，原实验文件不变。
- 未生成或未保存的代码、轨迹不会补造，缺项见coverage-exceptions.json。来源绝对路径只是溯源信息，可访问的证据使用portable_file.path或files[].path，均相对experiment/。原protocol中的冻结文件哈希用于描述当时环境，已标注provenance_only，不表示这些环境文件也在附件中。

validation.json记录覆盖、分类、链接、CRC、SHA256、output排除和凭据检查。图表脚本及绘图数据随原分析材料保留；PrepBench复现入口为03_error_analysis/PrepBench/03_reproducibility/make_publication_figures.py --bundle 03_error_analysis/PrepBench。
