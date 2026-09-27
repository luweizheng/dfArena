# PrepBench in dfArena

整理后的 case_001—case_006、本地 simulator、生成及评估流程。来源许可证见 [PREPBENCH_LICENSE](PREPBENCH_LICENSE)。

任务适配包括将 Tableau 操作要求改为 DataFrame 工作流、将实际 CSV 输入的 sheet 表述改为 input file，并同步知识库引用；删除仅涉及可视化的交付要求，保留表格计算需求与原有歧义。case_005 的 Policy Number 和 Customer ID 按任务要求配置为 integer。

当前 case_001 的完整需求包含排序约束，但保存的 GT 顺序与 reference 不一致，暂用 `ignore_order=true`；通过评估只代表内容通过，不代表排序要求已验证。历史迁移记录保留在本地 `curation/`，不作为运行依赖或本次发布内容。当前评估协议以 [evaluation/README.md](../evaluation/README.md) 为准。

## 安装与运行

在 dfArena 根目录使用宿主机 Python 3.11+：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker build -f docker/agent-sandbox.Dockerfile -t dfarena-agent-sandbox:latest .
```

完整流程：

```bash
.venv/bin/python PrepBench/run_benchmark.py \
  --case 001 --mode clarified --backend pandas \
  --model gpt-6-astra --image dfarena-agent-sandbox:latest

.venv/bin/python PrepBench/run_benchmark.py \
  --case 005 --mode interact --backend polars \
  --model gpt-6-astra --image dfarena-agent-sandbox:latest
```

默认镜像为 `dfarena-agent-sandbox:latest`；比较实验应固定镜像。`--mode` 默认 interact，`--backend` 支持 pandas/polars/ibis/pyspark。PySpark 使用本地 SparkSession，镜像需包含 PySpark 4.x 和 Java 17。`--model` 覆盖模型，`--agent-model` 仅设目录标签（默认 <agent>_<模型名>，OpenCode 去掉 provider/ 前缀）。推理程度来自 `--codex-config-dir` 的配置，默认 `runners/configs/codex`，实际值写入生成记录。

`--timeout` 默认 1800 秒，限制容器内所选 agent 进程；`--dry-run` 仅准备目录、prompt 和资产 hash，不启动 Docker、simulator 或评分，会占用运行编号。

## 脚本职责

- `run_benchmark.py`：分配运行目录，依次调用 generate.py 和 evaluate.py。生成失败时记录 evaluation.status=skipped；评估通过退出码为 0，否则为 1。
- `generate.py`：准备 query/输入，interact 模式启动 simulator，运行隔离的 Docker/agent，保存生成阶段记录。直接调用时也会自动分配新目录，或通过 `--run-dir` 使用指定的空目录。
- `evaluate.py`：读取指定 case 的 config、GT 与本次 candidate，调用根目录的通用 `evaluation/`，保存完整报告和评估摘要，不执行 agent 代码。
- `runners/results.py`：供 PrepBench/DataAgentBench 共用的阶段写入、token 汇总和 result.json 重建逻辑。
- `runners/timed_process.py`：供两者共用的容器内 agent 计时包装脚本。

单独生成和重新评估：

```bash
.venv/bin/python PrepBench/generate.py \
  --case 001 --mode clarified --backend pandas --image dfarena-agent-sandbox:latest

# 使用上一步打印的 RUN 路径；这里只是示例。
.venv/bin/python PrepBench/evaluate.py \
  --case 001 \
  --run-dir PrepBench/case_001/runs/clarified/codex_gpt-6-astra/pandas/r001
```

独立评分会核对 generation.json 中的任务与状态；重新评分不修改生成阶段记录，更新本次 evaluation.json 和汇总。底层 `python -m evaluation` 仍可用于任意 CSV 比较，但不自动更新运行汇总。配置及比较协议见 [evaluation/README.md](../evaluation/README.md)。

## 目录和结果

```text
PrepBench/
  run_benchmark.py
  generate.py
  evaluate.py
  simulator_server.py
  simulator/
  tests/
  case_XXX/
    inputs/
    query.md
    query_full.md
    amb_kb.json
    reference/solution.py
    evaluation/config.json
    evaluation/gt/output_*.csv
    runs/<mode>/<agent-model>/<backend>/r001/
      result.json
      detail/
        generation.json
        evaluation.json
        agent_exec_timing.json
        prompt.txt
        command.json
        codex_sessions/
      logs/
        agent_events.jsonl
        agent_stderr.log
        server.log               # interact
        interaction.jsonl        # interact
      assets.json
      session.json               # interact
      workspace/
        solution.py
        outputs/output_*.csv
