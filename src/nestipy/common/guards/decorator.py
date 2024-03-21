from nestipy.common.guards.meta import GuardMetaKey
from nestipy.common.metadata.decorator import SetMetadata
from .can_activate import CanActivate


def UseGuards(*guards):
    return SetMetadata(GuardMetaKey.guards, [g for g in guards if issubclass(g, CanActivate) or callable(g)],
                       as_list=True)
