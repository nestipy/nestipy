from typing import Type

from nestipy.common import Injectable
from nestipy.common.metadata.decorator import SetMetadata

GATEWAY_KEY = '__GATEWAY__'
EVENT_KEY = '__GATEWAY_EVENT__'


def Gateway(path: str = '/'):
    meta_decorator = SetMetadata(GATEWAY_KEY, path)

    def decorator(cls: Type):
        cls = meta_decorator(cls)
        return Injectable()(cls)

    return decorator


def SubscribeMessage(event: str):
    return SetMetadata(EVENT_KEY, event)
