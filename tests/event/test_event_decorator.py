from nestipy.event.event_decorator import OnEvent, OnceEvent
from nestipy.event.event_metadata import EventMetadata
from nestipy.metadata import Reflect


def test_event_decorators_set_metadata():
    def handler():
        return None

    decorated = OnEvent("ping")(handler)
    data = Reflect.get_metadata(decorated, EventMetadata.Event, None)
    assert data is not None
    assert data.name == "ping"
    assert data.once is False

    decorated_once = OnceEvent("pong")(handler)
    data_once = Reflect.get_metadata(decorated_once, EventMetadata.Event, None)
    assert data_once is not None
    assert data_once.name == "pong"
    assert data_once.once is True
