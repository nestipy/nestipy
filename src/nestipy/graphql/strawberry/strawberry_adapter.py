import inspect
from typing import Callable, Type, Any, get_type_hints, get_args, Optional

import strawberry
from strawberry import (
    type as strawberry_type,
    field as strawberry_field,
    mutation,
    subscription,
    Schema,
)
from strawberry.types.field import StrawberryField

from nestipy.ioc.dependency import TypeAnnotated
from nestipy.metadata.dependency import CtxDepKey
from ..graphql_adapter import GraphqlAdapter
from ..graphql_asgi import GraphqlAsgi
from ..graphql_module import GraphqlOption
from ..strawberry.strawberry_asgi import StrawberryAsgi


class StrawberryAdapter(GraphqlAdapter):
    def raise_exception(self, e: Exception):
        raise e

    _schema: Optional[Schema] = None

    def create_type_field_resolver(self, prop: dict, resolver: Callable) -> object:
        type_to_resolve: Type = prop["type"]
        prop_name = prop["name"]
        field = strawberry_field(resolver=resolver)
        field.name = prop_name
        fields: list[StrawberryField] = type_to_resolve.__strawberry_definition__.fields
        new_fields = [field if f.name == prop_name else f for f in fields]
        type_to_resolve.__strawberry_definition__.fields = new_fields
        return type_to_resolve

    def create_query_field_resolver(self, resolver: Callable) -> object:
        return strawberry_field(resolver)

    def create_mutation_field_resolver(self, resolver: Callable) -> object:
        return mutation(resolver)

    def create_subscription_field_resolver(self, resolver: Callable) -> object:
        return subscription(resolver)

    def mutate_handler(
        self, original_handler: Any, mutated_handler: Callable, default_return_type: Any
    ) -> Type:
        signature = inspect.signature(original_handler)
        return_annotation = (
            signature.return_annotation
            if (signature.return_annotation is not getattr(inspect, "_empty"))
            else default_return_type
        )
        # Set annotations for the new function
        if return_annotation is None:
            raise Exception(
                f"Method {original_handler.__name__} has no return annotation"
            )

        original_annotations = get_type_hints(original_handler)

        new_parameters = []
        for param_name, param in signature.parameters.items():
            args = get_args(param.annotation)
            if any(
                isinstance(arg, TypeAnnotated)
                and arg.metadata.key == CtxDepKey.Args
                and arg.metadata.token is None
                for arg in args
            ):
                new_parameters.append(param)

        new_parameters_keys = [k.name for k in new_parameters]
        # Add root and context
        if "root" not in new_parameters_keys and "info" not in new_parameters_keys:
            new_parameters.insert(
                0,
                inspect.Parameter(
                    "root", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Any
                ),
            )
            new_parameters.insert(
                1,
                inspect.Parameter(
                    "info",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=strawberry.Info,
                ),
            )

        if (
            "self" in signature.parameters
            and list(signature.parameters.keys())[0] == "self"
        ):
            new_parameters.insert(0, signature.parameters["self"])
        elif (
            "cls" in signature.parameters
            and list(signature.parameters.keys())[0] == "cls"
        ):
            new_parameters.insert(0, signature.parameters["cls"])

        new_signature = inspect.Signature(
            parameters=new_parameters, return_annotation=return_annotation
        )
        mutated_handler.__annotations__ = original_annotations
        mutated_handler.__signature__ = new_signature
        return return_annotation

    def create_schema(self, **kwargs):
        query = self.create_query()
        mutation_ = self.create_mutation()
        subscription_ = self.create_subscription()
        if query is None:

            def health() -> bool:
                return True

            query = type("Query", (), {"health": strawberry_field(health)})
        return Schema(
            query=strawberry_type(query),
            mutation=strawberry_type(mutation_) if mutation_ is not None else None,
            subscription=strawberry_type(subscription_)
            if subscription_ is not None
            else None,
            **kwargs,
        )

    def create_graphql_asgi_app(
        self, schema: Any, option: GraphqlOption
    ) -> GraphqlAsgi:
        app_asgi = StrawberryAsgi(schema=schema, option=option)
        return app_asgi
