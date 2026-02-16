from typing import Optional
import typing

from nestipy.core.types import JsonValue
from nestipy.microservice.context import RpcRequest
from .argument_host import ArgumentHost


class RpcArgumentHost(ArgumentHost):
    def get_args(self):
        return self.get_request(), self.get_data()

    def get_request(self) -> RpcRequest | None:
        return typing.cast(RpcRequest | None, self._req)

    def get_pattern(self) -> Optional[JsonValue]:
        request = self.get_request()
        return getattr(request, "pattern", None) if request is not None else None

    def get_headers(self) -> dict[str, JsonValue]:
        request = self.get_request()
        if request is None:
            return {}
        headers = getattr(request, "headers", None)
        return headers if isinstance(headers, dict) else {}

    def get_data(self) -> JsonValue | None:
        return self._socket_data

    def get_server(self):
        return self._socket_server
