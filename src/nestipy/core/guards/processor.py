import inspect
import typing
from typing import Type

from nestipy.common.decorator import Injectable
from nestipy.common.guards.can_activate import CanActivate
from nestipy.common.guards.meta import GuardKey
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.logger import logger
from nestipy.core.constant import APP_GUARD
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflector


@Injectable()
class GuardProcessor(SpecialProviderExtractor):
    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def process(
        self, context: ExecutionContext, is_http: bool = True
    ) -> tuple[bool, Type | None]:
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()
        global_guards = []
        if is_http:
            adapter = context.get_adapter()
            global_guards = adapter.get_global_guards() if adapter is not None else []
        # extract guards from global_providers
        module_guards = self.extract_special_providers(
            typing.cast(Type, handler_module_class), CanActivate, APP_GUARD
        )
        handler_class_guards = Reflector.get_metadata(handler_class, GuardKey.Meta, [])
        handler_guards = Reflector.get_metadata(handler, GuardKey.Meta, [])

        list_guards = (
            global_guards + module_guards + handler_class_guards + handler_guards
        )
        for g in list_guards:
            if inspect.isclass(g) and issubclass(g, CanActivate):
                services = self.container.get_all_services()
                # Put dependency
                Reflector.set_metadata(
                    g,
                    ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services),
                )
                #  load instance from container
                instance: CanActivate = typing.cast(
                    CanActivate, await self.container.get(g)
                )
                callback = instance.can_activate
                can_activate: bool = False
                # check if can_activate is coroutine
                if inspect.iscoroutinefunction(callback):
                    can_activate = typing.cast(bool, await callback(context))
                else:
                    can_activate = typing.cast(bool, callback(context))
                if not can_activate:
                    return False, g
        return True, None
