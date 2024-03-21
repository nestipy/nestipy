from abc import ABC, abstractmethod

from nestipy.common import Request, Response
from nestipy.types_ import NextFn


class NestipyMiddleware(ABC):
    @abstractmethod
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        pass
