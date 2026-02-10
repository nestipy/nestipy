import asyncio
import dataclasses
import inspect
import os.path
import traceback
from typing import Union, Type, Callable, Any

from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.pipes.processor import PipeProcessor
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.graphql.meta import NestipyGraphqlKey
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.ioc.helper import ContainerHelper
from nestipy.metadata import Reflect, CtxDepKey
from .graphql_explorer import GraphqlExplorer
from .graphql_module import GraphqlModule, GraphqlOption
from ..common import (
    Request,
    Response,
    HttpException,
    HttpStatus,
    HttpStatusMessages,
    Websocket,
)
from ..common.logger import logger
from ..core.adapter.http_adapter import HttpAdapter
from ..core.context.execution_context import ExecutionContext
from ..types_ import NextFn
from ..common.constant import DEVTOOLS_STATIC_PATH_KEY


class GraphqlProxy:
    """
    Proxy class that bridges Nestipy modules with a GraphQL server.
    It dynamically registers resolvers, applies guards, and sets up HTTP/WebSocket handlers.
    """

    def __init__(self, adapter: HttpAdapter, graphql_server: GraphqlAdapter):
        """
        :param adapter: The HTTP adapter instance to register handlers.
        :param graphql_server: The GraphQL adapter (e.g., Strawberry ASGI integration).
        """
        self._graphql_server = graphql_server
        self._adapter = adapter
        self.container = NestipyContainer.get_instance()

    async def apply_resolvers(
        self, graphql_module: GraphqlModule, modules: list[Union[Type, object]]
    ):
        self._graphql_server.reset()
        for module_ref in modules:
            query, mutation, subscription, field_resolver = GraphqlExplorer.explore(
                module_ref
            )
            for q in query:
                name, resolver = self._create_graphql_query_handler(module_ref, q)
                self._graphql_server.add_query_property(
                    name, resolver, q.get("field_options")
                )
            for m in mutation:
                name, resolver = self._create_graphql_query_handler(module_ref, m)
                self._graphql_server.add_mutation_property(
                    name, resolver, m.get("field_options")
                )
            for s in subscription:
                name, resolver = self._create_graphql_query_handler(module_ref, s)
                self._graphql_server.add_subscription_property(
                    name, resolver, s.get("field_options")
                )

            for fr in field_resolver:
                name, resolver = self._create_graphql_query_handler(
                    module_ref, fr, is_field=True
                )
                self._graphql_server.create_type_field_resolver(
                    fr, resolver, fr.get("field_options")
                )

        await self._create_graphql_request_handler(graphql_module.config or GraphqlOption())

    def _create_graphql_query_handler(
        self, module_ref: Union[Type, object], meta: dict, is_field: bool = False
    ) -> tuple[str, Callable]:
        resolver: Union[object, Type] = meta["class"]
        method_name: str = meta["handler_name"]
        method = getattr(resolver, method_name)
        default_return_type = Reflect.get_metadata(
            method, NestipyGraphqlKey.return_type, None
        )
        signature = inspect.signature(method)
        arg_token_map: dict[str, str] = {}
        for param_name, param in signature.parameters.items():
            if param_name in ("self", "cls") or param.annotation is inspect.Parameter.empty:
                continue
            _annotation, dep_key = ContainerHelper.get_type_from_annotation(
                param.annotation
            )
            if dep_key.metadata.key == CtxDepKey.Args:
                token = dep_key.metadata.token
                if isinstance(token, str) and token not in ("root", "info", "__all_args__"):
                    arg_token_map[token] = param_name

        async def graphql_handler(*_args, **kwargs):
            root = None
            info = None
            if _args:
                root = _args[0] if len(_args) >= 1 else None
                info = _args[1] if len(_args) >= 2 else None
            if "root" in kwargs:
                root = kwargs.get("root")
            if "info" in kwargs:
                info = kwargs.get("info")

            context_container = RequestContextContainer.get_instance()
            default_context = context_container.execution_context
            graphql_args = dict(kwargs)
            if root is not None:
                graphql_args.setdefault("root", root)
            if info is not None:
                graphql_args.setdefault("info", info)
            for token, param_name in arg_token_map.items():
                if token in kwargs:
                    graphql_args[param_name] = kwargs[token]
            graphql_context = None
            if info is not None and hasattr(info, "context"):
                graphql_context = info.context
            elif default_context is not None:
                graphql_context = default_context.switch_to_graphql().get_context()
            execution_context = ExecutionContext(
                self._adapter,
                module_ref,
                resolver,
                getattr(resolver, method_name),
                default_context.get_request(),
                default_context.get_response(),
                graphql_args,
                graphql_context,
            )
            context_container.set_execution_context(execution_context)
            await self.container.preload_request_scoped_properties()
            try:
                guard_processor: GuardProcessor = await self.container.get(
                    GuardProcessor
                )
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    raise HttpException(
                        HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED
                    )

                pipe_processor: PipeProcessor = await self.container.get(PipeProcessor)
                pipes = await pipe_processor.get_pipes(
                    execution_context, is_http=True
                )
                execution_context.set_pipes(pipes)

                async def next_fn():
                    return await self.container.get(resolver, method_name)

                interceptor: RequestInterceptor = await self.container.get(
                    RequestInterceptor
                )
                result = await interceptor.intercept(
                    execution_context, next_fn, is_http=True
                )
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, HttpException):
                    e = HttpException(
                        HttpStatus.INTERNAL_SERVER_ERROR,
                        str(e),
                        str(tb),
                    )
                exception_handler: ExceptionFilterHandler = await self.container.get(
                    ExceptionFilterHandler
                )
                filter_result = await exception_handler.catch(
                    e, execution_context, is_http=True
                )
                if isinstance(filter_result, Exception):
                    result = self._graphql_server.raise_exception(filter_result)
                elif filter_result is not None:
                    result = filter_result
                else:
                    result = self._graphql_server.raise_exception(e)
            if default_context is not None:
                context_container.set_execution_context(default_context)
            else:
                context_container.destroy()
            return result

        # mutate handle inside adapter
        self._graphql_server.modify_handler_signature(
            method, graphql_handler, default_return_type
        )
        return (
            meta.get("name", method_name),
            graphql_handler,
        )

    async def _create_graphql_request_handler(self, option: GraphqlOption):
        graphql_path = f"/{option.url.strip('/')}"
        schema_option: Any = option.schema_option or {}
        if dataclasses.is_dataclass(schema_option):
            schema_option = dataclasses.asdict(schema_option)
        schema_option = {
            key: value for key, value in schema_option.items() if value is not None
        }
        schema = option.schema
        if schema is None and option.schema_factory:
            schema = await NestipyContainer.get_instance().resolve_factory(
                option.schema_factory,
                inject=[],
                search_scope=[],
                disable_scope=True,
            )
        if schema is None:
            schema = self._graphql_server.create_schema(**schema_option)
        gql_asgi = self._graphql_server.create_graphql_asgi_app(
            option=option,
            schema=schema,
        )
        gql_asgi.set_devtools_static_path(
            self._adapter.get_state(DEVTOOLS_STATIC_PATH_KEY) or "/_devtools/static"
        )
        if option.auto_schema_file:
            schema_sdl = gql_asgi.print_schema()
            with open(os.path.join(os.getcwd(), option.auto_schema_file), "w+") as file:
                file.write(schema_sdl)

        # create graphql handler but using handle of graphql_adapter
        async def graphql_handler(_req: Request, res: Response, _next_fn: NextFn):
            context_container = RequestContextContainer.get_instance()
            previous_context = context_container.execution_context
            execution_context = ExecutionContext(
                self._adapter,
                None,
                None,
                graphql_handler,
                _req,
                res,
                None,
                None,
            )
            context_container.reset_request_cache()
            context_container.set_execution_context(execution_context)
            await self.container.preload_request_scoped_properties()
            scope = _req.scope
            queue: asyncio.Queue[bytes] = asyncio.Queue()
            completed = asyncio.Event()

            # Custom send method to handle ASGI messages
            async def send(message: dict):
                if message["type"] == "http.response.start":
                    headers = {
                        key.decode(): value.decode()
                        for key, value in message["headers"]
                    }
                    res.headers(headers)
                    res.status(message["status"] or 200)

                elif message["type"] == "http.response.body":
                    body = message.get("body", b"")
                    if body:
                        await queue.put(body)

                    if not message.get("more_body", False):
                        completed.set()

            async def stream_chunk_generator():
                while not completed.is_set() or not queue.empty():
                    chunk = await queue.get()
                    yield chunk

            try:
                await asyncio.get_running_loop().create_task(
                    gql_asgi.handle(scope, _req.receive, send)
                )
                # Return streaming response
                return await res.stream(stream_chunk_generator)
            finally:
                if previous_context is not None:
                    context_container.set_execution_context(previous_context)
                else:
                    context_container.destroy()

        async def graphql_ws_handler(_ws: Websocket):
            context_container = RequestContextContainer.get_instance()
            previous_context = context_container.execution_context
            execution_context = ExecutionContext(
                self._adapter,
                None,
                None,
                graphql_ws_handler,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )
            context_container.reset_request_cache()
            context_container.set_execution_context(execution_context)
            await self.container.preload_request_scoped_properties()
            scope = _ws.scope
            receive = _ws.receive
            send = _ws.send
            try:
                await gql_asgi.handle(scope, receive, send)
            finally:
                if previous_context is not None:
                    context_container.set_execution_context(previous_context)
                else:
                    context_container.destroy()

        self._adapter.all(graphql_path, graphql_handler, {})
        self._adapter.ws(graphql_path, graphql_ws_handler, {})

    @classmethod
    def should_render_graphql_ide(cls, req: Request) -> bool:
        return (
            req.method == "GET"
            and req.query_params.get("query") is None
            and any(
                [
                    supported_header in req.headers.get("accept", "")
                    for supported_header in ("text/html", "*/*")
                ]
            )
        )
