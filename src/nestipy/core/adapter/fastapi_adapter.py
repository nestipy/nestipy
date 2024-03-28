import typing

from fastapi import Response as FResponse, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from .http_adapter import HttpAdapter
from ...common import Response
from ...types_ import CallableHandler, MountHandler, WebsocketHandler


class FastApiAdapter(HttpAdapter):
    def __init__(self):
        self.instance = FastAPI(
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            openapi_url=None
        )

    def get_instance(self) -> any:
        return self.instance

    def use(self, callback: CallableHandler, metadata: dict) -> None:
        pass

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
        pass

    def close(self) -> None:
        pass

    def enable(self, args, *kwargs) -> None:
        pass

    def disable(self, args, *kwargs) -> None:
        pass

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self) -> None:
        self.instance.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
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
            return FResponse(
                content=getattr(result, '_content', ''),
                headers={k: v for k, v in getattr(result, '_headers', [])},
                status_code=getattr(result, '_status_code', 200)
            )

        return fastapi_handler
