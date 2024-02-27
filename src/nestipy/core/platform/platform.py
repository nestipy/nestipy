from abc import abstractmethod, ABC
from typing import Generic, TypeVar, Callable, Any

T = TypeVar('T')


class PlatformAdapter(Generic[T], ABC):
    app: T
    _handlers: list[Callable] = []
    _hooks: list[Callable] = []
    _listeners: list[Callable] = []

    def get_handlers(self):
        return self._handlers

    def add_handler(self, handler: Callable):
        self._handlers.append(handler)

    def get_hooks(self):
        return self._hooks

    def listeners(self):
        return self._listeners

    def add_listener(self, listener: Callable):
        self._listeners.append(listener)

    @abstractmethod
    async def setup(self, module):
        pass

    @abstractmethod
    def create_server(self, *args, **kwargs) -> T:
        pass
