import inspect
from functools import lru_cache
from typing import (
    ForwardRef,
    Type,
    Union,
    Any,
    Optional,
    Callable,
    Awaitable,
    TYPE_CHECKING,
)

from nestipy.metadata import (
    ClassMetadata,
    CtxDepKey,
    ModuleMetadata,
    ProviderToken,
    Reflect,
)
from .context_container import RequestContextContainer
from .dependency import TypeAnnotated
from .helper import ContainerHelper
from .utils import uniq

if TYPE_CHECKING:
    from .provider import ModuleProviderDict

_INIT = "__init__"


class NestipyContainer:
    """
    Singleton container class responsible for managing service instances and their dependencies.

    This container allows the registration and resolution of services (both transient and singleton),
    manages singleton instances, and handles dependency injection for classes and functions.
    """

    _instance: Union["NestipyContainer", None] = None
    _services: dict = {}
    _global_service_instances: dict = {}
    _singleton_instances: dict = {}
    _singleton_classes: set = set()

    def __new__(cls, *args, **kwargs):
        """
        Ensures the class is a singleton by creating only one instance.
        """
        if cls._instance is None:
            cls._instance = super(NestipyContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        Returns the singleton instance of the container.
        """
        return NestipyContainer(*args, **kwargs)

    def add_transient(self, service: Type):
        """
        Registers a transient service in the container.
        Transient services are created every time they are requested.

        :param service: The service class to be registered.
        """
        self._services[service] = service

    def add_singleton(self, service: Type):
        """
        Registers a singleton service in the container.
        Singleton services are created only once and reused for subsequent requests.

        :param service: The service class to be registered as singleton.
        """
        self._services[service] = service
        self._singleton_classes.add(service)

    def get_all_services(self) -> list:
        """
        Returns a list of all registered services in the container.

        :return: List of service types.
        """
        return list(self._services.keys())

    def add_singleton_instance(
        self, service: Union[Type, str], service_instance: object
    ):
        """
        Registers an instance of a singleton service.

        :param service: The service class or token.
        :param service_instance: The instance of the service to be used.
        """
        self._singleton_instances[service] = service_instance

    def get_all_singleton_instance(self) -> list:
        """
        Returns a list of all singleton instances currently in the container.

        :return: List of singleton instances.
        """
        return [v for k, v in self._singleton_instances.items()]

    @classmethod
    @lru_cache()
    def get_global_providers(cls) -> list:
        """
        Retrieves a list of global providers registered across all modules.

        :return: List of global provider services.
        """
        global_providers = []
        for service in cls._services:
            if service in global_providers:
                continue
            metadata: Union[ClassMetadata | None] = Reflect.get_metadata(
                service, ClassMetadata.Metadata, None
            )
            if metadata is not None:
                is_global = Reflect.get_metadata(
                    metadata.get_module(), ModuleMetadata.Global, False
                )
                is_root = Reflect.get_metadata(
                    metadata.get_module(), ModuleMetadata.Root, False
                )
                if is_global or is_root:
                    global_providers += Reflect.get_metadata(
                        metadata.get_module(), ModuleMetadata.Providers, []
                    )
        return uniq(global_providers)

    @classmethod
    def get_dependency_metadata(cls, service: Union[Type, object]) -> list:
        """
        Retrieves the metadata for the dependencies of a given service.

        :param service: The service class to resolve.
        :return: List of metadata related to the service's dependencies.
        """
        from .provider import ModuleProviderDict

        # extract global data from _service, not from module because all provider is already saved in _services of
        # container
        metadata: Union[ClassMetadata | None] = Reflect.get_metadata(
            service, ClassMetadata.Metadata, None
        )
        if metadata is not None:
            global_providers = cls.get_global_providers()
            providers, import_providers = metadata.get_service_providers()
            uniq_providers = []
            for m in uniq(providers + global_providers + import_providers):
                if isinstance(m, ModuleProviderDict):
                    for imported_module in m.imports:
                        m_provider, m_import_providers = metadata.get_service_providers(
                            imported_module
                        )
                        uniq_providers = uniq(
                            uniq_providers + m_import_providers + m_provider
                        )
                    uniq_providers.append(m.token)
                else:
                    uniq_providers.append(m)
            return uniq(uniq_providers)
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        return []

    @classmethod
    async def _resolve_contextual_service(
        cls, name: str, dep_key: TypeAnnotated, annotation: Union[Type, Any]
    ):
        """
        Resolves a context-specific service based on the provided dependency key.

        :param name: Name of the dependency.
        :param dep_key: Dependency key with metadata.
        :param annotation: Type or annotation for the service.
        :return: The resolved context service.
        """
        context_container = RequestContextContainer.get_instance()
        callback = dep_key.metadata.callback
        if inspect.iscoroutinefunction(callback):
            return await callback(
                name, dep_key.metadata.token, annotation, context_container
            )
        else:
            return callback(name, dep_key.metadata.token, annotation, context_container)

    async def _resolve_module_provider_dict(
        self, instance: "ModuleProviderDict", search_scope: list
    ):
        """
        Resolves a service instance from a ModuleProviderDict.

        :param instance: The ModuleProviderDict instance.
        :param search_scope: The search scope for resolving dependencies.
        :return: The resolved service instance or None.
        """
        if instance.value:
            return instance.value
        elif instance.existing:
            if isinstance(instance.existing, ProviderToken):
                return await self.get(instance.existing.key)
            else:
                return await self.get(instance.existing)
        elif instance.use_class:
            return await self.get(instance.use_class)
        elif instance.factory:
            return await self.resolve_factory(
                factory=instance.factory,
                inject=instance.inject,
                search_scope=search_scope,
            )

        else:
            return None

    async def _check_exist_singleton(self, key: Union[Type, str]):
        """
        Checks if a singleton instance exists for a given service key.

        :param key: The service class or token.
        :return: The singleton instance if it exists, otherwise None.
        """
        from .provider import ModuleProviderDict

        if key in self._singleton_instances:
            instance = self._singleton_instances[key]
            # to keep improve
            if isinstance(instance, ModuleProviderDict):
                search_scope = self.get_dependency_metadata(instance)
                if instance.token in search_scope:
                    value = await self._resolve_module_provider_dict(
                        instance, search_scope=search_scope
                    )
                    # update singleton instance to have the async value from ModuleProviderDict
                    self._singleton_instances[key] = value
                    return value
                else:
                    raise ValueError(
                        f"Service {instance.__class__.__name__} " f"not found in scope"
                    )
            else:
                return instance
        return None

    def _check_service(
        self, key: Union[Type, str], origin: Optional[list] = None
    ) -> tuple:
        """
        Checks if a service is registered and detects circular dependencies.

        :param key: The service class or token.
        :param origin: The list of services currently being resolved to avoid circular dependency.
        :return: The service class and updated origin list.
        :raises ValueError: If the service is not found or circular dependency is detected.
        """
        if key not in self._services:
            raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(
                f"Circular dependency found  for {service.__name__} service "
            )
        return service, origin or set()

    async def _resolve_property(
        self,
        key: Union[Type, str],
        origin: Optional[list] = None,
        disable_scope: bool = False,
    ):
        """
        Resolves dependencies for the properties of a service.

        :param key: The service class or token.
        :param origin: The list of services currently being resolved.
        :param disable_scope: Whether to disable scope-based resolution.
        """
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        annotations: dict = getattr(service, "__annotations__", {})
        for name, param_annotation in annotations.items():
            annotation, dep_key = ContainerHelper.get_type_from_annotation(
                param_annotation
            )
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_contextual_service(
                    name, dep_key, annotation
                )
                setattr(service, name, dependency)
            else:
                # check token
                if (
                    dep_key.metadata.token in search_scope
                    or annotation in search_scope
                    or disable_scope
                ):
                    key = dep_key.metadata.token or annotation
                    # A modifier
                    if isinstance(key, ForwardRef):
                        key = eval(key.__forward_arg__, globals(), locals())
                    dependency = await self.get(key)
                    setattr(service, name, dependency)
                else:
                    _name: str = (
                        annotation.__name__
                        if not isinstance(annotation, str)
                        else annotation
                    )
                    raise ValueError(
                        f"Service {_name} not found in scope {search_scope}"
                    )
        origin.remove(service)
        self._services[key] = service

    async def _get_method_dependency(
        self,
        method_to_resolve: Callable,
        search_scope: list,
        disable_scope: bool = False,
    ):
        """
        Resolves dependencies for a method's parameters.

        :param method_to_resolve: The method to resolve dependencies for.
        :param search_scope: The search scope for resolving dependencies.
        :param disable_scope: Whether to disable scope-based resolution.
        :return: A dictionary of resolved dependencies for the method.
        """
        params = inspect.signature(method_to_resolve).parameters
        args = {}
        for name, param in params.items():
            if name != "self" and param.annotation is not inspect.Parameter.empty:
                annotation, dep_key = ContainerHelper.get_type_from_annotation(
                    param.annotation
                )
                if dep_key.metadata.key is not CtxDepKey.Service:
                    dependency = await self._resolve_contextual_service(
                        name, dep_key, annotation
                    )
                    args[name] = dependency
                elif (
                    dep_key.metadata.token in search_scope
                    or annotation in search_scope
                    or disable_scope
                ):
                    dependency = await self.get(dep_key.metadata.token or annotation)
                    args[name] = dependency
                else:
                    _name: str = (
                        annotation.__name__
                        if not isinstance(annotation, str)
                        else annotation
                    )
                    raise ValueError(
                        f"Service {_name} not found in scope {search_scope}"
                    )
        return args

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        if inspect.iscoroutinefunction(method):
            return await method(**args)
        return method(**args)

    async def resolve_factory(
        self,
        factory: Callable,
        inject: list,
        search_scope: list,
        disable_scope: bool = False,
    ):
        """
        Resolves dependencies and calls a factory function to create an instance.

        :param factory: The factory function to call.
        :param inject: Optional list of dependencies to inject into the factory.
        :param search_scope: The search scope for resolving dependencies.
        :param disable_scope: disable scope for searching dependencies.
        :return: The instance created by the factory.
        """
        search_scope_by_inject = [m for m in inject if m in search_scope]
        args = await self._get_method_dependency(
            method_to_resolve=factory,
            search_scope=search_scope_by_inject,
            disable_scope=disable_scope,
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
        self,
        key: Union[Type, str, object],
        method: str = _INIT,
        origin: Optional[list] = None,
        disable_scope: bool = False,
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(
            method_to_resolve, search_scope, disable_scope=disable_scope
        )
        if method == _INIT:
            result = service(**args)
            if service in self._singleton_classes:
                self._singleton_instances[service] = result
        else:
            # Service must be an instance (controller)
            instance = await self.get(key)
            instance_method = getattr(instance, method, method_to_resolve)
            result = await self._call_method(instance_method, args)

        origin.remove(service)
        return result

    async def get(
        self,
        key: Union[Type, str],
        method: str = _INIT,
        origin: Optional[list] = None,
        disable_scope: Optional[bool] = False,
    ) -> Awaitable[object]:
        """
        Retrieves an instance of a service, creating it if necessary.

        :param key: The service class or token to retrieve.
        :param method: The name of the method to resolve.
        :param origin: The list of services currently being resolved.
        :param disable_scope: Disabling scope of search for dependencies.
        :return: The service instance.
        """
        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            await self._resolve_property(
                key, origin=origin, disable_scope=disable_scope
            )
        return await self._resolve_method(
            key, method=method, origin=origin, disable_scope=disable_scope
        )
