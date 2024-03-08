from nestipy.common import Inject
from .guard_service import GuardService
from nestipy.common.context import ExecutionContext
from nestipy.common.decorator.use_gards import NestipyCanActivate


class AuthGuard(NestipyCanActivate):
    service: GuardService = Inject(GuardService)

    def can_activate(self, context: ExecutionContext) -> bool:
        print(f'AuthGuard called')
        return True
