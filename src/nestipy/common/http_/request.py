from typing import Callable, Optional, Any
from urllib.parse import parse_qsl
from http import cookies as http_cookies
import ujson
from starlette.datastructures import UploadFile
from starlette.requests import Request as StarletteRequest

from .multipart import parse_content_header, parse_multipart_form, parse_url_encoded_form_data


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
        if scope["type"] == "http":
            self.starlette_request = StarletteRequest(scope, receive, send)

    @property
    def query_params(self) -> dict:
        if self._query_params is None:
            self._query_params = {k.decode(): v.decode() for k, v in
                                  dict(parse_qsl(self.scope["query_string"])).items()}
        return self._query_params

    @property
    def path_params(self) -> dict[str, Any]:
        return self.scope.get("path_params", {})

    @property
    def path(self) -> str:
        if self._path is None:
            self._path = self.scope.get('raw_path').decode()
        return self._path

    @property
    def method(self) -> str:
        if self._method is None:
            self._method = self.scope.get('method')
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
            host: tuple[str, int] = self.scope.get('server')
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

    def set_body(self, body: str):
        self._body = body

    async def body(self) -> str:
        if self._body is None:
            body = b""
            while True:
                message = await self.receive()
                body += message.get("body", b"")
                if not message.get("more_body", False):
                    break
            self._body = body
        return self._body.decode()

    async def files(self) -> list[UploadFile]:
        form_data = await self.starlette_request.form()
        return form_data.getlist('files')

    async def json(self) -> dict:
        if self._json is None:
            body = await self.body()
            try:
                self._json = ujson.loads('{}' if body == '' else body)
            except ujson.JSONDecodeError:
                self._json = {}
        return self._json

    @property
    def content_type(self) -> tuple[str, dict[str, str]]:
        _content_type = self.headers.get("content-type", "")
        return parse_content_header(
            _content_type
        )

    async def form(self) -> dict:
        if self._form is None:
            content_type, options = self.content_type
            if content_type == "multipart/form-data":
                self._form = parse_multipart_form(
                    body=(await self.body()).encode(),
                    boundary=options.get("boundary", "").encode(),
                    multipart_form_part_limit=1000,
                )
            elif content_type == "application/x-www-form-urlencoded":
                self._form = parse_url_encoded_form_data(
                    (await self.body()).encode(),
                )
            else:
                self._form = None
        return self._form

    @property
    def cookies(self) -> dict[str, str]:
        if not hasattr(self, "_cookies"):
            cookies: dict[str, str] = {}
            cookie_header = self.headers.get("cookie")

            if cookie_header:
                cookies = cookie_parser(cookie_header)
            self._cookies = cookies
        return self._cookies
