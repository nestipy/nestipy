from inspect import getmembers, isfunction
from typing import Union, Type

from nestipy.graphql.meta import NestipyGraphqlKey
from nestipy.metadata import ModuleMetadata, Reflect


class GraphqlExplorer:
    @classmethod
    def explore(
        cls, module_ref: Union[Type, object]
    ) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
        query: list[dict] = []
        mutation: list[dict] = []
        subscription: list[dict] = []
        field_resolver: list[dict] = []
        providers = Reflect.get_metadata(module_ref, ModuleMetadata.Providers, [])
        for provider in providers:
            if not Reflect.get_metadata(provider, NestipyGraphqlKey.resolver, False):
                continue
            cls._explore_resolver(
                provider, query, mutation, subscription, field_resolver
            )

        return query, mutation, subscription, field_resolver

    @classmethod
    def _explore_resolver(
        cls,
        resolver: Type,
        query: list,
        mutation: list,
        subscription: list,
        field_resolver: list[dict],
    ):
        class_to_resolve = Reflect.get_metadata(
            resolver, NestipyGraphqlKey.return_type, None
        )
        members = getmembers(resolver, isfunction)
        for method_name, _ in members:
            if method_name.startswith("__"):
                continue
            method = getattr(resolver, method_name)
            graphql_handler = Reflect.get_metadata(
                method, NestipyGraphqlKey.handler, None
            )
            if graphql_handler is not None:
                return_type = Reflect.get_metadata(
                    method, NestipyGraphqlKey.return_type, None
                )
                data: dict = {
                    "return_type": return_type,
                    "class": resolver,
                    "handler_name": method_name,
                }
                match graphql_handler:
                    case NestipyGraphqlKey.query:
                        query.append(data)
                    case NestipyGraphqlKey.mutation:
                        mutation.append(data)
                    case NestipyGraphqlKey.subscription:
                        subscription.append(data)
                    case NestipyGraphqlKey.field_resolver:
                        if class_to_resolve is not None:
                            kwargs: dict = Reflect.get_metadata(
                                method, NestipyGraphqlKey.kwargs, {}
                            )
                            name: str = method_name
                            if "name" in kwargs and kwargs.get("name"):
                                name = kwargs.get("name")
                            data["name"] = name
                            data["type"] = class_to_resolve
                            field_resolver.append(data)
