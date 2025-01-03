from typing import Optional

from nestipy.ioc.dependency import Req, SocketData, Inject
from .context import RpcRequest

Payload = SocketData
Ctx = Req
Context = RpcRequest


def Client(token: Optional[str] = None):
    return Inject(token)


__all__ = ["Payload", "Ctx", "Client", "Context"]
