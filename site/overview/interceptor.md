In simpler terms, Nestipy offers Interceptor functionality, which functions similarly to how Interceptors work in
NestJs, allowing you to intercept requests.
Nestipy Interceptor must be a class that extends `NestipyInterceptor`.

```python
from nestipy.common import Injectable
from nestipy.common import NestipyInterceptor
from nestipy.core import ExecutionContext
from nestipy.types_ import NextFn


@Injectable()
class TestInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        print('Intercepted...')
        return await next_fn()
```

### Apply interceptors

Interceptors can be applied to controllers, specific controller methods, within modules via providers, or even globally
across the application.

```python


from nestipy.common import Controller, Post, UseInterceptors, Module, ModuleProviderDict
from nestipy.core import AppKey


@UseInterceptors(TestInterceptor)
@Controller('cats')
class CatsController:

    @UseInterceptors(TestInterceptor)
    @Post()
    async def create(self):
        pass


@Module(
    controllers=[
        CatsController
    ],
    providers=[
        ModuleProviderDict(token=AppKey.APP_INTERCEPTOR, use_class=TestInterceptor)
    ]
)
class AppModule:
    pass

```

Globally , it works like.

```python
from nestipy.core import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use_global_interceptors(TestInterceptor)
```
Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-interceptors)** for an  example.








