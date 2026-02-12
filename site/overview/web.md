# Nestipy Web (Vite)

Nestipy Web lets you write frontend components in Python and compile them to TSX. The output is a standard React app that runs with Vite, so you can use any TypeScript/React library (shadcn/ui, Tailwind, Radix, etc.).

## Folder Structure

Nestipy Web is designed to live *inside the same repo as your backend* (monorepo-style). If your Python backend lives under `src/`, a typical layout looks like this:

```
main.py
cli.py
uv.lock
pyproject.toml
README.md
src/
  __init__.py
app_module.py
app_controller.py
app_service.py
web/                  # Vite project (generated / managed by Nestipy Web)
app/                  # Python UI sources (compiled to TSX)
  page.py
  layout.py
  components/
    card.py
```

The compiler reads Python UI from `app/` by default and writes the Vite project into `web/` by default.

If your UI code also lives under `src/` (e.g. `src/app/`), you can:
- run `nestipy run web:init --app-dir src/app`
- run `nestipy run web:dev --app-dir src/app --vite ...`

### UI-Only View

```
app/
  page.py              # /
  layout.py            # root layout
  actions.py           # RPC actions (optional)
  users/
    page.py            # /users
    [id]/
      page.py          # /users/:id
web/
  index.html
  src/
    main.tsx
    routes.tsx
    pages/...
```

## Routing Rules

- `app/page.py` maps to `/`
- `app/users/page.py` maps to `/users`
- `app/users/[id]/page.py` maps to `/users/:id`
- `app/blog/[...slug]/page.py` maps to `/*`

## Minimal Example

```py
from nestipy.web import component, h

@component
def Page():
    return h.div("Hello from Nestipy Web", class_name="p-6")
```

You can use any HTML tag as `h.tag`, and `class_name` is converted to `className`.

## Root Layout

Create `app/layout.py` to wrap all pages:

```py
from nestipy.web import component, h, Slot

@component
def Layout():
    return h.div(
        h.header("My App"),
        h(Slot),
        class_name="min-h-screen bg-slate-950 text-white",
    )
```

## External React Libraries

Use `external()` to import any TS/React library:

```py
from nestipy.web import component, h, external

Button = external("shadcn/ui/button", "Button")

@component
def Page():
    return h.div(
        Button("Save", variant="outline"),
        class_name="p-6",
    )
```

Use `external_fn()` for utility functions like `clsx`/`twMerge`:

```py
from nestipy.web import component, h, external_fn

clsx = external_fn("clsx", "clsx")

@component
def Page():
    return h.div(
        "Hello",
        class_name=clsx("base", True and "active"),
    )
```

## Props (Typed)

```py
from nestipy.web import component, props, h

@props
class CardProps:
    title: str
    active: bool = False

@component
def Card(props: CardProps):
    return h.div(h.h2(props.title), class_name="card")
```

## Control Flow (Pure Python)

Nestipy Web supports Python control flow in components (compiled to JS):

```py
from nestipy.web import component, h

@component
def Page():
    items = ["A", "B"]
    rows = []
    for item in items:
        rows.append(h.li(item))

    if items:
        message = h.p("Items found")
    else:
        message = h.p("No items")

    return h.div(h.ul(rows), message)
```

Multiple statements per branch are supported as long as each branch assigns the same variables:

```py
if show:
    label = "Shown"
    message = h.p(label)
else:
    label = "Hidden"
    message = h.p(label)
```

Nested loops are supported as long as each loop body appends to a list:

```py
rows = []
for group in groups:
    rows.append(h.h3(group["name"]))
    for item in group["items"]:
        rows.append(h.li(item))
```

You can also use list comprehensions and ternary expressions:

```py
return h.div(
    h.ul([h.li(item) for item in items if item]),
    h.p("Shown") if show else h.p("Hidden"),
)
```

### Control Flow Limits

- `for` loops must build UI by calling `list.append(...)`
- `if/elif/else` must either:
  - return in every branch, or
  - assign the same variable(s) in every branch
- `while`, `break`, `continue`, and `for/else` are not supported

