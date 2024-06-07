from typing import Union, Type, Callable

from nestipy.common.decorator import Injectable
from nestipy.metadata import SetMetadata

from .interface import NestipyInterceptor
from .meta import InterceptorKey


def UseInterceptors(*interceptors: Union[Type, NestipyInterceptor]):
    """
    Interceptor decorator to apply interceptor on controller or method of controller.
    Args:
        *interceptors (Union[Type, NestipyInterceptor]): List of interceptors

    Returns:
        wrapper(Callable): A decorator callable
    """
    decorator = SetMetadata(InterceptorKey.Meta, list(interceptors), as_list=True)

    def wrapper(cls: Union[Type, Callable]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper
