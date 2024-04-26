from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nestipy.common.http_ import Request, Response
    from nestipy.types_ import NextFn


class NestipyMiddleware(ABC):
    @abstractmethod
    async def use(self, req: "Request", res: "Response", next_fn: "NextFn"):
        pass
