from typing import TYPE_CHECKING

from nestipy.common.http_ import Response, Request
from .argument_host import ArgumentHost

if TYPE_CHECKING:
    from nestipy.common.http_ import Request, Response


class GraphqlArgumentHost(ArgumentHost):
    def get_request(self) -> Request:
        return self._req

    def get_response(self) -> Response:
        return self._res

    def get_args(self) -> dict:
        return self._graphql_args

    def get_context(self):
        return self._graphql_context
