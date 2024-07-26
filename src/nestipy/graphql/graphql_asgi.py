import os
from abc import abstractmethod
from typing import Callable, cast

import aiofiles

from nestipy.ioc import RequestContextContainer

from nestipy.common.http_ import Request, Response
from nestipy.graphql.graphql_module import GraphqlOption


class GraphqlAsgi:
    option: GraphqlOption = None

    def set_graphql_option(self, option: GraphqlOption):
        self.option = option

    async def get_graphql_ide(self) -> str:
        playground_path = os.path.join(
            os.path.dirname(__file__),
            'playground',
            f'graphql-playground-{self.option.ide}.html'
        )
        file = await aiofiles.open(playground_path, 'r')
        content = await file.read()
        await file.close()
        return content

    @abstractmethod
    async def handle(self, scope: dict, receive, send):
        self._setup_request(scope, receive, send)

    def modify_default_context(self, context: dict) -> dict:
        if self.option.context_callback:
            return self.option.context_callback(context)
        return context

    @classmethod
    def _setup_request(cls, scope: dict, receive, send):
        pass
        from nestipy.core import ExecutionContext
        req_container = RequestContextContainer.get_instance()
        req = Request(scope, receive, send)
        res = Response()
        req_container.set_execution_context(ExecutionContext(
            None,
            None,
            None,
            cast(Callable, None),
            req,
            res,
            None,
            None
        ))
