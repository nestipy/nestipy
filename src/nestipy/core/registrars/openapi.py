from __future__ import annotations

from typing import Any

from nestipy.metadata import Reflect


class OpenApiRegistrar:
    """Register the lazy OpenAPI handler when configured."""

    def __init__(self, owner: Any) -> None:
        self._owner = owner

    def register(self) -> None:
        from nestipy.openapi.constant import OPENAPI_HANDLER_METADATA

        openapi_register = Reflect.get_metadata(self._owner, OPENAPI_HANDLER_METADATA, None)
        if openapi_register is not None:
            openapi_register()


__all__ = ["OpenApiRegistrar"]
