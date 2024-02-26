from abc import ABC, abstractmethod
from typing import Callable


class NestipyMiddleware(ABC):
    middleware__ = True

    @abstractmethod
    def use(self, scope, receive, send):
        return scope


class Middleware:
    middleware: list

    def __init__(self, *middleware):
        self.middleware = list(middleware)

    def __call__(self, cls):
        setattr(cls, 'middleware__', self.middleware)
        return cls
