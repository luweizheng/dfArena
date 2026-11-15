# Shared coding-agent runners

Each `<benchmark>` runner supports `--agent codex|opencode`. Runners use isolated Docker runs and preserve generation and evaluation records separately.

## Session archives

Each run saves both the CLI event stream and the agent's native session archive:

| Artifact | Codex | OpenCode |
|---|---|---|
| Session archive | `detail/codex_sessions/` | `detail/opencode_sessions/opencode.db` |
| CLI events | `logs/agent_events.jsonl` | `logs/agent_events.jsonl` |
| CLI stderr | `logs/agent_stderr.log` | `logs/agent_stderr.log` |

Paths are relative to a run directory under `<benchmark>`. `agent_log_paths(run_dir)` in `runners/agents/` defines the shared CLI log paths. Historical runs retain their original names; use their recorded `artifacts.agent_log` path.

CLI events support token extraction and execution analysis. Native archives preserve additional session context. Both retain their original formats; paths are recorded in `artifacts.agent_log` and `artifacts.sessions`.

After container shutdown, the runner copies Codex session files or backs up OpenCode's SQLite database, including committed WAL data. Credentials and provider configuration are excluded. Failed and timed-out runs also attempt archiving. Resuming requires the corresponding workspace and configuration, not just the archive.

## Timing and token usage

`detail/agent_exec_timing.json` records UTC `started_at` / `finished_at` and monotonic `elapsed_seconds`. It measures the agent process inside Docker, including exploration, tool execution, repairs, and simulator waits. Docker startup, session archiving, and evaluation are excluded.

`runners/timed_process.py` is the in-container execution wrapper, not a test. The runner mounts this script into the container and invokes it as the container command; the wrapper starts Codex or OpenCode, forwards its standard input/output/error, waits for completion, and writes the timing report. On timeout it terminates the agent's process group before recording the final status and exit code.

Generation metrics go to `detail/generation.json`; evaluation has its own timing and status in `detail/evaluation.json`. `result.json` combines both records. When evaluation invokes an external validator, its stdout and stderr are combined in `logs/evaluation.log`.

Codex usage comes from `turn.completed.usage`; OpenCode usage comes from `step_finish.part.tokens`, deduplicated by session ID and part ID. The shared `token_usage` fields use inclusive counts:

| Field | Meaning |
|---|---|
| `input_tokens` | Input including cache |
| `cached_input_tokens` | Cache reads, already included in input |
| `output_tokens` | Output including reasoning |
| `total_tokens` | Input plus output |

For OpenCode 1.18.29, inclusive input is native `input + cache.read + cache.write`; inclusive output is native `output + reasoning`. Original counters remain in `token_usage_native`. Do not add cache or reasoning to the normalized totals again. For runs without cache writes, non-cached input is `input_tokens - cached_input_tokens`.

Missing counters remain `null`. `token_usage_status` describes the completeness of received events, not billing coverage. Simulator usage is excluded, and `reported_cost` is only the CLI's estimate.

**Current accounting uses the OpenCode CLI event stream.** In one audit, the provider recorded one additional LLM request beyond the 10 visible steps, likely for automatic title generation. This request was absent from the CLI steps and archived assistant messages. We keep the CLI event total as the reported coding agent usage and apply no inferred correction; the extra request is documented as a known coverage limitation.

## Agent adapter structure

```text
runners/
  agents/
    __init__.py       # Registry and shared entry points
    base.py           # AgentAdapter interface
    codex.py          # Codex configuration, command, archive, usage parser
    opencode.py       # OpenCode configuration, command, archive, usage parser
  results.py          # Stage persistence and result summary
  timed_process.py    # Agent process timing and timeout handling
```

Adapters implement `settings`, `prepare`, `archive_sessions`, and `metrics`, with optional overrides for CLI options, argument forwarding, and model labels. Benchmark runners manage task assets and Docker execution.

To add an agent, implement and register an adapter, install its CLI in the image, and check the timer's accepted agent names and benchmark conventions such as log naming and session ID extraction.

## Configuration

Local settings live in `configs/codex/config.toml` and `configs/opencode/opencode.json`. Start from the [Codex example](configs/codex/config.example.toml) or [OpenCode example](configs/opencode/opencode.example.json), then set the provider, model, reasoning effort, and credentials. Examples are shareable; actual configuration and authentication files are Git-ignored.

The host-side clarification simulator has a separate shared configuration at `configs/simulator/simulator.env`, based on [simulator.example.env](configs/simulator/simulator.example.env). Both benchmarks read its `SIMULATOR_*` settings in interactive mode; their `--simulator-env` option can select another file. Keep this configuration separate from coding-agent model settings.

Defaults resolve relative to this repository. Override them with `--codex-config-dir`, `--opencode-config`, or `--opencode-auth`. Missing local configuration does not fall back to global settings.

Interactive runners inject their local clarification MCP through `AgentAdapter.configure_local_mcp()`, after preparing isolated agent settings. The benchmark owns the command, environment and mounts; Codex/OpenCode adapters serialize native configuration. Codex retains separate startup/tool timeouts in seconds and `required=true`. OpenCode exposes one `timeout` in milliseconds, mapped from the tool budget; the startup timeout has no separate mapping. This does not assert identical startup or failure behavior. Existing provider settings and other explicitly injected servers are preserved; duplicate server names are rejected. Host MCP settings are not imported.

## Claude Code (experimental)

The `claude` adapter runs Claude Code inside the same isolated Docker workspace
used by the other agents. Build `docker/agent-sandbox.Dockerfile` to include
Claude Code 2.1.260. Permission bypass is enabled only inside this sandbox.
Copy `runners/configs/claude/settings.example.json` to `runners/configs/claude/settings.json`
and configure an **Anthropic Messages-compatible** provider and its actual
model ID. An OpenAI-only model endpoint cannot be used directly by Claude Code.
The local settings file is ignored by Git; keep its permissions at `0600`.

```bash
.venv/bin/python PrepBench/scripts/run_benchmark.py \
  --case 001 --mode clarified --backend pandas --agent claude \
  --model PROVIDER_MODEL_ID --timeout 1800
```

`--claude-config PATH` selects a different settings file. Only provider auth,
base URL, selected model and effort are copied into temporary configuration;
host hooks, MCP servers, history and personal instructions are not imported.
Interactive runs inject only the benchmark's clarification MCP server.
Native stream events and project session traces are retained. Usage uses the
final result event, including cached input tokens; timed-out runs without a
result event report unavailable usage. Provider-reported cost is retained but
is not assumed to be the third-party provider's actual invoice. Correctness
still comes from the separate benchmark evaluator, not the Claude exit code.

A provider reporting zero output tokens despite generated assistant content is
marked as partial usage. Do not use such counters for complete cost estimates.
The clarified pandas smoke test passed with nowcoding.ai and `gpt-6.1-sol`;
an interactive pandas smoke test also passed with two successful clarification calls.
