Interceptors wrap handler execution. They can transform responses, handle errors, or implement cross-cutting concerns like logging, caching, or metrics. Interceptors run after guards and pipes, and they can run logic both before and after the handler.

## Basic Interceptor

```python
from nestipy.common import Injectable, NestipyInterceptor
from nestipy.core import ExecutionContext
from nestipy.types_ import NextFn


@Injectable()
class LoggingInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        print("Before handler")
        result = await next_fn()
        print("After handler")
        return result
```

## Response Mapping Example

```python
from nestipy.common import Injectable, NestipyInterceptor
from nestipy.core import ExecutionContext
from nestipy.types_ import NextFn


@Injectable()
class WrapResponseInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        data = await next_fn()
        return {"data": data, "meta": {"ok": True}}
```

## Apply Interceptors

Interceptors can be applied at the controller, method, module, or global level.

```python
from nestipy.common import Controller, Post, UseInterceptors, Module, ModuleProviderDict
from nestipy.core import AppKey


@UseInterceptors(LoggingInterceptor)
@Controller("cats")
class CatsController:
    @UseInterceptors(LoggingInterceptor)
    @Post()
    async def create(self):
        pass


@Module(
    controllers=[CatsController],
    providers=[
        ModuleProviderDict(token=AppKey.APP_INTERCEPTOR, use_class=LoggingInterceptor)
    ],
)
class AppModule:
    pass
```

Global usage:

```python
from nestipy.core import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use_global_interceptors(LoggingInterceptor)
```

## Tips

- Always call `next_fn()` to allow handler execution unless you intentionally short-circuit.
- Interceptors are ideal for shaping response format consistently.
- Keep interceptors stateless or use request scope for per-request state.
