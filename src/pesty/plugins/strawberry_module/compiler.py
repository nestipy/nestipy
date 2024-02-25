import inspect
from strawberry import type as strawberry_type, field, mutation, Schema
import snakecase
from strawberry.tools import merge_types

from pesty.core import PestyContainer


class GraphqlCompiler:
    def __init__(self, modules):
        self.modules = modules

    def compile(self, **kwargs) -> Schema:
        queries, mutations = self.split_class_query_mutation()
        ComboQuery = merge_types("Query", tuple(queries))
        ComboMutation = merge_types("Mutation", tuple(mutations))
        return Schema(query=ComboQuery, mutation=ComboMutation, **kwargs)

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
        resolvers = self.get_resolver()
        for class_, instance_ in resolvers.items():
            name: str = self.get_name(class_)
            properties = self.extract_class_property(class_, instance_)
            methods = self.extract_class_method(class_)
            query_resolver = self.extract_class_query(methods)
            mutation_resolver = self.extract_class_mutation(methods)
            query_ = strawberry_type(type(name + 'Query', (), {'__module__': class_.__module__,
                                                               **self.tuple_to_dict(properties + query_resolver)}))
            mutation_ = strawberry_type(type(name + 'Mutation', (), {'__module__': class_.__module__,
                                                                     **self.tuple_to_dict(
                                                                         properties + mutation_resolver)}))
            class_mutation.append(mutation_)
            class_query.append(query_)

        return class_query, class_mutation

    @classmethod
    def extract_class_property(cls, resolver, instance_):
        properties = inspect.getmembers(resolver,
                                        predicate=lambda p: not inspect.ismethod(p) and not inspect.isfunction(p))
        return [(p[0], getattr(instance_, p[0])) for p in properties if not p[0].startswith('_')
                and not p[0].endswith('_')]

    @classmethod
    def extract_class_method(cls, resolver):
        methods = inspect.getmembers(resolver,
                                     predicate=lambda p: inspect.ismethod(p) or inspect.isfunction(p))

        return [p for p in methods if not p[0].startswith('__')]

    @classmethod
    def extract_class_query(cls, methods):
        return [(m[0], field(m[1])) for m in methods if hasattr(m[1], 'query__')]
        pass

    @classmethod
    def extract_class_mutation(cls, methods):
        return [(m[0], mutation(m[1])) for m in methods if hasattr(m[1], 'mutation__')]

    @classmethod
    def tuple_to_dict(cls, tuples: list):
        dicts = {}
        for key, value in tuples:
            dicts[key] = value
        return dicts

    @classmethod
    def get_name(cls, class_):
        return snakecase.convert(class_.__name__).split('_')[0].capitalize()
