from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):
    context: ExecutionContext

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(
        self, context: ExecutionContext, next_fn: "NextFn", is_http: bool = True
    ):
        self.context = context
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = (
            context.get_adapter().get_global_interceptors() if is_http else []
        )
        module_interceptors = self.extract_special_providers(
            handler_module_class, NestipyInterceptor, APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(
            handler_class, InterceptorKey.Meta, []
        )
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = (
            handler_interceptors
            + class_interceptors
            + module_interceptors
            + global_interceptors
        )
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept,
                    ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services),
                )

        return await self._recursive_apply_interceptor(0, all_interceptors, next_fn)

    async def _recursive_apply_interceptor(
        self, index: int, all_interceptors: list, next_fn: "NextFn"
    ):
        if len(all_interceptors) > index:
            interceptor = all_interceptors[index]
            instance: NestipyInterceptor = await self.container.get(interceptor)

            async def _next_fn():
                return await instance.intercept(self.context, next_fn)

            return await self._recursive_apply_interceptor(
                index + 1, all_interceptors, _next_fn
            )
        else:
            return await next_fn()


__all__ = ["RequestInterceptor"]
