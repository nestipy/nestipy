from strawberry import field, input, mutation, type as strawberry_type

from pesty.common.decorator import Injectable


class Resolver:
    resolver__ = True

    def __call__(self, cls, *_):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'type__', True)
        return Injectable()(cls)


class Query:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'query__', True)
        setattr(cls, 'kwargs__', self.kwargs)
        return cls


class Mutation:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'mutation__', True)
        setattr(cls, 'kwargs__', self.kwargs)
        return cls


class Type:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'type__', True)
        return strawberry_type(cls, **self.kwargs)


class Input:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'type__', True)
        return input(cls, **self.kwargs)
