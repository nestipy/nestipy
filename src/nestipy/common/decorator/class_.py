import enum
from typing import Type, Callable, Union, Optional

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import NestipyContainer, ModuleProviderDict
from nestipy.metadata import ModuleMetadata, Reflect, RouteKey


class Scope(enum.Enum):
    """
    Enum representing the lifecycle scope of a provider.
    """
    Request = "Request"
    Transient = "Transient"
    Singleton = "Singleton"


class Injectable:
    """
    Decorator that marks a class as a provider that can be injected as a dependency.
    """
    scope: Optional[Scope] = None

    def __init__(self, scope: Scope = Scope.Singleton):
        """
        Initialize the Injectable decorator.
        :param scope: The lifecycle scope of the provider (Singleton, Transient, or Request).
        """
        self.scope = scope
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls: Union[Type, Callable]) -> Type:
        """
        Register the class into the container with the specified scope.
        :param cls: The class to be marked as injectable.
        :return: The decorated class.
        """
        match self.scope:
            case Scope.Transient:
                self.container.add_transient(cls)
            case Scope.Request:
                self.container.add_transient(cls)
            case _:
                self.container.add_singleton(cls)
        return cls


class Controller:
    """
    Decorator that marks a class as a controller.
    Controllers are responsible for handling incoming requests and returning responses to the client.
    """
    def __init__(self, path: str = "/", **kwargs):
        """
        Initialize the Controller decorator.
        :param path: The base path for all routes defined in the controller.
        :param kwargs: Additional metadata for the controller.
        """
        self.path = path
        self.kwargs = kwargs
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls, **kwargs):
        """
        Register the class as a singleton in the container and set its route metadata.
        :param cls: The class to be marked as a controller.
        :return: The decorated class.
        """
        self.container.add_singleton(cls)
        # put path and kwargs in controller property
        Reflect.set_metadata(cls, RouteKey.path, self.path)
        Reflect.set_metadata(cls, RouteKey.kwargs, self.kwargs)
        return cls


class Module:
    """
    Decorator that marks a class as a module.
    Modules are used to organize the application structure and manage dependencies.
    """
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
        """
        Initialize the Module decorator.
        :param providers: List of providers that will be instantiated by the Nestipy injector.
        :param controllers: List of controllers defined in this module which have to be instantiated.
        :param imports: List of imported modules that export the providers which are required in this module.
        :param exports: List of providers that should be available in other modules.
        :param is_global: Whether the module should be globally available.
        """
        self.providers = providers or []
        self.controllers = controllers or []
        self.imports = imports or []
        self.exports = exports or []
        self.is_global = is_global
        self.container = NestipyContainer.get_instance()

    def __call__(self, cls: Type):
        """
        Register the module and its metadata in the Reflect system and the container.
        :param cls: The class to be marked as a module.
        :return: The decorated class.
        """
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
