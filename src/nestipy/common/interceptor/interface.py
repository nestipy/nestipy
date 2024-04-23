from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from nestipy.core.context.execution_context import ExecutionContext

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


class NestipyInterceptor(ABC):

    @abstractmethod
    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        pass
