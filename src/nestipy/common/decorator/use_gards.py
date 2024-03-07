from abc import ABC, abstractmethod

from nestipy.common.context import ExecutionContext


class NestipyCanActivate(ABC):
    guard__ = True
    middleware__ = True

    @abstractmethod
    def can_activate(self, context: ExecutionContext) -> bool:
        return True


class UseGuards:
    guards: list

    def __init__(self, *guards):
        self.guards = [g for g in list(guards) if issubclass(g, NestipyCanActivate)]

    def __call__(self, cls):
        middlewares = getattr(cls, 'middlewares__', [])
        setattr(cls, 'middlewares__', middlewares + self.guards)
        return cls
