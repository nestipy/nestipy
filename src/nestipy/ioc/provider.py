from typing import Union, Awaitable, Any, Callable, Type

from .container import NestipyContainer


class ModuleProviderDict:
    inject: list = []
    imports: list = []
    token: Union[str, Type]
    value: Any = None
    factory: Callable[..., Union[Awaitable, Any]] = None
    existing: Union[Type, str] = None
    use_class: Union[Type] = None

    def __init__(
        self,
        token: Union[str, Type],
        value: Any = None,
        factory: Union[Callable[..., Union[Awaitable, Any]], None] = None,
        existing: Union[Type, str, None] = None,
        use_class: Union[Type, None] = None,
        inject: Union[list, None] = None,
        imports: Union[list[Type], None] = None,
    ):
        self.token = token
        self.value = value
        self.factory = factory
        self.existing = existing
        self.use_class = use_class
        self.inject = inject or []
        self.imports = imports or []
        NestipyContainer.get_instance().add_singleton_instance(token, self)
