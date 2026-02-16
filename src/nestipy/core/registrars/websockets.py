from __future__ import annotations

from typing import Type

from nestipy.websocket.proxy import IoSocketProxy
from nestipy.core.adapter.http_adapter import HttpAdapter


class WebsocketRegistrar:
    """Apply websocket routes when an IO adapter is configured."""

    def __init__(self, http_adapter: HttpAdapter) -> None:
        self._http_adapter = http_adapter

    def apply(self, modules: list[Type | object]) -> None:
        if self._http_adapter.get_io_adapter() is None:
            return
        IoSocketProxy(self._http_adapter).apply_routes(modules)


__all__ = ["WebsocketRegistrar"]
