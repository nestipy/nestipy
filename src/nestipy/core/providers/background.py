from __future__ import annotations

import asyncio
import functools
import sys
import typing
from asyncio import Task

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

from starlette.concurrency import run_in_threadpool

P = ParamSpec("P")


def is_async_callable(obj: typing.Any) -> typing.Any:
    while isinstance(obj, functools.partial):
        obj = obj.func

    return asyncio.iscoroutinefunction(obj) or (
            callable(obj) and asyncio.iscoroutinefunction(getattr(obj, "__call__"))
    )


class BackgroundTask:
    def __init__(
            self, func: typing.Callable[P, typing.Any], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = is_async_callable(func)

    async def __call__(self) -> None:
        if self.is_async:
            await self.func(*self.args, **self.kwargs)
        else:
            await run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks:
    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.is_running = False
        self.worker_task: typing.Union[Task, None] = None

    def add_task(
            self, func: typing.Callable[P, typing.Any], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        task = BackgroundTask(func, *args, **kwargs)
        self.add(task)

    def add(self, task: BackgroundTask) -> None:
        self.queue.put_nowait(task)

    async def _worker(self) -> None:
        while self.is_running:
            task = await self.queue.get()
            try:
                await task()
            except Exception as e:
                print(f"Task failed: {e}")
            finally:
                self.queue.task_done()
            await asyncio.sleep(1)

    def run(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.get_running_loop().create_task(self._worker())

    async def shutdown(self) -> None:
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
        await self.queue.join()
