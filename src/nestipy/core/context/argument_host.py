from abc import ABC, abstractmethod
from typing import Type, Union, Callable

from nestipy.common import Request, Response


class ArgumentHost(ABC):

    def __init__(self, class_handler: Union[Type, object], handler: Callable, req: Request, res: Response):
        self._handler = handler
        self._class_handler = class_handler
        self._req = req
        self._res = res

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
