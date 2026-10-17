# 通用表格 evaluator

供 PrepBench、后续 LongDS/PandasBench 共用。任务目录保留自己的 `evaluation/config.json` 和 `evaluation/gt/`，此模块只读取 CSV 并评分，不运行 candidate 代码、不调用模型，也不修改输入资产。仅依赖 Python 3.10+ 标准库。

## 评估对象与代码组织

评估输入是已经生成的 candidate table (e.g., CSV)、事先准备并审核的 GT table，以及任务的 `config.json`。本模块验证表格结果是否满足配置契约，不验证 candidate 是否真正使用指定 dataframe backend，也不自动判断 query、GT 和配置是否一致。GT 的生成和配置标注需要由任务整理流程完成。

| 文件 | 职责 |
| --- | --- |
| [__main__.py](__main__.py) | CLI 参数、调用 evaluator、输出 JSON 报告及退出码 |
| [config.py](config.py) | 校验配置，转换字段规则和排序规则 |
| [normalization.py](normalization.py) | `normalize()` 规范化单元格，`equal()` 按类型和容差比较 |
| [evaluator.py](evaluator.py) | 文件检查、CSV 读取、key 对齐、内容与顺序检查、报告 |
| [tests/test_evaluator.py](tests/test_evaluator.py) | 协议边界和现有任务资产的回归测试 |

## 完整评估流程

### 可选 CSV 引号兼容

输出文件配置可显式设置 `"csv_quoting": "standard_or_backslash"`，报告使用 `dfarena-table-v9`，并在逐文件 `csv_dialects` 中记录实际采用的读法。默认仍为 `standard`。两侧资产均先按标准 CSV 严格读取；只有 CSV 语法解析失败时，才尝试把引号包围字段内的反斜杠转义双引号、双反斜杠转换后严格读取。未加引号字段及其他反斜杠保持原样。文件内容、列数、类型、key、行数和数值比较规则不变，原文件及其哈希不变。

标准读法成功时始终采用标准读法，不因内容与 GT 不符、字段数不符等原因切换解释。此项不自动识别所有 CSV 方言，也不修复缺失引号等损坏；两种读法都可能成立时不猜测作者意图。仅在逐题确认需要兼容时启用，并保留原评分报告与冻结输出重评记录。

```text
Evaluator.run()
  → 读取并校验 config，记录配置 SHA256
  → 检查 GT、candidate 和配置的 CSV 文件集合
  → 按配置逐文件调用 _evaluate()
      → _read()：读取两侧 CSV，并规范化所有声明字段
      → 如果要求顺序：_check_order() 检查 GT
      → 检查两侧行数是否相同
      → _align()：建立 GT 与 candidate 的 key 分组对应关系
      → 比较每个分组的行数和非 key 字段多重集合
      → 内容通过后，如果要求顺序：_check_order() 检查 candidate
  → 全部文件通过才设置 passed=true；首个失败即停止
```

文件扫描只包含输入目录直接包含的 CSV，不递归遍历子目录，也不把其他扩展名文件计入输出集合。配置文件名集合必须与 GT 一致；candidate 的 CSV 数量或名称不同会失败。

## 经审核的整数标签映射

整数列可单独配置精确标签映射，例如 `{"type":"integer","aliases":{"Tier 1":"1","Tier 2":"2"}}`。仅明确列出的完整标签参与映射，大小写与空格不自动清理；数字本身仍按整数规则解析，非整数拒绝。映射对 GT 和候选对称应用，先于 key 对齐与排序，因此排序按整数值比较。不能重映射已有数字表示、空值标签，或将标签映射到小数、其他标签或配置的空值。未启用的列行为不变。

启用整数标签映射的报告使用 `dfarena-table-v5`，可以同时使用下述整表替代答案。映射只表达已审核的同义表示；费用、计数、重复行和排序仍按原配置检查，不应借此合并不同业务身份。

## 经审核的文本标签映射

