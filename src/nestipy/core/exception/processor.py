import typing
from typing import Union, Callable

from nestipy.common.decorator import Injectable
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.interface import ExceptionFilter
from nestipy.common.exception.meta import ExceptionKey
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.utils import uniq_list
from nestipy.core.constant import APP_FILTER
from nestipy.core.context.argument_host import ArgumentHost
from nestipy.core.types import HandlerReturn
from nestipy.ioc import NestipyContainer
from nestipy.metadata import Reflect, ClassMetadata


@Injectable()
class ExceptionFilterHandler(SpecialProviderExtractor):
    context: Union[ArgumentHost, None] = None

    def __init__(
        self,
    ):
        self.container = NestipyContainer.get_instance()

    async def catch(
        self, exception: HttpException, context: ArgumentHost, is_http: bool = True
    ) -> HandlerReturn | None:
        self.context = context
        handler_module_class = self.context.get_module()
        handler_class = self.context.get_class()
        handler = self.context.get_handler()
        if is_http:
            adapter = context.get_adapter()
            global_filters = adapter.get_global_filters() if adapter is not None else []
        else:
            global_filters = []
        module_filters = self.extract_special_providers(
            typing.cast(typing.Type, handler_module_class), ExceptionFilter, APP_FILTER
        )
        class_filters = Reflect.get_metadata(handler_class, ExceptionKey.MetaFilter, [])
        handler_filters = Reflect.get_metadata(handler, ExceptionKey.MetaFilter, [])
        # NestJS order: method -> class -> module -> global (most specific first)
        all_filters = uniq_list(
            handler_filters + class_filters + module_filters + global_filters
        )
        # setup dependency as the same as the container
        for fit in all_filters:
            if issubclass(fit, ExceptionFilter):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    fit,
                    ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services),
                )
        return await self._apply_exception_filter(exception, 0, all_filters, None)

    async def _apply_exception_filter(
        self,
        exception: "HttpException",
        index: int,
        all_filters: list,
        result: HandlerReturn | None,
    ):
        if len(all_filters) > index:
            exception_filter = all_filters[index]
            all_exception_to_catch = Reflect.get_metadata(
                exception_filter, ExceptionKey.MetaType, []
            )
            new_result = await self._apply_exception_filter_for_exception(
                exception_filter, exception, 0, all_exception_to_catch, result
            )
            return await self._apply_exception_filter(
                exception,
                index + 1,
                all_filters,
                new_result if new_result is not None else result,
            )
        else:
            return result

    async def _apply_exception_filter_for_exception(
        self,
        exception_filter: Union[Callable, "ExceptionFilter"],
        exception: "HttpException",
        index: int,
        all_exception_to_catch: list,
        result: HandlerReturn | None,
    ):
        if len(all_exception_to_catch) > index:
            exception_to_catch = all_exception_to_catch[index]
            if isinstance(exception, exception_to_catch) or (
                exception.status_code == exception_to_catch.status_code
            ):
                new_result = await self._catch_exception(exception_filter, exception)
                return await self._apply_exception_filter_for_exception(
                    exception_filter,
                    exception,
                    index + 1,
                    all_exception_to_catch,
                    new_result if new_result is not None else result,
                )
            return result
        else:
            return await self._catch_exception(exception_filter, exception)

    async def _catch_exception(
        self,
        exception_filter: Union[Callable, "ExceptionFilter"],
        exception: "HttpException",
    ):
        instance = (
            await self.container.get(exception_filter)
            if not isinstance(exception_filter, ExceptionFilter)
            else exception_filter
        )
        return await instance.catch(exception, typing.cast(ArgumentHost, self.context))
