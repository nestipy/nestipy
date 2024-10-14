from dataclasses import dataclass
from typing import Any, Union

from nestipy.metadata import SetMetadata
from .client.option import Transport

MICROSERVICE_LISTENER = "__Microservice__Listener__"


class MicroserviceMetadata:
    Event = "__Microservice__Event__"
    Message = "__Microservice__Message__"


@dataclass
class MicroserviceData:
    pattern: Any
    type: str
    transport: Union[Transport, None] = None


def MessagePattern(pattern: Any, transport: Union[Transport, None] = None):
    return SetMetadata(
        MICROSERVICE_LISTENER,
        MicroserviceData(pattern, MicroserviceMetadata.Message, transport),
    )


def EventPattern(pattern: Any, transport: Union[Transport, None] = None):
    return SetMetadata(
        MICROSERVICE_LISTENER,
        MicroserviceData(pattern, MicroserviceMetadata.Event, transport),
    )
