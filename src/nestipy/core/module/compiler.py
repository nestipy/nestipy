import inspect
from typing import Callable, Any

from pyee import EventEmitter

from .hook_compiler import HookCompiler
from .middleware import MiddlewareDict
from .middleware_compiler import MiddlewareCompiler
from .provider_compiler import ProviderCompiler
from ..ioc import NestipyContainer
from ...plugins.dynamic_module.dynamic_module import DynamicModule


class ModuleCompiler:
    module: Any
    middlewares: list[MiddlewareDict]

    def __init__(self, module: Callable):
        self.module = module
        self.container = NestipyContainer()
        self.module_resolved = {}
        self.hooks = {}
        self.middlewares = []
        self.ee = EventEmitter()
        self.hook_compiler = HookCompiler(self)
        self.middleware_compiler = MiddlewareCompiler(self)
        self.provider_compiler = ProviderCompiler(self)

    def modify_module_imports(self, module, global_modules):
        self.remove_module_none_imported(module)
        filtered_global_modules = [m for m in global_modules if m != module]
        module_imports: list = (module.imports or [])
        module_imports_with_global = filtered_global_modules + module_imports
        setattr(module, 'imports', module_imports_with_global)
        if issubclass(module, DynamicModule):
            setattr(module, 'container__', self.container)

    @classmethod
    def remove_module_none_imported(cls, module):
        setattr(module, 'imports', [im for im in (module.imports or []) if im is not None])

    async def resolve_controllers_of_module(self, module):
        controllers = [ctrl for ctrl in module.controllers if hasattr(ctrl, 'controller__')]
        for ctrl in controllers:
            if inspect.isclass(ctrl):
                self.container.resolve(ctrl, module)
            else:
                token = ctrl.token__
                self.container.resolve_method(ctrl, token=token)

    @classmethod
    def put_module_provider_instance(cls, module, token, instance, is_middleware=False):
        if is_middleware:
            cls.put_module_element(module, 'middleware_instances__', token, instance)
        else:
            cls.put_module_element(module, 'provider_instances__', token, instance)

    @classmethod
    def put_module_element(cls, module, element_type, key, value):
        instances__ = {}
        if hasattr(module, element_type):
            instances__ = getattr(module, element_type)
        instances__[key] = value
        setattr(module, element_type, instances__)

    # MIDDLEWARE

    # COMPILE
    async def compile(self):
        await self.provider_compiler.compile(self.module, init=True)
        return self.module
