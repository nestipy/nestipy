import inspect
from dataclasses import asdict
from typing import TYPE_CHECKING, Callable

from strawberry import Schema, type
from strawberry.asgi import GraphQL
from strawberry.extensions import SchemaExtension
from strawberry.types import Info

from nestipy.common.decorator import NestipyMiddleware, Inject
from nestipy.core.ioc.container import NestipyContainer
from nestipy.common.context import Request, Response
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
    container: NestipyContainer | None = None

    async def resolve(self, _next, root, info: Info, *args, **kwargs):
        self.container = self.get_container()
        self.get_execution_context()
        await self.apply_guards(info=info)
        return _next(root, info, *args, **kwargs)

    def get_resolver(self, name: str):
        return self.execution_context.schema.get_field_for_type(
            name,
            self.execution_context.operation_type.value.capitalize()
        )

    def get_execution_context(self):
        request = self.execution_context.context.get('request')
        return request.app.context

    def get_container(self) -> NestipyContainer | None:
        request = self.execution_context.context.get('request')
        if request:
            scope = request.scope
            if scope:
                return scope['container']
        return None

    async def apply_guards(self, info: Info):
        resolver = self.get_resolver(name=info.field_name)
        if resolver is not None:
            base_resolver = getattr(resolver, 'base_resolver')
            wrapped_func = getattr(base_resolver, 'wrapped_func')
            guards = [m for m in getattr(wrapped_func, 'middlewares__', []) if hasattr(m, 'guard__')]
            module_parent = getattr(wrapped_func, 'module__parent__')
            await self.recursive_call_guards(module_parent, info=info, index=0, guards=guards)

    async def recursive_call_guards(self, module_parent, info: Info, index=0, guards: list = None) -> bool:

        if index < len(guards):
            context = self.get_execution_context()
            guard = guards[index]
            instance_guard = self.container.resolve(guard, module_parent)
            can_activate: Callable = getattr(instance_guard, 'can_activate')
            if inspect.iscoroutinefunction(can_activate):
                response = await can_activate(context)
            else:
                response = can_activate(context)
            if response:
                if index + 1 < len(guards):
                    return await self.recursive_call_guards(module_parent, info, index + 1, guards)
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
