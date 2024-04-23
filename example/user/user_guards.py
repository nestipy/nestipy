from nestipy_decorator import Injectable

from nestipy.common import CanActivate
from nestipy.core.context.execution_context import ExecutionContext


@Injectable()
class TestGuard(CanActivate):

    def can_activate(self, context: ExecutionContext) -> bool:
        print("TestGuard called")
        return True


@Injectable()
class TestGuardMethod(CanActivate):

    def can_activate(self, context: ExecutionContext) -> bool:
        print("TestGuardMethod called")
        return True
