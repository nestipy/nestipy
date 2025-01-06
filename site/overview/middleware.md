Middleware is a function that executes before the route handler in the application's request-response cycle. It has access to the request and response objects, as well as the `next_fn()` function, which passes control to the subsequent middleware. The `next_fn()` function is typically represented by the variable `next_fn`.

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

Nestipy middleware support dependency injection. Similar to providers and controllers, they can inject dependencies that are available within the same module.

### Applying middleware#

Nestipy apply middleware like the way Nestjs use. Modules that include middleware have to implement the NestipyModule.

```python title='app_module.py'
from nestipy.dynamic_module import NestipyModule

from nestipy.common import Module
from nestipy.core import MiddlewareConsumer


@Module()
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(LoggerMiddleware).for_route('cats')

```

## Apply middleware for controller

We can apply middleware for controller and excludes some routes.

```python title='app_module.py'
from nestipy.dynamic_module import NestipyModule

from nestipy.common import Module
from nestipy.core import MiddlewareConsumer


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

Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-middleware)** for an  example.

