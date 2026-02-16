from __future__ import annotations

from typing import Callable, Type

from nestipy.core.router.router_proxy import RouterProxy
from nestipy.openapi.openapi_docs.v3 import PathItem, Schema, Reference
from nestipy.core.types import JsonValue, ModuleRef
from nestipy.common.cache import CachePolicy


class RouteRegistrar:
    """Register HTTP routes using RouterProxy with dynamic prefix/conflict settings."""

    def __init__(
        self,
        router_proxy: RouterProxy,
        prefix_getter: Callable[[], str | None],
        detect_conflicts_getter: Callable[[], bool],
    ) -> None:
        self._router_proxy = router_proxy
        self._prefix_getter = prefix_getter
        self._detect_conflicts_getter = detect_conflicts_getter

    def apply(
        self,
        modules: list[ModuleRef],
        *,
        build_openapi: bool,
        register_routes: bool,
    ) -> tuple[
        dict[str, PathItem],
        dict[str, Schema | Reference],
        list[dict[str, JsonValue | CachePolicy]],
    ]:
        prefix = self._prefix_getter() or ""
        return self._router_proxy.apply_routes(
            modules,
            prefix,
            build_openapi=build_openapi,
            register_routes=register_routes,
            detect_conflicts=self._detect_conflicts_getter(),
        )


__all__ = ["RouteRegistrar"]
