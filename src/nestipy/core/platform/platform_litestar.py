import asyncio
import inspect
import logging
import traceback

from litestar import Litestar, Controller, route
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig

from .platform import PlatformAdapter
from ..utils import Utils


class PlatformLitestar(PlatformAdapter[Litestar]):
    resolved: list = []

    async def setup(self, module):
        try:
            imports = module.imports if hasattr(module, 'imports') else []
            if module.__name__ not in self.resolved:
                await self.controller_to_litestar_controller(module)
                self.resolved.append(module.__name__)
                for m in imports:
                    await self.setup(m)
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(e)
            logging.error(tb)

    def create_server(self, title: str = "My App", version: str = "1.0.0", **kwargs) -> Litestar:
        handlers = self.get_handlers()
        self.app = Litestar(debug=True, route_handlers=handlers,
                            openapi_config=OpenAPIConfig(title, version, **kwargs))
        return self.app

    @staticmethod
    def controller_to_extend_litestar_controller(ctrl):
        class_attrs = {}
        for name, value in inspect.getmembers(ctrl):
            if not inspect.ismethod(value) and not inspect.isfunction(value) and not inspect.isbuiltin(
                    value) and name != '__slots__':
                class_attrs[name] = value

        if not hasattr(ctrl, 'tags'):
            class_attrs['tags'] = [str(ctrl.__name__).replace('Controller', '')]
        return type(ctrl.__name__, (Controller,),
                    {**class_attrs, "__module__": ctrl.__module__})

    @staticmethod
    def module_providers_to_dependencies(module):
        providers = getattr(module, 'providers')
        dependencies = {}
        for p in providers:
            dependencies[p.injectable__name__] = Provide(lambda: p, sync_to_thread=True)
        return dependencies

    async def controller_to_litestar_controller(self, module):
        await asyncio.sleep(0.001)
        controllers: list = module.controllers
        wrapped_controller = []
        for ctrl in controllers:
            ctrl.dependencies = self.module_providers_to_dependencies(module)
            if not hasattr(ctrl, 'controller__'):
                continue
            new_ctrl = self.controller_to_extend_litestar_controller(ctrl)
            class_attrs = {}
            new_members = inspect.getmembers(new_ctrl)
            for name, value in new_members:
                if not name.startswith('__'):
                    class_attrs[name] = value
            methods = inspect.getmembers(ctrl, predicate=Utils.is_handler)
            for name, value in methods:
                class_attrs[name] = self.controller_method_to_handler(value)
            modified_ctrl = type(new_ctrl.__name__, new_ctrl.__bases__,
                                 {**class_attrs, "__module__": new_ctrl.__module__})
            wrapped_controller.append(modified_ctrl)
            self.add_handler(modified_ctrl)
        module.controllers = wrapped_controller
        return module

    @classmethod
    def controller_method_to_handler(cls, method):
        assert hasattr(method, "path__"), f'Path not exist for {method}.'
        kwargs = method.kwargs__ if hasattr(method, "kwargs__") else {}
        sync_to_thread = True if not inspect.iscoroutinefunction(method) else None
        return route(path=method.path__, http_method=method.method__,
                     sync_to_thread=sync_to_thread, **kwargs)(method)
