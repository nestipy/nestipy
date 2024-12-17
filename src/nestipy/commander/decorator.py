from typing import Callable

from graphql.pyutils import description

from nestipy.common.decorator import Injectable
from .meta import CommanderMeta
from nestipy.metadata.decorator import SetMetadata


class Command:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc

    def __call__(self, func: Callable) -> Callable:
        data = {
            "name": self.name,
            "description": self.desc
        }
        decorator = SetMetadata(CommanderMeta.Meta, data)
        return decorator(Injectable()(func))
