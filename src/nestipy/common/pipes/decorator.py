from typing import Type, Union, Callable

from nestipy.metadata import SetMetadata
from .interface import PipeTransform
from .meta import PipeKey


def UsePipes(*pipes: Union[Type[PipeTransform], PipeTransform]):
    """
    Pipe decorator for controller or method.
    Args:
        *pipes: list of pipe classes or instances
    """
    return SetMetadata(
        PipeKey.Meta,
        [p for p in pipes if isinstance(p, PipeTransform) or callable(p)],
        as_list=True,
    )