`text_exact`列也可配置`aliases`，将明确列出的同义标签映射到统一文本，例如`{"type":"text_exact","aliases":{"Recent fliers":"Recent Fliers (less than 3 months since last flight)"}}`。匹配完整原始文字，不自动截断括号、忽略大小写或清理空格；未列出的文字仍精确比较。两侧对称应用，重复行数量、其他字段及排序检查不变。映射目标必须直接是规范文本，禁止映射链、循环以及空值。启用文本映射时使用协议`dfarena-table-v6`；仅启用整数映射仍为v5。具体同义关系由每题配置声明，公共评分代码不包含任务专用类别。

## 经审核的整表替代答案

文件配置可以显式添加 `"alternative_gt": {"celsius": "celsius/output_02.csv"}`。路径相对于 GT 目录，必须指向该目录内的 CSV；替代文件通常放在子目录，不增加 candidate 应交文件数。该文件可以匹配原始 GT 或任一替代 GT，但必须整张表匹配同一版本，不能按行或单元格挑选答案。所有版本共用字段、key、类型、容差和顺序规则，不能借替代答案放松其他字段。

启用此项时报告使用 `dfarena-table-v4`，记录 `matched_variant`（原始版本为 `primary`）及各 GT 的相对路径和哈希。未启用的任务继续使用原有 v3 路径。全部替代 GT 都先检查可读性、字段类型和配置要求的顺序；即使原始答案匹配，损坏的替代 GT 也使评估报错。没有版本匹配时保留原始比较错误并附各版本错误。

此功能按输出文件选择版本，不提供跨文件联动约束。替代 GT 必须有任务契约依据并独立核验，不得从失败候选反推新增可接受答案。例如273明确允许两种温度单位，单位相关结果集中在一张输出表，基础信息表不随单位改变。

读取时保留 CSV 字段原始文本，再统一应用配置规则。缺失声明列、重复表头、行宽不一致都会失败；额外列及列顺序不参与比较。空白行跳过，只有表头的空表可以参与评估。规范化发生在生成 key 之前，且 GT 与 candidate 使用相同规则，因此格式不同但语义等价的日期、整数等可以对齐。非法表示报错，不作为普通缺失值继续比较。

## 调用

从 dfArena 根目录执行：

```bash
python -m evaluation \
  --gt-dir PrepBench/case_001/evaluation/gt \
  --cand-dir PrepBench/case_001/runs/clarified/codex_gpt-6/polars/r001/workspace/outputs \
  --config PrepBench/case_001/evaluation/config.json \
  --report PrepBench/case_001/runs/clarified/codex_gpt-6/polars/r001/evaluation.json
```

退出码：通过为 0，评估失败为 1，命令行参数错误为 2。`--report` 可省略，JSON 总会写到 stdout。报告不得写进 GT 或 candidate 目录，也不得覆盖配置。Python API：

```python
from evaluation import Evaluator
report = Evaluator(gt_dir, cand_dir, config_path).run()
```

底层 CLI 不自动更新 benchmark 的运行摘要；PrepBench/scripts/evaluate.py 提供阶段保存与汇总适配，PrepBench/scripts/run_benchmark.py 可串联生成和评分。报告记录实际读取的 config、GT、candidate SHA256，协议版本，以及每个文件的内容/顺序检查状态。`side` 表示错误出现在哪一侧或比较阶段，不自动推断 agent 的根因。

## 配置

```json
{
  "files": {
    "output_01.csv": {
      "key": ["Customer"],
      "columns": {
        "Customer": {"type": "text_exact", "null_values": []},
        "Date": {"type": "date", "formats": ["%Y-%m-%d", "%d/%m/%Y"]},
        "Count": "integer",
        "Revenue": {"type": "number", "abs_tol": 0.001, "rel_tol": 0.00001}
      },
      "ignore_order": false,
      "order_by": [
        {"column": "Revenue", "direction": "desc", "nulls": "last"},
        {"column": "Customer", "direction": "asc", "nulls": "last"}
      ]
    }
  }
}
```

