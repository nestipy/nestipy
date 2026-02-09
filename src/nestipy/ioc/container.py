import inspect
import sys
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
from nestipy.common.pipes import PipeTransform, PipeArgumentMetadata
from nestipy.common.constant import (
    NESTIPY_SCOPE_ATTR,
    SCOPE_REQUEST,
    SCOPE_SINGLETON,
    SCOPE_TRANSIENT,
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
    _request_scoped_classes: set = set()
    _method_dependency_cache: dict = {}
    _dependency_metadata_cache: dict = {}

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

    @classmethod
    def clear(cls):
        """
        Resets the singleton instance and all registered services.
        Used primarily for testing.
        """
        cls._instance = None
        cls._services = {}
        cls._global_service_instances = {}
        cls._singleton_instances = {}
        cls._singleton_classes = set()
        cls._request_scoped_classes = set()
        cls._method_dependency_cache = {}
        cls._dependency_metadata_cache = {}

    def add_transient(self, service: Type):
        """
        Registers a transient service in the container.
        Transient services are created every time they are requested.

        :param service: The service class to be registered.
        """
        self._services[service] = service

    def add_request_scoped(self, service: Type):
        """
        Registers a request-scoped service in the container.
        Request-scoped services are cached per-request using RequestContextContainer.
        """
        self._services[service] = service
        self._request_scoped_classes.add(service)

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

        if service in cls._dependency_metadata_cache:
            return cls._dependency_metadata_cache[service]

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
            deps = uniq(uniq_providers)
            cls._dependency_metadata_cache[service] = deps
            return deps
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        deps = []
        cls._dependency_metadata_cache[service] = deps
        return deps

    @classmethod
    def precompute_dependency_graph(cls, modules: list[Type]) -> None:
        cls._dependency_metadata_cache = {}
        candidates: set = set(cls._services.keys())
        from .provider import ModuleProviderDict

        for module in modules:
            # Avoid importing DynamicModule at top-level to prevent cycles
            if hasattr(module, "module") and hasattr(module, "providers"):
                module = module.module
            providers = Reflect.get_metadata(module, ModuleMetadata.Providers, [])
            controllers = Reflect.get_metadata(module, ModuleMetadata.Controllers, [])
            for p in providers:
                if isinstance(p, ModuleProviderDict):
                    if p.use_class is not None:
                        candidates.add(p.use_class)
                    elif p.existing is not None:
                        candidates.add(p.existing)
                    elif p.token is not None and not isinstance(p.token, str):
                        candidates.add(p.token)
                else:
                    candidates.add(p)
            for c in controllers:
                candidates.add(c)
            candidates.add(module)

        for service in list(candidates):
            try:
                cls.get_dependency_metadata(service)
            except Exception:
                continue

    @classmethod
    def get_dependency_graph(cls) -> dict[str, list[str]]:
        def _format_key(k: Union[Type, str, object]) -> str:
            from nestipy.metadata.provider_token import ProviderToken

            if isinstance(k, ProviderToken):
                return f"Token({k.key})"
            if isinstance(k, str):
                return k
            if inspect.isclass(k):
                return k.__name__
            return str(k)

        graph: dict[str, list[str]] = {}
        for key, deps in cls._dependency_metadata_cache.items():
            graph[_format_key(key)] = [_format_key(d) for d in deps]
        return graph

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

    async def _check_exist_singleton(self, key: Union[Type, str, object]):
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
                        f"Service {instance.__class__.__name__} not found in scope"
                    )
            else:
                return instance
        return None

    def _check_service(
        self, key: Union[Type, str, object], origin: Optional[set] = None
    ) -> tuple:
        """
        Checks if a service is registered and detects circular dependencies.

        :param key: The service class or token.
        :param origin: The list of services currently being resolved to avoid circular dependency.
        :return: The service class and updated origin list.
        :raises ValueError: If the service is not found or circular dependency is detected.
        """
        if key not in self._services:
            if inspect.isclass(key) and hasattr(key, NESTIPY_SCOPE_ATTR):
                scope = getattr(key, NESTIPY_SCOPE_ATTR, SCOPE_SINGLETON)
                if scope == SCOPE_TRANSIENT:
                    self.add_transient(key)
                elif scope == SCOPE_REQUEST:
                    self.add_request_scoped(key)
                else:
                    self.add_singleton(key)
            else:
                raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(
                f"Circular dependency found  for {service.__name__} service "
            )
        return service, origin or set()

    async def _resolve_property(
        self,
        key: Union[Type, str, object],
        origin: Optional[set] = None,
        disable_scope: bool = False,
        instance: Optional[object] = None,
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
        target = instance or service
        for name, param_annotation in annotations.items():
            annotation, dep_key = ContainerHelper.get_type_from_annotation(
                param_annotation
            )
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_contextual_service(
                    name, dep_key, annotation
                )
                setattr(target, name, dependency)
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
                        module = sys.modules.get(service.__module__)
                        global_ns = vars(module) if module else globals()
                        key = eval(key.__forward_arg__, global_ns, locals())
                    dependency = await self.get(
                        key, origin=origin, disable_scope=disable_scope
                    )
                    setattr(target, name, dependency)
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
        """
        Update the service in the container after resolving its properties.
        """

    async def _get_method_dependency(
        self,
        method_to_resolve: Callable,
        search_scope: list,
        disable_scope: bool = False,
        origin: Optional[set] = None,
    ):
        """
        Resolves dependencies for a method's parameters.

        :param method_to_resolve: The method to resolve dependencies for.
        :param search_scope: The search scope for resolving dependencies.
        :param disable_scope: Whether to disable scope-based resolution.
        :return: A dictionary of resolved dependencies for the method.
        """
        cached = self._method_dependency_cache.get(method_to_resolve)
        if cached is None:
            params = inspect.signature(method_to_resolve).parameters
            descriptors = []
            for name, param in params.items():
                if name == "self" or param.annotation is inspect.Parameter.empty:
                    continue
                annotation, dep_key = ContainerHelper.get_type_from_annotation(
                    param.annotation
                )
                descriptors.append((name, annotation, dep_key))
            self._method_dependency_cache[method_to_resolve] = descriptors
        else:
            descriptors = cached

        args = {}
        context_container = RequestContextContainer.get_instance()
        execution_context = context_container.execution_context
        pipes = execution_context.get_pipes() if execution_context else []
        for name, annotation, dep_key in descriptors:
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_contextual_service(
                    name, dep_key, annotation
                )
                if self._can_apply_pipes(dep_key.metadata.key):
                    param_pipes = list(getattr(dep_key.metadata, "pipes", [])) or []
                    pipes_to_apply = [*pipes, *param_pipes]
                    metadata = PipeArgumentMetadata(
                        type=self._pipe_type_from_key(dep_key.metadata.key),
                        metatype=annotation if isinstance(annotation, type) else None,
                        data=dep_key.metadata.token or name,
                    )
                    dependency = await self._apply_pipes(
                        dependency,
                        pipes_to_apply,
                        metadata,
                        origin=origin,
                        disable_scope=disable_scope,
                    )
                args[name] = dependency
            elif (
                dep_key.metadata.token in search_scope
                or annotation in search_scope
                or disable_scope
            ):
                dependency = await self.get(
                    dep_key.metadata.token or annotation,
                    origin=origin,
                    disable_scope=disable_scope,
                )
                args[name] = dependency
            else:
                _name: str = (
                    annotation.__name__ if not isinstance(annotation, str) else annotation
                )
                raise ValueError(
                    f"Service {_name} not found in scope {search_scope}"
                )
        return args

    @staticmethod
    def _pipe_type_from_key(key: str) -> str:
        mapping = {
            CtxDepKey.Body: "body",
            CtxDepKey.Query: "query",
            CtxDepKey.Queries: "query",
            CtxDepKey.Param: "param",
            CtxDepKey.Params: "param",
            CtxDepKey.Header: "header",
            CtxDepKey.Headers: "header",
            CtxDepKey.Cookie: "cookie",
            CtxDepKey.Cookies: "cookie",
            CtxDepKey.Session: "session",
            CtxDepKey.Sessions: "session",
            CtxDepKey.Args: "args",
            CtxDepKey.Arg: "args",
        }
        return mapping.get(key, "custom")

    @staticmethod
    def _can_apply_pipes(key: str) -> bool:
        return key in {
            CtxDepKey.Body,
            CtxDepKey.Query,
            CtxDepKey.Queries,
            CtxDepKey.Param,
            CtxDepKey.Params,
            CtxDepKey.Header,
            CtxDepKey.Headers,
            CtxDepKey.Cookie,
            CtxDepKey.Cookies,
            CtxDepKey.Session,
            CtxDepKey.Sessions,
            CtxDepKey.Args,
            CtxDepKey.Arg,
        }

    async def _apply_pipes(
        self,
        value: Any,
        pipes: list,
        metadata: PipeArgumentMetadata,
        origin: Optional[set] = None,
        disable_scope: bool = False,
    ) -> Any:
        if not pipes:
            return value
        current = value
        for pipe in pipes:
            instance = pipe
            if inspect.isclass(pipe) and issubclass(pipe, PipeTransform):
                if pipe in self._services:
                    instance = await self.get(
                        pipe, origin=origin, disable_scope=disable_scope
                    )
                else:
                    instance = pipe()
            if not hasattr(instance, "transform"):
                raise ValueError(
                    f"Pipe {pipe} does not implement transform(value, metadata)"
                )
            try:
                transform = getattr(instance, "transform")
                if inspect.iscoroutinefunction(transform):
                    current = await transform(current, metadata)
                else:
                    current = transform(current, metadata)
            except Exception as exc:
                from nestipy.common.exception.http import HttpException
                from nestipy.common.exception.status import HttpStatus
                from nestipy.common.exception.message import HttpStatusMessages

                if isinstance(exc, HttpException):
                    raise
                pipe_name = (
                    pipe.__name__
                    if inspect.isclass(pipe)
                    else instance.__class__.__name__
                )
                raise HttpException(
                    HttpStatus.BAD_REQUEST,
                    HttpStatusMessages.BAD_REQUEST,
                    details={"pipe": pipe_name, "error": str(exc)},
                ) from exc
        return current

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        """
        Call a method (sync or async) with the provided arguments.
        :param method: The method to call.
        :param args: The arguments to pass.
        :return: The result of the call.
        """
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
            origin=None,  # Or should we pass something here?
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
        self,
        key: Union[Type, str, object],
        method: str = _INIT,
        origin: Optional[set] = None,
        disable_scope: bool = False,
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(
            method_to_resolve, search_scope, disable_scope=disable_scope, origin=origin
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
        key: Union[Type, str, object],
        method: str = _INIT,
        origin: Optional[set] = None,
        disable_scope: bool = False,
    ) -> Union[object, Awaitable[object]]:
        """
        Retrieves an instance of a service, creating it if necessary.

        :param key: The service class or token to retrieve.
        :param method: The name of the method to resolve.
        :param origin: The list of services currently being resolved.
        :param disable_scope: Disabling scope of search for dependencies.
        :return: The service instance.
        """
        if method == _INIT and key in self._request_scoped_classes:
            context_container = RequestContextContainer.get_instance()
            cache = context_container.get_request_cache()
            if cache is not None and key in cache:
                return cache[key]

        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            if method == _INIT and key in self._singleton_classes:
                await self._resolve_property(
                    key, origin=origin, disable_scope=disable_scope
                )
        result = await self._resolve_method(
            key, method=method, origin=origin, disable_scope=disable_scope
        )
        if method == _INIT and key not in self._singleton_classes:
            await self._resolve_property(
                key, origin=origin, disable_scope=disable_scope, instance=result
            )
        if method == _INIT and key in self._request_scoped_classes:
            context_container = RequestContextContainer.get_instance()
            cache = context_container.get_request_cache()
            if cache is not None:
                cache[key] = result
        return result
