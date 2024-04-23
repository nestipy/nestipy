from typing import Type, Union

from nestipy_metadata import SetMetadata

from .can_activate import CanActivate
from .meta import GuardMetaKey


def UseGuards(*guards: Union[Type, CanActivate]):
    return SetMetadata(GuardMetaKey.guards, [g for g in guards if issubclass(g, CanActivate) or callable(g)],
                       as_list=True)
