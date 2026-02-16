from inspect import isfunction, getmembers
from typing import List

from nestipy.openapi.openapi_docs.v3 import Parameter, ParameterLocation

from nestipy.common.utils import deep_merge
from nestipy.core.types import ModuleRef
from nestipy.ioc import MiddlewareContainer
from nestipy.metadata import ModuleMetadata, Reflect, RouteKey
from nestipy.openapi.explorer import OpenApiExplorer
from .route_extractor import RouteParamsExtractor


class RouteExplorer:
    """
    Utility class for exploring modules and controllers to find route definitions.
    """

    _middleware_container: MiddlewareContainer
    _openapi_scanner = OpenApiExplorer()
    _version_prefix: str = "v"

    @classmethod
    def _normalize_path(cls, path: str) -> str:
        """
        Normalize a URI path by stripping leading and trailing slashes.
        :param path: The path to normalize.
        :return: Normalized path.
        """
        return path.strip("/")

    @classmethod
    def _normalize_versions(cls, value):
        if value is None:
            return None
        if isinstance(value, (list, tuple, set)):
            versions = [str(v) for v in value if str(v)]
            return versions or None
        return [str(value)] if str(value) else None

    @classmethod
    def _format_version(cls, version: str) -> str:
        version = version.strip("/")
        prefix = cls._version_prefix.strip("/")
        if not prefix:
            return version
        if version.startswith(prefix):
            return version
        return f"{prefix}{version}"

    @classmethod
    def set_version_prefix(cls, prefix: str) -> None:
        cls._version_prefix = prefix or ""

    @classmethod
    def explore(cls, module_ref: ModuleRef, include_openapi: bool = True):
        """
        Explore a module for controllers and their routes.
        :param module_ref: The module class or instance to explore.
        :return: A list of dictionaries, each containing route information.
        """
        controllers = Reflect.get_metadata(module_ref, ModuleMetadata.Controllers, [])
        routes = []
        ins = cls()
        for controller in controllers:
            controller_routes = ins.explore_controller(
                controller, include_openapi=include_openapi
            )
            routes = routes + controller_routes
        return routes

    def explore_controller(self, controller: type, include_openapi: bool = True) -> List[dict]:
        """
        Explore a controller class for route methods decorated with @Route, @Get, etc.
        :param controller: The controller class to explore.
        :return: A list of route definitions.
        """
        if include_openapi:
            docs, schemas = self._openapi_scanner.explore(controller)
        else:
            docs, schemas = {}, {}
        routes = []
        # need to extract middleware, guards, exception_handler,
        controller_path = self._normalize_path(
            Reflect.get_metadata(controller, RouteKey.path, "")
        )
        controller_versions = self._normalize_versions(
            Reflect.get_metadata(controller, RouteKey.version, None)
        )
        controller_cache = Reflect.get_metadata(controller, RouteKey.cache, None)
        for method_name, _ in getmembers(controller, isfunction):
            if method_name.startswith("__"):
                continue
            method = getattr(controller, method_name)
            path = Reflect.get_metadata(method, RouteKey.path, None)
            if path is not None:
                method_path = self._normalize_path(path)
                base_path = f"{controller_path}/{method_path}".strip("/")
                request_method = Reflect.get_metadata(method, RouteKey.method)
                method_versions = self._normalize_versions(
                    Reflect.get_metadata(method, RouteKey.version, None)
                )
                versions = method_versions if method_versions is not None else controller_versions
                cache_policy = Reflect.get_metadata(method, RouteKey.cache, None)
                if cache_policy is None:
                    cache_policy = controller_cache

                if not versions:
                    versions = [None]
                for version in versions:
                    if version:
                        version_segment = self._format_version(str(version))
                        full_path = f"/{self._normalize_path(f'{version_segment}/{base_path}')}"
                    else:
                        full_path = f"/{self._normalize_path(base_path)}"

                # openapi docs
                    if include_openapi:
                        params = RouteParamsExtractor.extract_params(full_path)
                        parameters = [
                            Parameter(
                                name=name,
                                in_=ParameterLocation.PATH,
                                required=True,
                                description="Route path",
                                allow_empty_value=False,
                            )
                            for name in params.keys()
                        ]
                        method_deps, method_schemas = self._openapi_scanner.explore(
                            method
                        )
                        method_docs = deep_merge(method_deps, {"parameters": parameters})
                        merged_docs = deep_merge(docs, method_docs)
                        merged_schemas = deep_merge(schemas, method_schemas)
                        path_docs = deep_merge(
                            {"tags": [controller.__name__.replace("Controller", "")]},
                            merged_docs,
                        )
                        path_docs["tags"] = [path_docs["tags"][0]]
                    else:
                        merged_schemas = {}
                        path_docs = {}

                    # end open api

                    route_info = {
                        "path": full_path,
                        "request_method": request_method,
                        "method_name": method_name,
                        "controller": controller,
                        "controller_name": controller.__name__,
                        "openapi": path_docs,  # openapi docs
                        "schemas": merged_schemas,
                        "version": version,
                        "cache": cache_policy,
                    }
                    routes.append(route_info)
        return routes
