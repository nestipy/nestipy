from typing import Type, Union, Callable, Any

from nestipy.metadata import Reflect

from nestipy.graphql.meta import NestipyGraphqlKey


class GraphQlDecorator:
    def __init__(self, graphql_type: str, value: Any = True, is_method: bool = True):
        self.graphql_type = graphql_type
        self.graphql_value = value
        self.is_method = is_method

    def __call__(self, return_type: Type = None, *args, **kwargs):
        def wrapper(class_ref: Union[Type, Callable]):
            from nestipy.common.decorator import Injectable
            if not self.is_method:
                class_ref = Injectable()(class_ref)
            Reflect.set_metadata(class_ref, self.graphql_type, self.graphql_value)
            Reflect.set_metadata(class_ref, NestipyGraphqlKey.return_type, return_type)
            return class_ref

        return wrapper


def Resolver(return_type: Type = None, *args, **kwargs):
    return GraphQlDecorator(NestipyGraphqlKey.resolver, is_method=False)(return_type, *args, **kwargs)


def Query(return_type: Type = None, *args, **kwargs):
    return GraphQlDecorator(NestipyGraphqlKey.handler, NestipyGraphqlKey.query)(return_type, *args, **kwargs)


def Mutation(return_type: Type = None, *args, **kwargs):
    return GraphQlDecorator(NestipyGraphqlKey.handler, NestipyGraphqlKey.mutation)(return_type, *args, **kwargs)


def Subscription(return_type: Type = None, *args, **kwargs):
    return GraphQlDecorator(NestipyGraphqlKey.handler, NestipyGraphqlKey.subscription)(return_type, *args, **kwargs)
