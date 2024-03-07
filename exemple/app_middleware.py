from typing import Callable

from nestipy.common.decorator.injectable import Injectable
from nestipy.common.decorator.middleware import NestipyMiddleware


@Injectable()
class AppMiddleware(NestipyMiddleware):
    async def use(self, request, response, next_function: Callable):
        print('AppMiddleware Called')
        await next_function()
