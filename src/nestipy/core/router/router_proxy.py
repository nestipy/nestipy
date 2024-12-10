import dataclasses
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
from nestipy.common.logger import logger
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext
from ...openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse


class RouterProxy:
    def __init__(
            self,
            router: HttpAdapter,
    ):
        self.router = router
        self._template_processor = TemplateRendererProcessor(router)

    def apply_routes(self, modules: list[Union[Type, object]], prefix: str = ""):
        _prefix: Union[str | None] = (
            f"/{prefix.strip('/')}"
            if prefix is not None and prefix.strip() != ""
            else None
        )
        json_paths = {}
        json_schemas = {}
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            for route in routes:
                path = (
                    f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip("/")
                    if _prefix
                    else route["path"]
                )
                methods = route["request_method"]
                method_name = route["method_name"]
                controller = route["controller"]
                handler = self.create_request_handler(
                    module_ref, controller, method_name
                )
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if path in json_paths:
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route["openapi"].keys():
                        route["openapi"]["responses"] = {200: ApiResponse()}
                    json_schemas = {**json_schemas, **route["schemas"]}
                    if "no_swagger" not in route["openapi"].keys():
                        route_path[method.lower()] = Operation(
                            **route["openapi"],
                            summary=snakecase_to_camelcase(method_name),
                        )
                        json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas

    def create_request_handler(
            self, module_ref: Type, controller: Union[object, Type], method_name: str
    ) -> CallableHandler:
        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):
            context_container = RequestContextContainer.get_instance()
            container = NestipyContainer.get_instance()
            controller_method_handler = getattr(controller, method_name)
            execution_context = ExecutionContext(
                self.router, module_ref, controller, controller_method_handler, req, res
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_execution_context(execution_context)
            handler_response: Response
            try:

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await container.get(controller, method_name)

                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        raise ex
                    g_processor: GuardProcessor = (
                        await NestipyContainer.get_instance().get(GuardProcessor)
                    )
                    passed = await g_processor.process(execution_context)
                    if not passed[0]:
                        raise HttpException(
                            HttpStatus.UNAUTHORIZED,
                            HttpStatusMessages.UNAUTHORIZED,
                            details=f"Not authorized from guard {passed[1]}",
                        )

                    interceptor: RequestInterceptor = await container.get(
                        RequestInterceptor
                    )
                    resp = await interceptor.intercept(
                        execution_context, next_fn_interceptor
                    )
                    #  execute Interceptor by using middleware execution as next_handler
                    if resp is None:
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
                if self._template_processor.can_process(
                        controller_method_handler, result
                ):
                    result = await res.html(self._template_processor.render())
                # transform result to response
                handler_response = await self._ensure_response(res, result)

            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, HttpException):
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))
                track = self.get_full_traceback_details(req, e.message, os.getcwd())
                e.track_back = track
                # Call exception catch
                exception_handler: ExceptionFilterHandler = await container.get(
                    ExceptionFilterHandler
                )
                result = await exception_handler.catch(e, execution_context)
                if result:
                    handler_response = await self._ensure_response(res, result)
                else:
                    handler_response = await self._ensure_response(
                        res, await next_fn(e)
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
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.model_dump(mode="json"))
        elif isinstance(result, Response):
            return result
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

    async def render_not_found(
            self, _req: "Request", _res: "Response", _next_fn: "NextFn"
    ) -> Response:
        try:
            raise HttpException(
                HttpStatus.NOT_FOUND,
                HttpStatusMessages.NOT_FOUND,
                "Sorry, but the page you are looking for has not been found or temporarily unavailable.",
            )
        except Exception as ex:
            track_b = self.get_full_traceback_details(
                _req,
                f"{HttpStatus.NOT_FOUND} - {HttpStatusMessages.NOT_FOUND}",
                os.getcwd(),
            )

            ex.track_back = track_b
            _res.status(404)
            execution_context = ExecutionContext(
                self.router, self, self, self.render_not_found, _req, _res
            )
            exception_handler = await NestipyContainer.get_instance().get(
                ExceptionFilterHandler
            )
            result = await exception_handler.catch(ex, execution_context)
            if result:
                handler_response = await self._ensure_response(_res, result)
            else:
                handler_response = await self._ensure_response(_res, await _next_fn(ex))
            return handler_response

    @classmethod
    def get_full_traceback_details(
            cls, req: Request, exception: typing.Any, file_path: str
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
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__,
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.path),
            message=getattr(exc_value, "details", None) or str(exc_value),
        )
