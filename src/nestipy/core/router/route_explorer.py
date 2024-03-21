from inspect import isfunction, getmembers
from typing import List, Type, Union

from openapidocs.v3 import Parameter, ParameterLocation

from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect
from nestipy.common.metadata.route import RouteKey
from nestipy.common.utils import deep_merge
from nestipy.openapi.scanner import OpenApiScanner
from .route_extractor import RouteParamsExtractor
from ..ioc.middleware_container import MiddlewareContainer


class RouteExplorer:
    _middleware_container: MiddlewareContainer
    _openapi_scanner = OpenApiScanner()

    def __init__(self, middleware_container: MiddlewareContainer = None):
        self.middleware_container = middleware_container

    @classmethod
    def _normalize_path(cls, path: str) -> str:
        return path.strip('/')

    @classmethod
    def explore(cls, module_ref: Union[Type, object]):
        controllers = Reflect.get_metadata(module_ref, ModuleMetadata.Controllers, [])
        routes = []
        for controller in controllers:
            controller_routes = cls.explore_controller(controller)
            routes = routes + controller_routes
        return routes

    @classmethod
    def explore_controller(cls, controller: Type) -> List[dict]:

        docs = cls._openapi_scanner.scan(controller)
        routes = []
        # need to extract middleware, guards, exception_handler,
        controller_path = cls._normalize_path(Reflect.get_metadata(controller, RouteKey.path, ''))
        for method_name, _ in getmembers(controller, isfunction):
            if method_name.startswith("__"):
                continue
            method = getattr(controller, method_name)
            path = Reflect.get_metadata(method, RouteKey.path, None)
            if path is not None:
                method_path = cls._normalize_path(path)
                path = f"/{cls._normalize_path(f'{controller_path}/{method_path}')}"
                request_method = Reflect.get_metadata(method, RouteKey.method)

                # openapi docs
                params = RouteParamsExtractor.extract_params(path)
                parameters = [Parameter(name=name, in_=ParameterLocation.PATH, required=True, description='Route path',
                                        allow_empty_value=False)
                              for name in params.keys()]
                method_docs = deep_merge(cls._openapi_scanner.scan(method), {'parameters': parameters})
                path_docs = deep_merge(
                    {'tags': [controller.__name__.replace('Controller', '')]},
                    deep_merge(docs, method_docs)
                )
                path_docs['tags'] = [path_docs['tags'][0]]

                # en open api

                route_info = {
                    'path': path,
                    'request_method': request_method,
                    'method_name': method_name,
                    'controller': controller,
                    'openapi': path_docs  # openapi docs
                }
                routes.append(route_info)
        return routes
