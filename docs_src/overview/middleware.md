Middleware runs **before guards, pipes, and interceptors** in the request cycle. It has access to the request/response objects and the `next_fn()` function, which passes control to the next middleware (or the route handler).

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

Nestipy middleware supports dependency injection. Similar to providers and controllers, it can inject dependencies available in the same module.

### Order (NestJS-like)

Middleware executes in this order:

1. Global middleware (registered with `app.use`)
2. Module middleware (registered with `consumer.apply(...)`)

Order is preserved within each group based on registration order. If you register the same middleware twice and both match, it runs twice (no automatic de-duplication).

### Matching rules

Nestipy uses NestJS-style route patterns:

- Exact prefix matches: `"/cats"` matches `"/cats"` and `"/cats/123"`
- Parameters: `"/cats/:id"` matches `"/cats/123"`
- Wildcards: `"*"` or `"/*"` matches all paths

Excludes use the same matching rules and can optionally be scoped to HTTP methods.

### Applying middleware

Nestipy apply middleware like the way Nestjs use. Modules that include middleware have to implement the NestipyModule.

```python title='app_module.py'
from nestipy.dynamic_module import NestipyModule

from nestipy.common import Module
from nestipy.core import MiddlewareConsumer


@Module()
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(LoggerMiddleware).for_route("cats")

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
You can exclude by **path** or **path + method**:

```python title='app_module.py'
from nestipy.ioc import MiddlewareExclude

consumer.apply(LoggerMiddleware).for_route("/users").excludes([
    "/users/health",
    {"path": "/users/internal", "method": "GET"},
    MiddlewareExclude(path="/users/:id/secret", method=["POST"]),
])
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

### Method-specific middleware

```python
consumer.apply(LoggerMiddleware).for_route("/users", method=["GET", "POST"])
```

### Common patterns

- **Request logging:** global middleware
- **Auth header parsing:** module middleware on protected routes
- **Request timing:** global middleware or a specific module

Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-middleware)** for an  example.
