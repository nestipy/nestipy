# Getting Started (End-to-End)

This walkthrough gives you a working backend + frontend using Nestipy Web.

## 1) Backend (actions + HTTP)

Project layout (backend in `src/`, web UI in `app/`, Vite output in `web/`):

```
main.py
pyproject.toml
src/
  __init__.py
  app_module.py
  user_actions.py
  user_controller.py
app/
  page.py
  layout.py
web/
```

`src/user_actions.py`:

```py
from nestipy.common import Injectable
from nestipy.web import action


@Injectable()
class UserActions:
    @action()
    async def hello(self, name: str) -> str:
        return f"Hello, {name}!"
```

`src/user_controller.py`:

```py
from nestipy.common import Controller, Get


@Controller("/api")
class UserController:
    @Get("/health")
    async def health(self) -> dict:
        return {"ok": True}
```

`src/app_module.py` (enable CSRF + allowed origins):

```py
from nestipy.common import Module
from nestipy.web import (
    ActionsModule,
    ActionsOption,
    OriginActionGuard,
    CsrfActionGuard,
)

from user_actions import UserActions
from user_controller import UserController


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[
                    OriginActionGuard(allowed_origins=["http://localhost:5173"]),
                    CsrfActionGuard(),
                ],
            )
        )
    ],
    providers=[UserActions],
    controllers=[UserController],
)
class AppModule:
    pass
```

`main.py`:

```py
from granian.constants import Interfaces
from nestipy.core import NestipyFactory
from src.app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == "__main__":
    # Optional router spec
    # export NESTIPY_ROUTER_SPEC=1
    # export NESTIPY_ROUTER_SPEC_TOKEN=secret
    app.listen(
        "main:app",
        host="127.0.0.1",
        port=8001,
        interface=Interfaces.ASGI,
        reload=True,
    )
```

Run backend:

```bash
python main.py
```

You now have:
- `POST /_actions` (RPC actions)
- `GET /_actions/schema` (actions schema)
- `GET /api/health` (HTTP example)
- `GET /_router/spec` (optional, when enabled)

## 2) Frontend (Python → TSX → Vite)

Initialize + run Vite with proxy:

```bash
nestipy run web:init
nestipy run web:dev --vite --install --proxy http://127.0.0.1:8001
```

Generate actions client + Python types (recommended):

```bash
nestipy run web:actions --spec http://127.0.0.1:8001/_actions/schema \
  --output web/src/actions.client.ts \
  --actions-types app/_generated/actions_types.py
```

Use actions in React/TS:

```ts
import { createActions } from './actions.client';

const actions = createActions();
const res = await actions.UserActions.hello({ name: 'Nestipy' });
if (res.ok) console.log(res.data);
```

Use actions from Python UI via `@js_import()`:

`app/page.py`:

```py
from nestipy.web import component, h, js_import, use_effect, use_state
from app._generated.actions_types import ActionsClient

@js_import("../actions.client", "createActions")
def create_actions() -> ActionsClient: ...

@component
def Page():
    value, set_value = use_state("")
    actions = create_actions()

    use_effect(
        lambda: actions.UserActions.hello({"name": "Nestipy"}).then(
            lambda res: set_value(res.data if res.ok else "Error")
        ),
        deps=[],
    )

    return h.div(
        h.h1("Nestipy Web"),
        h.p(value, class_name="text-sm"),
        class_name="p-8 space-y-3",
    )
```

### Optional: Typed HTTP Client

Generate the HTTP client from RouterSpec:

```bash
nestipy run web:codegen --spec http://127.0.0.1:8001/_router/spec \
  --output web/src/api/client.ts --lang ts
```

Use it in TS:

```ts
import { createApiClient } from './api/client';

const api = createApiClient();
const res = await api.UserController.health();
```
