# Actions (RPC)

Actions are providers, so HTTP guards don’t apply. Use action guards:

```py
from nestipy.web import action, UseActionGuards, ActionGuard, ActionContext

class AuthGuard(ActionGuard):
    def can_activate(self, ctx: ActionContext) -> bool:
        return ctx.user is not None

class DemoActions:
    @UseActionGuards(AuthGuard)
    @action()
    async def hello(self, name: str) -> str:
        return f"Hello, {name}"
```

## Built-in Action Guards

- `OriginActionGuard` — allow-list Origin/Referer
- `CsrfActionGuard` — double-submit CSRF
- `ActionSignatureGuard` — HMAC + nonce
- `ActionPermissionGuard` — `@ActionPermissions`

Example:

```py
from nestipy.web import (
    ActionsModule,
    ActionsOption,
    OriginActionGuard,
    CsrfActionGuard,
    ActionSignatureGuard,
    ActionPermissionGuard,
)

module = ActionsModule.for_root(
    ActionsOption(
        guards=[
            OriginActionGuard(allowed_origins=["http://localhost:5173"]),
            CsrfActionGuard(),
            ActionSignatureGuard(secret="dev-secret"),
            ActionPermissionGuard(),
        ]
    )
)
```

### Recommended Dev Setup

- `OriginActionGuard` with your Vite origin
- `CsrfActionGuard` for browser calls

```py
from nestipy.web import ActionsModule, ActionsOption, OriginActionGuard, CsrfActionGuard

ActionsModule.for_root(
    ActionsOption(
        path="/_actions",
        guards=[
            OriginActionGuard(allowed_origins=["http://localhost:5173"]),
            CsrfActionGuard(),
        ],
    )
)
```

## CSRF Token Endpoint

`GET /_actions/csrf` returns a token and sets a `csrf_token` cookie.

```ts
import { fetchCsrfToken } from './actions.client';
await fetchCsrfToken();
```

## Using Actions in Python UI

Actions are generated into `web/src/actions.client.ts` and used at runtime in the browser. In Python UI, import `createActions` via `@js_import()` and call methods from the generated client:

```py
from nestipy.web import component, h, js_import
from app._generated.actions_types import ActionsClient

@js_import("../actions.client", "createActions")
def create_actions() -> ActionsClient: ...

@component
def Page():
    actions = create_actions()
    return h.button(
        "Ping",
        on_click=lambda: actions.UserActions.hello({"name": "Nestipy"}),
        class_name="btn",
    )
```

`app/_generated/actions_types.py` is generated automatically when you run `web:dev --actions`
or `web:actions --actions-types ...`.

The compiler emits TS that calls the generated client. The Python code is compile‑time only.

### Auto‑Generation

- Run `nestipy run web:actions` to generate `web/src/actions.client.ts` from a running backend.
- In dev, enable auto refresh with `--actions` and `NESTIPY_WEB_ACTIONS_WATCH=./src` so the schema is only refetched when backend files change.

## Security Presets (Env + CLI)

You can enable default guard presets with environment variables:

- `NESTIPY_ACTION_SECURITY=1`
- `NESTIPY_ACTION_ALLOWED_ORIGINS=http://localhost:5173`
- `NESTIPY_ACTION_ALLOW_MISSING_ORIGIN=1`
- `NESTIPY_ACTION_CSRF=1`
- `NESTIPY_ACTION_SIGNATURE_SECRET=...`
- `NESTIPY_ACTION_PERMISSIONS=1`

CLI shortcut:

```
nestipy start --dev --action-security --action-origins "http://localhost:5173" --action-csrf
```

## ActionAuth Convenience Decorator

```py
from nestipy.web import ActionAuth, ActionPermissionGuard, action

class AppActions:
    @ActionAuth("hello:read", guards=[ActionPermissionGuard])
    @action()
    async def hello(self, name: str) -> str:
        return f"Hello {name}"
```
