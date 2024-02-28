import asyncio
import inspect
import logging
import traceback
from typing import Any

from fastapi import FastAPI, Depends, APIRouter
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from nestipy.core.utils import Utils
from .platform import PlatformAdapter


class PlatformFastAPI(PlatformAdapter[FastAPI]):
    resolved: list = []
    module: Any
    router: APIRouter = APIRouter()

    async def setup(self, module):
        try:
            imports = module.imports if hasattr(module, 'imports') else []
            if module.__name__ not in self.resolved:
                await self.controller_to_fastapi_controller(module=module)
                self.resolved.append(module.__name__)
                for m in imports:
                    await self.setup(m)
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(e)
            logging.error(tb)

    def create_server(self, *args, **kwargs) -> FastAPI:
        routes = self.get_handlers()
        self.app = FastAPI(*args, debug=True, **kwargs)
        for router in routes:
            self.app.include_router(router, include_in_schema=True)
        return self.app

    @classmethod
    def controller_method_to_handler(cls, router: APIRouter, method, prefix=''):
        assert hasattr(method, "path__"), f'Path not exist for {method}.'
        kwargs = method.kwargs__ if hasattr(method, "kwargs__") else {}
        path = f"{prefix.rstrip('/')}/{method.path__.lstrip('/')}"
        match str(method.method__.value).lower():
            case 'post':
                return router.post(path, **kwargs)(method)
            case 'put':
                return router.put(path, **kwargs)(method)
            case 'patch':
                return router.patch(path, **kwargs)(method)
            case 'delete':
                return router.delete(path, **kwargs)(method)
            case _:
                return router.get(path, **kwargs)(method)

    @staticmethod
    def module_providers_to_dependencies(module):
        providers = getattr(module, 'providers')
        dependencies = []
        for p in providers:
            dependencies.append(Depends(lambda: p))
        return dependencies

    async def controller_to_fastapi_controller(self, module):
        await asyncio.sleep(0.001)
        controllers: list = module.controllers
        wrapped_controller = []
        for ctrl in controllers:
            router = InferringRouter(
                tags=[str(ctrl.__name__).replace('Controller', '').capitalize()],
                dependencies=self.module_providers_to_dependencies(module)
            )
            if not hasattr(ctrl, 'controller__'):
                continue
            class_attrs = {}
            new_members = inspect.getmembers(ctrl)
            for name, value in new_members:
                if not name.startswith('__'):
                    class_attrs[name] = value
            methods = inspect.getmembers(ctrl, predicate=Utils.is_handler)
            for name, value in methods:
                class_attrs[name] = self.controller_method_to_handler(router=router, method=value,
                                                                      prefix=getattr(ctrl, 'path').rstrip('/'))
            attrs = {**class_attrs, "__module__": ctrl.__module__, '__name__': ctrl.__name__}
            new_controller: Any = type(ctrl.__name__, ctrl.__bases__, attrs)
            new_controller = cbv(router)(new_controller)
            wrapped_controller.append(new_controller)
            self.add_handler(router)
        module.controllers = wrapped_controller
        return module
