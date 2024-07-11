import enum
from dataclasses import dataclass


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
