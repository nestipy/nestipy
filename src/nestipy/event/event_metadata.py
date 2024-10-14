import dataclasses


class EventMetadata:
    Event: str = "__event_listener__"


@dataclasses.dataclass
class EventData:
    name: str
    once: bool
