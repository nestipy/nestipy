import json
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from typing import Sequence, Union
from urllib.parse import quote, urlencode

_DEFAULT_AGENT = (
    b"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"
)

_DEFAULT_ACCEPT = b"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

_DEFAULT_ACCEPT_LANGUAGE = b"en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7"

_DEFAULT_ACCEPT_ENCODING = b"gzip, deflate"


def _get_tuple(value: Union[List, Tuple[str, int]]) -> tuple:
    if isinstance(value, tuple):
        return value
    assert len(value) == 2
    return tuple(value)  # type: ignore


HeadersType = Union[None, Sequence[Tuple[bytes, bytes]], Dict[str, str]]
CookiesType = Union[None, Sequence[Tuple[bytes, bytes]], Dict[str, str]]
QueryType = Union[None, bytes, str, dict, list]


def get_example_scope(
    method: str,
    path: str,
    extra_headers: HeadersType = None,
    *,
    query: QueryType = None,
    scheme: str = "http",
    server: Union[None, List, Tuple[str, int]] = None,
    client: Union[None, List, Tuple[str, int]] = None,
    user_agent: bytes = _DEFAULT_AGENT,
    accept: bytes = _DEFAULT_ACCEPT,
    accept_language: bytes = _DEFAULT_ACCEPT_LANGUAGE,
    accept_encoding: bytes = _DEFAULT_ACCEPT_ENCODING,
    cookies: CookiesType = None,
):
    """Returns a mocked ASGI scope"""
    if "?" in path:
        raise ValueError(
            "The path in ASGI messages does not contain query string, "
            "use the `query` parameter"
        )

    if server is None:
        server = ("127.0.0.1", 8000)
    else:
        server = _get_tuple(server)

    if client is None:
        client = ("127.0.0.1", 51492)
    else:
        client = _get_tuple(client)

    server_port = server[1]
    if scheme == "http" and server_port == 80:
        port_part = ""
    elif scheme == "https" and server_port == 443:
        port_part = ""
    else:
        port_part = f":{server_port}"

    host = f"{server[0]}{port_part}"

    if isinstance(extra_headers, dict):
        extra_headers = [
            (key.encode(), value.encode()) for key, value in extra_headers.items()
        ]

    query_string: bytes = b""
    if query:
        if isinstance(query, list):
            query = dict(query)
        if isinstance(query, dict):
            query_string = urlencode(query).encode()
        if isinstance(query, str):
            query_string = query.encode()
        if isinstance(query, bytes):
            query_string = query

    cookies_headers: List[Tuple[bytes, bytes]] = []

    if cookies:
        if isinstance(cookies, list):
            cookies_headers = [
                (b"cookie", quote(key).encode() + b"=" + quote(value).encode())
                for key, value in cookies
            ]
        elif isinstance(cookies, dict):
            cookies_headers = [
                (b"cookie", quote(key).encode() + b"=" + quote(value).encode())
                for key, value in cookies.items()
            ]

    headers = (
        [
            (b"host", host.encode()),
            (b"user-agent", user_agent),
            (b"accept", accept),
            (b"accept-language", accept_language),
            (b"accept-encoding", accept_encoding),
            (b"connection", b"keep-alive"),
            (b"upgrade-insecure-requests", b"1"),
        ]
        + ([tuple(header) for header in extra_headers] if extra_headers else [])
        + cookies_headers
    )

    return {
        "type": scheme,
        "http_version": "1.1",
        "server": tuple(server),
        "client": client,
        "scheme": scheme,
        "method": method,
        "root_path": "",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "headers": headers,
    }


@dataclass
class HTTPBody:
    type: str
    body: bytes


@dataclass
class HTTPResponse:
    type: str
    status: int
    headers: List[Tuple[bytes, bytes]]
    body: HTTPBody


@dataclass
class TestResponse:
    response: HTTPResponse
    raw_response: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, response: List[Dict[str, Any]]) -> "TestResponse":
        response_body = HTTPBody(type=response[1]["type"], body=response[1]["body"])
        http_response = HTTPResponse(
            type=response[0]["type"],
            status=response[0]["status"],
            headers=response[0]["headers"],
            body=response_body,
        )
        return cls(raw_response=response, response=http_response)

    def status(self) -> int:
        return self.response.status

    def get_headers(self) -> Dict[str, str]:
        headers = {}
        for key, value in self.response.headers:
            headers[key.decode("utf-8")] = value.decode("utf-8")
        return headers

    def body(self) -> bytes:
        return self.response.body.body

    def json(self) -> Any:
        try:
            return json.loads(self.body())
        except json.JSONDecodeError:
            return None