- `files`、`columns` 和 `key` 必填。key 是 columns 的非空子集，可以包含全部字段。CSV 文件集合必须与配置及 GT 一致；额外列和列顺序忽略。错误配置、未知参数不会被静默忽略。
- CSV 先按原始字符串读取，支持 UTF-8（含 BOM），失败时兼容回退 Latin-1；不自动推断数字或 NA。随后对 GT/candidate 的全部声明字段应用同一规范化规则。
- `integer` 用 Decimal 精确检查，`1` 与 `1.0` 等价，非整数报 TYPE_ERROR，不把大整数转 float。
- 对象形式 `number` 使用 Decimal，公式为 `abs(candidate-GT) <= max(abs_tol, rel_tol*abs(GT))`。未指定的参数为 0，两个参数都省略即精确数值比较，边界包含在内。零值 GT 只靠绝对容差。容差必须为有限非负 JSON 数值。
- 对象形式 `text_exact` 保留大小写、前导零、空白及字段值中的引号；它可以用于字符串标识符，不另加 `id` 类型。`text_norm` 是显式选择的忽略大小写、首尾空白及合并内部连续空白规则。
- 对象规则可用 `null_values` 显式替换空值列表，默认列表为 `[""]`，`[]` 表示不映射任何空值。`date`/`datetime`/`time` 对字段值和列表项先去首尾空白、转小写再匹配，因此默认也识别纯空白；其他对象类型仍逐个按原始文本精确匹配。`NA`、`null` 不默认等同空值。
- 对象 `date`/`datetime`/`time` 按下节的日期协议解析，再共用于 key、字段比较和排序。
- boolean 沿用明确的 true/false、1/0、yes/no 等词表，未识别值报 TYPE_ERROR。

## 日期与时间比较

保留字段名 `formats`，其值为非空字符串列表。对于 `date`，配置声明额外可接受的日期格式，内置 ISO 表示始终可用；对于 `datetime`，配置格式与内置 ISO 格式合并去重，始终尝试全部格式。`time` 的显式格式仍替换默认集合。内置默认格式为：

| 类型 | 默认格式 |
| --- | --- |
| `date` | `%Y-%m-%d` |
| `time` | `%H:%M`、`%H:%M:%S`、`%H:%M:%S.%f` |
| `datetime` | `%Y-%m-%d %H:%M`、`%Y-%m-%dT%H:%M`、`%Y-%m-%d %H:%M:%S`、`%Y-%m-%dT%H:%M:%S`、`%Y-%m-%d %H:%M:%S.%f`、`%Y-%m-%dT%H:%M:%S.%f` |

query 未指定格式时，比较解析后的日期/时间语义。例如 pandas 的 `2024-01-02 10:30:00` 与 Polars 的 `2024-01-02T10:30:00.000000` 等价。对象规则中的斜线日期格式需要显式加入 `formats`；ISO datetime 仅到分钟的表示内置支持。默认不猜测月日顺序；同一输入解析出多个不同值时报 TYPE_ERROR，多个格式解析成同一个值则通过。

