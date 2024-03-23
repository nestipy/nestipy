from abc import ABC, abstractmethod

from nestipy.core.context.execution_context import ExecutionContext
from nestipy.types_ import NextFn


class NestipyInterceptor(ABC):

    @abstractmethod
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        pass
