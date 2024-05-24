from typing import Union, Any, TYPE_CHECKING

from nestipy.metadata import NestipyContextProperty

if TYPE_CHECKING:
    from nestipy.core import ExecutionContext
    from nestipy.ioc import NestipyContainer


class RequestContextContainer:
    _instance: Union["RequestContextContainer", None] = None
    execution_context: "ExecutionContext"
    container: "NestipyContainer"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RequestContextContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def set_execution_context(cls, context: "ExecutionContext"):
        ins = cls.get_instance()
        ins.execution_context = context

    @classmethod
    def set_container(cls, container: "NestipyContainer"):
        ins = cls.get_instance()
        ins.container = container

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return RequestContextContainer(*args, **kwargs)

    def destroy(self):
        self._instance = None
