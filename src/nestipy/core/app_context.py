import asyncio
import inspect
import logging
import traceback
from typing import Any, Annotated, Callable

from .module.provider import ModuleProvider
from .utils import Utils
from ..common.context import ExecutionContext
from ..common.decorator.gateway import GATEWAY_SERVER
from ..common.enum.platform import PlatFormType
from ..core.module.compiler import ModuleCompiler
from ..core.platform.platform import PlatformAdapter
from ..core.platform.platform_fastapi import PlatformFastAPI
from ..core.platform.platform_litestar import PlatformLitestar

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
    context: ExecutionContext

    engine_io: Any = None
    engine_io_path: Any = ''

    def __init__(self, module, platform=PlatFormType, adapter: PlatformAdapter = None, **kwargs):
        self.module = module
        self.platform = platform
        self.compiler = ModuleCompiler()
        self.adapter = adapter if adapter is not None else (
            PlatformLitestar() if platform == PlatFormType.LITESTAR else PlatformFastAPI())
        self.kwargs = kwargs
        self.config_logger()

    def mount(self, path: str, handler: Callable):
        self.adapter.mount(path, handler)

    def useSocketIo(self, engine_io: Any = None, engine_io_path: str = 'socket.io'):
        self.engine_io = engine_io
        self.engine_io_path = engine_io_path
        if not self.engine_io_path.startswith('/'):
            self.engine_io_path = '/' + self.engine_io_path
        providers = ([ModuleProvider(provide=GATEWAY_SERVER, use_value=self.engine_io)]
                     + getattr(self.module, 'providers', []))
        setattr(self.module, 'providers', providers)

    def registerSocketIoHandler(self):
        handlers = [(k, v) for k, v in self.compiler.container.instances.items() if
                    inspect.isclass(k) and hasattr(k, 'gateway__')]
        for k, gate in handlers:
            members = inspect.getmembers(k,
                                         predicate=lambda a: inspect.isfunction(a) and hasattr(a, 'gateway__handler__'))
            for name, member in members:
                event = getattr(member, 'gateway__handler__event__', None)
                if event is not None:
                    self.engine_io.on(event)(getattr(gate, name))

    def config_logger(self):
        formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)

    async def __call__(self, scope, receive, send, **kwargs):
        scope['app'] = self

        # platform socket
        if scope['type'] in ['http', 'websocket'] and \
                self.engine_io is not None and scope['path'].startswith(self.engine_io_path):
            await self.engine_io.handle_request(scope, receive, send)
        elif scope.get('type') == 'websocket':
            self.context = ExecutionContext(scope, receive, send)
            await self.call_middlewares(scope=scope, receive=receive, send=send)
        else:
            self.message = await receive()
            if scope['type'] == 'lifespan':
                await self.handle_lifespan()
                await self.app(scope, self.receive, send)
            else:
                self.context = ExecutionContext(scope, self.receive, send)
                # call middleware before
                await self.call_middlewares(scope=scope, receive=self.receive, send=send)

    async def receive(self):
        await asyncio.sleep(0.001)
        return self.message

    async def handle_lifespan(self):
        if self.message['type'] == 'lifespan.startup':
            await self.setup()
            await self.on_startup()
        elif self.message['type'] == 'lifespan.shutdown':
            await self.on_shutdown()
        return self.message

    async def setup(self):
        try:
            compiled_module = await self.compiler.compile(self.module)
            if self.engine_io is not None:
                self.registerSocketIoHandler()
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

    async def call_middleware(self, scope, receive, send, index: int, middlewares: list):
        middleware = middlewares[index]

        async def next_function():
            if index + 1 == len(middlewares):
                if hasattr(self, 'app') and self.app is not None:
                    return await self.app(scope, receive, send)
                else:
                    await self.handle_lifespan()
                    raise Exception('Platform Handler not initialized')
            else:
                return await self.call_middleware(scope, receive, send, index + 1, middlewares)

        dependencies = (self.context,) if middleware.guard else (
            self.context.get_request(), self.context.get_response(), next_function)
        if inspect.iscoroutinefunction(middleware.middleware):
            response = await middleware.middleware(*dependencies)
        else:
            response = middleware.middleware(*dependencies)
        if middleware.guard:
            if response is True:
                await next_function()
            else:
                await self.context.get_response().send_json(
                    {'error': 'Access to this resource on the server is denied'}, 403)
        return response or None

    async def call_middlewares(self, scope, receive, send):
        matched_middleware = []
        middlewares = self.compiler.middlewares
        for middleware in middlewares:
            path = scope["path"]
            match = Utils.match_route(middleware.path, path)
            if match:
                matched_middleware.append(middleware)
        try:
            if len(matched_middleware) > 0:
                response = await self.call_middleware(scope, receive, send, 0, matched_middleware)
            else:
                response = await self.app(scope, receive, send)
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
