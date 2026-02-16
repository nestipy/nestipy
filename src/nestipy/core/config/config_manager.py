from __future__ import annotations

import logging
from typing import Optional, Union


class ConfigManager:
    """Handle runtime configuration application and HTTP logging toggle."""

    def __init__(self, app: object) -> None:
        self._app = app

    def process_config(self, config: object) -> None:
        if getattr(config, "cors", None) is not None:
            self.enable_cors()
        debug = getattr(config, "debug", False)
        setattr(self._app, "_debug", debug)
        getattr(self._app, "_http_adapter").debug = debug
        if getattr(config, "log_http", False):
            self.enable_http_logging()

    @staticmethod
    def resolve_log_level(value: Optional[Union[int, str]], default: int) -> int:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        return logging._nameToLevel.get(value.upper(), default)

    def enable_cors(self) -> None:
        getattr(self._app, "_http_adapter").enable_cors()

    def enable_http_logging(self) -> None:
        setattr(self._app, "_http_log_enabled", True)
