from typing import Optional, Type

from .commander import NestipyCommander


class CommandFactory:

    @classmethod
    def create(cls, root_module: Optional[Type]) -> NestipyCommander:
        instance = NestipyCommander()
        instance.init(root_module)
        return instance
