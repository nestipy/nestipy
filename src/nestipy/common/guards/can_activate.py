from abc import abstractmethod, ABC
from typing import Awaitable, Union

from nestipy.core.context.execution_context import ExecutionContext


class CanActivate(ABC):

    @abstractmethod
    async def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        pass
