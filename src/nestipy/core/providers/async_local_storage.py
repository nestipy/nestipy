import inspect
from contextvars import ContextVar
from typing import Optional, Dict, Callable, TypeVar, Awaitable, Generic

from nestipy.common import Injectable

T = TypeVar("T")
R = TypeVar("R")


@Injectable()
class AsyncLocalStorage(Generic[T]):
    def __init__(self):
        # Create a ContextVar to store the local state
        self._store: ContextVar[Optional[Dict[str, T]]] = ContextVar(
            "store", default=None
        )

    async def run(self, data: Dict[str, T], func: Callable[..., R | Awaitable[R]]) -> R:
        """
        Async version of the `run` method.
        """
        token = self._store.set(data)
        try:
            if inspect.iscoroutinefunction(func):
                return await func()  # Execute the async function within this context
            else:
                return func()  # Execute the sync function within this context
        finally:
            self._store.reset(token)

    def get_store(self) -> Optional[Dict[str, T]]:
        """
        Retrieve the current store.
        """
        return self._store.get()

    def set_value(self, key: str, value: T):
        """
        Set a specific key-value pair in the current store.
        """
        store = self._store.get()
        if store is not None:
            store[key] = value
        else:
            raise RuntimeError("No active store found")

    def get_value(self, key: str, default: T | None = None) -> T | None:
        """
        Retrieve a specific value from the current store.
        """
        store = self._store.get()
        if store is not None and key in store:
            return store[key]
        return default
        # raise KeyError(f"No value found for key: {key}")
