from granian.constants import Interfaces

from nestipy.core import NestipyFactory

from app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == "__main__":
    app.listen(
        address="0.0.0.0",
        port=8001,
        interface=Interfaces.ASGI,
        reload=True,
    )
