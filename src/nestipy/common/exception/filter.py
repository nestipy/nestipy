from abc import ABC, abstractmethod
from typing import Union, Type, Any

from nestipy.common.decorator import Injectable
from nestipy.common.exception.http import HttpException
from nestipy.common.metadata.decorator import SetMetadata
from nestipy.common.metadata.reflect import Reflect
from nestipy.core.context.argument_host import ArgumentHost
from nestipy.core.ioc.nestipy_container import NestipyContainer

EXCEPTION_FILTER_KEY = '__exception_filter__'
EXCEPTION_TYPE_KEY = '__exception_filter_type__'


def Catch(*exceptions: Union[Type["HttpException"], HttpException]):
    decorator = SetMetadata(EXCEPTION_TYPE_KEY, list(exceptions), as_list=True)

    def wrapper(cls: Type["ExceptionFilter"]):
        cls = Injectable()(cls)
        return decorator(cls)

    return wrapper


def UseFilters(*filters: Union[Type["ExceptionFilter"], "ExceptionFilter"]):
    return SetMetadata(EXCEPTION_FILTER_KEY, list(filters), as_list=True)


class ExceptionFilter(ABC):
    @abstractmethod
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        pass


@Injectable()
class ExceptionFilterHandler:
    context: ArgumentHost = None

    def __init__(self, ):
        self.container = NestipyContainer.get_instance()

    async def handler(self, exception: HttpException, context: ArgumentHost) -> Union[Any, None]:
        self.context = context
        handler_class = self.context.get_class()
        handler = self.context.get_handler()
        class_filters = Reflect.get_metadata(handler_class, EXCEPTION_FILTER_KEY, [])
        handler_filters = Reflect.get_metadata(handler, EXCEPTION_FILTER_KEY, [])
        for ex_filter in class_filters + handler_filters:
            result = await self._recursive_apply_filter(ex_filter, exception)
            if not result:
                continue
            else:
                return result
        return None

    async def _catch(self, _filter: Union[Type["ExceptionFilter"], "ExceptionFilter"], exception: HttpException):
        instance = await self.container.get(_filter) if not isinstance(
            _filter,
            ExceptionFilter) else _filter
        return await instance.catch(exception, self.context)

    async def _recursive_apply_filter(
            self,
            exception_filter: Union[Type["ExceptionFilter"], "ExceptionFilter"],
            exception: HttpException,
    ):

        exceptions_to_catch = Reflect.get_metadata(exception_filter, EXCEPTION_TYPE_KEY, [])
        if len(exceptions_to_catch) == 0:
            return await self._catch(exception_filter, exception)
        else:
            for _ex_type in exceptions_to_catch:
                if isinstance(exception, _ex_type):
                    result = await self._catch(exception_filter, exception)
                    if result is None:
                        continue
                    else:
                        return result
        return None