- `date` 返回日历日期。内置接受 `YYYY-MM-DD`、`YYYY-MM-DD 00:00:00` 和 `YYYY-MM-DDT00:00:00`；零点时间可带任意位全零小数秒。非零时间或时区后缀不截断，报 TYPE_ERROR。额外 `formats` 只解析日期部分的完整字符串，不自动扩展为带时间格式；配置中包含时间指令仍报 CONFIG_ERROR。GT 和 candidate 应用同一规则，收集全部解析结果，不根据 GT 选择 candidate 的解释。
- `datetime` 精确比较，不使用数值容差，不舍入、不截断。小数秒支持 1–6 位（Python datetime 的微秒精度）；纳秒表示暂不支持。内置 ISO 格式允许省略秒，解析后秒为零；非零秒和微秒仍会产生差异。
- 默认仍不接受时区后缀或时区格式指令。仅当任务明确无时区值代表UTC时，可在`datetime`对象规则显式设置`"assume_timezone": "UTC"`（协议v8）。此时支持ISO日期时间的`Z`和`±HH:MM`后缀，按实际时区偏移换算UTC后精确比较；无后缀值解释为UTC。小数秒仍只支持1–6位，不截断。拒绝表示未知偏移的`-00:00`、非法偏移、时区名称和其他类型/时区配置。未启用的任务行为不变。
- 日期类对象规则的 `null_values` 忽略首尾空白和大小写，但不删除字段内容中的引号。例如 `["", "NA", "null"]` 将 ` NA ` 与 `Null` 都映射为 None。
- 非法或歧义日期统一报 TYPE_ERROR，并标记 gt/candidate，包括 key 字段。解析成功但值不同，key 报 KEY_MISMATCH，非 key 报 VALUE_MISMATCH。顺序检查按解析后的时间顺序进行。

`date`/`datetime` 验证日期时间语义，不验证输出字符串格式；`formats` 不是严格输出格式约束。若 query 严格要求字符串表示，可使用 `text_exact` 与符合要求的 GT 比较，但此时不再提供日期语义比较或日期排序。当前不新增 `output_format`。

## 旧类型字符串兼容

特别注意：`"Revenue": "number"` 保留旧的约 2% 比较规则，而 `"Revenue": {"type": "number"}` 默认精确比较。把字符串改成对象并非单纯换写法；需要容差时应显式声明 `abs_tol` / `rel_tol`。文本和空值等规则也存在下述兼容差别。

现有 PrepBench 的 `number`、`date`、`datetime`、`text_exact`、`text_norm`、`boolean` 字符串配置无需重标注即可读取。但新版故意不保留“非法值当空值”等可能误判通过的行为。

| 旧字符串类型 | 保留的行为 |
| --- | --- |
| `number` | float 解析，去掉逗号、美元符号和百分号（不做百分比缩放）；非零值使用 `abs(a-b)/max(abs(a),abs(b)) < 0.02`；任一值为零时使用 `abs(a-b) < 0.02` |
| `date` / `datetime` | 上游明确的格式列表，包括日/月/年；兼容三位年份补零；date 额外接受内置 ISO 日期及零点时间表示，datetime 额外接受全部内置 ISO datetime 格式；不是自动猜测月日 |
| `text_exact` | 首尾空白及包围引号清理，保留大小写 |
| `text_norm` | 上述清理后转小写、合并空白 |
| 旧空值规则 | 数字、文本、布尔将空串、none、nan、null、n/a、na 视为空；日期只使用空串、na、n/a、null；不区分这些 token 的大小写 |

`integer` 是新类型，空字符串为空值，不继承旧版宽泛空值别名。非法数值、非有限数值、非法日期等统一报 TYPE_ERROR；旧版某些数值解析失败会变 None、日期失败会退回字符串，新版不沿用。旧字符串 `number` 的 float 精度限制仍存在，需要精确的指标用对象规则，需要整数的用 `integer`。

## key 对齐与字段比较

`columns` 声明全部需要验证的字段，`key` 从中选出用于划分和对齐行组的字段。两者职责不同：key 决定“哪些行属于同一组”，其余字段决定“对应组的结果是否一致”。key 不要求唯一；排序字段则决定输出位置，可以与 key 不同。

例如以下是说明机制的示例，不对应某个特定 PrepBench case：

```json
{
  "key": ["Date", "Store"],
  "columns": {
    "Date": {"type": "date"},
    "Store": {"type": "text_exact"},
    "Sales": {"type": "number", "abs_tol": 0.01}
  }
}
```

