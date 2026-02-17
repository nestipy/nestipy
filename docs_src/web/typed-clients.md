# Typed Clients

## Actions Client

```ts
import { createActions } from './actions.client';
const actions = createActions();
```

Call actions:

```ts
const res = await actions.UserActions.hello({ name: 'Nestipy' });
```

### Python UI Usage (actions)

```py
from nestipy.web import component, h, js_import, use_effect, use_state
from app._generated.actions_types import ActionsClient

@js_import("../actions.client", "createActions")
def create_actions() -> ActionsClient: ...

@component
def Page():
    value, set_value = use_state("Loading...")
    actions = create_actions()

    use_effect(
        lambda: actions.UserActions.hello({"name": "Nestipy"}).then(
            lambda res: set_value(res.data if res.ok else "Error")
        ),
        deps=[],
    )

    return h.div(h.p(value))
```

## API Client

```ts
import { createApiClient } from './api/client';
const api = createApiClient();
```

Call HTTP endpoints:

```ts
const res = await api.UserController.health();
```

> Methods are grouped by controller class name.

### Python UI Usage (API)

```py
from nestipy.web import component, h, js_import, use_effect, use_state
from app._generated.api_types import ApiClient

@js_import("../api/client", "createApiClient")
def create_api_client() -> ApiClient: ...

@component
def Page():
    ping, set_ping = use_state("Loading...")
    api = create_api_client()

    use_effect(lambda: api.UserController.health().then(lambda res: set_ping(res)), deps=[])

    return h.div(h.p(ping))
```

`app/_generated/api_types.py` is generated when the router spec is available (`web:dev --router-spec ...` or `web:codegen --router-types ...`).

## Codegen

Generate actions client:

```bash
nestipy run web:actions --spec http://127.0.0.1:8001/_actions/schema \
  --output web/src/actions.client.ts
```

Generate API client from router spec:

```bash
nestipy run web:codegen --spec http://127.0.0.1:8001/_router/spec \
  --output web/src/api/client.ts --lang ts
```
