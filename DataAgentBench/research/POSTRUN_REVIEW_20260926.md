# 2026-09-26 首轮后复核记录

## GITHUB_REPOS/task1：等价比例格式误判

题目未限定小数形式。Pandas 和 Polars 原答案均为 `33.33% (1 of 3 README.md files with available contents).`，原评分器只提取小数并直接与 0.33 比较，误把百分数 33.33 当成比例 33.33。

修正：先识别百分号、percent 或分数，再换算为比例；保持原有四舍五入到两位为 0.33 的判定条件。增加回归测试，覆盖正确小数/百分数/分数及错误百分数、负数、零分母等。未修改题目、hints、ground truth、Agent 代码或答案。仅对保留答案重新评分。按用户后续要求，旧失败判定及对应评分日志已覆盖为通过，并同步主记录、总报告及配对分析；生成代码、答案、轨迹、Agent 计时与费用保持不变。冻结输入保留原版本，当前评分器的路径与哈希记录在各题 detail/evaluation_validator.json 中。

## usaspending：源数据与说明不一致，待处理

原始 contracts.sql 与当前 contract_amounts.parquet 的 10,266 条记录逐行逐字段一致。无具体金额的定性描述已存在于原 SQL；原 hints 承诺所有金额均可精确解析，且旧金额有 _OLD 标记，但实际 _OLD 行数为 0，存在 345 组重复 award_id。不能通过 Parquet 迁移修复信息缺失。

本地 manual_querycode/llm_corrupt.py 写明金额叙述已弃用，而实际 SQL 仍含叙述；这是代码/说明与已交付数据不一致的证据。仅凭这一点尚不能确认是哪次上游发布造成。本地未找到 clean.sqlite 或 manifest.sqlite；不根据标准答案反推补造金额。

后续需取得与当前说明和答案一致的数据版本，或与老师确认这些题目的处理方式。当前不改数据、提示、答案或通过率口径。

## crmarenapro/task2：暂时接受两种政策答案，仍列为疑难问题

2026-09-27，用户明确决定：validate.py 同时接受 Volume-Based Discounts（ka0Wt000000Eq0MIAS）、Mandatory Bundles for Quotes（ka0Wt000000Ens5IAC）任意一种或两种一起输出；拒绝其他政策 ID 混入。保持 answer 字符串接口，增加正确组合、错误/截断/嵌入 ID 和混合答案回归检查。

这属于实验评分口径的临时放宽，不代表已经确认原作者或原标准答案有误。原政策要求 PulseSim Pro 配套另外两种产品，但原始数据中 209 张含该产品的报价没有一张同时单列两个配套品，其中 61 张两个都没单列却标记 Approved。知识库没有政策版本或生效日期，报价也没有明确的套装组成信息；未找到规则变更或隐藏套装的直接证明，亦无法彻底排除。因此与 agnews 一样，继续列入疑难问题，后续需复核政策适用时点、套装表示方式及上游评测意图。

题目、hints、数据和原 ground_truth.csv 保留；本题实际可接受答案由扩展后的 validate.py 判定。按用户要求，删除两种后端该题旧运行记录，使用原模型、预算、数据、提示与 Docker 镜像重新生成＋评分，覆盖主记录并更新汇总；保留新代码、答案、完整轨迹、修复观察、Agent 耗时和 token/费用记录。运行时冻结新版评分器并记录其哈希，不向解题 Agent 暴露评分器或本次调查结论。

完成情况：Pandas 与 Polars 均已重新生成并通过新版评分，均输出 ka0Wt000000Ens5IAC；Agent 耗时分别为 64.62 秒、62.25 秒。Pandas 首次重跑遇到计时内辅助服务连接异常，已删除后重试。旧两条运行记录和旧调度日志已删除，新记录覆盖主汇总；其他 206 条运行未改动。全量核对 208 条结果及原生会话、104 对输入和配置、3412 个冻结文件通过。当前总计 Pandas 83 通过 / 20 未通过 / 1 未评分，Polars 82 / 20 / 2。本题仍为疑难问题。
## cve/task2：接受本地可核实的两名并列厂商

