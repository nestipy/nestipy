from strawberry import input, type as strawberry_type

from nestipy.common.decorator import Injectable


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


class Subscription:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__resolver__', True)
        setattr(cls, 'subscription__', True)
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
        setattr(cls, 'graphql__type__', True)
        return strawberry_type(cls, **self.kwargs)


class Input:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        setattr(cls, 'graphql__input__', True)
        return input(cls, **self.kwargs)