每行先用规范化后的 Date、Store 组成 tuple。evaluator 建立 tuple 到行号列表的分组索引，`_align()` 对齐 GT 与 candidate 的 key 组；并非仅用 set 判断两张表是否相同。组内先比较行数，再比较非 key 字段的多重集合。Date/Store 组无法匹配时是 `KEY_MISMATCH`，组大小不同是 `GROUP_SIZE_MISMATCH`，Sales 不符合规则时是 `VALUE_MISMATCH`。


全局保留所有精确 tuple 组匹配，剩余 key 组做列级容差匹配。精确匹配优先是明确的协议选择：有精确组匹配时，不再把附近的容差组匹配视为歧义。剩余匹配若出现多个候选组，报告 KEY_MISMATCH，不随扫描顺序猜测。此处比上游逐行排除已使用行更明确；数值零值候选的原版索引边界问题也不沿用。

仅在未精确匹配的 key 组中按精确 key 分量分桶，桶内检查容差。全数值 key 且没有精确匹配时最坏为二次复杂度；首版面向现有小表，不承诺大表性能。

对齐后比较所有非 key 字段。精确规则的非 key tuple 使用计数比较，因此组内顺序和重复值都被正确处理；带数值容差的非 key 字段使用保守的一对一匹配，多个不同候选均可匹配时报告 `AMBIGUOUS_MATCH`。key 字段错误可能表现为 KEY_MISMATCH，非 key 内容错误表现为 VALUE_MISMATCH。

全字段 key 指 `key` 包含 `columns` 中的所有字段。此时没有剩余非 key 字段，但完整 key tuple 的出现次数仍会比较；完全相同的重复行只要两边次数一致就通过。`NON_UNIQUE_KEY` 不再表示普通重复 key，当前协议允许 key 组包含多行。

key 中的 number 同样使用该列的容差规则；非数值字段使用规范化后的精确相等。实现先保留全部精确匹配，再匹配剩余行，避免前面的容差匹配抢占后面的精确匹配。对剩余部分采用保守的一对一匹配，不搜索可能消除局部歧义的全局最优匹配。

## 顺序检查：当前实现

以下记录当前代码行为；最终排序协议仍待讨论，本次不改变实现。

`ignore_order` 缺省或为 true 时不检查顺序；默认fields模式下，显式 false 时必须提供非空 `order_by`（显式GT位置模式见下文）。每项声明列、asc/desc 和 nulls first/last。排序列必须在 columns 中，不要求属于 key，也不要求唯一。为防止静默忽略，true 与非空 order_by 同时存在会报 CONFIG_ERROR。

先验证 GT 是否满足排序配置（不满足时报 GT_ORDER_ERROR），内容比较通过后检查 candidate 原始相邻行是否按多字段字典序有逆序；禁止先排序 candidate。全部排序字段相等时允许换位。并列判断不使用内容数值容差；空值位置独立于升降序；文本采用该列规范化后的 Unicode 字典序。不支持 locale 排序、隐藏排序列、稳定保留输入顺序或额外排序表达式；这些需求需要另行适配，不能当作已验证。日期字符串排序可用精确文本列规则表达，但不能同时假定该列按日期格式等价比较。

实际顺序判断集中在 `_check_order(rows, order, side)`。它依次检查每对相邻行，按照 `order_by` 的字段优先级比较：当前字段相同就比较下一字段；第一个不相同的字段决定这对行是否有逆序；全部排序字段相同则为并列，可以交换。比较使用规范化后的数值、日期或文本，不是原始 CSV 字符串的一律字典序比较。

例如仅按 Revenue 降序时，Revenue 都为 100 的两行可以互换；如果还规定 Customer 升序，那么这两行还必须满足 Customer 的顺序。排序字段无需唯一，也无需属于 key。内容比较的数值容差不会把两个不同的 Revenue 值变成排序并列。

默认字段排序模式不会直接按 GT 行位置验证顺序，也不会从 query 或 GT 自动推断 `order_by`。配置生成阶段需要明确标注排序列、方向和空值位置。evaluator 不会重排 candidate 来使结果通过。

