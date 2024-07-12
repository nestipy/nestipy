import asyncio
import traceback

from nestipy.common.logger import console
from nestipy.core import NestipyApplication, NestipyConfig
from nestipy.microservice.client.base import MicroserviceOption
from nestipy.microservice.client.factory import ClientModuleFactory
from nestipy.microservice.proxy import MicroserviceProxy
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server import MicroServiceServer
from nestipy.microservice.server.module import MicroserviceServerModule
from rich.style import Style


class NestipyMicroservice:
    app: NestipyApplication
    servers: list[MicroServiceServer] = []
    _ms_ready: bool = False
    coroutines: list = []

    console: Console

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
        self.coroutines = []
        loop = asyncio.get_running_loop()
        # start server listener
        if not self._ms_ready:
            await self.ready()
        for server in self.servers:
            self.coroutines.append(server.listen())
        await asyncio.gather(*self.coroutines)

    async def stop(self):
        # for task in self.coroutines:
        #     task.done()
        for server in self.servers:
            try:
                await server.close()
            except RuntimeError as e:
                traceback.print_exc()
                print(e)
            finally:
                pass

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope.get('type') == 'lifespan':
            asyncio.create_task(self.start())
            console.print("[INFO]    Microservice startup completed", style=Style(color="green", bold=True))


class NestipyConnectMicroservice(NestipyMicroservice, NestipyApplication):
    _running: bool = False

    def __init__(self, module: Type, config: NestipyConfig, option: list[MicroserviceOption]):
        NestipyMicroservice.__init__(self, module, option)
        NestipyApplication.__init__(self, config)
        self.app = self

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        await NestipyApplication.__call__(self, scope, receive, send)

    def start_all_microservices(self):
        def start():
            asyncio.create_task(self.start())

        self.app.on_startup(start)
        self.app.on_shutdown(self.stop)
