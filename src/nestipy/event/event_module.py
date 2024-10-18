import inspect
from typing import Annotated, Union, Callable

from nestipy.common import Module
from nestipy.core import DiscoverService
from nestipy.dynamic_module import NestipyModule
from nestipy.ioc import Inject, ModuleProviderDict
from nestipy.metadata import Reflect
from .event_builder import ConfigurableClassBuilder, EventOption
from .event_emitter import EventEmitter
from .event_metadata import EventMetadata, EventData


@Module(
    providers=[ModuleProviderDict(token=EventEmitter, value=EventEmitter())],
    exports=[EventEmitter],
)
class EventEmitterModule(ConfigurableClassBuilder, NestipyModule):
    _discovery: Annotated[DiscoverService, Inject()]
    _event_emitter: Annotated[EventEmitter, Inject()]

    @classmethod
    def _is_listener(cls, method: callable):
        v = Reflect.get_metadata(method, EventMetadata.Event)
        return v is not None

    def _register_listener(self, method: callable):
        event_data: Union[EventData, None] = Reflect.get_metadata(
            method, EventMetadata.Event, None
        )
        if event_data:
            callback = self._create_async_handler(method)
            if event_data.once:
                self._event_emitter.once(event_data.name, callback)
            else:
                self._event_emitter.add_listener(event_data.name, callback)

    @classmethod
    def _create_async_handler(cls, callback: Callable) -> callable:
        async def async_handler(*args, **kwargs):
            if inspect.iscoroutinefunction(callback):
                return await callback(*args, **kwargs)
            else:
                return callback(*args, **kwargs)

        return async_handler

    def _register_listeners(self):
        instances = (
            self._discovery.get_all_controller() + self._discovery.get_all_provider()
        )
        for p in instances:
            elements = inspect.getmembers(
                p,
                lambda a: inspect.isfunction(a)
                or inspect.iscoroutinefunction(a)
                or inspect.ismethod(a),
            )
            methods = [
                method
                for (method, _) in elements
                if not method.startswith("__") and self._is_listener(getattr(p, method))
            ]
            for m in methods:
                self._register_listener(getattr(p, m))

    async def on_startup(self):
        self._register_listeners()

    async def on_shutdown(self):
        pass

    @classmethod
    def for_root(cls, is_global: bool = True):
        return cls.register(EventOption(), extras={"is_global": is_global})
