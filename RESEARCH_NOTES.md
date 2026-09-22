# dfArena 研究记录

主要用中文记录论文定位思路。README 面向项目介绍与运行；本文件保留研究讨论与当前共识。

记录原则：区分【已确认】【部分已确认】【候选方案】【待核查】和【已实现】。讨论中的示意问答不等于实际 agent 轨迹；计划接入不等于已经完成实验。

## Motivation 与论文主题

Pandas 是最广泛使用的表格数据分析与处理工具之一，但其单机、内存内执行模型限制了可扩展性。为满足不同的性能和部署需求，数据社区发展出了 Polars、PySpark、Ibis 等替代接口与执行系统，使表格处理能够采用不同的执行方式并适配更广泛的数据处理场景。

与此同时，数据分析与处理正在从人类手写程序，逐步扩展到人类用自然语言描述需求，由 AI agent 探索数据、生成并执行程序。Agent 既可以根据自然语言需求直接使用 pandas 或其他 DataFrame backend 完成任务，也可以将已有 pandas 工作流迁移到其他 backend。

然而，生成可执行代码并不意味着正确完成任务。一方面，用户的自然语言需求往往不完整或存在歧义，agent 需要区分能够通过数据探查确认的事实与必须向用户询问的业务选择，通过必要的交互明确计算口径。另一方面，不同 backend 的 API、默认行为与执行语义存在差异；即使需求已经明确，agent 仍需选择正确的实现，避免隐式默认行为改变结果。对于代码迁移任务，则需要以原 pandas 程序为语义依据，尽量保持迁移前后的结果一致。

因此，我们关注 AI-assisted DataFrame programming 的正确性与可靠性：agent 能否确定任务所要求的语义，并在不同 backend 上忠实实现；以及能否利用执行和交互反馈改进其澄清与实现策略，在有限的用户交互下更准确地完成任务。

## Empirical study 与错误诊断

【部分已确认】前期运行表明，coding agent 不仅能够生成 pandas 程序，也能够通过读取 schema、探查数据和尝试当前环境中的 API 来生成 Polars、Ibis 等 backend 的程序。生成可执行代码仍不等于正确完成任务。当前重点关注以下几类可由执行轨迹和评估结果验证的现象：

- Pandas 训练先验带来的隐式语义假设，例如缺失分组键、`count` 与行数统计、CSV 缺失值表示、类型推断和去重保留规则。
- 不同 backend 的 API、默认行为和执行语义差异，导致 agent 将 Pandas 的习惯直接迁移到其他系统。
- 自然语言需求没有明确字段含义、统计口径、缺失值处理或输出要求，agent 需要在默认假设和用户澄清之间作选择。
- agent 已经获得澄清回答，但没有更新需求记录或将回答落实到最终代码。
- 后续再完善...

empirical study 的作用不仅是报告不同模型、coding agent 和 backend 的通过率，还要保存 query、数据探查、提问与回答、生成代码、修复轨迹和 evaluator 报告，使错误归因可以回溯到具体证据。

## Harness-level self-improvement for DataFrame agents

【候选方案】基于上述诊断，候选方法是研究面向 DataFrame agent 的 harness-level self-improvement。系统在不更新模型参数的情况下，利用执行轨迹、交互记录和 evaluator feedback，迭代改进可复用的 DataFrame skill、instruction 和澄清流程，使 agent 更快确定用户意图并正确使用目标 backend。第一版只允许修改 versioned skill/instruction，固定模型、工具、任务资产、simulator 和 evaluator。

skill 不只是提醒 agent“遇到问题就提问”，而应覆盖三个连续决策：

```text
数据探查：哪些事实可以从输入数据确认？
需求澄清：哪些会改变结果的业务选择必须询问用户？
语义实现：确认后的选择如何落实到目标 backend？
```

外层优化循环暂定为：

```text
运行开发任务，收集代码、轨迹、问答与评估结果
    → 从证据中提炼可迁移的 DataFrame failure mode
    → 生成少量候选 skill 修改
    → 在固定开发条件下评估候选
    → 检查正确率、交互成本和回归
    → 保留并版本化通过的 skill
    → 在新任务、模型或 backend 上冻结测试
```

