from __future__ import annotations

from nestipy.websocket.proxy import IoSocketProxy
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.core.types import ModuleRef


class WebsocketRegistrar:
    """Apply websocket routes when an IO adapter is configured."""

    def __init__(self, http_adapter: HttpAdapter) -> None:
        self._http_adapter = http_adapter

    def apply(self, modules: list[ModuleRef]) -> None:
        if self._http_adapter.get_io_adapter() is None:
            return
        IoSocketProxy(self._http_adapter).apply_routes(modules)


__all__ = ["WebsocketRegistrar"]
