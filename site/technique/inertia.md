Nestipy provides package adapter for using InertiaJS.

### Installation

```bash
pip install nestipy_inertia
```
### Usage
`main.py`
```python
  import os

import uvicorn
from nestipy.core import NestipyFactory
from nestipy.common import session
from app_module import AppModule, inertia_config
from nestipy_inertia import inertia_head, inertia_body, vite_react_refresh

app = NestipyFactory.create(AppModule)

# set view engine mini jinja and
app.set_base_view_dir(os.path.join(os.path.dirname(__file__), "views"))

# app.use_static_assets()
env = app.get_template_engine().get_env()
env.add_function("inertiaHead", inertia_head)
env.add_function("inertiaBody", inertia_body)

# When using react
env.add_function("viteReactRefresh", vite_react_refresh)
# Inertia config

front_dir = (
    os.path.join(os.path.dirname(__file__), "inertia", "dist")
    if inertia_config.environment != "development" or inertia_config.ssr_enabled is True
    else os.path.join(os.path.dirname(__file__), "inertia", "src")
)

app.use_static_assets(front_dir, "/dist")
app.use_static_assets(os.path.join(front_dir, "assets"), "/assets")
app.use(session())

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)


```
`app_module.py`
```python
import os

from nestipy.common import Module

from app_controller import AppController
from app_service import AppService
from nestipy_inertia import InertiaModule, InertiaConfig

inertia_config = InertiaConfig(
    manifest_json_path=os.path.join(
        os.path.dirname(__file__), "inertia", "dist", "manifest.json"
    ),
    environment="development",
    use_flash_messages=True,
    use_flash_errors=True,
    entrypoint_filename="main.tsx",
    ssr_enabled=False,
    assets_prefix="/dist",
)


@Module(
    imports=[
        InertiaModule.register(
            inertia_config
        )
    ],
    controllers=[AppController],
    providers=[
        AppService,
    ]
)
class AppModule:
    ...

```

`vite.config.ts`
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import nestipyVite from "./nestipy.inertia";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        nestipyVite({
            entry: './src/main.tsx',
            ssr: './src/ssr.tsx'
        }),
    ],
})

```

`nestipy.inertia.ts`
```ts
import { PluginOption } from "vite";

type Input = {
    entry: string,
    ssr?: string,
    manifest?: string
}
type NestipyPlugin = (options: Input) => PluginOption
const nestipyVite: NestipyPlugin = ({entry, ssr, manifest = "manifest.json"}) => {
    return {
        name: "nestipy-vite-plugin",
        config: (config, env) => {
            return {
                ...config,
                build: {
                    manifest: env.isSsrBuild ? false: manifest,
                    outDir: env.isSsrBuild ? "dist/ssr" : "dist",
                    rollupOptions: {
                        input: env.isSsrBuild && ssr ? ssr : entry,
                    },
                },
                ssr: {
                    noExternal: ['@inertiajs/server']
                }
            }
        }
    }
}

export default nestipyVite

```

`views/index.html`
```html
<!Doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <link rel="icon" type="image/svg+xml" href="/vite.svg"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Nestipy + Vite + React + TS + Inertia + Mini jinja</title>
    {{ inertiaHead() }}
</head>
<body>
{{ viteReactRefresh() }}
{{ inertiaBody() }}
</body>
</html>

```
`app_controller.py`
```python
from typing import Annotated

from nestipy.common import Controller, Get, Response, Post
from nestipy.ioc import Inject, Res, Body
from pydantic import BaseModel, EmailStr

from app_service import AppService
from nestipy_inertia import InertiaResponse
from nestipy_inertia import lazy


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @Get()
    async def get(self, res: Annotated[InertiaResponse, Res()]) -> Response:
        props = {
            "message": "hello from index",
            "lazy_prop": lazy(lambda: "hello from lazy prop"),
        }
        return await res.inertia.render("Index", props)

    @Get('/2')
    async def get2(self, res: Annotated[InertiaResponse, Res()]) -> Response:
        res.inertia.flash("hello from index2 (through flash)", category="message")
        return await res.redirect('/3')

    @Get('/3')
    async def get3(self, res: Annotated[InertiaResponse, Res()]) -> Response:
        res.inertia.flash("hello from index3 (through flash)", category="message")
        return await res.inertia.render("Other", {})

    @Post("/login")
    async def some_form(self, user: Annotated[UserLogin, Body()], res: Annotated[InertiaResponse, Res()]) -> Response:
        res.inertia.flash("form submitted", category="message")
        return await res.inertia.back()

```
Viw full exapmle code [here](https://github.com/nestipy/inertia/tree/main/example).
