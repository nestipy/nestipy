from __future__ import annotations

import time
from typing import Callable, TYPE_CHECKING

from nestipy.common.logger import logger


if TYPE_CHECKING:
    from nestipy.core.nestipy_application import NestipyApplication


class AsgiHandler:
    """Central ASGI entrypoint helper with optional HTTP logging and web-static handling."""

    def __init__(self, app: "NestipyApplication") -> None:
        self._app = app

    async def handle(self, scope: dict, receive: Callable, send: Callable) -> None:
        app = self._app
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
                status_code = int(message.get("status", 0) or 0)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    "[HTTP] %s %s -> %s (%.2fms)",
                    method,
                    path,
                    status_code,
                    duration_ms,
                )
            await send(message)

        send_fn = send_wrapper if getattr(app, "_http_log_enabled", False) else send
        if await app._helpers.web_static.maybe_handle(scope, receive, send_fn):
            return

        try:
            await app.get_adapter()(scope, receive, send_fn)
        except Exception:
            if status_code is None:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    "[HTTP] %s %s -> 500 (%.2fms)",
                    method,
                    path,
                    duration_ms,
                )
            raise
