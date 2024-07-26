from nestipy.common.decorator import Injectable

from nestipy.common import CanActivate
from nestipy.core.context.execution_context import ExecutionContext


@Injectable()
class TestGuard(CanActivate):

    def can_activate(self, context: ExecutionContext) -> bool:
        headers = context.switch_to_http().get_request().headers
        print("TestGuard called with headers::: ", headers)
        return False


@Injectable()
class TestGuardMethod(CanActivate):

    def can_activate(self, context: ExecutionContext) -> bool:
        print("TestGuardMethod called")
        return True
