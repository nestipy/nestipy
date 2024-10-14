from typing import Callable

import uvicorn

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
    uvicorn.run("test:app", reload=True)
