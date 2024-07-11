import asyncio
from typing import Type

from nestipy.common import logger
from nestipy.core import NestipyApplication, NestipyConfig
from nestipy.microservice.client.base import MicroserviceOption
from nestipy.microservice.client.factory import ClientModuleFactory
from nestipy.microservice.proxy import MicroserviceProxy
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server import MicroServiceServer
from nestipy.microservice.server.module import MicroserviceServerModule


class NestipyMicroservice:
    app: NestipyApplication
    servers: list[MicroServiceServer] = []
    _ms_ready: bool = False

    def __init__(self, module: Type, option: list[MicroserviceOption]):
        self.root_module = module
        self.option = option
        self.serializer = JSONSerializer()
        self.app = NestipyApplication()

    async def ready(self):
        for opt in self.option:
            client_adapter = ClientModuleFactory.create(opt)
            server = MicroServiceServer(
                pubsub=client_adapter,
            )
            self.servers.append(server)
        self.app.init(self.root_module)
        self.app.add_module_root_module(MicroserviceServerModule, _init=True)
        # create all instance if not
        await self.app.setup()
        # get server module
        server_module: MicroserviceServerModule = await self.app.get(MicroserviceServerModule)
        controllers = server_module.discover.get_all_controller()
        for server in self.servers:
            MicroserviceProxy(server).apply_routes(controllers)

        self._ms_ready = True

    async def start(self):
        # start server listener
        if not self._ms_ready:
            await self.ready()

        coroutines = []
        for server in self.servers:
            coroutines.append(server.listen())
        await asyncio.gather(*coroutines)

    async def stop(self):
        for server in self.servers:
            await server.close()
        asyncio.get_running_loop().close()


class NestipyConnectMicroservice(NestipyMicroservice, NestipyApplication):
    _running: bool = False

    def __init__(self, module: Type, config: NestipyConfig, option: list[MicroserviceOption]):
        NestipyMicroservice.__init__(self, module, option)
        NestipyApplication.__init__(self, config)
        self.app = self

    def start_all_microservices(self):
        async def start():
            if not self._ready:
                await self.ready()
            if not self._running:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                for server in self.servers:
                    def create_task():
                        task = server.listen()
                        asyncio.create_task(task)

                    create_task()
                self._running = True

        self.app.on_startup(start)
        self.app.on_shutdown(self.stop)
