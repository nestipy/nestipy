from typing import Union, Type, TYPE_CHECKING

from nestipy.metadata import SetMetadata

from nestipy.common.decorator import Injectable
from .meta import ExceptionKey

if TYPE_CHECKING:
    from .interface import ExceptionFilter
    from nestipy.common.exception.http import HttpException


def Catch(*exceptions: Union[Type["HttpException"], "HttpException"]):
    decorator = SetMetadata(ExceptionKey.MetaType, list(exceptions), as_list=True)

    def wrapper(cls: Type["ExceptionFilter"]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper


def UseFilters(*filters: Union[Type["ExceptionFilter"], "ExceptionFilter"]):
    return SetMetadata(ExceptionKey.MetaFilter, list(filters), as_list=True)
