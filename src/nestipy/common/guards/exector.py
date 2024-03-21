import inspect
from typing import Callable, Type, Union

from nestipy.common import Injectable, Reflect
from nestipy.core.context.execution_context import ExecutionContext
from .can_activate import CanActivate
from .meta import GuardMetaKey


@Injectable()
class GuardProcessor:

    @classmethod
    async def process(cls, context: ExecutionContext) -> tuple[bool, Union[Type, None]]:
        from nestipy.core.ioc.nestipy_container import NestipyContainer
        handler_class = context.get_class()
        handler = context.get_handler()
        handler_class_guards = Reflect.get_metadata(handler_class, GuardMetaKey.guards, [])
        handler_guards = Reflect.get_metadata(handler, GuardMetaKey.guards, [])

        for g in handler_class_guards + handler_guards:
            if issubclass(g, CanActivate):
                #  load instance from container
                instance: CanActivate = await NestipyContainer.get_instance().get(g)
                callback: Callable = instance.can_activate
                # check if can_activate is coroutine
                if inspect.iscoroutinefunction(callback):
                    can_activate: bool = await callback(context)
                else:
                    can_activate: bool = callback(context)
                if not can_activate:
                    return False, g
        return True, None
