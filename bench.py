#!/usr/bin/env python3

# -------- Nestipy App --------
from nestipy.common.decorator import Controller, Get, Module
from nestipy.core import BlackSheepApplication, FastApiApplication
from nestipy.core.nestipy_factory import NestipyFactory


@Controller()
class AppController:
    @Get("/")
    async def root(self):
        return "ok"

    @Get("/cpu")
    async def cpu(self, ms: int = 2):
        end = time.perf_counter() + (ms / 1000.0)
        x = 0.0
        while time.perf_counter() < end:
            x = (x + 1.000001) % 1.234567
        return "ok"

    @Get("/io")
    async def io(self, ms: int = 5):
        await asyncio.sleep(ms / 1000.0)
        return "ok"


@Module(controllers=[AppController])
class AppModule: ...


async def run_server(host: str, port: int, workers: int, is_b: bool = False):
    import uvicorn
    if is_b:
        print("Running Black Sheep server .......")
        app = NestipyFactory[BlackSheepApplication].create(AppModule)
    else:
        print("Running Fastapi server .......")
        app = NestipyFactory[FastApiApplication].create(AppModule)
    config = uvicorn.Config(app=app, host=host, port=port, workers=workers, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


import asyncio
import httpx
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from argparse import ArgumentParser
import os


class Benchmark:
    def __init__(self, url: str, concurrency: int, duration: int):
        self.url = url
        self.concurrency = concurrency
        self.duration = duration
        self.latencies = []
        self.errors = 0
        self.timeline = defaultdict(list)  # per second latencies
        self.failures = defaultdict(int)

    async def worker(self, client: httpx.AsyncClient):
        while time.time() < self.end:
            t0 = time.time()
            try:
                r = await client.get(self.url)
                if r.status_code != 200:
                    self.errors += 1
                    self.failures[int(time.time() - self.start)] += 1
            except Exception:
                self.errors += 1
                self.failures[int(time.time() - self.start)] += 1
                continue
            dt = (time.time() - t0) * 1000
            self.latencies.append(dt)
            sec = int(time.time() - self.start)
            self.timeline[sec].append(dt)

    async def run(self):
        self.start = time.time()
        self.end = self.start + self.duration
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = [asyncio.create_task(self.worker(client)) for _ in range(self.concurrency)]
            await asyncio.gather(*tasks)

    def report(self, outdir="bench_out"):
        os.makedirs(outdir, exist_ok=True)

        lats = np.array(self.latencies)
        reqs = len(lats)
        duration = self.duration
        rps = reqs / duration

        # Stats
        stats = {
            "requests": reqs,
            "fails": self.errors,
            "avg": np.mean(lats),
            "min": np.min(lats),
            "max": np.max(lats),
            "rps": rps,
        }
        percentiles = {p: np.percentile(lats, p) for p in [50, 60, 70, 80, 90, 95, 99]}

        print("\n=== Request Statistics ===")
        print(f"Requests: {stats['requests']}, Fails: {stats['fails']}, "
              f"Avg: {stats['avg']:.2f} ms, Min: {stats['min']:.2f}, "
              f"Max: {stats['max']:.2f}, RPS: {stats['rps']:.2f}")

        print("\n=== Response Time Statistics (ms) ===")
        for p, v in percentiles.items():
            print(f"{p}th: {v:.2f}")

        # --- Charts ---
        times = sorted(self.timeline.keys())
        rps_series = [len(self.timeline[t]) for t in times]
        fail_series = [self.failures.get(t, 0) for t in times]

        # RPS vs Failures
        plt.figure(figsize=(8, 4))
        plt.plot(times, rps_series, marker="o", label="RPS", color="green")
        plt.plot(times, fail_series, marker="x", label="Failures/s", color="red")
        plt.xlabel("Time (s)")
        plt.ylabel("Requests per second")
        plt.title("Total Requests per Second")
        plt.legend()
        plt.savefig(f"{outdir}/rps.png")
        plt.close()

        # Response times (median + 95th percentile)
        medians = [np.median(self.timeline[t]) if self.timeline[t] else 0 for t in times]
        p95s = [np.percentile(self.timeline[t], 95) if self.timeline[t] else 0 for t in times]
        plt.figure(figsize=(8, 4))
        plt.plot(times, medians, label="Median Response Time", color="green")
        plt.plot(times, p95s, label="95% percentile", color="orange")
        plt.xlabel("Time (s)")
        plt.ylabel("Response Time (ms)")
        plt.title("Response Times")
        plt.legend()
        plt.savefig(f"{outdir}/response_times.png")
        plt.close()

        # Number of users (constant = concurrency)
        plt.figure(figsize=(8, 4))
        plt.plot(times, [self.concurrency] * len(times), label="Users", color="blue")
        plt.xlabel("Time (s)")
        plt.ylabel("Users")
        plt.title("Number of Users")
        plt.legend()
        plt.savefig(f"{outdir}/users.png")
        plt.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("serve")
    s1.add_argument("--port", type=int, default=8000);
    s1.add_argument("--workers", type=int, default=1)
    s1.add_argument("--is-bs", type=bool, default=False)
    s2 = sub.add_parser("bench")
    s2.add_argument("--url", type=str, required=True, help="Target URL")
    s2.add_argument("-c", "--concurrency", type=int, default=100)
    s2.add_argument("-d", "--duration", type=int, default=15)
    s2.add_argument("--out", type=str, default="bench_out")
    args = parser.parse_args()

    if args.cmd == "serve":
        asyncio.run(run_server("127.0.0.1", args.port, args.workers, args.is_bs))
    else:
        bench = Benchmark(args.url, args.concurrency, args.duration)
        asyncio.run(bench.run())
        bench.report(args.out)
