import asyncio

import pytest

from nestipy.event.event_emitter import EventEmitter
from nestipy.event.event_module import EventEmitterModule
from nestipy.event.event_decorator import OnEvent, OnceEvent
from nestipy.event.event_builder import EventOption
from nestipy.metadata import Reflect


class ListenerProvider:
    def __init__(self):
        self.called = []

    @OnEvent("ping")
    def on_ping(self, payload):
        self.called.append(("ping", payload))

    @OnceEvent("once")
    async def on_once(self, payload):
        self.called.append(("once", payload))


class FakeDiscover:
    def __init__(self, providers):
        self._providers = providers

    def get_all_controller(self):
        return []

    def get_all_provider(self):
        return self._providers


@pytest.mark.asyncio
async def test_event_emitter_module_registers_listeners():
    provider = ListenerProvider()
    emitter = EventEmitter()
    module = EventEmitterModule()
    module._discovery = FakeDiscover([provider])
    module._event_emitter = emitter

    await module.on_startup()

    # Emit normal event
    emitter.emit("ping", "data")
    await asyncio.sleep(0)

    # Emit once event twice
    emitter.emit("once", "first")
    emitter.emit("once", "second")
    await asyncio.sleep(0)

    assert ("ping", "data") in provider.called
    assert ("once", "first") in provider.called
    assert ("once", "second") not in provider.called


def test_event_module_for_root_sets_global():
    dynamic = EventEmitterModule.for_root(is_global=True)
    assert dynamic.is_global is True

    dynamic_false = EventEmitterModule.for_root(is_global=False)
    assert dynamic_false.is_global is False

    # Ensure option token is injected
    providers = dynamic.providers
    assert any(getattr(p, "token", None) for p in providers)
