import os
from abc import abstractmethod

import aiofiles
from nestipy_ioc import NestipyContextContainer
from nestipy_metadata import NestipyContextProperty

from nestipy.common.http_ import Request
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

    @classmethod
    def _setup_request(cls, scope: dict, receive, send):
        req = Request(scope, receive, send)
        NestipyContextContainer.get_instance().set_value(NestipyContextProperty.request, req)
        pass
