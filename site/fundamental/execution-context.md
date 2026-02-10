The `ExecutionContext` gives guards, interceptors, filters, and pipes a unified view of the current request. It provides access to the handler, controller class, and transport-specific arguments, and lets you switch between HTTP, RPC, WebSocket, and GraphQL contexts.

## Why It Matters

In Nestipy, the same guard or interceptor can be applied to HTTP, RPC, or WebSocket handlers. The execution context is the bridge that lets you read the correct request data for each transport.

## Common Accessors

- `get_handler()` returns the route handler function.
- `get_class()` returns the controller class.
- `get_args()` returns `(controller_class, handler, request, response)` for HTTP.
- `switch_to_http()` returns an `HttpArgumentHost`.
- `switch_to_rpc()` returns an `RpcArgumentHost`.
- `switch_to_websocket()` returns a `WebsocketArgumentHost`.
- `switch_to_graphql()` returns a `GraphqlArgumentHost`.

## HTTP Example

```python
from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class AuthGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> bool:
        req = context.switch_to_http().get_request()
        return req.headers.get("authorization") is not None
```

## RPC Example

```python
from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class RpcGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> bool:
        data = context.switch_to_rpc().get_data()
        return data is not None
```

## WebSocket Example

```python
from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class WsGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> bool:
        client = context.switch_to_websocket().get_client()
        return client is not None
```

## GraphQL Example

```python
from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class GqlGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> bool:
        gql = context.switch_to_graphql()
        return gql.get_context() is not None
```

## Tips

- Use `get_handler()` and `get_class()` to read metadata set by decorators.
- Use transport-specific hosts to read request data safely.
- Guards and interceptors should avoid transport-specific imports when possible.
