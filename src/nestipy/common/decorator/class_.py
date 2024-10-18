import enum
from typing import Type, Callable, Union, Optional

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import NestipyContainer, ModuleProviderDict
from nestipy.metadata import ModuleMetadata, Reflect, RouteKey


class Scope(enum.Enum):
    Request = "Request"
    Transient = "Transient"
    Singleton = "Singleton"


class Injectable:
    scope: Optional[Scope] = None

    def __init__(self, scope: Scope = Scope.Singleton):
        self.scope = scope
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls: Union[Type, Callable]) -> Type:
        match self.scope:
            case Scope.Transient:
                self.container.add_transient(cls)
            case Scope.Request:
                self.container.add_transient(cls)
            case _:
                self.container.add_singleton(cls)
        return cls


class Controller:
    def __init__(self, path: str = "/", **kwargs):
        self.path = path
        self.kwargs = kwargs
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls, **kwargs):
        self.container.add_singleton(cls)
        # put path and kwargs in controller property
        Reflect.set_metadata(cls, RouteKey.path, self.path)
        Reflect.set_metadata(cls, RouteKey.kwargs, self.kwargs)
        return cls


class Module:
    providers: list[Union[Type, ModuleProviderDict]] = []
    controllers: list[Type] = []
    imports: list[Union[Type, Callable, ModuleProviderDict, DynamicModule]] = []
    exports: list[Union[Type, Callable, str]] = []
    is_global: bool = False

    def __init__(
        self,
        providers: Optional[list[Callable | ModuleProviderDict]] = None,
        controllers: Optional[list[Callable]] = None,
        imports: Optional[
            list[Union[Type, Callable, ModuleProviderDict, DynamicModule]]
        ] = None,
        exports: Optional[list[Union[Type, Callable, str]]] = None,
        is_global: bool = False,
    ):
        self.providers = providers or []
        self.controllers = controllers or []
        self.imports = imports or []
        self.exports = exports or []
        self.is_global = is_global
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls: Type):
        Reflect.set_metadata(
            cls,
            ModuleMetadata.Providers,
            self.providers + getattr(cls, ModuleMetadata.Providers, []),
        )
        Reflect.set_metadata(
            cls,
            ModuleMetadata.Controllers,
            self.controllers + getattr(cls, ModuleMetadata.Controllers, []),
        )
        Reflect.set_metadata(
            cls,
            ModuleMetadata.Imports,
            self.imports + getattr(cls, ModuleMetadata.Imports, []),
        )
        Reflect.set_metadata(
            cls,
            ModuleMetadata.Exports,
            self.exports + getattr(cls, ModuleMetadata.Exports, []),
        )
        Reflect.set_metadata(
            cls,
            ModuleMetadata.Global,
            self.is_global or getattr(cls, ModuleMetadata.Global, False),
        )
        Reflect.set_metadata(cls, ModuleMetadata.Module, True)
        self.container.add_singleton(cls)
        return cls
