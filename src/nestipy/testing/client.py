from typing import Optional

from nestipy.core.nestipy_application import NestipyApplication
from .helpers import TestResponse
from .simulator import TestSimulator


class TestClient:
    __test__ = False

    def __init__(self, app: NestipyApplication):
        self._simulator = TestSimulator(app)

    async def get(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("GET", path, headers, body)

    async def post(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("POST", path, headers, body)

    async def put(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("PUT", path, headers, body)

    async def delete(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("DELETE", path, headers, body)

    async def options(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("OPTIONS", path, headers, body)
