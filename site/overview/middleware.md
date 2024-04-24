Nestipy define middleware like NestJs do.

```python
from nestipy.common import Injectable

from nestipy.common import Request, Response
from nestipy.common import NestipyMiddleware
from nestipy.types_ import NextFn


@Injectable()
class LoggerMiddleware(NestipyMiddleware):
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        print('Requesting ....')
        await next_fn()
```

### Dependency injection

Nestipy middleware support dependency injection

### Applying middleware#

Nestipy apply middleware like the way Nestjs use. Modules that include middleware have to implement the NestipyModule.

```python title='app_module.py'
from nestipy_dynamic_module import NestipyModule, MiddlewareConsumer

from nestipy.common import Module


@Module()
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(LoggerMiddleware).for_route('cats')

```

## Apply middleware for controller

We can apply middleware for controller and excludes some routes.

```python title='app_module.py'
from nestipy.common import Module
from nestipy_dynamic_module import NestipyModule,MiddlewareConsumer


@Module()
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(LoggerMiddleware).for_route(CatsController).excludes([])

```

### Functional middleware

```python
from nestipy.common import Request, Response
from nestipy.types_ import NextFn


async def logger(req: Request, res: Response, next_fn: NextFn):
    print('Requesting ....')
    await next_fn()
```

And use it within the AppModule:

```python
consumer.apply(logger).for_route(CatsController).excludes([])
```

## Global middleware

```python
from nestipy.core import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use(logger)
```

