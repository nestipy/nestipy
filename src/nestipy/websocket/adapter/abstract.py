from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class IoAdapter(ABC):
    def __init__(self, path: str = "socket.io"):
        self._path = f"/{path.strip('/')}"

    @abstractmethod
    def on(
        self, event: str, namespace: Optional[str] = None
    ) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def emit(
        self,
        event: Any,
        data: Optional[Any] = None,
        to: Optional[Any] = None,
        room: Optional[Any] = None,
        skip_sid: Optional[Any] = None,
        namespace: Optional[Any] = None,
        callback: Optional[Any] = None,
        ignore_queue: bool = False,
    ):
        pass

    @abstractmethod
    def on_connect(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def on_message(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def on_disconnect(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def broadcast(self, event: Any, data: Any):
        pass

    @abstractmethod
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> bool:
        pass
