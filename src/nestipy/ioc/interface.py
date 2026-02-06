from typing import Protocol, Type, Union, Any, Awaitable, Optional, Callable


class NestipyIContainer(Protocol):
    def add_transient(self, service: Type): ...

    def add_singleton(self, service: Type): ...

    def add_singleton_instance(
        self, service: Union[Type, str], service_instance: object
    ): ...

    async def get(
        self,
        key: Union[Type, str],
        method: str = "__init__",
        origin: Optional[list] = None,
        disable_scope: Optional[bool] = False,
    ) -> Union[object, Awaitable[object]]: ...

    async def resolve_factory(
        self,
        factory: Callable,
        inject: list,
        search_scope: list,
        disable_scope: bool = False,
    ): ...
