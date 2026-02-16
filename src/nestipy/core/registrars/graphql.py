from __future__ import annotations

from typing import Any, Type, Union

from nestipy.graphql.graphql_proxy import GraphqlProxy


class GraphqlRegistrar:
    """Apply GraphQL resolvers through the configured adapter."""

    def __init__(self, http_adapter: Any, graphql_adapter: Any) -> None:
        self._http_adapter = http_adapter
        self._graphql_adapter = graphql_adapter

    async def apply(self, graphql_module_instance: object, modules: list[Type]) -> None:
        await GraphqlProxy(self._http_adapter, self._graphql_adapter).apply_resolvers(
            graphql_module_instance,
            modules,
        )


__all__ = ["GraphqlRegistrar"]
