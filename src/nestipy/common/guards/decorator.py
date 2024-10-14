from typing import Type, Union

from nestipy.metadata import SetMetadata
from .can_activate import CanActivate
from .meta import GuardKey


def UseGuards(*guards: Union[Type, CanActivate]):
    """
    Guard decorator
    Args:
        *guards(Union[Type, CanActivate]): List of guards.

    Returns:
        decorator(): UseGuards decorator
    """
    return SetMetadata(
        GuardKey.Meta,
        [g for g in guards if issubclass(g, CanActivate) or callable(g)],
        as_list=True,
    )
