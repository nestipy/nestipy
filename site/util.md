#### Config static dir, based view, lifecycle hook, cors

```python
import os

from nestipy.core import NestipyFactory
from nestipy.common import session

app = NestipyFactory.create(AppModule)

# Enable cors
app.enable_cors()

# define static folder
app.use_static_assets(os.path.join(os.path.dirname(__file__), 'public'))

# Config view for template rendering
app.set_base_view_dir(os.path.join(os.path.dirname(__file__), 'views'))
app.set_view_engine('minijinja')  # minijinja as template engine.

template_engine = app.get_template_engine()  # get template engine

# use session
app.use(session())

# LIFECYCLE HOOKS 

@app.on_startup
async def on_startup_callback():
    print('Starting ...')


@app.on_shutdown
async def on_shutdown_callback():
    print('Shutdown ...')
```

Render template

```python
from nestipy.common import Get, Response, Request, Render
from nestipy.types_ import Req, Res


class AppController:

    @Render('index.html')
    @Get()
    async def test(self, req: Req[Request], res: Res[Response]):
        return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})
```