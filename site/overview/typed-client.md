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
from nestipy.router import build_router_spec, write_client_file
from app_module import AppModule

spec = build_router_spec([AppModule], prefix="/api")
write_client_file(spec, "clients/api_client.py", class_name="ApiClient")
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
- The generated client uses `httpx`.
