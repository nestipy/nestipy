from abc import ABC, abstractmethod
from typing import Type, Union, Callable, TYPE_CHECKING

from nestipy.common import Request, Response

if TYPE_CHECKING:
    from nestipy.core.adapter.http_adapter import HttpAdapter


class ArgumentHost(ABC):

    def __init__(
            self,
            adapter: "HttpAdapter",
            module: Union[Type, object],
            class_handler: Union[Type, object],
            handler: Callable,
            req: Union[Request, Request],
            res: Union[Response, None]
    ):
        self._adapter = adapter
        self._module = module
        self._handler = handler
        self._class_handler = class_handler
        self._req = req
        self._res = res

    def get_adapter(self) -> "HttpAdapter":
        return self._adapter

    def get_module(self) -> Union[Type, object, None]:
        return self._module

    def get_request(self) -> Request:
        return self._req

    def get_response(self) -> Response:
        return self._res

    def get_class(self) -> Union[Type, None]:
        return self._class_handler

    def get_handler(self) -> Union[Callable, None]:
        return self._handler

    @abstractmethod
    def get_args(self):
        pass
