from inspect import getmembers, isfunction
from typing import Union, Type

from nestipy.metadata import ModuleMetadata, Reflect
from nestipy.graphql.meta import NestipyGraphqlKey


class GraphqlExplorer:

    @classmethod
    def explore(cls, module_ref: Union[Type, object]) -> type[list[dict], list[dict], list[dict]]:
        query = []
        mutation = []
        subscription = []
        providers = Reflect.get_metadata(module_ref, ModuleMetadata.Providers, [])
        for provider in providers:
            if not Reflect.get_metadata(provider, NestipyGraphqlKey.resolver, False):
                continue
            cls._explore_resolver(provider, query, mutation, subscription)

        return query, mutation, subscription

    @classmethod
    def _explore_resolver(cls, resolver: Type, query: list,
                          mutation: list,
                          subscription: list):
        members = getmembers(resolver, isfunction)
        for method_name, _ in members:
            if method_name.startswith("__"):
                continue
            method = getattr(resolver, method_name)
            graphql_handler = Reflect.get_metadata(method, NestipyGraphqlKey.handler, None)
            if graphql_handler is not None:
                return_type = Reflect.get_metadata(method, NestipyGraphqlKey.return_type, None)
                data: dict = {
                    'return_type': return_type,
                    'class': resolver,
                    'handler_name': method_name
                }
                match graphql_handler:
                    case NestipyGraphqlKey.query:
                        query.append(data)
                    case NestipyGraphqlKey.mutation:
                        mutation.append(data)
                    case NestipyGraphqlKey.subscription:
                        subscription.append(data)
