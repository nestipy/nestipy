from typing import Union, Type, Callable

from nestipy.graphql.graphql_adapter import GraphqlAdapter
from .graphql_explorer import GraphqlExplorer
from .graphql_module import GraphqlModule, GraphqlOption
from ..common import Request
from ..common.guards.exector import GuardProcessor
from ..common.metadata.container import NestipyContainerKey
from ..core.adapter.http_adapter import HttpAdapter
from ..core.context.execution_context import ExecutionContext
from ..core.ioc.nestipy_container import NestipyContainer
from ..core.ioc.nestipy_context_container import NestipyContextContainer


class GraphqlProxy:

    def __init__(self, adapter: HttpAdapter, graphql_server: GraphqlAdapter):
        self._graphql_server = graphql_server
        self._adapter = adapter

    def apply_resolvers(self, graphql_module: GraphqlModule, modules: set[Union[Type, object]]):

        for module_ref in modules:
            query, mutation, subscription = GraphqlExplorer.explore(module_ref)
            for q in query:
                name, return_type, resolver = self._create_graphql_query_handler(q)
                self._graphql_server.add_query_property(name, return_type, resolver)
            for m in mutation:
                name, return_type, resolver = self._create_graphql_query_handler(m)
                self._graphql_server.add_mutation_property(name, return_type, resolver)
            for s in subscription:
                name, return_type, resolver = self._create_graphql_query_handler(s)
                self._graphql_server.add_subscription_property(name, return_type, resolver)

        self._create_graphql_request_handler(graphql_module.config or GraphqlOption())

    def _create_graphql_query_handler(self, meta: dict) -> tuple[str, Type, Callable]:
        resolver: Union[object, Type] = meta['class']
        method_name: str = meta['handler_name']
        method = getattr(resolver, method_name)

        async def graphql_handler(*_args, **kwargs):
            context_container = NestipyContextContainer.get_instance()
            context_container.set_value(NestipyContainerKey.args, kwargs)
            try:
                # TODO: Refactor with routerProxy
                # create execution context
                execution_context = ExecutionContext(
                    resolver,
                    getattr(resolver, method_name),
                    context_container.get_value(NestipyContainerKey.request),
                    context_container.get_value(NestipyContainerKey.response)
                )
                #  apply guards
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # TODO: is this need to specify return Exception
                    raise Exception(f"Not authorized from guard {can_activate[1]}")

                # perform query request
                ins = NestipyContainer.get_instance()
                result = await ins.get(resolver, method_name)
                return result
            finally:
                context_container.destroy()

        # mutate handle inside adapter
        return_type = self._graphql_server.mutate_handler(method, graphql_handler)
        return method_name, return_type, graphql_handler,

    def _create_graphql_request_handler(self, option: GraphqlOption):
        self._adapter.mount(
            f"/{option.url.strip('/')}",
            self._graphql_server.create_graphql_asgi_app(
                option=option,
                schema=self._graphql_server.create_schema()
            ).handle
        )

    @classmethod
    def should_render_graphql_ide(cls, req: Request) -> bool:
        return (
                req.method == "GET"
                and req.query_params.get("query") is None
                and any(supported_header in req.headers.get("accept", "") for supported_header in ("text/html", "*/*"))
        )
