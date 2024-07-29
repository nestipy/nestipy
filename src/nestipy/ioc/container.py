import inspect
from functools import lru_cache
from typing import Type, Union, Any, Optional, Callable, Awaitable, TYPE_CHECKING

from nestipy.metadata import ClassMetadata, CtxDepKey, ModuleMetadata, ProviderToken, Reflect
from .context_container import RequestContextContainer
from .dependency import TypeAnnotated
from .meta import ContainerHelper
from .utils import uniq

if TYPE_CHECKING:
    from .provider import ModuleProviderDict

_INIT = "__init__"


class NestipyContainer:
    _instance: "NestipyContainer" = None
    _services = {}
    _global_service_instances = {}
    _singleton_instances = {}
    _singleton_classes = set()
    helper = ContainerHelper()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NestipyContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return NestipyContainer(*args, **kwargs)

    def add_transient(self, service: Type):
        self._services[service] = service

    def add_singleton(self, service: Type):
        self._services[service] = service
        self._singleton_classes.add(service)

    def get_all_services(self) -> list:
        return list(self._services.keys())

    def add_singleton_instance(self, service: Union[Type, str], service_instance: object):
        self._singleton_instances[service] = service_instance

    def get_all_singleton_instance(self) -> list:
        return [v for k, v in self._singleton_instances.items()]

    @classmethod
    @lru_cache()
    def get_global_providers(cls) -> list:
        global_providers = []
        for service in cls._services:
            if service in global_providers:
                continue
            metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
            if metadata is not None:
                is_global = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Global, False)
                is_root = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Root, False)
                if is_global or is_root:
                    global_providers += Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Providers, [])
        return uniq(global_providers)

    @classmethod
    def get_dependency_metadata(cls, service: Union[Type, object]) -> list:
        from .provider import ModuleProviderDict
        # extract global data from _service, not from module because all provider is already saved in _services of
        # container
        metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
        if metadata is not None:
            global_providers = cls.get_global_providers()
            providers, import_providers = metadata.get_service_providers()
            uniq_providers = []
            for m in uniq(providers + global_providers + import_providers):
                if isinstance(m, ModuleProviderDict):
                    for my in m.imports:
                        m_provider, m_import_providers = metadata.get_service_providers(my)
                        uniq_providers = uniq(uniq_providers + m_import_providers + m_provider)
                    uniq_providers.append(m.token)
                else:
                    uniq_providers.append(m)
            return uniq(uniq_providers)
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        return []

    @classmethod
    async def _resolve_context_service(cls, name: str, dep_key: TypeAnnotated, annotation: Union[Type, Any]):
        context_container = RequestContextContainer.get_instance()
        callback = dep_key.metadata.callback
        if inspect.iscoroutinefunction(callback):
            return await callback(name, dep_key.metadata.token, annotation, context_container)
        else:
            return callback(name, dep_key.metadata.token, annotation, context_container)

    async def _resolve_module_provider_dict(self, instance: "ModuleProviderDict", search_scope: list):
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
                search_scope=search_scope
            )

        else:
            return None

    async def _check_exist_singleton(self, key: Union[Type, str]):
        from .provider import ModuleProviderDict
        if key in self._singleton_instances:
            instance = self._singleton_instances[key]
            # to keep improve
            if isinstance(instance, ModuleProviderDict):
                search_scope = self.get_dependency_metadata(instance)
                if instance.token in search_scope:
                    value = await self._resolve_module_provider_dict(instance, search_scope=search_scope)
                    # update singleton instance to have the async value from ModuleProviderDict
                    self._singleton_instances[key] = value
                    return value
                else:
                    raise ValueError(
                        f"Service {instance.__class__.__name__} "
                        f"not found in scope")
            else:
                return instance
        return None

    def _check_service(self, key: Union[Type, str], origin: Optional[list] = None) -> tuple:
        if key not in self._services:
            raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(f"Circular dependency found  for {service.__name__} service ")
        return service, origin or set()

    async def _resolve_property(
            self,
            key: Union[Type, str],
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        annotations: dict = getattr(service, '__annotations__', {})
        for name, param_annotation in annotations.items():
            annotation, dep_key = self.helper.get_type_from_annotation(param_annotation)
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_context_service(name, dep_key, annotation)
                setattr(service, name, dependency)
            elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                dependency = await self.get(dep_key.metadata.token or annotation)
                setattr(service, name, dependency)
            else:
                _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                raise ValueError(f"Service {_name} not found in scope {search_scope}")
        origin.remove(service)
        self._services[key] = service

    async def _get_method_dependency(
            self,
            method_to_resolve: Callable,
            search_scope: list,
            disable_scope: bool = False
    ):
        params = inspect.signature(method_to_resolve).parameters
        args = {}
        for name, param in params.items():
            if name != 'self' and param.annotation is not inspect.Parameter.empty:
                annotation, dep_key = self.helper.get_type_from_annotation(param.annotation)
                if dep_key.metadata.key is not CtxDepKey.Service:
                    dependency = await self._resolve_context_service(name, dep_key, annotation)
                    args[name] = dependency
                elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                    dependency = await self.get(dep_key.metadata.token or annotation)
                    args[name] = dependency
                else:
                    _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                    raise ValueError(f"Service {_name} not found in scope {search_scope}")
        return args

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        if inspect.iscoroutinefunction(method):
            return await method(**args)
        return method(**args)

    async def resolve_factory(self, factory: Callable, inject: list, search_scope: list, disable_scope: bool = False):
        search_scope_by_inject = [m for m in inject if m in search_scope]
        args = await self._get_method_dependency(
            method_to_resolve=factory,
            search_scope=search_scope_by_inject,
            disable_scope=disable_scope
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
            self,
            key: Union[Type, str, object],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(method_to_resolve, search_scope, disable_scope=disable_scope)
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
            disable_scope: Optional[bool] = False
    ) -> Awaitable[object]:
        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            await self._resolve_property(key, origin=origin, disable_scope=disable_scope)
        return await self._resolve_method(key, method=method, origin=origin, disable_scope=disable_scope)
