import typing
from http import cookies as http_cookies
from typing import Callable, Optional, Any
from urllib.parse import parse_qsl

import ujson
from multipart.multipart import parse_options_header
from starlette._utils import AwaitableOrContextManagerWrapper, AwaitableOrContextManager
from starlette.requests import Request as StarletteRequest

from .form_parsers import MultiPartParser, MultiPartException, FormParser, FormData
from .multipart import parse_content_header


def cookie_parser(cookie_string: str) -> dict[str, str]:
    cookie_dict: dict[str, str] = {}
    for chunk in cookie_string.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            cookie_dict[key] = http_cookies._unquote(val)
    return cookie_dict


class ClientDisconnect(Exception):
    pass


class Request:
    def __init__(self, scope: dict, receive: Callable, send: Callable) -> None:
        self.scope = scope
        self.receive = receive
        self.send = receive
        self._query_params = None
        self._headers: Optional[dict] = None
        self._path = None
        self._method = None
        self._client = None
        self._host = None
        self._body = None
        self._json = None
        self._files = None
        self._user = None
        self._form = None
        self._session = None
        self._cookies = None
        self._stream_consumed = False
        self._is_disconnected = False
        if scope["type"] == "http":
            self.starlette_request = StarletteRequest(scope, receive, send)

    @property
    def query_params(self) -> dict:
        if self._query_params is None:
            self._query_params = {
                k.decode(): v.decode()
                for k, v in dict(parse_qsl(self.scope["query_string"])).items()
            }
        return self._query_params

    @property
    def path_params(self) -> dict[str, Any]:
        return self.scope.get("path_params", {})

    @property
    def path(self) -> str:
        if self._path is None:
            self._path = self.scope.get("raw_path").decode()
        return self._path

    @property
    def method(self) -> str:
        if self._method is None:
            self._method = self.scope.get("method")
        return self._method

    @property
    def user(self) -> Any:
        return self._user

    @user.setter
    def user(self, u: Any):
        self._user = u

    @property
    def host(self) -> str:
        if self._host is None:
            host: tuple[str, int] = self.scope.get("server")
            self._host = f"{self.scope.get('scheme')}://{host[0]}:{host[1]}"
        return self._host

    @property
    def headers(self) -> dict:
        if self._headers is None:
            self._headers = {}
            scope_headers: list[tuple[bytes, bytes]] = list(self.scope["headers"])
            for key, value in scope_headers:
                self._headers[key.decode()] = value.decode()
        return self._headers

    @property
    def client(self) -> list:
        if self._client is None:
            self._client = self.scope.get("client", ())
        return self._client

    @property
    def session(self) -> dict:
        if self._session is None:
            self._session = {}
        return self._session

    @session.setter
    def session(self, session: dict):
        self._session = session

    async def stream(self) -> typing.AsyncGenerator[bytes, None]:
        """
        Returns:
            stream: A stream generator value form request
        """
        if self._body is not None:
            yield self._body
            yield b""
            return
        if self._stream_consumed:
            raise RuntimeError("Stream consumed")
        while not self._stream_consumed:
            message = await self.receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if not message.get("more_body", False):
                    self._stream_consumed = True
                if body:
                    yield body
            elif message["type"] == "http.disconnect":
                self._is_disconnected = True
                raise ClientDisconnect()
        yield b""

    async def body(self) -> bytes:
        """
        Returns:
            body(bytes): Return bytes version of request body
        """
        if self._body is None:
            chunks: list[bytes] = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> typing.Any:
        """

        Returns:
            json(dict): Return json value of request body
        """
        if self._json is None:
            body = await self.body()
            try:
                self._json = ujson.loads("{}" if body == "" else body)
            except ujson.JSONDecodeError:
                self._json = {}
        return self._json

    @property
    def content_type(self) -> tuple[str, dict[str, str]]:
        """

        Returns:
            content_type: Content-Type of request body
        """
        _content_type = self.headers.get("content-type", "")
        return parse_content_header(_content_type)

    def form(
        self, *, max_files: int | float = 1000, max_fields: int | float = 1000
    ) -> AwaitableOrContextManager[FormData]:
        return AwaitableOrContextManagerWrapper(
            self._get_form(max_files=max_files, max_fields=max_fields)
        )

    async def _get_form(
        self, *, max_files: int | float = 1000, max_fields: int | float = 1000
    ) -> FormData:
        if self._form is None:
            assert (
                parse_options_header is not None
            ), "The `python-multipart` library must be installed to use form parsing."
            content_type_header = self.headers.get("content-type")
            content_type: bytes
            content_type, _ = parse_options_header(content_type_header)
            if content_type == b"multipart/form-data":
                try:
                    multipart_parser = MultiPartParser(
                        self.headers,
                        self.stream(),
                        max_files=max_files,
                        max_fields=max_fields,
                    )
                    self._form = await multipart_parser.parse()
                except MultiPartException as exc:
                    raise exc
            elif content_type == b"application/x-www-form-urlencoded":
                form_parser = FormParser(self.headers, self.stream())
                self._form = await form_parser.parse()
            else:
                self._form = FormData()
        return self._form

    @property
    def cookies(self) -> dict[str, str]:
        if self._cookies is None:
            cookies: dict[str, str] = {}
            cookie_header = self.headers.get("cookie")
            if cookie_header:
                cookies = cookie_parser(cookie_header)
            self._cookies = cookies
        return self._cookies
