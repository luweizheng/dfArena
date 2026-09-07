#!/usr/bin/env python3
"""
Test Script

Run one DataAgentBench-style dataframe task with Codex in Docker.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import time
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BACKENDS = {
    "pandas": (
        "Use pandas as the main dataframe backend for loading, transformation, "
        "and computation."
    ),
    "polars": (
        "Use Polars as the main dataframe backend for loading, transformation, "
        "and computation. Do not use pandas for the main dataframe logic. "
        "Pandas may be used only for an explicit boundary interoperability step "
        "when required, not to perform the workflow computation."
    ),
    "ibis": (
        "Use Ibis with DuckDB as the main dataframe backend for loading, filtering, "
        "joins, aggregation, sorting, and date handling. Keep relational computation "
        "lazy until final materialization where practical. Do not use pandas "
        "for the main dataframe logic. Pandas may be used only for a small final "
        "boundary conversion when required, not to perform the workflow computation."
    ),
}
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = "dfarena-agent-sandbox:latest"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def docker_available() -> bool:
    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, check=False
    )
    return result.returncode == 0


def next_run(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    ids = [int(p.name[1:]) for p in root.glob("r[0-9][0-9][0-9]")]
    out = root / f"r{max(ids, default=0) + 1:03d}"
    out.mkdir()
    return out


def usage_from_jsonl(text: str) -> dict:
    for line in reversed(text.splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
            return {"available": True, "source": "codex_jsonl", **usage}
    return {"available": False, "source": "codex_jsonl_missing_turn_usage"}

def usage_from_local_new_api(start: float, end: float) -> dict:
    key = os.environ.get("LOCALNEW_API_KEY")
    if not key:
        p = Path.home() / ".codex-bench" / "api_key"
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("LOCALNEW_API_KEY="):
                    key = line.split("=", 1)[1].strip(); break
    if not key:
        return {"available": False, "source": "local_new_api_missing_key"}
    items, page = [], 0
    while True:
        q = urllib.parse.urlencode({"p": page, "type": 2, "start_timestamp": int(start-10), "end_timestamp": int(end+10)})
        req = urllib.request.Request(f"http://127.0.0.1:3000/api/log/self?{q}", headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=15) as resp: data = json.load(resp).get("data", {})
        batch = data.get("items", []); items.extend(batch)
        if len(items) >= data.get("total", len(items)) or not batch: break
        page += 1
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "cache_tokens": 0, "cache_creation_tokens": 0, "quota": 0}
    items = [item for item in items if item.get("model_name") or item.get("prompt_tokens")
             or item.get("completion_tokens") or item.get("quota")]
    for item in items:
        other = item.get("other", {})
        if isinstance(other, str):
            try: other = json.loads(other)
            except json.JSONDecodeError: other = {}
        totals["prompt_tokens"] += int(item.get("prompt_tokens", 0) or 0)
        totals["completion_tokens"] += int(item.get("completion_tokens", 0) or 0)
        totals["quota"] += int(item.get("quota", 0) or 0)
        totals["cache_tokens"] += int(other.get("cache_tokens", 0) or 0)
        totals["cache_creation_tokens"] += int(other.get("cache_creation_tokens", 0) or 0)
    totals["total_tokens"] = totals["prompt_tokens"] + totals["completion_tokens"]
    totals["cost_usd"] = totals["quota"] / 1_000_000
    return {"available": True, "source": "local_new_api", "request_count": len(items), **totals}


def task_paths(benchmark: Path, task_name: str) -> tuple[Path, Path, Path, Path]:
    """Resolve the public task file, hidden answer directory, and data directory."""
    task_dir = benchmark / task_name
    if not task_dir.is_dir():
        raise FileNotFoundError(f"task directory not found: {task_dir}")
    task_file = task_dir / "task.json"
    if not task_file.exists():
        task_file = task_dir / "query.json"
    answer_dir = task_dir / "answer"
    if not answer_dir.is_dir():
        answer_dir = task_dir
    data_dir = benchmark / "data"
    if not data_dir.is_dir():
        data_dir = benchmark / "query_dataset"
    return task_dir, task_file, answer_dir, data_dir


def validate(answer_dir: Path, run_dir: Path) -> dict:
    try:
        payload = json.loads((run_dir / "answer.json").read_text())
        answer = payload["answer"]
        if not isinstance(answer, str):
            raise TypeError("answer must be a string")
        spec = importlib.util.spec_from_file_location("task_validator", answer_dir / "validate.py")
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        passed, message = module.validate(answer)
        return {"format_correct": True, "semantic_correct": bool(passed), "message": str(message)}
    except Exception as exc:
        return {"format_correct": False, "semantic_correct": False, "message": str(exc)}


def run_solution(run_dir: Path, data_dir: Path, image: str, repetitions: int, timeout: int) -> dict:
    command = ["docker", "run", "--rm", "-v", f"{run_dir.resolve()}:/workspace/output:rw",
               "-v", f"{data_dir.resolve()}:/workspace/input:ro", "-w", "/workspace/output",
               image, "python", "solution.py"]
    samples, errors = [], []
    for index in range(repetitions + 1):
        start = time.perf_counter()
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
            elapsed = time.perf_counter() - start
            if result.returncode:
                errors.append({"phase": "solution", "attempt": index + 1, "returncode": result.returncode,
                               "stderr": result.stderr[-4000:]})
            elif index > 0:
                samples.append(elapsed)
        except subprocess.TimeoutExpired as exc:
            errors.append({"phase": "solution", "attempt": index + 1, "error": f"timeout: {exc}"})
    return {"warmup": 1, "repetitions": repetitions, "samples_sec": samples,
            "median_sec": sorted(samples)[len(samples) // 2] if samples else None, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--task", required=True, help="Task directory name, e.g. task1")
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument(
        "--codex-config-dir",
        default="~/.codex-bench",
        help="Codex config directory to mount for the benchmark agent",
    )
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--runtime-repetitions", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not docker_available():
        raise RuntimeError(
            "Docker daemon is not available. Start Docker Desktop and retry."
        )

    benchmark = args.benchmark.resolve()
    task_dir, task_file, answer_dir, data_dir = task_paths(benchmark, args.task)
    run_dir = next_run(benchmark / "runs" / args.backend / args.task)
    prompt = (ROOT / "prompt" / "goal_to_answer_backend.md").read_text()
    prompt = prompt.replace("{backend_instructions}", BACKENDS[args.backend])
    run_config = {"benchmark": str(benchmark), "task": args.task, "task_file": str(task_file), "backend": args.backend,
                  "agent": "codex", "model": args.model, "docker_image": args.image,
                  "timeout_sec": args.timeout, "runtime_repetitions": args.runtime_repetitions,
                  "started_at": datetime.now(timezone.utc).isoformat()}
    write_json(run_dir / "run.json", run_config)
    if args.dry_run:
        print(run_dir)
        return 0

    config_dir = Path(args.codex_config_dir).expanduser().resolve()
    shell = "set -o pipefail; codex exec --json --sandbox danger-full-access --skip-git-repo-check "
    if args.model:
        shell += f"--model {shlex.quote(args.model)} "
    shell += "-o /workspace/output/last_message.json - < /workspace/output/prompt.txt"
    command = ["docker", "run", "--rm", "--add-host=host.docker.internal:host-gateway",
               "-v", f"{task_file}:/workspace/task.json:ro",
               "-v", f"{data_dir}:/workspace/input:ro", "-v", f"{run_dir}:/workspace/output:rw",
               "-v", f"{config_dir}:/root/.codex:rw", "-w", "/workspace", args.image, "bash", "-lc", shell]
    insert_at = command.index("-w")
    for visible_name in ("schema.yaml", "hints.md", "context.md"):
        visible_path = benchmark / visible_name
        if visible_path.exists():
            command[insert_at:insert_at] = ["-v", f"{visible_path}:/workspace/{visible_name}:ro"]
            insert_at += 2
    (run_dir / "prompt.txt").write_text(prompt)
    task_started = time.time()
    started = time.perf_counter()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout, check=False)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "")
        timed_out = True
    agent_elapsed = time.perf_counter() - started
    (run_dir / "agent.stdout.jsonl").write_text(result.stdout or "")
    (run_dir / "agent.stderr.log").write_text(result.stderr or "")
    task_finished = time.time()
    validation = validate(answer_dir, run_dir)
    runtime = run_solution(run_dir, data_dir, args.image, args.runtime_repetitions, args.timeout)
    errors = []
    if timed_out:
        errors.append({"phase": "agent", "error": "timeout"})
    if result.returncode:
        errors.append({"phase": "agent", "returncode": result.returncode})
    errors.extend(runtime["errors"])
    if not validation["semantic_correct"]:
        errors.append({"phase": "validation", "message": validation["message"]})
    with (run_dir / "errors.jsonl").open("w") as f:
        for error in errors:
            f.write(json.dumps(error, ensure_ascii=False) + "\n")
    metrics = {"status": "timeout" if timed_out else "completed", "agent_total_wall_time_sec": agent_elapsed,
               "agent_returncode": result.returncode, "solution_runtime": runtime,
               "validation": validation, "token_usage": usage_from_local_new_api(task_started, task_finished),
               "codex_token_usage": usage_from_jsonl(result.stdout or ""),
               "finished_at": datetime.now(timezone.utc).isoformat()}
    write_json(run_dir / "metrics.json", metrics)
    print(json.dumps({"run_dir": str(run_dir), **metrics}, ensure_ascii=False))
    return 0 if validation["semantic_correct"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
