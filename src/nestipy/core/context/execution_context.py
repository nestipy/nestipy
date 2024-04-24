from typing import Type, Callable, Union

from nestipy.common.http_ import Response, Request
from .argument_host import ArgumentHost
from .http_argument_host import HttpArgumentHost


class ExecutionContext(ArgumentHost):
    def get_args(self) -> tuple[Union[Type, object], Callable, Union[Request, None], Union[Response, None]]:
        return self.get_class(), self.get_handler(), self.get_request(), self.get_response()

    def switch_to_http(self) -> HttpArgumentHost:
        return HttpArgumentHost(
            self.get_adapter(),
            self.get_module(),
            self.get_class(),
            self.get_handler(),
            self.get_request(),
            self.get_response()
        )

    def switch_to_graphql(self):
        pass

    def get_context(self):
        return self
