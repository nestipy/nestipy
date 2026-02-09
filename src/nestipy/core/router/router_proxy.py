import dataclasses
import inspect
import os
import sys
import traceback
import typing
from typing import Type, Union

from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.http import ExceptionDetail, RequestTrack, Traceback
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.pipes.processor import PipeProcessor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer, NestipyIContainer
from nestipy.ioc import RequestContextContainer
from nestipy.openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..context.execution_context import ExecutionContext

if typing.TYPE_CHECKING:
    from ..adapter.http_adapter import HttpAdapter


def omit(d: dict, keys: set):
    return {k: v for k, v in d.items() if k not in keys}


class RouterProxy:
    """
    Proxy class that handles the registration of routes from modules and controllers.
    It acts as a bridge between Nestipy modules and the underlying HTTP adapter.
    """

    def __init__(
        self,
        router: "HttpAdapter",
        container: typing.Optional[NestipyIContainer] = None,
    ):
        """
        Initialize the RouterProxy.
        :param router: The HTTP adapter (e.g., FastApiAdapter, BlackSheepAdapter).
        :param container: The IoC container instance.
        """
        self.router = router
        self.container = container or NestipyContainer.get_instance()

    def apply_routes(
        self,
        modules: list[Union[Type, object]],
        prefix: str = "",
        build_openapi: bool = True,
        register_routes: bool = True,
    ):
        """
        Explore the provided modules for controllers and register their routes with the HTTP adapter.
        :param modules: List of modules to explore.
        :param prefix: Global path prefix for all routes.
        :return: A tuple containing (OpenAPI paths, OpenAPI schemas, List of registered routes).
        """
        _prefix: Union[str | None] = (
            f"/{prefix.strip('/')}"
            if prefix is not None and prefix.strip() != ""
            else None
        )
        json_paths = {}
        json_schemas = {}
        list_routes = []
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref, include_openapi=build_openapi)
            list_routes = [
                *list_routes,
                *[omit(u, {"controller", "openapi", "schemas"}) for u in routes],
            ]
            for route in routes:
                path = (
                    f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip("/")
                    if _prefix
                    else route["path"]
                )
                methods = route["request_method"]
                method_name = route["method_name"]
                controller = route["controller"]
                handler = None
                if register_routes:
                    handler = self.create_request_handler(
                        self.router,
                        typing.cast(Type, module_ref),
                        controller,
                        method_name,
                        container=self.container,
                    )
                for method in methods:
                    if register_routes and handler is not None:
                        getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if build_openapi:
                        if path in json_paths:
                            route_path = json_paths[path]
                        else:
                            route_path = {}
                        if "responses" not in route["openapi"].keys():
                            route["openapi"]["responses"] = {200: ApiResponse()}
                        json_schemas = {**json_schemas, **route["schemas"]}
                        if "hidden" not in route["openapi"].keys():
                            openapi_payload = dict(route["openapi"])
                            openapi_payload.setdefault(
                                "summary", snakecase_to_camelcase(method_name)
                            )
                            route_path[method.lower()] = Operation(**openapi_payload)
                            json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas, list_routes

    @classmethod
    def create_request_handler(
        cls,
        http_adapter: "HttpAdapter",
        module_ref: typing.Optional[Type] = None,
        controller: typing.Optional[Union[object, Type]] = None,
        method_name: typing.Optional[str] = None,
        custom_callback: typing.Optional[
            typing.Callable[["Request", "Response", NextFn], typing.Any]
        ] = None,
        container: typing.Optional[NestipyIContainer] = None,
    ) -> CallableHandler:
        controller_method_handler = custom_callback or getattr(
            controller, typing.cast(str, method_name)
        )
        _template_processor = TemplateRendererProcessor(http_adapter)
        context_container = RequestContextContainer.get_instance()
        container = container or NestipyContainer.get_instance()

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):
            interceptor_called = False
            execution_context = ExecutionContext(
                http_adapter,
                custom_callback or module_ref,
                custom_callback or controller,
                controller_method_handler,
                req,
                res,
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.reset_request_cache()
            context_container.set_execution_context(execution_context)
            await container.preload_request_scoped_properties()
            handler_response: Response
            try:

                async def next_fn_interceptor(ex: typing.Any = None):
                    nonlocal interceptor_called
                    interceptor_called = True
                    if ex is not None:
                        return await cls._ensure_response(res, await next_fn(ex))
                    if custom_callback:
                        callback_res = custom_callback(req, res, next_fn)
                        if inspect.isawaitable(callback_res):
                            return await callback_res
                        else:
                            return callback_res
                    return await container.get(
                        typing.cast(typing.Union[typing.Type, str], controller),
                        typing.cast(str, method_name),
                    )

                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        raise ex
                    g_processor: GuardProcessor = typing.cast(
                        GuardProcessor, await container.get(GuardProcessor)
                    )
                    passed = await g_processor.process(execution_context)
                    if not passed[0]:
                        raise HttpException(
                            HttpStatus.UNAUTHORIZED,
                            HttpStatusMessages.UNAUTHORIZED,
                            details=f"Not authorized from guard {passed[1]}",
                        )

                    pipe_processor: PipeProcessor = typing.cast(
                        PipeProcessor, await container.get(PipeProcessor)
                    )
                    pipes = await pipe_processor.get_pipes(execution_context)
                    execution_context.set_pipes(pipes)

                    interceptor: RequestInterceptor = typing.cast(
                        RequestInterceptor, await container.get(RequestInterceptor)
                    )
                    resp = await interceptor.intercept(
                        execution_context, next_fn_interceptor
                    )
                    #  execute Interceptor by using middleware execution as next_handler
                    if not interceptor_called:
                        raise HttpException(
                            HttpStatus.BAD_REQUEST,
                            "Handler not called because of interceptor: Invalid Request",
                        )
                    return resp

                # Call middleware before all
                result = await MiddlewareExecutor(
                    req, res, next_fn_middleware
                ).execute()

                # process template rendering

                if _template_processor.can_process(controller_method_handler, result):
                    result = await res.html(_template_processor.render() or "")
                # transform result to response
                handler_response = await cls._ensure_response(res, result)

            except Exception as e:
                handler_response = await cls.handle_exception(
                    e, execution_context, next_fn, container=container
                )
            finally:
                #  reset request context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(
        cls, res: "Response", result: Union["Response", str, dict, list]
    ) -> "Response":
        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result))
        elif isinstance(result, (list, dict)):
            return await res.json(content=result)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(typing.Any, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.model_dump(mode="json"))
        elif isinstance(result, Response):
            return result
        elif result is None:
            return await res.status(204).send("")
        else:
            return await res.json(
                content={"error": "Unknown response format"}, status_code=403
            )

    @classmethod
    def get_center_elements(cls, lst: list, p: int, m: int):
        n = len(lst)
        size = (m * 2) + 1
        if n < size:
            return lst, 1
        start = max(0, p - m - 1)
        end = min(n, p + m + 1)

        return lst[start:end], start + 1

    @classmethod
    def get_code_context(cls, filename, lineno, n):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
            elements, start_line = cls.get_center_elements(lines, lineno, n)
            return "".join(elements), start_line
        except Exception as e:
            return f"Could not read file {filename}: {str(e)}"

    @classmethod
    async def render_not_found(
        cls, _req: "Request", _res: "Response", _next_fn: "NextFn"
    ) -> Response:
        raise HttpException(
            HttpStatus.NOT_FOUND,
            HttpStatusMessages.NOT_FOUND,
            "Sorry, but the page you are looking for has not been found or temporarily unavailable.",
        )

    @classmethod
    async def handle_exception(
        cls,
        ex: Exception,
        execution_context: ExecutionContext,
        next_fn: NextFn,
        container: typing.Optional[NestipyIContainer] = None,
    ):
        tb = traceback.format_exc()
        if not isinstance(ex, HttpException):
            ex = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(ex), str(tb))
        track_b = cls.get_full_traceback_details(
            execution_context.get_request(),
            ex.message,
            os.getcwd(),
        )
        ex.track_back = track_b
        container = container or NestipyContainer.get_instance()
        exception_handler = typing.cast(
            ExceptionFilterHandler, await container.get(ExceptionFilterHandler)
        )
        result = await typing.cast(typing.Any, exception_handler).catch(
            ex, execution_context
        )
        response = typing.cast(Response, execution_context.get_response())
        if result:
            handler_response = await cls._ensure_response(response, result)
        else:
            handler_response = await cls._ensure_response(response, await next_fn(ex))
        return handler_response

    @classmethod
    def get_full_traceback_details(
        cls, req: typing.Optional[Request], exception: typing.Any, file_path: str
    ):
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback_details = []

        # Extracting traceback details
        tb = exc_tb
        while tb is not None:
            filename: str = tb.tb_frame.f_code.co_filename
            code, start = cls.get_code_context(
                tb.tb_frame.f_code.co_filename, tb.tb_lineno, 9
            )
            frame_info = Traceback(
                filename=f"{filename.replace(file_path, '').strip('/')}",
                lineno=tb.tb_lineno,
                name=tb.tb_frame.f_code.co_name,
                code=code,
                start_line_number=start,
                is_package=not filename.startswith(file_path),
            )
            traceback_details.append(frame_info)
            tb = tb.tb_next
        traceback_details.reverse()
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__ if exc_type else "Unknown",
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.path)
            if req
            else RequestTrack(method="GET", host="localhost"),
            message=getattr(exc_value, "details", None) or str(exc_value),
        )
