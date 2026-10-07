## interact 结果总览

下表是当前 benchmark 的初步审核实验表，不是最终 benchmark 分数。它用不同 backend 的 interact 结果暴露 workload 需求表述、simulator 澄清信息和 evaluator 验证规则中的问题：有些失败来自 agent 的真实计算错误，有些来自需求没有清晰表达，有些来自验证规则覆盖不足。因此，这些结果用于指导后续 curation 和资产修订，不能直接解释为 backend 能力排名。`通过/失败` 指对应运行时配置下 interact 生成后的 evaluator 状态；`跳过` 表示生成记录存在但评测未执行；`未运行` 表示目前没有该 backend 的 interact 结果。

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
| 050 | 失败（r001） | 失败（r001） | 失败（r001） | 失败（r001） |

001–006 采用 2026-09-27 首次运行的原始正式评测结果，来源为 `../dfArena/PrepBench/case_00X/runs/interact/codex_gpt-6-astra/<backend>/r001/result.json`；24 次运行均完成生成和评测。此处不采用更早的 `interact_legacy` 实验、后续 run、当前配置离线重评或 2026-10-04 修改题面后的复验结果。原始失败报告：002 Ibis 为 `KEY_MISMATCH`；004 pandas/Ibis/PySpark 为 `MISSING_COLUMNS`，Polars 为 `KEY_MISMATCH`；006 PySpark 为 `MISSING_COLUMNS`。

说明：030 的三个 r001 因模型网关额度不足而生成失败、评测跳过；表中采用后续 r002 状态。030–033 的详细记录见下文。034 的三个 `r001` 均通过当前配置，运行记录及日期字面格式、同日行序的未覆盖项见下文 034 条目；035–037 的运行记录见 `interact_validation_035_037.json`，038–039 见 `interact_validation_038_039.json`，040–044 见 `interact_validation_040_044.json`，045–049 的原始快照见 `interact_validation_045_049.json`。045 的 pandas 有 r001 跳过、r002 失败，表中采用最新 r002；048 的原始 r001 因模型网关额度不足而跳过，已删除，并将四个通过的 r002 归档为 r001（见下文）；049 的四个 r001 因模型网关额度不足而跳过，表中采用后续 r002 的正式评测状态。050 原 r001 四后端均因额度不足跳过，已删除；原 r002 均正式失败，现归档为 r001。该表按现有记录维护，后续重跑或补充 backend 时更新对应单元格。

# PrepBench 迁移与审核日志

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
