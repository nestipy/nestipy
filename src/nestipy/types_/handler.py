from typing import Callable, Awaitable

from nestipy.common.http_ import Request, Response, Websocket

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]

HandlerResult = Response | JsonValue | None
NextFn = Callable[..., Awaitable[HandlerResult]]

CallableHandler = Callable[
    [Request, Response, NextFn], Awaitable[HandlerResult] | HandlerResult
]

WebsocketHandler = Callable[[Websocket], Awaitable[HandlerResult] | HandlerResult]

MountHandler = Callable[[dict, Callable, Callable], Awaitable[HandlerResult] | HandlerResult]
