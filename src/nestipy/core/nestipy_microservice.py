import asyncio
from typing import Type

from nestipy.core import NestipyApplication, NestipyConfig
from nestipy.microservice.client import MqttClientProxy, RabbitMQClientProxy, NatsClientProxy
from nestipy.microservice.client import RedisClientProxy, ClientProxy
from nestipy.microservice.client.option import MicroserviceOption, Transport
from nestipy.microservice.proxy import MicroserviceProxy
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server import MicroServiceServer
from nestipy.microservice.server.module import MicroserviceServerModule


class NestipyMicroservice:
    app: NestipyApplication
    servers: list[MicroServiceServer] = []

    def __init__(self, module: Type, option: list[MicroserviceOption]):
        self.root_module = module
        self.option = option
        self.serializer = JSONSerializer()
        self.app = NestipyApplication()

    async def _setup_microservice(self):
        self.app.init(self.root_module)
        self.app.add_module_root_module(MicroserviceServerModule, _init=True)
        # create all instance
        await self.app.setup()
        # get server module
        server_module: MicroserviceServerModule = await self.app.get(MicroserviceServerModule)
        controllers = server_module.discover.get_all_controller()
        for server in self.servers:
            MicroserviceProxy(server).apply_routes(controllers)

    async def start(self):
        for opt in self.option:
            client_adapter = self._create_client_adapter(opt)
            server = MicroServiceServer(
                pubsub=client_adapter,
                serializer=self.serializer
            )
            self.servers.append(server)
        # get all handler
        await self._setup_microservice()
        # start server listener
        coroutines = []
        for server in self.servers:
            coroutines.append(server.listen())
        await asyncio.gather(*coroutines)

    async def stop(self):
        for server in self.servers:
            await server.close()
        asyncio.get_running_loop().close()

    def _create_client_adapter(self, option: MicroserviceOption) -> ClientProxy:
        match option.transport:
            case Transport.REDIS:
                return RedisClientProxy(
                    option,
                    self.serializer
                )
            case Transport.MQTT:
                return MqttClientProxy(
                    option,
                    self.serializer
                )
            case Transport.RABBITMQ:
                return RabbitMQClientProxy(
                    option,
                    self.serializer
                )
            case Transport.NATS:
                return NatsClientProxy(
                    option,
                    self.serializer
                )
            case Transport.CUSTOM:
                if option.proxy is not None and isinstance(option.proxy, ClientProxy):
                    return option.proxy
                else:
                    raise Exception("Transport not known")
            case _:
                raise Exception("Transport not known")


class NestipyConnectMicroservice(NestipyMicroservice, NestipyApplication):
    def __init__(self, module: Type, config: NestipyConfig, option: list[MicroserviceOption]):
        super(NestipyApplication).__init__(config)
        super(NestipyMicroservice).__init__(module, option)
        self.app = self

    def start_all_microservice(self):
        self.app.on_startup(self.start)
        self.app.on_shutdown(self.stop)
