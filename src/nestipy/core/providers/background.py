from __future__ import annotations

import asyncio
import functools
import sys
import typing
import uuid
from asyncio import Task
from enum import Enum

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

from starlette.concurrency import run_in_threadpool

P = ParamSpec("P")


class TaskStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


def is_async_callable(obj: typing.Any) -> typing.Any:
    while isinstance(obj, functools.partial):
        obj = obj.func
    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(getattr(obj, "__call__", None))
    )


class BackgroundTask:
    def __init__(
        self,
        func: typing.Callable[P, typing.Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self.task_id = str(uuid.uuid4())
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = is_async_callable(func)
        self.status: TaskStatus = TaskStatus.PENDING
        self.error: typing.Optional[str] = None

    async def __call__(self) -> None:
        self.status = TaskStatus.STARTED
        try:
            if self.is_async:
                await self.func(*self.args, **self.kwargs)
            else:
                await run_in_threadpool(self.func, *self.args, **self.kwargs)
            self.status = TaskStatus.SUCCESS
        except asyncio.CancelledError:
            self.status = TaskStatus.CANCELLED
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            print(f"Task {self.task_id} failed: {e}")


class BackgroundTasks:
    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.is_running = False
        self.worker_task: typing.Optional[Task] = None
        self.tasks: dict[str, BackgroundTask] = {}

    def add_task(
        self,
        func: typing.Callable[P, typing.Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str:
        task = BackgroundTask(func, *args, **kwargs)
        return self.add(task)

    def add(self, task: BackgroundTask) -> str:
        task_id = task.task_id
        self.tasks[task_id] = task
        self.queue.put_nowait(task)
        return task_id

    async def _worker(self) -> None:
        while self.is_running:
            task = await self.queue.get()
            try:
                await task()
            finally:
                self.queue.task_done()
            await asyncio.sleep(0.1)

    def run(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.get_running_loop().create_task(self._worker())

    async def shutdown(self) -> None:
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
        await self.queue.join()

    def get_status(self, task_id: str) -> typing.Optional[dict[str, typing.Any]]:
        task = self.tasks.get(task_id)
        if task:
            return {
                "id": task.task_id,
                "status": task.status,
                "error": task.error,
            }
        return {
            "id": task_id,
            "status": TaskStatus.CANCELLED,
            "error": "Task not found",
        }

    def all_tasks(self) -> list[dict[str, typing.Any]]:
        return [
            {
                "id": task.task_id,
                "status": task.status,
                "error": task.error,
            }
            for task in self.tasks.values()
        ]
