from typing import Callable, Awaitable, Any, Union

from nestipy.common.http_ import Request, Response, Websocket

NextFn = Callable[..., Union[Awaitable[Any]]]

CallableHandler = Callable[
    [Request, Response, NextFn], Union[Awaitable[Response], Response, str, dict, list]
]

WebsocketHandler = Callable[[Websocket], Any]

MountHandler = Callable[[dict, Callable, Callable], Any]
