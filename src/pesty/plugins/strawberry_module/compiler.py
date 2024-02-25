import inspect

import snakecase
from strawberry import type as strawberry_type, Schema
from strawberry.tools import merge_types

from .override.field import field


class GraphqlCompiler:
    def __init__(self, modules):
        self.modules = modules

    def compile(self, **kwargs) -> Schema:
        queries, mutations, subscriptions = self.split_class_query_mutation()
        ComboQuery = merge_types("Query", tuple(queries)) if len(queries) > 0 else None
        ComboMutation = merge_types("Mutation", tuple(mutations)) if len(mutations) > 0 else None
        ComboSubscription = merge_types("Subscription", tuple(subscriptions)) if len(subscriptions) > 0 else None
        return Schema(query=ComboQuery, mutation=ComboMutation, subscription=ComboSubscription, **kwargs)

    def get_resolver(self):
        key = 'provider_instances__'
        resolvers = {}
        for m in self.modules:
            module_resolvers_instances = getattr(m, key) if hasattr(m, key) else []
            for key, value in module_resolvers_instances.items():
                if hasattr(value, 'graphql__resolver__'):
                    resolvers[key] = value
        return resolvers

    def split_class_query_mutation(self):
        class_query = []
        class_mutation = []
        class_subscription = []
        resolvers = self.get_resolver()
        for class_, instance_ in resolvers.items():
            name: str = self.get_name(class_)
            properties = self.extract_class_property(class_, instance_)
            class_methods = self.extract_class_not_resolver(class_)
            instance = self.create_instance_of_class(class_.__name__, properties + class_methods)
            methods = self.put_metadata_to_resolver(instance, self.extract_class_method_resolver(class_))

            query_resolver = self.extract_class_query(methods)
            query_ = strawberry_type(type(name + 'Query', (), {'__module__': class_.__module__,
                                                               **self.tuple_to_dict(query_resolver)}))
            class_query.append(query_)

            mutation_resolver = self.extract_class_mutation(methods)
            if len(mutation_resolver) > 0:
                mutation_ = strawberry_type(type(name + 'Mutation', (), {'__module__': class_.__module__,
                                                                         **self.tuple_to_dict(mutation_resolver)}))
                class_mutation.append(mutation_)

            subscription_resolver = self.extract_class_subscription(methods)
            if len(subscription_resolver) > 0:
                subscription_ = strawberry_type(type(name + 'Subscription', (), {'__module__': class_.__module__,
                                                                                 **self.tuple_to_dict(
                                                                                     subscription_resolver)}))
                class_subscription.append(subscription_)

        return class_query, class_mutation, class_subscription

    @classmethod
    def put_metadata_to_resolver(cls, instance, resolvers: list[tuple]):
        modified_resolvers: list[tuple] = []
        for key, method in resolvers:
            setattr(method, 'metadata__', instance)
            modified_resolvers.append((key, method))
        return modified_resolvers

    def create_instance_of_class(self, name, properties):
        cls = type(name, (), {**self.tuple_to_dict(properties)})
        return cls()

    @classmethod
    def extract_class_property(cls, resolver, instance_):
        properties = inspect.getmembers(resolver,
                                        predicate=lambda p: not inspect.ismethod(p) and not inspect.isfunction(p))
        return [(p[0], getattr(instance_, p[0])) for p in properties if not p[0].startswith('_')
                and not p[0].endswith('_')]

    @classmethod
    def is_resolver(cls, p):
        return hasattr(p, 'graphql__resolver__')

    @classmethod
    def extract_class_method_resolver(cls, resolver):
        methods = inspect.getmembers(resolver,
                                     predicate=lambda p:
                                     (inspect.ismethod(p) or inspect.isfunction(p)) and cls.is_resolver(p))

        return [p for p in methods if not p[0].startswith('__')]

    @classmethod
    def extract_class_not_resolver(cls, resolver):
        methods = inspect.getmembers(resolver,
                                     predicate=lambda p:
                                     (inspect.ismethod(p) or inspect.isfunction(p))
                                     and not cls.is_resolver(p))
        return [(m[0], m[1]) for m in methods if not m[0].startswith('__')]

    @classmethod
    def extract_class_query(cls, methods):
        return [(m[0], field(m[1], **cls.get_kwargs(m[1]))) for m in methods if hasattr(m[1], 'query__')]
        pass

    @classmethod
    def extract_class_mutation(cls, methods):
        return [(m[0], field(m[1], **cls.get_kwargs(m[1]))) for m in methods if hasattr(m[1], 'mutation__')]

    @classmethod
    def extract_class_subscription(cls, methods):
        return [(m[0], field(m[1], **cls.get_kwargs(m[1]), is_subscription=True)) for m in methods if
                hasattr(m[1], 'subscription__')]

    @classmethod
    def tuple_to_dict(cls, tuples: list):
        dicts = {}
        for key, value in tuples:
            dicts[key] = value
        return dicts

    @classmethod
    def get_name(cls, class_):
        return snakecase.convert(class_.__name__).split('_')[0].capitalize()

    @classmethod
    def get_kwargs(cls, method):
        return method.kwargs if hasattr(method, 'kwargs') else {}
