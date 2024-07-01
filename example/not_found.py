from typing import Any

from nestipy.common import Injectable, HttpException, HttpStatus
from nestipy.common import ExceptionFilter
from nestipy.core import ArgumentHost


@Injectable()
class NotFoundHandler(ExceptionFilter):
    async def catch(self, exception: "HttpException", host: "ArgumentHost") -> Any:
        if exception.status_code == HttpStatus.NOT_FOUND:
            return await host.get_response().status(200).render('index.html')
