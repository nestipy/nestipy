from typing import Annotated

import pytest

from nestipy.common import Injectable, Module, Controller, Get, UsePipes
from nestipy.common.pipes import PipeTransform, PipeArgumentMetadata, ParseIntPipe
from nestipy.core import ExecutionContext, AppKey
from nestipy.ioc import NestipyContainer, RequestContextContainer, Query, ModuleProviderDict
from nestipy.common.exception.http import HttpException
from nestipy.common.http_ import Request, Response


@Injectable()
class MultiplyPipe(PipeTransform):
    async def transform(self, value: str, metadata: PipeArgumentMetadata) -> int:
        return int(value) * 2


@pytest.mark.asyncio
async def test_pipe_applied_to_query_param():
    NestipyContainer.clear()
    container = NestipyContainer.get_instance()

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"value=3",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    req = Request(scope, receive, send)
    res = Response()

    async def handler(value: Annotated[int, Query("value")]):
        return value

    ctx = ExecutionContext(None, None, None, handler, req, res)
    ctx.set_pipes([MultiplyPipe])
    RequestContextContainer.set_execution_context(ctx)

    args = await container._get_method_dependency(handler, [])
    assert args["value"] == 6


@pytest.mark.asyncio
async def test_param_pipe_applied_when_global_empty():
    NestipyContainer.clear()
    container = NestipyContainer.get_instance()

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"value=4",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    req = Request(scope, receive, send)
    res = Response()

    async def handler(value: Annotated[int, Query("value", MultiplyPipe)]):
        return value

    ctx = ExecutionContext(None, None, None, handler, req, res)
    ctx.set_pipes([])
    RequestContextContainer.set_execution_context(ctx)

    args = await container._get_method_dependency(handler, [])
    assert args["value"] == 8


@pytest.mark.asyncio
async def test_pipe_order_global_module_controller_method_param():
    NestipyContainer.clear()
    container = NestipyContainer.get_instance()
    order: list[str] = []

    class GlobalPipe(PipeTransform):
        async def transform(self, value, metadata):
            order.append("global")
            return value

    class ModulePipe(PipeTransform):
        async def transform(self, value, metadata):
            order.append("module")
            return value

    class ClassPipe(PipeTransform):
        async def transform(self, value, metadata):
            order.append("class")
            return value

    class MethodPipe(PipeTransform):
        async def transform(self, value, metadata):
            order.append("method")
            return value

    class ParamPipe(PipeTransform):
        async def transform(self, value, metadata):
            order.append("param")
            return value

    @Controller("t")
    @UsePipes(ClassPipe)
    class TestController:
        @Get()
        @UsePipes(MethodPipe)
        async def handler(self, value: Annotated[str, Query("value", ParamPipe)]):
            return value

    @Module(
        providers=[
            ModuleProviderDict(token=AppKey.APP_PIPE, use_class=ModulePipe)
        ],
        controllers=[TestController],
    )
    class TestModule:
        pass

    class DummyAdapter:
        def __init__(self, global_pipes):
            self._global_pipes = global_pipes

        def get_global_pipes(self):
            return self._global_pipes

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"value=1",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    req = Request(scope, receive, send)
    res = Response()

    adapter = DummyAdapter([GlobalPipe])
    ctx = ExecutionContext(adapter, TestModule, TestController, TestController.handler, req, res)
    from nestipy.core.pipes.processor import PipeProcessor

    pipes = await PipeProcessor().get_pipes(ctx)
    ctx.set_pipes(pipes)
    RequestContextContainer.set_execution_context(ctx)

    args = await container._get_method_dependency(TestController.handler, [])
    assert args["value"] == "1"
    assert order == ["global", "module", "class", "method", "param"]


@pytest.mark.asyncio
async def test_pipe_error_returns_bad_request():
    NestipyContainer.clear()
    container = NestipyContainer.get_instance()

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"value=abc",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    req = Request(scope, receive, send)
    res = Response()

    async def handler(value: Annotated[int, Query("value", ParseIntPipe)]):
        return value

    ctx = ExecutionContext(None, None, None, handler, req, res)
    ctx.set_pipes([])
    RequestContextContainer.set_execution_context(ctx)

    with pytest.raises(HttpException) as exc:
        await container._get_method_dependency(handler, [])
    assert exc.value.status_code == 400
