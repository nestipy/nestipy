from nestipy.common.context import ExecutionContext
from strawberry.types import ExecutionContext as StrawberryExecutionContext
from nestipy.common.decorator.use_gards import NestipyCanActivate


class AuthGuard(NestipyCanActivate):
    def can_activate(self, context: ExecutionContext | StrawberryExecutionContext) -> bool:
        print(f'AuthGuard called')
        return True
