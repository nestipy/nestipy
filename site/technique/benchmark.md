This page describes a repeatable way to compare Nestipy adapters (FastAPI vs BlackSheep) and changes over time.

## Goals

- Same machine, same Python, same dependencies.
- Same endpoints and load profile.
- Multiple trials with warmup.
- Compare median p50/p95/p99 + RPS + failures.

## Quick Start

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

## Notes

- Always run benchmarks on an idle machine.
- Keep the same concurrency and duration between runs.
- Compare median of multiple trials for stable results.
