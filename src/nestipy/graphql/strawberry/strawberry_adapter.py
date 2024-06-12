import inspect
from typing import Callable, Type, Any

from strawberry import type as strawberry_type, field as strawberry_field, mutation, subscription, Schema

from ..graphql_adapter import GraphqlAdapter
from ..graphql_asgi import GraphqlAsgi
from ..graphql_module import GraphqlOption
from ..strawberry.strawberry_asgi import StrawberryAsgi


class StrawberryAdapter(GraphqlAdapter):
    def raise_exception(self, e: Exception):
        raise e

    _schema: Schema = None

    def create_query_field_resolver(self, resolver: Callable) -> object:
        return strawberry_field(resolver)

    def create_mutation_field_resolver(self, resolver: Callable) -> object:
        return mutation(resolver)

    def create_subscription_field_resolver(self, resolver: Callable) -> object:
        return subscription(resolver)

    def mutate_handler(self, original_handler: Any, mutated_handler: Callable) -> Type:
        signature = inspect.signature(original_handler)
        return_annotation = signature.return_annotation
        # Set annotations for the new function
        if return_annotation is None:
            raise Exception(f"Method {original_handler.__name__} has nor return annotation")

        mutated_handler.__annotations__ = original_handler.__annotations__
        mutated_handler.__signature__ = signature
        return return_annotation

    def create_schema(self, *args, **kwargs):
        query = self.create_query()
        mutation_ = self.create_mutation()
        subscription_ = self.create_subscription()
        if query is None:
            def health() -> bool:
                return True

            query = type('Query', (), {'health': strawberry_field(health)})
        return Schema(
            query=strawberry_type(query),
            mutation=strawberry_type(mutation_) if mutation_ is not None else None,
            subscription=strawberry_type(subscription_) if subscription_ is not None else None,
            *args, **kwargs
        )

    def create_graphql_asgi_app(self, schema: Any, option: GraphqlOption) -> GraphqlAsgi:
        app_asgi = StrawberryAsgi(schema=schema, option=option)
        return app_asgi
