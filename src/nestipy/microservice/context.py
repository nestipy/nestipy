import dataclasses
from typing import Any, Optional, Literal, Union

from dataclasses_json import dataclass_json

from .exception import RpcException

MICROSERVICE_CHANNEL = "channel:microservice"


@dataclasses.dataclass
class RpcRequest:
    data: Any
    pattern: Any
    response_topic: Optional[Any] = None
    headers: dict[str, str] = dataclasses.field(default_factory=lambda: {})

    def is_event(self) -> bool:
        return self.response_topic is None


@dataclass_json
@dataclasses.dataclass
class RpcResponse:
    pattern: str
    data: Any
    status: Literal["success", "error"]
    exception: Union[RpcException, None] = None
    headers: dict[str, str] = dataclasses.field(default_factory=lambda: {})