## Commands (nestipy-cli)

- `nestipy run web:init` — create `app/` scaffold and initial Vite output
- `nestipy run web:init --no-build` — scaffold `app/` without generating `web/`
- `nestipy run web:build` — compile Python UI into `web/`
- `nestipy run web:dev` — watch `app/` and rebuild on changes
- `nestipy run web:dev --vite` — also start Vite dev server (HMR)
- `nestipy run web:dev --vite --install` — install frontend deps before starting Vite
- `nestipy run web:dev --vite --proxy http://127.0.0.1:8001` — start Vite with backend proxy
- `nestipy run web:dev --vite --backend "python main.py"` — start backend + frontend together
- `nestipy run web:dev --vite --backend "python main.py" --backend-cwd ./backend` — backend in another folder
- `nestipy run web:install` — install frontend dependencies
- `nestipy run web:add react` — add a frontend dependency
- `nestipy run web:add -D tailwindcss` — add a dev dependency
- `nestipy run web:add --peer react-dom` — add a peer dependency
- `nestipy run web:codegen --output web/src/api/client.ts --lang ts` — generate typed clients
- `nestipy run web:build --spec http://localhost:8001/_router/spec --lang ts` — build + generate client into `web/src/api/client.ts`
- `nestipy run web:actions --output web/src/actions.client.ts` — generate typed action wrappers
- `nestipy run web:build --actions` — build and generate `web/src/actions.client.ts`

### Defaults via Environment Variables

If you don’t want to pass backend flags every time, set:

- `NESTIPY_WEB_BACKEND` — default backend command for `web:dev`
- `NESTIPY_WEB_BACKEND_CWD` — default working directory for the backend command

## Vite Scaffold

If `web/` is empty, the build generates:

- `web/package.json`
- `web/vite.config.ts`
- `web/tsconfig.json`
- `web/src/main.tsx`
- `web/src/routes.tsx`
- `web/src/actions.ts` (RPC action client helper)
- `web/src/index.css` (Tailwind v4 via `@tailwindcss/vite`, no config file)

## Server Actions (RPC)

Nestipy Web supports a Next.js-like RPC action flow using a single endpoint.

## Full Working Example (Backend + Frontend)

This walkthrough gives you a working backend that exposes:
- HTTP routes (controllers)
- Server actions (single RPC endpoint at `/_actions`)
- Router spec (`/_router/spec`) for typed HTTP clients (optional)

### Backend

Example structure (backend under `src/`, frontend under `web/`):

```
main.py
cli.py
pyproject.toml
src/
  __init__.py
  app_module.py
  user_actions.py
  user_controller.py
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

    # Cache the result for 30 seconds (key defaults to args/kwargs).
    @action(cache=30)
    async def get_server_time(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
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

`src/app_module.py`:

```py
from nestipy.common import Module
from nestipy.web import ActionsModule, ActionsOption

from user_actions import UserActions
from user_controller import UserController


