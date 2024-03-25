import typing

from blacksheep import Application, Response as BlackSheepResponse
from blacksheep import get, put, post, patch, head, options, delete, route as all_route, Content, ws as websocket, \
    WebSocket as BSWebSocket

from nestipy.common.http_ import Response
from nestipy.types_ import CallableHandler, WebsocketHandler, MountHandler
from .http_adapter import HttpAdapter


class BlackSheepAdapter(HttpAdapter):

    def __init__(self):
        self.instance = Application()
        self.instance.on_start(self.on_startup)
        self.instance.on_stop(self.on_shutdown)

    def get_instance(self) -> Application:
        return self.instance

    def close(self) -> None:
        pass

    def enable(self, args, *kwargs) -> None:
        pass

    def disable(self, args, *kwargs) -> None:
        pass

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self) -> None:
        self.instance.use_cors(
            allow_methods="GET POST PUT DELETE OPTIONS",
            allow_origins="*",
            allow_headers="Content-Type",
            max_age=300,
        )

    def use(self, callback: CallableHandler, metadata: dict) -> None:
        # need to transform
        self.instance.middlewares.append(callback)

    @classmethod
    def get_tag(cls, metadata: dict) -> list:
        ctrl: typing.Type = metadata['controller']
        return [ctrl.__name__]

    def get(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        get(route)(self._create_blacksheep_handler(callback, metadata))

    def post(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        post(route)(self._create_blacksheep_handler(callback, metadata))

    def put(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        put(route)(self._create_blacksheep_handler(callback, metadata))

    def delete(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        delete(route)(self._create_blacksheep_handler(callback, metadata))

    def options(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        options(route)(self._create_blacksheep_handler(callback, metadata))

    def head(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        head(route)(self._create_blacksheep_handler(callback, metadata))

    def patch(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        patch(route)(self._create_blacksheep_handler(callback, metadata))

    def all(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        all_route(route)(self._create_blacksheep_handler(callback, metadata))

    def ws(self, route: str, callback: WebsocketHandler, metadata: dict) -> None:
        websocket(route)(self._create_blacksheep_websocket_handler(callback, metadata))

    def mount(self, route: str, callback: MountHandler) -> None:
        self.instance.mount(route, callback)

    def _create_blacksheep_handler(self, callback: CallableHandler, metadata: dict):
        # path = metadata['path']
        # params = RouteParamsExtractor.extract_params(path)
        async def blacksheep_handler() -> BlackSheepResponse:
            req, res, next_fn = self.create_handler_parameter()
            result: Response = await callback(req, res, next_fn)
            return BlackSheepResponse(
                content=Content(data=getattr(result, '_content', ''), content_type=result.content_type().encode()),
                headers=[(k.encode(), v.encode()) for k, v in getattr(result, '_headers', [])],
                status=getattr(result, '_status_code', 200)
            )

        return blacksheep_handler

    def _create_blacksheep_websocket_handler(self, callback: WebsocketHandler, metadata: dict):
        async def blacksheep_websocket_handler(bsw: BSWebSocket):
            wbs = self.create_websocket_parameter()
            return await callback(wbs)

        return blacksheep_websocket_handler
