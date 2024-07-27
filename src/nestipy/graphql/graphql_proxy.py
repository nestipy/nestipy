import traceback
from typing import Union, Type, Callable

from nestipy.core.guards import GuardProcessor
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.graphql.meta import NestipyGraphqlKey
from nestipy.metadata import Reflect
from .graphql_explorer import GraphqlExplorer
from .graphql_module import GraphqlModule, GraphqlOption
from ..common import Request, Response, HttpException, HttpStatus, HttpStatusMessages
from ..common.logger import logger
from ..core.adapter.http_adapter import HttpAdapter
from ..core.context.execution_context import ExecutionContext
from ..types_ import NextFn


class GraphqlProxy:

    def __init__(self, adapter: HttpAdapter, graphql_server: GraphqlAdapter):
        self._graphql_server = graphql_server
        self._adapter = adapter
        self.container = NestipyContainer.get_instance()

    async def apply_resolvers(self, graphql_module: GraphqlModule, modules: list[Union[Type, object]]):

        for module_ref in modules:
            query, mutation, subscription, field_resolver = GraphqlExplorer.explore(module_ref)
            for q in query:
                name, resolver = self._create_graphql_query_handler(module_ref, q)
                self._graphql_server.add_query_property(name, resolver)
            for m in mutation:
                name, resolver = self._create_graphql_query_handler(module_ref, m)
                self._graphql_server.add_mutation_property(name, resolver)
            for s in subscription:
                name, resolver = self._create_graphql_query_handler(module_ref, s)
                self._graphql_server.add_subscription_property(name, resolver)

            for fr in field_resolver:
                resolver_class = await self.container.get(fr["class"])
                resolver = getattr(resolver_class, fr["handler_name"])
                self._graphql_server.create_type_field_resolver(fr, resolver)

        self._create_graphql_request_handler(graphql_module.config or GraphqlOption())

    def _create_graphql_query_handler(self, module_ref: Union[Type, object], meta: dict) -> tuple[str, Callable]:
        resolver: Union[object, Type] = meta['class']
        method_name: str = meta['handler_name']
        method = getattr(resolver, method_name)
        default_return_type = Reflect.get_metadata(method, NestipyGraphqlKey.return_type, None)

        async def graphql_handler(*_args, **kwargs):
            context_container = RequestContextContainer.get_instance()
            default_context = context_container.execution_context
            execution_context = ExecutionContext(
                self._adapter,
                module_ref,
                resolver,
                getattr(resolver, method_name),
                default_context.get_request(),
                default_context.get_response(),
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
                    raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)

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
        self._graphql_server.mutate_handler(method, graphql_handler, default_return_type)
        return method_name, graphql_handler,

    def _create_graphql_request_handler(self, option: GraphqlOption):
        graphql_path = f"/{option.url.strip('/')}"
        # create graphql handler but using handle of graphql_adapter
        self._adapter.mount(
            graphql_path,
            self._graphql_server.create_graphql_asgi_app(
                option=option,
                schema=self._graphql_server.create_schema(**(option.schema_option or {}))
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
