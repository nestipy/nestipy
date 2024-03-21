from typing import Union, Awaitable, Any, Callable, Type

from nestipy.core.ioc.nestipy_container import NestipyContainer


class ModuleProviderDict:
    inject: list = []
    provide: Union[str, Type]
    value: Any = None
    factory: Callable[..., Union[Awaitable, Any]] = None
    existing: Any = None

    def __init__(
            self,
            provide: Union[str, Type],
            value: Any = None,
            factory: Callable[..., Union[Awaitable, Any]] = None,
            existing: Any = None,
            inject: list = None
    ):
        self.provide = provide
        self.value = value
        self.factory = factory
        self.existing = existing
        self.inject = inject or []
        NestipyContainer.get_instance().add_singleton_instance(provide, self)
