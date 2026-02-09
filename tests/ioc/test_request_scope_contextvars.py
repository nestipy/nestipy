import asyncio

import pytest

from nestipy.common import Injectable, Scope
from nestipy.common.http_ import Request, Response
from nestipy.core import ExecutionContext
from nestipy.ioc import NestipyContainer, RequestContextContainer


@pytest.mark.asyncio
async def test_request_scope_isolated_between_tasks():
    NestipyContainer.clear()
    container = NestipyContainer.get_instance()

    @Injectable(scope=Scope.Request)
    class RequestScopedService:
        pass

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    async def task_run():
        req = Request(scope, receive, send)
        res = Response()
        ctx = ExecutionContext(None, None, None, None, req, res)
        RequestContextContainer.set_execution_context(ctx)
        svc = await container.get(RequestScopedService)
        return svc

    svc1, svc2 = await asyncio.gather(task_run(), task_run())
    assert svc1 is not svc2
