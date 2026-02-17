import inspect
from typing import Callable, Type, Any, get_type_hints, get_args, Optional, cast

import strawberry
from graphql import GraphQLError
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
from nestipy.core.exception.error_policy import build_graphql_error, request_context_info
from ..graphql_adapter import GraphqlAdapter
from ..graphql_asgi import GraphqlASGI
from ..graphql_module import GraphqlOption
from ..strawberry.strawberry_asgi import StrawberryASGI


class StrawberryAdapter(GraphqlAdapter):
    def raise_exception(self, e: Exception):
        if isinstance(e, GraphQLError):
            raise e
        request_id, debug = request_context_info()
        message, extensions = build_graphql_error(
            e, request_id=request_id, debug=debug
        )
        raise GraphQLError(message, original_error=e, extensions=extensions or None)

    _schema: Optional[Schema] = None

    def create_type_field_resolver(
        self, prop: dict, resolve: Callable, field_options: Optional[dict] = None
    ) -> object:
        type_to_resolve: Type = prop["type"]
        prop_name = prop["name"]
        options = dict(field_options or {})
        options.pop("name", None)
        field = strawberry_field(resolver=resolve, **options)
        field.name = prop_name
        fields: list[StrawberryField] = type_to_resolve.__strawberry_definition__.fields
        new_fields = [field if f.name == prop_name else f for f in fields]
        type_to_resolve.__strawberry_definition__.fields = new_fields
        return type_to_resolve

    def create_query_field_resolver(
        self, resolver: Callable, field_options: Optional[dict] = None
    ) -> object:
        options = dict(field_options or {})
        options.pop("name", None)
        return strawberry_field(resolver, **options)

    def create_mutation_field_resolver(
        self, resolver: Callable, field_options: Optional[dict] = None
    ) -> object:
        options = dict(field_options or {})
        options.pop("name", None)
        return mutation(resolver, **options)

    def create_subscription_field_resolver(
        self, resolver: Callable, field_options: Optional[dict] = None
    ) -> object:
        options = dict(field_options or {})
        options.pop("name", None)
        return subscription(resolver, **options)

    def modify_handler_signature(
        self,
        original_handler: Callable,
        wrapper_handler: Callable,
        default_return_type: Any,
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
                f"Method {cast(Any, original_handler).__name__} has no return annotation"
            )

        original_annotations = get_type_hints(original_handler)

        new_parameters = []
        for param_name, param in signature.parameters.items():
            args = get_args(param.annotation)
            if any(
                isinstance(arg, TypeAnnotated)
                and arg.metadata.key == CtxDepKey.Args
                and arg.metadata.token not in ("root", "info", "__all_args__")
                for arg in args
            ):
                token = next(
                    (
                        arg.metadata.token
                        for arg in args
                        if isinstance(arg, TypeAnnotated)
                        and arg.metadata.key == CtxDepKey.Args
                    ),
                    None,
                )
                if isinstance(token, str) and token and token != param.name:
                    new_param = inspect.Parameter(
                        token,
                        param.kind,
                        default=param.default,
                        annotation=param.annotation,
                    )
                    new_parameters.append(new_param)
                else:
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
        new_annotations: dict[str, Any] = {}
        for param in new_signature.parameters.values():
            if param.name in original_annotations:
                new_annotations[param.name] = original_annotations[param.name]
            elif param.annotation is not inspect._empty:
                new_annotations[param.name] = param.annotation
        if "return" in original_annotations:
            new_annotations["return"] = original_annotations["return"]
        cast(Any, wrapper_handler).__annotations__ = new_annotations
        cast(Any, wrapper_handler).__signature__ = new_signature
        return return_annotation

    def create_schema(self, **kwargs) -> Schema:
        query = self.create_query()
        mutation_ = self.create_mutation()
        subscription_ = self.create_subscription()
        if query is None:

            def health() -> bool:
                return True

            query = type("Query", (), {"health": strawberry_field(health)})
        return Schema(
            query=cast(Type, strawberry_type(query)),
            mutation=cast(Type, strawberry_type(mutation_))
            if mutation_ is not None
            else None,
            subscription=cast(Type, strawberry_type(subscription_))
            if subscription_ is not None
            else None,
            **kwargs,
        )

    def create_graphql_asgi_app(
        self, schema: Any, option: GraphqlOption
    ) -> GraphqlASGI:
        app_asgi = StrawberryASGI(schema=schema, option=option)
        return app_asgi
