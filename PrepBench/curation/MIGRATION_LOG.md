## interact 结果总览


下表是当前 benchmark 的初步审核实验表，不是最终 benchmark 分数。它用不同 backend 的 interact 结果暴露 workload 需求表述、simulator 澄清信息和 evaluator 验证规则中的问题：有些失败来自 agent 的真实计算错误，有些来自需求没有清晰表达，有些来自验证规则覆盖不足。因此，这些结果用于指导后续 curation 和资产修订，不能直接解释为 backend 能力排名。`通过/失败` 指对应运行时配置下 interact 生成后的 evaluator 状态；`跳过` 表示生成记录存在但评测未执行；`未运行` 表示目前没有该 backend 的 interact 结果；`不纳入` 表示已决定排除出 benchmark，不再安排运行。

| Case | pandas | Polars | Ibis | PySpark |
| --- | --- | --- | --- | --- |
| 001 | 通过 | 通过 | 通过 | 通过 |
| 002 | 通过 | 通过 | 失败 | 通过 |
| 003 | 通过 | 通过 | 通过 | 通过 |
| 004 | 失败 | 失败 | 失败 | 失败 |
| 005 | 通过 | 通过 | 通过 | 通过 |
| 006 | 通过 | 通过 | 通过 | 失败 |
| 007 | 通过 | 通过 | 通过 | 未运行 |
| 008 | 通过 | 失败 | 失败 | 未运行 |
| 010 | 通过 | 失败 | 未运行 | 失败 |
| 011 | 通过 | 未运行 | 通过 | 通过 |
| 012 | 通过 | 通过 | 通过 | 未运行 |
| 013 | 失败 | 通过 | 通过 | 未运行 |
| 014 | 通过 | 通过 | 通过 | 未运行 |
| 015 | 失败 | 未运行 | 失败 | 失败 |
| 016 | 通过 | 通过 | 通过 | 未运行 |
| 017 | 通过 | 通过 | 通过 | 通过 |
| 018 | 通过 | 通过 | 未运行 | 通过 |
| 019 | 通过 | 未运行 | 通过 | 失败 |
| 020 | 通过 | 未运行 | 通过 | 通过 |
| 021 | 通过 | 通过 | 未运行 | 通过 |
| 022 | 通过 | 未运行 | 通过 | 通过 |
| 023 | 通过 | 通过 | 未运行 | 通过 |
| 024 | 通过 | 未运行 | 失败 | 失败 |
| 025 | 失败 | 未运行 | 失败 | 失败 |
| 026 | 通过 | 未运行 | 通过 | 通过 |
| 027 | 通过 | 未运行 | 通过 | 通过 |
| 028 | 通过 | 通过 | 未运行 | 通过 |
| 029 | 通过 | 通过 | 通过 | 未运行 |
| 030 | 失败 | 失败 | 未运行 | 失败 |
| 031 | 通过 | 未运行 | 失败 | 通过 |
| 032 | 通过 | 未运行 | 通过 | 通过 |
| 033 | 失败 | 失败 | 失败 | 未运行 |
| 034 | 通过 | 通过 | 未运行 | 通过 |
| 035 | 失败 | 失败 | 未运行 | 通过 |
| 036 | 失败 | 未运行 | 失败 | 失败 |
| 037 | 通过 | 通过 | 失败 | 未运行 |
| 038 | 通过 | 通过 | 未运行 | 通过 |
| 039 | 通过 | 未运行 | 通过 | 通过 |
| 040 | 失败 | 失败 | 失败 | 未运行 |
| 041 | 通过 | 失败 | 失败 | 失败 |
| 042 | 失败 | 失败 | 通过 | 未运行 |
| 043 | 通过 | 通过 | 未运行 | 通过 |
| 044 | 通过 | 未运行 | 通过 | 通过 |
| 045 | 失败 | 通过 | 通过 | 失败 |
| 046 | 失败 | 失败 | 失败 | 失败 |
| 047 | 通过 | 跳过 | 跳过 | 通过 |
| 048 | 通过 | 通过 | 通过 | 通过 |
| 049 | 通过 | 通过 | 失败 | 通过 |
| 050 | 失败 | 失败 | 失败 | 失败 |
| 051 | 通过 | 通过 | 通过 | 未运行 |
| 052 | 通过 | 通过 | 通过 | 未运行 |
| 053 | 通过 | 失败 | 未运行 | 通过 |
| 054 | 失败 | 通过 | 通过 | 未运行 |
| 055 | 通过 | 通过 | 通过 | 未运行 |
| 056 | 通过 | 通过 | 未运行 | 通过 |
| 057 | 不纳入 | 不纳入 | 不纳入 | 不纳入 |
| 058 | 通过 | 未运行 | 通过 | 通过 |
| 059 | 失败 | 失败 | 未运行 | 失败 |
| 060 | 通过 | 未运行 | 通过 | 通过 |
| 061 | 通过 | 未运行 | 通过 | 通过 |
| 062 | 通过 | 通过 | 未运行 | 通过 |
| 063 | 失败 | 未运行 | 通过 | 失败 |
| 064 | 通过 | 通过 | 通过 | 未运行 |
| 065 | 通过 | 通过 | 通过 | 未运行 |
| 066 | 通过 | 通过 | 通过 | 未运行 |
| 067 | 通过 | 失败 | 通过 | 通过 |
| 068 | 通过 | 未运行 | 通过 | 通过 |
| 069 | 通过 | 通过 | 未运行 | 通过 |
| 070 | 通过 | 未运行 | 失败 | 失败 |
| 071 | 未运行 | 未运行 | 通过 | 通过 |
| 072 | 通过 | 失败 | 失败 | 未运行 |
| 073 | 通过 | 通过 | 通过 | 未运行 |
| 074 | 未运行 | 未运行 | 通过 | 通过 |
| 075 | 通过 | 通过 | 通过 | 未运行 |
| 076 | 通过 | 通过 | 未运行 | 未运行 |
| 077 | 失败 | 未运行 | 失败 | 失败 |
| 078 | 通过 | 通过 | 未运行 | 通过 |
| 079 | 通过 | 通过 | 通过 | 未运行 |
| 220 | 通过 | 通过 | 通过 | 未运行 |
| 221 | 通过 | 未运行 | 通过 | 通过 |
| 222 | 通过 | 通过 | 通过 | 未运行 |
| 223 | 通过 | 未运行 | 通过 | 通过 |
| 224 | 通过 | 未运行 | 通过 | 通过 |
| 225 | 通过 | 通过 | 未运行 | 通过 |
| 226 | 通过 | 通过 | 通过 | 未运行 |
| 227 | 通过 | 未运行 | 通过 | 通过 |
| 228 | 通过 | 未运行 | 通过 | 通过 |
| 229 | 通过 | 通过 | 通过 | 未运行 |
| 230 | 通过 | 未运行 | 通过 | 通过 |
| 231 | 通过 | 通过 | 未运行 | 通过 |
| 232 | 通过 | 通过 | 通过 | 未运行 |
| 233 | 通过 | 通过 | 未运行 | 通过 |
| 234 | 不纳入 | 不纳入 | 不纳入 | 不纳入 |
| 235 | 通过 | 通过 | 未运行 | 通过 |
| 236 | 通过 | 未运行 | 通过 | 通过 |
| 237 | 失败 | 失败 | 通过 | 未运行 |
| 238 | 通过 | 通过 | 未运行 | 通过 |
| 239 | 通过 | 通过 | 通过 | 未运行 |
| 240 | 通过 | 未运行 | 通过 | 通过 |
| 241 | 通过 | 未运行 | 通过 | 通过 |
| 242 | 通过 | 未运行 | 通过 | 通过 |
| 243 | 通过 | 通过 | 未运行 | 通过 |
| 244 | 通过 | 未运行 | 通过 | 通过 |
| 245 | 通过 | 未运行 | 通过 | 通过 |
| 246 | 通过 | 通过 | 通过 | 未运行 |
| 247 | 通过 | 通过 | 未运行 | 通过 |
| 248 | 通过 | 未运行 | 通过 | 通过 |
| 249 | 通过 | 通过 | 通过 | 未运行 |
| 250 | 通过 | 通过 | 通过 | 未运行 |
| 251 | 不纳入 | 不纳入 | 不纳入 | 不纳入 |
| 252 | 通过 | 通过 | 未运行 | 通过 |
| 253 | 通过 | 未运行 | 通过 | 通过 |
| 254 | 通过 | 未运行 | 通过 | 通过 |
| 255 | 通过 | 通过 | 未运行 | 通过 |
| 256 | 通过 | 通过 | 未运行 | 通过 |
| 257 | 通过 | 通过 | 通过 | 未运行 |
| 258 | 通过 | 未运行 | 通过 | 通过 |
| 259 | 通过 | 通过 | 未运行 | 通过 |
| 260 | 通过 | 未运行 | 通过 | 通过 |
| 261 | 通过 | 未运行 | 通过 | 通过 |
| 262 | 通过 | 通过 | 未运行 | 通过 |
| 263 | 通过 | 未运行 | 通过 | 通过 |
| 264 | 通过 | 通过 | 通过 | 未运行 |
| 265 | 通过 | 通过 | 通过 | 未运行 |
| 266 | 不纳入 | 不纳入 | 不纳入 | 不纳入 |
| 267 | 通过 | 通过 | 未运行 | 通过 |
| 268 | 通过 | 未运行 | 通过 | 通过 |
| 269 | 通过 | 通过 | 未运行 | 通过 |
| 270 | 通过 | 未运行 | 通过 | 通过 |
| 271 | 失败 | 通过 | 失败 | 未运行 |
| 272 | 通过 | 通过 | 通过 | 未运行 |
| 273 | 通过 | 通过 | 通过 | 未运行 |
| 274 | 通过 | 未运行 | 通过 | 通过 |
| 275 | 通过 | 未运行 | 通过 | 通过 |
| 276 | 通过 | 通过 | 未运行 | 通过 |
| 277 | 通过 | 未运行 | 通过 | 通过 |
| 278 | 通过 | 未运行 | 通过 | 通过 |
| 279 | 通过 | 未运行 | 通过 | 通过 |
| 280 | 通过 | 通过 | 未运行 | 通过 |
| 281 | 通过 | 未运行 | 通过 | 通过 |
| 282 | 通过 | 通过 | 未运行 | 通过 |
| 283 | 通过 | 通过 | 未运行 | 通过 |
| 284 | 通过 | 通过 | 通过 | 未运行 |
| 285 | 通过 | 通过 | 未运行 | 通过 |
| 286 | 通过 | 未运行 | 通过 | 通过 |
| 287 | 通过 | 通过 | 未运行 | 通过 |
| 288 | 通过 | 通过 | 通过 | 未运行 |
| 289 | 通过 | 通过 | 未运行 | 通过 |
| 290 | 通过 | 未运行 | 通过 | 通过 |
| 291 | 通过 | 未运行 | 通过 | 通过 |
| 292 | 通过 | 未运行 | 通过 | 通过 |
| 293 | 通过 | 通过 | 未运行 | 通过 |
| 294 | 通过 | 通过 | 未运行 | 通过 |
| 295 | 通过 | 通过 | 通过 | 未运行 |
| 296 | 通过 | 未运行 | 通过 | 通过 |
| 297 | 失败 | 失败 | 未运行 | 通过 |
| 298 | 通过 | 通过 | 未运行 | 通过 |
| 299 | 通过 | 未运行 | 通过 | 失败 |
| 300 | 失败 | 未运行 | 通过 | 通过 |
| 301 | 通过 | 未运行 | 通过 | 通过 |
| 302 | 不纳入 | 不纳入 | 不纳入 | 不纳入 |
| 303 | 通过 | 通过 | 未运行 | 通过 |
| 304 | 通过 | 通过 | 未运行 | 通过 |
| 305 | 通过 | 未运行 | 通过 | 通过 |
| 306 | 通过 | 通过 | 通过 | 未运行 |

**239—220 头表版本说明（2026-10-16）。** 本批20个题号，19题保留，234因重复235排除；头表升序、逐题记录倒序。采用最终交付题意对应的正式生成与已记录评估，不按最好成绩挑选。220三个后端为r002；227 pandas/PySpark为r002、Ibis为r001；其余保留题均r001。232采用兼容季度标签后另存的冻结输出重评结果，原Ibis正式失败报告仍保留；没有重新生成。57份当前候选55通过、2失败，237 pandas/Polars的真实舍入失败按用户决定保留。未抽中后端记“未运行”。逐题说明列明历史、资产和评估版本，不能混作统一benchmark分数。

**259—240 头表版本说明（2026-10-16）。** 本批20个题号，19题保留，251排除；头表保持升序、详细记录倒序。沿用上一批交付口径，采用最终交付题意对应的正式运行，不按最好成绩挑选。259 pandas为r002、其余两后端r001；255/252三个后端均r002；253 pandas/Ibis为r004、PySpark为r005；246三个后端均r003；其余保留题均r001。257/250/244为获批配置对同一冻结输出的重评，原报告保留；不是新生成。57份当前候选全部通过，但255首轮失败、环境错误及评分覆盖限制均保留于逐题说明。未抽中后端记“未运行”。不将这些审核结果与老师首次运行口径混作统一benchmark分数。

**306—260 头表版本说明（2026-10-14）。** 头表统一按题号升序排列，本批逐题说明仍按306→260倒序；采用当前交付任务对应的正式验证状态，不按最好成绩选择运行；与上方老师历史批次的取样口径分别记录，不合并解释为统一版本分数。题面或澄清信息变化后采用新生成；仅评分配置变化时采用原始冻结输出的获批重评，旧报告保留。未抽中的后端记“未运行”，302/266记“不纳入”。

本批采用的run：306、305、300、299、297、294、279、275、273、267、263、261的三个后端均为r002；262均为r003；280分别为pandas r001、Polars r002、PySpark r003（旧澄清故障/运行器错误见逐题记录）；其余保留题均为r001。265 r001采用数值等价配置重评，263旧r001标签重评不是本次采用的新题面r002。共有135份当前候选，129通过、6失败；300/pandas、299/PySpark、297/pandas与Polars、271/pandas与Ibis的失败如实保留。完整历史及改动依据见下文“306—260 倒序审核交付”。

060–069 于 2026-10-10 补入头表，采用当前 `dfArena-prepbench-curation` worktree 的正式 `result.json`，路径为 `PrepBench/case_XXX/runs/interact/codex_gpt-6-astra/<backend>/<run>/result.json`。060–069 全部采用各后端现存首次生成 r001，已核对 generation.started_at；不以后续通过替换首次失败。063 pandas/PySpark 漏掉 MONEY HEIST，正式失败保留；其中 pandas r001 曾在修正 Rating 容差后对同一候选重评，因此“首次生成”不等于“首次评分配置”，详见下文 060–067 记录。067 采用已确认的新版“同香型增长率之差”资产下各后端 r001：pandas/Ibis/PySpark 通过、Polars 失败。后续 pandas/Polars r002 均通过，仅作复验记录，不计入头表。旧贡献差版本位于 `case_067_bak/`，不混入本表。068 是固定销售数值转长表任务，不代表随机生成能力。

070 尚未纳入本次头表及任务资产提交。其当前 worktree 的记录为 Ibis 通过、PySpark 失败；相邻 `../dfArena` main worktree 的另一组运行是 pandas 通过、Ibis/PySpark 失败，两边任务资产并不完全相同，不能合并为同一组结果。当前 PySpark 与 main Ibis 的已核对差异均为 Edgehill Description 将双空格压成单空格。060–067 的详细初步审核见下文及 `REVIEW_060_067.md`，068–070 见 `REVIEW_068_070.md` 和 `interact_validation_068_070.json`。

001–006 采用 2026-09-27 首次运行的原始正式评测结果，来源为 `../dfArena/PrepBench/case_00X/runs/interact/codex_gpt-6-astra/<backend>/r001/result.json`；24 次运行均完成生成和评测。此处不采用更早的 `interact_legacy` 实验、后续 run、当前配置离线重评或 2026-10-04 修改题面后的复验结果。原始失败报告：002 Ibis 为 `KEY_MISMATCH`；004 pandas/Ibis/PySpark 为 `MISSING_COLUMNS`，Polars 为 `KEY_MISMATCH`；006 PySpark 为 `MISSING_COLUMNS`。

说明：030 的三个 r001 因模型网关额度不足而生成失败、评测跳过；表中采用后续 r002 状态。030–033 的详细记录见下文。034 的三个 `r001` 均通过当前配置，运行记录及日期字面格式、同日行序的未覆盖项见下文 034 条目；035–037 的运行记录见 `interact_validation_035_037.json`，038–039 见 `interact_validation_038_039.json`，040–044 见 `interact_validation_040_044.json`，045–049 的原始快照见 `interact_validation_045_049.json`。045 的 pandas 有 r001 跳过、r002 失败，表中采用最新 r002；048 的原始 r001 因模型网关额度不足而跳过，已删除，并将四个通过的 r002 归档为 r001（见下文）；049 的四个 r001 因模型网关额度不足而跳过，表中采用后续 r002 的正式评测状态。050 原 r001 四后端均因额度不足跳过，已删除；原 r002 均正式失败，现归档为 r001。该表按现有记录维护，后续重跑或补充 backend 时更新对应单元格。

# PrepBench 迁移与审核日志

## 2026-10-16：239—220 倒序审核交付

按每20题一批覆盖239→220：19题保留，234按已确认决定排除，不建立可运行目录。基于老师最新main `57a3d6eababc3945e0d04104940b71c8b1a30153` 创建独立工作分支，经PR审阅合并；保留老师新增077—079、073修正及已有260—306、240—259资产和记录。本批不修改共享运行器、评分器或审核准则。

**来源与环境。** 只读来源`D:/DataFrameStudy/prepbench`：题面/KB/输入在`data/case_XXX`，reference在`reference/solutions/case_XXX`，主GT/旧配置在`src/evaluate/gt/case_XXX`；全部输入与源哈希核对。232另查原始Excel工作表和官方解答，见逐题记录。实验在原审核目录与原运行器完成，未冒称在最新main适配器重新生成。固定镜像`sha256:89b6eb5a3313c26423d8bbebe9edea96e22a3d3de580a4626c671ebcb2f83570`，Python3.11.16/pandas2.3.3，与老师历史镜像不同；解题gpt-6-astra/low走ChatGPT订阅，simulator为gpt-6-astra、temperature0、nowcoding.ai授权API，每组1800秒。pandas必选，另两后端抽样后固定，计划记录种子及资产哈希。

**共同整理与验证。** 标准目录、元数据领域分类、准确KB引用/intent及经审核的key/类型/容差齐全；reference通常仅适配入口，特别处理见逐题说明。沿用老师准则及用户逐题决定，不机械补齐query。交付复查19份GT、19份固定环境reference输出、19份独立核算输出全部通过；57份最终候选55通过、2份237舍入失败与记录一致。核对输出schema、来源与最终生成计划，未以旧题意候选冒充新版本验收。main已有的整数/文本别名与alternative_gt机制满足本批需求，无共享代码改动。评分代码聚合SHA256 `6ef93a5a5acc96cab8e36f5fdea2502d5d0b879369de20282bd985f05f06c480`（config.py、evaluator.py、normalization.py依次按路径:SHA256加换行聚合）。

**记录与限制。** 以下“历史”使用原正式result状态；232的兼容重评另行说明，220旧失败也不覆盖。生成失败/评估跳过与答案错误分开。每题`curation/output/XXX/`的source_manifest、review、interact_plan、final_review、正反例和独立核算，以及`case_XXX/runs/interact/codex_gpt-6-astra/<backend>/<run>/`原代码/CSV/问答，均作为本地证据保留、不入Git、不作为仓库运行依赖。私有GT/reference/config/KB不直接提供给解题模型。共享比较器允许额外列，实际schema另查；通过仅证明当前输入与配置，不证明未触发分支和未强制的格式/行序。

### 239：赛前比赛经验倒推

**决定与改动。** 按Team与Player ID分组，独立扣除当前及之后各届比赛场次，核对赛前经验；题意业务规则不变，reference仅适配入口。

**验证与运行。** 主GT行数：output_01.csv=436。当前采用：ibis r001 通过；pandas r001 通过；polars r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；ibis r001 通过。

**限制与解释。** 日期按值比较，不强制full的DD/MM/YYYY；同日重复赛事未覆盖。部分模拟回复把计算顺序延伸成展示顺序，最终行序不评分。

**版本与证据。** 当前任务聚合SHA256 `7c9fdfaf975f8a0c7afd13a2f19dcb89acd2e506c7c90bdb33a88ed0f8ccde82`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/239/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 238：员工跨配送中心调动

**决定与改动。** 用户决定query不公开全公司去重人数，保留交互澄清：各DC人数相加590，全公司按ID去重537。独立核验相邻记录及1—2个月调动间隔、35次调动与7行汇总。

**验证与运行。** 主GT行数：output_01.csv=7。当前采用：pandas r001 通过；polars r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。

**限制与解释。** query原百分比例子33.35%=35.35存在笔误，full/KB公式明确，按既有决定保留。当前所有DC都有调动，Polars无调动时均值留空而full要求0的分支未触发；展示顺序不检查。

**版本与证据。** 当前任务聚合SHA256 `a23d3602de3faa67c4bb28f68ef3e640f6397fe50977a2cd65509313d6d8ce0c`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/238/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 237：月度及过去12月离职率

**决定与改动。** 核验任职区间补全、期初期末人数与离职率。用户明确不在query新增half-up说明，保留真实舍入失败；full/reference/GT规则不变。

**验证与运行。** 主GT行数：output_01.csv=315。当前采用：ibis r001 通过；pandas r001 失败；polars r001 失败。原正式运行历史：pandas r001 失败；polars r001 失败；ibis r001 通过。

**限制与解释。** r001 pandas/Polars把实际3.125舍入为3.12，而full/GT要求3.13，正式失败保留；Ibis通过。不放宽评分追求通过。无重叠任职区间，部分去重分支未区分；full日期字面形式和最终展示序不强制。

**版本与证据。** 当前任务聚合SHA256 `2079eafc790c39f8b930be2b2c3d2c1b86c472fa5c8f801a6a90f8b8edd4523d`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/237/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 236：工龄与人口分类补零

**决定与改动。** 保留既有月底工龄规则，用户决定query不补明，交互可澄清；核验月工龄、整年及全局人口分类组合补零。query明确指定的month_end_date按DD/MM/YYYY精确文本检查。

**验证与运行。** 主GT行数：output_01.csv=7440, output_02.csv=14758。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 当前员工ID唯一且guid均匹配，单键与双键关联等价；缺日期、默认0及负工龄等分支未覆盖。其他日期语义比较、full最终展示序不检查。

**版本与证据。** 当前任务聚合SHA256 `574c460fa98643d0047f46b3b35426fc90ff16fa6636e5f76b676ace5e33bbd7`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/236/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 235：员工年龄与世代分组

**决定与改动。** 保留本题，核验出生年世代映射、月末周岁及五岁年龄组，使用输入定义及原Millenials拼写；reference仅适配入口。

**验证与运行。** 主GT行数：output_01.csv=537, output_02.csv=7440。当前采用：pandas r001 通过；polars r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。

**限制与解释。** 当前员工ID唯一且guid完全匹配，query单键与full/reference双键关联未产生差别；日期按值比较，最终行序不检查。

**版本与证据。** 当前任务聚合SHA256 `e8835bffec1b9f90b0a72f78631627f25018ac5ff27cff3656cf50a2f087bf85`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/235/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 234：与235重复，排除

**决定与改动。** 用户确认保留235、排除234。原query、三张输入、reference和原config完全相同，GT全部记录及重数相同，仅full/KB表述不同。

保留原文件与本地batch_239_200/duplicate234_235.json对比证据，不导入可运行case目录，不安排interact。

### 233：双标识缺失补全

**决定与改动。** 用完整employee_id/guid对建立双向映射，补齐两表缺失ID；原业务题意保持，配置保留非ID字段及行重数检查。

**验证与运行。** 主GT行数：output_01.csv=537, output_02.csv=7440。当前采用：pandas r001 通过；polars r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。

**限制与解释。** 当前映射一对一且全部缺失可补齐；冲突和仍不可解析的映射未覆盖。full要求保留日期文本，评分按日期语义兼容，展示顺序不检查。

**版本与证据。** 当前任务聚合SHA256 `3afaff1f12867a2dd75148a1e515f6fc1d8edbc78581d108c563e7823e150ea3`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/233/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 232：财务季度销售与门店分类

**决定与改动。** 追溯原始Excel及官方解答：CSV匿名文件名丢失工作表月份，原2000行星期标签本身有误。按用户决定在query/full/KB公开12个文件的原月份，说明用月/日/年重建日期并忽略星期；输入、reference与主GT不改。整数季度兼容1..4及Q1..Q4。

**验证与运行。** 主GT行数：output_01.csv=20。当前采用：ibis r001 通过（兼容重评）；pandas r001 通过（兼容重评）；polars r001 通过（兼容重评）。原正式运行历史：pandas r001 通过；polars r001 通过；ibis r001 失败。

**限制与解释。** 原始r001 pandas/Polars通过、Ibis仅因Q前缀季度标签失败。配置兼容后单独重评三个冻结输出均通过，原正式报告不覆盖；头表采用此次有记录的重评。缺季度及前期销售为0的分支未覆盖。

