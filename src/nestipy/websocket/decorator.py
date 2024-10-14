from typing import Type

from nestipy.common.decorator import Injectable
from nestipy.metadata import SetMetadata

GATEWAY_KEY = "__GATEWAY__"
EVENT_KEY = "__GATEWAY_EVENT__"
SUCCESS_EVENT_KEY = "__GATEWAY_SUCCESS_EVENT__"
ERROR_EVENT_KEY = "__GATEWAY_ERROR_EVENT__"


def Gateway(namespace: str = "/"):
    meta_decorator = SetMetadata(GATEWAY_KEY, namespace)

    def decorator(cls: Type):
        cls = meta_decorator(cls)
        return Injectable()(cls)

    return decorator


def SubscribeMessage(event: str):
    return SetMetadata(EVENT_KEY, event)


def SuccessEvent(event: str):
    return SetMetadata(SUCCESS_EVENT_KEY, event)


def ErrorEvent(event: str):
    return SetMetadata(ERROR_EVENT_KEY, event)
