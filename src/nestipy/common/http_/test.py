from typing import Callable

from granian import Granian
from granian.constants import Interfaces

from request import Request
from response import Response


async def app(scope: dict, receive: Callable, send: Callable):
    if scope.get("type") == "http":
        request = Request(scope, receive, send)
        json = await request.json()
        print(request.query_params, json)
        res = Response()
        await res.status(200).json({"test": "test"})


if __name__ == "__main__":
    granian = Granian(
        target="test:app",
        host="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
    )
    granian.serve()
