from typing import Union, Type, Callable

from nestipy.common.decorator import Injectable
from nestipy.metadata import SetMetadata

from .interface import NestipyInterceptor
from .meta import InterceptorKey


def UseInterceptors(*interceptors: Union[Type, NestipyInterceptor]):
    decorator = SetMetadata(InterceptorKey.Meta, list(interceptors), as_list=True)

    def wrapper(cls: Union[Type, Callable]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper
