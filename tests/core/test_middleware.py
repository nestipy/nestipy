import pytest

from collections import OrderedDict

from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.ioc import MiddlewareContainer, MiddlewareProxy, NestipyContainer


def _reset_middleware_container():
    container = MiddlewareContainer.get_instance()
    container._middlewares = []
    container._middleware_instances = {}
    container._registry_dirty = True
    container._registry = []
    container._match_cache = OrderedDict()


def _make_request(path: str, method: str = "GET"):
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"",
        "headers": [],
        "raw_path": path.encode(),
        "method": method,
        "server": ("localhost", 80),
        "scheme": "http",
    }
    return Request(scope, receive, send), Response()


@pytest.mark.asyncio
async def test_middleware_order_global_then_module():
    NestipyContainer.clear()
    _reset_middleware_container()
    order: list[str] = []
    container = MiddlewareContainer.get_instance()

    async def global_mw(_req, _res, next_fn):
        order.append("global")
        return await next_fn()

    async def module_mw(_req, _res, next_fn):
        order.append("module")
        return await next_fn()

    container.add_singleton(MiddlewareProxy(global_mw))
    module_proxy = MiddlewareProxy(module_mw).for_route("/users")
    container.add_singleton(module_proxy, module=object())

    req, res = _make_request("/users/123")

    async def final_handler():
        order.append("handler")
        return "ok"

    from nestipy.core.middleware.executor import MiddlewareExecutor

    executor = MiddlewareExecutor(req, res, final_handler)
    result = await executor.execute()

    assert result == "ok"
    assert order == ["global", "module", "handler"]


def test_middleware_path_matching_and_params():
    NestipyContainer.clear()
    _reset_middleware_container()
    container = MiddlewareContainer.get_instance()

    async def users_mw(_req, _res, next_fn):
        return await next_fn()

    async def health_mw(_req, _res, next_fn):
        return await next_fn()

    container.add_singleton(MiddlewareProxy(users_mw).for_route("/users/:id"))
    container.add_singleton(MiddlewareProxy(health_mw).for_route("/health"))

    matched = container.match("/users/123/profile", "GET")
    assert [m.middleware for m in matched] == [users_mw]


def test_middleware_exclude_method():
    NestipyContainer.clear()
    _reset_middleware_container()
    container = MiddlewareContainer.get_instance()

    async def mw(_req, _res, next_fn):
        return await next_fn()

    proxy = (
        MiddlewareProxy(mw)
        .for_route("/users")
        .excludes({"path": "/users/health", "method": "GET"})
    )
    container.add_singleton(proxy)

    matched_get = container.match("/users/health", "GET")
    matched_post = container.match("/users/health", "POST")

    assert matched_get == []
    assert [m.middleware for m in matched_post] == [mw]


@pytest.mark.asyncio
async def test_middleware_allows_duplicates():
    NestipyContainer.clear()
    _reset_middleware_container()
    order: list[str] = []
    container = MiddlewareContainer.get_instance()

    async def mw(_req, _res, next_fn):
        order.append("mw")
        return await next_fn()

    container.add_singleton(MiddlewareProxy(mw))
    container.add_singleton(MiddlewareProxy(mw).for_route("/users"), module=object())

    req, res = _make_request("/users/1")

    async def final_handler():
        order.append("handler")
        return "ok"

    from nestipy.core.middleware.executor import MiddlewareExecutor

    executor = MiddlewareExecutor(req, res, final_handler)
    result = await executor.execute()

    assert result == "ok"
    assert order == ["mw", "mw", "handler"]


@pytest.mark.asyncio
async def test_class_based_middleware_executes():
    NestipyContainer.clear()
    _reset_middleware_container()
    container = MiddlewareContainer.get_instance()
    di = NestipyContainer.get_instance()
    order: list[str] = []

    class ClassMiddleware(NestipyMiddleware):
        async def use(self, _req, _res, next_fn):
            order.append("class")
            return await next_fn()

    di.add_singleton(ClassMiddleware)
    container.add_singleton(MiddlewareProxy(ClassMiddleware).for_route("/"))

    req, res = _make_request("/any")

    async def final_handler():
        order.append("handler")
        return "ok"

    from nestipy.core.middleware.executor import MiddlewareExecutor

    executor = MiddlewareExecutor(req, res, final_handler)
    result = await executor.execute()

    assert result == "ok"
    assert order == ["class", "handler"]
