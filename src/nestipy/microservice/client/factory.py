from .base import ClientProxy, MicroserviceOption
from .grpc.client import GrpcClientProxy
from .mqtt import MqttClientProxy
from .nats import NatsClientProxy
from .option import RabbitMQClientOption, GrpcClientOption
from .option import (
    TCPClientOption,
    RedisClientOption,
    NatsClientOption,
    MqttClientOption,
)
from .option import Transport
from .rabbitmq import RabbitMQClientProxy
from .redis import RedisClientProxy
from .tcp import TCPClientProxy


class ClientModuleFactory:
    @classmethod
    def create(cls, option: MicroserviceOption) -> ClientProxy:
        match option.transport:
            case Transport.TCP:
                if option.option is None:
                    option.option = TCPClientOption()
                return TCPClientProxy(
                    option,
                )
            case Transport.REDIS:
                if option.option is None:
                    option.option = RedisClientOption()
                return RedisClientProxy(
                    option,
                )
            case Transport.MQTT:
                if option.option is None:
                    option.option = MqttClientOption()
                return MqttClientProxy(
                    option,
                )
            case Transport.RABBITMQ:
                if option.option is None:
                    option.option = RabbitMQClientOption()
                return RabbitMQClientProxy(
                    option,
                )
            case Transport.NATS:
                if option.option is None:
                    option.option = NatsClientOption()
                return NatsClientProxy(
                    option,
                )

            case Transport.GRPC:
                if option.option is None:
                    option.option = GrpcClientOption()
                return GrpcClientProxy(
                    option,
                )
            case Transport.CUSTOM:
                if option.proxy is not None and isinstance(option.proxy, ClientProxy):
                    return option.proxy
                else:
                    raise Exception("Unknown Transport")
            case _:
                raise Exception("Unknown Transport")
