import traceback
from typing import Type, Union

from openapidocs.v3 import Operation, PathItem

from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.http_ import Request, Response
from nestipy.common.metadata.container import NestipyContainerKey
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_server import HttpServer
from ..context.execution_context import ExecutionContext
from ..ioc.nestipy_container import NestipyContainer
from ..ioc.nestipy_context_container import NestipyContextContainer
from ...common.exception.http import HttpException
from ...common.exception.status import HttpStatus
from ...common.guards.exector import GuardProcessor
from ...common.middleware.executor import MiddlewareExecutor


class RouterProxy:
    def __init__(self, router: HttpServer):
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
                handler = self.create_request_handler(controller, method_name)
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

    @classmethod
    def create_request_handler(cls, controller: Union[object, Type], method_name: str) -> CallableHandler:

        async def request_handler(req: Request, res: Response, next_fn: NextFn):

            context_container = NestipyContextContainer.get_instance()
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_value(NestipyContainerKey.request, req)
            context_container.set_value(NestipyContainerKey.response, res)
            context_container.set_value(NestipyContainerKey.params, req.path_params)
            context_container.set_value(NestipyContainerKey.query_params, req.query_params)
            context_container.set_value(NestipyContainerKey.headers, req.headers)

            try:

                # create next_function that call handler
                async def next_fn_res():
                    return await NestipyContainer.get_instance().get(controller, method_name)

                # create execution context
                execution_context = ExecutionContext(controller, getattr(controller, method_name), req, res)
                # Execute Guard
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # pass execution to next
                    return await next_fn(HttpException(
                        HttpStatus.UNAUTHORIZED,
                        HttpStatusMessages.UNAUTHORIZED,
                        details=f"Not authorized from guard {can_activate[1]}"
                    ))
                #  execute middleware
                result = await MiddlewareExecutor(req, res, next_fn_res).execute()
                # transform result to response
                response = await cls._create_response(res, result)
                # result = await getattr(controller, method_name)(req, res, next)
                # apply after middleware
                # Reset container Request

                return response
            except HttpException as e:
                # Call exception handler
                return await cls._create_response(res, await next_fn(e))
            except Exception as e:
                tb = traceback.format_exc()
                # Call exception handler
                return await cls._create_response(res,
                                                  await next_fn(
                                                      HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))))
            finally:
                context_container.destroy()

        return request_handler

    @classmethod
    async def _create_response(cls, res: Response, result: Union[Response, str, dict, list]) -> Response:
        if isinstance(result, str):
            return await res.send(content=result, status_code=200)
        elif isinstance(result, list) or isinstance(result, dict):
            return await res.json(content=result, status_code=200)
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(content={'error': 'Unknown response format'}, status_code=403)
