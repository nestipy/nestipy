import traceback
from typing import Union, Type, Callable

from nestipy.core.guards import GuardProcessor
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from .graphql_explorer import GraphqlExplorer
from .graphql_module import GraphqlModule, GraphqlOption
from ..common import Request, Response
from ..common.logger import logger
from ..core.adapter.http_adapter import HttpAdapter
from ..core.context.execution_context import ExecutionContext
from ..types_ import NextFn


class GraphqlProxy:

    def __init__(self, adapter: HttpAdapter, graphql_server: GraphqlAdapter):
        self._graphql_server = graphql_server
        self._adapter = adapter
        self.container = NestipyContainer.get_instance()

    def apply_resolvers(self, graphql_module: GraphqlModule, modules: list[Union[Type, object]]):

        for module_ref in modules:
            query, mutation, subscription = GraphqlExplorer.explore(module_ref)
            for q in query:
                name, return_type, resolver = self._create_graphql_query_handler(module_ref, q)
                self._graphql_server.add_query_property(name, return_type, resolver)
            for m in mutation:
                name, return_type, resolver = self._create_graphql_query_handler(module_ref, m)
                self._graphql_server.add_mutation_property(name, return_type, resolver)
            for s in subscription:
                name, return_type, resolver = self._create_graphql_query_handler(module_ref, s)
                self._graphql_server.add_subscription_property(name, return_type, resolver)

        self._create_graphql_request_handler(graphql_module.config or GraphqlOption())

    def _create_graphql_query_handler(self, module_ref: Union[Type, object], meta: dict) -> tuple[str, Type, Callable]:
        resolver: Union[object, Type] = meta['class']
        method_name: str = meta['handler_name']
        method = getattr(resolver, method_name)

        async def graphql_handler(*_args, **kwargs):
            context_container = RequestContextContainer.get_instance()
            execution_context = ExecutionContext(
                self._adapter,
                module_ref,
                resolver,
                getattr(resolver, method_name),
                None,
                None,
                kwargs,
                None

            )
            context_container.set_execution_context(execution_context)
            try:
                # TODO: Refactor with routerProxy
                # create execution context

                #  apply guards
                guard_processor: GuardProcessor = await self.container.get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # TODO: is this need to specify return Exception
                    raise Exception(f"Not authorized from guard {can_activate[1]}")

                # perform query request
                result = await self.container.get(resolver, method_name)
                return result
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                context_container.destroy()
                return self._graphql_server.raise_exception(e)
            finally:
                context_container.destroy()

        # mutate handle inside adapter
        return_type = self._graphql_server.mutate_handler(method, graphql_handler)
        return method_name, return_type, graphql_handler,

    def _create_graphql_request_handler(self, option: GraphqlOption):
        graphql_path = f"/{option.url.strip('/')}"
        # create graphql handler but using handle of graphql_adapter
        self._adapter.mount(
            graphql_path,
            self._graphql_server.create_graphql_asgi_app(
                option=option,
                schema=self._graphql_server.create_schema()
            ).handle
        )

        async def graphql_redirect(_req: Request, res: Response, _next_fn: NextFn):
            return await res.redirect(f"{graphql_path}/")

        self._adapter.get(graphql_path, graphql_redirect, {})

    @classmethod
    def should_render_graphql_ide(cls, req: Request) -> bool:
        return (
                req.method == "GET"
                and req.query_params.get("query") is None
                and any(supported_header in req.headers.get("accept", "") for supported_header in ("text/html", "*/*"))
        )
