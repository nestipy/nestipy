from .event_gateway import EventGateway
from nestipy.common import Module


@Module(
    providers=[EventGateway],
    exports=[EventGateway],
    is_global=True
)
class EventModule:
    ...
