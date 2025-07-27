import asyncio
import traceback
from typing import Callable, Type

from rich.style import Style

from nestipy.common.logger import console
from nestipy.core import NestipyApplication, NestipyConfig, DiscoverService
from nestipy.microservice.client.base import MicroserviceOption
from nestipy.microservice.client.factory import ClientModuleFactory
from nestipy.microservice.proxy import MicroserviceProxy
from nestipy.microservice.server import MicroServiceServer


class NestipyMicroservice:
    app: NestipyApplication
    servers: list[MicroServiceServer] = []
    _ms_ready: bool = False
    coroutines: list = []

    def __init__(
        self, module: Type, option: list[MicroserviceOption], auto_init: bool = True
    ):
        self.root_module = module
        self.option = option
        if auto_init:
            self.app = NestipyApplication()
            self.app.init(root_module=self.root_module)

    async def ms_setup(self):
        self.servers = []
        for opt in self.option:
            client_adapter = ClientModuleFactory.create(opt)
            server = MicroServiceServer(
                pub_sub=client_adapter,
            )
            self.servers.append(server)
        # self.app.add_module_root_module(MicroserviceServerModule, _init=True)
        # create all instance if not
        await self.app.setup()
        discover: DiscoverService = await self.app.get(DiscoverService)
        controllers = discover.get_all_controller()
        for server in self.servers:
            MicroserviceProxy(server).apply_routes(controllers)

        self._ms_ready = True

    async def start(self):
        self.coroutines = []
        # start server listener
        if not self._ms_ready:
            await self.ms_setup()
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
        if scope.get("type") == "lifespan":

            def create_task():
                asyncio.create_task(self.start())

            create_task()
            console.print(
                "[INFO]  Microservice startup completed",
                style=Style(color="green", bold=True),
            )


class NestipyConnectMicroservice(NestipyMicroservice, NestipyApplication):
    _running: bool = False

    def __init__(
        self, module: Type, config: NestipyConfig, option: list[MicroserviceOption]
    ):
        NestipyMicroservice.__init__(self, module, option, auto_init=False)
        NestipyApplication.__init__(self, config)
        self.app = self
        self.init(self.root_module)
        self.ms_task = None

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        await NestipyApplication.__call__(self, scope, receive, send)

    def start_all_microservices(self):
        def on_start():
            if self.ms_task is None:
                self.ms_task = asyncio.get_running_loop().create_task(self.start())
                console.print(
                    "INFO:     Microservice startup completed.",
                    style=Style(color="green", bold=True),
                )

        async def on_stop():
            if self.ms_task is not None:
                self.ms_task.cancel()
            await self.stop()

        self.app.on_startup(on_start)
        self.app.on_shutdown(on_stop)
