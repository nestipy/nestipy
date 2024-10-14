from typing import Union, Type, TYPE_CHECKING, Callable

from nestipy.metadata import SetMetadata

from nestipy.common.decorator import Injectable
from .meta import ExceptionKey

if TYPE_CHECKING:
    from .interface import ExceptionFilter
    from nestipy.common.exception.http import HttpException


def Catch(
    *exceptions: Union[Type["HttpException"], "HttpException"],
) -> Callable[[Type["ExceptionFilter"]], Type["ExceptionFilter"]]:
    """
    Catch decorator
    Args:
        *exceptions(Union[Type["HttpException"], "HttpException"]): List of exceptions

    Returns:
        decorator: Catch decorator
    """
    decorator = SetMetadata(ExceptionKey.MetaType, list(exceptions), as_list=True)

    def wrapper(cls: Type["ExceptionFilter"]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper


def UseFilters(*filters: Union[Type["ExceptionFilter"], "ExceptionFilter"]):
    """
    Filter decorator
    Args:
        *filters (Union[Type["ExceptionFilter"], "ExceptionFilter"]): List of filters

    Returns:
        decorator: Filter decorator
    """
    return SetMetadata(ExceptionKey.MetaFilter, list(filters), as_list=True)
