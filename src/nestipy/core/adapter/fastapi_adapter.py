import typing

from fastapi import Response as FResponse, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse as FStreamingResponse
from starlette.middleware import _MiddlewareFactory
from starlette.types import ASGIApp

from nestipy.common.http_ import Response
from nestipy.types_ import CallableHandler, MountHandler, WebsocketHandler
from .http_adapter import HttpAdapter


class FastApiAdapter(HttpAdapter):
    def __init__(self):
        self.instance = FastAPI(
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            openapi_url=None,
        )

    def get_instance(self) -> any:
        return self.instance

    def create_wichard(self, prefix: str = "/", name: str = "full_path") -> str:
        return f"/{prefix.strip('/')}" + "/{" + f"{name}:path" + "}"

    def use(self, callback: CallableHandler, metadata: dict) -> None:
        # need to transform if we use middleware from here
        self.instance.middleware("http")

    def get(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.get(route)(self._create_fastapi_handler(callback, metadata))

    def post(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.post(route)(self._create_fastapi_handler(callback, metadata))

    def ws(self, route: str, callback: WebsocketHandler, metadata: dict) -> None:
        pass

    def mount(self, route: str, callback: MountHandler) -> None:
        self.instance.mount(route, typing.cast(ASGIApp, callback))

    def put(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.put(route)(self._create_fastapi_handler(callback, metadata))

    def delete(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.delete(route)(self._create_fastapi_handler(callback, metadata))

    def patch(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.patch(route)(self._create_fastapi_handler(callback, metadata))

    def options(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.options(route)(self._create_fastapi_handler(callback, metadata))

    def head(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        self.instance.head(route)(self._create_fastapi_handler(callback, metadata))

    def all(self, route: str, callback: CallableHandler, metadata: dict) -> None:
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
            typing.cast(_MiddlewareFactory[typing.Any], CORSMiddleware),
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _create_fastapi_handler(self, callback: CallableHandler, metadata: dict):
        # path = metadata['path']
        # params = RouteParamsExtractor.extract_params(path)
        async def fastapi_handler() -> FResponse:
            req, res, next_fn = self.create_handler_parameter()
            result: Response = await callback(req, res, next_fn)
            if result.is_stream():
                return FStreamingResponse(
                    content=result.get_stream(),
                    headers={k: v for k, v in result.headers()},
                    status_code=result.status_code() or 200,
                )
            return FResponse(
                content=result.content(),
                headers={k: v for k, v in result.headers()},
                status_code=result.status_code() or 200,
            )

        return fastapi_handler
