
from blacksheep import (
    Application,
    Response as BlackSheepResponse,
    Request as BlackSheepRequest,
)
from blacksheep import (
    get,
    put,
    post,
    patch,
    head,
    options,
    delete,
    route as all_route,
    Content,
    ws as websocket,
    WebSocket as BSWebSocket,
    StreamedContent,
)

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

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self) -> None:
        self.instance.use_cors(
            allow_methods="GET POST PUT DELETE OPTIONS",
            allow_origins="*",
            allow_headers="Content-Type",
            max_age=300,
        )

    def create_wichard(self, prefix: str = "/", name: str = "full_path") -> str:
        return f"/{prefix.strip('/')}" + "/{" + f"path:{name}" + "}"

    def use(self, callback: CallableHandler, metadata: dict) -> None:
        # need to transform
        self.instance.middlewares.append(callback)

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

    def _create_blacksheep_handler(self, callback: CallableHandler, _metadata: dict):
        # path = metadata['path']
        # params = RouteParamsExtractor.extract_params(path)
        async def blacksheep_handler(
            _bs_request: BlackSheepRequest,
        ) -> BlackSheepResponse:
            req, res, next_fn = self.create_handler_parameter()
            result: Response = await callback(req, res, next_fn)
            if result.is_stream():
                return BlackSheepResponse(
                    content=StreamedContent(
                        content_type=result.content_type().encode(),
                        data_provider=result.get_stream,
                    ),
                    headers=[(k.encode(), v.encode()) for k, v in result.headers()],
                    status=result.status_code() or 200,
                )
            return BlackSheepResponse(
                content=Content(
                    data=result.content(), content_type=result.content_type().encode()
                ),
                headers=[(k.encode(), v.encode()) for k, v in result.headers()],
                status=result.status_code() or 200,
            )

        return blacksheep_handler

    def _create_blacksheep_websocket_handler(
        self, callback: WebsocketHandler, metadata: dict
    ):
        async def blacksheep_websocket_handler(bsw: BSWebSocket):
            wbs = self.create_websocket_parameter()
            return await callback(wbs)

        return blacksheep_websocket_handler
