import inspect
from typing import Callable, Type, Union

from nestipy.common import Injectable, Reflect
from nestipy.core.context.execution_context import ExecutionContext
from .can_activate import CanActivate
from .meta import GuardMetaKey
from ..helpers import SpecialProviderExtractor
from ...core.constant import APP_GUARD


@Injectable()
class GuardProcessor(SpecialProviderExtractor):

    def __init__(self):
        from nestipy.core.ioc.nestipy_container import NestipyContainer
        self.container = NestipyContainer.get_instance()

    async def process(self, context: ExecutionContext) -> tuple[bool, Union[Type, None]]:

        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_guards = context.get_adapter().get_global_guards()
        module_guards = self.extract_special_providers(
            handler_module_class,
            CanActivate,
            APP_GUARD
        )
        handler_class_guards = Reflect.get_metadata(handler_class, GuardMetaKey.guards, [])
        handler_guards = Reflect.get_metadata(handler, GuardMetaKey.guards, [])

        for g in global_guards + module_guards + handler_class_guards + handler_guards:
            if issubclass(g, CanActivate):
                #  load instance from container
                instance: CanActivate = await self.container.get(g)
                callback: Callable = instance.can_activate
                # check if can_activate is coroutine
                if inspect.iscoroutinefunction(callback):
                    can_activate: bool = await callback(context)
                else:
                    can_activate: bool = callback(context)
                if not can_activate:
                    return False, g
        return True, None