2026-09-27，用户决定将评分器改为接受 fortinet 或 ivanti。原始 SQLite、SQL、BSON 与迁移后的 Parquet 核对一致；独立解码全部 68,367 条评分记录并核对全部 317 条 Known 勒索相关 KEV 记录后，本地能够确认的 CRITICAL 数为 Fortinet 4、Ivanti 4。两者分别有 13、12 条满足勒索条件的 KEV 记录，均达到至少 3 条的资格门槛。另有 9、6 条记录在当前本地输入中缺少严重度；缺失不当作非 CRITICAL，也不根据外部最新数据补造评分。

题目和现有 hints 未给出并列裁决规则。作者的数据构造代码引用非公开 clean.sqlite 与 manifest.sqlite，并声明保留原稿中所有非空数值评分；本地未找到干净底稿及本题生成标准答案的查询。因此这是用户确认的本地实验评分口径，不能据此断言原作者出错，也不能断言两者在完整外部目录中必然并列。

新版 validate.py 接受两个厂商中的任意一个，按题目要求返回单个名称；忽略首尾空白及大小写，拒绝其他厂商、嵌入子串和混合答案。原 ground_truth.csv 保留上游 fortinet 作为来源记录，实际接受范围由评分器明确列出。题目、hints 和数据均不改动，不向解题 Agent 暴露本次核查或可接受答案。

已有两种后端均回答 ivanti，可保留生成过程重新评分。两份生成程序均漏计了仅有西班牙语描述、但数值评分为 9.8 的 Fortinet CVE-2023-48788；即使最终答案被接受，这一程序漏计仍保留为错误分析证据，不能解释成计算过程完全正确。新增回归检查覆盖两个允许名称与误匹配边界。


完成情况（2026-09-27）：19 个回归案例全部通过。已使用原 Docker 评分流程对 Pandas、Polars 保留的 ivanti 答案重新评分，两者均通过，并覆盖原失败评分和相应评分日志；未重新生成。主汇总、旧 Pandas 汇总和配对分析已同步。评分器路径及 SHA256 记录在各运行的 detail/evaluation_validator.json，其他 206 条运行的 result/generation/evaluation 文件及本题两份生成过程文件核对未变。当前总计 Pandas 84 通过 / 19 未通过 / 1 未评分，Polars 83 / 19 / 2。详细证据位于本地复核输出的 cve-task2-rescore.json。

## civic_unstructured：用户确认年度街道养护归并口径

2026-09-27，用户确认：Annual Street Maintenance名称中的年份表示同一持续性项目的年度批次，不是独立项目；跨年度记录先归并，再按各题指定时间范围判断状态变化、汇总资金。该约定仅针对年度街道养护，不推广到其他带年份的工程。

已将以下英文条目加入共享context/hints.md一次，不附重复中文或括号译名：

> For Annual Street Maintenance, the year in the name identifies an annual cycle of the same ongoing project rather than a separate project. Combine this project's records across years, then apply the time range specified in each question to determine status changes and aggregate funding.

本次仅更新正式提示及变更记录。原运行、冻结输入、答案与评分保持原样，当前成绩仍对应旧提示；后续新运行须冻结新版hints，并记录新哈希。不得仅凭澄清已加入就将原失败改为通过。

第5题金额已对账，作者归并口径可复现参考答案；该澄清是用户确认的业务约定，不代表现实中年度工程只有一种划分方式。详见本地Civic第5题_年度工程归并口径核查.md。

## civic_unstructured：用户确认垃圾拦截网分期归并口径

2026-09-27，用户批准将Storm Drain Trash Screens及Phase Two视为同一项目的不同阶段，合并记录后按各题规定日期判断状态、汇总资金。仅约定这个项目，不推广到所有分期工程。

> For Storm Drain Trash Screens, treat "Storm Drain Trash Screens" and "Storm Drain Trash Screens Phase Two" as phases of the same project rather than separate projects. Combine their records, then determine status and aggregate funding using the dates specified in each question.

已加入共享英文hints一次；保留原年度养护澄清。用户同时要求对civic第10题Pandas、Polars重新生成＋评分并替换旧记录，实际运行及结果以本地civic-task10-rerun.json为准。只修改提示，题目、数据和评分器均不变。

报告rid_0010精确日期仍未核实；本次不为匹配参考答案添加日期指令。分期合并是经用户确认的统计粒度，不表示第二期当时在现实中已竣工。

