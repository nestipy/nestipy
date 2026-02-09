import inspect
import typing
from typing import Type, Union, Any

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.pipes import PipeTransform, PipeKey
from nestipy.core.constant import APP_PIPE
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect


@Injectable()
class PipeProcessor(SpecialProviderExtractor):
    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def get_pipes(
        self, context: ExecutionContext, is_http: bool = True
    ) -> list[Union[Type, PipeTransform]]:
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_pipes = (
            typing.cast(Any, context.get_adapter()).get_global_pipes()
            if is_http
            else []
        )
        module_pipes = self.extract_special_providers(
            typing.cast(Type, handler_module_class), PipeTransform, APP_PIPE
        )
        class_pipes = Reflect.get_metadata(handler_class, PipeKey.Meta, [])
        handler_pipes = Reflect.get_metadata(handler, PipeKey.Meta, [])

        all_pipes = [*global_pipes, *module_pipes, *class_pipes, *handler_pipes]

        # Setup DI scope for pipe classes if needed
        services = self.container.get_all_services()
        for p in all_pipes:
            if inspect.isclass(p) and issubclass(p, PipeTransform):
                Reflect.set_metadata(
                    p,
                    ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services),
                )
        return all_pipes
