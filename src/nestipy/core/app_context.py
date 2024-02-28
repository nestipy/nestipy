import asyncio
import inspect
import logging
import traceback
from typing import Any, Annotated

from .utils import Utils
from ..common.enum.platform import PlatFormType
from ..core.module.compiler import ModuleCompiler
from ..core.platform.platform import PlatformAdapter
from ..core.platform.platform_litestar import PlatformLitestar
from ..core.platform.platform_fastapi import PlatformFastAPI

Injected = Annotated[int, 'Test']

FORMAT = '%(levelname)-10s%(asctime)-15s - %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'

logging.basicConfig(format=FORMAT, datefmt=DATE_FORMAT)


class AppNestipyContext:
    server_kwargs: dict
    adapter: PlatformAdapter
    compiler: ModuleCompiler
    app: Any
    message: Any = None
    logger: logging.Logger

    def __init__(self, module, platform=PlatFormType, **kwargs):
        self.platform = platform
        self.compiler = ModuleCompiler(module)
        self.adapter = PlatformFastAPI() if platform == PlatFormType.FASTAPI else PlatformLitestar()
        self.kwargs = kwargs
        self.config_logger()

    def config_logger(self):
        formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)

    async def __call__(self, scope, receive, send, **kwargs):
        if scope['type'] == 'lifespan':
            self.message = await self.handle_lifespan(receive)
            await self.app(scope, self.receive, send)
        else:
            # call middleware before
            response = await self.call_middleware(scope, receive, send)
            if not response:
                if hasattr(self, 'app') and self.app is not None:
                    await self.app(scope, receive, send)
                else:
                    raise Exception('Platform Handler not initialized')

    async def receive(self):
        await asyncio.sleep(0.001)
        return self.message

    async def handle_lifespan(self, receive):
        message = await receive()
        if message['type'] == 'lifespan.startup':
            await self.setup()
            await self.on_startup()
        elif message['type'] == 'lifespan.shutdown':
            await self.on_shutdown()
        return message

    async def setup(self):
        try:
            compiled_module = await self.compiler.compile()
            await self.adapter.setup(compiled_module)
            self.app = self.adapter.create_server(**self.kwargs)
            self.logger.info("Application initialized successfully.")
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(e)
            logging.error(tb)
            raise e

    async def call_hooks(self, key):

        if key in self.compiler.hooks.keys():
            hooks = self.compiler.hooks.get(key)
            for hook in hooks:
                try:
                    if inspect.iscoroutinefunction(hook):
                        await hook()
                    else:
                        hook()
                except Exception as e:
                    tb = traceback.format_exc()
                    logging.error(e)
                    logging.error(tb)
                    raise e

    async def call_middleware(self, scope, receive, send):
        middlewares = self.compiler.middlewares
        for middleware in middlewares:
            path = scope["path"]
            match = Utils.match_route(middleware.path, path)
            if match:
                try:
                    if inspect.iscoroutinefunction(middleware.middleware):
                        response = await middleware.middleware(scope, receive, send)
                        if response:
                            return response
                    else:
                        response = middleware.middleware(scope, receive, send)
                        if response:
                            return response
                except Exception as e:
                    tb = traceback.format_exc()
                    logging.error(e)
                    logging.error(tb)
                    raise e

    async def on_startup(self):
        await self.call_hooks('on_startup')

    async def on_shutdown(self):
        await self.call_hooks('on_shutdown')
