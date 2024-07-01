from typing import Callable, Union, Type, Any

from .event_metadata import EventMetadata, EventData
from nestipy.metadata import SetMetadata


def OnEvent(name: str) -> Callable[[Union[Type, Callable[..., Any]]], Any]:
    return SetMetadata(EventMetadata.Event, EventData(name=name, once=False))


def OnceEvent(name: str) -> Callable[[Union[Type, Callable[..., Any]]], Any]:
    return SetMetadata(EventMetadata.Event, EventData(name=name, once=True))
