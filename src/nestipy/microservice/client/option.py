import enum
from dataclasses import dataclass, field
from typing import Union, Optional

from .base import ClientProxy
from .transporter import CustomTransportStrategy


class Transport(enum.Enum):
    REDIS = "REDIS"
    MQTT = "MQTT"
    NATS = "NATS"
    RABBITMQ = "RABBITMQ"
    CUSTOM = "CUSTOM"


@dataclass
class MicroserviceClientOption:
    host: str
    port: int


@dataclass
class MicroserviceOption:
    transport: Union[Transport, CustomTransportStrategy] = field(default=Transport.REDIS)
    option: Optional[MicroserviceClientOption] = None
    url: Optional[str] = None
    proxy: Optional[ClientProxy] = None
