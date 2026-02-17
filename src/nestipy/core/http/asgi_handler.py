from __future__ import annotations

import time
import uuid
from typing import Callable, TYPE_CHECKING

from nestipy.common.logger import logger
from nestipy.core.security.cors import apply_cors_headers


if TYPE_CHECKING:
    from nestipy.core.nestipy_application import NestipyApplication


def _extract_header(scope: dict, name: str) -> str | None:
    target = name.lower().encode()
    for key, value in scope.get("headers", []) or []:
        if key.lower() == target:
            try:
                return value.decode()
            except Exception:
                return None
    return None


def _ensure_state(scope: dict) -> dict:
    state = scope.setdefault("state", {})
    if not isinstance(state, dict):
        state = {}
        scope["state"] = state
    return state


def _ensure_request_id(scope: dict) -> str:
    state = _ensure_state(scope)
    existing = state.get("request_id")
    if isinstance(existing, str) and existing:
        return existing
    header_id = _extract_header(scope, "x-request-id") or _extract_header(
        scope, "x-correlation-id"
    )
    if header_id:
        state["request_id"] = header_id
        return header_id
    new_id = uuid.uuid4().hex
    state["request_id"] = new_id
    return new_id


def _add_header(headers: list[tuple[bytes, bytes]], name: str, value: str) -> None:
    header_name = name.lower().encode()
    if any(k.lower() == header_name for k, _ in headers):
        return
    headers.append((name.encode(), value.encode()))


def _apply_security_headers(
    headers: list[tuple[bytes, bytes]], enabled: bool
) -> None:
    if not enabled:
        return
    defaults = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "no-referrer",
    }
    for name, value in defaults.items():
        _add_header(headers, name, value)


class AsgiHandler:
    """Central ASGI entrypoint helper with optional HTTP logging and web-static handling."""

    def __init__(self, app: "NestipyApplication") -> None:
        self._app = app

    async def handle(self, scope: dict, receive: Callable, send: Callable) -> None:
        app = self._app
        state = _ensure_state(scope)
        state["debug"] = bool(getattr(app, "_debug", False))
        request_id = _ensure_request_id(scope)
        if scope.get("type") == "lifespan":
            await app.ready()
            await app.get_adapter()(scope, receive, send)
            return

        if scope.get("type") != "http":
            await app.get_adapter()(scope, receive, send)
            return

        start = time.perf_counter()
        status_code: int | None = None
        method = scope.get("method", "-")
        path = scope.get("path", "")

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message.get("type") == "http.response.start":
                headers = list(message.get("headers", []) or [])
                _add_header(headers, "X-Request-Id", request_id)
                _apply_security_headers(
                    headers, bool(getattr(app, "_security_headers_enabled", False))
                )
                cors_options = getattr(app, "_cors_options", None)
                if cors_options is not None:
                    origin = _extract_header(scope, "origin")
                    header_map = {
                        k.decode(): v.decode()
                        for k, v in headers
                        if isinstance(k, (bytes, bytearray)) and isinstance(v, (bytes, bytearray))
                    }
                    apply_cors_headers(header_map, origin, cors_options)
                    headers = [(k.encode(), v.encode()) for k, v in header_map.items()]
                message["headers"] = headers
                status_code = int(message.get("status", 0) or 0)
                duration_ms = (time.perf_counter() - start) * 1000
                if log_enabled:
                    logger.info(
                        "[HTTP] %s %s -> %s (%.2fms) req_id=%s",
                        method,
                        path,
                        status_code,
                        duration_ms,
                        request_id,
                        extra={
                            "request_id": request_id,
                            "method": method,
                            "path": path,
                            "status": status_code,
                            "duration_ms": duration_ms,
                        },
                    )
            await send(message)

        log_enabled = bool(getattr(app, "_http_log_enabled", False))
        send_fn = send_wrapper
        if await app._helpers.web_static.maybe_handle(scope, receive, send_fn):
            return

        try:
            await app.get_adapter()(scope, receive, send_fn)
        except Exception:
            if status_code is None:
                duration_ms = (time.perf_counter() - start) * 1000
                if log_enabled:
                    logger.exception(
                        "[HTTP] %s %s -> 500 (%.2fms) req_id=%s",
                        method,
                        path,
                        duration_ms,
                        request_id,
                        extra={
                            "request_id": request_id,
                            "method": method,
                            "path": path,
                            "status": 500,
                            "duration_ms": duration_ms,
                        },
                    )
            raise
