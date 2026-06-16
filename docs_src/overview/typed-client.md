# Typed Client

Nestipy builds a typed **TypeScript** HTTP client directly from your controllers, so a
JS/TS frontend (Inertia, React, Vue, Svelte, anything) can call your API with full typing.
This mirrors the “router-based client” flow you get in frameworks like Hono or tRPC, but
stays plain HTTP. A Python client generator is also available (see the end of this page).

## CLI: `client:gen`

The quickest way — generate a `.ts` client straight from your modules:

```bash
nestipy run client:gen --output clients/api_client.ts --class ApiClient
```

Or from a running server's router-spec endpoint:

```bash
nestipy run client:gen --spec http://127.0.0.1:8000/_router/spec --output clients/api_client.ts
```

Flags: `--output/-o` (required), `--class`/`--name` (client class name), `--prefix`
(route prefix), `--spec`/`--url` (generate from a spec endpoint instead of local modules).

The `client:gen` command is wired through the commander entrypoint:

```python
import asyncio
import sys
from nestipy.commander import CommandFactory
from app_module import AppModule

if __name__ == "__main__":
    command = CommandFactory.create(AppModule)
    asyncio.run(command.run(sys.argv[1], tuple(sys.argv[2:])))
```

```bash
python cli.py client:gen --output clients/api_client.ts
```

## Programmatic generation

From the `nestipy.client` facade:

```python
from nestipy.client import generate_client, generate_client_from_url
from app_module import AppModule

generate_client([AppModule], "clients/api_client.ts", class_name="ApiClient", prefix="/api")

# or from a running server's spec endpoint
generate_client_from_url(
    "http://127.0.0.1:8000/_router/spec",
    "clients/api_client.ts",
    class_name="ApiClient",
)
```

From the app instance:

```python
from nestipy.core import NestipyFactory
from app_module import AppModule

app = NestipyFactory.create(AppModule)
app.generate_typescript_client("clients/api_client.ts", class_name="ApiClient")
```

The generator reads controller route metadata: HTTP method + path, parameter sources
(`Param`, `Query`, `Body`, `Header`), and return annotations for type hints.

## Using the generated client

```ts
import { createApiClient } from "./api_client"

const api = createApiClient({ baseUrl: "http://localhost:8001" })

// methods grouped by controller, fully typed
const cat = await api.CatsController.getCat(1, { query: { q: "tom" } })
```

- Uses `fetch` by default; pass a custom fetcher to `createApiClient`.
- Inputs are grouped into a single `options` object with `query`, `headers`, `body`, `cookies`.
- Path params are positional arguments.

## Router spec endpoint (optional)

Expose the RouterSpec JSON only when explicitly enabled — useful for `--spec` generation:

```python
from nestipy.core import NestipyFactory, NestipyConfig

app = NestipyFactory.create(
    AppModule,
    config=NestipyConfig(router_spec_enabled=True, router_spec_token="secret"),
)
```

The endpoint defaults to `/_router/spec` and accepts the token via the
`x-router-spec-token` header or `?token=...` query param. Override the path with
`router_spec_path="/internal/router-spec"`.

## Python client (optional)

The same router spec can emit a typed **Python** client:

```python
from nestipy.router import build_router_spec, write_client_file

spec = build_router_spec([AppModule], prefix="/api")
write_client_file(spec, "clients/api_client.py", class_name="ApiClient")
```

```python
from clients.api_client import ApiClient

client = ApiClient(base_url="http://localhost:8001")
cat = client.get_cat(1, query={"q": "tom"})
client.close()
```

The generated Python client works with `httpx`, `requests`, or any object exposing
`.request(...)`; pass `client=` or a custom `request=` function to inject it.
