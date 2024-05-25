import os
from abc import abstractmethod

import aiofiles

from nestipy.ioc import RequestContextContainer

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
        pass
        # from nestipy.core import ExecutionContext
        # req = Request(scope, receive, send)
        # req_container = RequestContextContainer.get_instance()
        # res = req_container.execution_context.get_response()
        # class_handler = req_container.execution_context.get_class()
        # handler = req_container.execution_context.get_handler()
        # module = req_container.execution_context.get_module()
        # adapter = req_container.execution_context.get_adapter()
        # graphql = req_container.execution_context.switch_to_graphql()
        # req_container.set_execution_context(ExecutionContext(
        #     adapter,
        #     module,
        #     class_handler,
        #     handler,
        #     req,
        #     res,
        #     graphql.get_context(),
        #     graphql.get_args()
        # ))
