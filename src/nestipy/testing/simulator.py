import asyncio
from typing import Optional
from urllib.parse import urlparse, parse_qs

from nestipy.core.nestipy_application import NestipyApplication
from .helpers import (
    HeadersType,
    QueryType,
    CookiesType,
    get_example_scope,
    TestResponse,
)


class TestSimulator:
    __test__ = False

    def __init__(self, app: NestipyApplication):
        self.app = app
        self.scope: dict = {}
        self.receive_queue = asyncio.Queue()
        self.send_queue = asyncio.Queue()

    @classmethod
    def _create_scope(
        cls,
        method: str,
        path: str,
        headers: Optional[HeadersType] = None,
        query: Optional[QueryType] = None,
        cookies: Optional[CookiesType] = None,
    ) -> dict:
        """Creates a mocked ASGI scope"""
        return get_example_scope(
            method, path, extra_headers=headers, query=query, cookies=cookies
        )

    async def _simulate_receive(self):
        return await self.receive_queue.get()

    async def _simulate_send(self, message: dict):
        await self.send_queue.put(message)

    @classmethod
    def _extract_query_params(cls, path) -> QueryType:
        parsed_url = urlparse(path)
        return parse_qs(parsed_url.query)

    async def make_request(
        self, method: str, path: str, headers: Optional[dict[str, str]] = None, body=b""
    ):
        if headers is not None:
            headers = [
                (key.encode("utf-8"), value.encode("utf-8")) for key, value in headers
            ]
        # app request
        self.scope = self._create_scope(
            method, urlparse(path).path, headers, query=self._extract_query_params(path)
        )
        await self.receive_queue.put(
            {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }
        )
        await self.app.setup()
        await self.app(self.scope, self._simulate_receive, self._simulate_send)
        response = []
        while not self.send_queue.empty():
            response.append(await self.send_queue.get())
        return TestResponse.from_dict(response)