```

每个 mode/model/backend 组合独立递增编号，并发编号分配暂未实现。新运行不再写 run.json，旧运行不自动迁移。生成目录必须为空，防止旧答案或旧评估结果被误用。

`detail/generation.json` 保存模型、模式、后端、生成状态、计时、token、输出路径和交互信息；`detail/evaluation.json` 保存评估时间、status、passed、错误类型以及 `report` 内的完整 evaluator 报告（含 config/GT/candidate hash）。`result.json` 汇总关键指标，始终可以由两份阶段文件重建。写入采用临时文件再替换，不删除阶段记录。

生成 completed 只表示 agent 正常结束且 solution.py/CSV 存在，不代表结果正确。未评估/跳过时 passed=null；candidate 比较失败时 passed=false；GT/config/evaluator 错误时 status=error、passed=null，并保留底层报告。

## 时间与 token

生成的 started_at/finished_at 为 UTC ISO 8601，elapsed_seconds 来自容器内单调时钟：启动所选 agent 前开始，agent 退出或超时终止后结束。排除 Docker 启动、simulator 启动、资源清理和评估；包含 agent 内部探索、代码执行/修复及等待 simulator。不是 solution.py 单独执行时间。无计时报告时保留 null，不用 Docker 耗时替代。正常失败和超时仍保存报告；容器强杀等情况可能缺失。

token_usage 汇总 Codex 有效的 turn.completed.usage，包含 input_tokens、output_tokens、cached_input_tokens、total_tokens（输入加输出，缓存不重复计入）。缺失为 null；token_usage_status 为 complete/partial/unavailable。该统计不包含 simulator，无法补齐未报告的中断请求。

交互摘要在 interaction 中，包含 enabled 和 ask_calls。ask_calls 是 HTTP 请求日志条数，不代表不同问题数量，也不保证每次都成功；完整请求/回答见 interaction.jsonl。评估 elapsed_seconds 单独统计通用表格 evaluator 的运行时间。

## Simulator 与隔离

simulator 使用本机 `PrepBench/.env`，参考 `.env.example`，不随分享包含；进程环境变量优先。默认最多 3 轮，每次最多 10 个问题，总问题预算按 KB 大小计算。

- clarified 将 query_full.md 只读挂载为 `/workspace/query.md`，不启动 simulator。
- interact 将 query.md 挂载到相同路径，宿主机启动 FastAPI simulator，agent 在同一 session 内通过 HTTP/curl 提问，不需要每次 resume。
- inputs 只读挂载到 `/workspace/inputs`，本次 workspace 可写挂载到 `/workspace/work`。不挂载整个 case；GT/config、知识库和 reference 不暴露给 agent。
- Codex 使用独立临时配置目录，只复制模型/provider/推理程度及认证，不带入宿主机历史会话、MCP 或 skills。仅归档本次 session，不归档凭证。
- command.json 保存实际 Docker 参数，用于诊断；临时目录和端口在结束后失效，不能视为可直接重放的脚本。
- 不同运行使用独立 workspace；正常完成、异常和超时均尝试清理本次容器和 simulator。输入挂载期间不要修改资产。

历史探索 runs、case_173/242 和逐项 diff 仍留在 PandasLift/benchmark/PrepBench。参考程序部分 main 使用旧相对路径，运行 reference 时应显式调用 solve(case_dir / 'inputs')。这些参考程序不参与 agent 生成。

## 测试

```bash
.venv/bin/python -m unittest discover -s PrepBench/tests -v
.venv/bin/python -m unittest discover -s evaluation/tests -v
.venv/bin/python -m unittest discover -s DataAgentBench/scripts/tests -v
```

单元/集成测试使用模拟 agent 和 simulator 响应，覆盖两种模式串联、生成失败跳过评分、重评保留生成记录、计时及结果汇总。真实模型运行的结果保存在各自 runs 下，不把模拟测试当作真实模型正确性证据。

## OpenCode 选项

`generate.py` 和 `run_benchmark.py` 都支持 `--agent codex|opencode`，默认 codex。OpenCode 的配置隔离、token 口径和镜像安装见 [runners/README.md](../runners/README.md)。自定义 provider 示例（先按共享说明准备本地配置）：

```bash
.venv/bin/python PrepBench/run_benchmark.py \
  --case 001 --mode clarified --backend pandas \
  --agent opencode --opencode-config runners/configs/opencode/opencode.json \
  --model custom/gpt-6-astra --image dfarena-agent-sandbox:latest
```

OpenCode 同样支持 interact 模式，通过 prompt 中的 HTTP 接口向 simulator 提问；这次真实模型验证使用 clarified 模式，尚未用 OpenCode 实测 interact。OpenCode 保存 `logs/agent_events.jsonl`、`logs/agent_stderr.log` 和 `detail/agent_exec_timing.json`，session ID 记录在 generation.json 中；会话数据库归档到 `detail/opencode_sessions/opencode.db`。阶段文件和 result.json 的路径不变。
