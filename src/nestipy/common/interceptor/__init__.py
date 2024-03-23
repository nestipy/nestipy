from typing import Union, Type, Callable

from .interface import NestipyInterceptor
from .. import Injectable, Reflect
from ..metadata.decorator import SetMetadata
from ...core.context.execution_context import ExecutionContext
from ...core.ioc.nestipy_container import NestipyContainer
from ...types_ import NextFn

INTERCEPTOR_KEY = '__interceptor__'


def UseInterceptors(*interceptors: Union[Type, NestipyInterceptor]):
    decorator = SetMetadata(INTERCEPTOR_KEY, list(interceptors), as_list=True)

    def wrapper(cls: Union[Type, Callable]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper


@Injectable()
class RequestInterceptor(NestipyInterceptor):

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        class_handler = context.get_class()
        handler = context.get_handler()
        class_interceptors = Reflect.get_metadata(class_handler, INTERCEPTOR_KEY, [])
        handler_interceptors = Reflect.get_metadata(handler, INTERCEPTOR_KEY, [])
        for interceptor in class_interceptors + handler_interceptors:
            instance: NestipyInterceptor = await self.container.get(interceptor)
            result = await instance.intercept(context, next_fn)
            if not result:
                continue
            else:
                return result
        return None


__all__ = [
    "NestipyInterceptor",
    "UseInterceptors",
    "RequestInterceptor"
]
