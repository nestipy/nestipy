from __future__ import annotations

from nestipy.graphql.graphql_proxy import GraphqlProxy
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.core.types import ModuleRef
from nestipy.graphql.graphql_module import GraphqlModule


class GraphqlRegistrar:
    """Apply GraphQL resolvers through the configured adapter."""

    def __init__(self, http_adapter: HttpAdapter, graphql_adapter: GraphqlAdapter) -> None:
        self._http_adapter = http_adapter
        self._graphql_adapter = graphql_adapter

    async def apply(self, graphql_module_instance: GraphqlModule, modules: list[ModuleRef]) -> None:
        await GraphqlProxy(self._http_adapter, self._graphql_adapter).apply_resolvers(
            graphql_module_instance,
            modules,
        )


__all__ = ["GraphqlRegistrar"]
