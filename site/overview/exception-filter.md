This is a example of using exception filter with Nestipy.

```python
from typing import Any

from nestipy.common import ExceptionFilter, Catch, HttpException
from nestipy.core import ArgumentHost


@Catch()
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher')
```

To catch specific exception we need to create class that extends `HttpException`.

```python
import datetime
from typing import Any

from nestipy.common import ExceptionFilter, Catch, HttpStatus, HttpStatusMessages, HttpException,
from nestipy.core import ArgumentHost


class BadRequestException(HttpException):
    def __init__(self):
        super(self, ).__init__(HttpStatus.BAD_REQUEST, HttpStatusMessages.BAD_REQUEST)


@Catch(BadRequestException)
class BadRequestExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        response = host.get_response()
        request = host.get_request()
        status = exception.status_code
        print('Catcher')
        return await response.json({
            'statusCode': status,
            'timestamp': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            'path': request.path,
        })

```

##Binding filters
Let's tie our new BadRequestExceptionFilter to the CatsController's create() method.

```python
from nestipy.common import Controller, Post
from nestipy.common import UseFilters


@Controller('cats')
class CatsController:

    @UseFilters(BadRequestExceptionFilter)
    @Post()
    async def create(self):
        raise BadRequestException()
```

Apply on controller.

```python
from nestipy.common import Controller, Post
from nestipy.common import UseFilters


@UseFilters(BadRequestExceptionFilter)
@Controller('cats')
class CatsController:

    @Post()
    async def create(self):
        raise BadRequestException()
```

To create a global-scoped filter, you would do the following:

```python
from nestipy.core.nestipy_factory import NestipyFactory

app = NestipyFactory.create(AppModule)

app.use_global_filters(BadRequestExceptionFilter)
```

Using it from provider.

```python


from nestipy.common import Module, ModuleProviderDict
from nestipy.core.constant import AppKey


@Module(
    providers=[
        ModuleProviderDict(token=AppKey.APP_FILTER, use_class=BadRequestExceptionFilter)
    ]
)
class AppModule:



```