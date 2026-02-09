import json as _json
from typing import Optional, Any

from nestipy.core.nestipy_application import NestipyApplication
from .helpers import TestResponse
from .simulator import TestSimulator


class TestClient:
    __test__ = False

    def __init__(self, app: NestipyApplication):
        self._simulator = TestSimulator(app)

    @staticmethod
    def _apply_json(
        headers: Optional[dict[str, str]], body: bytes, json_data: Optional[Any]
    ) -> tuple[Optional[dict[str, str]], bytes]:
        if json_data is None:
            return headers, body
        encoded = _json.dumps(json_data).encode("utf-8")
        if headers is None:
            headers = {}
        if not any(key.lower() == "content-type" for key in headers.keys()):
            headers["content-type"] = "application/json"
        return headers, encoded

    async def get(
        self, path: str, headers: Optional[dict[str, str]] = None, body: bytes = b""
    ) -> TestResponse:
        return await self._simulator.make_request("GET", path, headers, body)

    async def post(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
        body: bytes = b"",
        json: Optional[Any] = None,
    ) -> TestResponse:
        headers, body = self._apply_json(headers, body, json)
        return await self._simulator.make_request("POST", path, headers, body)

    async def put(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
        body: bytes = b"",
        json: Optional[Any] = None,
    ) -> TestResponse:
        headers, body = self._apply_json(headers, body, json)
        return await self._simulator.make_request("PUT", path, headers, body)

    async def delete(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
        body: bytes = b"",
        json: Optional[Any] = None,
    ) -> TestResponse:
        headers, body = self._apply_json(headers, body, json)
        return await self._simulator.make_request("DELETE", path, headers, body)

    async def options(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
        body: bytes = b"",
        json: Optional[Any] = None,
    ) -> TestResponse:
        headers, body = self._apply_json(headers, body, json)
        return await self._simulator.make_request("OPTIONS", path, headers, body)
