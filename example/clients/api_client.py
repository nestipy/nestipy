from __future__ import annotations

import dataclasses
import inspect
import typing
from typing import TypedDict, Required, NotRequired

try:
    import httpx  # type: ignore
except Exception:
    httpx = None
try:
    import requests  # type: ignore
except Exception:
    requests = None


def _jsonify(value: typing.Any) -> typing.Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, dict):
        return {k: _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value

def _normalize_mapping(value: typing.Any) -> typing.Optional[dict[str, typing.Any]]:
    if value is None:
        return None
    payload = _jsonify(value)
    if isinstance(payload, dict):
        return payload
    return None

def _encode_cookies(cookies: dict[str, typing.Any]) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def _join_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not base_url:
        return path
    return base_url.rstrip("/") + "/" + path.lstrip("/")


AppControllerPostBody = TestBody

class AppControllerTestHeaders(TypedDict, total=False):
    headers: Required[dict[str, typing.Any]]

class AppControllerTestCookies(TypedDict, total=False):
    cookies: Required[dict[str, typing.Any]]

class UserControllerGetUserHeaders(TypedDict, total=False):
    headers: Required[dict[str, typing.Any]]

class ApiClient:
    def __init__(
        self,
        base_url: str,
        client: typing.Any = None,
        request: typing.Optional[typing.Callable[..., typing.Any]] = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._owns_client = False
        if request is not None:
            self._requester = request
        else:
            if client is None:
                self._client = self._build_default_client(async_client=False)
                self._owns_client = True
            if not hasattr(self._client, "request"):
                raise TypeError("Client must provide a request(method, url, ...) method")
            self._requester = self._client.request

    def _build_default_client(self, async_client: bool = False):
        if async_client:
            if httpx is None:
                raise RuntimeError("httpx is required for async clients")
            return httpx.AsyncClient()
        if httpx is not None:
            return httpx.Client()
        if requests is not None:
            return requests.Session()
        raise RuntimeError("No supported HTTP client found. Install httpx or requests.")

    def close(self) -> None:
        if not self._owns_client or self._client is None:
            return
        close_fn = getattr(self._client, "close", None)
        if close_fn is not None:
            close_fn()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: typing.Optional[dict[str, typing.Any]] = None,
        json: typing.Any = None,
        headers: typing.Optional[dict[str, typing.Any]] = None,
    ) -> typing.Any:
        url = _join_url(self._base_url, path)
        response = self._requester(
            method,
            url,
            params=params,
            json=json,
            headers=headers,
        )
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        status_code = getattr(response, "status_code", None)
        if status_code == 204:
            return None
        try:
            payload = response.json()
            return payload
        except Exception:
            text = getattr(response, "text", None)
            if callable(text):
                text = text()
            return text

    def post(self, *, body: typing.Optional[AppControllerPostBody] = None) -> typing.Any:
        path = "/"
        query_params = None
        header_params = None
        json_body = _jsonify(body) if body is not None else None
        return self._request("POST", path, params=query_params or None, json=json_body, headers=header_params or None)

    def test(self, *, headers: typing.Optional[AppControllerTestHeaders] = None, cookies: typing.Optional[AppControllerTestCookies] = None) -> typing.Any:
        path = "/"
        query_params = None
        header_params = _normalize_mapping(headers)
        json_body = None
        cookie_params = _normalize_mapping(cookies)
        if cookie_params:
            header_params = header_params or {}
            header_params['Cookie'] = _encode_cookies(cookie_params)
        return self._request("GET", path, params=query_params or None, json=json_body, headers=header_params or None)

    def get_user(self, *, headers: typing.Optional[UserControllerGetUserHeaders] = None) -> Union[Response, dict[str, typing.Any]]:
        path = "/users"
        query_params = None
        header_params = _normalize_mapping(headers)
        json_body = None
        return self._request("GET", path, params=query_params or None, json=json_body, headers=header_params or None)

    def get_user_by_id(self, id: typing.Any) -> Union[Response, dict[str, typing.Any]]:
        path = "/users/{id}"
        path = path.replace("{id}", str(id))
        query_params = None
        header_params = None
        json_body = None
        return self._request("POST", path, params=query_params or None, json=json_body, headers=header_params or None)


Response = typing.Any
TestBody = typing.Any