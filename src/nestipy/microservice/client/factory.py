from .base import ClientProxy, MicroserviceOption
from .mqtt import MqttClientProxy
from .nats import NatsClientProxy
from .option import Transport
from .rabbitmq import RabbitMQClientProxy
from .redis import RedisClientProxy


class ClientModuleFactory:
    @classmethod
    def create(cls, option: MicroserviceOption) -> ClientProxy:
        match option.transport:
            case Transport.REDIS:
                return RedisClientProxy(
                    option,
                )
            case Transport.MQTT:
                return MqttClientProxy(
                    option,
                )
            case Transport.RABBITMQ:
                return RabbitMQClientProxy(
                    option,
                )
            case Transport.NATS:
                return NatsClientProxy(
                    option,
                )
            case Transport.CUSTOM:
                if option.proxy is not None and isinstance(option.proxy, ClientProxy):
                    return option.proxy
                else:
                    raise Exception("Transport not known")
            case _:
                raise Exception("Transport not known")
