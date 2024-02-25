import inspect
from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Optional, Callable, Any, Awaitable

T = TypeVar('T')


@dataclass
class ModuleOption:
    use_value: Optional[Any]
    use_factory: Optional[Callable[[Any], Any]]


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
    def _create_module(
            cls,
            use_class: Optional[Callable] = None,
            use_value: Optional[Any] = None,
            use_factory: Optional[Awaitable[Callable]] = None,
            token=None,
            inject=None,
            is_async=False):
        if inject is None:
            inject = []
        members = inspect.getmembers(cls, predicate=lambda a: not inspect.ismethod(a))
        class_attrs = {
            'provider_inject__': inject
        }
        if token is not None:
            class_attrs['token__'] = token
        if is_async:
            class_attrs['async__'] = use_value
        if use_value is not None:
            class_attrs['use_value__'] = use_value
        if use_value is not None:
            class_attrs['use_class__'] = use_class
        if use_factory is not None:
            class_attrs['use_factory__'] = use_factory
        for name, value in members:
            if not name.startswith('__'):
                class_attrs[name] = value
        return type(cls.__name__, (DynamicModule,), class_attrs)

    @classmethod
    def register(cls, value=None, token=None):
        return cls._create_module(use_value=value, token=token)

    @classmethod
    def register_async(cls, option: ModuleOption, token, inject: list[Callable]):
        create_module_params = {
            'inject': inject or [],
            'is_async': True
        }
        if option is not None:
            if option.use_value is not None:
                create_module_params['use_value'] = option.use_value
            if option.use_factory is not None:
                create_module_params['use_factory'] = option.use_factory
        return cls._create_module(token=token, **create_module_params)