## 三题英文澄清修复（2026-09-27）

用户要求将 bookreview/task1、stockindex/task3、googlelocal/task3 的中文运行澄清改为英文，并重新生成及评分。原始中文讨论作为研究记录保留，不再用作运行输入。agnews 暂缓，内容与运行均不改变。

- bookreview/task1: When calculating the average rating, each individual review has equal weight. Determine the publication decade using the publication date of the edition corresponding to the book entry in the provided data; if there are multiple editions, use the earliest published edition.
- stockindex/task3: From 2000 onward, invest a fixed amount monthly in each index, starting once data for that index becomes available, and buy at the closing price on the first trading day of each month. Compare overall returns using the cumulative rate of return: subtract total contributions from the final value of the accumulated holdings, then divide by total contributions. Use a common investment cutoff date for all indices: the earliest of their last available record dates. Value each index at its closing price on that date, or on the most recent trading day before it.
- googlelocal/task3: Exclude businesses marked as permanently or temporarily closed, even if operating hours remain recorded.

只翻译已经确认的语义，并以题号限定适用范围；不增加解题信息，不改数据、任务 query、答案或评分器。三后端共九次替代运行由本地 english-clarification-fix-20260927 记录；输入版本变更与技术故障重试分开记录。


## AG News：共享主旨澄清取代旧分类约定（2026-09-28）

用户采用一条通用澄清，保留原始两条 hints；撤下旧版科技企业经营、贸易争端、体育企业财务、球员转会、干细胞/克隆许可等额外具体约定。环境治理等候选未加入。

> When an article contains content relevant to multiple categories, consider its title and description together to determine the main focus of the report; do not treat the presence of a particular keyword or entity as decisive.

正式 context/hints.md 已更新，四题共用。历史逐题澄清标记为已被替代；本地新批次准备入口改为从正式 hints 复制，不再从旧试跑追加中文。题目、数据、标准答案和评分器不变。既有运行记录未更改，不能视作新版实验；尚未重新生成或评分。


## civic_unstructured: approved correction to rid_0010 meeting date (2026-09-28)

The user approved adding this source-verified correction to the formal shared English hints:

> According to the official complete meeting agenda, the meeting date for report rid_0010 is January 26, 2022; the date in the report header is incorrect.

Official source: https://www.malibucity.org/AgendaCenter/ViewFile/Agenda/1835?html=true. The complete agenda identifies the January 26, 2022 meeting and includes the matching report as item 4.A, while the attachment retains an obsolete October 2021 header. This supersedes the earlier unresolved-date status. Template reuse is a possible explanation, not a confirmed cause.

All existing hints are retained. The correction occurs once in each of the ten task prompts checked with Pandas, Polars and Ibis instructions. These are prompt assembly checks only, not model runs. Data, task queries, answers, validators, description and generation code are unchanged. Existing frozen inputs and results were not edited; future runs must freeze the updated hints. No Git commit, model generation or scoring was performed for this edit.


## civic_unstructured task1: exact project-set scoring (2026-09-28)

User approved replacing positive-name containment with exact selected-project-set validation. The reference names and existing alias map are unchanged. Missing names, extra identities (including unknown names), and conflicting inclusion/exclusion fail with diagnostics. Common lists, Markdown tables, JSON string lists and funding annotations are accepted. Explicit exclusions are distinguished from selected projects; unsupported prose produces a parsing diagnostic.

54 answer cases across 9 regression test methods passed. Both retained Pandas and Polars task1 answers pass a read-only check against the new validator. No retained run records, frozen inputs, model outputs or scores were overwritten; no new generation or Docker scoring was launched. Data, task query, hints, ground truth and other validators are unchanged. Future formal evaluation must record the new validator version. Evidence: C:\Users\Lenovo\Documents\Codex\2026-09-25\ni-x\outputs\civic-task1-validator-fix-20260928.json


## civic_unstructured task3: empty-result and exclusion scoring fix (2026-09-28)

User approved accepting explicit empty lists/sets and distinguishing named exclusions from positive funding-source selections. The validator now checks complete empty-result assertions, accepts unambiguous negative explanations, and rejects nonempty selections, contradictions and unsupported prose with diagnostics. The reference empty set and funding-source universe are unchanged.

