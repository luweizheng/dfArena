#!/usr/bin/env python3
"""
Test Scripts

Run one dataframe benchmark task with OpenCode locally (no Docker).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from run_codex import BACKENDS, next_run, run_solution, validate, write_json


def usage_from_json(text: str) -> dict:
    events = []
    finishes = []
    session_id = None
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(event)
        session_id = session_id or event.get("sessionID") or event.get("session_id")
        part = event.get("part") if isinstance(event.get("part"), dict) else {}
        if event.get("type") == "step_finish" and isinstance(part.get("tokens"), dict):
            finishes.append(part)
    if not finishes:
        return {"available": False, "source": "opencode_json", "event_count": len(events),
                "session_id": session_id, "reason": "no_step_finish_tokens"}
    tokens = {"total": 0, "input": 0, "output": 0, "reasoning": 0,
              "cache": {"write": 0, "read": 0}}
    for part in finishes:
        step_tokens = part["tokens"]
        for key in ("total", "input", "output", "reasoning"):
            tokens[key] += int(step_tokens.get(key, 0) or 0)
        cache = step_tokens.get("cache", {})
        tokens["cache"]["write"] += int(cache.get("write", 0) or 0)
        tokens["cache"]["read"] += int(cache.get("read", 0) or 0)
    cost = sum(float(part.get("cost", 0) or 0) for part in finishes)
    return {"available": True, "source": "opencode_json", "event_count": len(events),
            "session_id": session_id, "steps": len(finishes), "tokens": tokens,
            "cost": cost}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--model", default="su8/gpt-5.6-sol")
    parser.add_argument("--config", default="~/.config/opencode/opencode.json")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    benchmark = args.benchmark.resolve()
    query_dir, data_dir = benchmark / "queries" / args.query, benchmark / "data"
    run_dir = next_run(benchmark / "runs" / "opencode" / args.backend / args.query)
    template = (Path(__file__).resolve().parents[1] / "prompt" / "goal_to_answer_backend.md").read_text()
    prompt = template.replace("{backend_instructions}", BACKENDS[args.backend])
    prompt += "\n\nWrite the required answer.json and solution.py files in the current working directory.\n"
    (run_dir / "prompt.txt").write_text(prompt)
    write_json(run_dir / "run.json", {"benchmark": str(benchmark), "query": args.query,
        "backend": args.backend, "agent": "opencode", "model": args.model,
        "config": str(Path(args.config).expanduser()), "timeout_sec": args.timeout,
        "started_at": datetime.now(timezone.utc).isoformat()})
    if args.dry_run:
        print(run_dir)
        return 0

    config = Path(args.config).expanduser().resolve()
    if not config.exists():
        raise FileNotFoundError(f"OpenCode config not found: {config}")
    env = os.environ.copy()
    env["OPENCODE_CONFIG"] = str(config)
    command = ["opencode", "run", "--format", "json", "--auto", "--model", args.model,
               "--dir", str(run_dir), prompt]
    started = time.perf_counter()
    try:
        result = subprocess.run(command, env=env, cwd=run_dir, capture_output=True,
                                text=True, timeout=args.timeout, check=False)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "")
        timed_out = True
    elapsed = time.perf_counter() - started
    (run_dir / "agent.stdout.jsonl").write_text(result.stdout or "")
    (run_dir / "agent.stderr.log").write_text(result.stderr or "")
    validation = validate(query_dir, run_dir)
    runtime = run_solution(run_dir, data_dir, "dfarena-agent-sandbox:latest", 3, args.timeout)
    metrics = {"status": "timeout" if timed_out else "completed", "agent_total_wall_time_sec": elapsed,
               "agent_returncode": result.returncode, "validation": validation,
               "solution_runtime": runtime, "token_usage": usage_from_json(result.stdout or ""),
               "finished_at": datetime.now(timezone.utc).isoformat()}
    write_json(run_dir / "metrics.json", metrics)
    print(json.dumps({"run_dir": str(run_dir), **metrics}, ensure_ascii=False))
    return 0 if validation["semantic_correct"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
