import inspect
from typing import Type, Union

from nestipy.common.decorator import Injectable
from nestipy.common.guards.can_activate import CanActivate
from nestipy.common.guards.meta import GuardKey
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.core.constant import APP_GUARD
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect


@Injectable()
class GuardProcessor(SpecialProviderExtractor):
    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def process(
        self, context: ExecutionContext, is_http: bool = True
    ) -> tuple[bool, Union[Type, None]]:
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()
        global_guards = []
        if is_http:
            global_guards = context.get_adapter().get_global_guards()
        module_guards = self.extract_special_providers(
            handler_module_class, CanActivate, APP_GUARD
        )
        handler_class_guards = Reflect.get_metadata(handler_class, GuardKey.Meta, [])
        handler_guards = Reflect.get_metadata(handler, GuardKey.Meta, [])

        for g in handler_guards + handler_class_guards + module_guards + global_guards:
            if inspect.isclass(g) and issubclass(g, CanActivate):
                services = self.container.get_all_services()
                # Put dependency
                Reflect.set_metadata(
                    g,
                    ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services),
                )
                #  load instance from container
                instance: CanActivate = await self.container.get(g)
                callback = instance.can_activate
                # check if can_activate is coroutine
                if inspect.iscoroutinefunction(callback):
                    can_activate: bool = await callback(context)
                else:
                    can_activate: bool = callback(context)
                if not can_activate:
                    return False, g
        return True, None
