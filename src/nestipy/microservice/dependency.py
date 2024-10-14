from typing import Optional

from nestipy.ioc.dependency import Req, SocketData, Inject

Payload = SocketData
Ctx = Req


def Client(token: Optional[str] = None):
    return Inject(token)


__all__ = ["Payload", "Ctx", "Client"]
