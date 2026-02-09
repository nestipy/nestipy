from typing import Annotated

import pytest

from nestipy.common import Injectable
from nestipy.ioc import NestipyContainer, Inject, RequestContextContainer
from nestipy.core import ExecutionContext
from nestipy.common.http_ import Request, Response


@pytest.fixture
def container():
    """
    Fixture to provide a fresh instance of NestipyContainer for each test.
    """
    NestipyContainer.clear()
    return NestipyContainer.get_instance()


@pytest.mark.asyncio
async def test_singleton_instance(container):
    """
    Test adding and retrieving a singleton instance from the container.
    """

    class DummyService:
        pass

    service_instance = DummyService()

    container.add_singleton_instance(DummyService, service_instance)

    retrieved_instance = await container.get(DummyService)
    assert retrieved_instance is service_instance, (
        "Singleton instance should be the same."
    )


@pytest.mark.asyncio
async def test_transient_service(container):
    """
    Test adding and retrieving a transient service from the container.
    """

    class TransientService:
        pass

    container.add_transient(TransientService)

    instance1 = await container.get(TransientService)
    instance2 = await container.get(TransientService)

    assert instance1 is not instance2, (
        "Transient service should create a new instance each time."
    )


# @pytest.mark.asyncio
# async def test_global_providers(container):
#     """
#     Test retrieving global providers.
#     """
#
#     class GlobalService:
#         pass
#
#     container.add_singleton(GlobalService)
#
#     global_providers = container.get_global_providers()
#
#     assert GlobalService in global_providers, "Global providers should include GlobalService."
#


@pytest.mark.asyncio
async def test_dependency_injection(container):
    """
    Test automatic dependency injection for a service.
    """

    @Injectable()
    class ServiceA:
        pass

    @Injectable()
    class ServiceB:
        service_a: Annotated[ServiceA, Inject()]

    service_b_instance = await container.get(ServiceB, disable_scope=True)
    serv = service_b_instance.service_a
    assert isinstance(serv, ServiceA), "ServiceB should have ServiceA injected."


@pytest.mark.asyncio
async def test_circular_dependency(container):
    """
    Test for detection of circular dependencies.
    """

    @Injectable()
    class ServiceA:
        service_b: Annotated["ServiceB", Inject()]

    @Injectable()
    class ServiceB:
        service_a: Annotated[ServiceA, Inject()]

    globals()["ServiceA"] = ServiceA
    globals()["ServiceB"] = ServiceB

    try:
        await container.get(ServiceA, disable_scope=True)
    except ValueError as e:
        print(f"Caught ValueError: '{str(e)}'")
        assert "Circular dependency found" in str(e)
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {str(e)}")
        raise e


@pytest.mark.asyncio
async def test_factory_resolution(container):
    """
    Test resolving a service using a factory function.
    """

    @Injectable()
    class ServiceA:
        pass

    @Injectable()
    class ServiceB:
        def __init__(self, service_a: Annotated[ServiceA, Inject()]):
            self.service_a = service_a

    async def factory_func(service_a: Annotated[ServiceA, Inject()]):
        return ServiceB(service_a)

    service_b_instance = await container.resolve_factory(
        factory_func, [], [], disable_scope=True
    )
    assert isinstance(service_b_instance, ServiceB), (
        "Factory function should return an instance of ServiceB."
    )


@pytest.mark.asyncio
async def test_resolve_property(container):
    """
    Test resolving properties for a service with dependencies.
    """

    @Injectable()
    class ServiceA:
        pass

    @Injectable()
    class ServiceB:
        service_a: Annotated[ServiceA, Inject()]

    service_b_instance = await container.get(ServiceB, disable_scope=True)
    assert isinstance(service_b_instance.service_a, ServiceA), (
        "ServiceB should have ServiceA resolved as property."
    )


@pytest.mark.asyncio
async def test_get_method_dependency(container):
    """
    Test resolving method dependencies using annotations.
    """

    class ServiceA:
        pass

    class ServiceB:
        pass

    container.add_singleton(ServiceA)
    container.add_singleton(ServiceB)

    async def test_method(
        service_a: Annotated[ServiceA, Inject()],
        service_b: Annotated[ServiceB, Inject()],
    ):
        return service_a, service_b

    method_dependencies = await container._get_method_dependency(
        test_method, [ServiceA, ServiceB]
    )

    assert isinstance(method_dependencies["service_a"], ServiceA)
    assert isinstance(method_dependencies["service_b"], ServiceB)


@pytest.mark.asyncio
async def test_check_service(container):
    """
    Test the service checking mechanism for circular dependencies.
    """

    class ServiceA:
        pass

    container.add_singleton(ServiceA)

    service, origin = container._check_service(ServiceA)
    assert service is ServiceA, "ServiceA should be correctly checked and returned."
    assert origin == set(), "Origin should be empty for first service resolution."


@pytest.mark.asyncio
async def test_request_scoped_service(container):
    class RequestScopedService:
        pass

    container.add_request_scoped(RequestScopedService)

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_msg):
        return None

    scope = {
        "type": "http",
        "query_string": b"",
        "headers": [],
        "raw_path": b"/",
        "method": "GET",
        "server": ("localhost", 80),
        "scheme": "http",
    }

    req = Request(scope, receive, send)
    res = Response()
    ctx = ExecutionContext(None, None, None, None, req, res)

    RequestContextContainer.set_execution_context(ctx)
    instance1 = await container.get(RequestScopedService)
    instance2 = await container.get(RequestScopedService)
    assert instance1 is instance2, "Request-scoped should be cached per request."

    RequestContextContainer.get_instance().destroy()

    req2 = Request(scope, receive, send)
    res2 = Response()
    ctx2 = ExecutionContext(None, None, None, None, req2, res2)
    RequestContextContainer.set_execution_context(ctx2)
    instance3 = await container.get(RequestScopedService)
    assert instance1 is not instance3, "Request-scoped should not leak across requests."