**原始来源与重评。** [官方2023 Week 30解答](https://preppindata.blogspot.com/2023/08/2023-week-30-solution.html)从Excel工作表名取得月份；本地`original_source_audit_20261015.json`记录CSV逐格与原Excel一致、2000个原星期标签不符日期、官方20行输出与主GT相符。按原月份恢复信息，不修改CSV星期值。重评证据为`232/reevaluation_quarter_aliases_20261015.json`，记录原候选/config/GT哈希。

**版本与证据。** 当前任务聚合SHA256 `ba37cc3031a2610be43a48877c27a03d31f79e0dad19b33800b8dbb7ecfdcbff`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/232/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 231：月销售补零与移动平均

**决定与改动。** 将工具专用操作和冲突动态文件名适配为DataFrame处理及output_01.csv；业务保持。核验截至2023年6月完整月份、按门店车型补零及完整三月窗口，前两月均值保持空。

**验证与运行。** 主GT行数：output_01.csv=2089。当前采用：pandas r001 通过；polars r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。

**限制与解释。** 数值按6/9位精度比较，兼容尾部零与语义日期；不把部分窗口或0当成前两月均值。

**版本与证据。** 当前任务聚合SHA256 `a121ac6ce21820f9c8f9f3a5d6fc9f075267cd959fad934d077cdad5b040f914`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/231/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 230：学生短跑筛选排名

**决定与改动。** 按用户决定在query公开competition ranking：并列同名次，之后跳号，例如1、1、3。实际100米14.31秒并列边界已核验；名次精确整数，拒绝dense rank或拆分并列。

**验证与运行。** 主GT行数：output_01.csv=31。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 全部300条学生/时间均能匹配基准，未匹配基准分支未覆盖；输入空格按清洗处理，输出列名和标签仍严格。

**版本与证据。** 当前任务聚合SHA256 `cbdbbba476ea69a86536b53caaba59c8271ed60820855d930602f7a222ecd156`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/230/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 229：学校月度成本

**决定与改动。** 核验四份输入合并、按学校月份重塑及总成本；按query要求检查学校内月份顺序，full为学校升序后日期升序，GT满足。

**验证与运行。** 主GT行数：output_01.csv=48。当前采用：ibis r001 通过；pandas r001 通过；polars r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；ibis r001 通过。

**限制与解释。** 当前月份均英文、成本为完整整数；混合月份及非法成本fallback未覆盖。日期按值兼容，不强制full的DD/MM/YYYY。

**版本与证据。** 当前任务聚合SHA256 `435a446a4a2eff3b913060ff5a8166df7427936e1d7a447462816b223d643cb5`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/229/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 228：学校录取名单

**决定与改动。** 核验学生与申请/住址关联，按课程和地区配额、分数及距离选人；reference与GT日期写法不同但同值，评分按日期语义处理。

**验证与运行。** 主GT行数：output_01.csv=100。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 当前无多匹配、fallback关联或录取边界完全同分同距离；最终展示顺序不检查，但选人顺序参与计算。

**版本与证据。** 当前任务聚合SHA256 `b02854d63890775e50756f25eedb293f279ced7b1829d29bb065a21b3b755340`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/228/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 227：学生申请与成绩汇总

**决定与改动。** 核验12000条成绩汇总4000学生；同一School ID证实的St Marys/St. Mary's、Viliers Hill/Villiers Hill按用户决定配置精确别名，其他名称及ID严格检查。

**验证与运行。** 主GT行数：output_01.csv=4000。当前采用：ibis r001 通过；pandas r002 通过；pyspark r002 通过。原正式运行历史：pandas r001 评估跳过（生成runner_error）, r002 通过；ibis r001 通过；pyspark r001 评估跳过（生成runner_error）, r002 通过。

**限制与解释。** pandas/PySpark r001为启动环境错误、评估跳过；恢复后r002通过，Ibis r001通过。当前每生三门有效成绩且学校唯一匹配；未知成绩、重复科目及未匹配学校未覆盖。日期语义兼容。

**版本与证据。** 当前任务聚合SHA256 `8d19ba15818664f790acf6843e72060191ea5d85ab26d707ba1951f2acb5acef`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/227/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 226：成绩四分位与学生标记

**决定与改动。** 核验按科目成绩阈值分四组、Tiles映射、班级清洗及两科处最低四分位的筛选。当前边界并列导致组大小不等，不能按等人数硬切。

**验证与运行。** 主GT行数：output_01.csv=7。当前采用：ibis r001 通过；pandas r001 通过；polars r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；ibis r001 通过。

**限制与解释。** 50名学生均有三门有效成绩，full非缺失n规则与reference对NaN的处理差异未触发；展示顺序不检查。

**版本与证据。** 当前任务聚合SHA256 `984607b45eb68b6c13ad75a88e078d37864fed9b83964db14329a2f89dd8d5c4`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/226/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 225：各科最弱班级

**决定与改动。** 核验班级学科平均成绩与最弱班级筛选；平均值一位小数采用abs_tol=0.05、rel_tol=0，接受合理更高精度，不强迫特定末位写法。

**验证与运行。** 主GT行数：output_01.csv=3。当前采用：pandas r001 通过；polars r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。

**限制与解释。** 三个学科舍入后最弱班级均唯一，字母序破同分分支未验证；不宣称容差强制了特定舍入算法，展示顺序不检查。

**版本与证据。** 当前任务聚合SHA256 `c48f8b6a7d13c57393bceab3d257a261db308b426d9ce994ab88b408906205e8`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/225/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 224：出勤标签与成绩

**决定与改动。** 按用户决定修正query与既有full/reference/GT冲突：90%及以上High，70%至不足90%为Medium，低于70%为Low，统一标签。三名恰90%学生及70%边界已核验；保留成绩half-up整数舍入。

**验证与运行。** 主GT行数：output_01.csv=20。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 20个姓名均唯一匹配且只有一个下划线，缺失/重复关联及多下划线拆名未覆盖；query的最近整数表述不另加中点说明。

**版本与证据。** 当前任务聚合SHA256 `2f1aa96199d36fa47ef7c9b7b0f624a739e78dc970e0f13e9d45102fe2a96173`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/224/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 223：学生年度成绩下降

**决定与改动。** 核验八项年度类别成绩重塑、两年均值、差值及负差筛选；四分之一刻度均值和差值按数值精确比较。

**验证与运行。** 主GT行数：output_01.csv=10。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 全部ID唯一且八项成绩完整，缺项/重复未覆盖；full的student_id展示排序不评分，原GT物理顺序也不同。

**版本与证据。** 当前任务聚合SHA256 `4ac2d952a862ef514bb2ee9e31d58078360c1e98d7281e1121cae8b66433b689`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/223/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 222：餐食类型价格与比例

**决定与改动。** 适配两份实际CSV，合并Veggie/Vegetarian及已证实的Meat based/Meat-based标签；仍要求类别合并。query未指定舍入，价格abs_tol=0.005、比例abs_tol=0.5个百分点，rel_tol=0。

**验证与运行。** 主GT行数：output_01.csv=3。当前采用：ibis r001 通过；pandas r001 通过；polars r001 通过。原正式运行历史：pandas r001 通过；polars r001 通过；ibis r001 通过。

**限制与解释。** 30种餐食唯一匹配，未知类别与缺失/重复关联未覆盖。容差允许高精度而非强制舍入；full最终展示序不评分。

**版本与证据。** 当前任务聚合SHA256 `67e6c603004bbf8229facbd46be5535d3822259e44d4f51d2cbdac45677955b4`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/222/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 221：会议讲者与场地关联

**决定与改动。** 核验三个级联输出：讲者/描述拆分和分类，会议地点关联，再找二楼讲数据去重的目标讲者。既有业务规则保持。

**验证与运行。** 主GT行数：output_01.csv=3, output_02.csv=1, output_03.csv=1。当前采用：ibis r001 通过；pandas r001 通过；pyspark r001 通过。原正式运行历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。

**限制与解释。** 当前目标唯一，多个目标会议与缩写歧义未覆盖；full确定性展示顺序不评分。

**版本与证据。** 当前任务聚合SHA256 `3e33ea91610991ae1a8641cd4beef684f6bcb069644a798157abf3f9bc1ecd97`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/221/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。

### 220：城市坚果收入与均价

**决定与改动。** 用户批准兼容未指定的两种中点舍入：Liverpool原均价7.725，接受7.72和7.73。保留reference及主GT，新增独立Decimal核算的整表half_up替代GT；full/KB说明兼容，query不改。均价abs_tol=0.005，Revenue零容差。

**验证与运行。** 主GT行数：output_01.csv=3。当前采用：ibis r002 通过；pandas r002 通过；polars r002 通过。原正式运行历史：pandas r001 通过, r002 通过；polars r001 通过, r002 通过；ibis r001 失败, r002 通过。

**限制与解释。** 旧r001 Ibis仅舍入差异失败，原报告保留并单独重评；full/KB改变后新生成r002三后端均通过。Ibis r002有一次模拟请求502/超时，轮内重试成功，不能把失败调用算成功澄清轮。当前36行无重复城市/坚果/指标组合，重复取首条分支未覆盖；展示顺序不评分。

**版本与证据。** 当前任务聚合SHA256 `4848482133c3a8256ed29ffa9e39049870ea8357cee42c8e4c581dcf031ced3b`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/220/review.json`与对应`interact_plan*.json`、`final_review*.json`记录独立检查、正反例、抽样及生成/评估版本；最终query/full/KB/输入与所选生成计划一致。


## 2026-10-16：259—240 倒序审核交付

本批按每20题交付覆盖259→240：19题保留、251按已确认决定排除，不创建可运行目录。239及以下保留在本地，不混入本次提交。基于老师已合并PR #13的main `8f1d93086f5bc5e90a41161b0d110075d2e401e5`，保留老师更新的NOTES、287来源说明及已有任务和运行器。

**来源与环境。** 来源仍为只读`D:/DataFrameStudy/prepbench`，题面/输入/KB来自`data/case_XXX`，参考代码来自`reference/solutions/case_XXX`，答案与旧配置来自`src/evaluate/gt/case_XXX`。本批输入逐文件与源哈希一致；不导入AppleDouble伴随文件。实验在原审核目录、原运行器上完成，未冒称已在最新main适配器重新生成。固定镜像`sha256:89b6eb5a3313c26423d8bbebe9edea96e22a3d3de580a4626c671ebcb2f83570`，Python3.11.16/pandas2.3.3，与老师历史镜像不同。解题gpt-6-astra/low走ChatGPT订阅，simulator为gpt-6-astra、temperature0、nowcoding.ai授权API，每组1800秒；pandas必选、另两后端抽样后固定。

**共同整理。** 采用标准目录、公开输入输出角色、准确KB引用与intent、经审核的key/类型/容差；reference通常仅适配文件入口，特别变动列在逐题记录。遵循老师更新后的规则：必要业务契约尽量明确，不机械补齐query；已决定保留给交互的细节仍按逐题记录。domain按业务主题分类：学校及学习挑战为education，储蓄产品为finance，航班/生产/项目运营为business，网球为sports，SDG为public_sector。metadata分类补正不改变解题信息，不重跑生成。

**验证与公共依赖。** 19份GT、57份最终冻结候选、19份当前固定环境reference输出均使用交付评分器复核通过；核对schema、KB引用、来源及运行计划资产哈希。256顶层reference_output为旧错误快照，本次采用`256/price_tolerance_20261014/fixed_reference/`，旧证据保留。各题已有独立核算和正反例验证，下面仅摘要关键边界。共享评分器新增显式`gt_position`用于257，附协议和测试；默认旧行为保持，46项回归通过。另跑PrepBench本地集成测试13项，6个子场景因现有Windows路径分隔符断言失败（logs\\agent_events.jsonl与logs/agent_events.jsonl）；对应测试和生成/运行器文件与main一致，本批未修改，不宣称全套测试通过。评分代码聚合SHA256 `6ef93a5a5acc96cab8e36f5fdea2502d5d0b879369de20282bd985f05f06c480`（config.py、evaluator.py、normalization.py依次按路径:SHA256加换行聚合）。

**证据与局限。** 每题`curation/output/XXX/`的review、source_manifest、interact_plan、final_review及正反例目录，与`case_XXX/runs/interact/codex_gpt-6-astra/<backend>/<run>/`原代码/CSV/问答均本地保留，不提交、不作为仓库依赖。任务私有资产不直接提供给解题模型；simulator按授权读取澄清材料。共享比较器允许额外列，实际候选schema另查。通过仅证明当前输入和配置下结果，不证明未触发分支或被有意保留的格式/行序要求。

### 259：未预订座位

**决定与改动。** 取消full/KB的额外最终行序，忽略展示顺序；仍严格检查Class/Seat/Row及行重数。GT和reference业务计算不变。

**验证与运行。** GT行数：output_01.csv=7。当前采用pandas r002；polars r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 评估跳过（生成runner_error）, r002 通过；polars r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 输出不含持卡分组计数，CSV比较不能证明中间分组步骤；当前键均非空。

**版本与证据。** 交付任务聚合SHA256 `5289e33d4c01695a21ebcc8014b3c4743661aecaeabc14e07280083740a368de`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/259/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 258：舱位月度销售与目标

**决定与改动。** 取消full/KB中月份和FC→BC→PE→E的额外最终行序；保留48个分组及金额精确比较。

**验证与运行。** GT行数：output_01.csv=48。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 当前目标键唯一、全部匹配且输入均有效；异常日期、未知舱位和未匹配目标未覆盖。

**版本与证据。** 交付任务聚合SHA256 `aa913a7fb320ec25a96846dbf152548c8c51ddadfe665580403c2ab422291729`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/258/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 257：季度价格统计块

**决定与改动。** 保留并公开中位数→最大值→最小值及八组块内顺序；六列schema不变。新增通用gt_position顺序模式，独立核验GT后逐位置比较。四个金额列abs_tol=1e-10、rel_tol=0，仅兼容浮点表示。

**验证与运行。** GT行数：output_01.csv=24。当前采用ibis r001；pandas r001；polars r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；ibis r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 首评pandas/Polars因522.5999999999999与522.6差异失败，保留旧报告后统一重评r001通过；并非重新生成。缺组/缺舱位未触发，相同统计值无法区分计算身份。

**版本与证据。** 交付任务聚合SHA256 `41a65d9c55ea184f64a9c7092026926533fd038f5eccd35f3c7e9c98c1086bb9`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/257/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 256：航班拆分与持卡分流

**决定与改动。** reference读取CSV保留字面Meal Type=None；Price绝对容差1e-10、相对0，兼容输入浮点尾数。

**验证与运行。** GT行数：output_01.csv=1883, output_02.csv=1895。当前采用pandas r001；polars r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 用户保留full原行序要求及ignore_order=true的差异；日期按值比较，不强制DD/MM/YYYY字面形式。异常价格/卡标志未覆盖。

**版本与证据。** 交付任务聚合SHA256 `cb291ad4c1dba7f59052fefeb74d74996d29691d4ce0f1e89223e1ff93084aa8`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/256/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 255：挑战技巧分类汇总

**决定与改动。** query不公开分类表；full与KB补齐既有两轮58/42项映射，明确追问时解释实际分类规则，不指向不可见表格。reference/GT不改。

**验证与运行。** GT行数：output_01.csv=73。当前采用pandas r002；polars r002；pyspark r002，均完成生成/评分并通过。历史：pandas r001 失败, r002 通过；polars r001 失败, r002 通过；pyspark r001 评估跳过（生成missing_output）, r002 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** r001 pandas/Polars因未获完整映射而行数错误，PySpark未产出、评估跳过；KB修正后r002通过。full的Priority升序仍未由评分器检查，按用户决定保留。分类映射并非唯一合理分类。

**版本与证据。** 交付任务聚合SHA256 `53908f7516325df6fd197fe5428c63aef0df3f35565c2dc54e659129c284d559`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/255/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 254：玩具生产累计及余量分配

**决定与改动。** 建立输入输出角色、准确KB引用与intent，核对累计数量、配额及分配；reference仅适配入口。

**验证与运行。** GT行数：output_01.csv=612, output_02.csv=12。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 当前没有并列最大超额或余量超过单玩具产量；分数配额、任意新增周布局未覆盖。

**版本与证据。** 交付任务聚合SHA256 `e041309fa544ea08be0999c450ada9051735424d251e80505c693421b774be82`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/254/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 253：计划存款与不计息余额

**决定与改动。** query公开计划每月存款300、12个月期限及既有四级升序；不公开计算答案。reference/GT规则保持。

**验证与运行。** GT行数：output_01.csv=144。当前采用ibis r004；pandas r004；pyspark r005，均完成生成/评分并通过。历史：pandas r001 通过, r002 通过, r003 通过, r004 通过；ibis r001 通过, r002 通过, r003 通过, r004 通过；pyspark r001 通过, r002 通过, r003 评估跳过（生成runner_error）, r004 通过, r005 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 旧r001至r003对应逐步补明前版本；最终pandas/Ibis r004、PySpark r005。PySpark r003运行器失败并跳过评分，不能记为内容错误。当前仅12种账户、正利率与300存款；小写y分支未验证。

**版本与证据。** 交付任务聚合SHA256 `9dd138bb52df1800fc5e226fa29f646fce7e7e0e5fb7305760361ba544157215`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/253/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 252：账户储蓄与排名

**决定与改动。** query公开总利息排名/Month升序及从1起连续Sort编号，保留计算规则；公开后重新生成r002。

**验证与运行。** GT行数：output_01.csv=144。当前采用pandas r002；polars r002；pyspark r002，均完成生成/评分并通过。历史：pandas r001 通过, r002 通过；polars r001 通过, r002 通过；pyspark r001 通过, r002 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 当前正利率使第12月余额恰为最大值；零负利率、并列排名及部分舍入分支未覆盖。

**版本与证据。** 交付任务聚合SHA256 `f030cf0290917e2ad322bcdc92ab78944d1b6d15b2d62aa7fe1117340acc0d22`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/252/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 251：报告日历生成

**决定与改动。** 用户确认排除：输入仅Year，主要生成日期脚手架和日历公式，数据处理区分度不足。

保留原始文件和本地证据，不提交可运行case目录、不安排interact。

### 250：学生GPA与滚动奖项

**决定与改动。** query公开前2%向上取整人数及移动均值/GPA/姓名破同分规则；两表兼容1..6与Term 1..Term 6，其他计算保持。

**验证与运行。** GT行数：output_01.csv=3000, output_02.csv=20。当前采用ibis r001；pandas r001；polars r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；ibis r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 仅配置别名重评r001，保留原失败。用户决定跳过日期字面格式事项：候选ISO日期通过语义比较，但不满足full的DD/MM/YYYY字面要求。当前学生都有六学期且姓名唯一。

**版本与证据。** 交付任务聚合SHA256 `22fa1d1fd2f3c6098812067450a79835da50ceda221b43506f86a5fea4d9706f`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/250/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 249：迟到程度与比例排名

**决定与改动。** 核验星期和学生汇总、迟到比例及名次，配置准确key/类型/容差并补已有KB规则。

**验证与运行。** GT行数：output_01.csv=5, output_02.csv=8。当前采用ibis r001；pandas r001；polars r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；ibis r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 星期均值非负且无并列；全缺勤学生等分支未覆盖。

**版本与证据。** 交付任务聚合SHA256 `a1ebcae368a3e2d2c64dca5ac7e1de9ad012f3a2f2c09899acb64936edadb3bc`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/249/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 248：项目账目填充汇总

**决定与改动。** 核验项目标题填充、Invoice/Expense分类及利润；配置项目key与数值比较。

**验证与运行。** GT行数：output_01.csv=3。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 候选用包含关键词、full/reference用前缀，当前输入不区分；非法数值和带引号跨行CSV未覆盖。

**版本与证据。** 交付任务聚合SHA256 `c9920fafc2e2cb31204d2166f48763ede4a58ae7a5da12edc78e3024b71499c0`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/248/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 247：校历与课后社团

**决定与改动。** 核验日期展开、工作日筛选及事件/社团关联；保留既有业务口径。

**验证与运行。** GT行数：output_01.csv=30。当前采用pandas r001；polars r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 三个候选实际均为DD/MM/YYYY，但评分器仍兼容ISO日期；边界事件恰为最早/最晚日期，缺社团或重复事件未覆盖。

**版本与证据。** 交付任务聚合SHA256 `046a02880a8126fc3f924a21408092f782dab9f614645f2d941c2d0325ebfd38`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/247/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 246：出勤率与年级奖项

**决定与改动。** 删除full/KB/reference中无依据的兜底选人与最终行序；query公开对舍入出勤率的线性95分位、含阈值和并列规则，GT保持。

**验证与运行。** GT行数：output_01.csv=2, output_02.csv=55。当前采用ibis r003；pandas r003；polars r003，均完成生成/评分并通过。历史：pandas r001 通过, r002 通过, r003 通过；polars r001 通过, r002 通过, r003 通过；ibis r001 通过, r002 通过, r003 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** r001/r002保留，最终题意对应r003。当前均三学期、分母非零且姓名年级完全匹配；通过不证明未匹配记录保留行为。

**版本与证据。** 交付任务聚合SHA256 `4111c1a93645bfe755a84b726708d0f18c89ff49a58b97e434252919e1405064`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/246/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 245：歌曲投票

**决定与改动。** 取消最终行序要求，纠正KB虚构Missing标签而保留full既有缺失分组语义；reference确定性排序仅为允许的实现。

**验证与运行。** GT行数：output_01.csv=8。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 当前无缺失歌曲或未匹配学生，相关分支未覆盖。

**版本与证据。** 交付任务聚合SHA256 `3cfb6b5ebc001d1a0d8adb9083f5f2575826fff18fdf60f032df68e45dab2d81`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/245/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 244：班级主要国籍

**决定与改动。** 兼容Brazil/ Brasil两种已确认标签，其他字段严格；配置变更重评冻结r001，原报告保留。

**验证与运行。** GT行数：output_01.csv=2。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 当前48个ID唯一且两表全匹配，不能以通过证明未匹配学生处理或关联步骤本身。

**版本与证据。** 交付任务聚合SHA256 `8adcab9bddd4282f11d55ef8ea41f651a241b06a7b8068e401e9cd518e2eb33c`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/244/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 243：科目退课率

**决定与改动。** 计数改精确integer，Subject为key，比率abs_tol=5e-10/rel_tol=0；当前拼写匹配结果一致，不新加算法要求。

**验证与运行。** GT行数：output_01.csv=7。当前采用pandas r001；polars r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；polars r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 用户跳过最终行序问题，full指定科目序仍保留、评分忽略；三候选按字母序。所有科目有在读及退课，缺状态分支未覆盖。

**版本与证据。** 交付任务聚合SHA256 `d2e791b0deae9251f48bb99ae9865d350171f26ea93a27b047825e60167c51f0`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/243/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 242：网球前200胜

**决定与改动。** 保留query对双方球员视角的原表达；Win Number和Days Since Last Win改精确integer，拒绝编号差1等旧配置误接受。24份正式CSV导入，不导入AppleDouble伴随文件。

**验证与运行。** GT行数：output_01.csv=943。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 四人均达到200胜；缺失别名及不足200胜未覆盖。PySpark同日轮次排序与full不同，当前六组同日比赛仍全部数值一致；展示行序/日期字面形式未强制。

**版本与证据。** 交付任务聚合SHA256 `27529cc9b856e9367904f0b8bd3391f733d88a67ce73eab0654ab6b5f033ed0f`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/242/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 241：国家可持续发展目标展开

**决定与改动。** query将Excel表头操作改为实际CSV相邻列说明并明确Overview=input_04；保留业务映射。排名精确integer，分数abs_tol=5e-10/rel_tol=0。

**验证与运行。** GT行数：output_01.csv=3502。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** 373个缺失趋势保留空值；未知标签、缺失国家和不可解析数值未触发，最终展示顺序不检查。

**版本与证据。** 交付任务聚合SHA256 `2750ffe9f6b8f8aa35ca4f0ab67745dacbed34e1d625319c7b76f26227a7b06d`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/241/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。

### 240：订单前后变化

**决定与改动。** query补回input_02=2023-07-01、input_01=2023-08-01，并明确同Customer+Book比较、Bigger Order?为当前减上一笔数量。编号/数量/差值精确integer，首笔保留空。

**验证与运行。** GT行数：output_01.csv=18。当前采用ibis r001；pandas r001；pyspark r001，均完成生成/评分并通过。历史：pandas r001 通过；ibis r001 通过；pyspark r001 通过。其中配置重评前的原报告另存，不能将上列最终状态理解为首次评分状态。

**限制与解释。** GT物理行序与full顺序要求不同，按决定忽略展示序、严格核对Sequence ID。日期按值比较；仅两个月输入，reference日期字符串排序及跨行CSV等泛化未验证。

**版本与证据。** 交付任务聚合SHA256 `7c1b15b3a60f92d0e880fea305b14dbc0d0c82da3f72dbacf6e331a78307d723`（按仓库相对路径排序，路径:文件SHA256加换行聚合）。本地`curation/output/240/review.json`及对应`interact_plan*.json`、`final_review*.json`记录来源核算、正反例、抽样及生成/评估资产版本；本次仅补metadata分类，不改变最终运行对应的query/full/KB/输入。


## 2026-10-14：306—260 倒序审核交付

本批覆盖306至260共47题：45题保留，302/266按用户决定排除，不创建可运行目录；259及以下不在本次提交。流程经老师确认：先静态审核和必要修正，再interact、诊断及复验。以下按题号倒序记录最终决定，历史失败不删除，不把复验通过冒充首次通过。

**来源与环境。** 原始只读来源为本机`D:/DataFrameStudy/prepbench`：题面/KB/输入在`data/case_XXX`，reference在`reference/solutions/case_XXX`，GT/config在`src/evaluate/gt/case_XXX`。整理起点为老师提交`0eaf29d97288b8e264822d26ab65f976d5e4f2c0`；本次交付基于最新`a4c2f54`，完整保留老师新增070—076及交互适配修复。实验仍对应原运行器与下列固定镜像，未将历史运行冒称在最新适配器重新生成。

固定镜像`sha256:89b6eb5a3313c26423d8bbebe9edea96e22a3d3de580a4626c671ebcb2f83570`，Python3.11.16/pandas2.3.3；与老师历史镜像不同。解题为ChatGPT订阅的gpt-6-astra/low，模拟用户gpt-6-astra/temperature0（nowcoding.ai），每组1800秒；pandas必选，另两后端抽样后固定。source_manifest、每轮plan与正式result均本地保留。reference验证与解题隔离，GT/KB/reference/config不直接提供给interact解题模型。

**共同改动与验证。** 建立标准目录、metadata、输入输出约定，核对KB引用并补必要intent；通常仅适配reference入口，业务或GT变化在逐题说明。输入保持原字节。字段采用经审核的key、类型、数值容差和顺序，不统一放宽。已有固定环境reference、独立计算及正反例报告；交付时再次核对文件、元数据、引用、源哈希、运行版本，使用交付比较器检查GT和冻结候选。

**领域分类补正（2026-10-14）。** 交付复核遗漏了domain分类，本批45题原先均为general；现按根目录README的Workload domain taxonomy补齐一个主领域。按业务主题分类，不按所用算法或是否出现金额分类：工资/客户/销售等运营归business，贷款及预算、财务汇总归finance，运动员收入榜归sports，节目/卡牌/节庆题归media_culture。

| Domain | Case |
| --- | --- |
| `business` | 260, 261, 263, 264, 265, 268, 269, 270, 275, 276, 277, 278, 279, 280, 281, 293, 294, 295, 298, 299, 300 |
| `finance` | 267, 271, 272, 274 |
| `sports` | 282, 283, 284, 285, 286, 290, 291, 292, 296, 303 |
| `media_culture` | 262, 287, 297, 305, 306 |
| `education` | 288, 289 |
| `science` | 273 |
| `health` | 304 |
| `geospatial` | 301 |

此次仅修改metadata.domain及本日志，输入、query/full、KB、reference、GT、config和运行产物均未改变，不重新生成或评分，头表结果不变。逐题“当前任务资产”哈希已更新为分类补正后的交付版本；原运行plan、原哈希和报告保持原样，不能把补正后的metadata称为当时运行版本。本地`delivery_306_260/domain_review.json`保存逐题新旧哈希与检查结果。

**评分器依赖。** 本批包含按列整数标签映射（263）、精确文本标签映射（260）、整表替代GT（273）三项通用机制及其测试/协议文档；未启用时保持旧行为。不同温度答案只能整表选择，不能逐格拼答案。公共实现无case编号特判。交付评分代码聚合SHA256：`574034ea0fc96e96c46e65f6c0eba3504c88b2202cff8e90692e4ab95ef8bafa`。

**记录口径。** 本批结果已并入文首总表，采用的run见头表下方“306—260 头表版本说明”；它是审核状态，不是统一版本benchmark成绩。逐题段落另列全部历史run状态。265的r001为获批config重评后的冻结输出，原失败报告保留；263的r001亦曾因标签兼容重评，最新为新题面r002；280有澄清故障/运行器错误，不能仅因旧输出通过视为交互成功。306的reference入口后补但solve不变，不要求重新生成。

本批各保留题选取三个后端，共135份当前候选；生成/评分完成不等于所有候选通过。共享比较器仍不拒绝额外列，实际schema单独核对；候选通过也不证明缺失、并列、未知类别等未触发分支。

`curation/output/`和`case_XXX/runs/`的引用均指研究者本地证据，按提交清单不入Git，不是仓库运行依赖。原始长日志及未交付题记录保留在本地交付快照；本节将已决定事项整理为最终口径，不保留已解决的“待决定”措辞。

**交付前复核。** 2026-10-14在最新main基础上重新核对408个来源文件、128个输入哈希，45题metadata/字段数及现有KB引文均一致（少数原条目本来只含intent/ref，没有source_text，未为整理擅自增加）。45题GT自比通过；135份当前冻结候选重新评分，129通过、6失败，与逐题正式状态一致，失败未修补。老师既有75题GT自比全部通过。公共评分器40项测试、共享运行器10项测试通过；PrepBench脚本14项测试分别在固定镜像和具备FastAPI依赖的本地环境完成，覆盖的14项均通过。固定镜像缺FastAPI导致的单项导入错误由本地假模型HTTP测试补验，不调用外部模型；Windows沙箱临时目录权限失败不计作程序回归。详细交付报告保留在研究者本地delivery_306_260/。

### 306：姓名名单汇总

按原始姓名分组，先比较Naughty/Nice次数，只有并列才取最大合成Index。full/KB明确最终行序不限及文本等价呈现；输入和GT不改，reference仅适配入口。r001与修订后r002分别保留。

**验证与运行。** GT行数：output_01.csv=4269。历史记录：pandas r001通过, r002通过；polars r001通过, r002通过；ibis r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 6000条输入得到4269人；457个并列组已核算，但最大Index自身的冲突标签未出现。

**版本与证据。** 当前任务资产聚合SHA256 `2fcf0f9e0bc152c83be7864b431f44defdeb78c44973152159d823650566f718`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/306/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 305：舞蹈决赛成绩与进步率

清理重复表头及不可计算评分，按Series/Couple汇总决赛均分和相对首次评分周的变化率。最终query公开首次周多支舞取均值，KB同步；原GT保留，评分按九位小数精度容差而非固定格式。题面变化后新建r002。

**验证与运行。** GT行数：output_01.csv=62。历史记录：pandas r001通过, r002通过；ibis r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 62组；当前每组决赛评委数一致，不能区分舞蹈等权与评委加权，超出1—21季的过滤未被实际数据触发。

**版本与证据。** 当前任务资产聚合SHA256 `12dc25ffec29053cdfd88f27bf275baf59e6301cbecc9eac913d7ec0a4a9027b`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/305/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 304：各洲寿命变化排名

标准化多表关联、国家/大洲对比与排名输出，保留既有1950—2020窗口及完整需求。公开交付字段，配置显式类型与精度；按用户决定不追加大洲来源说明。

**验证与运行。** GT行数：output_01.csv=18。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 190个匹配国家均有71年数据和两端年份，缺年、零分母及前三边界并列未触发。

**版本与证据。** 当前任务资产聚合SHA256 `d0e523c76fd8da08c5515bb7a8bb06834b147588b6408da6807e800dbe3e7ea4`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/304/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 303：跨运动球队排名

原query的唯一名次与full/reference/GT并列规则冲突，获批改为允许并列并跳号；Magic/Pacers真实完全并列保留。样本标准差等既有计算规则保持，不公开补充用户已否决的细节。

**验证与运行。** GT行数：output_01.csv=92, output_02.csv=4。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 真实并列已验证；零标准差和单球队运动未出现，reference近零判断不升级为新业务要求。

**版本与证据。** 当前任务资产聚合SHA256 `a521bcb7d8a6bd2557e477733ce23d06a3ffc607c23470cf2713d0cdcb22c884`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/303/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 302：排除：极小表完全重复记录去重

用户决定不纳入：5行客户数据仅按ID删除完全相同记录，剩3行，无冲突合并或其他处理，区分能力过弱。原始资料本地保留，不提交为可运行case。

未安排interact。

### 301：站点客流与坐标

导入站点客流和位置关联任务，明确文件角色、输出字段与数据粒度，显式配置数值精度、身份key及无要求的行序忽略。reference入口适配，保留业务和GT。

**验证与运行。** GT行数：output_01.csv=90, output_02.csv=20, output_03.csv=267。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 实际平均客流无并列、同一站点无冲突坐标；dense排名和三字段去重仅由研究者边界检查覆盖。

**版本与证据。** 当前任务资产聚合SHA256 `c605195757e53e9e46f32902de7be28466c2db16b7f98f4a35efa6f7280a47a5`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/301/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 300：周库存与采购频率

按每周快照推导销售和采购频率；获批在query公开首次周的零值参与平均，KB同步并新建r002。用户决定保持精确文本，不因pandas标签尾空格放宽评分。

**验证与运行。** GT行数：output_01.csv=100。历史记录：pandas r001通过, r002失败；ibis r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** r002 pandas因尾空格正式失败，Ibis/PySpark通过；100条序列均有14个连续快照，缺周、零订单等不由当前通过证明。

**版本与证据。** 当前任务资产聚合SHA256 `8395a184ce5b72515880407692dff4139a7491b574e8a7be1ba6fbf36e0946c4`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/300/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 299：退货退款与月度销售

获批采用HALF_UP四舍五入至分，修改完整需求/KB及reference的舍入实现；保留旧r001，新建r002。空退款额/次数仍为空，不以0代替；年度日历与边界按既有契约。

**验证与运行。** GT行数：output_01.csv=12。历史记录：pandas r001失败, r002通过；ibis r001通过, r002通过；pyspark r001通过, r002失败。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** r002 pandas/Ibis通过；PySpark将应为空的退款额及次数填0，真实失败保留。实际1.995不区分两种中点规则，专用边界检查单列。

**版本与证据。** 当前任务资产聚合SHA256 `c2b5a3500b13791782aa2b15d75539f6781f9a6b4ebb01bf710e7adef1053543`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/299/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 298：累计销售占比筛选

审核累计占比及15%阈值，修复reference浮点边界判断，保留当前GT；百分比按两位小数精度设置容差，不强制尾零或具体舍入算法。

**验证与运行。** GT行数：output_01.csv=11。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 实际没有同额销售或恰15%边界；研究者反例验证边界，未凭实现顺序新增并列取舍。

**版本与证据。** 当前任务资产聚合SHA256 `967df6a203e26818adc6396a37f08940c48b38d092ca13b2947a5ffcb31dae35`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/298/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 297：团体舞去重与歌曲拆分

获批按Series＋Week＋Dance＋原始Music判定同场团体舞，保留首条其他字段再拆歌；同步full/KB/reference/GT。GroupLindy Hop冲突评分保留首条Judges Scores，Total Score缺失；另修复标点正则使7行Theme去引号，GT由2524改为2523行，保留逐项差异。新建r002保留r001。

**验证与运行。** GT行数：output_01.csv=2523。历史记录：pandas r001失败, r002失败；polars r001失败, r002失败；pyspark r001失败, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** r001三后端失败均受21个Stage的GT空值错误影响，Polars还漏清理姓名数字；修正Stage资产后另做r002，不能将旧失败全部归因于模型。r002三者Stage均正确，pandas/Polars仅因Alex & Kevin1未去数字失败，PySpark追问后通过。当前不存在跨Series同周同舞同歌冲突，跨届隔离由专用检查验证；候选未做的最终全行去重未被当前输入触发。

**版本与证据。** 当前任务资产聚合SHA256 `7d5b71e09570fa9866e1bd8db7f9a8b8a20c3d56a24b079102437c09c162f361`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/297/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 296：运动员收入网页表清理

将网页抓取操作改为处理已给输入，公开缺失的年份与文件对应信息；拆分金额并保留独立来源收入列，不为使分项相加一致而改源总额。

**验证与运行。** GT行数：output_01.csv=130。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 130位运动员金额均可解析；一行总收入与分项和不同，按题意分别保留，非法金额分支只经研究者检查。

**版本与证据。** 当前任务资产聚合SHA256 `ea3c7f0c1f56eaeaa5ddb6821f94635a9ee66e85e81d8373aa0eb662ce5c57f5`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/296/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 295：用户事件与耗时汇总

保留首次时间、逐记录向上取整及均值向上取整的既有规则，整理输入输出契约、评分key与类型；不将ceil问题改成HALF_UP或HALF_EVEN偏好。

**验证与运行。** GT行数：output_01.csv=5。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前无首次时间并列、未匹配用户或负耗时；并列边界仅单独验证。

**版本与证据。** 当前任务资产聚合SHA256 `aad9c7fcb2e726abe1917e3a29a67cda15c4813fda9ad23820f3249e452cb8bb`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/295/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 294：工作日收益与名次

完整题意明确两层competition排名（并列后跳号），取消无依据的最终展示排序；reference计算与GT不变。最终按用户确认在query公开Calendar Days=end−start（不加1），收入仍按包含起止两端的工作日计算，KB引用同步后新建r002。Initials空值别名修订仅重评冻结输出，原配置及报告保留。

**验证与运行。** GT行数：output_01.csv=693。历史记录：pandas r001通过, r002通过；polars r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 693条输入、635条参与收益并列；competition与dense差异实际被覆盖，周末-only及同日情形由专用检查验证。

**版本与证据。** 当前任务资产聚合SHA256 `d5d434a792d94ccbc2a722ce23a36f43ad5b683b26cca706d67d11e8872d7f86`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/294/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 293：等级日期区间清理

保留每级最小值、先去无效逆序区间、再按起止日期排序的原规则；重叠比较对象是排序后紧邻的原记录而非最后保留记录，Order允许空缺。

**验证与运行。** GT行数：output_01.csv=693。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 真实40条逆序区间和266条重叠删除，比较对象不同会改变6次决定；起点恰等前终点未在正式输入触发。

**版本与证据。** 当前任务资产聚合SHA256 `54f03d8f0edd2d7cb11238694e3d617a3658a7abb4a672e2f04a448e55f83025`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/293/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 292：比赛日积分榜与近期战绩

比赛按双方展开，按Matchday累计并排名，生成当前及前四场战绩；保留既有末级队名取舍，不将最终展示排序额外强制评分。

**验证与运行。** GT行数：output_01.csv=760。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 每队每Matchday恰一场；缺比分、同日多赛未覆盖。reference在固定pandas2.3.3验证，未承诺pandas3兼容。

**版本与证据。** 当前任务资产聚合SHA256 `146554e92ef903bf5f1b0ddb80ad329dfdba23e51ac2570fc440d653b7a961bb`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/292/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 291：比赛日累计积分榜

比赛展开为两队记录，累计积分、进失球并按完整需求排名；明确计算顺序与最终CSV行序不同，保持无要求的输出行序兼容。

**验证与运行。** GT行数：output_01.csv=760。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前无赛程空缺或同一Matchday多场；reference有被覆盖的多余排序，未将其视为独立业务要求。

**版本与证据。** 当前任务资产聚合SHA256 `e7be135cfa7a120755ddbda4dad104c5402608bb15db416bcbca915d51d49310`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/291/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 290：半结构化比赛记录解析

按CSV记录而非物理换行编号，首条公告不计入，后续公告/空记录计数；解析比赛日、日期、比分与队名，保留原语义。

**验证与运行。** GT行数：output_01.csv=380。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前赛事均可解析且含FT标记；参考解析器的任意网页/格式泛化能力未验证。

**版本与证据。** 当前任务资产聚合SHA256 `9e3598403a4413e25757064f038a91223de61d9bd40ac9df965017e928f3a8d1`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/290/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 289：生日蛋糕与银行假日

用户决定保留既有最近上学日安排及五月银行假日调整，不为统一288而修改。明确两题独立：97个暑假生日在本题安排至7月22日，而288采用7月18日。

**验证与运行。** GT行数：output_01.csv=185。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 无2月29日、缺失生日或空校历；姓名＋生日去重不代表真实人物身份消歧。

**版本与证据。** 当前任务资产聚合SHA256 `a17f902dfd283da30e710c5c93390ba842653510e50fa978a08d34f45eb869d4`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/289/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 288：生日蛋糕与学期安排

保留假期生日安排至上一学期最后周五的规则及原校历，不额外引入289的银行假日修订；按学生人数计数，不按不同生日数计数。

**验证与运行。** GT行数：output_01.csv=186。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 1000名学生唯一，无闰日生日；无上一学期/无合格周五分支只经研究者检查。

**版本与证据。** 当前任务资产聚合SHA256 `5e7dd54ff5580944ba9355da5940998af0554dac9f0a82692cea8052a9f555e7`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/288/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 287：卡牌与图鉴排序

按原query的馆主、道馆、宝可梦及图鉴/等级/编号等排序组织卡牌，保留lookup去重和未匹配保留规则，显式检查要求的最终排序。

**验证与运行。** GT行数：output_01.csv=252。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 实际卡牌均有图鉴匹配、完整排序键不同；小数形态代码及fallback未由实际输入验证。

**版本与证据。** 当前任务资产聚合SHA256 `e3a9f8d619a17273c731e094af31402f0dd118ac28314a3744f3471648bedff8`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/287/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 286：田径成绩宽转长

填充运动员标识，将七项赛事成绩展开，NM保留为空；按原要求检查Position/Event No.顺序，身份与名次严格核对。

**验证与运行。** GT行数：output_01.csv=126。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** Performance混合距离、秒数与冒号时间，当前text_exact无法接受全部语义等价表示；此为已记录比较器限制。

**版本与证据。** 当前任务资产聚合SHA256 `2454a8923dffefaebc0a82c245f39c02c7bd8c89fd82ae41f147802e3dc1860b`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/286/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 285：足球分时段预期进球

保留无进球比赛进入分母、分钟区间、赛事合并与已有HALF_UP规则。独立精确23/40=0.575发现三处GT为0.57，修正为0.58，与reference一致；未改输入。

**验证与运行。** GT行数：output_01.csv=351。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 8个源赛事名映射为7类，169场Championship归Gold Cup；只输出实际出现的分段，不补13个未出现组合，0.005容差不验证舍入算法。

**版本与证据。** 当前任务资产聚合SHA256 `6132925c1dc630958e86fd82ed0a446635ca29bd1a724ea5a00ad80fe8299991`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/285/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 284：车手最快圈速

query/full均要求最短有效圈速，源GT三位车手误用较慢圈；独立最小值与reference一致，修正GT的11/27/31号车手圈速，名次不变。移除full无依据的并列先后兜底。

**验证与运行。** GT行数：output_01.csv=20。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前20人最快圈速无并列且lookup唯一；将来出现并列需另定业务口径，不能凭原实现顺序取舍。

**版本与证据。** 当前任务资产聚合SHA256 `ac245a6115c58c5ec51ba35091eddc4194eaf6a94a521df026ad057036d43d66`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/284/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 283：网球冠军类别与排名

双打逐人展开、清理国家注记，混双计入双打，按单打/双打资格筛选并累计冠军数；competition并列不由最近夺冠年份打破。

**验证与运行。** GT行数：output_01.csv=58。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 有9组总数并列；姓名按清理后的输入文字识别，不做外部别名映射。

**版本与证据。** 当前任务资产聚合SHA256 `822e8641c18a3799d468ef5a51fe4dfb3793cd921d0e4d527c9587e4b62eb187`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/283/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 282：环法赛段与胜场关联

对环法赛事、赛段类型、胜场和完赛数据关联，保留赛段/序幕及非休息日的原筛选，整理明确输出角色、key和字段类型。reference业务与GT不改。

**验证与运行。** GT行数：output_01.csv=294。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 验证范围限于给定赛段、赛季及既有代码映射，未扩充输入。

**版本与证据。** 当前任务资产聚合SHA256 `0d194ecac28f3e52593e586bcdfb684bf11c857661be1261f673bb26289bff83`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/282/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 281：投诉布尔字段与结案日期

获批以query/reference/GT一致的映射为准，修正full及三个KB intent；评分采用显式类型，日期与布尔输出接受语义等价，保留原文本规范化。

**验证与运行。** GT行数：output_01.csv=53。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 输入仅含True/False；输出布尔兼容不等于扩大输入词汇映射，未知输入词未验证。

**版本与证据。** 当前任务资产聚合SHA256 `a19f91256d24c289ee04006c5faf5510098f8ca7f20830ed71ad39152492d04e`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/281/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 280：投诉描述拆分与日期筛选

原reference交换部分年月日，与完整题意冲突。获批按标准年月日修复reference并重建GT，53行变50行，保留旧版及逐条差异。三种规定日期格式独立核验。

**验证与运行。** GT行数：output_01.csv=50。历史记录：pandas r001通过；polars r001通过, r002通过；pyspark r001通过, r002runner_error / skipped, r003通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** pandas r001通过；Polars/PySpark r001虽输出通过但澄清服务故障，不作为完整交互验收。恢复后Polars r002、PySpark r003通过；PySpark r002运行器错误保留。

**版本与证据。** 当前任务资产聚合SHA256 `ddf3c7baf3c2eb88758be1971e3e888fe87df7b88d451b73fbf76715ea5b4b51`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/280/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 279：经理周薪及年度费用占比

周日对齐展开任期，周薪汇总与年度费用内连接；用户保留等价日期兼容。最终在query公开周表Week升序、年表Year升序，只改query并新建r002。

**验证与运行。** GT行数：output_01.csv=830, output_02.csv=16。历史记录：pandas r001通过, r002通过；ibis r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 830周、16年；候选对非法记录的拒绝/跳过行为不完全相同，当前有效输入不触发，DD/MM/YYYY字面格式不强制评分。

**版本与证据。** 当前任务资产聚合SHA256 `16f9bfdef53d8fd02b4122bd2fc9d7e12658b843a74c3e288fe3f6fb809c86e0`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/279/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 278：在职经理工资异常

按批准口径在query公开仅检查在职经理及向偶数舍入，具体工资公式继续留在full/KB。应付工资与差额精确评分，未使用的日期重映射按用户决定保持。

**验证与运行。** GT行数：output_01.csv=3。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 16位经理、10位在职、3个异常；无精确半整数，代码审阅不能替代中点数据验证。

**版本与证据。** 当前任务资产聚合SHA256 `9a68188eacabbf80af6e5d886d21ae2125a40b9446e0a9965a41b6c1dad64f81`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/278/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 277：门店客户忠诚积分排名

保留姓名/邮箱匹配、门店关联、店内积分排名与top筛选；按用户决定保持日期值兼容，不强化full的字面格式要求，不新增题意。

**验证与运行。** GT行数：output_01.csv=65。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 65行；DD/MM/YYYY与ISO输出等价，不把当前匹配结果当作同名客户消歧能力。

**版本与证据。** 当前任务资产聚合SHA256 `2a96384808994b4156a95a0533fdc7fa6e00a5a5e4c9dbe1954d2274ea739b6a`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/277/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 276：忠诚类别性别比例

修复reference缺失性别百分比单元格填0，使其符合既有full/KB；保留当前输入/GT。评分核对类别、计数与百分比，未将模拟用户额外中点偏好升级为要求。

**验证与运行。** GT行数：output_01.csv=3。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前数据未触发两种中点规则的输出差异；已记录模拟用户限制，不据此重开题意。

**版本与证据。** 当前任务资产聚合SHA256 `6ccd43816e85b071caf5d1de21dbc679cf53bada644499be237efad8fc0e030d`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/276/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 275：周一交易排名

按姓名关联客户、解析交易渠道和星期，以Sales作competition排名。最终获批公开Sales降序、Receipt Number升序，KB引用同步；只改query/KB后新建r002。

**验证与运行。** GT行数：output_01.csv=151。历史记录：pandas r001通过, r002通过；ibis r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 151行、两组同额销售，收据号只排展示顺序，不拆并列名次；当前全部客户匹配，不证明未匹配交易保留分支。

**版本与证据。** 当前任务资产聚合SHA256 `0cf148ed9b58508237a9b223e516c4bab551d3170c17c777dba5cb772c5098aa`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/275/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 274：年度金额单位转换

解析年度文件的K/M金额单位并汇总Sales/Profits，公开输入输出角色，采用显式整数/数值规则；reference业务和GT不改。

**验证与运行。** GT行数：output_01.csv=5。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前换算值均为整数，不能区分小数中点规则。

**版本与证据。** 当前任务资产聚合SHA256 `f6481b04e0e198fea0f053ff63f4f3ebfa30c284218ae0d4c25f237b84f457e1`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/274/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 273：物种栖息地温度与优先级

获批query公开有符号温差及排名口径；保留Ray-finned fishes连字符，修复reference/GT额外清洗。按输入两套单位分别独立核算F/C整表答案，配置只能整表择一，禁止混搭单元格；信息变化后新建r002。

**验证与运行。** GT行数：output_01.csv=326, output_02.csv=80。历史记录：pandas r001失败, r002通过；polars r001失败, r002通过；ibis r001失败, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 326物种、80非理想记录，37个负温差、4个缺状态名次为空；本轮三候选均选F，C只有独立/参考验证，非正式模型C运行。

**版本与证据。** 当前任务资产聚合SHA256 `1ba8776cdafd0aff742e0725c2e6ed1b45c61d157d96afa6f7efc38e4fbae71a`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/273/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 272：年度超预算与月度最大超支

原query只排除年度低于预算，full却排除小于等于预算；获批以query为准，将full/KB/reference改为年度相等也保留，当前GT不变。query公开月预算与月实际支出均先half-to-even取整后求差，并列最高超支只取合并输入处理顺序中的首项。金额与差额精确整数评分；独立核算108个年月类别值、12行结果。

**验证与运行。** GT行数：output_01.csv=12。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 三候选均漏内部TransactionFees映射，但12个月均不影响最大项，因此输出通过；这是已观察内部处理限制，不宣称解题过程完全正确。

**版本与证据。** 当前任务资产聚合SHA256 `10bfd3fae1979a135dd86bf9bd2261f0d86c1c672ea7a56fa4630b57267fd549`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/272/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 271：预算与实际支出

修正已批准的类别名称，Forecasted/Actual采用零容差number、Difference采用integer，拒绝旧百分比容差放过的真实金额差。用户否决再补TransactionFees名称澄清，保持题面及原失败。

**验证与运行。** GT行数：output_01.csv=9。历史记录：pandas r001失败；polars r001通过；ibis r001失败。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** Polars9行通过，pandas/Ibis各漏交易费而仅8行，ROW_COUNT_MISMATCH保留；拒答及名称说明差异不全归为计算错误。

**版本与证据。** 当前任务资产聚合SHA256 `4a199339261984c4b25f6daafc0ec982060224cf2d10e37e41ff7f13771e82e3`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/271/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 270：召回移除速度及超时

保留日期级截止、分组平均及排名规则；最终行序不是原query要求，忽略展示排序但仍精确检查Rank。reference业务及GT保持。

**验证与运行。** GT行数：output_01.csv=10, output_02.csv=10。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 只有日期无日内时刻；模拟用户额外中点规则对当前答案无影响，保留观察而不新增题意。

**版本与证据。** 当前任务资产聚合SHA256 `009999504e3415782c74894588dd5d9f9ff05493079c5064258bd9fea5aad4e9`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/270/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 269：召回损失与门店优先级

导入召回数据与成本/门店关联、损失计算和优先级任务，公开文件角色，显式配置key、数值精度和类别；reference业务及GT保持。

**验证与运行。** GT行数：output_01.csv=5, output_02.csv=10。历史记录：pandas r001通过；polars r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 保留当前输入验证边界，不凭未出现数据扩充业务规则。

**版本与证据。** 当前任务资产聚合SHA256 `6cfd6acd1d150f430fdeed059185dfbbd774e50d09174793962e5c1eb6c76d9c`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/269/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 268：复活节相对周销售

删除依赖缺失图表的描述，保留按每年真实复活节对齐第12周、逐记录保留及Price×Quantity Sold。用户决定接受等价日期，不强制DD/MM/YYYY。

**验证与运行。** GT行数：output_01.csv=1752。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 2020—2024五年1752行，周序1—12；无重复日期/产品键或非午夜时刻。

**版本与证据。** 当前任务资产聚合SHA256 `631b963afad9bcf0bab09b3f43b01a6a37e7a230d78f5cebc87ef479990294d2`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/268/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 267：逐年借款、利息与还款

虽仅两张各2行输入，但确有跨表关联、年度展开、利息及还款，用户决定保留。最终在query明确余额取还款后，KB同步并新建r002，旧首轮失败保留。

**验证与运行。** GT行数：output_01.csv=1。历史记录：pandas r001失败, r002通过；polars r001失败, r002通过；pyspark r001失败, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 只评分请求的35000快照及单行汇总，不代表所有贷款参数均验证。

**版本与证据。** 当前任务资产聚合SHA256 `9013d7edbe0c0309f719fbab672931541f526d0ec188d13a767d87470a9b6ab9`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/267/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 266：排除：固定28天月份日历

用户决定不纳入：主要按2024年生成28天月份日历，reference不使用输入内容，数据处理区分能力不足。原始资料本地保留，不提交为可运行case。

未安排interact。

### 265：交易、会员与产品清洗

原浮点数量/利润计算与完整规则不一致，获批以Decimal向下取整数量、计算折后销售额和HALF_UP利润；GT修正2078个Quantity和3037个Profit数值。full/KB修正Goald/Sliver/Bronz规范化与原query的冲突；query公开缺会员/折扣/原销售额时销售额和利润为空及利润HALF_UP两位。Decimal独立核对39254行。按批准配置Sales Before Discount精确数值比较，接受14.7/14.70，Date与Quantity继续精确文本；冻结r001重新评分，不重新解题。

**验证与运行。** GT行数：output_01.csv=39254。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 当前数量都是整数且无缺价/零价/负价，不能验证fractional floor分支；模拟用户额外half-even在当前四位小数上无影响，不作为新要求。

**版本与证据。** 当前任务资产聚合SHA256 `d4d8d21a3c93330ede5f9e0bbfb0a31387c6335af0db5712ba3c9fbdc75a9f79`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/265/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 264：航班预订累计

公开累计处理的必要顺序，按最新动作保留取消/预订状态并关联航班；兼容语义相同数字ID表示，保留业务值严格评分。

**验证与运行。** GT行数：output_01.csv=500。历史记录：pandas r001通过；polars r001通过；ibis r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 实际最新日期无并列，非取消记录客户ID非空；候选额外按Flight Date关联在当前数据不改变结果。

**版本与证据。** 当前任务资产聚合SHA256 `617a91e67aa7f492286ebc17c183e3afdefed218fbf40dcf50d36cd0fafb17a9`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/264/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 263：两种会员方案年度成本

以飞行数分档，继承所有低等级福利，汇总各等级成本及不同客户数。获批整数与Tier n标签兼容；最终query公开两表Tier升序，新建r002，保留原TYPE_ERROR及标签重评。

**验证与运行。** GT行数：output_01.csv=6, output_02.csv=3。历史记录：pandas r001通过, r002通过；ibis r001通过, r002通过；pyspark r001通过, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 6行/3行；成本abs_tol=1e-8仅容纳算术表示误差，不接受舍入到分。无重复规则福利对，候选未显式去重；零成本且有费用匹配的福利计数保留。

**版本与证据。** 当前任务资产聚合SHA256 `2ad8beb9d78a9ea596e6a74d0b7f9067a98cd2f253c2c2fac24832b12c5f5f38`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/263/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 262：情侣情人节次数与礼物

用户要求将既有次数/姓名排序公开到query，KB同步；删除公开说明中提前透露的未匹配礼物保留规则，该细节仍可交互获得。最终版本为r003，r001失败及r002均保留。

**验证与运行。** GT行数：output_01.csv=10。历史记录：pandas r001失败, r002通过, r003通过；polars r001失败, r002通过, r003通过；pyspark r001失败, r002通过, r003通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 输出字段及排序严格核对，未因行数/礼物匹配的历史失败放宽评分。

**版本与证据。** 当前任务资产聚合SHA256 `5f51cee584c8eb94d521bf5106f03e4b594ff874459b7d64c82beb6460e87131`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/262/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 261：最新员工工资及税档

按原行位置选员工最新记录，汇总工资并计算题设税档；获批query用英文明确未达到税档的字段留空，KB同步并新建r002。

**验证与运行。** GT行数：output_01.csv=803。历史记录：pandas r001通过, r002通过；ibis r001通过, r002通过；pyspark r001失败, r002通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 模拟用户有时额外要求保持输入行序，未采纳为评分要求；当前CSV无嵌入换行，Spark按物理行解析的泛化未验证。

**版本与证据。** 当前任务资产聚合SHA256 `b9538590b6e1b3b69f6604fd960aaba4d1adcdeea8a505f53d5280f411835916`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/261/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。

### 260：航班预订及未预订客户

按批准固定天数分档，取消full多余最终排序，兼容ID及四类名称，金额精确；五个日期字段明确采用严格YYYY-MM-DD。用户否决额外补公开全年范围，保持现契约。

**验证与运行。** GT行数：output_01.csv=44768, output_02.csv=296, output_03.csv=1260。历史记录：pandas r001通过；ibis r001通过；pyspark r001通过。当前采用版本见头表下方的本批版本说明。

**限制与失败解释。** 三表44768/296/1260行；未预订客户无非法、缺失或未来最后飞行日期，-1/Recent分支保持但未被实际输入触发。

**版本与证据。** 当前任务资产聚合SHA256 `d080846ad76e8b994bec90ff9dc968a139436ae9cd1c16f3e4429a714b9afb4d`（按仓库相对路径排序，以`路径:文件SHA256`加换行聚合）。本地`curation/output/260/review.json`、`source_manifest.json`、各轮`interact_plan*.json`及`final_review*.json`记录原始来源、独立/边界检查、资产和评估版本；正式候选及问答在该题`runs/interact/codex_gpt-6-astra/<backend>/<run>/`。


## 2026-10-10：072–073 导入与验证（curation/prepbench-07x）

**状态：资产导入、固定镜像 reference、独立核算及六组真实 interact 完成；4通过、2失败。073本轮验证完成，072存在九位小数舍入契约问题待决定。** 当前主工作目录 dfArena；没有从相邻 curation worktree 复制运行记录。070 按用户决定保留内部空格要求及精确文本评分，不修改其 query_full、KB、reference、GT、config 或失败候选。

来源为 `../prepbench/data/case_072/073`、`reference/solutions/case_072/073/solution.py`、`src/evaluate/gt/case_072/073`。输入与 GT 按原字节复制，来源哈希见本地忽略的 `curation/output/07x/import_072_073.json`；当前资产哈希另存 current_assets_072_073.json。reference 仅修复入口为 case 根目录 inputs/output，业务实现未改。没有共享 runner/evaluator/simulator 代码修改。

**072。** 20个内部ID、47个第三方ID，均各自唯一。先按ID精确匹配，再在未匹配部分按Scent形成候选，按销售差绝对值先为第三方选最近内部ID，再对内部ID去重；不重新分配次优候选。query保留匹配歧义，在Output公开四个精确Status标签及输出粒度；query_full补明一次两阶段筛选、按内部/第三方原行序解决相同差值、精确匹配采用内部Scent、无最终行序要求。KB纠正不存在的pairs_filtered引用并同步规则。key为ID/3rd Party ID，身份空字符串按精确文本保留；Status/Scent精确文本，两个Sales为number，abs_tol=5e-10、rel_tol=0、仅空字符串作为null。依据为GT九位小数的半末位精度，允许输入原精度，不强制九位小数字面格式。独立Decimal逐第三方提名、逐内部选择得到49行：Matched 5、Matched on Scent 13、Unmatched - Internal 2、Unmatched - 3rd Party 29。42个第三方提名因内部冲突保留13个；现有数据没有最小差并列，不宣称验证并列规则或重复源ID行为。

**073。** 三输入分别8/2/4列；site属性CSV有额外前导行、星号分隔行及来源页脚，保留原输入。query/query_full删除重复Input Data项并补输出行含义，不在初始query提前给出top-1规则。query_full/KB补输入header位置、过滤无效站点、trim站点名/人员Skill、重复人员地点保留首条，以及无合适地点时不输出、无最终行序要求。基于skill成员关系、season交集、board交集同时成立筛选，按Rating降序及五级Reliability降序取每人一个地点。key为Name，Rating零容差number，其他字段精确文本；输出显示顺序不评分，选最佳地点的计算排序必须正确。独立集合核算：Tom/Jenny/Carl/Jonathan分别有2/1/7/11个合适地点；最佳分别为Thurlestone Reef/Salcombe/Bigbury Bay/Thurlestone Reef。Carl的两个最高评分地点通过可靠性区分，无最终双重并列；全部4人有结果，源数据不验证无匹配人员、真正重复站点或双重并列的处理。现有query_full未定义评分与可靠性都相等时的唯一选择，记录覆盖限制，不凭reference默认排序增加第三排序字段。

**验证。** 两份reference在镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921` 执行并通过当前评估，输出49/4行；GT自比、独立结果、重复行拒绝、错误匹配/状态拒绝、销售精度边界、错误最佳站点/评分/文本拒绝等共19项检查通过。证据脚本及报告在本地 `curation/output/07x/verify_072_073.py`、validation_072_073.json、reference_072/073_execution.json、reference_072/073_evaluation.json。

**真实运行计划。** seeds为20261010072/20261010073，两题均抽到Ibis/Polars，加pandas；先各题pandas再启动该题两个抽样后端。Codex gpt-6-astra/low、simulator gpt-6-astra/temperature 0、固定上述镜像、1800秒上限。实际结果如下。未提交或推送。

| Case | Backend | Run | 正式评测 | 行数 | ask次数 | agent秒数 |
|---|---|---|---|---|---|---|
| 072 | pandas | r001 | 通过 | 49 | 2 | 64.62 |
| 072 | ibis | r001 | 失败：VALUE_MISMATCH | 49 | 2 | 84.02 |
| 072 | polars | r001 | 失败：VALUE_MISMATCH | 49 | 2 | 83.27 |
| 073 | pandas | r001 | 通过 | 4 | 2 | 80.17 |
| 073 | ibis | r001 | 通过 | 4 | 1 | 78.13 |
| 073 | polars | r001 | 通过 | 4 | 1 | 61.22 |

072三组均获得“两阶段去重、不重分配”澄清，49行匹配关系/状态/Scent/空值完全一致。Ibis有3个数值、Polars有2个数值比GT高1e-9，其余数值一致。例：输入78530.3866906395，GT/reference的二进制float格式化得到78530.386690639，Ibis/Polars Decimal得到78530.386690640；输入21304.1041794475也出现同类差异。Ibis另对70989.4678953545使用HALF_UP得到70989.467895355，GT/Polars为70989.467895354。前两例精确Decimal HALF_EVEN和HALF_UP都向上，所以不能仅规定HALF_EVEN来复现全部GT。原query未规定数值舍入，完整需求仅说最多九位小数，未要求复现二进制float的边界偏差；不能把这些差异笼统当作匹配错误。

正式config暂保留abs_tol=5e-10，原失败报告及候选不改。另存 proposed_072_config_abs_tol_1e-9.json，以1e-9容差诊断性重评三份冻结候选全部通过（diagnostic_072_abs_tol_1e-9.json），不计作正式通过。建议按允许不同九位舍入边界的语义将容差定为1e-9，但本轮没有据此改正式配置，待用户决定。完整逐字段差异见diagnostic_072.json。

073三组均得到全部三个适用条件同时满足、精确技能成员关系而非技能等级阈值、每人只取一个最佳地点的正确澄清，输出均与GT一致。pandas使用cross merge、集合交集过滤、去重排序；Ibis/Polars使用各自后端的关联、列表/数组成员及交集、排序选择。当前候选仍有未覆盖的实现限制：073 pandas要求季节映射完整，Ibis/Polars用inner join而非完整需求的left join，现有16个有效地点均有季节映射，故输出不受影响；072 pandas断言精确匹配的两侧Scent相同，当前5对满足，未覆盖题面允许的不同Scent。无API/网络失败。部分多主题提问被拒后拆分重问，成功获取规则；各组ask调用数均为有效轮数。实际结果和问答保留在runs目录及interact_results_072_073.json。



## 2026-10-09：070–071 导入与静态审核（curation/prepbench-07x）

**状态：权限恢复后，两份固定镜像 reference 已执行并通过；六组真实 interact 已完成，4通过、2失败。** 先前 Docker socket 访问拒绝已解除。reference 使用固定 Docker 镜像中的 pandas 3.0.2，070 输出63行、071输出1行，均通过当前正式配置；执行及评测报告在本地 `curation/output/07x/reference_070/071_*`。主机 .venv 另安装了 pandas 3.0.6，但本轮 reference 验证使用的是 Docker 环境。

来源为相邻 `../prepbench/data/case_070/071`、`reference/solutions/case_070/071/solution.py` 及 `src/evaluate/gt/case_070/071/`。输入与GT逐字节保留，来源哈希在忽略的本地 `curation/output/07x/import.json`。新增metadata、标准reference/evaluation目录。reference仅调整主入口路径，从case根目录读取inputs并写output，业务计算未改。070领域media_culture，1张输入/1列DownloadData；071领域education，3张输入分别1/2/1列。无共享runner/evaluator/simulator修改。

**070。** 网页抓取半结构化文本整理为Date/Battle/War/Victors/Description，每行一个完整战役记录。输入文件虽为.csv，仍按完整原始行解析，不将其中描述逗号误当列分隔。初始query将dateparse软件函数提示改为中性的日期解析表述；两份题面补输出行粒度及精确列名。完整需求补全四个明确日期格式、移除原query未要求的保留输入行序；明确原reference/GT已有的Ł→£纠错、保留&amp;字面形式，以及不从外部知识改写事实。KB修复不连续拼接的source_text引用，同步dateparse替换并补文本规则。未把完整解析算法加入初始query。

标准库独立拆解HTML段和手工月份字典解析日期，65条源记录排除Battle of the Standard（缺War）、Battle of the Braes（不能得到五个完整字段），得到63行，与GT逐字段一致。63个战役名唯一；两场St Albans通过内部标题区分，无需去重。两条日期范围取起始日；991 AD和1578补1月1日。3条War含字面&amp;，1条Description修正英镑符号。Roundway Down结构日期为30 June 1643而叙述为13 July 1643，保留源结构字段、不做历史事实纠正。key为Battle/Date；日期语义比较，追加%d/%m/%Y，文本精确且不自动清理空白；行序不评分，日期字面格式也不评分。Description内部空格保留。源reference部分匹配区分大小写，而query_full称不区分大小写；现有输入没有触发差异，记录为参考实现覆盖限制。标题fallback、未知日期、同名同日重复记录等未由现有数据充分覆盖。

**071。** 按原任务完成字符展开、位置顺序、映射表左关联和条件求和，保留scaffold输入及完整需求中的使用约定；原query无软件操作需删。输出每个给定罗马数字一行，key为Number精确文本，Numeric Equivalent用integer精确比较，不继承旧number的2%容差。独立用“全部符号之和减两倍减法项”核算MMMCDXVII的9个字符，唯一减法项为C(100)，结果3417，与GT一致；mapping7行，scaffold49行。与057不同，该题reference实际使用merge/apply/sum，但仅一个输入字符串和一个输出，属于小规模教学型workload；不宣称能够验证通用Roman语法、未知字符、scaffold不足或多输入行。当前reference读取首行，与原query_full单个字符串约定一致，不额外扩充输入。

**验证。** 两题共18项检查通过，包括独立结果、GT自比、重复行拒绝，070乱序/ISO日期（含0991年）接受、文本尾空格/日期区间末日/HTML实体解码拒绝；071整数.0接受、加1/非整数/未减法结果拒绝。metadata表数列数、KB原文引用和reference语法检查通过。脚本和报告位于本地 `curation/output/07x/prepare.py`、`validate.py`、`validation.json`，不作为运行依赖或提交资产。独立核算通过不等于原reference已经执行。

**运行配置。** seed070=20261009070，pandas后抽到PySpark/Ibis；seed071=20261009071，pandas后抽到Ibis/Polars。使用固定image `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`、Codex gpt-6-astra/low、simulator gpt-6-astra/temperature 0、1800秒上限。各组均为当前目录新建r001；先完成每题pandas，再启动该题两个抽样后端。计划及结果保存在本地interact_plan.json和各自runs目录。

**真实 interact 结果。** 六组 generation 均完成，正式评估如下；未修改候选、GT或评分规则来消除失败。

| Case | Backend | Run | 正式评测 | ask调用数 | agent耗时（秒） |
|---|---|---|---|---|---|
| 070 | pandas | r001 | 通过 | 2 | 108.55 |
| 070 | pyspark | r001 | 失败：VALUE_MISMATCH | 4 | 492.23 |
| 070 | ibis | r001 | 失败：VALUE_MISMATCH | 5 | 639.93 |
| 071 | pandas | r001 | 通过 | 1 | 48.94 |
| 071 | ibis | r001 | 通过 | 1 | 62.53 |
| 071 | polars | r001 | 通过 | 1 | 67.18 |

070 的 PySpark/Ibis 均输出63行，逐字段核对唯一差异为 Battle of Edgehill 的 Description：源文本/GT在 `1642.` 后有两个空格，候选合并为一个。当前完整需求要求保留Description内部空格，精确文本评分因此失败；正式失败保留。两组首次 simulator 调用出现RuntimeError，随后模型连接发生持续重连，原run自动恢复后完成；耗时包含故障等待，不适合直接作后端性能比较。PySpark共4次ask（1次错误、3轮有效澄清）；Ibis共5次ask（1次错误、3轮有效澄清、1次quota reached）。关键日期、标题、实体保留、Ł→£规则在问答中传达，但未明确追问Description内部空格规则。071三组均澄清紧邻字符减法规则并输出3417；实际实现包含展开或cross join、lookup join、shift/lead以及分组求和。当前数据仍不覆盖未知字符等行为。详细结果在本地 `curation/output/07x/interact_results.json`，原始问答、代码和正式报告在各自runs目录。未提交或推送。


## 2026-10-09：058 正式容差改为0.01并重评

按用户确认，仅将 Sales 的 abs_tol 从0.005改为0.01，rel_tol保持0。保留源GT、reference、query、query_full、KB和输入，不采用此前提出的精确乘积GT方案。该规则接受相对源GT不超过一分钱的差异（含边界），适用于所有Sales单元格，不仅限于舍入中点；不验证特定舍入算法或严格两位小数字面格式。

修改前的config及三个r001的evaluation.json/result.json保存在忽略的本地 `curation/output/05x/formal_058_tol001_20261009/`。通过正式evaluate.py重评pandas、PySpark、Ibis现有r001，三者均通过并刷新正式evaluation/result；顶部总览采用此次新配置重评结果，下方2026-10-08运行表仍保留首次0.005规则下的失败历史。未重新生成，不称作新的interact运行。哈希确认generation记录、候选代码和CSV均未改变。

定向边界检查：相对GT加减0.01通过，加减0.0101拒绝。详细验证与新config哈希见上述目录的verification.json。058精度口径至此已决定，无需修改GT或继续筛选运行。


## 2026-10-09：057 排除出 benchmark

用户确认跳过057，不纳入本次任务资产或正式benchmark。该题核心是装箱规则和Python循环算法，reference中的pandas主要负责CSV读写、行访问和结果组装，DataFrame语义考察较弱；另有箱数优先与空余容量优先的契约冲突。不再修订该题目标或安排interact。

已将本轮导入资产移至忽略的本地审核归档 `curation/output/05x/excluded_case_057/`，`PrepBench/case_057/` 保持空目录，不添加占位文件。上游 `../prepbench` 原始资产未改；既有独立核算和reference验证证据保留。下方057迁移记录为排除决定之前的历史过程，不代表当前仍待迁移。Git不跟踪空目录，因此057任务目录不会进入提交。


## 2026-10-09：059 公开部门排名范围

按用户确认，在 query.md 的部门 SLA 排名条目下、Closed cases only 后新增：

> For output_03.csv only, include departments whose SLA Agreement is 18 business days and whose SLA achieved percentage is greater than 0.

将完整需求已有的两个范围限制公开到初始请求，并以 output_03.csv only 限定作用范围。query_full 和 KB 已包含同一规则及全局计数不受限的解释，无需修改；KB 原文引用核对通过。未改变输入、reference、GT 或评分配置。此前三个 r001 的失败结果仍是旧题面历史结果；本次仅修改题面，尚未新建 generation run 验证，不能将旧候选诊断视为新题面通过。




## 2026-10-08：055–059 迁移与验证（curate/prepbench-case-05x）

本轮在主工作目录新建分支，未改 050–054 已有资产或历史候选。055–059 来源为相邻 `../prepbench/data/case_XXX/`、`reference/solutions/case_XXX/solution.py` 和 `src/evaluate/gt/case_XXX/`。inputs 和 GT 均逐字节保留；来源路径及 SHA256 在本地 `curation/output/05x/import.json`。新增 metadata（055 为 public_sector，其余为 business）、标准 reference/evaluation 目录，reference 主入口统一从 case 根目录读取 inputs 并写忽略的 output/。

**055。** 一行代表候选人在一个 Poll/End Date 的结果。初始题面没有 Tableau 操作；两份 query 补充行粒度、精确列名及 Sample Type 标签，不公开日期年份或排名计算答案。完整需求明确保留零得分、前两个候选人结果之差（保留并列），移除原始 query 没有的强制四字段输出排序。无效日期的有效候选人结果保留，同一 Poll 的空日期为一组，这是本轮明确的边界规则，当前输入不触发。KB 补自然语言 intent、同步引用和展示约定；reference 使用 dropna=False，并以 transform 替代 groupby.apply，避免 pandas 3 丢分组列。当前 GT 不变。key 为 Poll/End Date/Candidate；文本精确，Rank 为 integer，Poll Results/Spread 为零容差 number；End Date 按日期值比较并支持 DD/MM/YYYY，行序不评分。

49 条输入去掉平均行，48 组民调展开后删除一个 --，输出 383 行；31 组有得分并列，无榜首并列、单候选人组、无效日期或 Unknown 输出。标准库独立核算全部字段与 GT 一致，固定镜像 reference 复现 GT。12 项评分检查通过，包括错误 min/dense 排名、得分/差值/排名加1、重复行和误删零得分拒绝，乱序与 ISO 日期接受。pandas、Ibis、Polars interact r001 均通过，关键年份/并列/差值规则在问答中正确传达。Ibis 首轮合并缺失处理和排序的问题被拒，拆开追问后获得回答。通过不覆盖未触发边界或日期字面格式。

**056。** 清除 Profile Pane 操作和 2019.3.2 版本说明，明确 input_01 是 256 个笛卡尔组合、input_02 是四个独立属性列表，两者为替代起点，不应拼接为订单。保留全部七条线索和原业务歧义；输出每个客户一行，key 为 LastName，Priority 为 integer，其他文本精确，忽略无要求的行序。独立枚举原始四列表的排列并检查所有七条线索，恰有一个四行解，与 GT 一致；两份输入的属性组合也已核对。reference 在固定镜像复现 GT 内容（其行序与源 GT 不同，不构成错误）。

**057：契约待决定，未启动 interact。** 原 query 要求减少箱数，query_full 背景更明确 primarily minimize number of boxes；reference/GT 却依次分配120/24/6的满箱，仅余数使用一个最小箱。独立枚举证明 GT 对应先最小化空余容量、再最小化箱数。7 个订单中5个与箱数优先不同：17块3箱 vs 1箱，48块2 vs 1，60块4 vs 1，470块10 vs 4，801块11 vs 7。已提出保留 GT 并修正两份题面目标的方案，尚未应用。标准目录、输出文件角色、业务 key（订单；订单/箱号）和精确整数配置已准备；Order Number 为精确文本标识符，保留原表示。修复 KB 中并非原文的 “Soaps in Box - Last Box Per Box Size” 引用，改为真实字段名并补充按订单/箱型计数的 intent。reference/独立核算与7行订单表及33行箱表一致，但这不解决契约冲突。箱号计算顺序按内容验证，不将源 GT 的随机行排列规定为输出顺序。

**058。** 两份 query 公开精确 Secnt 列名及 lookup 的 canonical 标签，保留 Lavendar 拼写；完整需求取消无原始依据的自定义 scent/size 排列，KB 同步。三张输入分别80/320/32行；独立按空白/大小写清理后的 scent、后缀拆分和 ISO 周关联，用 Decimal 乘法核算307行，13个零占比被排除。key 为 Year Week Number/Secnt/Size/Product Type；周号 integer、文本精确、Sales abs_tol=0.005/rel_tol=0。依据是完整需求两位小数而原始 query 未规定舍入；最大未舍入差为0.005，15行落在半分钱边界。该配置允许未舍入值，不声称验证精确舍入算法，不接受相差一分钱的另一舍入结果。行序不评分，reference 保留稳定展示顺序而非新增任务要求。当前数据没有负占比，跨 ISO 年边界和去重分支不据此宣称已覆盖。

**059。** 删除过期“26th Jan 更新输入”的提示，公开三个输出文件角色及 Missed SLA/On Track to Meet SLA 精确标签。保留原 query 的业务歧义；query_full/KB 明确只有部门排名限制 SLA=18，全局两个计数覆盖所有匹配 SLA 的部门。部门先按未舍入百分比降序、名称升序分配连续名次，排名表按名次输出。key 分别为 Current Status、Metric、Department；计数和排名精确 integer，Achieved % abs_tol=0.005/rel_tol=0（百分数单位的半个末位），身份文本精确；仅排名表检查 Department Rank 升序。独立逐日累计工作日秒数，不复用 reference 的 busday_count 公式：2542个事件、665张票，103张已关闭，32超时/71达标，与 GT 三表5/2/5行一致；32个已关闭票的开始、35个结束在周末。SLA=18 的6个部门中 Marketing 达标率为0被排除，留下5个排名部门。SLA=18及排除0%来自原 query_full/KB/reference，而非原 query 明文，保留其隐藏范围可发现性限制。当前无关闭后重开、恰等于 SLA 或调整后负时长，不能验证这些边界；分钟/秒精度的实现差异也不能仅凭汇总通过排除。

**环境与验证证据。** 固定 Docker image `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`（pandas 3.0.2），研究者侧 reference 验证与 agent 容器分开。056–059 共36项独立核算、GT自比、reference复现、重复行/错误值/容差边界/排名顺序检查全部符合预期；不把057的计算一致视为契约正确。详见本地 `curation/output/05x/validation_056_059.json` 及可复核脚本。初始引用逐条检查，metadata 与真实 CSV 表头一致。未修改共享 evaluator、runner 或 simulator；未扩充任务输入或改写 GT。

**真实 interact 计划。** Codex gpt-6-astra/low，simulator gpt-6-astra/temperature=0，同一固定镜像，1800秒上限。seed 分别20261008055/056/058/059，每题先pandas后两个不重复后端：055 Ibis/Polars；056 PySpark/Polars；058 PySpark/Ibis；059 Polars/PySpark。当前运行与私有资产哈希记录于本地 `curation/output/05x/plan_*.json`，候选和问答保留各 case 的 runs/；这些本地证据不作为任务运行依赖，不提交。不得修补候选 CSV 后记作通过。

**058 精度复核（2026-10-08历史记录；已于10-09决定采用0.01容差）。** 源 GT 与精确 Decimal HALF_UP 有9行差异，与精确 HALF_EVEN 有8行差异；query_full 没有规定舍入模式。pandas/PySpark/Ibis r001 分别有6/7/9个 Sales 与源 GT 相差0.01，其余字段和业务key全部一致，所有候选对精确乘积的最大误差均为0.005。例2259.435，GT2259.43而候选2259.44，二者都距精确值0.005。因此本轮 VALUE_MISMATCH 不直接归因为 agent 业务计算错误。提出以未舍入精确乘积作为 GT、维持0.005容差的方案，本地副本离线比较三后端均通过；尚未采用，不算正式通过，也未覆盖源 GT、候选或正式报告。具体差异和方案见本地 `curation/output/05x/diagnostics.json`、`058_decision.md`、`proposal_058_exact_gt_comparison.json`。若修改完整需求/KB，须新建生成验证；仅旧CSV重评不能宣称新题面interact通过。

**059 澄清可发现性。** pandas r001 两个全局汇总表通过，部门表12行，未获得SLA=18或排除0%的规则。Polars r001 两个全局表通过，部门表6行；它拆分被拒绝的多主题问题并用满三轮，最终获得SLA=18，但未取得排除0%的规则。仅在内存诊断中按隐藏范围过滤并重新排名，两份冻结输出均与GT五部门匹配；正式候选不改，失败保留。这是隐藏过滤条件未获得的交互失败，不能笼统称为收到规则后实现错误。


**本轮最终运行结果。** 055/056各三组通过；058/059各三组正式失败，均完成生成，无评估跳过。057当时因契约待决未启动，后于2026-10-09决定排除，不再运行。未通过重复运行筛选成功结果；所有run为当前分支资产下的r001。

| Case | Backend | Run | 正式评估 | 输出行数 | ask次数 | agent秒数 |
| --- | --- | --- | --- | --- | --- | --- |
| 055 | ibis | r001 | 通过 | 383 | 2 | 147.88 |
| 055 | pandas | r001 | 通过 | 383 | 1 | 93.86 |
| 055 | polars | r001 | 通过 | 383 | 1 | 104.40 |
| 056 | pandas | r001 | 通过 | 4 | 1 | 97.47 |
| 056 | polars | r001 | 通过 | 4 | 1 | 83.95 |
| 056 | pyspark | r001 | 通过 | 4 | 2 | 138.05 |
| 058 | ibis | r001 | 失败：VALUE_MISMATCH | 307 | 1 | 134.41 |
| 058 | pandas | r001 | 失败：VALUE_MISMATCH | 307 | 1 | 90.79 |
| 058 | pyspark | r001 | 失败：VALUE_MISMATCH | 307 | 1 | 104.72 |
| 059 | pandas | r001 | 失败：ROW_COUNT_MISMATCH | 5/2/12 | 1 | 122.27 |
| 059 | polars | r001 | 失败：ROW_COUNT_MISMATCH | 5/2/6 | 3 | 205.46 |
| 059 | pyspark | r001 | 失败：ROW_COUNT_MISMATCH | 5/2/12 | 1 | 193.74 |

056三后端都正确获得优先级方向、相邻关系及属性唯一性；PySpark首轮多主题问题被拒，拆开追问后通过。059 PySpark最终与pandas相同：前两表通过，部门表12行，未获得SLA=18及排除0%规则；内存诊断仅过滤范围并重新排名后匹配GT。三后端正式失败均保留，未修改候选/正式报告。

运行与问答详见 `case_XXX/runs/interact/codex_gpt-6-astra/<backend>/r001/` 的 `result.json`、`detail/evaluation.json`、`logs/interaction.jsonl`。本地汇总为 `curation/output/05x/interact_summary.json`，最终资产SHA256为 `current_assets.json`。当前分支未提交或推送；未执行新的050复验，051–054沿用既有审核。

## 2026-10-08：051–054 初步结果确认

051–054 的 12 次三后端 interact r001 已全部完成生成及正式评估，共 10 次通过、2 次失败；上方总览及下方各题记录保留原始正式结果。051、052 为 pandas/Polars/Ibis 均通过；053 为 pandas/PySpark 通过、Polars 因 Month 保留 Feb-2019 而 TYPE_ERROR；054 为 Polars/Ibis 通过、pandas 因未获得 Week 5–8 范围而多出 bar/Week 1，ROW_COUNT_MISMATCH。

用户确认 052、053 保持当前整理后的任务和评分配置，不为消除失败继续修改。054 当前也保留原始初步结果；pandas 未获得报告范围澄清，与获得正确规则后实现错误区分，隐藏规则可发现性仍记作任务限制。053/054 暂不评分行序，052 的周偏移与精度口径、054 预算版本/周范围依据及两列预算选择矛盾等审核限制继续保留。未重跑或修改候选以筛选通过。

本次提交范围为 case_051–054 的任务资产、NOTES.md 和本日志。下文引用的 JSON 快照、REVIEW_052_054.md 和 runs/ 是本地审核证据，不纳入本次提交，也不是运行依赖；主要结论与待决项已写入本日志。



## 2026-10-07：NOTES 流程重整与 052–054 导入（初步审核）

按用户确认重整 NOTES.md：以首次整理 case 的六步流程为主线，说明完成标准、资产可见性、评估规则、interact 抽样、错误归因、修改后复验和提交清单。加入 021–023、051 的经验，区分内容通过与排序/字面格式/隐藏规则的覆盖；固定 worktree、环境与配置来源。文档链接、JSON 示例和 diff 空白检查通过。

052–054 来源为相邻 prepbench 仓库的 data/、reference/solutions/ 和 src/evaluate/gt/；完整来源哈希见 import_cases_052_054.json。输入与 GT 逐字节保留。新增标准 metadata、reference 与 evaluation 结构；reference 入口从 case 根目录读 inputs，写忽略的 output/。054 query 删除 Excel 工作簿、禁止手写计算和过期更新时间的背景，改为 supplied CSV；两份 query 的 Week worksheets 改为 weekly sales input files。原有业务歧义与 KB 条目保留，所有 source_text 引用已核对。

评估使用业务 key：052 为 Week，053 为 Month，054 为 Type/Week；显式字段规则替换旧全字段 key 和隐式 2% 容差。052 两位金额先精确比较，053 工资总额/人数为 integer，均值 abs_tol=5e-10、rel_tol=0，Month 解析 %m/%d/%Y 或内置 ISO；054 周号/数量为 integer、金额零容差、Type 为 text_exact。053/054 的源 GT 不符合完整需求的排序要求，052 的标签不能由当前协议按隐藏的年/周排序，暂不评分行序，冲突留人工裁定，不以放宽行序宣布契约已完全一致。

固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921 中，054 原 reference 的表头探测遇到 NaN 报 TypeError，改为 fillna("") 后转字符串，未改业务计算。三题 reference 均复现源 GT 内容。标准库独立核算：052 为 153 条汇率、31 条销售、22 条输出，9 个未匹配销售周排除；053 为 17 名员工、13 个月；054 为 108 条销售、16 个产品/周组，输出 5/6 行。32 项 GT 自比、错误字段、重复行及行序检查符合当前评分预期，详见 validation_cases_052_054.json。

人工待决及覆盖限制集中见 本地 `REVIEW_052_054.md`：052 周偏移与金额精度，053/054 GT 排序冲突，054 预算日期和周范围依据、两列预算选择矛盾、阈值等号及互斥规则未触发。保留源业务口径供初步 interact 诊断；未修改共享 evaluator、runner 或 simulator。

抽样计划见 interact_plan_052_054.json：各题种子为 20261007052/053/054；pandas 后分别抽得 Polars/Ibis、Polars/PySpark、Ibis/Polars。Codex gpt-6-astra/low、interact、1800 秒上限；配置显式指向当前 worktree，镜像固定为上述 ID。九组 r001 均完成生成和正式评估，7 通过、2 失败；问题不自动修改为通过。本轮未提交或推送。

| Case | Backend | 正式评估 | 输出行数 | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- | --- |
| 052 | pandas | 通过 | 22 | 2 | 360.61 秒 |
| 052 | polars | 通过 | 22 | 2 | 189.72 秒 |
| 052 | ibis | 通过 | 22 | 2 | 159.46 秒 |
| 053 | pandas | 通过 | 13 | 2 | 142.52 秒 |
| 053 | polars | 失败 | 13 | 1 | 175.70 秒 |
| 053 | pyspark | 通过 | 13 | 2 | 201.91 秒 |
| 054 | pandas | 失败 | 6 / 6 | 2 | 148.80 秒 |
| 054 | ibis | 通过 | 5 / 6 | 2 | 339.17 秒 |
| 054 | polars | 通过 | 5 / 6 | 2 | 181.62 秒 |

052 三后端均获得周日周号、同年 Week - 1 关联、缺失周排除、两位金额和周标签的澄清并通过。053 pandas/PySpark 通过；Polars 只问了工资和在职口径，输出 Month 保留 Feb-2019，正式 TYPE_ERROR。临时额外接受 %b-%Y 后冻结输出通过，其他数值正确，但未将该格式写入正式配置，留人工判断。054 pandas 预算表多出 bar/Week 1，正式 ROW_COUNT_MISMATCH；问答未获得隐藏的 Week 5–8 范围，也未追问互斥逻辑。临时副本只过滤 Week 5–8 后两表通过。Polars/Ibis 主动追问预算范围或两个输出关系，获得范围与互斥规则后正式通过。

完整运行摘要、私有资产哈希和问答见 interact_validation_052_054.json；诊断见 diagnostics_052_054.json，未覆盖正式候选或报告。人工复核清单已补充以上两次失败归因和可选处理。输入与 GT 的源哈希再次核对一致。共享代码未改，未新增通用测试或重复运行已有单元测试；本轮验证针对任务资产与真实模型运行。


## 2026-10-07：051 导入与三后端 interact 验证

来源为相邻 prepbench 仓库的 data/case_051、reference/solutions/case_051/solution.py、src/evaluate/gt/case_051/。源文件路径及 SHA-256 记录于 import_case_051.json；源目录只读，输入与 GT 逐字节保留。新增标准 case 目录及 sports metadata（1 张输入表、10 列）。

迁移删除原始 query 的 Tableau/Prep 软件版本背景，保留 Standard Competition 与 Modified Competition 的 10/9/9/8 示例；将错误的“three statistics per rank”改为“four statistics per venue”。完整需求改用 supplied dataset，不新增对赛事/对手的筛选。明确 HTf/HTa 的 '-' 和空字段表示缺失，并在 KB 的原有过滤条目补充 intent，不改变歧义条目数量。所有场次先过滤再全局排名，随后按 Venue 汇总。

原 reference 硬编码了十个场馆的分类顺序，该顺序无题面依据，删除固定列表和相关排序，保留计算逻辑；main 入口改为从 case 根目录读 inputs、写忽略的 output/。评估以 Venue 为 key，场次及 best/worst rank 为 integer，Venue 为 text_exact/null_values=[]；Avg. Rank 使用 number、abs_tol=5e-10、rel_tol=0，依据源 GT 九位小数的半个末位单位接受未舍入均值，不沿用旧 2% 相对容差。该规则衡量数值精度，不强制候选执行九位舍入。行序不评分，GT 原有行序不修改。

验证：固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921 中 reference 复现源 GT。另用 Python 标准库按 rank=1+分差严格更大的比赛数独立计算，验证 105 场输入排除 2 场，103 场汇总为 10 个场馆，25 组分差存在并列。用 Fraction 精确核对全部均值，GT 在九位精度内一致。11 个定向检查全部符合预期：乱序与未舍入精确均值允许；重复行、场次/最佳/最差排名加 1、均值偏差 1e-9、场馆尾空格、dense rank、场馆内部排名和反向排名均拒绝。详细记录见 validation_case_051.json。

seed=20261007051，从 polars/ibis/pyspark 抽到 Polars/Ibis，加 pandas。Codex gpt-6-astra/low、interact、上述固定镜像、1800 秒上限，Codex/simulator 配置显式使用当前 worktree 路径。三组均为 r001，generation 完成、正式 evaluation 通过，均输出 10 行；详情见 interact_validation_051.json 及各自 runs/。所有 agent 均澄清了全局排名和半场缺失过滤。pandas 未询问均值九位精度，但在容差内通过；Polars/Ibis 收到九位精度回答。simulator 对 Polars 回答无顺序要求，对 Ibis 却额外要求 Venue 升序；这是无充分题面依据的回答差异，未将排序新增为评分项，也未将三后端通过解释为 simulator 完全一致。

本轮未修改公共 evaluator 或 runner，未修改 NOTES.md，未提交 case_051。既有 001–050 提交及未提交日志改动保留。运行记录与来源快照不作为任务运行依赖。

## 2026-10-07：029 资产审核及三后端 interact

仅修改 evaluation/config.json：客户表 key 为 Name，套餐表 key 为 Subscription Package，年费、套餐编号、价格均为精确 integer；Name 用 text_exact 对象、null_values=[]。Product 最终保留原字符串 text_exact 规则，比较时清理首尾空格且保留大小写。query、query_full、KB、reference、GT、输入均未修改。旧配置保存为 case_029_initial_config.json。

独立重算：11 条订阅、10 个姓名，Eve 的两条相同订阅均保留并累加；非 Mystery 套餐 1–6 的年度订单数分别为 17/8/28/16/72/56，总计 197，加权价格总额 4245，均价 21.548223350253807，floor 后 Mystery 价格为 21。两张 GT 金额全部一致；固定镜像 reference 重算、自评和逐字段扰动检查通过。Product 输入 `Active ` 带尾部空格，reference strip 后 GT 为 `Active`；query_full 未要求 trim，且描述保持原套餐表。当前输入没有未知频率、缺失非 Mystery 价格或总权重为零等情况，这些默认分支未被覆盖。

Codex gpt-6-astra/low、interact、1800 秒上限、主工作树 Codex 配置及当前 simulator 设置，固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921。seed 2026100729 抽得 polars/ibis，加 pandas；各当前 worktree r001。

| Backend | 最终配置正式重评 | 输出行数（客户/套餐） | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- |
| pandas | 两表通过 | 10 / 7 | 1 | 157.92 秒 |
| Polars | 两表通过 | 10 / 7 | 1 | 124.63 秒 |
| Ibis | 两表通过 | 10 / 7 | 1 | 111.41 秒 |

三组均获得年度频次加权、排除 Mystery、保留重复订阅并按姓名汇总、Mystery 先 floor 再算年费的澄清。所有金额与 GT 精确相等。初始将 Product 也改成对象形式的严格比较，三组都仅因保留输入的 `Active ` 尾部空格而 VALUE_MISMATCH，客户表均通过。沿用用户此前 015 的 strip 比较偏好，撤回 Product 这一不必要的严格化，保持其原有比较语义；未改 query/input/GT 或候选。对三个冻结 CSV 使用正式 evaluate.py 重评，三者均通过，result.json/evaluation.json 已更新，头表采用此最终配置结果。

初始严格配置及失败报告另存 case_029_strict_product_baseline/；前后结果见 interact_validation_029.json。最终配置重新自评及 reference 检查通过，原错误扰动继续拒绝，Active 尾部空格通过而小写 active 拒绝，见 evaluation_checks_029_final.json。旧 Product 字符串规则还清理包围引号、使用旧空值别名，并非新增的仅 strip 专用规则；当前套餐标签没有这些边界，本轮不修改共享 evaluator。整数比较接受等价 5.0，不强制 CSV 的整数字面格式；行序未规定也未评分。没有生成或额度失败，未提交。

## 2026-10-07：023 Scent 改为无首尾空格并重新验证

按用户确认，query_full.md 将 Scent 的单个尾部空格要求改为 no leading or trailing whitespace；amb_kb.json 的 5_C2_scent_first_word 增加同义 intent；reference/solution.py 删除追加空格的语句。在固定镜像中重跑 reference 生成 GT，逐行核对 18 行仅 Scent 删除一个尾部空格，其余字段及行序完全相同。原始 query.md 和 evaluation/config.json 不变，仍以 text_exact 严格检查 Scent。旧资产与全量原文件哈希保存在 case_023_before_scent_trim/。

新 GT 自比通过，额外添加首部或尾部空格的反例均被拒绝；旧 GT 按新规则比较也被拒绝，未将旧候选修补成新规则下的通过结果。检查记录见 case_023_scent_trim_checks.json。

使用与 r001 相同的 pandas/Polars/PySpark 三后端，Codex gpt-6-astra/low、interact、1800 秒上限，固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921，Codex/simulator 配置显式指向当前 worktree。三组新建 r002，生成与正式评测全部完成并通过，每组输出 18 行，Scent 均无首尾空格。顶部 023 的三个通过现对应 r002；旧 r001 的代码、输出、问答、报告均保留，代表修改前契约下的结果。正式新报告汇总见 case_023_scent_trim_interact.json。

本轮仅修改上述四个任务资产文件并新增整理/运行记录；日期字面格式和行序的既有评测边界不变，未提交 Git。

## 2026-10-07：028 资产审核及三后端 interact

本轮仅修改 evaluation/config.json：key 从全字段改为 Employee/Observation Interval，两项观察数字为精确 integer，四个分类/身份字段为 text_exact、null_values=[]，特别保留 Manager Proximity 的字面 NA；datetime 格式保持原配置。旧配置为 case_028_initial_config.json。query、query_full、KB、reference、GT、输入均未修改。

输入有双层表头，剔除子表头后为 90 条记录，A/B/C 各 30 个唯一观察区间，基准时间分别为 09:00/10:15/13:00。独立按区间序号累加前序时长并重建分类，所有 GT 字段一致，总观察时长为 56/59/65 分钟。Interaction 和 Task Engagement 各行均恰好一个 X；经理距离命名列中 71 行单选、19 行无选，后者恰好对应第四个无标题列中的 X，reference 忽略该列并输出字面 NA。固定镜像 reference 重算、GT 自评通过，七字段错误扰动（含 NA 改为空值）均被拒绝，详见 evaluation_checks_028.json。

Codex gpt-6-astra/low、interact、1800 秒上限、主工作树 Codex 配置及当前 simulator 设置，固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921。seed 2026100728 抽得 pyspark/polars，加 pandas；均为当前 worktree r001。

| Backend | 正式评测 | 输出行数 | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- |
| pandas | 通过 | 90 | 1 | 228.52 秒 |
| PySpark | 通过 | 90 | 1 | 125.18 秒 |
| Polars | 通过 | 90 | 1 | 99.55 秒 |

三组均通过澄清获得基准日期 2019-08-16、忽略无标题距离列及缺失命名选项使用 NA 的规则。最终内容逐行按 Employee/Interval 核对完全一致，19 个字面 NA 均保留，时间字面格式也满足 DD/MM/YYYY HH:MM:SS。三者均按员工/区间排列，未满足完整需求的七字段展示排序；当前 evaluator 忽略行序，正式通过仅表示内容通过，原始 query 未规定展示顺序，暂不加排序处罚。报告及核对快照见 interact_validation_028.json，运行记录在各 case_028/runs/interact/codex_gpt-6-astra/<backend>/r001/。

未触发边界：多个 X 时 reference 取字段列表首项，但完整需求未写冲突优先级；无 Interaction/Task 选项的默认空字符串也未被输入覆盖。query_full/KB 的非数字 coercion 后转 int 实际会对 NaN 报错，并非有效缺失值容错规则；当前数字全为有效正整数，没有修改这一未触发规则。基准日期与 NA 标签不可仅从 query/input 推导，但本轮三后端均主动询问并得到一致答复。当前未发现必须改 GT 的业务冲突，未提交。

## 2026-10-07：022 统一窗口描述与平均值容差

按用户确认，仅调整两个任务资产点：query.md 的 Context 将 “using the 7 days before the current date” 改为 “using the current day and the previous six days”，与 Requirements 及 query_full 的包含当天窗口一致；evaluation/config.json 的 Moving Avg Sales 改为 abs_tol=0.005、rel_tol=0，接受未舍入但与 GT 相差不超过半分钱的均值。Sales 仍为零容差，其余任务资产不变。query_full 仍要求两位小数，当前评分不再强制验证该舍入行为。

使用新配置对 pandas/PySpark/Ibis r001 的冻结 CSV 只读离线检查，三者均通过，未覆盖原运行报告。此次未新跑 interact，因此不能将这些旧题面产物称为修改题面后的新生成验证。未提交 Git。

## 2026-10-07：027 资产审核及三后端 interact

本轮只修改 evaluation/config.json：key 从全字段改为 Store/Date，Running Total Sales 与 Daily Store Sales 使用精确 integer，Store 和 Pre / Post Valentines Day 为 text_exact、null_values=[]，日期解析格式保持原配置。旧配置保存为 case_027_initial_config.json。query、query_full、KB、reference、GT、输入均未修改。原始 Context 的 Table Calculations 背景不约束代码实现，暂不作文字清理。

输入为 Leeds/York 两家店、2019-02-01 至 2019-02-28，每店 28 行，Store/Date 唯一且销售值为整数。独立使用真实日期与整数累加核对全部 56 行 GT 一致：14 日为 Pre、15 日重置；Leeds Pre/Post 总额为 5074/2435，York 为 4960/1033。固定镜像 reference 重算和 GT 自评通过，五个字段的错误扰动均被拒绝，见 evaluation_checks_027.json。

Codex gpt-6-astra/low、interact、1800 秒上限，主工作树 ../dfArena/runners/configs/codex 配置及当前 simulator 设置，固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921。按 seed 2026100727 抽取 ibis/pyspark 加 pandas，各当前 worktree r001。

| Backend | 正式评测 | 输出行数 | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- |
| pandas | 通过 | 56 | 2 | 217.24 秒 |
| Ibis | 通过 | 56 | 1 | 115.49 秒 |
| PySpark | 通过 | 56 | 1 | 216.12 秒 |

三组均明确得到 Pre/Post 精确标签及情人节当天归 Pre 的回答。Ibis 澄清确认 Daily Store Sales 直接来自每行 Value，不额外按 Store/Date 聚合；执行中修正 read_csv 的 schema 参数使用，最终通过。三份输出按 Store/真实日期逐行核对，标签和两个整数指标全部精确匹配 GT，没有额度或生成失败。

覆盖限制：三份候选全部输出 ISO 日期，date evaluator 接受等价日期值，未评分 query_full 的 DD/MM/YYYY 字面格式。完整需求以 Store/period/Date 排序，pandas 满足，Ibis/PySpark 采用 Store/Date，因此展示顺序不满足该完整需求；当前正式 evaluator 忽略行序，不能将内容通过解释成全部完整需求通过。累计计算的日期顺序及分组重置均已通过精确内容核对。原始 query 未规定展示顺序，不在本轮新增排序处罚。当前输入无重复 Store/Date、非整数销售或跨年数据，不据此扩展规则。记录见 interact_validation_027.json，各正式报告与问答在 case_027/runs/interact/codex_gpt-6-astra/<backend>/r001/；未提交。

## 2026-10-07：021 按用户确认接受半分钱绝对误差

原始 query.md 未要求两位小数，query_full.md 要求平均值舍入两位（患者表明确 HALF_UP）；Polars 未在交互预算内获得该精度要求。按用户确认，本轮将两张输出表的 Avg Cost per Day 改为 abs_tol=0.005、rel_tol=0，评分接受未舍入但与 GT 相差不超过半分钱的结果。总费用和人数仍为精确 integer，其余字段、key、日期和顺序规则不变。此为评分口径调整，不宣称候选已经执行两位小数舍入或 HALF_UP；query_full 的舍入要求仍保留，严格舍入行为不再由当前评估验证。

正式 evaluate.py 对 pandas/Polars/PySpark r001 的冻结输出重评，三者两张表均通过，顶部 021 更新为当前容差下的结果。修改前配置及正式报告保存在 case_021_before_tolerance_update.json；新报告与边界检查见 case_021_tolerance_reevaluation.json。此前 evaluation_checks_021_023.json 和下文三题审核表保留零容差阶段的历史结果。

GT 自比通过；13 项定向检查符合预期：两个平均值分别在 ±0.005 边界通过，±0.0051 和 +0.01 被拒绝；三个整数列加 1 均拒绝。哈希确认 query、完整需求、KB、reference、inputs、GT、generation 记录及候选代码/输出未变。仅刷新评估报告，未重新生成，未提交 Git。

## 2026-10-07：021–023 原始题面 interact 与评估修订

沿用 020 流程，先保留 query/KB 运行 pandas 和两个抽样后端，再修改 config 对冻结输出正式重评。全部在当前 prepbench-curation worktree 执行，Codex 与 simulator 配置均显式使用当前目录的本地配置，不引用 main worktree。Codex gpt-6-astra/low，interact，1800 秒上限，固定镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`。各题 seed 为 20261007000 + case 编号，抽样计划见 interact_plan_021_023.json；九组均为各 backend 的 r001，未通过重试筛选结果。

| Case | Backend | 旧配置 | 新配置 | 输出行数 |
| --- | --- | --- | --- | --- |
| 021 | pandas | 通过 | 通过 | 139 / 21 |
| 021 | Polars | 通过 | 失败：未舍入平均费用 | 139 / 21 |
| 021 | PySpark | 通过 | 通过 | 139 / 21 |
| 022 | pandas | 通过 | 通过 | 365 |
| 022 | PySpark | 通过 | 通过 | 365 |
| 022 | Ibis | 通过 | 通过 | 365 |
| 023 | pandas | 通过 | 通过 | 18 |
| 023 | Polars | 通过 | 通过 | 18 |
| 023 | PySpark | 通过 | 通过 | 18 |

顶部 021–023 表采用新配置重评状态。旧 config、evaluation/result 报告及保护资产哈希分别保存于 case_021_before_evaluation_update.json、case_022_before_evaluation_update.json、case_023_before_evaluation_update.json。正式 scripts/evaluate.py 已刷新九组 evaluation/result；没有修改候选或重新 generation。

**021。** output_01 每个住院日期一行，以 Date in Hospital 对齐；output_02 每位患者一行，以 Patient Name 对齐，当前输入的 21 个患者姓名均唯一。总费用和人数为精确 integer，两个 Avg Cost per Day 为零容差 number，姓名为 text_exact/null_values=[]。Polars 的首个正式错误为日均费用 76.66666666666667 对 GT 76.67（VALUE_MISMATCH）；按姓名另作只读诊断，其患者表还有 14 个未舍入平均值，例如 Andy 86.9047619047619 对 86.9、Camiila 90.625 对 90.63。旧 2% 容差掩盖了这些差异。

Polars 两次将舍入和其他规则合并提问，均收到 refuse_too_broad；随后拆开提问时已超过三轮预算，没有收到舍入答案。因此这是交互中未取得需求、最终输出不满足完整契约的失败，不能称为忽略了已得到的正确舍入澄清。保持失败和问答记录，不放宽容差。pandas/PySpark 的两表数值均与 GT 精确一致。日均 HALF_EVEN 是 simulator 对 PySpark 给出的额外细化；完整需求明确两位小数，但其日均半值规则仍有文档覆盖限制，不能将库默认行为自动提升为统一契约。

**022。** 每个日期一条销售记录，以 Date 为 key；Sales、Moving Avg Sales 为零容差 number。首六行移动均值为空，保留空值序列化语义。独立 Decimal 重算 7 行窗口与 GT 一致，365 个日期连续。三后端全部通过。PySpark 额外检查窗口首尾相距六个日历日，当前连续数据无法区分这一实现与完整需求的七行窗口；通过不覆盖缺日期输入行为。

**023。** 每条输入销售记录对应一行，缺少独立记录 ID，保留全字段对齐及行重数，不擅自选偶然唯一的身份键。Value 为 integer，所有文本为显式 text_exact/null_values=[]，包括完整需求明确要求的 Scent 单个尾部空格。18 行 GT 无全行重复，三个候选均通过；反例验证重复行仍会被拒绝。simulator 对 pandas 额外要求按输入文件/行序保留，但完整需求中的 append 不足以单独证明这一展示顺序必须评分，因此不新增排序限制。

**验证及边界。** 最终配置下三份 reference 在固定镜像复现 GT，行数为 139/21、365、18；GT 自比通过。23 个定向检查符合预期：错误数值、重复行被拒绝；022 未满窗口填零或擦除有效均值被拒绝；023 删除 Scent 尾空格、改变 Notes 大小写被拒绝；逆序行及 ISO 等价日期被接受。公共 evaluator 单元测试 29/29 通过。详细正式报告与反例见 evaluation_checks_021_023.json。

日期继续采用与 020 一致的日期值评分；完整需求中的 DD/MM/YYYY 字面格式尚未评分，formats 并不限制只能输出该格式。本轮不单独将 022/023 日期改成精确文本。行序继续忽略；内容通过不代表全部操作或展示要求已经覆盖。哈希核对三题 query、query_full、KB、inputs、GT、reference、候选代码/输出和 generation 记录均未变。当前没有证据要求为取得通过而改 query，故本轮仅修订 evaluation 配置及记录，未提交 Git。

## 2026-10-07：026 资产审核及三后端 interact

query 和 query_full 删除源自 Tableau Prep 的禁止 typed calculations / copying formulas 操作限制，改为使用 DataFrame workflow 构建配料明细；业务要求、输入、KB、reference 和 GT 均未修改。原 query 的 Ingredient/Price 中间列名与最终输出字段不同，但允许重命名；拼写等非必要文字暂保留。旧 query、query_full、config 备份于 case_026_before_review/。

evaluation key 从全字段改为 Cocktails/Ingredient Position，位置为精确 integer，鸡尾酒及配料名为 text_exact 且 null_values=[]，原价 number 零容差，平均价 abs_tol=1e-9、rel_tol=0。这一平均价容差用于九位小数级比较，可接受未舍入均值与 GT 的微小差距，不严格验证九位舍入动作。GT 自评、固定镜像 reference 重算均通过，五个逐字段错误扰动均被拒绝（evaluation_checks_026.json）。独立使用 Decimal 重算全部 53 行指标与 GT 一致；输入为 13 款鸡尾酒、39 种配料，无空分段、无单款内重复配料，Cocktails/位置唯一。

Codex gpt-6-astra/low、interact、1800 秒上限，固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921，Codex 配置来自 ../dfArena/runners/configs/codex，simulator 沿用当前设置。抽样 seed 2026100726，从 polars/ibis/pyspark 抽到 ibis/pyspark，加 pandas；均为当前 worktree r001，使用上述修改后的资产。

| Backend | 正式评测 | 输出行数 | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- |
| pandas | 通过 | 53 | 1 | 85.22 秒 |
| Ibis | 通过 | 53 | 1 | 103.32 秒 |
| PySpark | 通过 | 53 | 2 | 187.44 秒 |

三组均获得位置从 1 开始、逗号拆分并 trim、按配料对整杯价格求均值（含 mocktail）、九位小数及排序的澄清。PySpark 首轮组合问题被要求拆开，第二轮取得完整回答；中间修正一次 wholetext 读取 API 使用，最终无生成/服务错误。按 key 只读逐行比较，三份候选原价及平均价均与 GT 精确相同，输出行序也与 GT 相同。详见 interact_validation_026.json 和各 runs/interact/codex_gpt-6-astra/<backend>/r001/。

覆盖限制：query_full 未显式写 trim，但 reference 执行且三组澄清均传达；排序由完整需求规定，当前 evaluator 忽略行序，本次只读核对不等于正式评分；按原始 cocktail 次序排序无法仅靠现有输出字段的常规 order_by 完整表达。同一鸡尾酒重复出现同配料时按出现次数加权的行为当前输入未覆盖。不为这些未触发问题扩改业务资产或 GT，本轮未提交。

## 2026-10-07：025 删除额外空 Fellow Artists 行规则

按用户确认，删除 query_full 中“所有斜杠分段非空时额外补一条空行”的句子，删除 KB 的 5_O2_fellow_artists_blank_row 条目，reference 删除 need_blank 和人工 _blank 列逻辑。主演片段精确匹配后置空、原始空分段以及无斜杠时输出空 Fellow Artists 的规则保留，query.md 和 evaluation/config.json 不变。

固定镜像 pandas 3.0.2 的 stack() 保留宽拆分表的 NaN 填充单元格，因此仅删人工补行仍输出 1747 行；reference 同步使用 stack().dropna() 排除这些非真实分段，保留实际空字符串。重算后 GT 为 1746 行。逐行多重集验证仅删除 Ben Howard 在 2013-07-29 的 `Ben Ho\u00adward / Michael Kiwanuka` 演出对应空 Fellow Artists 行，没有新增或更改任何其他行。

新 GT 自评通过；pandas r002 的原始冻结输出使用当前配置离线重评通过。报告另存 case_025_blank_rule_removal_reevaluation.json，旧资产及差异保存在 case_025_before_blank_rule_removal/。未修改候选，未覆盖 r002 原始失败报告，未新跑 interact；头表仍表示原运行时的正式结果，不把本次离线通过当作新资产下重新生成通过。KB 删除条目后未来 interact 的歧义数量由 10 减为 9，按现有公式问题预算由 25 减为 23；已有 r002 只使用 4 个问题，原交互记录保留。

## 2026-10-07：025 修复后 pandas interact r002

使用修订后的 query_full/KB/reference/GT，沿用 Codex gpt-6-astra/low、主工作树 Codex 配置、interact、1800 秒上限和固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921，新建 pandas r002。生成完成，耗时 131.33 秒（含 simulator 22.28 秒），2 次 ask 调用。正式评测失败：ROW_COUNT_MISMATCH，候选 1746 行、GT 1747 行；无服务或额度错误。

simulator 在第二轮准确给出四组标签优先级，候选正确实现大小写去重及优先级，并保留全部 23 条空坐标记录。按日期值与精确数值只读对齐后，无多余行，唯一缺失为 Ben Howard 在 2013-07-29、SummerStage, Central Park 的 `Ben Ho\u00adward / Michael Kiwanuka` 演出对应的空 Fellow Artists 行。软连字符使首段不能精确匹配 Artist；候选没有实现“所有分段非空时额外增加空行”的既有规则。本次提问围绕 self token，simulator 仅回答精确匹配置空，未传达独立的额外空行规则，不能称作 agent 收到该规则后仍实现错误。

候选仍输出 ISO 日期，当前日期语义评测接受，字面格式不评分。未修改候选或继续改业务资产；本次结果说明标签澄清修复有效，但不代表整体通过。正式结果及问答见 case_025/runs/interact/codex_gpt-6-astra/pandas/r002/，只读诊断见 case_025_pandas_r002_review.json。头表 025 pandas 的失败状态不变，最新运行是 r002；Ibis/PySpark 仍为修复前 r001。

## 2026-10-07：025 最小业务资产修复

按用户确认，reference 去重分组改为其他全部输出字段加 Concert 小写值，并使用 dropna=False 保留缺失坐标组。原有四组标签优先级不变，完整列入 query_full 和 KB；KB 的大小写分组引用同步新实现。query.md、输入、evaluation 配置及额外空 Fellow Artists 行规则未修改。

固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921 重算 GT：1730 → 1747 行。逐行 Counter 核对仅增加之前独立诊断中的 23 条空坐标记录、删除 6 条大小写重复记录，其他行完全相同；每条被删记录都有按既有优先级保留的大小写等价行，新 GT 无此类重复，GT 自评通过。旧 reference/GT 和精确差异保存在本地 case_025_before_asset_fix/。

使用新 GT 对三个 r001 冻结候选离线重评，pandas/PySpark 1746 行、Ibis 1753 行，均仍为 ROW_COUNT_MISMATCH。报告另存 case_025_asset_fix_reevaluation.json，不覆盖旧运行 result.json 或 evaluation.json；头表保留原运行结论。本次没有新跑 interact，旧候选不能用于证明修订后的澄清是否有效，也未修改候选来获取通过。

## 2026-10-07：024 删除无对应输出指标的问题

按用户确认，仅从 query.md 删除完整条目 `Who sent the longest message?`，使题面问题与现有六列发送者汇总输出一致；未删除或改写其他题面文字。query_full 无此句，reference、GT、evaluation 和输出契约均未修改。本次未重跑；上文头表及下文三后端 r001 仍属于删除前题面的历史结果。此前记录的最长单条消息题意缺口由本次删除解决。

本文件记录逐 case 的问题、证据、决定与后续验证；通用迁移和标注准则见 [NOTES.md](NOTES.md)。历史 manifest、validation 文件和 runs 是对应版本的快照，不代表当前资产状态。

## 2026-10-07：020 仅更新评估配置并重评

按用户要求，只修改 evaluation/config.json；三后端冻结输出在新规则下通过后，保留现有 query，不继续修改题面。output_01 按每人一行使用 Name 为 key，output_02 按每天一行使用 Date 为 key；Cost、Cost per Day、Number of Patients 改为显式 integer，两个已要求保留两位小数的平均值改为零容差 number，Name 改为 text_exact/null_values=[]。日期保留按日期值比较，行序继续忽略，不将 simulator 额外给出的排序要求纳入评分。

修改前配置、三个后端完整 evaluation/result 及保护资产哈希保存在 case_020_before_evaluation_update.json。使用正式 scripts/evaluate.py 对 pandas/Ibis/PySpark 的同一 r001 冻结输出重评，均完成且通过（9/33 行），各运行 evaluation/result 已刷新；没有新 generation。GT 自比通过；11 个定向检查符合预期：每个数值结果列的增量错误、非整数人数、重复行、姓名尾部空格均拒绝；ISO 等价日期、行序逆转、整数写成小数表示均接受，见 evaluation_checks_020.json。

哈希核对 query、query_full、KB、reference、inputs、GT、三个候选代码/输出及 generation 记录未变。interact_validation_020.json 保留旧配置的基线快照，不能当作新评估快照。日期字面格式与 scaffold 方法要求仍非当前表格评估覆盖范围，simulator 无依据排序回答仍保留为已知问题；本次通过不宣称解决这些问题。未提交 case 资产。

## 2026-10-07：020 补充 Ibis/PySpark interact 基线

保持 020 任务资产不变，以固定种子 20261007020 从 [polars, ibis, pyspark] 抽取两个不重复后端，结果为 Ibis、PySpark；与先前 pandas 使用相同 gpt-6-astra/low、当前 worktree 配置、固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921 和 1800 秒上限。两个后端各自在当前 worktree 新建 r001。Ibis 生成 157.00 秒、2 次澄清调用；PySpark 155.09 秒、3 次调用；均完成生成并通过正式评测（9/33 行）。按姓名和解析后日期另作精确比较，两表全部数值与 GT 相同。三后端公开资产哈希均与当前资产一致；结果及评估资产哈希快照见 interact_validation_020.json。未重新生成 pandas，未修改正式输出或任务资产。

两者均询问复查是否纳入，simulator 均排除复查；组合多个政策的问题被拒绝过宽后，agent 拆分追问。每人平均分母、每日 distinct Name 人数、仅输出有人住院的日期、平均值保留两位等通过 fallback 澄清。simulator 还向两个后端都要求按 Name/Date 升序，但两份 query 未规定排序；这与 reference 默认 groupby 排列相符，属于无题面依据的额外要求，不能据此新增排序评分。现有 KB 与排序回答的约束仍待审核。

Ibis 和 PySpark 均使用 scaffold，但把 Value 当零基 offset，再定义 DayIndex=Value+1；完整需求/reference 使用 Value>=1 且 DayIndex=Value。当前连续 scaffold 0–13 覆盖最长 13 天，两种算法生成相同结果，输出通过不能验证 scaffold 语义一致。Ibis 忽略 input_04；PySpark 硬编码其异常日期标签到三个价格 band 后读取价格，说明异常输入会诱导实现特例。Ibis 日期为 ISO，PySpark 日期为日/月/年；两者日期值正确，仍不把 evaluator 日期解析通过称为字面格式验证。三后端均通过只说明当前表结果正确，额外输入来源、输出契约、KB、key/字段规则和方法要求仍待审核；未提交 case 资产。

## 2026-10-07：020 修改前 pandas interact 基线

按用户要求，先运行现有资产观察效果，尚未修改 query、query_full、amb_kb、reference、GT 或 evaluation/config。运行目录为当前 prepbench-curation worktree 的 `PrepBench/case_020/runs/interact/codex_gpt-6-astra/pandas/r001`。使用 Codex gpt-6-astra/low、固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、interact/pandas、1800 秒上限。当前 worktree 原无 Codex 实际配置，本次从主工作树提取模型/provider 设置到当前 worktree 的 Git 忽略配置文件；执行时显式指定当前 worktree 的 Codex 与 simulator 配置绝对路径。

生成完成，正式评测通过：output_01 共 9 行，output_02 共 33 行。生成耗时 100.41 秒，1 次澄清调用含 3 个问题，simulator 耗时 16.71 秒。agent 询问首日与住院天数边界、出院后复查是否纳入、价格区间异常日期的解释。simulator 明确首日为第 1 天、只计住院而不含复查、按住院天序使用 100/80/75 阶梯价格；其中排除复查为 fallback 回答，现有 KB 没有直接对应条目。完整问答见运行 logs/interaction.jsonl。

独立核对候选数值与 GT：按姓名/解析后的日期对齐，两表所有数值精确相同，并非仅靠旧 number 容差通过。候选 Date 输出 ISO 日期，GT 为日/月/年；当前 evaluator 按日期值接受等价表示，query_full 的字面格式要求未被单独验证。候选用 Python 循环生成住院日，再以 pandas 聚合，未使用 input_02 scaffold；因此输出通过不代表满足题面的 scaffold 操作要求，也不能视为纯 pandas 向量化实现。input_03 复查范围与 input_04 异常区间的来源仍待追溯；现有 key、字段类型和澄清覆盖仍待审核。本轮仅一个后端的修改前基线，不构成三后端完整审核；未修改候选输出，未提交 case 资产。

## 2026-10-07：024–025 资产审核与 interact

024：一行代表发送者，key 改为 Name；Text、Number of Words、Text while at work 用精确 integer，两项舍入到一位的小数用零容差 number，Name 精确文本且 null_values=[]。72 条消息均解析成功，16 位发送者的全部 GT 指标经独立重算一致；无缺失日历匹配、首尾空白发送者或恰好处于工作时间边界的记录。原题“最长一条消息”没有对应最大值输出指标，当前表只给每人总词数和平均词数；不新增列或擅改业务，记录题意覆盖缺口。姓名含 Unicode 格式字符，不自动归一化。原题禁止 split，内容 evaluator 不检测实现方法。完整需求排序仍不评分。

025：一行代表演出及同台艺人条目，key 改为 Artist/Concert Date/Concert/Venue/Location/Fellow Artists，坐标和家乡字段作为结果比较；四个坐标字段零容差 number，文本精确且 null_values=[]，空同台艺人属于有效标签。旧配置分别保存为 case_024_initial_config.json、case_025_initial_config.json。两题 GT 自评、固定镜像 reference 重算均通过；17 个逐字段扰动全部被拒绝，见 evaluation_checks_024_025.json。

025 存在业务资产冲突，暂保留 baseline：query/query_full 要求保留坐标未匹配演出，但 reference 的 groupby 默认 dropna=True，丢掉 15 条原始演出的 23 条展开结果，GT 仅 1730 行。临时诊断副本只增加 dropna=False 后为 1753 行；未覆盖正式 reference/GT。另有大小写去重缺陷：reference 只有在整个非 Concert 分组的 Concert 全部小写后相同时才去重；混有其他 Concert 时，不会对子组去重，GT 中仍可同时保留 RED Tour/Red Tour/RED tour 等。完整需求所谓固定偏好顺序未列举，KB 也用省略号，只有 reference 给出了四组具体偏好；不把该硬编码自动当作获批业务规范。地点/姓名清理与完整需求的严格匹配表述也存在潜在冲突，但当前输入相关列没有首尾空白/不可见字符；Concert 内软连字符保留在 GT 中。

本轮使用 Codex gpt-6-astra/low、固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、主工作树 Codex 配置、当前 simulator 设置，interact 上限 1800 秒。按 2026100700+case 编号抽样，024 与 025 都为 pandas/Ibis/PySpark，顺序生成 r001。六组均完成生成和正式评测，没有额度或服务失败；未修改 query、query_full、KB、reference、GT 或候选。025 的业务资产冲突保留待决。共享 evaluator 单元测试 29/29 通过。

| Case | Backend | Run | 正式评测 | 输出行数 | ask_calls | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- | --- | --- |
| 024 | pandas | r001 | 通过 | 16 | 4 | 207.74 秒 |
| 024 | Ibis | r001 | 失败：VALUE_MISMATCH | 16 | 1 | 425.37 秒 |
| 024 | PySpark | r001 | 失败：VALUE_MISMATCH | 16 | 2 | 217.20 秒 |
| 025 | pandas | r001 | 失败：ROW_COUNT_MISMATCH | 1746 | 2 | 100.44 秒 |
| 025 | Ibis | r001 | 失败：ROW_COUNT_MISMATCH | 1753 | 2 | 227.68 秒 |
| 025 | PySpark | r001 | 失败：ROW_COUNT_MISMATCH | 1746 | 2 | 164.55 秒 |

024 pandas 全部指标通过；第 4 次 ask 为额度用尽后的请求，不是第 4 轮有效澄清。Ibis 仅按日号关联跨 May/June/July 的日历，使每条消息重复三次；其所谓 spaces 实为清洗字符串长度减空格数量，计算的是非空格字符数，再加一，导致词数与平均值也错误。PySpark 使用 `d MMM`，将 June 转成 Jun 而不能匹配日历完整月份，漏掉 Sam 在 2019-06-24 15:30:30 的工作消息：Text while at work 为 3 而非 4，比例为 23.1 而非 30.8，其余输出值一致。两者均为候选实现错误，不修改资产或放宽配置。

025 三组均保留 23 条空坐标记录，符合 query 的 left join 要求，却与旧 GT 冲突。只读按日期值及数值归一化后的全行差异：pandas/PySpark 各 GT-only 8、candidate-only 24；Ibis 为 1、24。三者均漏掉 `Ben Ho\u00adward / Michael Kiwanuka` 对应的空 Fellow Artists 行：软连字符使该片段不能精确匹配 Ben Howard，query_full 要求所有片段非空时另加空行，但候选均未实现该步骤，交互回答也未主动传达这一细节。candidate-only 均包含 23 条空坐标行；剩余一条为 `Divide Tour`。pandas/PySpark 用它替代 GT 的 `Divide tour`，Ibis 则两者均保留。

大小写去重须区分资产缺陷和候选行为：GT 本身多留 6 条应按 case-insensitive 规则合并的记录；pandas/PySpark 完成了这些合并，但选择标签分别用首条和字典序。pandas 明确追问固定优先级时，simulator 答复业务未给出顺序、采用 keep_first，与 reference 硬编码不一致；PySpark 自选字典序也不等同于澄清中的 keep_first。Ibis 只被告知全字段精确去重，未获得大小写合并规则，候选也没有实现。因此不能把当前正式失败简单当作后端能力结论。

三组 Concert Date 均为 ISO 日期；共享 date evaluator 本来就接受 ISO，故此是 query_full 字面格式要求未评分，不是本次正式失败原因。025 原始 Context 仍有 live session、Workout Wednesday、挑战耗时等不影响计算的背景，可后续精简；本轮未改。024 原题最长单条消息没有相应指标、025 额外空同行与大小写标签偏好等规则仍需明确是否保留，再同步完整需求、KB、reference 与 GT。仅修 dropna 后的 1753 行不是最终修复 GT（仍含大小写重复）。

证据保存在各 case 的 `runs/interact/codex_gpt-6-astra/{pandas,ibis,pyspark}/r001/`，正式状态以 result.json 和 detail/evaluation.json 为准；只读差异与耗时快照为 `interact_validation_024_025.json`。配置收紧可保留，但 025 在修复业务资产之前不能作为已验收 case。没有提交 runs、配置凭证或本轮资产。

## 2026-10-07：019 完整需求明确 Gap 实际格式

按用户要求，将 query_full.md 中泛指的 signed duration 改为实际输入格式：正号开头、两位时分秒，秒单位为两个单引号，并写明总秒数公式 HH * 3600 + MM * 60 + SS；原有独立 `-` 表示零差距的规则保留。与现有 KB/reference 一致，未修改计算口径、输入、GT 或 evaluation。本次未重跑，既有运行属于修改前完整需求版本。

## 2026-10-07：018 原始题面明确 HALF_UP

按用户要求，在 query.md 添加简短规则 `Use round-half-up for all rounding.`，并将 Max Rating 的两位小数要求同步到原始题面，与既有 query_full 保持一致。evaluation 暂保留上一轮用户指定的绝对容差（Avg Rating 0.01、Avg Viewers 1）；本次未恢复零容差、未重跑。此前三后端的运行与重评记录属于修改前题面，不能视为新题面的生成验证。

## 2026-10-07：018 放宽绝对容差并重评冻结输出

按用户要求，Avg Rating 改为 number、abs_tol=0.01、rel_tol=0；Avg Viewers 从精确 integer 改为 number、abs_tol=1、rel_tol=0。Max Rating 仍为零容差，其余配置保持不变。修改前配置及三个后端的正式报告保存在 case_018_before_abs_tol_evaluation.json。

使用正式 evaluate.py 重评 pandas/PySpark/Polars interact r001 的同一批冻结 CSV，三者均完成且通过，各 77 行；各运行的 evaluation/result 与头表已更新。本次没有重新生成，也没有修改 query、query_full、KB、reference、GT 或候选。原始运行快照 interact_validation_017_019.json 与原定向检查 evaluation_checks_017_019.json 保留原评测版本，不代表本次配置。

本次通过表示容差接受 pandas 三处观众数少 1 和 PySpark 一处平均评分少 0.01，不表示候选实现了严格 HALF_UP。完整需求及 KB 仍要求 HALF_UP；当前评测接受上述数值误差，且 Avg Viewers 的 number 规则不再强制整数输出。此为本次容差调整的明确限制。

## 2026-10-07：016 pandas 删除工具缺失记录并重跑

按用户要求，删除原 pandas r001/r002 两个 generation=missing_output、evaluation=skipped 的运行目录；以相同 Codex gpt-6-astra/low、固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、主工作树 Codex 配置和 interact 模式重跑，重新使用 r001。此次 shell/文件执行及 clarification 工具可用，1 次澄清调用后完成生成，耗时 73.76 秒；输出 72 行，正式评测通过（行序仍忽略）。头表已更新为通过，未修改题面、输入、GT 或评测配置。下方 2026-10-05 的工具缺失记录仅为历史说明，原 pandas 两个目录已删除。

## 2026-10-07：019 Ibis 删除额度中断记录并重跑

按用户要求核查 017–019 九次运行，仅 019 Ibis 因模型服务 403 额度不足而中断，其他八次均完成生成。删除该中断运行的 runs/interact/codex_gpt-6-astra/ibis/r001 目录，以相同模型 gpt-6-astra/low、固定镜像、Codex 配置和 interact 模式重新生成 r001。新运行生成完成，正式评测通过，输出两行与 GT 字节一致：TEAM SKY=96、MOVISTAR TEAM=97，各 7 名骑手；ask_calls=1，生成耗时 120.40 秒。头表和 interact_validation_017_019.json 已更新为新 r001。下方 2026-10-06 的额度中断描述仅保留历史说明，不再代表当前状态。

## 2026-10-06：017–019 配置审核与新 interact（已结束，019 Ibis 因额度中断）

017 清理后的 query 公开 Voting System 标签 FPTP/AV/Borda，与完整需求一致；配置以 Voting System 为 key，两列精确文本。018 完整需求和 KB 补明拆分 genre 后去除首尾空白，与 reference 现有行为一致；配置以 Genre/Type 为 key，Avg Viewers 为精确 integer，两项评分为零容差 number，文本精确比较。019 配置以 Team 为 key，平均差距与人数均为精确 integer；保留忽略行序，不将完整需求中的展示排序自动升级为原始请求的评分要求。旧配置分别保存在 case_017/018/019_initial_config.json。三题 GT 自评、固定镜像 reference 重算均通过；11 项逐字段扰动反例全部被拒绝，见 evaluation_checks_017_019.json。

原始数据检查：017 共 11 张完整选票，首轮 A=5/B=2/C=4，实际不触发并列或零票候选；reference 的 AV 计数未补齐零票候选，属于潜在实现覆盖缺口，当前数据不受影响。018 有 6,638 个拆分项需要去除首尾空白；77 个组的最高评分均无并列，代表作品 tie-break 未被本数据覆盖。使用 Fraction 精确重算两项平均数，所有 GT 均符合 HALF_UP，含 5 个半值边界。019 的 145 行 Gap 均可解析；入选 TEAM SKY=96、MOVISTAR TEAM=97（各 7 人），未取整平均分别约 96.592857、97.280952 分钟；实际没有 100–101 分钟的边界组，先 floor 再筛选与先筛选的差异未被覆盖。完整需求所称 signed duration 超出 reference 仅解析正号格式的范围，但当前输入无负数。

新 interact 使用 Codex gpt-6-astra/low、固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、主工作树 Codex 配置，每次上限 1800 秒；按种子 2026100600+case 编号抽样：017 pandas/PySpark/Ibis，018 pandas/PySpark/Polars，019 pandas/PySpark/Ibis。新运行在当前 worktree，新建 r001；017 旧主工作树 r001 保留。结果快照见 interact_validation_017_019.json。017 Polars 头表仍保留清理前主工作树记录，其余本轮结果均来自当前 worktree。


| Case | Backend | 正式结果 | 输出行数 | ask_calls | 生成耗时（秒） |
| --- | --- | --- | --- | --- | --- |
| 017 | pandas | 通过 | 3 | 1 | 193.66 |
| 017 | pyspark | 通过 | 3 | 1 | 106.69 |
| 017 | ibis | 通过 | 3 | 2 | 166.84 |
| 018 | pandas | 失败 | 77 | 1 | 133.47 |
| 018 | pyspark | 失败 | 77 | 1 | 210.96 |
| 018 | polars | 通过 | 77 | 1 | 286.85 |
| 019 | pandas | 通过 | 2 | 1 | 162.42 |
| 019 | pyspark | 失败 | 2 | 1 | 173.26 |
| 019 | ibis | 跳过 | — | 1 | 140.35 |

017 三个新后端均得到 FPTP=A、AV=C、Borda=B。Ibis 在提问中错误声称 A/C 的 Borda 分数并列；simulator 第一轮说没有定义 FPTP/Borda 并列规则，第二轮却补出按字母选 A 的规则。实际分数 A=21、B=23、C=22；最终程序按数据计算，未受错误澄清影响。输出通过不代表 simulator 一致性通过；保留问答作为待改进证据，不据此添加无依据的并列规则。

018 pandas 的 77 行中仅三项 Avg Viewers 错误：Music/Movie 29130 对 GT 29131、Slice of Life/Movie 78558 对 78559、Vampire/Movie 58372 对 58373。代码使用 pandas 默认半偶 round，未澄清 HALF_UP。PySpark 也输出 77 行，但只有 Mecha/Movie Avg Rating 为 7.73 对 7.74；代码先用 double 求均值，再 format_string("%.2f")，精确均值为 7.735，浮点聚合与格式化路径未实现要求的精确半值舍入。不是三处观众数错误。Polars 77 行全部通过。不得放宽容差掩盖 0.01 或 1 的真实舍入差异。

019 pandas 两行通过；PySpark 两行中 MOVISTAR TEAM 平均差距为 96 对 GT 97，人数均正确。其秒数正则要求数字后跟双引号，而输入秒单位是两个单引号，匹配失败后补 0，漏掉全部秒数。Ibis 因模型服务返回 403 额度不足而 generation failed、evaluation skipped，未形成可评测 CSV，属于服务阻塞而非 agent 业务失败。额度恢复后可新建 r002 补验；本轮未反复重试。

## 2026-10-06：006 中止重跑与 010 pandas 复验

用户指出 006 已审核，无需重复，本轮启动的当前 worktree pandas r001 已停止；generation 未成功、evaluation skipped，不计作 agent 业务失败，不替换历史头表。010 pandas r001 已启动后用户转向 017–019，保留该次运行，不追加其他后端；当前 worktree pandas r001 已完成生成且正式评测通过，头表更新为通过，历史失败记录保留。

## 2026-10-06：013 评测配置修订与冻结输出重评

按用户确认，仅修改 evaluation/config.json：三张表的 key 从全字段改为 Account/Name/Date，表示客户及周期起始日；Account、Name 使用对象形式 text_exact 且 null_values=[]，保留编号前导零与文本空白；天数统计、Month/Quarter/Week 和已取整的平均交易额使用精确 integer；平均余额使用零容差 number，按题目要求比较舍入两位后的结果。日期解析规则和忽略行序行为保留。

原始配置和三组 result/evaluation 归档至 case_013_initial_evaluation.json。使用正式 evaluate.py 重评现有 pandas/Ibis/Polars interact r001 冻结输出：Ibis、Polars 三张表均通过；pandas 月度 18 行、季度 6 行通过，周度仍为 78 行对 GT 81 行，正式失败 ROW_COUNT_MISMATCH，未进入周表内容比较。失败原因仍见下文周分组诊断。各 run 的 evaluation/result 与头表已更新；本次未重新生成，未修改 query、KB、reference、GT 或候选。

验证：GT 自评通过。三张表逐字段构造反例：账户加前导零、姓名增加尾部空格、日期增加一天、平均余额增加 0.01、其余数值增加 1 均被拒绝；三表分别改为 ISO 日期并逆序输出均通过。共 27 项定向检查符合预期，记录见 evaluation_checks_013.json。

## 2026-10-06：011 评测配置修订与冻结输出重评

按用户确认，仅修改 evaluation/config.json：业务 key 从 Date/volume/Row 改为 Row；Row、volume 使用精确 integer；high、low、adjclose、close、open 使用 `number, abs_tol=1e-9, rel_tol=0`。价格是输入数值透视结果，GT 保存九位小数；该容差接受既有候选与 GT 最大 4.84e-10 的序列化差异，取代旧约 2% 的相对容差。Date 规则及忽略行序的行为保持原样。

原始配置和三组 result/evaluation 归档至 case_011_initial_evaluation.json。使用正式 evaluate.py 对现有 pandas/Ibis/PySpark interact r001 冻结输出重评，三组均完成且通过；各 run 的 evaluation/result 和头表已更新，未重新运行 interact，未修改 query、KB、reference、GT 或候选。时区、精度和排序的 simulator 回答不一致仍是后续澄清资产审核事项，本次重评不能验证或消除该问题。

验证：GT 自评通过；五个价格字段分别增加 5e-10 通过、增加 2e-9 失败；volume 增加 1、Row 增加 10000 或 0.5、Date 增加一秒均失败；逆序输出通过。15 项定向检查符合预期，记录见 evaluation_checks_011.json。

## 2026-10-06：017 删除无关操作说明与调侃

按用户确认，从 query.md 和 query_full.md 同步删除下载指令、Twitter 宣传、Prep 计票及手动筛选操作、flow 加分项；从 query.md 删除 Bounty 不如 Aero/Crunchie 的口味调侃。这句话不定义投票偏好、权重或并列规则。保留 ABC 偏好解释、巧克力候选映射和全部投票计算规则；完整题面中清理后无实质内容的 Notes 标题一并删除。KB、输入、reference、GT、评测配置未改。已检查删除项不存在及业务说明保留。本次未新跑 interact；下文 2026-10-05 的通过记录属于清理前题面，位于主工作树 ../dfArena/PrepBench/case_017/runs/，不作为修改后题面的复验记录。

## 2026-10-06：014 金额容差调整为 0.01 并重评

按用户后续要求，将四个金额字段统一调整为 `type=number, abs_tol=0.01, rel_tol=0`，取代下文的 0.005 配置；精确键匹配规则不变。使用正式 `evaluate.py` 对同一批 pandas、Polars、Ibis interact r001 冻结输出重评，三组均完成且通过，evaluation/result 和头表已更新。该容差接受本次输出与 GT 相差一分钱的结果；通过不表示下文记录的舍入口径冲突或 pandas 中间精度误差已修复。本次没有重新生成候选，也没有修改题面、KB、reference 或 GT。

## 2026-10-06：014 金额容差统一为 0.005 并重评

按用户确认，将四个金额字段（Total Ticket Price、Ticket Price Variance to Meal Deal Earnings、Total Meal Deal Earnings、Total Excess）统一为 `type=number, abs_tol=0.005, rel_tol=0`；TicketID/MemberID 的精确匹配规则保留。此配置取代下文首次收紧时的 `1e-8`、零容差和套餐收入 integer 规则。使用正式 `evaluate.py` 对原有三个 interact r001 的冻结输出重评，更新各 run 的 evaluation/result：pandas、Ibis 均为 `VALUE_MISMATCH`，Polars 通过，头表状态不变。原价和套餐收入均一致；pandas/Ibis 的 Excess 及收入差额仍分别有 444/445 张票据相差 0.01，超过新容差。舍入口径冲突及 pandas 的 3 张中间精度误差仍按下文诊断解释，不将重评失败直接视为后端能力错误。

验证：GT 自评通过；四个金额字段分别增加 0.004 均通过，分别增加 0.006、0.01 均失败，共 12 项扰动检查通过。本次仅修改金额容差并重评，没有重新生成候选，也没有修改题面、KB、reference 或 GT。

## 2026-10-06：014 工具措辞清理、interact 与金额容差收紧

**状态：三后端运行及重评完成；舍入口径待决定。** 014 才是含“2019.1 / Rows to Columns”提示的任务。删除 `query.md`、`query_full.md` 中的四处版本/软件操作提示；完整需求已经明确按 TicketID、MemberID、Type 汇总数量和金额，保留业务要求及原有澄清歧义。未修改 KB、reference 或 GT。固定种子 2026100614，从 `[polars, ibis, pyspark]` 抽得 Polars/Ibis，加 pandas；Codex `gpt-6-astra`/low，镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`，单次上限 1800 秒，顺序运行，配置显式使用 `../dfArena/runners/configs/codex`。三组 interact r001 均生成 20,278 行，原始旧配置下全部通过；耗时 pandas 76.94 秒、Polars 113.79 秒、Ibis 128.30 秒，澄清调用分别 1/2/1 次。PySpark 未运行。

用户确认金额旧容差过宽后，配置保留业务 key `TicketID/MemberID`，将 TicketID 改为精确文本，MemberID 和套餐收入改为精确 integer；Total Excess 是明确舍入后的分值，使用零容差 number；原价与收入差额使用 `abs_tol=1e-8, rel_tol=0`，仅容纳浮点求和/相减噪声。旧字符串 number 的约 2% 相对容差（零值附近绝对差小于 0.02）不再使用。对同一批冻结 CSV 重评，pandas/Ibis 为 VALUE_MISMATCH，Polars 通过；头表采用这次新配置重评状态。原始配置和三组原始 result/evaluation 完整归档在 `case_014_initial_evaluation.json`，各 run 的 generation 和候选未改，result/evaluation 已由正式 evaluate.py 更新。

只读核对：三组候选的票据键与 GT 一致。pandas 的 Total Excess 和差额在 444 张票据上差 0.01，Ibis 的 Total Excess 在 445 张票据上差 0.01；Polars 的 Total Excess 全部相同，其他金额最大差为 8e-15。固定镜像重算 reference 也在 444 张票据的 excess/差额上与 GT 差 0.01，原价和套餐收入一致。例如 TicketID 100121、MemberID 0，未舍入 excess 为 3.125，reference HALF_UP 得 3.13，GT 为 3.12。pandas/Ibis 的 simulator 回答明确要求 HALF_UP；Polars 仅被告知总额舍入两位，使用默认 round(2)。完整需求没有明确半分边界，KB 的 ref 使用 pandas round，而 reference 使用 HALF_UP，资产口径存在冲突。因此新配置下的失败不能简单归为 agent 计算错误，也不能为通过而恢复宽容差；下一步需决定舍入规则，再同步完整需求、KB、reference/GT 并新建 generation。

进一步以原始价格字符串构造 Fraction、全量精确重算 20,278 张票据：Ibis 全部符合精确 HALF_UP；pandas 有 3 张不符合 HALF_UP，128514/321965 的精确 excess 为 8.625，却输出 8.62，328839 的精确 excess 为 7.375，却输出 7.37。原因是先用 50 位 Decimal 算循环小数均价，再相乘求和，得到略低于半分边界的值，最终 HALF_UP 向下舍入。GT 与精确 HALF_UP 相差 445 张，与精确 HALF_EVEN 也相差 4 张：100050 的 19.225 输出 19.23，118737/207808 的 4.975 输出 4.97，119243 的 24.675 输出 24.67。因此 GT 不能视为严格的精确 HALF_EVEN 标准，Polars 与现有 GT 一致也不代表已解决数值口径。主要失败来源仍是资产/澄清的舍入规则冲突，pandas 的 3 张中间精度误差应单独记录。

验证：GT 自评通过；原价加 1e-9 的等价浮点扰动通过；原价、Total Excess、收入差额各加 0.01 的反例均失败；套餐收入加 1、MemberID 加 1 均失败。当前忽略行序，任务没有排序要求。证据在 `case_014/runs/interact/codex_gpt-6-astra/{pandas,polars,ibis}/r001/` 的阶段记录、候选及问答日志。

## 2026-10-06：013 三后端 interact

固定抽样种子 20261006，从 `[polars, ibis, pyspark]` 抽得 Ibis/Polars，加 pandas；使用 Codex `gpt-6-astra`/low、同一镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`，单次上限 1800 秒，顺序运行。通过 `--codex-config-dir ../dfArena/runners/configs/codex` 使用主仓库本地配置，未复制配置到本分支。三组 r001 均完成生成和评测；Ibis、Polars 三表通过，分别输出 18/6/81 行；pandas 月度、季度通过，周度仅 78 行，正式失败为 `ROW_COUNT_MISMATCH`（GT 81 行）。PySpark 未运行。

pandas 获得自定义周规则的澄清后，仍用 `Date > first_sunday` 判断边界，并以元旦为基准计算 `Week`，再仅按账户、姓名、周号分组，导致 1 月 1–12 日合并为 Week 1，后续周号少 1，每个账户少一个周组。记录为澄清后的周规则实现错误，保留原始失败，不修改 query、KB、reference、GT 或评测配置。三组 ISO 日期均可按当前 date 规则解析；日期字面格式和行序不由本次通过结论保证。证据位于 `case_013/runs/interact/codex_gpt-6-astra/{pandas,ibis,polars}/r001/` 的 `result.json`、`detail/evaluation.json`、`workspace/solution.py` 和 `logs/interaction.jsonl`。

## 2026-10-05：012 资产审核与 interact

012 原先无迁移或正式运行记录。每行是一个保留的停机事件；按 System、Error Source、开始与结束时间对齐。公开输出约定补全来源标签、小时与占比精度、日期展示格式，并明确占比是 0–1 的比例。完整需求补充 reference 已执行的 `Planed Outage` 到 `Planned Outage` 规范化，KB 添加对应依据。配置用事件身份作为 key，列规则改为显式对象形式。固定 Docker 镜像重算 reference 与 GT 自评通过，错误时长反例失败。抽样种子 2026100512，除 pandas 外选 Polars/Ibis；Codex `gpt-6-astra`/low 的三次 interact r001 均生成 11 行并正式通过，simulator 问答也与完整需求一致。PySpark 未运行。完整需求提到先保留自动行、再按时间倒序附加手工行；当前配置忽略行序，因此通过仅覆盖内容。

## 2026-10-05：015–016 资产审核与 interact

按 `NOTES.md` 审核 query、澄清 KB、reference、GT 和配置。固定镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`，Codex `gpt-6-astra`/low，单次上限 1800 秒。抽样种子 20261005：015 为 pandas/Ibis/PySpark，016 为 pandas/Ibis/Polars。两题 reference 重算后均通过当前 evaluator；GT 自评也通过。

- **015**：每行是一笔保留的交易，按 Region/Customer ID/Order Date/Stock 对齐；百分比及金额用零容差 `number`，Customer ID 用 `integer`。GT 的百分比为 9 位小数，故 `query_full`、澄清 intent 和 reference 统一为 9 位。输入 Stock 有少数尾部空格，GT 对其中部分行去掉了空格；暂沿用旧 `text_exact` 的首尾空白兼容行为，此项不能解释为字面 Stock 已严格评分。pandas r001 将区域和全公司总额按所有 Stock 汇总，正式失败；PySpark r001 使用 `input_01` 等作为 Region 且未乘 100，正式失败。Ibis r001 因模型连接持续失败而在 1800 秒超时，评测跳过；Ibis r002 正式失败，首个差异是百分比未舍入到 9 位。仅在临时副本中将 Ibis 的两列百分比舍入到 9 位后，整表通过当前配置；正式产物和报告未改。
- **016**：每行是一个入选客户，按 Email 对齐；排名用 `integer`，显示金额用零容差 `number`。清理了下载文件夹的旧操作说明，保留非销售输入文件不修改的要求。Ibis、Polars r001 各输出 72 行并正式通过。pandas r001/r002 均因 Codex 会话未提供 shell/file 执行工具而没有生成 `solution.py` 或输出，评测跳过；这两次不能作为 pandas 计算能力结果。

两题原始 r001 状态保留在顶部表中，r002 仅作重试和诊断记录。015 的行序要求只在完整需求中，原始 query 未公开，当前配置未评分；016 的最终行序亦未评分。若后续决定将排序作为交付约束，应先同步原始 query 和完整需求，再调整 evaluator，并重新生成 interact。

## 2026-10-05：017 interact

按 `NOTES.md` 审核后，017 的 query、`query_full.md`、`amb_kb.json`、reference、GT 和 evaluator 语义一致，不需要修改资产。pandas 和 Polars 使用 Codex `gpt-6-astra`/low 的 interact r001 均生成 `FPTP=A`、`AV=C`、`Borda=B`，正式评测通过。两次候选行序为 FPTP、AV、Borda，GT 行序为 FPTP、Borda、AV；当前配置未要求顺序，因此 `order_status=ignored`，不构成问题。Ibis、PySpark 本轮未运行。

## 2026-10-05：015 pandas 复验

公开 `query.md` 补充两项百分比均针对同一 `Stock`、五个输入文件的 Region 标签、`Order Date` 的日/月/年解析及输出格式，以及百分比和金额的舍入精度。使用本 worktree 的 simulator 设置重跑 Codex `gpt-6-astra`/low、pandas interact r002。simulator 两次问答均成功：同一 Region/Stock 的保留条件由 KB 命中，百分比使用 0–100 的回答由 fallback 给出。生成 1012 行，正式评测通过；`order_status=ignored`。顶部表保留原始 r001 失败，r002 为修订后复验结果。

## 记录方式

每次记录包含日期、case、状态（待审／已决定待验证／已验证）、问题与证据、决定及变更文件、验证后端和 run 编号、下一步。未批准的建议不能写成已实施；通过仅指报告覆盖的检查。已解决问题更新状态并保留简短决定，不继续列在待审清单中。

## 2026-10-03：030–033 配置审核与 interact

本批使用本地 `dfarena-agent-sandbox:latest`（镜像 ID `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`）、Codex `gpt-6-astra`/low、simulator 同模型/temperature 0、每次上限 1800 秒，并发最多 3。固定种子 20261002，除 pandas 外，030 抽 Polars/PySpark，031 抽 PySpark/Ibis，032 抽 Ibis/PySpark，033 抽 Polars/Ibis。只修改四题的 `evaluation/config.json`；GT 自评均通过，每题一个错误数值反例均失败，公共 evaluator 29 项测试通过。reference 已在该镜像中重算并通过当前配置。031–033 均为 r001；030 的 r001 因模型网关 403 额度不足生成失败、评测跳过，额度恢复后以 r002 重试，不将环境失败记作 backend 失败。

| Case | 配置决定与当前结果 | 待审或未覆盖项 |
| --- | --- | --- |
| 030 | 一行是 Tweet Id、Comment Split、Category 对应的词级记录；以这三列为 key，温度用零容差 `number`，文本精确比较。pandas/Polars/PySpark r002 分别输出 30,818/31,102/31,094 行，均少于 GT 的 31,104 行，正式失败。只读 key 差异：pandas 缺 322、多 36 个 key（例如撇号词多出 `t`）；Polars 仅缺 tweet `496240342665265152` 的 `½` 在两类各一行；PySpark 缺 18、多 8 个 key，包含 tweet `1066107206557417473` 的多个缺词。 | `Created At` 按精确文本检查完整需求的 `DD/MM/YYYY HH:MM:SS` 格式。需继续结合候选代码与澄清记录确定这些词级差异的原因及需求是否足够明确；不能仅凭行数放宽规则。 |
| 031 | 四表分别按 Customer、Customer、Order、City 对齐；计数及 Order 用 `integer`，平均值和九位小数比例使用零容差 `number`。pandas/PySpark r001 四表通过；Ibis r001 原评测因 `33.333333333333336` 与 GT 的 `33.333333333` 不同而失败。随后将该字段的 `abs_tol` 调整为 `0.01`、`rel_tol = 0`；顶部总览仍保留原始 Ibis interact 失败状态。 | `query_full.md` 的客户/城市自定义行序当前未评分，原始 query 也未明确；需先确认是否为业务约束，不能把内容通过称作顺序通过。当前较宽的容差决定已记录，但尚未以新配置重新生成 interact。 |
| 032 | 一行是 Customer/Product 产品明细；以这两列对齐，Property Number/Sales 用 `integer`，地址及邮编精确文本。pandas、Ibis、PySpark r001 均通过当前配置，均输出 12 行。 | 当前无已发现的评分差异；通过只覆盖配置所表达的字段内容和行重数，没有行序要求。 |
| 033 | 两表以 Store/Name 对齐；奖金百分比零容差 `number`，薪资/奖金/区间界限等离散值用 `integer`。pandas r001 奖金汇总通过，但 Leeds outlier 两行均漏填指定 `End Date = 01/10/2019`；Polars r001 把超出工资范围的 Bubbles 的空白奖金百分比写为 0.0；Ibis r001 首表输出 12 行而 GT 为 10 行，且 Store 缺少 ` Store` 后缀。三者正式失败。 | Ibis 第一处行数错误会遮住后续字段比较；可继续只读诊断，但不据此改写候选或放宽配置。日期输出格式由当前 `date` 比较按日历语义验证，不验证字面 `dd/mm/YYYY`。 |

正式记录在各题 `runs/interact/codex_gpt-6-astra/<backend>/<run>/` 的 `detail/generation.json`、`detail/evaluation.json`、`workspace/solution.py`、`workspace/outputs/` 与问答日志中。上述通过只指当前配置，不代表未表达的顺序和日期字面格式已验证。

## 2026-10-02：034 配置审核与三后端 interact

**状态：已验证当前配置；输出格式与同日行序待决定。** 输出是每个匹配的交付日期与规则一行。输入日期覆盖 2019-10-01 至 2019-12-31，GT 有 48 行；reference 重算后与 GT 全部字段及行序一致。配置将 key 从全字段改为 Date/Product/Scent/Supplier，保留重复 key 的行重数检查；Month Name 和 Weekday 作为待比较结果字段。Quantity 是库存件数，改用精确 `integer`，身份和标签文本改用无空值别名的 `text_exact`。`query_full.md` 要求日期升序，配置新增 Date 升序检查；GT 满足该顺序。仅修改 `case_034/evaluation/config.json`，未修改需求、reference、GT 或候选。

GT 自评通过。应通过的 ISO 等价日期、应失败的 Quantity 加一、复制一行、日期逆序四项检查结果符合预期；公共 evaluator 29 项测试通过。interact 使用本地镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`，Codex `gpt-6-astra`/low，simulator `gpt-6-astra`/temperature 0，单次上限 1800 秒、并发 3。抽样种子 20261002，从 Polars/Ibis/PySpark 抽得 Polars/PySpark，加 pandas。三者的 `r001` 均完成生成并在当前配置下通过，内容和日期升序各为 passed，输出各 48 行；每次有一轮澄清，主要确认“每月第 n 个星期几”与只输出匹配交付。记录见 `case_034/runs/interact/codex_gpt-6-astra/{pandas,polars,pyspark}/r001/`。

**未覆盖／待决定：** `query_full.md` 规定 Date 字面格式 DD/MM/YYYY，三个候选实际都输出 YYYY-MM-DD；当前 `date` 规则只比较日历日期，不能验证字面格式。完整需求还按原始规则行序、Product、Scent 对同日记录排序；原始规则行序不在输出列中，当前 `order_by` 无法表达。三个候选同日改按 Product/Scent/Supplier 排序，与 GT 的原始规则顺序在 24 个交付日期中的 12 个不同，但日期升序仍通过。原始 `query.md` 没有指定日期字面格式或输出行序，需先决定完整需求里的这两项是否应作为业务交付约束；不能把当前三后端通过解释为这两项已通过，也不能仅为旧候选改变 GT 或 evaluator。若决定公开格式／顺序约定，应同步两份 query 与澄清资产并重新生成；若决定评分同日规则顺序，需先扩展评测表达能力。

## 2026-10-01：待审清单整理

以下条目由原 NOTES.md 移入，未因此修改任何任务资产。001–007 仅列仍待复核事项；045–050 仅保留 050 的待决问题。

## 001–007：仍待复核的事项

以下依据当前文件检查，属于待审项目，不表示已经批准对应修改。没有待决事项的 case 不单独列出。

| Case | 当前证据 | 待复核事项 |
| --- | --- | --- |
| 001 | 汽车销量各列仍用旧 `number` 容差；query_full 要求 Date、Dealership 升序，config 未检查顺序，GT 也不满足按真实日期的该排序。 | 核对销量是否统一使用精确整数；确认排序是否为任务要求，再决定是否调整 GT 顺序和配置。不能把当前内容通过当作排序通过。 |
| 002 | query 仍残留“升级到 2019.1”的工具版本提示；天气指标全部使用旧 `number`，key 包含所有指标。 | 清理过时工具措辞；按天气观测的实际粒度审核 City/Date 能否标识记录，并确定各指标所需精度，不从 GT 唯一性直接推断。 |
| 003 | Contract Length (months)、Monthly Cost 使用旧 `number`，key 包含全部输出字段；query_full 要求按月份偏移及输入姓名逆序排列，原始 query 未明确，config 未检查顺序。 | 核对合同月数的整数语义和费用精度；明确合同/月度记录的身份；判断该特殊排列是业务要求还是参考实现细节。 |
| 004 | query 背景仍含 Prep、profile pane、Prep Builder 和可选可视化表述；三类比赛统计值使用旧 `number`，key 包含全部字段；query_full 要求 True Date 升序但 config 未检查。 | 清理工具相关表述并明确表格交付范围；核对统计值的整数语义和比赛记录的 key；确认是否应对最终日期排序评分。 |
| 006 | query_full 要求计算后的 Profit 四舍五入为整数，config 仍用旧 `number`，且 Profit 在 key 中；完整需求还规定保留主表顺序并按指定产品顺序追加，config 未覆盖。 | 分别核对已有主表及新增行的利润精度；按 Country/Month/Product 的业务粒度审核 key；确认追加顺序是否为评分要求。 |

其中 001、003、004、006、007 的顺序问题需先确定任务约定，不能仅因 reference 恰好如此输出就新增排序限制。上述数值和 key 问题也不意味着全部改成 integer 或缩减 key，需逐题根据语义决定。

## 050：待决定的规则

045–050 范围内，本轮仅将 050 保留在待审清单。此前的实现错误、已解决的格式问题和其他 case 的操作性记录不再在此逐项展开。

### 1. 店名 Amstelveen 是否应映射为 Amsterdam

- 当前 reference 的 `_clean_store` 强制进行这一映射，GT 和原始 `input_03.csv` 中 Bas 的 Store 均为 Amsterdam。
- query 和 query_full 只要求统一店名，没有给出这个具体业务映射；四个后端的现 r001 均保留 Amstelveen。
- PySpark 询问该映射时，simulator 拒绝确认。`input_03.csv` 有示例，但其输入角色和权威性仍待核实。
- **待决定**：保留 Amstelveen，还是明确将其视为 Amsterdam 的业务归并。取消映射目前只是建议，尚未执行。
- 无论选择哪种规则，都应同步 query_full、amb_kb、reference 和 GT；不能靠 evaluator 别名掩盖差异。

### 2. 日期缺少年份时能否推断

- reference 将 `Monday - 13th Jan` 判为不可解析；query_full 没有明确缺少年份的处理规则。
- 这会影响 Etienne 的 Latest 记录是否保留。pandas/Polars/Ibis 的现 r001 有额外的 Latest；PySpark 得到“不推断年份”的回答后没有保留该记录。
- **已决定**：缺少年份且无法无歧义解析的日期一律视为不可解析，Completion Date 设为 null，不根据上下文推断年份；规则已写入 query_full。这样的响应不参与 First/Latest 选择。

### 3. 数值缺失值是否接受 nan 表示

- Ibis 的现 r001 在可空数值列中输出 `nan`；当前 integer 规则默认不把它视为空值，050 也尚未配置额外 `null_values`。
- **待决定**：是否在允许缺失的数值列中显式接受空字符串和 `nan`。按列配置，不能推广为所有文本列的空值规则。
- 允许等价空值表示不等于允许丢失有效值：GT 非空、候选为空时仍应失败。

### 4. input_03.csv 的输入角色

- 该文件具有示例输出性质，agent 已将其与原始数据比较，并发现店名、年龄和保留记录等差异。
- **待复核**：它是任务允许使用的示例、辅助数据，还是不应暴露给 agent 的答案资产。未决定前不删除，也不将其视为权威 GT。

### 下一步验证

先确定上述规则，再使用新资产运行 pandas 和两个记录在案且不重复的抽样后端。

两份 query 已补充“列名必须包含括号内文字”，公共 evaluator 也已支持额外日期格式与内置 ISO datetime 格式合并。这两项不再列为疑问。但现 r001（原 r002）CSV 的表头没有随 query 修改而变化，仍会先报列名缺失；必须重新生成，不能手动补表头后记作通过。

当前年龄规则是 `2020 − birth_year`，有效日期才可参与 First/Latest 选择。这些规则已明确，不属于本轮待决项；候选采用周岁算法或保留空日期造成的结果差异仍按真实错误处理。

证据位置：`case_050/runs/interact/codex_gpt-6-astra/<backend>/r001/` 下的 `workspace/solution.py`、`workspace/outputs/`、`logs/interaction.jsonl` 和 `detail/evaluation.json`。此前对临时副本做过的列名及格式规范化仅用于诊断，不是正式通过结果。

## 2026-10-01：040–044 三后端审核

本批按 pandas 加两个不重复抽样后端执行 interact。随机种子为 20261001：将 Polars/Ibis/PySpark 的三种二元组合各放两份后打乱，取前五项，兼顾抽样与覆盖。模型为 gpt-6-astra，单次上限 1800 秒，并发为 3。

| Case | 额外后端 | 配置审核与处理 |
| --- | --- | --- |
| 040 | Polars、Ibis | 汇总人数及原始评分使用 integer；NPS、keynote 和 food 的明确舍入结果用零容差 number。汇总无独立记录身份，明细缺少受访者 ID，保留全字段对齐而不把 Timestamp 偶然唯一当作业务 ID。 |
| 041 | Ibis、PySpark | 保留退款类别、Product/Scent 粒度的 key；金额用零容差 number；Scent 采用无 null 别名的精确文本，保留字面 N/A；按完整需求增加 Product/Scent 升序检查。GT 已满足该顺序。 |
| 042 | Polars、Ibis | 完整需求明确每个 Zip Code 保留最大销售的一条记录，故 key 改为 Zip Code，邮编用精确文本；汇率为原样附加的 lookup 值，改零容差 number。增加 City/Country/Zip Code 升序检查。 |
| 043 | Polars、PySpark | 按 Store/Quarter 汇总和关联，key 改为 Store/Quarter；金额字段改零容差 number，保持季度及截断百分数的 integer。不把货币金额仅凭本次为整数就一概标成 integer。 |
| 044 | Ibis、PySpark | 按 Store/Team Member 平均，key 改为这两个维度；两位小数估计值用零容差 number，Rank 保持 integer；按完整需求增加 Store/Rank/Team Member 顺序检查。 |

042 和 044 的旧 GT 未按完整需求排列。本次仅重排 GT 行，程序检查重排前后全部字段和行重数相同，未修改 reference 或业务值。顺序依据来自 query_full，且与 reference 一致；原始 query 未明确这些顺序，解释实验时需要保留这一信息。

已完成验证：五份 reference 通过新版 config；每题检查等价数值表示应通过、数值加一应失败、复制一行应失败，共 15 项符合预期；公共 evaluator 29 项测试通过。对应检查见 [evaluation_checks_040_044.json](evaluation_checks_040_044.json)。生成及评测进度见 [interact_validation_040_044.json](interact_validation_040_044.json)，未完成项不能计作成功或语义失败。

预检关注点：040 的任意大小写词表及 Minty. 标点例外由完整需求/reference 规定，原始需求只要求分组清洗，需要检查 simulator 能否可靠说明；明确时间字面格式当前仅验证 datetime 语义。042 的有效城市白名单和 043 的 Actions 阈值应结合实际问答判断，不靠放宽文本比较解决。以上暂为审查重点，尚不是已确认的 agent 错误。

### 040–044 运行结果

15 次运行均完成生成，没有环境/额度失败。040 三后端均未通过；041 pandas 通过，Ibis/PySpark 未通过；042 Ibis 通过，pandas/Polars 仅顺序未通过；043 和 044 的三个后端均通过。共 8/15 正式通过，另有 042 的两次内容通过。所有运行是对应 backend 的 r001。

逐文件只读诊断见 [diagnostics_040_044.json](diagnostics_040_044.json)，避免第一张表错误遮住其他输出。这些报告不修改 candidate，也不替代正式结果。

- **040，精度与 schema 问题（历史 r001 记录）**：三次 NPS 都是未舍入的 -35.8974358974359，而 GT 为 -35.9。原始 query 当时没有精度说明；旧 config 曾用 `abs_tol: 0.05`，但 NPS 同时是 key，该容差并不能在此记录上完成预期匹配。三次明细都至少缺少规定列名（如 ___why?）；这是独立的 schema 错误。simulator 回答“使用预定义 canonical mapping”，却未附映射表，agent 实际拿不到完整大小写约定。以下 2026-10-02 修订已处理可见性、精度和时间要求；r001 仍是旧资产结果。
- **041，部分候选错误及输出约定待完善**：Ibis 的金额表通过，库存表把字面 N/A 写为空；PySpark 使用 Refunds/Recalls/Total 代替完整标签，并把无香型写为空。完整需求有明确约定，但原始 query 未公开这些词汇。Ibis 曾询问退款标签并获得正确回答，PySpark 未询问。建议后续像 046 一样公开固定输出词汇；本次未变更 query，不将旧候选当作见过新 schema。保留金额和库存严格检查。
- **042，内容通过、顺序约定待确认**：pandas/Polars 各字段均通过，仅排列不符合 query_full 的 City/Country/Zip Code 升序。原始 query 未规定该排序，问答也未澄清排序。因此保留按当前完整需求得到的正式失败，同时单独报告内容通过；后续决定公开排序要求还是不将此排列作为业务评分要求，不因某个 backend 的结果临时调整。
- **043、044**：三后端均通过当前内容和配置检查，无需进一步放宽规则。044 的排序来自完整需求，原始 query 未明示；成功不代表证明这一排序应成为原任务的业务约束。

## 2026-10-01 至 2026-10-02：038–039 三后端审核

抽样种子为 20261002，每题从三个额外后端中 random.sample 两个：038 为 Polars/PySpark，039 为 PySpark/Ibis，均加 pandas。沿用 interact、gpt-6-astra、1800 秒上限和并发 3。

- **038**：输出为每条就诊记录，使用 VisitID 作为 key；VisitID/PatientID 改为无 null 别名的精确文本，避免对身份编号进行近似匹配；访问次数和序号使用 integer。完整需求中的排序用于确定访问序号，不额外从参考输出推导全表展示顺序。两列日期继续按 date 语义比较，不检查字面格式。输入日期月/日含义需关注澄清是否明确。
- **039**：三个输出分别以 Browser、Operating System、Origin 为 key；访问量用 integer，Origin 四舍五入后的百分数和差值用 integer；其他百分数及其差值用精确 number，保留 0.5。输入行序保留无法用当前 order_by 直接表达，继续忽略输出顺序并明确覆盖限制。

两题 reference 均通过更新后的配置。进度与最终结果见 [interact_validation_038_039.json](interact_validation_038_039.json)。


### 038–039 运行结果与覆盖限制

六次生成和正式评测均完成，按当前 config 全部通过，无环境或额度失败。所有运行均为对应 backend 的 r001；没有修改候选输出，也没有为通过而追加放宽配置。

| Case | pandas | 抽样后端一 | 抽样后端二 |
| --- | --- | --- | --- |
| 038 | 通过；2 次 ask | Polars 通过；2 次 ask | PySpark 通过；1 次 ask |
| 039 | 通过；1 次 ask | PySpark 通过；1 次 ask | Ibis 通过；2 次 ask |

两题 reference 验证及六项正反例检查见 [evaluation_checks_038_039.json](evaluation_checks_038_039.json)，逐输出内容诊断见 [diagnostics_038_039.json](diagnostics_038_039.json)。

- **038**：三后端均正确生成就诊粒度的访问序号、总次数、首次日期和新患者标记。本轮未发现日期解析差异，无需修改日期配置。当前只比较日期语义，不验证 DD/MM/YYYY 字面格式，也不额外检查全表展示顺序。
- **039，顺序要求的模式范围**：原始 `query.md` 没有规定输出行顺序；`query_full.md` 作为 clarified 模式的完整说明仍保留“本月原序、再接历史独有成员原序”的要求。为避免 interact 模式把该额外约定当作 ambiguity 主动提问，已从 `amb_kb.json` 删除 `2_O1_row_order_policy`。当前 `evaluation/config.json` 仍不检查行顺序，因此正式通过只代表已配置的内容检查通过；顺序要求若要成为 clarified 的判分项，后续应单独扩展顺序评测能力。原有顺序诊断见 [order_diagnostics_039.json](order_diagnostics_039.json)。
- **Simulator 分类一致性，待审**：038 中“标记标签 + 日期格式 + 输出顺序”的相似复合问题，对 pandas/Polars 返回 refuse_too_broad，对 PySpark 则一次回答。前两者拆问后取得答案并通过，但拒绝会消耗轮次和问题预算；该差异影响交互成本，值得单独审查 simulator 的复合问题判定。本轮不据此修改 case config，也不重跑筛选更好的问答。
- **039 Ibis 的中间 API 错误已自行修复**：最初向 DuckDB read_csv 传入 schema 参数失败，agent 改用 columns 后成功运行及评测。这是生成过程中的可恢复实现错误，不是最终失败或评测协议问题。

## 2026-10-02：040 需求与评测修订（已决定，待 interact 验证）

040 的 r001 三后端都在旧资产下失败，不能用改动后的 query 重新解释旧候选。检查发现汇总表的 `NPS Score` 同时是全字段 key，旧 `abs_tol: 0.05` 虽已配置却不能可靠完成所期望的 NPS 比较。原始 query 也未写一位小数要求。现在原始 query 公开 NPS 四舍五入到一位、准确输出列名和使用 `input_02.csv`；汇总 key 改为三个计数字段，NPS 作为零容差结果值比较。总表只有一行，三个计数字段用于对齐，不把 NPS 错误藏在身份字段中。

完整需求已有 91 项规范词形映射，但 simulator 在 r001 只回答“使用预定义映射”，未交付词表，大小写精确评分因而缺少可见依据。原始 query 明确了 `input_01.csv` 和 `input_02.csv` 是同批响应的两种表示，以免双计。词形映射的交付方式见下面 2026-10-03 的修订。

输入时间戳含小数秒，GT 只保留整秒。两份 query 现在明确丢弃小数秒；具体日期时间字符串不评分，`datetime` 仍检查秒级时刻。完整需求原有 `M/D/YYYY H:MM:SS AM/PM` 字面格式要求已改为允许无歧义的整秒表示，避免与 evaluator 覆盖范围冲突。

验证：更新后的 reference 输出 1 行汇总、113 行明细并通过 GT/config；公共 evaluator 29 项测试通过。GT 自评通过，未舍入 NPS `-35.8974358974359`、复制一条明细行、时间戳错一秒分别被拒绝。尚未新建三后端 interact run：本 worktree 的 `runners/configs/codex/config.toml` 不存在，只有示例配置。需要在有 runner 配置的环境中以新资产运行 pandas、Polars、Ibis（各 r002），保存问答/输出/评测，再更新顶部结果表。旧 r001 三次失败保留为历史快照。

## 2026-10-03：040 词表资产简化（已决定，待 interact 验证）

对照原始 `prepbench/data/case_040` 和 `prepbench/reference/solutions/case_040`：`query_full.md` 原已列出全部 91 项映射，reference 原已内嵌同一字典，原 KB 只有歧义条目和简短代码 `ref`。撤回新增的 `inputs/word_mapping.json`、KB 中重复的词表以及通用 simulator 提示特例。reference 恢复独立的内嵌字典，不在运行时读取 KB。

当前 `amb_kb.json` 各条目用自然语言 `intent` 说明规则，不包含 `ref` 代码。词形条目指向完整需求中的规范映射并说明大小写、标点和未映射词处理；原始 query 继续保留分组清理的歧义。旧 r001 的 simulator 只回答“使用预定义映射”，说明能否在 interact 中传达完整词表仍需实跑确认；不把提示修改当成已验证的修复。

## 2026-10-03：040 新资产 interact 复验

用现有镜像、Codex gpt-6-astra/low 和 simulator 配置重跑 pandas、Polars、Ibis，分别保存在 `case_040/runs/interact/codex_gpt-6-astra/<backend>/r002/`。三次生成均完成，汇总表均通过（1 行）；明细表均为 113 行，pandas 通过，Polars 和 Ibis 的正式评测均为 `KEY_MISMATCH`。

- pandas：3 轮澄清后取得 50 个需保留大小写的 canonical 形式，明细内容通过。
- Polars：3 轮澄清仍未取得词表。其明细与 GT 在标准化时间、数值和首尾空白后有 15 行词形大小写不一致；再忽略词形大小写则 113 行全部匹配。因此这次失败指向映射未可靠传达，并非计数或展开行数错误。
- Ibis：2 轮澄清取得完整 91 项映射，但复用了将均值舍入到 1 位的函数，使 `Food Rating Score` 也只有 1 位；完整需求和 GT 要求 9 位，57 行不匹配。它没有询问食物分数的输出精度，原始 query 也未明确该精度。

词表保留在 `query_full.md`，reference 保留内嵌字典，KB 仍只写自然语言 intent；此次复验未增加资产文件或改变候选。后续需要决定如何让 simulator 在 agent 明确索取完整映射时稳定提供它，并将食物分数精度写入 interact 可见需求或可靠澄清。旧 r001 仍是改动前快照。

离线复核：reference 仍输出 1 行汇总、113 行明细，按现行配置通过 GT；evaluator 与 simulator 的 32 项测试通过。三后端 r002 仍待运行。

## 2026-10-02：035–038 评测配置审核与 interact 抽样

本轮按 `NOTES.md` 执行：先核对原始需求、完整需求、ambiguity KB、reference、GT 和配置，再用 pandas 加两个不重复抽样后端运行 interact。035–037 使用抽样种子 20261003：035 为 Polars/PySpark，036 为 Ibis/PySpark，037 为 Polars/Ibis；038 沿用本轮前已完成的 pandas/Polars/PySpark r001，因为其 query、ambiguity KB 和配置没有变化。

### 配置调整

- **035**：output_01 的业务粒度为 Supplier/Product/Scent，output_02 为一条店铺请求，使用 Store/Product/Scent/Supplier/Date Required 作为可辩护的请求身份。数量和延迟改为 integer，Stock Ready? 为 boolean，日期按 `%d/%m/%Y` 的 date 语义比较，文本身份字段使用无 null 别名的精确文本，Surplus Product 使用零容差 number 改为 integer，因为它是库存数量。
- **036**：两个输出各是一名球员记录，使用 NAME 作为记录 key；Jersey Number 作为文本编号，保留 `00` 等字面值。身高和体重是 reference 明确保留两位小数的连续结果，使用零容差 number；AGE 使用 integer，其余标签和薪资使用精确文本。`query_full`/`amb_kb` 已明确 output_01 来自 input_02、output_02 来自 input_01，配置不替 agent 修复文件映射。
- **037**：每行是一个汇总类型，使用 Type 作为 key；Returned Orders 和 Total Orders 为 integer，`% Returned` 是明确四舍五入一位小数的 number，使用零容差。完整需求给出了 Type 的自定义分组顺序，但原始 query 没有要求，当前 order_by 不能表达这套自定义序列，因此不把 GT 排列作为正式评分项。
- **038**：沿用已审核配置：VisitID 为身份文本，访问次数为 integer，日期按 date 语义比较；reference 已验证通过。

四题 reference 均通过当前配置；035–037 新配置对应的 GT 自评通过。运行和逐文件诊断见 [interact_validation_035_037.json](interact_validation_035_037.json) 和 [diagnostics_035_037.json](diagnostics_035_037.json)。

### interact 结果

| Case | pandas | 抽样后端一 | 抽样后端二 |
| --- | --- | --- | --- |
| 035 | 失败 | Polars 失败 | PySpark 通过 |
| 036 | 失败 | Ibis 失败 | PySpark 失败 |
| 037 | 通过 | Polars 通过 | Ibis 失败 |
| 038 | 已完成：通过 | Polars 通过 | PySpark 通过 |

- **035**：pandas/Polars 的 output_01 多出 `Premium Parry Products / Liquid Soap / Lavender / 50`，把不符合完整需求“恰好一个请求且该请求延迟”条件的库存也判为 surplus；output_02 内容行数相符。PySpark 两张表通过。当前保留严格 config，不为多出的业务行放宽行数或 key。
- **036**：三个候选都把两个输入对应的输出文件反向生成：output_01 产生 19 行（input_02），output_02 产生 20 行（input_01），而 GT 规定相反映射。该失败来自忽略 clarification/任务映射，不是 key 或数值容差问题。保留 NAME key 和严格字段类型。
- **037**：pandas/Polars 内容通过当前配置；Polars 的行排列不同，但原始 query 没有顺序要求，故不判失败。Ibis 的多个 `% Returned` 保留了未舍入值，例如 Fruit 输出 `50.26`，GT 要求一位小数 `50.3`，属于真实舍入错误，不能通过容差掩盖。
- **038**：三后端均通过；本轮不重复生成。

035–037 的 simulator 问答、耗时、agent 代码和候选输出均保留在各自的 `runs/interact/.../r001` 中。以上失败没有修改 query、reference 或 GT；若后续决定修订任务语义，应先同步完整资产并重新生成。

## 2026-10-03：036 原始 query 补充 output/input 映射

复核 036 的三份 interact 问答记录后确认，pandas、Ibis、PySpark 均未在 simulator 交互中询问两个输入文件与两个输出文件的对应关系；三者因此都将 `output_01` 与 `output_02` 反向生成。原始 `query.md` 只描述“用一个文件构建、在另一个文件测试”，没有明确映射。现补充：`output_01.csv` 由 `input_02.csv` 生成，`output_02.csv` 由 `input_01.csv` 生成。仅修改 `case_036/query.md`，未修改 evaluation、GT 或 reference；已有 r001 保留为旧 query 下的历史 interact 结果，尚未按新 query 重跑。

## 2026-10-03：037 原始 query 补充百分比舍入规则

复核 037 的 interact 问答和候选输出后确认，Ibis 未将 `% Returned` 舍入到 GT 要求的一位小数，输出了如 `50.26` 而非 `50.3`；pandas 和 Polars 在交互中获得或推断了该规则并通过。原始 `query.md` 只写“Form your % Return Rates”，没有明确计算公式和精度。现补充 `% Returned = (Returned Orders / Total Orders) * 100`，并明确四舍五入到 1 位小数。仅修改 `case_037/query.md`，未修改 evaluation、GT 或 reference；已有 r001 结果保留为旧 query 下的历史 interact 结果，尚未按修订后的 query 重跑。

## 后半部分：按 case 顺序整理

以下段落是对后半部分审核记录的顺序化索引；前面的首次执行记录和原始 interact 错误保持不变。

**001。** 已复核：每行是一个日期、经销商的销量，保留 Date/Dealership key，销量字段改为精确 integer，Dealership 改为显式精确文本。之前四后端的 interact 输出按当前配置重评均通过。完整需求的 Date/Dealership 升序尚未评分，reference 按格式化日期字符串排序，GT 也未满足真实日期顺序；本轮不调整 reference 或 GT。

**002。** 已复核：每行代表一个城市、日期的天气，key 改为 City/Date，四个指标依完整需求改为 integer，City 使用显式精确文本；原始 query 删除过时的 2019.1 软件版本提示。旧 pandas/Polars/PySpark 输出重评通过，旧 Ibis 失败：`ibis.row_number()` 从 0 开始，但代码用 `== 1` 选择所谓第一条记录，导致取到第二条并丢失单条记录的指标；simulator 已正确说明保留输入顺序第一条，不放宽评测。修改 query 后另补跑 interact，结果见本轮复验记录。

**003。** 已复核：每行代表一份合同的一个付款日期，key 改为 Payment Date/Name/Start Date；完整需求明确要求整数费用和合同月数，两列改为 integer，Name 使用显式精确文本。旧四后端输出重评均通过。完整需求的月份偏移及输入姓名逆序没有在原始 query 中明确，暂不新增排序评分，未修改 query、reference 或 GT。

**004。** 已复核：每行是一场 Spurs 比赛，key 改为 True Date/OPPONENT，三个统计值改为 integer，文本列显式精确比较。原始 query 改为 DataFrame 清洗表交付；两份 query 明确括号属于 `Opponent (clean)` 列名，并规定 W/L、Home/Away 固定标签。旧四后端重评均失败：全部使用 Win/Loss，三个还错误命名 Opponent；pandas/PySpark 按输入顺序累计 W-L，Polars 保留损坏的原始 W-L，Ibis 的累计值正确。修改 query 后另补跑 interact。累计胜负必须按真实日期计算，但最终展示顺序暂未评分；reference 对格式化日期字符串排序与 GT 不一致，本轮未修改 reference 或 GT。

**005。** 已复核：每行是一条联系记录，没有稳定联系 ID，保留全字段 key 和重复记录数量；boolean/integer 改为显式对象配置。旧四后端输出重评均通过，simulator 正确给出两份输入的周一锚点 2019-06-17、2019-06-24。未修改 query、KB、reference 或 GT。

**006。** 已复核：每行代表一个国家、月份、产品，key 改为 Country/Month/Product，移出结果列 Profit；利润按输入和明确舍入要求改为 integer，Country/Product 使用显式精确文本。旧 pandas/Polars/Ibis 输出重评通过，PySpark 因输出 `Category` 而非契约规定的 `Product` 失败；仅在内存中重命名作诊断后内容相同，但正式结果仍为失败。保留主表顺序和 Bar/Liquid 追加顺序尚未评分，未修改 query、reference 或 GT。

**007。** 已复核：`Max Weight`、`Max Volume`、`Weight Allocated`、`Volume Allocated` 均改为 `integer`，其余字段和全字段 key 保持不变。pandas、Polars、Ibis 的 interact r001 均完成生成并通过当前配置；Ibis 改变了输入顺序，但当前 evaluator 忽略行序，因此该项未被评分。完整需求要求保留 `Departure Details` 输入顺序，当前配置仍未覆盖该顺序；未修改 query、reference 或 GT。

**008。** 三后端 interact 均完成生成和正式评测：pandas 通过，Polars 和 Ibis 失败。Ibis 和 Polars 都把 `Stock Adjusted` 输出成调整数量而不是最早调整日期；Ibis 对无调整事件输出 `0`，Polars 还把 `Number of Records` 错算为 Theft 与 Stock Adjusted 记录总数，而该字段只统计 Theft 记录。失败属于候选实现错误，未修改 query、evaluation config、reference 或 GT。

**009–029。** 当前没有独立的后续审核段；未在此补造 case 结论，interact 状态以顶部总览为准。

**030。** 详见前面的 030–033 原始记录。当前三次 r002 均因词级输出行数不足失败，差异原因仍需结合分词、停用词和需求澄清继续审查。

**031。** 详见前面的 030–033 原始记录。pandas 和 PySpark 原始 interact 通过，Ibis 原始 interact 因九位小数浮点表示差异失败；后续配置已将该字段 `abs_tol` 调整为 `0.01`，但顶部总览保留原始失败状态，尚未重新生成 interact。

**032。** 详见前面的 030–033 原始记录。pandas、Ibis、PySpark 均通过当前配置，输出 12 行；当前没有发现额外评分差异。

**033。** 详见前面的 030–033 原始记录。pandas、Polars、Ibis 均失败，分别涉及 outlier 日期缺失、空白奖金百分比被写成 0，以及员工行数和门店名称差异。

**034。** 详见前面的 034 原始记录。三个已运行 backend 在当前配置下通过，但日期字面格式和同日行序仍未被当前 evaluator 覆盖。

**035。** 配置按 Supplier/Product/Scent 和店铺请求粒度审核，数量及延迟使用 integer，Stock Ready? 使用 boolean，日期按 `%d/%m/%Y` 语义比较。pandas/Polars 多出不符合“恰好一个请求且该请求延迟”条件的 surplus 行，PySpark 通过；不因失败放宽 key 或行数。

**036。** 两个输出分别代表球员记录，使用 NAME 作为 key，Jersey Number 保留文本编号，身高体重为精确小数，AGE 为 integer。原始 interact 中三个 backend 都反向使用了两个输入文件，导致 output_01/output_02 映射错误；复核确认 simulator 未询问该映射，现已将映射直接补入 `query.md`。旧 r001 结果保留，尚未按修订后的 query 重跑。

**037。** 每行是一个汇总类型，Type 为 key，订单数为 integer，百分比为一位小数 number。原始 interact 中 pandas/Polars 内容通过，Polars 的排列差异不评分；Ibis 未按一位小数舍入，属于真实计算错误。复核确认原始 query 未明确该精度，现已将计算公式和 `round to 1 decimal place` 补入 `query.md`；旧 r001 结果保留，尚未按修订后的 query 重跑。

**038。** VisitID 是精确身份文本，访问次数为 integer，日期按 date 语义比较；pandas、Polars、PySpark 当前均通过。完整需求中的日期字面格式和全表展示顺序仍未评分。

**039。** 三个输出分别按 Browser、Operating System、Origin 对齐，访问量为 integer，明确舍入后的字段按对应精度比较。三个 backend 均通过当前内容配置；输入行序保留要求无法由当前 order_by 表达，因此不作为正式评分项。

**040。** 该 case 经历需求、词表和精度修订：NPS 改为一位小数并从 key 移出，汇总 key 改为计数字段，词形映射写入完整需求。r002 pandas 汇总及明细通过，Polars 因词表大小写未可靠传达失败，Ibis 因错误复用一位小数舍入导致 Food Rating 失败；旧 r001 不按新资产重解释。

**041。** 配置保留退款类别及 Product/Scent 粒度，金额使用零容差 number，Scent 精确保留字面 N/A，并检查 Product/Scent 顺序。pandas 通过，Ibis/PySpark 在标签或空值表示上失败；完整需求虽已规定固定标签，但原始 query 未公开这些词汇。

**042。** 每个 Zip Code 保留最大销售记录，邮编按精确文本比较，汇率为零容差 number，并检查 City/Country/Zip Code 顺序。Ibis 内容通过，pandas/Polars 仅因完整需求排序失败；原始 query 未明确排序，因此该顺序是否应成为业务约束仍待决定。

**043。** 按 Store/Quarter 汇总和关联，金额使用零容差 number，季度及明确截断百分数使用 integer。三个运行 backend 均通过当前配置；完整需求中的 Actions 阈值仍需结合实际澄清审查，不因通过而扩大规则。

**044。** 按 Store/Team Member 平均，估计值使用零容差 number，Rank 使用 integer，并检查 Store/Rank/Team Member 顺序。三个 backend 均通过；该排序来自完整需求而非原始 query，业务必要性仍需单独确认。

**045。** 顶部总览保留 pandas r002 失败、Polars/Ibis 通过、PySpark 失败的结果；pandas 的 r001 是跳过记录。后续解释应以各自 run 的正式 evaluator 报告为准，不把不同 run 混为一次实验。

**046。** 顶部总览显示四个 backend 均失败；当前记录保留各候选的 schema、标签和计算差异，不通过放宽 evaluator 来消除真实错误。

**047。** pandas 和 PySpark 当前通过，Polars/Ibis 为生成后未执行评测的跳过记录；跳过不计作失败或通过，后续如需覆盖应重新运行并保留新 run。

**048。** 原 r001 四个后端均因模型网关额度不足而生成失败、评测跳过；这些失败归档已删除。原 r002 四个后端均完成生成，各输出 50 行，正式 evaluator 内容及顺序均通过；现统一归档为 r001。`interact_validation_045_049.json` 仍是删除前的原始快照，其中 048 的跳过记录不代表当前归档状态。

**049。** 原始 r001 四后端因模型网关额度不足生成失败、评测跳过；顶部采用后续 r002 的正式评测状态。r002 四后端均完成生成和评测：pandas、Polars、PySpark 两表通过；Ibis 因 output_01/output_02 东西部反置先报 `KEY_MISMATCH`。只读交换文件后仍发现西部 2 个、东部 4 个 Rank 错误，两表各 15 个 L10 均错误，多数 Strk 错误：候选代码按日期文本排序、将零起点 `row_number` 用 `<= 10` 筛选，并对并列名次采用最小名次。这些是候选实现错误，未改候选或放宽评测。reference 与 GT 按 Team 对齐后两表一致；东部两个 Rank 14 球队的行序不同，需求和 config 均只检查 Rank 升序。原始 query 未规定输出文件对应的会议，现按既有 query_full/reference/GT 在 query 中公开 `output_01.csv` 为 Western、`output_02.csv` 为 Eastern；r002 仍是旧题面下的历史结果，修改后尚未新跑 interact。

**050。** 原 r001 四后端均因模型网关 `403 Forbidden: 用户额度不足` 生成失败、评测跳过；失败归档已删除。原 r002 四后端均完成生成和评测，正式报告均为 `MISSING_COLUMNS`，现归档为 r001。它们都将 `Completion Date (Date Time stamp)` 和 `Result (First / Latest)` 缩写为 `Completion Date`、`Result`，内容未获正式评测。旧输出的只读诊断另见上文；当前补充列名要求后的题面尚未重跑。店名 Amstelveen 是否映射为 Amsterdam、缺少年份日期是否推断、数值缺失是否接受 `nan`、`input_03.csv` 的输入角色仍是待决定事项；应先统一规则并同步 query、KB、reference 和 GT，再重新生成候选。

## 2026-10-03：045 当前资产 interact 复验

仅重跑原始失败的 pandas 和 PySpark，使用当前 query/KB/reference/config、`gpt-6-astra` 和 `dfarena-agent-sandbox:latest`。顶部原始运行结果保持不变，Polars/Ibis 原始通过，本次未重跑。

| Backend | Run | 正式评测 | 输出行数 |
|---|---|---|---|
| pandas | r003 | 两表内容通过，顺序未评分 | output_01：20；output_02：10 |
| PySpark | r002 | 两表内容通过，顺序未评分 | output_01：20；output_02：10 |

两个后端均收到明确的 0–1 比例、两位小数和完整日期标签要求，最终未乘 100，也未删去日期中的星期文本。pandas 首次 clarification 调用出现 RuntimeError，重试后成功；这两次调用不代表两轮有效澄清，interaction budget 记录一轮。PySpark 一次调用完成澄清。

## 2026-10-04：001–006 复核与资产整理

本轮复用了相邻工作目录 `../dfArena/PrepBench/case_001` 至 `case_006` 中用户之前的实验。修改前两目录的 query、query_full、KB 和 reference 逐字节相同，历史 run 的可见 query/input 哈希也与本轮修改前资产一致。历史 CSV 仅用当前配置离线重评，没有覆盖历史代码、输出或报告；002/004 修改 query 后另在当前 worktree 新建 interact run。前半部分首次执行表保持不变，后半部分 001–006 段落记录当前决定。

### 历史输出按当前配置重评

此表的 run 全部来自 `../dfArena`，与当前 worktree 的同名 r001 不同。001 的 pandas 使用 r004、Polars 使用 r002，其余均使用各 backend 的 r001；选择的是各后端最近已有正式评测的 run，未为获取通过结果筛选旧 run。

| Case | pandas | Polars | Ibis | PySpark |
|---|---|---|---|---|
| 001 | 通过 | 通过 | 通过 | 通过 |
| 002 | 通过 | 通过 | 失败：去重行号错误 | 通过 |
| 003 | 通过 | 通过 | 通过 | 通过 |
| 004 | 失败：列名、标签及累计 W-L | 失败：标签及原始 W-L | 失败：列名、标签 | 失败：列名、标签及累计 W-L |
| 005 | 通过 | 通过 | 通过 | 通过 |
| 006 | 通过 | 通过 | 通过 | 失败：Category 列名 |

所有正式失败保持不变；临时列名/标签替换仅在内存中用于定位后续差异，不修改候选 CSV，也不计作通过。详细证据保存在本地 `historical_reevaluation_001_006.json`。

### 资产变化与验证

六个 case 的配置均改为显式字段对象，并保留已有日期解析格式。001 销量、002 四个天气指标、003 费用及合同月数、004 三个统计值、006 利润采用精确 integer；身份文本使用 `text_exact` 且 `null_values: []`。002 key 收敛为 City/Date，003 为 Payment Date/Name/Start Date，004 为 True Date/OPPONENT，006 为 Country/Month/Product；001 保留 Date/Dealership，005 没有稳定联系 ID，保留全字段对齐和重复行数量。002 清理旧软件版本提示；004 清理旧工具操作背景，并在两份 query 的 Output 中公开精确列名及固定标签。KB、inputs、reference 和 GT 均未修改。

六份 reference 在固定 Docker image `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921` 中执行并通过当前配置，输出行数依次为 48、14、54、64、15、12。GT 自比通过；24 个正反例检查符合预期：等价整数 `.0` 通过，整数加 1、增加小数 0.1、复制输出行均失败。公共 evaluator 单元测试 29/29 通过。

顺序与日期字面格式仍有覆盖限制：001 的 GT/reference 不满足完整需求的真实日期排序；003 的特殊排序未在原始 query 中公开；004 的最终展示顺序未评分且 reference 对日期字符串排序，但按真实日期累计 W-L 是必须验证的计算；006 的主表顺序及 Bar/Liquid 追加顺序未评分。日期配置按解析值比较，不强制字面 `dd/mm/YYYY`。本轮不以 reference 默认行为新增排序规则，不修改 GT 排列。

### 修改 query 后的新 interact

使用上述固定 image ID、Codex `gpt-6-astra`（low reasoning）及 `gpt-6-astra` simulator（temperature 0）。抽样 seed 为 `20261004`，每题 pandas 加两个不重复后端：002 抽到 Polars/PySpark，004 抽到 Ibis/PySpark。当前 worktree 下各 backend 新 run 均为 r001；与历史实验的同名编号分别记录。运行日志、候选及本地审核报告不属于 workload 提交资产。

| Case | Backend | 当前 worktree Run | 正式评测 | 输出行数 |
|---|---|---|---|---|
| 002 | pandas | r001 | 通过 | 14 |
| 002 | Polars | r001 | 通过 | 14 |
| 002 | PySpark | r001 | 通过 | 14 |
| 004 | pandas | r001 | 通过 | 64 |
| 004 | Ibis | r001 | 通过 | 64 |
| 004 | PySpark | r001 | 通过 | 64 |

002 新运行正确合并输入并处理重复天气指标。004 三后端均获得按 DATE 真实时间顺序重算累计 W-L 的澄清，使用精确列名和固定标签后通过；Ibis 在执行过程中修正实现问题，最终正式评测通过。以上为当前配置下的内容通过，最终展示顺序仍未评分。新运行的 seed、后端及退出状态保存在本地 `interact_validation_002_004.json`，问答及正式评测报告保留在各自 runs 目录。

提交前再次直接使用保存的候选 CSV 和当前 config 运行 evaluator，共复验 33 份已有正式评测的 interact 产物：相邻 `../dfArena` 的 27 份（包含所有 001–006 首次 r001，以及 001 pandas r003/r004、Polars r002），当前 worktree 的 002/004 新产物 6 份。所有通过/失败状态与各 run 原报告一致，没有原先通过的输出因本轮配置修改而失败。旧 002 Ibis、004 四后端及006 PySpark 仍为正式失败；由于结果值移出 key，002 Ibis 和004 Polars 的错误类型由 KEY_MISMATCH 变为 VALUE_MISMATCH，但状态仍为失败。新 002 pandas/Polars/PySpark、004 pandas/Ibis/PySpark 全部通过。未重命名或修补候选，未覆盖原报告；本地复验报告为 `saved_output_verification_001_006.json`，不纳入 workload 提交。

正式报告分别见 `PrepBench/case_045/runs/interact/codex_gpt-6-astra/pandas/r003/detail/evaluation.json` 和 `PrepBench/case_045/runs/interact/codex_gpt-6-astra/pyspark/r002/detail/evaluation.json`；问答保存在各自 `logs/interaction.jsonl`。当前新增的比例及日期表示 intent 在此次复验中有效传达；不据此保证 LLM simulator 在所有后续运行中都稳定。本次未修改任务资产或放宽 evaluator。


## 2026-10-05：011 原始资产三后端 interact

**状态：当前配置下已完成运行；资产语义与评测修订待决定。** 使用 `PrepBench/scripts/run_benchmark.py`，Codex `gpt-6-astra`/low、interact、每组限时 1800 秒，固定镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`。Codex 配置显式指向主仓库 `../dfArena/runners/configs/codex`，simulator 使用本 worktree 的共享配置。随机种子 20261005，从 `[polars, ibis, pyspark]` 抽得 Ibis/PySpark，加 pandas；三组均为 `r001`。未修改 query、KB、reference、GT 或 evaluation/config。

| Backend | 正式评测 | 输出行数 | ask 次数 | agent 耗时（含 simulator） |
| --- | --- | --- | --- | --- |
| pandas | 通过 | 503 | 1 | 175.56 秒 |
| Ibis | 通过 | 503 | 1 | 209.53 秒 |
| PySpark | 通过 | 503 | 2 | 186.66 秒 |

只读逐行核对：三份候选 Row 均唯一，Date 与 volume 全部匹配 GT。pandas/Ibis 保留源数值精度，与 GT 五个小数指标最大绝对差为 4.84e-10；PySpark 输出九位小数，与 GT 数值完全一致。当前评测忽略行序，仍使用旧 number 规则及 Date/volume/Row key；三次通过不能证明这些规则已合理。

问答暴露 simulator 一致性问题：pandas/PySpark 被告知使用 UTC，Ibis 被告知需求未指定时区；pandas/PySpark 被要求按 Row 升序，Ibis 被告知需求未要求排序；PySpark 被告知输出九位小数，Ibis 被告知没有保留原始精度的要求。上述 UTC、排序、精度需先确定语义，再同步完整需求/KB，不能自动把 reference 默认行为升级成要求。pandas/PySpark 代码遇到重复 Row/指标会报错，未实现完整需求的取首值规则；当前输入无重复，正式通过不覆盖该行为。

证据：`case_011/runs/interact/codex_gpt-6-astra/{pandas,ibis,pyspark}/r001/` 下的 result.json、workspace/solution.py、输出和 logs/interaction.jsonl。下一步先决定时区、精度和日期字面格式，修订 key/类型/容差并做正反例；如修改澄清资产，需新建 generation run。


## 2026-10-08：060–067 迁移、独立核算及三后端 interact

按用户要求先完成 060–064，再完成 065–067，供后续逐题人工审核。资产已导入标准目录，输入/GT 原样保留；来源及导入哈希分别保存在本地 `import_cases_060_064.json`、`import_cases_065_067.json`。完整审核入口为 [REVIEW_060_067.md](REVIEW_060_067.md)，逐题列明契约决定、改动和未覆盖分支。

固定 Docker image `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921`，Codex `gpt-6-astra` / low、interact、simulator `gpt-6-astra` / temperature 0，每次 timeout 1800 秒。每题先 pandas，再以 `20261008000 + case 编号` 为 seed 从 `[polars, ibis, pyspark]` 抽两个不重复后端。8 份 reference Docker 复现 GT；独立 CSV/Decimal 核算全部一致，82 项评分正反例、29 项共享 evaluator 单元测试通过。最终 24 次 generation/evaluation 均 completed，22 通过、2 失败；没有跳过或环境失败。

| Case | pandas | 另两个后端 | 关键决定 / 人工审核事项 |
| --- | --- | --- | --- |
| 060 | 通过 | Ibis / PySpark 通过 | 修公式排版及输入行数；Species/Trait key，九位小数精度；尾部空格保留需人工确认 |
| 061 | 通过 | Ibis / PySpark 通过 | LHSItem/RHSItem key；初始需求统一公开箭头格式，保留指标原公式 |
| 062 | 通过 | Polars / PySpark 通过 | Store/Category/Scent/Date key；金额精确、工日 integer；自定义展示排序不评分 |
| 063 | 失败 | PySpark 失败 / Ibis 通过 | pandas/PySpark 均漏 MONEY HEIST；完整需求的 Other 解释及尾部括号清理范围需人工确认 |
| 064 | 通过 | Ibis / Polars 通过 | 完整需求/reference 修正有效比赛行识别，零出场/90 分钟换入由数据覆盖 |
| 065 | 通过 | Polars / Ibis 通过 | Games OoP 沿用球员级总数；reference 修复不可解析比分归零分支 |
| 066 | 通过 | Polars / Ibis 通过 | 单行文本精确评分、空格保留；数字 scaffold 可选 |
| 067 | 通过* | Ibis / Polars 通过* | *来源完整需求下通过；原始增长率之差与 GT 贡献差定义冲突，契约待人工决定 |

配置改为显式类型，结果值移出业务 key。060/061/064 连续指标容差为 5e-10，依据 GT 九位小数；063 Rating 为 5e-13，依据十二位小数；065 均值为 1e-15，仅容纳当前小量级浮点表示误差；062 金额及 067 已舍入指标零容差。计数、排名和整数分钟精确比较，文本不 trim。所有最终行序不评分：原始 query 均未提出明确排序约束；062/067 的完整需求自定义顺序未伪装为字段字典序。日期按语义比较，不检查字面格式。

063 初版误将 Rating 容差设为 5e-10，pandas r001 后校正为 5e-13，旧 config/result/evaluation 保存在 `case_063_before_precision_review/`，仅重评同一原始 CSV；其余后端开始时已使用最终配置。失败原因不是容差：两份候选只去掉 `Money Heist (La casa de papel) (2020)` 最后一个括号组，漏掉 MONEY HEIST。其余十个 show 的 Rank/Rating 均与 GT 一致，但正式结果保持 ROW_COUNT_MISMATCH。Ibis 去掉连续括号组后通过。

067 修正两份 query 的明显 bps 单位错误为 1 bp = 0.01 percentage point，保持 ×10000 公式。独立算例确认原题与来源 GT 不是等价解释：Orange 的贡献差为 3.64，按香型自身增长率之差为 31.94；按未舍入贡献最后求差为 3.65。暂保留源 GT 并在私有 KB 明确输出专用贡献差公式，未改写初始 Outperformance 定义来掩盖冲突，不能标为业务契约已审核完成。人工决定后如改 query/full/KB，必须新建 generation run。

问答中独立问题打包有时被要求拆问；所有计划运行均完成。063 Ibis simulator 无依据补充 output_01 Device 排序，评估未采纳；060 pandas 的保留物种尾空格规则来自原资产解释，应人工复核。完整问答、候选代码与 CSV 均保留于 `case_XXX/runs/interact/codex_gpt-6-astra/<backend>/r001/`。本地 `interact_validation_060_067.json` 汇总逐次结果/问答，`final_verification_060_067.json` 证明冻结 CSV 按最终配置重验状态一致、源资产/输入/GT 未改、可见输入哈希一致且生成阶段未挂载私有资产。研究者 reference 验证与真实生成容器分离。


## 2026-10-09：067 增长率之差对照版本（验证待完成）

按用户要求，将原 `case_067/` 整体移动至 `case_067_bak/`，包括旧贡献差版本的三个 interact r001；备份文件哈希全部核对未变。新 `case_067/` 不复制旧 runs，沿用原 metadata case_id。原有审核索引中的 067/r001 路径指旧版本，现应查 `case_067_bak/runs/`；新目录未来的同名 r001 属于新版本，不得混淆。

新版本只改 query_full、amb_kb、reference 和 output_02 GT 的 Outperformance：分别以各组该香型的 March 销售额为分母算增长率，使用未舍入增长率求差，最后 HALF_UP 两位小数。query、输入、metadata、evaluation config、output_01 GT 和 output_02 两个贡献列均未改变。七个分母均非零，不额外定义零分母业务规则。

新 Outperformance 按 Rose/Orange/Lime/Coconut/Watermelon/Pineapple/Jasmine 顺序为 -10.11、31.94、-4.19、4.48、-5.66、2.16、175.17。GT 使用标准库 Decimal 重算并用精确 Fraction 独立确认舍入；GT 自比通过，旧贡献差 GT 被当前配置拒绝。此次还没有执行更新后的 pandas reference，也没有真实 interact：本会话沙箱拒绝访问 Docker socket，宿主 Python 无 pandas。未以独立核算代替 reference 或模型执行结论。

本地证据为 `curation/output/067_growth_variant/validation.json`。终端运行 `bash PrepBench/curation/run_case_067_growth_variant.sh` 会先在原固定 image 中执行 reference 并正式比较 GT，再依次运行 pandas/Ibis/Polars interact，保留失败结果；不改共享 runner。待三次运行后需核对问答及正式 result/evaluation，再补最终结论。


## 2026-10-09：067 新版采用及补充验证

用户确认采用新版增长率差定义，旧贡献差版本保留在 `case_067_bak/`。新版 reference 已在原固定 Docker image 中重放并通过当前 GT，报告为 `reference_067_growth_check.json`。本会话新增 interact：pandas/r002（122.65 秒、1 次澄清）、随机抽中的 Polars/r002（92.45 秒、2 次澄清）及 PySpark/r001（101.86 秒、2 次澄清），三个后端的两份输出均通过。模型为 Codex gpt-6-astra / low。两次补充后端抽样使用系统随机源，从 pandas 之外的三个后端无放回抽取，抽样结果和实际 run 路径记录于此；没有追溯性筛选通过运行。旧版分数不得与新版混合；上节“验证待完成”描述的是当时状态。

Polars/PySpark 均询问 Outperformance 定义，模拟用户明确回复同香型内未舍入增长率之差。两者第一轮均有展示格式与排序打包的问题被要求拆问，后续完成。通过固定输入评分不代表未覆盖业务边界已通过，也不消除模拟用户单条 ref 无法完整表达复合答案依据的局限。


## 2026-10-09：068–070 导入与三后端 interact

已完成任务资产、显式评估配置、参考解 Docker 重放、独立核算及 9 次真实 interact。详细记录见 [REVIEW_068_070.md](REVIEW_068_070.md)，来源/导入哈希见 `import_cases_068_070.json`，独立核算及 42 项评分正反例见 `diagnostics_068_070.json`。29 项共享 evaluator 单元测试通过；070 的大小写标签和非粗体小写标题另有 2 项参考解扰动检查。输入及 GT 与来源逐字节一致；宿主私有资产未挂入生成容器。

068 的源题混合随机生成要求和公开的完整固定销售表，源 reference 直接返回固定值。此次明确整理为固定数值转长表，保留公开数值及全部输入，删除随机生成与固定答案并存的矛盾；不能把通过计作随机生成或澄清能力。069 补明答案 token trim、pair 粒度及 dense rank；070 补明源 reference 已有的 Ł→£ 修复，并让 Battle/Victors 大小写匹配与源完整规格一致。key 分别为 Company/Scent/Month、Name、Battle；068 Sales 精确比较，069 分数/排名 integer，070 日期语义比较、文本精确。没有将源全列 key 或旧 number 2% 容差直接沿用。

按每题 seed=20261009000+编号冻结无放回抽样：068 pandas/PySpark/Ibis 均通过；069 pandas/Polars/PySpark 均通过；070 pandas/Ibis 通过、PySpark 失败。模型 Codex gpt-6-astra/low、interact、原固定 Docker image，timeout 1800 秒。所有尝试均为各后端 r001，9 次生成和评分 completed，8 次 passed、1 次 failed。详细问答、时间和挂载审核保存在 `interact_validation_068_070.json`。

070 PySpark 仅 Edgehill Description 将两个空格合并为一个，63 条 key 和其他字段完全一致；当前完整规格要求保留内部空格，因此保留 VALUE_MISMATCH，未改候选或放宽评分。是否将此空格区别作为业务正确性要求需单独审核。该 agent 没有针对 Description 内部空格提问，不能说它忽略了直接澄清；Ibis 则明确询问并保留内部空格。Ibis 4 次 ask 日志中最后一次是额度用尽，只有 3 个处理轮次。070 simulator 对“清洗后仍重名”补充保留记录的建议缺乏明确规则支持，当前输入的完整标题唯一，故不影响这次结果。


## 2026-10-10：072 按用户要求将正式绝对容差改为0.001

Sales与3rd Party Sales的abs_tol由5e-10改为0.001，rel_tol保持0。只改evaluation/config.json；query、query_full、KB、reference、输入、GT和候选CSV不变。此处覆盖前文“精度口径待决定”的状态：当前按用户选择接受千分之一销售额的数值差异，不再严格验证九位小数舍入结果。原配置及三个run的evaluation/result报告备份在本地 `curation/output/07x/072_before_tol_0_001_20261010_221438/`。

使用正式evaluate.py重评现有pandas/Ibis/Polars r001，三份49行输出全部通过；本次仅重评，没有重新生成或重新调用interact。之前Ibis/Polars因1e-9差值失败的原报告保留在备份目录。存量reference输出也通过；两个字段分别验证±0.001通过、±0.001001与+1拒绝，10项数值边界检查符合预期。报告见本地validation_072_tol_0_001.json。历史interact_results_072_073.json仍表示原5e-10规则下的结果；当前正式状态以各run更新后的result.json及本段为准。未提交或推送。


## 2026-10-10：074 导入与验证

**状态：导入、固定镜像reference、独立核算及三后端真实interact全部完成并通过。** 来源 ../prepbench/data/case_074、reference/solutions/case_074/solution.py、src/evaluate/gt/case_074。输入和GT保持原字节，来源与当前版本哈希分别在本地curation/output/07x/import_074.json、current_assets_074.json。metadata为sports、两表11/1列。query将Excel双sheet及Tableau背景改为两个实际CSV；query_full修复单文件表述，明确scaffold是可选辅助、Games保留原罗马数字、Host原文保留、无最终行序要求，KB同步输出规则。reference仅修改入口路径，计算逻辑不变。没有公共Python模块变更。

每行是一届日期完整的奥运会。以Games为key，Start/End Date按日期语义评分（补%m/%d/%Y，接受ISO等价日期，不强制M/D/YYYY字面格式），Games/Host精确文本且无null别名，Nations/Sports/Events为精确integer，最终行序不评分。Host现有28条都含不间断空格，题目未要求修改Host文本，沿用原样保留；不会自动改空格或去标点。

固定镜像 sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921 中执行reference，28行与GT一致。独立以符号之和减去两倍减法项计算Roman，按1896+4*(n-1)算年，再用datetime构造真实日期，输出ISO与GT比较通过。34条输入剔除VI/XII/XIII/XXXII/XXXIII/XXXIV六条缺日期记录；8条补起始月份，20条跨月且保留明确起始月份。15项检查通过：reference、GT自比、独立结果、乱序接受、重复行拒绝、三个计数等价.0接受/+1拒绝、跨月错误/取消届次导致年份位移/Host NBSP替换/Games输出阿拉伯数字拒绝。证据为prepare_verify_074.py、validation_074.json及reference_074执行/评估报告。原reference对未知月份或非数字日会抛异常且没有验证日历有效性，现有非空日期均合法，因此未据此宣称覆盖所有坏日期。scaffold原有10行，reference不依赖它；本题Roman及日期主要通过apply调用Python函数，另有列算术、布尔过滤、投影和类型转换，属于混合文本处理任务。

抽样seed=20261010074，选Polars/Ibis，加pandas。Codex gpt-6-astra/low、simulator gpt-6-astra/temperature 0、上述固定镜像、1800秒上限；每个后端新建r001。三组generation均完成、正式evaluation均通过，每组28行；结果如下。未提交或推送。


| 074 Backend | Run | 正式评测 | ask次数 | agent秒数 |
|---|---|---|---|---|
| pandas | r001 | 通过 | 2 | 73.35 |
| polars | r001 | 通过 | 1 | 69.72 |
| ibis | r001 | 通过 | 1 | 72.08 |

三组均澄清Games保留罗马数字、1896起每届递增四年且不跳过停办届次、缺失日期不外部补齐、Host保留原文含NBSP。pandas使用Roman转换map、str.extract、日期向量化构造及dropna；Polars使用字符计数/减法对修正表达式、正则列提取和日期转换；Ibis使用scaffold展开罗马字符、按位置提取相邻字符比较并聚合，再解析日期。问答与正式报告见各自runs；汇总见本地interact_results_074.json。运行期间资产哈希未变化。


## 2026-10-10：075 导入与验证

**状态：资产导入、固定镜像reference、独立核算及三后端真实interact全部完成并通过。** 来源为../prepbench/data/case_075、reference/solutions/case_075/solution.py及src/evaluate/gt/case_075。输入与GT原字节保留；来源哈希和当前版本哈希在本地curation/output/07x/import_075.json、current_assets_075.json。metadata为business，三表6/2/3列，100位attendees、90条公司经理映射、4条汇率。query将Excel多sheet改成实际CSV路径，两份query明确明细/国家汇总粒度。query_full删除仅扩展需求增加的output_02排序，KB同步；主表原query要求的经理分组排序保留。reference仅修复入口路径，不修改计算或默认输出顺序。无公共模块改动。

公司名从Email的@后首个点之前提取，忽略大小写关联且输出保留AM表公司大小写。价格按100 GBP乘当地汇率、截断为整数；GBP固定100。Full Refund为负、Credit Note/No Refund为正，其他类型0。主表key为Email（当前100个唯一电子邮件，作为参会者联系身份；重复key仍按行重数评估），Order/Ticket Price Local为integer，其他字段精确文本；允许缺经理/公司/Order/Refund Type的空字符串。经理按人数降序/姓名升序编号，主表按Order升序、缺失置末验序；同经理客户可任意排列。汇总key Country/Currency，Money Gain/Loss精确integer，忽略最终行序。

reference在固定镜像sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921执行，100/8行输出与GT一致。独立字典关联、Decimal乘汇率、Counter经理计数和分国家累加复核通过。经理人数Tom30/Jonathan25/Jenny24/Carl21，Order依次1/2/3/4。票价USD125/EUR110/MXN2837/GBP100/CAD170；35位Full Refund、32位Credit Note、33位No Refund。15项检查通过，包括主表逆序拒绝、同经理内部倒序接受、汇总倒序接受、重复客户/错误整数/公司大小写/收支符号拒绝及整数.0等价接受。证据prepare_verify_075.py、validation_075.json、reference_075执行/评估报告。现有数据无经理人数并列、缺经理、缺非GBP汇率、未知退款类型，也未触发带小数当地票价截断；这些规则未由当前数据充分覆盖，不新增样本来冒充原任务覆盖。

抽样seed20261010075，Ibis/Polars加pandas；先运行pandas，再启动两个后端。模型gpt-6-astra/low、simulator gpt-6-astra/temperature0、固定上述镜像、1800秒上限，各组r001。三组均完成生成并正式评估通过，主表100行且order_status=passed、汇总8行。未提交或推送。


| 075 Backend | Run | 正式评测 | ask次数 | agent秒数 |
|---|---|---|---|---|
| pandas | r001 | 通过 | 1 | 79.35 |
| ibis | r001 | 通过 | 1 | 95.62 |
| polars | r001 | 通过 | 1 | 74.90 |

三组均一轮澄清获取退款符号、按参会者行数而非公司数统计经理客户数、Order是经理序号而非客户流水号，以及乘汇率后截断整数的正确规则。现有数据下未发现simulator错答或资产矛盾。原问答、代码、CSV和正式报告在各自runs，汇总在本地interact_results_075.json；输入/GT原字节及运行前资产哈希已复核。


## 2026-10-10：076 导入与验证

**状态：资产导入、固定镜像reference、独立核算及三后端真实interact全部完成并通过。** 来源../prepbench/data/case_076、reference/solutions/case_076/solution.py及src/evaluate/gt/case_076。输入和GT原字节复制；来源/当前哈希见本地curation/output/07x/import_076.json、current_assets_076.json。metadata为weather，三表1/1/2列，input_03第二列无标题且全空。完整需求明确仅input_02/03的Data为输出来源，保留input_01四条day-part原始记录供澄清范围，不从资产中删除。query新增固定Forecast Type标签与输出粒度；query_full移除无关的填写姓名提示，补明input_01不入输出、忽略input_03空列、降雨行不参与温度提取、保留标签及无最终行序要求；KB同步。reference只修复入口路径，不改算法。

输出每个forecast entry一行，key为Forecast Type/Date or Time，不强制key唯一、保留重复行重数；文本精确，日期/时间列是Now/Today/Wed 06/0:00等原标签，不能猜年份或归一化为时刻。四个数值字段为nullable integer，CSV空字符串为null，不能替换为0；行序不评分。小时5行+每日5行=10行，Today只填Min Temp=3，其他4个每日最低温均为负数。所有10条有效记录都有降雨概率；空Data、缺降雨、缺温度分支未由当前有效记录充分覆盖。原reference会跳过只有一行的非空hourly Data，而query_full称每个非空Data输出一行，现有Data均多行，不改输入或算法，记录未触发的不一致。

固定镜像sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921执行reference通过。独立按度数符号/百分比文字拆解并处理Today，同GT一致。12项检查通过，包括GT自比、乱序接受、重复行拒绝、Today max/min错位、负号丢失、null变0、概率除100、概率误当温度和时间标签变更拒绝，整数4.0接受。证据prepare_verify_076.py、validation_076.json、reference_076执行/评估报告。

此reference主要是iterrows+Python正则与列表构造，pandas用于读表和输出类型转换，DataFrame操作偏少；本轮按用户要求迁移并验证，不能仅凭通过宣称具有复杂DataFrame workload。抽样seed20261010076，Polars/Ibis加pandas，先pandas后两个后端；模型gpt-6-astra/low、simulator gpt-6-astra/temperature0、固定上述镜像、1800秒上限，各组新r001。三组generation完成、正式evaluation均通过，各10行。未提交或推送。


| 076 Backend | Run | 正式评测 | ask次数 | agent秒数 |
|---|---|---|---|---|
| pandas | r001 | 通过 | 2 | 110.34 |
| polars | r001 | 通过 | 2 | 70.89 |
| ibis | r001 | 通过 | 2 | 85.34 |

三组均通过两轮澄清获得输入范围、原标签保留、温度整数/百分比0–100、null而非0和Today仅最低温的规则；第一轮多主题问题被拒后拆分重问，无错误回答或网络失败。候选实际使用后端字符串表达式、条件投影和合并，非照搬reference逐行正则，说明可以表达为DataFrame任务，但10行数据仍属于简单文本清理。pandas候选没有显式过滤空Data单元格，当前大量空物理行由read_csv跳过，不能据通过宣称覆盖真正空单元格分支。候选、交互及正式报告在各自runs；本地汇总interact_results_076.json，资产与输入/GT哈希已复核。

## 当前 worktree 本地审核历史（与 main 的独立运行分开解释）

## 2026-10-10：删除 067 旧版本地备份

按用户要求，确认新版 case_067 资产齐全、参考解已保存输出通过当前 GT，且 pandas r002、Polars r002、Ibis r001、PySpark r001 的生成均完成、公开资产哈希匹配、原候选按当前配置重评均通过后，删除当前 worktree 未跟踪的 `case_067_bak/`（含旧版任务和旧运行记录）。新版及其运行记录保留。以上是已有输出复核，不是新生成；首次结果头表仍保留新版 Polars r001 失败。本文此前的备份路径是历史记录，不再指向现存目录。


## 2026-10-10：078–079 迁移及首次 interact

导入 078 店长向下填充、079 周三至周二库存损耗/利润排名任务，来源 `../prepbench`，输入和 GT 逐字节保留。来源及导入哈希见本地 `import_cases_078_079.json`，完整审核见 `REVIEW_078_079.md`。078 删除 Tableau Script Step 限制，改为 DataFrame fill-down；完整需求明确按输入行序填充和清理列名；reference 将 dropna 限于三个必需字段，修复额外无关列有空值时误删有效行的问题。079 删除过时数据编辑提示，修复 KB 原文引用、补充自然语言解释，保留题目明确的 Profit=Weekly Sales−Cost×Waste 公式，不额外扣已售成本。两份 reference 主入口改为 case 根目录 inputs/output。

078 用 Store 作为 key，目标值 integer；079 用 Scent 作为 key，排名 integer，Total Profit abs_tol=1e-9、rel_tol=0，仅容纳浮点表示误差，一分钱偏差拒绝。两题不评物理输出行序，078 填充顺序仍是业务逻辑。独立 CSV/Decimal 核算与 GT 一致，Docker reference 重放通过，18 项评分正反例及 29 项共享 evaluator 测试通过。078 的参考解另用合成输入验证前导空经理、后续新增经理、缺少必需字段和无关空列；不将参考解分支验证当作模型覆盖。079 实际为 17 周×5 香型、85 个完整七天分组，无缺失 lookup/order、负 waste 或并列利润，相关边界未覆盖。

Codex gpt-6-astra/low、interact，固定 image sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921，timeout 1800 秒。每题先 pandas，再以 seed=20261010000+编号从 polars/ibis/pyspark 无放回抽两种：078 PySpark/Polars，079 Ibis/Polars。六次均为当前 worktree 首次 r001，generation/evaluation 全部 completed 且 passed；没有重试筛选。头表仅采用这些首次结果。资产和源哈希核对通过，生成容器未挂载私有 case 材料，详细路径/问答/计时见 `interact_validation_078_079.json`。

078 pandas 的模拟用户把“输出 integer”扩展为小数目标截断及非法数值转换失败；完整需求没有明确这两个边界，当前输入也未触发，不将这些回复升级为已审核业务规则。078 Polars/PySpark 正确确认按 CSV 输入顺序而非 Row ID 排序填充。079 pandas/Ibis 确认不额外扣已售成本，Ibis 确认每周订单量分别适用于每个香型。079 的并列利润排序缺少固定 tie-breaker，当前无并列，不声称已验证。


## 2026-10-10：077 源资产预审，待任务契约决定

已在独立 Docker 容器重放源 reference，三表按无序行多重集合与源 GT 精确一致（1242/28/33202 行）。尚未导入 runtime case_077，也未运行真实 agent。审核发现：20 个 host 日期的 GT 按非 ISO 年-日-月解释；Cycling Road→Cycling Track 及按年份/事件合并规则未完整写入完整规格；项目名称存在额外空格/x/×规则，唯一对齐诊断子集中有209条田径记录与基础文字替换不同。完整规格的排序要求与 GT 行序也不一致。两条英国特殊国家名称实际属于2016年，和两条Ivory Coast一样无法通过精确国家表补全，按完整需求即可删除；不能误判为无依据删除2012奖牌。

详细审核见 `REVIEW_077.md`，源哈希、差异样例及重放输出保存在本地 `curation/output/077_audit/`。保留源资产，暂不把未公开规则造成的差异记作 agent 失败；需先决定保留源约定补全规格，还是统一规则并重建真值。077 尚无 interact 结果，不填通过/失败。


## 2026-10-11：077 源规则诊断 interact 首次运行

按用户要求导入 case_077，原始 query/query_full/KB/reference/input/GT 不变；config 改为显式精确文本、整数和日期类型，汇总 key=Country/Year、host key=Games/Year、明细全字段 key，行序忽略。源 reference 已存输出通过该配置。此为待审核源规则的诊断任务，并非契约已定稿。Codex gpt-6-astra/low、pandas、interact r001，生成 completed，约116.33秒、3次澄清；正式评估失败 KEY_MISMATCH。output_01（1242行）和output_02（28行）通过，output_03（33202行）失败，首个差异为2016 Usain Bolt 100m 与候选100 m。模拟用户明确要求100 metres→100 m、保留空格，故此差异属于澄清/真值约定冲突，不能直接当作 agent 计算错误。源资产、候选和正式报告未作修补。详细差异见 `case_077_pandas_r001_diagnosis.json`，导入身份见 `import_case_077_diagnostic.json`。


## 2026-10-11：077 Event 空格手动修正诊断

按用户要求复制 pandas interact r001 的三份输出，仅在副本 output_03 的 Athletics Event 中删除数字与米单位 m 之间的空格（不处理 km），共改变239行。使用原 evaluation/config.json 和原 GT 重评，三份表全部通过：1242/28/33202行。证据为 `curation/output/077_event_spacing_recheck/evaluation.json` 和 `summary.json`。哈希确认原候选CSV、result.json、正式evaluation.json均未改变；头表仍保留首次失败。这是手动修正后的诊断通过，不是新的模型运行或原始结果通过。

## 2026-10-11：077 田径米单位空格规则 v1.1

按用户确认，田径 Event 中数字与米单位 `m` 在所有年份统一保留一个空格，接力距离亦如此；`km` 和接力 `x/×` 规则不变。已同步 `query.md`、`query_full.md`、`amb_kb.json`、reference，并将 metadata 版本设为 1.1。修改前资产与哈希存于本地 `curation/output/077_before_metre_spacing/`。输入、evaluation config 及 output_01/02 的 GT 值不变；重放 reference 后 output_03 GT 的 33,202 行中有 2,343 行仅 Event 改变。独立字段核对、奖牌汇总核算、Docker reference 重放、正式 evaluator 自检，以及紧凑、双空格和错误距离的反例检查均见 `curation/output/077_metre_spacing_v1_1/validation.json`。首次 pandas interact r001 及正式报告原样保留，头表仍记首次失败；新版 r002 的结果另记。主办日期与自行车/其他项目命名的完整契约仍待单独审核。

新版 pandas interact r002（Codex gpt-6-astra/low）生成 completed，130.15秒，3次澄清共11个问题；正式 evaluation completed、passed=false，KEY_MISMATCH。output_01/02 通过；output_03 的3,831条田径记录均符合新版米单位空格规则，但303条自行车 Discipline 为 Cycling Road（GT 为 Cycling Track），另9条田径保留20kilometres/50kilometres walk（GT 为20km/50km walk）。仅在内存应用这两类替换后全表多重集合与GT一致，未改候选或正式结果。模拟用户被问到精确映射时仅给出 Track cycling/Road cycling→Cycling Track，未披露 reference 更广的映射；紧贴数字的 kilometres 替换在 query_full 有规定，但本次未问到且整词替换漏掉。第二轮3个问题被拒绝，第三轮拆分再问。详细诊断见 `curation/output/077_metre_spacing_v1_1/r002_diagnosis.json`、`REVIEW_077.md`。共享 evaluator 29项测试及 git diff --check 通过；不将本次记录为修复后整题通过。

## 2026-10-11：077 v1.1 随机追加两个 backend interact

按用户要求以 seed=20261011077 从 polars/ibis/pyspark 无放回抽中 PySpark、Ibis，均为当前 worktree 对应 backend 首次 r001，不重试。使用 case_077 v1.1、Codex gpt-6-astra/low、interact、timeout 1800秒和固定 image sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921。PySpark 生成 completed，121.71秒、2次澄清/7个问题；Ibis 生成 completed，301.19秒、3次请求/6个问题。两者正式 evaluation completed、passed=false，均在 output_01 首先报 VALUE_MISMATCH。头表更新两者首次失败；pandas 仍保留旧版 r001 首次失败，不能把三个单元格视为同版比较。

为避免正式 fail-fast 掩盖后续文件，使用临时单文件配置和原样候选副本分别诊断，不覆写正式评估：两者 output_01 均仅有992个缺失奖牌单元格被写成0（Gold 426、Silver 310、Bronze 256）；output_02 均有20个日期单元格不同（Start Date 6、End Date 14）。两者模拟用户明确要求 ISO-looking 日期按年-月-日解析，与 reference/GT 的年-日-月冲突，属于澄清/资产冲突。PySpark output_03 报 READ_ERROR，CSV 引号转义不符合 evaluator 读取要求，明细内容未通过检验；Ibis output_03 的33,202行正式规则单文件诊断通过，其澄清获得了 road/track 均归 Cycling Track 的映射。未修改任务资产、生成代码或候选输出。运行前后资产哈希及公开资产身份一致；已检查生成容器挂载，私有资产未暴露。抽样、资产哈希、完整结果和逐表诊断见本地 `curation/output/077_metre_spacing_v1_1/backend_plan.json`、`backend_results.json`、`*_r001_per_file.json`。

## 2026-10-12：071–076 筛选与迁移

按用户要求排除 DataFrame 处理很少的 workload：076 主要逐条解析天气文本，随后组装/union；074 主要罗马数字解码与逐行日期字符串转换；071 的实际输入只有一个罗马数字，scaffold/join/sum 是标量转换的表格式实现。这是任务范围筛选，不是运行失败；三题在当前 worktree 尚未导入，故不创建 runtime case、不安排模型运行，上游原件不删。来源哈希、范围判断见 `import_cases_073_076.json`、`import_cases_071_072.json` 与相应 REVIEW。073 虽然源参考解使用循环，但业务包含多表关联、条件匹配、去重和分组选优，因此保留；075 和072也保留。

075 将 Excel 多页签描述改为实际 CSV 文件；保留源定价和退款符号约定。完整需求/KB 删除公开题面未要求的汇总表物理排序，客户经理分组顺序仍按题意检查：Order 升序、缺失最后，组内可交换。key=Email 与 Country/Currency，金额/排名均精确整数。独立 CSV/Decimal 核对100人、4位经理（Tom30/Jonathan25/Jenny24/Carl21）和8组国家币种汇总一致；当前没有未匹配经理或人数并列。参考解只改主入口路径，GT不变。

073 补明第二物理行才是表头、banner/footer非数据、站点名和Skill周边空白需清理。完整需求/KB 明确选择完整站点行、无适合站点者不输出，reference由groupby.first改为排名后按Name保留整行，防止跨站点拼接非空字段；当前GT不变。独立集合匹配核对16站点、4人，候选数Tom2/Jenny1/Carl7/Jonathan11，四个最优结果唯一且与GT一致。key=Name，Rating零容差数值，其他文本精确，不评分输出行序；无候选、缺失季节、冲突重复行及完全并列边界未覆盖。

072 保留两阶段匹配：精确ID关联后，同香型构造候选，按差额排序，先按第三方ID去重，再从保留下来的记录按内部ID去重，不回填、不做全局最优指派。补明精确匹配取内部Scent，修正KB引用不存在的pairs_filtered为pairs_join，reference只改主入口。独立Decimal核对20条内部/47条第三方、145个候选，输出49行（Matched5/Matched on Scent13/Unmatched - Internal2/Unmatched - 3rd Party29），差额无并列。key=ID/3rd Party ID，Sales abs_tol=5e-10、rel_tol=0，依据完整规格小数后9位的半个末位；GT与原值最大差恰为5e-10，数值评分不强制字面格式或特定舍入算法。stable tie的跨后端候选顺序仍未覆盖。

三题输入和GT均逐字节保留；固定Docker镜像重放reference全部通过；独立核算及49项定向评分检查通过（07522/07314/07213），共享evaluator29项测试通过。每题先pandas，再用seed=20261012000+编号从Polars/Ibis/PySpark无放回抽两个，本批三题均抽中Polars/Ibis；Codex gpt-6-astra/low、interact、固定image sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、timeout1800秒。首次r001结果完整保留，不重试筛选。最终结果在后文追加。

073与075的pandas/Polars/Ibis首次r001全部通过，generation/evaluation均completed。073耗时104.92/108.47/86.60秒；075耗时106.77/92.71/144.41秒，各一次澄清。资产身份及生成挂载allowlist核对通过，私有资产未挂载，详细问答及路径见`interact_validation_073_076.json`。075三次均获得Credit Note为正、票价截断整数、经理分组排名口径；073三次均获得三个匹配条件同时满足、只选一条、保留站点完整列表的规则。完全并列时回复keep_first，但未指定额外候选顺序，当前无此边界。

072最终首次结果：pandas r001通过（99.54秒、1次澄清）；Polars r001失败（139.57秒、2次澄清），Ibis r001失败（138.33秒、2次澄清），均生成/评测completed，失败为VALUE_MISMATCH。独立逐键核对：49条匹配/未匹配关系、状态、Scent全部正确，Polars仅2个、Ibis仅3个数值单元格与GT相差1e-9；均为小数后9位舍入中点，GT和候选距原始值都是5e-10。例如78530.3866906395，GT为78530.386690639，而Polars/Ibis为78530.386690640，精确HALF_EVEN/HALF_UP都支持后者；21304.1041794475同类。Ibis另将70989.4678953545舍入到70989.467895355，GT/HALF_EVEN为70989.467895354。源GT包含二进制浮点舍入影响，不能当成严格十进制HALF_EVEN标准。当前以GT为中心的5e-10容差无法同时接纳两个相反半末位选择，题面未规定中点策略，属于精度契约待决而非ID匹配错误。本轮不为通过而改GT/容差，不重试，头表保留首次失败；证据见`case_072_rounding_diagnosis.json`。两次非pandas均拆分被拒的多主题问题后取得精度要求；回答认可内部输入行序后第三方行序处理并列，当前无差额并列，未据此宣称覆盖。

本批完成071–076：保留072/073/075，排除071/074/076；九次首次interact共7通过、2失败，PySpark未抽中。`interact_validation_073_076.json`与`interact_validation_071_072.json`记录全部来源/导入/运行公开资产哈希一致及生成挂载隔离核对；上游六题资产未变。未提交Git，未修改既有077或其他任务资产。

## 2026-10-14：077 v1.2 公开日期格式与自行车归类

按用户确认，将日期格式和完整Cycling归类规则同时写入query、query_full和KB。斜杠主办日期明确MM/DD/YYYY，年份开头明确YYYY-DD-MM，忽略时间部分；输出DD/MM/YYYY，Year取Start Date。未把reference的日期fallback防御分支升级为业务要求。独立解析全部56个日期（34个斜杠、22个年份开头）及Year，与现有GT一致。

Cycling规则直接公开：仅Sport=Cycling，Discipline包含四种road/track变体，或Year≤1992，或Event包含road race/time trial时归Cycling Track，文本模式忽略大小写；其余保留其他明确重命名后的Discipline。替换query_full中不完整映射与无条件保留BMX/Mountain Bike的冲突描述，KB同步当前reference的完整条件。任务版本1.2，输入/reference/GT/config未改，历史运行未改。此版公开了此前需澄清的规则，不能与v1.1作为相同query条件比较；尚未运行v1.2 interact，头表仍保留历史首次结果。备份/哈希及验证见本地curation/output/077_explicit_dates_cycling_v1_2/。其他Event命名及源排序约定仍有此前记录的审核项，不能据此宣称整题完全定稿。

## 2026-10-14：恢复071、074、076并测试两个随机后端

按用户确认恢复三题，撤销此前排除决定。不能仅因源reference使用循环/apply就否定表处理价值：071覆盖字符展开、lookup join、相邻值和聚合（实际仅一个输入）；074覆盖派生列、日期解析、过滤和类型转换；076覆盖文本列提取、条件赋值、nullable整数和统一schema合并。保留此前排除日志作为历史记录。

输入和GT逐字节保留；reference只适配case根目录inputs/output路径。074将Excel页签描述改为CSV输入；076删去完整需求中无关的姓名/挑战登记提示。key分别为Number、Games、Forecast Type/Date or Time；数值均integer，074日期明确按%m/%d/%Y解析；文本精确，最终行序不评分。三份reference在固定Docker镜像重放通过，标准库独立计算复现1/28/10行，12项定向比较检查通过。071只处理一个罗马数字；074异常日期和076缺失/单行文本边界未据此验证，源reference的防御行为不代表完整契约已覆盖。

各题从pandas/polars/ibis/pyspark无放回抽两种（seed=20261014000+编号）：071 Ibis/PySpark；074 PySpark/Ibis；076 pandas/Polars。Codex gpt-6-astra/low、interact、timeout1800秒、固定image sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921。来源/导入哈希、抽样及验证见import_cases_071_074_076.json、interact_plan_071_074_076.json、reference_checks_071_074_076.json、validation_071_074_076.json。072资产和正式精度配置不变。

六次首次r001均generation/evaluation completed且passed；没有重试或修改候选输出。来源/导入/公开运行资产哈希一致，输入GT与上游字节一致，生成容器挂载allowlist核对通过，私有资产未挂载。完整路径、问答和挂载证据见interact_validation_071_074_076.json。

| Case | Backend | Run | 结果 | Agent秒 | ask calls |
| --- | --- | --- | --- | ---: | ---: |
| case_071 | ibis | r001 | 通过 | 104.58 | 3 |
| case_071 | pyspark | r001 | 通过 | 77.88 | 1 |
| case_074 | pyspark | r001 | 通过 | 90.46 | 1 |
| case_074 | ibis | r001 | 通过 | 98.24 | 2 |
| case_076 | pandas | r001 | 通过 | 106.07 | 2 |
| case_076 | polars | r001 | 通过 | 104.52 | 3 |

生成代码补充证据：071 Ibis使用cross_join、lookup left_join、lead窗口与sum聚合；074 PySpark用列表达式、正则、日期转换和filter；076 pandas使用str.extractall/unstack、条件赋值和concat，Polars使用str/list表达式、when和concat，未照搬reference逐行循环。支持保留三题的DataFrame测试价值，但固定小输入通过不代表复杂边界覆盖。

模拟用户边界记录：074 Ibis被告知保留输入行序，076两后端被告知小时在前/天在后并保留源行序，这些不是初始题面明确排序要求，本次未据此添加排序评分。071未映射字符规则有追问，实际输入没有此情况。076 reference对单行小时文本可能跳过，完整需求说每个非空Data单元一行；当前数据没有触发，作为未覆盖边界保留，不把本轮通过视为完全验证。未改072资产/正式容差，未提交Git。

## 2026-10-15：当前 worktree 合并 origin/main

合并 origin/main（8f1d930），保留双方历史审核记录。071–076在main中已有独立修订；本worktree合并前未提交的版本作为本地未提交改动恢复，未覆盖研究资产或runs。特别是072：main记录为0.001容差，本worktree仍按本会话要求保留5e-10，头表本地首次结果不被main另一组记录替换。以上历史记录按各自worktree和资产版本解释。重叠文件备份：/tmp/dfarena-before-main-merge-20261015-203113。

## 2026-10-15：071–079 对齐与复验

按用户确认采用 origin/main `8f1d930` 为 071–076 基线。071、072、074、075、076 的跟踪资产与该基线一致；073 只保留 reference 整行选取修正及 query_full/KB 对应说明：用 drop_duplicates 保留排名第一的完整站点行，避免 groupby.first 用次优站点的非空字段补入该行。输入、GT、配置不变。合成样例验证冠军 Wind Direction 为空、次名 East 时仍输出空；现有数据 reference 回放也通过。

072 采用 main 的 Sales/3rd Party Sales abs_tol=0.001、rel_tol=0，覆盖上一段合并阶段暂留 5e-10 的状态。历史正式运行报告不覆盖；复验另存。071–079 九个 reference 在固定镜像 `sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921` 中回放均通过。071–076、078–079 的 21 份本地历史输出按最终配置离线评测均通过（各 case 份数依次为 2/3/3/2/3/2/3/3）；这些候选生成时使用旧 query/KB，不能当作 main 新 query 的 interact 结果。此前本地排除或暂存 071/074/076 的记录保留为历史，当前三题均保留。

077–079 独立保留为待提交资产；078/079 本轮未修改资产。对齐前 071–079 完整资产及 runs 备份在 `curation/output/reconcile_main_20261015_215117/`。研究证据、验证脚本、最终资产 SHA256 清单在 `curation/output/reconciled_reference/`；reference 与历史输出复验报告为 `validation.json`，073 合成测试为 `check_073_whole_row.json`。研究回放允许读取 reference；正式 generation 仅挂载公开 query、inputs、独立工作目录和运行适配器，不挂载私有评测材料。共享 evaluator 单测 40 项通过。

## 2026-10-15：077 v1.2 三后端 interact 复验

保持 v1.2 资产不变，Codex gpt-6-astra/low、固定镜像及 1800 秒超时，新建 pandas r003、Ibis r002、PySpark r002，三组 generation 均 completed，但正式 evaluation 均失败。未修补候选或覆盖历史结果。下表为按原配置逐文件隔离诊断，不能替换正式整题评测：

| Backend / Run | output_01 奖牌汇总 | output_02 主办信息 | output_03 明细 |
| --- | --- | --- | --- |
| pandas r003 | 失败：1244 行，GT 1242 | 通过 | 失败：比 GT 多 4 行，另有内容差异 |
| Ibis r002 | 失败：空奖牌数写为 0 | 通过 | 失败：KEY_MISMATCH |
| PySpark r002 | 通过 | 通过 | 失败：KEY_MISMATCH |

pandas 对未能用 lookup 补齐 Code 的记录未按规则剔除；其最后一次追问超出三轮预算，未获答案。Ibis/PySpark 获得了剔除未匹配记录的澄清。三组日期表均通过，表明本次明确日期格式后这些运行没有再现旧日期错误；不意味着整题已审核完成。明细原始行多重集差异分别为 pandas 缺1217/多1221、Ibis 缺1437/多1437、PySpark 缺1867/多1867；样例涉及泳接力分隔符、Cycling `25 km` 与 `25km`、射击距离空格等。模拟用户的一些 Event 格式回答过宽或遗漏例外，仍需独立审核规则与 reference/GT 的一致性，不能把这些失败全部归因于 backend。没有为通过评测继续修改资产或重跑。

正式阶段记录及问答见各 run；逐文件评测、挂载检查与差异样例见本地 `curation/output/reconciled_reference/077_v1_2_results.json`、`077_detail_differences.json`。生成挂载不含 reference、GT、evaluation config 或 KB。头表保留历史首次结果，本段是 v1.2 新运行。077 待继续审核，078/079 现有资产与冻结输出复验通过。

## 2026-10-15：077 v1.3 简化游泳接力与射击 Event 格式

按用户确认，query 与 query_full 使用相同的两条简短规则：Use ` x ` between swimming relay distances, e.g. `4×100m` → `4 x 100m`；Standardize metre spacing in Shooting events, e.g. `50m pistol` → `50 m pistol`。reference 将游泳数字之间 x/× 统一为带两侧空格的小写 x，保留接力单位间距；删除射击枪种/次数的格式例外，统一数字与 m 间一个空格。KB同步。删除 query_full 三个输出的附加排序要求，KB明确无行序要求；evaluator原本忽略行序，配置不变。日期、Cycling、Athletics 规则不变。版本升至1.3。

固定镜像回放通过。独立使用CSV/正则从旧GT及原始泳接力文本推导新明细，与新reference多重集完全一致：766行Shooting、1434行Aquatics的Event改变；其他字段及行重数不变，output_01/02内容按无序比较不变，保留两份GT原字节。仅更新output_03 GT。该变化影响实验可比性，历史候选与报告未覆盖。备份、独立核对脚本、报告及哈希见本地curation/output/077_v1_3/。旧GT保存在before/evaluation/gt/。

新版 pandas interact r004 正式通过：三份输出分别为1242/28/33202行；generation completed，evaluation passed，3次澄清，agent进程169.03秒。模型gpt-6-astra/low，固定镜像同前。公开query/inputs及私有澄清资产在生成期间未改动；新GT在生成期间完成独立核对并写入，正式评测使用v1.3 GT（哈希见报告），未暴露给agent。旧运行报告未改写。此为v1.3新运行，不替换头表首次失败。40项evaluator单测与diff检查通过；本轮未重跑Ibis/PySpark。

## 2026-10-15：077 v1.3 Ibis / PySpark interact 复验

沿用gpt-6-astra/low、固定镜像sha256:904f17a0381e9478630368f0a9d5480340e5c1feda5def40e78311e18e62c921、1800秒超时；新建Ibis r003与PySpark r003，无重试。两组generation completed，正式evaluation均失败，保留原始候选和阶段报告。Ibis进程214.84秒、3次ask；PySpark186.54秒、4次ask（最后一次已超过三轮预算）。

| 后端 | output_01 | output_02 | output_03 |
| --- | --- | --- | --- |
| Ibis r003 | 失败：992个空奖牌数写为0 | 通过 | 失败：3行Cycling `25 km`写成`25km` |
| PySpark r003 | 通过 | 通过 | 失败：18行Event差异 |

逐文件隔离评测与完整CSV多重集比较确认：两个后端的明细非Event字段及行重数全部一致；本轮修改的游泳接力和射击格式没有剩余差异。Ibis汇总仅差Gold426/Silver310/Bronze256个空值写0，未询问空奖牌计数规则；其simulator明确说Cycling用紧连km，却遗漏25 km例外，因而3行差异涉及澄清不完整。PySpark的18行由同样3行Cycling空格、9行`20km race walk`误改`20km walk`、6行`marathon 10km`误改`10km marathon`组成；后两项与得到的保留措辞/紧缩空格澄清不符，是候选额外改写。25 km例外仍只见reference而未在query_full充分公开，不因新规则通过就宣称整题契约完整。

本轮未修改任务资产、未修补候选、未覆盖历史结果。生成前后全部资产SHA256一致，run公开资产哈希一致，挂载检查未发现reference/GT/config/KB泄露。证据：curation/output/077_v1_3/backend_assets_before.json、backend_results.json及check_backends.py；原始问答和正式报告见各run。连同pandas r004，v1.3当前结果为pandas通过、Ibis/PySpark失败；头表仍保留历史首次运行，不替换成新版结果。
