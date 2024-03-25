from typing import Union, Awaitable, Any, Callable, Type

from nestipy.core.ioc.nestipy_container import NestipyContainer


class ModuleProviderDict:
    inject: list = []
    token: Union[str, Type]
    value: Any = None
    factory: Callable[..., Union[Awaitable, Any]] = None
    existing: Union[Type, str] = None
    use_class: Type = None

    def __init__(
            self,
            provide: Union[str, Type],
            value: Any = None,
            factory: Callable[..., Union[Awaitable, Any]] = None,
            existing:  Union[Type, str] = None,
            use_class: Type = None,
            inject: list = None
    ):
        self.token = provide
        self.value = value
        self.factory = factory
        self.existing = existing
        self.use_class = use_class
        self.inject = inject or []
        NestipyContainer.get_instance().add_singleton_instance(provide, self)
