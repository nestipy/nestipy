import importlib
import sys
import types

import pytest

from nestipy.common.http_ import Response


class FakeRouter:
    def __init__(self):
        self.calls = []
        self.ws_routes = {}

    def add(self, method, route, handler):
        self.calls.append((method, route, handler))

    def ws(self, route):
        def decorator(handler):
            self.ws_routes[route] = handler
            return handler

        return decorator


class FakeApplication:
    def __init__(self):
        self.router = FakeRouter()
        self.middlewares = []
        self.cors_args = None
        self.mounted = []
        self.on_start_callbacks = []
        self.on_stop_callbacks = []

    def on_start(self, cb):
        self.on_start_callbacks.append(cb)

    def on_stop(self, cb):
        self.on_stop_callbacks.append(cb)

    def use_cors(self, **kwargs):
        self.cors_args = kwargs

    def mount(self, route, callback):
        self.mounted.append((route, callback))

    async def start(self):
        return None


class FakeContent:
    def __init__(self, data=None, content_type=b""):
        self.data = data
        self.content_type = content_type


class FakeStreamedContent:
    def __init__(self, content_type=b"", data_provider=None):
        self.content_type = content_type
        self.data_provider = data_provider


class FakeResponse:
    def __init__(self, content=None, headers=None, status=200):
        self.content = content
        self.headers = headers or []
        self.status = status


class FakeRequest:
    pass


class FakeWebSocket:
    pass


def _install_fake_blacksheep(monkeypatch):
    fake = types.ModuleType("blacksheep")

    def route(*_args, **_kwargs):
        def decorator(handler):
            return handler

        return decorator

    def ws(*_args, **_kwargs):
        def decorator(handler):
            return handler

        return decorator

    fake.Application = FakeApplication
    fake.Response = FakeResponse
    fake.Request = FakeRequest
    fake.Content = FakeContent
    fake.StreamedContent = FakeStreamedContent
    fake.WebSocket = FakeWebSocket
    fake.route = route
    fake.ws = ws
    fake.get = route
    fake.put = route
    fake.post = route
    fake.patch = route
    fake.head = route
    fake.options = route
    fake.delete = route

    monkeypatch.setitem(sys.modules, "blacksheep", fake)
    return fake


@pytest.fixture()
def blacksheep_adapter_module(monkeypatch):
    fake = _install_fake_blacksheep(monkeypatch)
    sys.modules.pop("nestipy.core.adapter.blacksheep_adapter", None)
    module = importlib.import_module("nestipy.core.adapter.blacksheep_adapter")
    importlib.reload(module)
    try:
        yield module, fake
    finally:
        sys.modules.pop("nestipy.core.adapter.blacksheep_adapter", None)


def test_blacksheep_adapter_routes(blacksheep_adapter_module):
    module, _fake = blacksheep_adapter_module
    adapter = module.BlackSheepAdapter()

    def handler():
        return None

    adapter.get("/a", handler)
    adapter.post("/b", handler)
    adapter.put("/c", handler)
    adapter.delete("/d", handler)
    adapter.options("/e", handler)
    adapter.head("/f", handler)
    adapter.patch("/g", handler)

    methods = [call[0] for call in adapter.instance.router.calls]
    assert methods == ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


def test_blacksheep_adapter_all_routes(blacksheep_adapter_module):
    module, _fake = blacksheep_adapter_module
    adapter = module.BlackSheepAdapter()

    def handler():
        return None

    adapter.all("/all", handler)
    methods = [call[0] for call in adapter.instance.router.calls]
    assert methods == ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]


def test_blacksheep_adapter_helpers(blacksheep_adapter_module):
    module, _fake = blacksheep_adapter_module
    adapter = module.BlackSheepAdapter()

    def middleware():
        return None

    adapter.enable_cors()
    adapter.use(middleware)
    adapter.mount("/mount", middleware)

    assert adapter.instance.cors_args is not None
    assert adapter.instance.middlewares == [middleware]
    assert adapter.instance.mounted == [("/mount", middleware)]
    assert adapter.create_wichard("api", "full_path") == "/api/{path:full_path}"


@pytest.mark.asyncio
async def test_blacksheep_handler_builds_response(blacksheep_adapter_module):
    module, fake = blacksheep_adapter_module
    adapter = module.BlackSheepAdapter()

    async def fake_process_callback(_callback, _metadata=None):
        response = Response()
        response.header("X-Test", "1")
        await response.send("ok", status_code=201)
        return response

    adapter.process_callback = fake_process_callback
    handler = adapter._create_blacksheep_handler(lambda: None, None)
    result = await handler(fake.Request())

    assert isinstance(result, fake.Response)
    assert isinstance(result.content, fake.Content)
    assert result.status == 201
    assert (b"X-Test", b"1") in result.headers


@pytest.mark.asyncio
async def test_blacksheep_handler_streams_response(blacksheep_adapter_module):
    module, fake = blacksheep_adapter_module
    adapter = module.BlackSheepAdapter()

    async def fake_process_callback(_callback, _metadata=None):
        response = Response()

        async def stream():
            yield b"chunk"

        await response.stream(stream)
        return response

    adapter.process_callback = fake_process_callback
    handler = adapter._create_blacksheep_handler(lambda: None, None)
    result = await handler(fake.Request())

    assert isinstance(result, fake.Response)
    assert isinstance(result.content, fake.StreamedContent)
