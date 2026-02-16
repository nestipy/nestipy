import typing

from fastapi import Response as FResponse, FastAPI, WebSocket as FastAPIWebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse as FStreamingResponse
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp

from nestipy.common.http_ import Response, Websocket
from nestipy.types_ import CallableHandler, MountHandler, WebsocketHandler
from .http_adapter import HttpAdapter


class FastApiAdapter(HttpAdapter):
    """
    HTTP adapter for FastAPI.
    """

    def __init__(self):
        self.instance = FastAPI(
            lifespan=self.lifespan,
            openapi_url=None,
        )
        self.instance.redirect_slashes = False

    def get_instance(self) -> any:
        return self.instance

    def create_wichard(self, prefix: str = "/", name: str = "full_path") -> str:
        prefix = prefix.strip("/")
        return ("/" + prefix).rstrip("/") + "/{" + f"{name}:path" + "}"

    def use(
        self, callback: CallableHandler, metadata: typing.Optional[dict] = None
    ) -> None:
        # need to transform if we use middleware from here
        self.instance.middleware("http")

    def static(
        self, route: str, directory: str, name: str = None, option: dict = None
    ) -> None:
        self.instance.mount(
            route, StaticFiles(directory=directory, **(option or {})), name=name
        )

    def get(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.get(route)(self._create_fastapi_handler(callback, metadata))

    def post(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.post(route)(self._create_fastapi_handler(callback, metadata))

    def ws(
        self,
        route: str,
        callback: WebsocketHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.websocket(route)(
            self._create_fastapi_ws_handler(callback, metadata)
        )

    def mount(self, route: str, callback: MountHandler) -> None:
        self.instance.mount(route, typing.cast(ASGIApp, callback))

    def put(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.put(route)(self._create_fastapi_handler(callback, metadata))

    def delete(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.delete(route)(self._create_fastapi_handler(callback, metadata))

    def patch(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.patch(route)(self._create_fastapi_handler(callback, metadata))

    def options(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.options(route)(self._create_fastapi_handler(callback, metadata))

    def head(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.head(route)(self._create_fastapi_handler(callback, metadata))

    def all(
        self,
        route: str,
        callback: CallableHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        self.instance.get(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.post(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.put(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.patch(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.delete(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.head(route)(self._create_fastapi_handler(callback, metadata))
        self.instance.options(route)(self._create_fastapi_handler(callback, metadata))

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self) -> None:
        self.instance.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


    def _create_fastapi_handler(
        self, callback: CallableHandler, _metadata: typing.Optional[dict] = None
    ):
        async def fastapi_handler() -> FResponse:
            result: Response = await self.process_callback(callback, _metadata)
            if result.is_stream():
                return FStreamingResponse(
                    content=result.stream_content(),
                    headers={k: v for k, v in result.headers()},
                    status_code=result.status_code() or 200,
                )
            return FResponse(
                content=result.content(),
                headers={
                    k: v for k, v in typing.cast(set[tuple[str, str]], result.headers())
                },
                media_type=result.content_type(),
                status_code=result.status_code() or 200,
            )

        return fastapi_handler

    def _create_fastapi_ws_handler(
        self, callback: WebsocketHandler, _metadata: typing.Optional[dict] = None
    ):
        async def fastapi_ws_handler(ws: FastAPIWebSocket):
            websocket = Websocket(self.scope, self.receive, self.send)
            await callback(websocket)

        return fastapi_ws_handler
