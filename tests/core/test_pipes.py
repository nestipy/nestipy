from typing import Annotated

import pytest

from nestipy.common import Injectable
from nestipy.common.pipes import PipeTransform, PipeArgumentMetadata
from nestipy.core import ExecutionContext
from nestipy.ioc import NestipyContainer, RequestContextContainer, Query
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
