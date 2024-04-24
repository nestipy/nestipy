from inspect import isfunction, getmembers
from typing import List, Type, Union

from nestipy_ioc import MiddlewareContainer
from nestipy_metadata import ModuleMetadata, Reflect, RouteKey
from openapidocs.v3 import Parameter, ParameterLocation

from nestipy.common.utils import deep_merge
from nestipy.openapi.explorer import OpenApiExplorer
from .route_extractor import RouteParamsExtractor


class RouteExplorer:
    _middleware_container: MiddlewareContainer
    _openapi_scanner = OpenApiExplorer()

    @classmethod
    def _normalize_path(cls, path: str) -> str:
        return path.strip('/')

    @classmethod
    def explore(cls, module_ref: Union[Type, object]):
        controllers = Reflect.get_metadata(module_ref, ModuleMetadata.Controllers, [])
        routes = []
        ins = cls()
        for controller in controllers:
            controller_routes = ins.explore_controller(controller)
            routes = routes + controller_routes
        return routes

    def explore_controller(self, controller: Type) -> List[dict]:

        docs = self._openapi_scanner.explore(controller)
        routes = []
        # need to extract middleware, guards, exception_handler,
        controller_path = self._normalize_path(Reflect.get_metadata(controller, RouteKey.path, ''))
        for method_name, _ in getmembers(controller, isfunction):
            if method_name.startswith("__"):
                continue
            method = getattr(controller, method_name)
            path = Reflect.get_metadata(method, RouteKey.path, None)
            if path is not None:
                method_path = self._normalize_path(path)
                path = f"/{self._normalize_path(f'{controller_path}/{method_path}')}"
                request_method = Reflect.get_metadata(method, RouteKey.method)

                # openapi docs
                params = RouteParamsExtractor.extract_params(path)
                parameters = [Parameter(name=name, in_=ParameterLocation.PATH, required=True, description='Route path',
                                        allow_empty_value=False)
                              for name in params.keys()]
                method_docs = deep_merge(self._openapi_scanner.explore(method), {'parameters': parameters})
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
