#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict
from typing import Any

import httpx
import numpy as np

from bench import Benchmark


def wait_ready(url: str, timeout: int = 20) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Server not ready at {url} after {timeout}s")


async def run_benchmark(url: str, concurrency: int, duration: int) -> dict[str, Any]:
    bench = Benchmark(url, concurrency, duration)
    await bench.run()
    latencies = np.array(bench.latencies)
    if len(latencies) == 0:
        return {
            "requests": 0,
            "fails": bench.errors,
            "avg_ms": 0.0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "rps": 0.0,
        }
    return {
        "requests": int(len(latencies)),
        "fails": int(bench.errors),
        "avg_ms": float(np.mean(latencies)),
        "min_ms": float(np.min(latencies)),
        "max_ms": float(np.max(latencies)),
        "p50_ms": float(np.percentile(latencies, 50)),
        "p95_ms": float(np.percentile(latencies, 95)),
        "p99_ms": float(np.percentile(latencies, 99)),
        "rps": float(len(latencies) / bench.duration),
    }


def aggregate_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    if not trials:
        return {}
    keys = trials[0].keys()
    agg = {}
    for key in keys:
        values = [t[key] for t in trials]
        agg[key] = float(np.median(values))
    return agg


def start_server(port: int, workers: int, is_bs: bool) -> subprocess.Popen:
    cmd = [
        sys.executable,
        "bench.py",
        "serve",
        "--port",
        str(port),
        "--workers",
        str(workers),
        "--is-bs",
        str(is_bs),
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def stop_server(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def print_summary(results: dict[str, Any]) -> None:
    print("\n=== Benchmark Summary (median across trials) ===")
    for server, endpoints in results.items():
        print(f"\n[{server}]")
        for endpoint, stats in endpoints.items():
            print(
                f"{endpoint:<15} rps={stats['rps']:.2f} "
                f"p50={stats['p50_ms']:.2f}ms p95={stats['p95_ms']:.2f}ms "
                f"p99={stats['p99_ms']:.2f}ms fails={stats['fails']}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark comparison runner")
    parser.add_argument("--fastapi-port", type=int, default=8000)
    parser.add_argument("--blacksheep-port", type=int, default=8001)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("-c", "--concurrency", type=int, default=200)
    parser.add_argument("-d", "--duration", type=int, default=20)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument(
        "--endpoint",
        action="append",
        default=["/", "/cpu?ms=2", "/io?ms=5"],
        help="Endpoint path to benchmark (repeatable).",
    )
    parser.add_argument("--out", type=str, default="bench_out")
    parser.add_argument("--no-start", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    servers = {
        "fastapi": {"port": args.fastapi_port, "is_bs": False},
        "blacksheep": {"port": args.blacksheep_port, "is_bs": True},
    }

    processes = {}
    try:
        if not args.no_start:
            for name, cfg in servers.items():
                processes[name] = start_server(cfg["port"], args.workers, cfg["is_bs"])
            for name, cfg in servers.items():
                wait_ready(f"http://127.0.0.1:{cfg['port']}/")

        results: dict[str, Any] = {"fastapi": {}, "blacksheep": {}}

        for name, cfg in servers.items():
            base_url = f"http://127.0.0.1:{cfg['port']}"
            for endpoint in args.endpoint:
                url = f"{base_url}{endpoint}"
                if args.warmup > 0:
                    asyncio.run(run_benchmark(url, args.concurrency, args.warmup))
                trials = []
                for _ in range(args.trials):
                    stats = asyncio.run(
                        run_benchmark(url, args.concurrency, args.duration)
                    )
                    trials.append(stats)
                results[name][endpoint] = aggregate_trials(trials)

        out_path = os.path.join(args.out, "bench_compare.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print_summary(results)
        print(f"\nSaved results to {out_path}")

    finally:
        for proc in processes.values():
            stop_server(proc)


if __name__ == "__main__":
    main()