54 cases in 6 test methods passed. Both retained task3 answers still fail: they positively select three sources. Read-only checks of tasks 1, 3 and 10 in Pandas and Polars retain pass/fail outcomes: task1 passes, task3 and task10 fail. No generated solutions, frozen inputs, existing evaluations or scores were overwritten. Formal generation/scoring was not launched. Data, queries, hints, ground truths and other validators are unchanged.

Further process review found that task1 also merges the guardrail and Malibu Park drainage pairs, but the retained intermediate tables classify them as disaster, so the capital-only filter removes them. Its correct final name set does not establish complete entity-resolution correctness. The old task1 runs predate the approved annual-maintenance unification and date correction. Detailed analysis and evidence are in the current task outputs.

## AG News：三个后端新版重新生成评分完成（2026-09-28）

四题使用正式共享英文hints：原两条规则加通用主旨澄清，旧具体分类约定不再追加。Pandas、Polars共八条旧运行已删除并替换；Ibis新增四条运行。模型、600秒预算、镜像、数据、题目、标准答案及评分器保持既定版本；生成＋评分，无重放。

| 后端 | 通过 | 未通过 | 未评分 |
|---|---:|---:|---:|
| pandas | 2 | 2 | 0 |
| polars | 2 | 1 | 1 |
| ibis | 1 | 3 | 0 |

因基础设施异常删除重试 3 次；正常解题超时和评分失败保留。全量292份现行提示未检出中文，12条新运行提示逐条核对，其他280条运行记录（不含临时work文件）哈希未变。

核查与当前结果：Codex工作目录 outputs/agnews-general-three-backends-20260928。此前中文运行与分类分析为旧版本证据；本次通过不等于所有逐篇分类正确，尚未完成逐篇语义复核。

## stockindex/task3：用户撤回定投专项澄清（2026-09-28）

用户决定移除 task3 的月度定投专项澄清，保留上游同时接受买入持有与月度定投两套名单的评分规则。本条取代前文“三题英文澄清修复”中 stockindex/task3 作为现行提示的状态；此前文字仅保留为历史记录。

已从正式 context/hints.md 删除整个 Clarification for task3 段落，保留原有四条通用 hints。题目、数据、ground_truth.csv 和 validate.py 不变。已有运行及其冻结输入、答案、评分均未改动；那些使用过专项澄清的运行仍属于旧提示版本，不能认作撤回澄清后的实验。后续新运行须读取当前正式 hints；本次未重新生成或评分。
## GITHUB_REPOS/task2：准确仓库名的简短答案评分修复（2026-09-28）

用户批准修改评分器：新增完整仓库名 SwiftAndroid/swift 的大小写不敏感直接匹配，支持简短答案及常见展示格式；原有固定窗口、最多3字符差异的模糊匹配分支原样保留。题目、hints、数据与参考答案不变。

本题19个案例通过，覆盖准确名称、大小写/空白/Markdown、原模糊匹配及错误答案；连同第1题既有20个案例，5个测试方法共39个案例通过。数据集其余22个文件哈希未变。既有运行和冻结输入未修改，尚未执行正式Docker重新评分或更新汇总。变更证据：C:/Users/Lenovo/Documents/Codex/2026-09-25/ni-x/outputs/github-task2-validator-fix-20260928。
## googlelocal/task2：整数评分格式修复并暂存重新评分（2026-09-28）

用户批准修改评分器并重新评分。数值识别现支持整数及小数，5、5.0、5.00 等价；保留原商家名单、10字符查找范围和四舍五入到两位小数的判定规则，同时保留数值符号以防负数被当作正数。22个检查案例通过，数据集其他16个文件哈希未变。

Pandas、Polars、Ibis 的原有答案均通过原 Docker 流程使用新版评分器重新评分。没有重新生成或执行解题代码，原代码、答案、轨迹、生成耗时和费用未变。新评分与评分器快照暂存在 C:/Users/Lenovo/Documents/Codex/2026-09-25/ni-x/outputs/googlelocal-task2-rescore-20260928，状态 rescored_pending_publication。按用户要求，等剩余问题处理完且 civic 完成后统一覆盖；本次未覆盖旧运行或更新共享汇总。
## PANCANCER_ATLAS/task1：格式及完整数值解析修复（2026-09-28）

