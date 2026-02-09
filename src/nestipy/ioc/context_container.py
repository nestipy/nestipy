from contextvars import ContextVar
from typing import Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nestipy.core import ExecutionContext


class RequestContextContainer:
    _instance: Union["RequestContextContainer", None] = None
    _execution_context: ContextVar[Optional["ExecutionContext"]] = ContextVar(
        "nestipy_execution_context", default=None
    )
    _request_cache: ContextVar[Optional[dict]] = ContextVar(
        "nestipy_request_cache", default=None
    )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RequestContextContainer, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    @classmethod
    def set_execution_context(cls, context: "ExecutionContext"):
        ins = cls.get_instance()
        ins.execution_context = context

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return RequestContextContainer(*args, **kwargs)

    @property
    def execution_context(self) -> Union["ExecutionContext", None]:
        return self._execution_context.get()

    @execution_context.setter
    def execution_context(self, context: Optional["ExecutionContext"]) -> None:
        self._execution_context.set(context)
        if context is not None and self._request_cache.get() is None:
            self._request_cache.set({})

    def get_request_cache(self) -> Optional[dict]:
        return self._request_cache.get()

    def set_request_cache(self, cache: Optional[dict]) -> None:
        self._request_cache.set(cache)

    def reset_request_cache(self) -> None:
        self._request_cache.set({})

    def destroy(self):
        self._execution_context.set(None)
        self._request_cache.set(None)
        self._instance = None
