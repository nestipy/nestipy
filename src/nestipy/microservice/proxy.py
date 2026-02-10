import inspect
import traceback
from typing import Type, Callable, cast, Any, Union

from nestipy.common.logger import logger
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards.processor import GuardProcessor
from nestipy.core.interceptor.processor import RequestInterceptor
from nestipy.ioc import RequestContextContainer, NestipyContainer
from nestipy.metadata.class_ import ClassMetadata
from nestipy.metadata.reflect import Reflect
from .context import RpcRequest, RpcException
from .decorator import MICROSERVICE_LISTENER, MicroserviceMetadata, MicroserviceData
from .exception import RPCErrorCode, RPCErrorMessage
from .server.base import MicroServiceServer


class MicroserviceProxy:
    def __init__(self, adapter: MicroServiceServer):
        self.adapter = adapter

    def apply_routes(self, controllers: list[object | Type]):
        for ctrl in controllers:
            elements = inspect.getmembers(
                ctrl, lambda a: inspect.isfunction(a) or inspect.iscoroutinefunction(a)
            )
            methods = [
                method
                for (method, _) in elements
                if not method.startswith("__")
                and self._is_listener(getattr(ctrl, method))
            ]
            for m in methods:
                metadata: ClassMetadata = Reflect.get_metadata(
                    ctrl, ClassMetadata.Metadata, None
                )
                if metadata is not None:
                    data: MicroserviceData = Reflect.get_metadata(
                        getattr(ctrl, m), MICROSERVICE_LISTENER, None
                    )
                    if (
                        not data.transport
                        or data.transport == self.adapter.get_transport()
                    ):
                        handler = self._create_event_handler(
                            metadata.get_module(),
                            ctrl,
                            m,
                        )
                        self.register_listener(handler, data)

    @classmethod
    def _is_listener(cls, method: Callable):
        return Reflect.get_metadata(method, MICROSERVICE_LISTENER, None) is not None

    def register_listener(self, listener: Callable, data: MicroserviceData):
        match data.type:
            case MicroserviceMetadata.Event:
                self.adapter.subscribe(data.pattern, listener)
            case MicroserviceMetadata.Message:
                self.adapter.request_subscribe(data.pattern, listener)

    @classmethod
    def _create_event_handler(
        cls,
        module_ref: Type,
        controller: Union[Type, object],
        method_name: str,
    ):
        async def event_handler(server: MicroServiceServer, request: RpcRequest):
            context_container = RequestContextContainer.get_instance()
            previous_context = context_container.execution_context
            container = NestipyContainer.get_instance()
            execution_context = ExecutionContext(
                None,
                module_ref,
                controller,
                getattr(controller, method_name),
                cast(Any, request),
                None,
                None,
                None,
                server,
                None,
                request.data,
            )
            context_container.reset_request_cache()
            context_container.set_execution_context(execution_context)
            await container.preload_request_scoped_properties()
            try:
                guard_processor: GuardProcessor = await container.get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context, False)
                if not can_activate[0]:
                    raise RpcException(
                        RPCErrorCode.PERMISSION_DENIED,
                        RPCErrorMessage.PERMISSION_DENIED,
                    )

                async def next_fn():
                    return await container.get(controller.__class__, method_name)

                interceptor: RequestInterceptor = await container.get(
                    RequestInterceptor
                )
                return await interceptor.intercept(execution_context, next_fn, False)

            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, RpcException):
                    e = RpcException(RPCErrorCode.INTERNAL, RPCErrorMessage.INTERNAL)
                exception_handler: ExceptionFilterHandler = await container.get(
                    ExceptionFilterHandler
                )
                result = await exception_handler.catch(e, execution_context, False)
                if isinstance(result, RpcException):
                    raise result
                if result is not None:
                    raise RpcException(e.status_code, str(result))
                raise e
            finally:
                if previous_context is not None:
                    context_container.set_execution_context(previous_context)
                else:
                    context_container.destroy()

        return event_handler