这里借鉴 [Gear](https://github.com/rsi-gear/gear) 的反馈驱动候选、版本封存、分阶段评估和回归保护思想，但当前并未声称已经集成 Gear，也不同时优化模型权重、工具实现或完整 harness。需要与以下对照比较：无额外 skill、人工编写的静态 skill、反馈优化后的 skill；如资源允许，再加入相同预算的通用 prompt 优化基线。这里的 self-improvement 是 harness-level 改进，不等同于模型参数训练、完整 RSI 或 agent 自主修改自身代码。

主要指标包括最终正确率、交互轮数、实际问题数、重复/无效问题数、token、agent 时间，以及 skill 在未见任务和不同 backend 上的迁移效果。一次请求包含多个问题时，不能只用 HTTP 请求数表示交互成本。

这条方法主线需要通过实验验证：执行反馈驱动的 skill 是否比静态指导更有效，收益是否来自可迁移的语义规则而非记忆任务答案，以及是否引入了新的 backend 回归。

## 实验矩阵与研究假设

核心实验采用“需求清晰度 × harness 条件”的 2×3 矩阵：

| 需求条件 | S0：无额外 skill | S1：人工静态 skill | S2：反馈演化 skill |
|---|---|---|---|
| 无歧义、完整需求 | 测量基础 NL-to-DataFrame 能力 | 检查静态指导是否提升能力或引入回归 | 检查演化后的 skill 是否保持清晰任务上的泛化 |
| 有歧义、不完整需求 | interactive baseline | 检查通用澄清规则的效果 | 检查反馈驱动改进对澄清和实现的影响 |

无歧义条件使用完整、经过审核的需求，agent 直接完成任务；有歧义条件使用保留不确定性的原始需求，允许 agent 通过 simulator 获取局部澄清。两类条件应尽量由同一任务构成配对，以隔离需求清晰度的影响。S0、S1 和 S2 使用相同的模型、coding agent、工具、输入数据、simulator、Docker 环境和交互预算。

第一阶段先运行 2×2 的 S0/S1 对照，快速确认静态 skill 是否有效；第二阶段加入 S2，验证 feedback-driven 改进是否超过人工静态 skill。Pandas、Polars 和 Ibis 可以作为独立实验面板逐步加入，不能把 backend、模型和 skill 同时变化后再归因。

当前需要验证的假设是：

- **H1：** 需求模糊是独立于代码生成能力的重要错误来源。
- **H2：** 静态 DataFrame skill 能减少需求理解、缺失值处理和 backend 语义使用错误。
- **H3：** 基于执行轨迹和 evaluator feedback 演化的 skill，在未见任务上优于无 skill 和人工静态 skill。
- **H4：** skill 的收益不仅体现在最终正确率，也体现在更少的无效提问、交互轮数和 token 消耗。
- **H5：** skill 学到的规则能够迁移到未见任务或其他 backend，同时不引入明显的 backend 回归。

## Harness 条件与数据隔离

三种 harness 条件定义如下：

- **S0：** 不加载额外的 DataFrame skill，只使用 agent 原有的系统提示、工具和运行环境。
- **S1：** 使用实验前人工编写并冻结的静态 DataFrame skill。
- **S2：** 只使用开发集的轨迹、交互记录和 evaluator feedback 迭代得到的、带版本号的 skill。

S2 的演化过程只能访问开发集中的任务、错误类型和反馈。测试集任务、reference、GT、evaluation config 和最终测试结果在 skill 演化过程中不可见。候选 skill 必须先通过开发集的正确率、交互成本和回归检查，再冻结版本并用于测试。skill 中应保存可迁移的语义规则，例如缺失值分组、`count` 的统计口径、日期和类型处理以及何时需要向用户询问；不能写入具体任务的答案、行值或用于识别测试样本的提示。

## 评价指标与实验产物

主指标是 task correctness 和 semantic error rate；interactive 任务还单独报告最终正确率。辅助指标包括 clarification rounds、有效问题数、重复或无效问题数、token usage、agent elapsed time 和 backend regression rate。正确率与交互成本暂不合成为单一总分，优先报告固定交互或 token 预算下的正确率，并同时展示成本变化。

每个 run 至少保存需求版本、输入数据标识、backend、model、agent、skill 版本、完整 trajectory、生成代码、执行结果、evaluator 报告和 timing/token 统计。一次 HTTP 请求可能包含多个问题，不能只用请求数表示交互成本。

## 实施路线与阶段性产物

1. 固定 evaluation protocol，完成 PrepBench 任务迁移和任务契约审计。
2. 运行 S0 baseline，建立不同 backend 和错误类型的初始结果。
3. 构造并冻结 S1 静态 skill，先验证澄清和 backend 语义规则是否有效。
4. 根据开发集 trajectory 和 evaluator feedback 提出少量 S2 skill 候选，执行候选筛选和回归保护。
5. 冻结 S2 版本，在未见任务、backend 和模型条件上测试泛化。
6. 在 pilot 结果支持主线后，再扩展到 DataAgentBench、LongDS 和 PandasBench，并增加跨模型、跨 agent 的比较。

## 三类任务入口与实验覆盖

| 类别 | 初始输入 | Agent 的任务 | 主要资产来源 |
|---|---|---|---|
| Code-to-Code Transpilation | 已有 [PandasBench](https://arxiv.org/abs/2506.02345) 代码 + 数据 | 迁移到其他 backend，保持结果语义 | 现有 PandasBench，补充 Kaggle 和可获得的企业代码 |
| Direct NL-to-DataFrame | 明确的自然语言需求 + 数据 | 生成并执行程序，获得正确答案或结果表 | 整理、澄清后的 [PrepBench](https://arxiv.org/abs/2605.08687)、[DataAgentBench](https://arxiv.org/abs/2603.20576) 等 |
| Interactive NL-to-DataFrame | 不完整或有歧义的自然语言需求 + 数据 | 自主提问获取局部澄清，再完成程序 | 优先复用 PrepBench interactive 流程与资产 |

三类任务是错误诊断和 skill 验证的互补 workload，而不是三个相互独立的论文贡献：已有代码定义语义，完整自然语言定义语义，交互过程逐步明确语义。统一评测 agent 能否在不同 backend 上正确实现这些语义，并检验从失败反馈中提炼的 skill 是否能够迁移。

## 论文贡献的暂定表述

1. **可审计、可复现、可评估的 NL-to-DataFrame 任务与协议。** 整理任务、输入、reference、GT、typed evaluation config、运行隔离和 trajectory/report 资产，使不同模型、coding agent 和 backend 的结果可以复核。
2. **跨模型、跨 agent、跨 backend 的实证研究。** 系统分析自然语言需求、Pandas 语义先验和 backend API/执行语义差异如何影响 DataFrame 程序的正确性，并区分需求、交互、实现和环境层面的失败。
3. **training-free 的 harness-level self-improvement。** 将 DataFrame skill、instruction 和澄清流程作为 harness 的可版本化组成部分，从执行轨迹、交互记录和评估反馈中提出并验证改进，研究其在有限交互预算下对准确性、成本和跨任务/backend 泛化的影响。

第三项贡献目前仍是候选主线，需要先完成 pilot 和开发/测试隔离后再作为已验证结论。

### 第一类：迁移已有 Pandas 程序（transpilation workload）

- 延续第一稿，完善 PandasBench 的可执行性、参考输出、验证规则和任务描述。
- 补充 Kaggle 代码；如果能够获取可复现、可使用的企业代码则更好，但目前没有确认新增来源。
- 记录代码和数据来源及许可。公开数据构造的企业风格任务不能称为真实企业生产代码。
- 加速或扩大可处理的数据规模是迁移的应用动机；本轮共同核心是正确性与语义保持，完整的大规模性能评测不是主要研究目的，所以也不太关注执行时间，只要保证结果正确。
- 目标接口包括 Polars、Ibis，如果有余力试一下 PySpark。

### 第二类：明确需求直接生成程序（direct NL workload）

- 整理 PrepBench、DataAgentBench 的现有任务，消除歧义、补全必要业务规则，明确输出要求。
- “删除歧义”主要指澄清文本；无法可靠澄清或验证的任务可以排除。保留原始请求、改写内容和修改依据。
- Agent 可探索数据、执行与修复代码，但不通过用户交互获取缺失需求。
- 以可验证结果表或结构化答案为依据，避免只判断自由文本中是否包含正确数字。

### 第三类：交互澄清需求后生成程序（interactive NL workload）

- 初始就提供原始请求和输入数据；agent 自主决定是否提问、问什么以及何时停止。
- 优先复用 PrepBench 的 interactive 任务与资产；具体接入方案另行讨论。
- 本轮限定为“目标固定，但初始表达不完整”的需求澄清。
- 暂不研究用户看过中间结果后的纠错、改变目标和长程状态管理。用户不满意结果可能是实现错误，也可能是需求演化，不能一概称为 agent 错误。

### 共同实验关注点

- 执行是否成功，最终结果是否正确，是否真正使用指定 backend。
- 区分需求缺陷、理解错误、API/实现错误、backend 语义差异、环境错误和验证规则问题。
- 记录探索、提问、执行、修复、时间、token 和成本；具体主指标与预算待 pilot 冻结。
