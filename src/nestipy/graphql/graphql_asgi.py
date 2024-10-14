import os
from abc import abstractmethod
from typing import Callable, cast, Optional

import aiofiles

from nestipy.ioc import RequestContextContainer, NestipyContainer

from nestipy.common.http_ import Request, Response
from nestipy.graphql.graphql_module import GraphqlOption


class GraphqlAsgi:
    option: Optional[GraphqlOption] = None

    @abstractmethod
    def print_schema(self) -> str:
        pass

    def set_graphql_option(self, option: GraphqlOption):
        self.option = option

    async def get_graphql_ide(self) -> str:
        playground_path = os.path.join(
            os.path.dirname(__file__),
            "playground",
            f"graphql-playground-{self.option.ide}.html",
        )
        file = await aiofiles.open(playground_path, "r")
        content = await file.read()
        await file.close()
        return content

    @abstractmethod
    async def handle(self, scope: dict, receive, send):
        self._setup_request(scope, receive, send)

    async def modify_default_context(self, context: dict) -> dict:
        if self.option.context_callback:
            return await NestipyContainer.get_instance().resolve_factory(
                self.option.context_callback,
                inject=[],
                search_scope=[],
                disable_scope=True,
            )
        return context

    @classmethod
    def _setup_request(cls, scope: dict, receive, send):
        from nestipy.core import ExecutionContext

        req_container = RequestContextContainer.get_instance()
        req = Request(scope, receive, send)
        res = Response()
        req_container.set_execution_context(
            ExecutionContext(
                None, None, None, cast(Callable, None), req, res, None, None
            )
        )
