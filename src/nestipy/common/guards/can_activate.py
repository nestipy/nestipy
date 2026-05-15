from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Awaitable, Union

if TYPE_CHECKING:
    from nestipy.core.context.execution_context import ExecutionContext


class CanActivate(ABC):
    @abstractmethod
    async def can_activate(
        self, context: "ExecutionContext"
    ) -> Union[Awaitable[bool], bool]:
        """
        Method to handle context and validate it by returning boolean or None
        Args:
            context(ExecutionContext): ExecutionContext of request
        """
        pass
