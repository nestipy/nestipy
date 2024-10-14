from abc import abstractmethod, ABC
from typing import Awaitable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.core.context.execution_context import ExecutionContext


class CanActivate(ABC):
    @abstractmethod
    def can_activate(self, context: "ExecutionContext") -> Union[Awaitable[bool], bool]:
        """
        Method to handle context and validate it by returning boolean or None
        Args:
            context(ExecutionContext): ExecutionContext of request
        """
        pass
