from nestipy.core import NestipyFactory

from app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == "__main__":
    app.listen(
        interface="asgi",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
