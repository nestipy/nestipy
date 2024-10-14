from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.core import ExecutionContext


class RequestContextContainer:
    _instance: Union["RequestContextContainer", None] = None
    execution_context: Union["ExecutionContext", None] = None

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

    def destroy(self):
        self._instance = None
