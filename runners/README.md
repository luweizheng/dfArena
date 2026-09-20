# Shared coding-agent runners

DataAgentBench supports `--agent codex|opencode`. Runs use isolated Docker containers and preserve generation and evaluation records separately.

## Session archives

Each run saves both the CLI event stream and the agent's native session archive:

| Artifact | Codex | OpenCode |
|---|---|---|
| Session archive | `detail/codex_sessions/` | `detail/opencode_sessions/opencode.db` |
| DataAgentBench CLI events | `logs/codex_stdout.jsonl` | `logs/opencode_stdout.jsonl` |

CLI events support token extraction and execution analysis. Native archives preserve additional session context. Both retain their original formats; paths are recorded in `artifacts.agent_log` and `artifacts.sessions`.

After container shutdown, the runner copies Codex session files or backs up OpenCode's SQLite database, including committed WAL data. Credentials and provider configuration are excluded. Failed and timed-out runs also attempt archiving. Resuming requires the corresponding workspace and configuration, not just the archive.

## Timing and token usage

`detail/agent_exec_timing.json` records UTC `started_at` / `finished_at` and monotonic `elapsed_seconds`. It measures the agent process inside Docker, including exploration, tool execution, repairs, and simulator waits. Docker startup, session archiving, and evaluation are excluded.

Generation metrics go to `detail/generation.json`; evaluation has its own timing and status in `detail/evaluation.json`. `result.json` combines both records. DataAgentBench merges validator stdout and stderr into `logs/evaluation.log`.

Codex usage comes from `turn.completed.usage`; OpenCode usage comes from `step_finish.part.tokens`, deduplicated by session ID and part ID. The shared `token_usage` fields use inclusive counts:

| Field | Meaning |
|---|---|
| `input_tokens` | Input including cache |
| `cached_input_tokens` | Cache reads, already included in input |
| `output_tokens` | Output including reasoning |
| `total_tokens` | Input plus output |

For OpenCode 1.18.29, inclusive input is native `input + cache.read + cache.write`; inclusive output is native `output + reasoning`. Original counters remain in `token_usage_native`. Do not add cache or reasoning to the normalized totals again. For runs without cache writes, non-cached input is `input_tokens - cached_input_tokens`.

Missing counters remain `null`. `token_usage_status` describes the completeness of received events, not billing coverage. Simulator usage is excluded, and `reported_cost` is only the CLI's estimate.

**CLI usage can omit auxiliary requests.** In one OpenCode audit, all 10 visible steps matched provider counters, but the provider recorded an additional 4,861-token request consistent with automatic title generation. Neither CLI steps nor archived assistant messages included it. Whole-run accounting therefore requires provider logs filtered by experiment key and time window; do not treat that example's overhead as a fixed correction.

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

Defaults resolve relative to this repository. Override them with `--codex-config-dir`, `--opencode-config`, or `--opencode-auth`. Missing local configuration does not fall back to global settings.
