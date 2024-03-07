import inspect

from nestipy.common.decorator.middleware import NestipyMiddleware
from nestipy.common.decorator.use_gards import NestipyCanActivate
from nestipy.core.module import MiddlewareConsumer
from nestipy.core.module.middleware import MiddlewareDict
from nestipy.core.utils import Utils


class MiddlewareCompiler:
    def __init__(self, compiler):
        self.compiler = compiler
        self.middleware_consumer = MiddlewareConsumer(self)

    @classmethod
    def get_middleware_of_handler(cls, handler, path='path__'):
        path = getattr(handler, path) or ''
        if hasattr(handler, 'middlewares__'):
            return path, getattr(handler, 'middlewares__', [])
        return path, []

    def apply_middleware_to_path(self, module, path, middlewares: list):
        transformed_middleware = []
        for m in middlewares:
            if inspect.isclass(m):
                instance = self.compiler.container.resolve(m, module)
                if isinstance(instance, NestipyMiddleware):
                    middleware = getattr(instance, 'use')
                    transformed_middleware.append(MiddlewareDict(path=path, middleware=middleware))
                elif isinstance(instance, NestipyCanActivate):
                    middleware = getattr(instance, 'can_activate')
                    transformed_middleware.append(MiddlewareDict(path=path, middleware=middleware, guard=True))
                else:
                    pass
            elif inspect.isfunction(m) or inspect.ismethod(m):
                transformed_middleware.append(MiddlewareDict(path=path, middleware=m, guard=hasattr(m, 'guard__')))

        self.compiler.middlewares += transformed_middleware
        return transformed_middleware

    def apply_middleware_to_ctrl(self, module, ctrl, middlewares=None):
        if middlewares is None:
            middlewares = []
        applied_middlewares = []
        ctrl_path, ctrl_middleware = self.get_middleware_of_handler(ctrl, path='path')
        # applied_middlewares += self.apply_middleware_to_path(module, ctrl_path, middlewares + ctrl_middleware)
        methods = inspect.getmembers(ctrl, predicate=Utils.is_handler)
        for name, value in methods:
            method_path, method_middleware = self.get_middleware_of_handler(value)
            applied_middlewares += self.apply_middleware_to_path(module, ctrl_path + method_path
                                                                 , middlewares + ctrl_middleware + method_middleware)
        return applied_middlewares

    def extract_middleware_of_module(self, module):
        module_middlewares: list[MiddlewareDict] = []
        middlewares: list = [p for p in getattr(module, 'providers') if hasattr(p, 'middleware__')]
        controllers = [ctrl for ctrl in module.controllers if hasattr(ctrl, 'controller__')]
        for ctrl in controllers:
            module_middlewares += self.apply_middleware_to_ctrl(module, ctrl, middlewares)
        setattr(module, 'middlewares__', module_middlewares)

        if hasattr(module, 'nestipy_module__') and getattr(module, 'nestipy_module__'):
            if hasattr(module, 'configure'):
                c = self.middleware_consumer
                module_instance = module()
                module_instance.configure(c)
