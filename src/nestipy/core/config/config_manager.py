from __future__ import annotations

import logging
import os
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.core.nestipy_application import NestipyApplication
    from nestipy.core.nestipy_application import NestipyConfig

from nestipy.core.security.cors import resolve_cors_options, CorsOptions

class ConfigManager:
    """Handle runtime configuration application and HTTP logging toggle."""

    def __init__(self, app: "NestipyApplication") -> None:
        self._app = app

    def process_config(self, config: "NestipyConfig") -> None:
        cors_value = getattr(config, "cors", None)
        if cors_value is not None:
            self.enable_cors(cors_value)
        debug = getattr(config, "debug", False)
        os.environ["NESTIPY_DEBUG"] = "1" if debug else "0"
        setattr(self._app, "_debug", debug)
        getattr(self._app, "_http_adapter").debug = debug
        security_headers = getattr(config, "security_headers", True)
        env_security = os.getenv("NESTIPY_SECURITY_HEADERS", "").strip().lower()
        if env_security in {"0", "false", "no", "off"}:
            security_headers = False
        elif env_security in {"1", "true", "yes", "on"}:
            security_headers = True
        setattr(self._app, "_security_headers_enabled", bool(security_headers))
        if getattr(config, "log_http", False):
            self.enable_http_logging()

    @staticmethod
    def resolve_log_level(value: Optional[Union[int, str]], default: int) -> int:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        return logging._nameToLevel.get(value.upper(), default)

    def enable_cors(self, options: CorsOptions | dict | bool | None = None) -> None:
        resolved = resolve_cors_options(options)
        setattr(self._app, "_cors_options", resolved)
        if resolved is None:
            return
        getattr(self._app, "_http_adapter").enable_cors(resolved)

    def enable_http_logging(self) -> None:
        setattr(self._app, "_http_log_enabled", True)
