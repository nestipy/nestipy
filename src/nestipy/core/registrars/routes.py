from __future__ import annotations

from typing import Any, Callable, Type, Union


class RouteRegistrar:
    """Register HTTP routes using RouterProxy with dynamic prefix/conflict settings."""

    def __init__(
        self,
        router_proxy: Any,
        prefix_getter: Callable[[], str | None],
        detect_conflicts_getter: Callable[[], bool],
    ) -> None:
        self._router_proxy = router_proxy
        self._prefix_getter = prefix_getter
        self._detect_conflicts_getter = detect_conflicts_getter

    def apply(
        self, modules: list[Type], *, build_openapi: bool, register_routes: bool
    ) -> tuple[Any, Any, list[dict[str, Any]]]:
        prefix = self._prefix_getter() or ""
        return self._router_proxy.apply_routes(
            modules,
            prefix,
            build_openapi=build_openapi,
            register_routes=register_routes,
            detect_conflicts=self._detect_conflicts_getter(),
        )


__all__ = ["RouteRegistrar"]
