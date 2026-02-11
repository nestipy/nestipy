# Typed Client

Nestipy can build a typed HTTP client directly from your controllers. This mirrors the “router‑based client” flow you get in frameworks like Hono or tRPC, but stays fully HTTP.

## Generate From App

```python
from nestipy.core import NestipyFactory
from app_module import AppModule

app = NestipyFactory.create(AppModule)

# Generate a sync client
app.generate_typed_client("clients/api_client.py", class_name="ApiClient")

# Generate an async client
app.generate_typed_client(
    "clients/api_client_async.py",
    class_name="ApiClientAsync",
    async_client=True,
)
```

The generator reads:
- Controller route metadata
- HTTP method + path
- Parameter sources (`Param`, `Query`, `Body`, `Header`)
- Return annotations (for type hints)

## Generate From Router Spec

```python
from nestipy.router import build_router_spec, write_client_file, write_typescript_client_file
from app_module import AppModule

spec = build_router_spec([AppModule], prefix="/api")
write_client_file(spec, "clients/api_client.py", class_name="ApiClient")
write_typescript_client_file(spec, "clients/api_client.ts", class_name="ApiClient")
```

## Client Usage

```python
from clients.api_client import ApiClient

client = ApiClient(base_url="http://localhost:8001")
cat = client.get_cat(1, q="tom")
client.close()
```

Notes:
- Query/body/header values set to `None` are skipped.
- `Body` values support dicts, dataclasses, and Pydantic models.
- The generated client can use `httpx`, `requests`, or any client that exposes `.request(...)`.

## Dynamic HTTP Clients

You can inject any HTTP implementation:

```python
import requests
from clients.api_client import ApiClient

session = requests.Session()
client = ApiClient(base_url="http://localhost:8001", client=session)
```

Or pass a custom request function:

```python
def request(method, url, **kwargs):
    ...

client = ApiClient(base_url="http://localhost:8001", request=request)
```

## TypeScript Client

```python
from nestipy.core import NestipyFactory
from app_module import AppModule

app = NestipyFactory.create(AppModule)
app.generate_typescript_client("clients/api_client.ts", class_name="ApiClient")
```

The generated client uses `fetch` by default and accepts a custom fetcher.

## Router Spec Endpoint (Optional)

Expose the RouterSpec JSON only when explicitly enabled:

```python
from nestipy.core import NestipyFactory, NestipyConfig

app = NestipyFactory.create(
    AppModule,
    config=NestipyConfig(router_spec_enabled=True),
)
```

By default the endpoint is disabled.

You can also protect it with a token:

```python
config = NestipyConfig(
    router_spec_enabled=True,
    router_spec_token="secret",
)
```

The endpoint defaults to `/_router/spec` and accepts the token via:
- `x-router-spec-token` header
- `?token=...` query param

You can override the path with `router_spec_path="/internal/router-spec"`.

## CLI Codegen (Optional)

Enable codegen explicitly via the commander entrypoint:

```python
import asyncio
import sys
from nestipy.commander import CommandFactory
from app_module import AppModule

if __name__ == "__main__":
    command = CommandFactory.create(AppModule)
    asyncio.run(command.run(sys.argv[1], tuple(sys.argv[2:])))
```

Then run:

```bash
NESTIPY_ROUTER_SPEC=1 python cli.py codegen:client --output clients/api_client.py
```

Generate TypeScript:

```bash
NESTIPY_ROUTER_SPEC=1 python cli.py codegen:client --output clients/api_client.ts --lang ts
```
