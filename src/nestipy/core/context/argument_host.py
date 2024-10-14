from abc import ABC, abstractmethod
from typing import Type, Union, Callable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nestipy.core.adapter.http_adapter import HttpAdapter
    from nestipy.common.http_ import Request, Response


class ArgumentHost(ABC):
    def __init__(
        self,
        adapter: Union["HttpAdapter", None],
        module: Union[Type, object],
        class_handler: Union[Type, object],
        handler: Callable,
        req: Union["Request", None],
        res: Union["Response", None],
        graphql_args: Optional[dict] = None,
        graphql_context: Optional[any] = None,
        socket_server: Optional[any] = None,
        socket_client: Optional[any] = None,
        socket_data: Optional[any] = None,
    ):
        self._adapter = adapter
        self._module = module
        self._handler = handler
        self._class_handler = class_handler
        self._req = req
        self._res = res
        self._graphql_args = graphql_args or {}
        self._graphql_context = graphql_context or None
        self._socket_server = socket_server
        self._socket_client = socket_client
        self._socket_data = socket_data

    def get_adapter(self) -> Union["HttpAdapter", None]:
        return self._adapter

    def get_module(self) -> Union[Type, object, None]:
        return self._module

    def get_request(self) -> Union["Request", None]:
        return self._req

    def get_response(self) -> "Response":
        return self._res

    def get_class(self) -> Union[Type, None]:
        return self._class_handler

    def get_handler(self) -> Union[Callable, None]:
        return self._handler

    @abstractmethod
    def get_args(self):
        pass
