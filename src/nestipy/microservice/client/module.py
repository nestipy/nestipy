from dataclasses import dataclass

from nestipy.common.decorator.class_ import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder, DynamicModule
from nestipy.ioc.provider import ModuleProviderDict
from nestipy.microservice.serilaizer import JSONSerializer, Serializer
from .base import ClientProxy
from .mqtt import MqttClientProxy
from .nats import NatsClientProxy
from .option import MicroserviceOption, Transport
from .rabbitmq import RabbitMQClientProxy
from .redis import RedisClientProxy


@dataclass
class ClientsConfig:
    name: str
    option: MicroserviceOption


ConfigurableModuleClass, CLIENT_OPTION = ConfigurableModuleBuilder[list[ClientsConfig]]().build()


@Module()
class ClientsModule(ConfigurableModuleClass):

    @classmethod
    def register(cls, option: list[ClientsConfig]):
        dynamic_module: DynamicModule = getattr(ConfigurableModuleClass, "register")(option)
        providers = []
        for opt in option:
            providers.append(
                ModuleProviderDict(
                    token=opt.name,
                    value=cls._create_client_adapter(opt.option)
                )
            )
        dynamic_module.providers = dynamic_module.providers + providers
        dynamic_module.is_global = True
        return dynamic_module

    @classmethod
    def _create_client_adapter(
            cls,
            option: MicroserviceOption,
            serializer: Serializer = JSONSerializer()
    ) -> ClientProxy:
        match option.transport:
            case Transport.REDIS:
                return RedisClientProxy(
                    option,
                    serializer
                )
            case Transport.MQTT:
                return MqttClientProxy(
                    option,
                    serializer
                )
            case Transport.RABBITMQ:
                return RabbitMQClientProxy(
                    option,
                    serializer
                )
            case Transport.NATS:
                return NatsClientProxy(
                    option,
                    serializer
                )
            case Transport.CUSTOM:
                if option.proxy is not None and isinstance(option.proxy, ClientProxy):
                    return option.proxy
                else:
                    raise Exception("Transport not known")
            case _:
                raise Exception("Transport not known")
