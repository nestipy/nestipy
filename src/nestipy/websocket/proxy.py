import inspect
from typing import Type, Union, Callable, Any

from .decorator import GATEWAY_KEY, EVENT_KEY
from ..common import Reflect, ModuleMetadata
from ..common.metadata.container import NestipyContainerKey
from ..core.adapter.http_adapter import HttpAdapter
from ..core.context.execution_context import ExecutionContext
from ..core.ioc.nestipy_container import NestipyContainer
from ..core.ioc.nestipy_context_container import NestipyContextContainer


class IoSocketProxy:
    def __init__(self, adapter: HttpAdapter):
        self.adapter = adapter

    def apply_routes(self, modules: set[Union[Type, object]]):
        io_adapter = self.adapter.get_io_adapter()
        for module_ref in modules:
            gateways = self._get_module_provider_gateway(module_ref)
            for gateway in gateways:
                subscribers = self._get_method_event_subscriber(gateway)
                path = Reflect.get_metadata(gateway, GATEWAY_KEY, '/')
                for sub in subscribers:
                    gateway_method = getattr(gateway, sub)
                    event_name = Reflect.get_metadata(gateway_method, EVENT_KEY, '*')
                    handler = self._create_io_handler(module_ref, gateway, sub)
                    io_adapter.on(event=event_name, namespace=path)(handler)

    @classmethod
    def _get_module_provider_gateway(cls, module_ref: Union[Type, object]) -> list[Type]:
        providers = Reflect.get_metadata(module_ref, ModuleMetadata.Providers, [])
        return [p for p in providers if Reflect.get_metadata(p, GATEWAY_KEY, None) is not None]

    @classmethod
    def _get_method_event_subscriber(cls, gateway: Type) -> list[str]:
        methods = []
        for method_name, _ in inspect.getmembers(gateway, inspect.isfunction):
            if method_name.startswith("__"):
                continue
            if Reflect.get_metadata(getattr(gateway, method_name), EVENT_KEY, None) is not None:
                methods.append(method_name)
        return methods

    def _create_io_handler(self, module_ref: Type, gateway: Type, method_name: str) -> Callable[..., Any]:
        async def io_handler(sid: Any, data: Any):
            context_container = NestipyContextContainer.get_instance()
            # setup container for query params, route params, request, response, session, etc..
            # context_container.set_value(NestipyContainerKey.request, io)
            context_container.set_value(NestipyContainerKey.io_client, sid)
            context_container.set_value(NestipyContainerKey.io_data, data)
            context_container.set_value(NestipyContainerKey.io_server, self.adapter.get_io_adapter())

            container = NestipyContainer.get_instance()
            gateway_method = getattr(gateway, method_name)
            execution_context = ExecutionContext(
                self.adapter,
                module_ref,
                gateway,
                gateway_method,
                None,
                None
            )
            context_container.set_value(NestipyContainerKey.execution_context, execution_context)
            try:
                result = await container.get(gateway, method_name)
                if result is not None:
                    # send response to websocket
                    pass
            except Exception as e:
                print(e)
                pass
            finally:
                context_container.destroy()

        return io_handler
