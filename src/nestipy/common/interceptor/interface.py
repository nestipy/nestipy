from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn
    from nestipy.core.context.execution_context import ExecutionContext


class NestipyInterceptor(ABC):
    @abstractmethod
    async def intercept(self, context: "ExecutionContext", next_fn: "NextFn"):
        """
        Args:
            context (ExecutionContext): ExecutionContext of request
            next_fn (NextFn): The next function handler
        """
        pass
