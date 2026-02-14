from granian import Granian
from nestipy.core import NestipyFactory

from app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == "__main__":
    Granian(
        "main:app",
        interface="asgi",
        address="0.0.0.0",
        port=8000,
        reload=True,
    ).serve()