@Module(
    imports=[ActionsModule.for_root(ActionsOption(path="/_actions"))],
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
    # Optional: enable RouterSpec (for `/_router/spec`) and protect it with a token.
    # export NESTIPY_ROUTER_SPEC=1
    # export NESTIPY_ROUTER_SPEC_TOKEN=secret
    app.listen(
        "main:app",
        address="127.0.0.1",
        port=8001,
        interface=Interfaces.ASGI,
        reload=True,
    )
```

Run backend:

```bash
python main.py
```

Endpoints you now have:
- `POST /_actions` (RPC)
- `GET /_actions/schema` (schema for codegen)
- `GET /api/health` (HTTP example)
- `GET /_router/spec` (optional, enable with `NESTIPY_ROUTER_SPEC=1`; token via `NESTIPY_ROUTER_SPEC_TOKEN`)

### Frontend

Create/compile the frontend:

```bash
nestipy run web:init
nestipy run web:dev --vite --install --proxy http://127.0.0.1:8001
```

Generate typed server-action wrappers (recommended):

```bash
nestipy run web:actions --spec http://127.0.0.1:8001/_actions/schema --output web/src/actions.client.ts
```

Optional: generate typed HTTP client from RouterSpec:

```bash
# If you configured a token, pass it via query or header:
# - query:  /_router/spec?token=secret
# - header: x-router-spec-token: secret
nestipy run web:build --spec http://127.0.0.1:8001/_router/spec --lang ts --output web/src/api/client.ts
```

Now you can call actions from React/TS:

```ts
import { createActions } from './actions.client';

const actions = createActions();

const res = await actions.UserActions.hello({ name: 'Nestipy' });
if (res.ok) {
  console.log(res.data);
}
```

You can also wire a React component that calls actions and mount it from `app/page.py`:

`web/src/components/HelloAction.tsx`:

```ts
import React from 'react';
import { createActions } from '../actions.client';

const actions = createActions();

export function HelloAction() {
  const [value, setValue] = React.useState<string>('');

  React.useEffect(() => {
    actions.UserActions.hello({ name: 'Nestipy' }).then((res) => {
      if (res.ok) {
        setValue(res.data);
      }
    });
  }, []);

  return <div className="text-sm text-slate-300">Action says: {value}</div>;
}
```

`app/page.py`:

```py
from nestipy.web import component, h, external

HelloAction = external("../components/HelloAction", "HelloAction")

@component
def Page():
    return h.div(
        h.h1("Nestipy Web"),
        h(HelloAction),
        class_name="p-8 space-y-3",
    )
```

### Backend

```py
from nestipy.common import Module, Injectable
from nestipy.web import ActionsModule, ActionsOption, action

@Injectable()
class UserActions:
    @action()
    async def hello(self, name: str) -> str:
        return f"Hello, {name}!"

@Module(
    imports=[ActionsModule.for_root(ActionsOption(path="/_actions"))],
    providers=[UserActions],
)
class AppModule:
    pass
```

### Frontend (Vite)

```ts
import { createActionClient } from './actions';
import { createActions } from './actions.client';

const callAction = createActionClient();

const res = await callAction<string>('UserActions.hello', ['Nestipy']);
if (res.ok) {
  console.log(res.data);
}

const actions = createActions();
const res2 = await actions.UserActions.hello({ name: 'Nestipy' });
if (res2.ok) {
  console.log(res2.data);
}
```

## Hot Reload

Run both the Python compiler and Vite dev server:

```bash
nestipy run web:dev --vite
```

This watches `app/**/*.py`, rebuilds TSX on change, and Vite handles HMR.

## One Command (Backend + Frontend)

You can start both the backend and the frontend from a single Nestipy-CLI command:

```bash
nestipy run web:dev --vite --install --proxy http://127.0.0.1:8001 --backend "python main.py"
```

If your backend entrypoint is not at the repo root, pass a working directory:

```bash
nestipy run web:dev --vite --backend "python main.py" --backend-cwd ./backend
```

## Vite Proxy

If your Nestipy backend runs on another port, you can configure a Vite proxy so the frontend can call:
- `/_actions` (server actions)
- `/_router/spec` (router spec)
- `/_devtools/*` (optional)

```bash
nestipy run web:dev --vite --proxy http://127.0.0.1:8001
```

Customize proxied paths:

```bash
nestipy run web:dev --vite --proxy http://127.0.0.1:8001 --proxy-paths /_actions,/_router
```

Env vars:
- `NESTIPY_WEB_PROXY`
- `NESTIPY_WEB_PROXY_PATHS` (comma-separated)

## Actions Schema (For Codegen)

The actions endpoint exposes a schema:
- `GET /_actions/schema`

Generate `web/src/actions.client.ts` from a running app:

```bash
nestipy run web:actions --spec http://127.0.0.1:8001/_actions/schema --output web/src/actions.client.ts
```

## Notes

- Output is plain React + Vite and can be integrated with Tailwind or any React UI kit.
- Use `js("...")` only for raw JS snippets; most rendering can stay pure Python.
- Components must return a `h(...)` tree (no arbitrary Python execution in render).
- Nested components in the same file should be decorated with `@component` so the compiler emits them.
