This page describes a repeatable way to benchmark Nestipy adapters (FastAPI vs BlackSheep) and track changes over time. The goal is to keep the setup simple, deterministic, and close to how Nestipy is used in real projects while still isolating adapter performance.

## What This Measures

The benchmark focuses on:

- End-to-end request latency (p50/p95/p99).
- Throughput (requests per second).
- Error rate.

It runs a small Nestipy app with three endpoints:

- `/` for a fast, mostly empty handler.
- `/cpu` for a short CPU-bound loop.
- `/io` for a short async sleep.

This gives you a mix of fast-path, CPU-bound, and async I/O behavior.

## Goals

- Same machine, same Python, same dependencies.
- Same endpoints and load profile.
- Multiple trials with warmup.
- Compare median p50/p95/p99 + RPS + failures.

## Requirements

- `uv` or `python3`
- `granian` (used by `bench.py serve`)

If you already have servers running, you can skip `granian` and use `--no-start`.

## Quick Start

There are two modes:

- Manual: start one server, benchmark it.
- Comparison runner: start both servers, warmup, run multiple trials, save summary JSON.

### 1) Run a single server

```bash
uv run python bench.py serve --port 8000 --workers 5 --is-bs False
```

Then benchmark it:

```bash
uv run python bench.py bench --url http://127.0.0.1:8000/ -c 200 -d 20 --out bench_out/fastapi_root
uv run python bench.py bench --url http://127.0.0.1:8000/cpu?ms=2 -c 200 -d 20 --out bench_out/fastapi_cpu
uv run python bench.py bench --url http://127.0.0.1:8000/io?ms=5 -c 200 -d 20 --out bench_out/fastapi_io
```

Repeat for BlackSheep by switching `--is-bs True` and using another port.

### 2) Automated comparison

Use the comparison runner to do warmup + multiple trials and save a JSON report.

```bash
uv run python bench_compare.py --workers 5 -c 200 -d 20 --trials 3 --warmup 5 --out bench_out
```

There is a convenience script that wraps the comparison runner:

```bash
./scripts/benchmark.sh --workers 5 -c 200 -d 20 --trials 3 --warmup 5 --out bench_out
```

Defaults benchmark these endpoints:

- `/`
- `/cpu?ms=2`
- `/io?ms=5`

Override endpoints with `--endpoint` (repeatable):

```bash
uv run python bench_compare.py --endpoint / --endpoint /users --endpoint /cpu?ms=5
```

If you already started servers yourself, add `--no-start` and set ports.

```bash
uv run python bench_compare.py --no-start --fastapi-port 8000 --blacksheep-port 8001
```

## Output

The comparison runner writes:

- `bench_out/bench_compare.json` with median stats across trials.

The single benchmark run (`bench.py bench`) writes charts:

- `rps.png` requests per second over time
- `response_times.png` median and p95 latency over time
- `users.png` concurrent users over time

## How To Read The Results

- Prefer median across multiple trials instead of a single run.
- Look at p95 and p99 for tail latency, not only average.
- Compare failures as well as speed. Fast but error-prone is not a win.

## Reproducibility Tips

- Always run benchmarks on an idle machine.
- Pin the same Python version, dependencies, and OS.
- Keep the same concurrency and duration between runs.
- Keep the same CPU governor and power profile when possible.
- Restart servers between large test changes to avoid warm caches.

## Common Pitfalls

- Comparing one-off runs. Always use multiple trials.
- Changing concurrency or duration mid-comparison.
- Running other CPU-heavy tasks in parallel.
- Comparing results from different hardware.

## Extending The Benchmark

If you add endpoints to your app:

- Update `bench.py` with the new handlers.
- Pass `--endpoint` to `bench_compare.py` to include them.

Example:

```bash
uv run python bench_compare.py --endpoint / --endpoint /users --endpoint /cpu?ms=5
```
