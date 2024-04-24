from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy_ioc import NestipyContainer
from nestipy_metadata import ClassMetadata, Reflect

from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = context.get_adapter().get_global_interceptors()
        module_interceptors = self.extract_special_providers(
            handler_module_class,
            NestipyInterceptor,
            APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(handler_class, InterceptorKey.Meta, [])
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = global_interceptors + class_interceptors + handler_interceptors
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept, ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services)
                )
        for interceptor in all_interceptors:
            instance: NestipyInterceptor = await self.container.get(interceptor)
            result = await instance.intercept(context, next_fn)
            if not result:
                continue
            else:
                return result
        return await next_fn()


__all__ = [
    "RequestInterceptor"
]
