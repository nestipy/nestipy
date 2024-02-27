import inspect
from abc import ABC
from typing import TypeVar

from nestipy.core.module.provider import ModuleProvider

T = TypeVar('T')


class DynamicModule(ABC):
    providers = []
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_container(self):
        if hasattr(self, 'container__'):
            return getattr(self, 'container__')
        else:
            return None

    @classmethod
    def _create_module(cls, provider: ModuleProvider = None):
        members = inspect.getmembers(cls, predicate=lambda a: not inspect.ismethod(a))
        class_attrs = {}
        if provider is not None:
            class_attrs['module_provider__'] = provider
        for name, value in members:
            if not name.startswith('__'):
                class_attrs[name] = value
        return type(cls.__name__, (DynamicModule,), class_attrs)

    @classmethod
    def register(cls, provide=None, value=None, inject: list = None):
        provider = None
        if provide is not None and value is not None:
            provider = ModuleProvider(provide=provide, use_value=value, inject=inject or [])
        return cls._create_module(provider=provider)

    @classmethod
    def register_async(cls, provider: ModuleProvider = None):
        return cls._create_module(provider=provider)
