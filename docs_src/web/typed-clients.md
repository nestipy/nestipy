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
from nestipy.web import component, h, external_fn, use_effect, use_state

create_actions = external_fn("../actions.client", "createActions", alias="createActions")

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
from nestipy.web import component, h, external_fn, use_effect, use_state

create_api_client = external_fn("../api/client", "createApiClient", alias="createApiClient")

@component
def Page():
    ping, set_ping = use_state("Loading...")
    api = create_api_client()

    use_effect(lambda: api.UserController.health().then(lambda res: set_ping(res)), deps=[])

    return h.div(h.p(ping))
```

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
