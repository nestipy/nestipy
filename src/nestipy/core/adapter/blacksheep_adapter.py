from typing import Optional, Callable

from blacksheep import (
    Application,
    Response as BlackSheepResponse,
    Request as BlackSheepRequest,
)
try:
    from blacksheep.server.routing import Router  # type: ignore
except Exception:
    Router = None
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

from nestipy.types_ import CallableHandler, WebsocketHandler, MountHandler
from .http_adapter import HttpAdapter
from nestipy.common.http_ import Response, Websocket
from nestipy.core.security.cors import CorsOptions, resolve_cors_options


class BlackSheepAdapter(HttpAdapter):
    def __init__(self):
        if Router is None:
            self.instance = Application()
        else:
            try:
                self.instance = Application(router=Router())
            except TypeError:
                self.instance = Application()
        self.instance.on_start(self.on_startup)
        self.instance.on_stop(self.on_shutdown)
        self._cors_enabled = False

    async def start(self):
        await self.instance.start()

    def get_instance(self) -> Application:
        return self.instance

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self, options: CorsOptions | None = None) -> None:
        if self._cors_enabled or getattr(self.instance, "_cors_strategy", None) is not None:
            return
        self._cors_enabled = True
        if options is None:
            options = CorsOptions.from_env()
        else:
            options = resolve_cors_options(options)
        if options is None:
            return
        allow_origins = options.allow_origins
        if options.allow_all or "*" in allow_origins:
            allow_origins = ["*"]
        origins_value = " ".join(allow_origins)
        self.instance.use_cors(
            allow_methods=" ".join(options.allow_methods),
            allow_origins=origins_value,
            allow_headers=" ".join(options.allow_headers),
            max_age=options.max_age or 300,
        )


    def create_wichard(self, prefix: str = "/", name: str = "full_path") -> str:
        prefix = prefix.strip("/")
        base = "/" + prefix if prefix else ""
        return base + "/{path:" + name + "}"

    def use(self, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        # need to transform
        self.instance.middlewares.append(callback)

    def static(
        self, route: str, directory: str, name: str = None, option: dict = None
    ) -> None:
        # self.instance.serve_files()
        pass

    def get(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "GET", route, self._create_blacksheep_handler(callback, metadata)
        )

    def post(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "POST", route, self._create_blacksheep_handler(callback, metadata)
        )

    def put(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "PUT", route, self._create_blacksheep_handler(callback, metadata)
        )

    def delete(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "DELETE", route, self._create_blacksheep_handler(callback, metadata)
        )

    def options(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        if self._is_wildcard_route(route):
            return
        self.instance.router.add(
            "OPTIONS", route, self._create_blacksheep_handler(callback, metadata)
        )

    def head(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "HEAD", route, self._create_blacksheep_handler(callback, metadata)
        )

    def patch(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.add(
            "PATCH", route, self._create_blacksheep_handler(callback, metadata)
        )

    def all(
        self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None
    ) -> None:
        handler = self._create_blacksheep_handler(callback, metadata)
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
        if self._is_wildcard_route(route):
            methods = [m for m in methods if m != "OPTIONS"]
        for method in methods:
            self.instance.router.add(method, route, handler)

    @staticmethod
    def _is_wildcard_route(route: str) -> bool:
        return "*" in route or "{path:" in route

    def ws(
        self, route: str, callback: WebsocketHandler, metadata: Optional[dict] = None
    ) -> None:
        self.instance.router.ws(route)(
            self._create_blacksheep_websocket_handler(callback, metadata)
        )

    def mount(self, route: str, callback: MountHandler) -> None:
        self.instance.mount(route, callback)

    def _create_blacksheep_handler(
        self, callback: CallableHandler, metadata: Optional[dict] = None
    ):
        # path = metadata['path']
        # params = RouteParamsExtractor.extract_params(path)
        async def blacksheep_handler(
            _bs_request: BlackSheepRequest,
        ) -> BlackSheepResponse:
            result: Response = await self.process_callback(callback, metadata)
            if result.is_stream():
                return BlackSheepResponse(
                    content=StreamedContent(
                        content_type=result.content_type().encode(),
                        data_provider=result.stream_content,
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
        self, callback: WebsocketHandler, _metadata: Optional[dict] = None
    ):
        async def blacksheep_websocket_handler(bsw: BSWebSocket):
            ws = Websocket(self.scope, self.receive, self.send)
            return await callback(ws)

        return blacksheep_websocket_handler
