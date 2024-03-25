import dataclasses
import traceback
import typing
from typing import Type, Union

from openapidocs.v3 import Operation, PathItem
from pydantic import BaseModel

from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.http_ import Request, Response
from nestipy.common.metadata.container import NestipyContainerKey
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext
from ..ioc.nestipy_container import NestipyContainer
from ..ioc.nestipy_context_container import NestipyContextContainer
from ...common.exception.filter import ExceptionFilterHandler
from ...common.exception.http import HttpException
from ...common.exception.status import HttpStatus
from ...common.guards.processor import GuardProcessor
from ...common.interceptor import RequestInterceptor
from ...common.middleware.executor import MiddlewareExecutor
from ...common.template import TemplateRendererProcessor


class RouterProxy:
    def __init__(self, router: HttpAdapter):
        self.router = router

    def apply_routes(self, modules: set[Union[Type, object]]):
        json_paths = {}
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            for route in routes:
                path = route['path']
                methods = route['request_method']
                method_name = route['method_name']
                controller = route['controller']
                handler = self.create_request_handler(module_ref, controller, method_name)
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)

                    # OPEN API REGISTER
                    if path in json_paths.keys():
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route['openapi'].keys():
                        continue
                    route_path[method.lower()] = Operation(
                        **route['openapi'],
                        summary=snakecase_to_camelcase(method_name)
                    )
                    json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths

    def create_request_handler(
            self,
            module_ref: Type,
            controller: Union[object, Type],
            method_name: str
    ) -> CallableHandler:
        template_processor = TemplateRendererProcessor(self.router)

        async def request_handler(req: Request, res: Response, next_fn: NextFn):

            context_container = NestipyContextContainer.get_instance()
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_value(NestipyContainerKey.request, req)
            context_container.set_value(NestipyContainerKey.response, res)
            context_container.set_value(NestipyContainerKey.params, req.path_params)
            context_container.set_value(NestipyContainerKey.query_params, req.query_params)
            context_container.set_value(NestipyContainerKey.headers, req.headers)

            container = NestipyContainer.get_instance()
            controller_method = getattr(controller, method_name)
            execution_context = ExecutionContext(self.router, module_ref, controller, controller_method, req, res)

            try:
                # TODO : Refactor
                # create execution context
                # Execute Guard
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # Raise error
                    raise HttpException(
                        HttpStatus.UNAUTHORIZED,
                        HttpStatusMessages.UNAUTHORIZED,
                        details=f"Not authorized from guard {can_activate[1]}"
                    )

                # create next_function that call catch
                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await container.get(controller, method_name)

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await MiddlewareExecutor(req, res, next_fn_middleware).execute()

                #  execute Interceptor by using middleware execution as next_handler
                interceptor: RequestInterceptor = await container.get(RequestInterceptor)
                result = await interceptor.intercept(execution_context, next_fn_interceptor)
                if result is None:
                    raise HttpException(
                        HttpStatus.BAD_REQUEST,
                        "Handler not called: Invalid Request"
                    )

                # process template rendering
                if template_processor.can_process(controller_method, result):
                    result = await res.html(template_processor.render())
                # transform result to response
                response = await self._ensure_response(res, result)

                return response
            except Exception as e:
                if not isinstance(e, HttpException):
                    tb = traceback.format_exc()
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))

                # Call exception catch
                exception_handler = await container.get(ExceptionFilterHandler)
                result = await exception_handler.catch(e, execution_context)
                if result:
                    return await self._ensure_response(res, result)
                return await self._ensure_response(res, await next_fn(e))
            finally:
                #  reset context container
                context_container.destroy()

        return request_handler

    @classmethod
    async def _ensure_response(cls, res: Response, result: Union[Response, str, dict, list]) -> Response:

        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result), status_code=200)
        elif isinstance(result, (list, dict)):
            return await res.json(content=result, status_code=200)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
                status_code=200
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.dict(), status_code=200)
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(content={'error': 'Unknown response format'}, status_code=403)
