import dataclasses
import traceback
import typing
from typing import Type, Union

from nestipy_ioc import NestipyContainer
from nestipy_ioc import NestipyContextContainer
from nestipy_metadata import NestipyContextProperty
from openapidocs.v3 import Operation, PathItem
from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext


class RouterProxy:
    def __init__(self, router: HttpAdapter):
        self.router = router
        self._template_processor = TemplateRendererProcessor(router)

    def apply_routes(self, modules: list[Union[Type, object]]):
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

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):

            context_container = NestipyContextContainer.get_instance()
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_value(NestipyContextProperty.request, req)
            context_container.set_value(NestipyContextProperty.response, res)
            context_container.set_value(NestipyContextProperty.params, req.path_params)
            context_container.set_value(NestipyContextProperty.query_params, req.query_params)
            context_container.set_value(NestipyContextProperty.headers, req.headers)
            form_data = await req.form()
            if form_data is not None:
                context_container.set_value(NestipyContextProperty.body, form_data)
            else:
                json_data = await req.json()
                context_container.set_value(NestipyContextProperty.body, json_data)

            # TODO: req.files

            container = NestipyContainer.get_instance()
            controller_method_handler = getattr(controller, method_name)
            execution_context = ExecutionContext(self.router, module_ref, controller, controller_method_handler, req,
                                                 res)
            context_container.set_value(NestipyContextProperty.execution_context, execution_context)
            handler_response: Response
            try:
                # TODO : Refactor
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
                        "Handler not called because of interceptor: Invalid Request"
                    )

                # process template rendering
                if self._template_processor.can_process(controller_method_handler, result):
                    result = await res.html(self._template_processor.render())
                # transform result to response
                handler_response = await self._ensure_response(res, result)

            except Exception as e:
                if not isinstance(e, HttpException):
                    tb = traceback.format_exc()
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))

                # Call exception catch
                exception_handler = await container.get(ExceptionFilterHandler)
                result = await exception_handler.catch(e, execution_context)
                if result:
                    handler_response = await self._ensure_response(res, result)
                else:
                    handler_response = await self._ensure_response(res, await next_fn(e))
            finally:
                #  reset context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(cls, res: "Response", result: Union["Response", str, dict, list]) -> "Response":

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