待讨论的替代思路是“以 GT 的组间顺序为准，允许并列组内部换位”。这种方式可以考虑只标注定义并列的排序字段，省略方向和空值位置，但依赖 GT 顺序正确，并且仍需知道用哪些字段判断并列。仅凭 GT 的行顺序无法区分“只按 Revenue 排序”和“Revenue 后再按 Customer 排序”。该替代方案尚未实现，不是当前配置支持的额外模式。

## 报告与测试

报告使用 `protocol_version: "dfarena-table-v3"`，包含总体 `passed`、`errors`、首个错误摘要 `diff_summary`、逐文件状态 `files` 和已读取资产的哈希 `assets`。因为首个错误即停止，哈希和文件状态只覆盖当次已处理的资产，不保证包含全部文件。

首版 fail-fast。主要错误包括 CONFIG_ERROR、FILE_COUNT_MISMATCH、MISSING_FILE、READ_ERROR、MISSING_COLUMNS、ROW_COUNT_MISMATCH、TYPE_ERROR、KEY_MISMATCH、GROUP_SIZE_MISMATCH、VALUE_MISMATCH、AMBIGUOUS_MATCH、GT_ORDER_ERROR、ROW_ORDER_MISMATCH。旧版的 `NON_UNIQUE_KEY` 不再用于普通重复 key。未知内部异常标为 EVALUATOR_ERROR。

错误可按阶段理解：配置问题为 `CONFIG_ERROR`；文件/结构问题包括 `READ_ERROR`、`MISSING_COLUMNS` 和数量不匹配；规范化失败为 `TYPE_ERROR`；key 组对齐问题为 `KEY_MISMATCH`，组大小不一致为 `GROUP_SIZE_MISMATCH`，组内容差匹配歧义为 `AMBIGUOUS_MATCH`；对齐后的内容差异为 `VALUE_MISMATCH`；顺序问题区分 GT 和 candidate 两侧。`passed=false` 本身不能区分 candidate 错误与 GT、配置或 evaluator 故障，需要结合错误码和 `side` 查看。

`content_status` 与 `order_status` 分开；未完成检查保留 not_checked，忽略顺序标为 ignored。即使内容通过，顺序不通过也使总 passed=false。失败详情含文件、侧别、相关列和从 0 开始的行号。

```bash
python -m unittest discover -s evaluation/tests -v
```

测试涵盖六个现有 case 的 GT 自比较和行逆序比较，以及数值/整数边界、日期和空值、key 歧义、并列与多列排序、GT 排序错误、文件/字段/类型错误和 CLI。GT 自比较通过只验证评估链路，不证明 GT 满足任务需求。

`time` 表示一天内的时刻，不表示时长。`7:19`、`07:19` 和 `07:19:00` 等价；秒和微秒仍精确比较。显式 `formats` 替换默认格式，不能包含日期或时区。非法时间（如 `24:00`）报 TYPE_ERROR，不自动折算到次日。简写 `"time"` 同样使用这些默认格式，默认仅将空白映射为空值。

## 显式 GT 位置顺序（v7）

当题目明确规定最终行位置（例如固定统计块及块内自定义顺序），且研究者已独立核验 GT 顺序时，可配置 `ignore_order: false, order_mode: "gt_position"`，不设置 `order_by`。仍先检查行数、key组及组内内容多重集，再逐位置比较全部已声明字段，沿用字段类型和容差；不重排候选。内容正确但位置不符报 `ROW_ORDER_MISMATCH`，content_status保持passed。相同的重复行仍需保留数量；数值等价表示允许。

此模式不从字段推导排序，无法自行证明GT顺序满足题意，必须先独立审核；不能用于仅要求按某字段排序、允许其他不同值并列换位的任务。不能与ignore_order=true、非空order_by或alternative_gt合用。不启用时原比较行为不变。
