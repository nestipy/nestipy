import inspect
from typing import Type, Union, Callable, Any, TYPE_CHECKING

from nestipy_ioc import NestipyContainer
from nestipy_ioc import NestipyContextContainer
from nestipy_metadata import NestipyContextProperty, Reflect, ModuleMetadata

from .decorator import GATEWAY_KEY, EVENT_KEY, SUCCESS_EVENT_KEY, ERROR_EVENT_KEY
from ..core.context.execution_context import ExecutionContext

if TYPE_CHECKING:
    from ..core.adapter.http_adapter import HttpAdapter


class IoSocketProxy:
    def __init__(self, adapter: "HttpAdapter"):
        self.adapter = adapter

    def apply_routes(self, modules: list[Union[Type, object]]):
        io_adapter = self.adapter.get_io_adapter()
        for module_ref in modules:
            gateways = self._get_module_provider_gateway(module_ref)
            for gateway in gateways:
                subscribers = self._get_method_event_subscriber(gateway)
                namespace = Reflect.get_metadata(gateway, GATEWAY_KEY, '/')
                for method_name in subscribers:
                    gateway_method = getattr(gateway, method_name)
                    event_name = Reflect.get_metadata(gateway_method, EVENT_KEY, '*')
                    handler = self._create_io_handler(module_ref, gateway, method_name, namespace, event_name)
                    io_adapter.on(event=event_name, namespace=namespace)(handler)

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

    @classmethod
    async def call_handler(cls, handler: Callable, params: dict):
        if inspect.iscoroutinefunction(handler):
            return await handler(**params)
        else:
            return handler(**params)

    def _create_io_handler(
            self,
            module_ref: Type,
            gateway: Type,
            method_name: str,
            namespace: str,
            event_name: Any
    ) -> Callable[..., Any]:
        async def io_handler(sid: Any, data: Any):
            io_adapter = self.adapter.get_io_adapter()
            context_container = NestipyContextContainer.get_instance()
            context_container.set_value(NestipyContextProperty.io_client, sid)
            context_container.set_value(NestipyContextProperty.io_data, data)
            context_container.set_value(NestipyContextProperty.io_server, io_adapter)

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
            context_container.set_value(NestipyContextProperty.execution_context, execution_context)
            try:
                result = await container.get(gateway, method_name)
                if result is not None:
                    # get success event from handler
                    success_event = Reflect.get_metadata(gateway, SUCCESS_EVENT_KEY, None)
                    # send response to websocket
                    await self.call_handler(io_adapter.emit, {
                        'event': success_event or event_name,
                        'data': result,
                        'namespace': namespace,
                        "to": sid
                    })
            except Exception as e:
                error_event = Reflect.get_metadata(gateway, ERROR_EVENT_KEY, None)
                if error_event is not None:
                    await self.call_handler(io_adapter.emit, {
                        'event': error_event,
                        'data': str(e),
                        'namespace': namespace,
                        "to": sid
                    })
                # create exception handler
            finally:
                context_container.destroy()

        return io_handler
