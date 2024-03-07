import inspect
from dataclasses import asdict
from typing import TYPE_CHECKING, Callable

from strawberry import Schema, type
from strawberry.asgi import GraphQL
from strawberry.extensions import SchemaExtension
from strawberry.types import Info

from nestipy.common.decorator import NestipyMiddleware, Inject
from .constant import STRAWBERRY_MODULE_OPTION
from .override.field import field

if TYPE_CHECKING:
    from .strawberry_module import StrawberryOption
    from ...common.context import Request, Response


@type
class Query:
    @field
    def test(self) -> str:
        return 'Test ok'


class ExecutionContextExtension(SchemaExtension):
    async def resolve(self, _next, root, info: Info, *args, **kwargs):
        await self.apply_guards(info=info)
        return _next(root, info, *args, **kwargs)

    def get_resolver(self, name: str):
        return self.execution_context.schema.get_field_for_type(
            name,
            self.execution_context.operation_type.value.capitalize()
        )

    async def apply_guards(self, info: Info):
        resolver = self.get_resolver(name=info.field_name)
        if resolver is not None:
            base_resolver = getattr(resolver, 'base_resolver')
            wrapped_func = getattr(base_resolver, 'wrapped_func')
            guards = [m for m in getattr(wrapped_func, 'middlewares__', []) if hasattr(m, 'guard__')]
            await self.recursive_call_guards(info=info, index=0, guards=guards)

    async def recursive_call_guards(self, info: Info, index=0, guards: list = None) -> bool:

        if index < len(guards):
            context = self.execution_context
            instance_guard = guards[index]()
            can_activate: Callable = getattr(instance_guard, 'can_activate')
            if inspect.iscoroutinefunction(can_activate):
                response = await can_activate(context)
            else:
                response = can_activate(context)
            if response:
                if index + 1 < len(guards):
                    return await self.recursive_call_guards(info, index + 1, guards)
                else:
                    return True
            else:
                raise Exception(f'Error handler during applying guards {instance_guard.__class__.__name__}!')
        else:
            return True


class StrawberryMiddleware(NestipyMiddleware):
    option: 'StrawberryOption' = Inject(STRAWBERRY_MODULE_OPTION)

    def __init__(self):
        dict_option = asdict(self.option)
        if hasattr(self, 'schema'):
            self.app = GraphQL(schema=getattr(self, 'schema'), **dict_option)
        else:
            self.app = GraphQL(schema=Schema(query=Query, extensions=[ExecutionContextExtension], ), **dict_option)

    async def use(self, request: "Request", response: "Response", next_function):
        if hasattr(self, 'app'):
            await self.app(request.scope, request.original_receive, response.send)
            return None
        await next_function()