按用户继续修改剩余评分问题的要求，评分器忽略 Markdown 加粗与代码标记，读取完整数值，避免原10字符截断造成误判；仍要求数值起点靠近对应编码、不跨越下一个组织学编码，保留原参考值及四位小数判定。新增26个案例通过，覆盖表格、加粗、完整精度、科学计数法、错误数值、负号、缺失或错配编码及句末句号。

初次新解析在已有答案复核中暴露句末句号被误当数值后缀的问题，已在最终版修正；googlelocal/task2 的新数值识别同步补齐这一兼容，检查案例扩充至24个。两题最终各三后端均通过 Docker 正式重新评分。过程中发现的暂存评分器回归不属于 Agent 解题失败，不计入正式实验成绩。

PANCANCER 数据集其余15个文件未变，原运行记录未覆盖。最终评分、评分器快照和新哈希位于当前对话 outputs/pancancer-task1-rescore-20260928、outputs/googlelocal-task2-rescore-20260928；等待用户完成剩余问题讨论后统一覆盖。未重新生成答案或执行解题程序，既有生成耗时、轨迹、费用保留。

## Civic 全目录三后端重跑（2026-09-28）

按用户授权使用 git2 已批准的英文 hints（含 rid_0010 日期）及第1、3题评分修订，30题次均重新生成＋评分，无重放。Pandas/Polars旧20条记录被替换，Ibis新增10条。

| 后端 | 通过 | 未通过 | 未评分 |
|---|---:|---:|---:|
| pandas | 4 | 6 | 0 |
| polars | 4 | 6 | 0 |
| ibis | 4 | 6 | 0 |

基础设施异常删除重试 9 次。最终核查302条当前记录、全英文提示和输入一致性通过；其他272条记录未改动。

第3题三个后端的答案均明确表示没有资金来源达到25%门槛，当前评分器未识别该表达，作为待复核评分边界保留，不修改冻结批次评分口径。详情与时间、费用、轨迹见 C:\Users\Lenovo\Documents\Codex\2026-09-21\ni-x\outputs\civic-three-backends-20260928。


## stockindex/task3：撤回专项澄清后重跑完成（2026-09-28）

用户授权对三个后端重新生成＋评分并覆盖原记录。现已完成，保留上游同时接受两套名单的评分器；新运行使用不含定投专项澄清的正式 hints，替代 9 月 27 日运行。总汇总、旧 Pandas 汇总及后端对比已更新。具体答案、通过情况、耗时与核查见 C:\Users\Lenovo\Documents\Codex\2026-09-25\ni-x\outputs\stockindex-no-hint-20260928\运行结果.md。


## 统一覆盖已完成的新运行与评分（2026-09-28）

用户授权现在覆盖此前暂存结果。Civic批次已完成并核查通过后，stockindex/task3 三份新版生成＋评分已替换；GITHUB_REPOS/task2、googlelocal/task2、PANCANCER_ATLAS/task1 共9份新评分已覆盖，均通过。重评分题的生成代码、答案、轨迹、计时和费用未改；所有当前记录与共享汇总已核对。CRM/task1 和 Civic/task3 尚待评分修复，未擅自改动。详情：C:\Users\Lenovo\Documents\Codex\2026-09-25\ni-x\outputs\consolidated-rescores-20260928\verification.json。


## 最后两项评分问题的用户决定（2026-09-29）

用户决定CRM第1题不改，维持当前评分规则和三个Authority答案的成绩；不再作为本轮待处理项。Civic第3题只补充明确25%门槛空结果表达的识别，75个测试案例通过。三个保留答案均通过原Docker流程重新评分，从未通过改为通过；评分记录和共享汇总已更新。原生成代码、答案、轨迹、计时和费用不变；未加hints、未重跑生成。Civic各后端现为5/10。

此前USAspending三后端30条新结果也已发布，Pandas/Polars替换旧20条、Ibis补10条；全项目17个数据集104题、三后端312条记录已齐。本条取代历史段落中的上述待处理状态。完整代码语义复核不在本次范围内。证据：C:\Users\Lenovo\Documents\Codex\2026-09-25\ni-x\outputs\civic-task3-threshold-publication-20260929\verification.json。
