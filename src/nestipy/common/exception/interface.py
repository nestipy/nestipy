from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.core.context.argument_host import ArgumentHost
    from nestipy.common.exception.http import HttpException


class ExceptionFilter(ABC):
    @abstractmethod
    async def catch(self, exception: "HttpException", host: "ArgumentHost") -> Any:
        pass
