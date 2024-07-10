from nestipy.ioc.dependency import Req, SocketData, Inject

Payload = SocketData
Ctx = Req


def Client(token: str = None):
    return Inject(token)


__all__ = [
    "Payload",
    "Ctx",
    "Client"
]
