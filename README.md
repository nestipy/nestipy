<p align="center">
  <a target="_blank"><img src="https://raw.githubusercontent.com/nestipy/nestipy/release-v1/nestipy.png" width="200" alt="Nestipy Logo" /></a></p>
<p align="center">
    <a href="https://pypi.org/project/nestipy">
        <img src="https://img.shields.io/pypi/v/nestipy?color=%2334D058&label=pypi%20package" alt="Version">
    </a>
    <a href="https://pypi.org/project/nestipy">
        <img src="https://img.shields.io/pypi/pyversions/nestipy.svg?color=%2334D058" alt="Python">
    </a>
    <a href="https://github.com/tsiresymila1/nestipy/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/tsiresymila1/nestipy" alt="License">
    </a>
</p>

## Description

<p>Nestipy is a Python framework built on top of FastAPI that follows the modular architecture of NestJS</p>
<p>Under the hood, Nestipy makes use of <a href="https://fastapi.tiangolo.com/" target="_blank">FastAPI</a>, but also provides compatibility with a wide range of other libraries, like <a href="https://fastapi.tiangolo.com/" target="_blank">Blacksheep</a>, allowing for easy use of the myriad of third-party plugins which are available.</p>

## Getting started

```cmd
    pip install nestipy-cli
    nestipy new my_app
    cd my_app
    nestipy start --dev
```

```
    ├── src
    │    ├── __init__.py
    ├── app_module.py
    ├── app_controller.py
    ├── app_service.py
    ├── main.py
    ├── cli.py
    ├── pyproject.yml
    ├── uv.lock
    ├── README.md
    
       
```
The main.py file contains an instance of application and bootstrapping it with granian.

```python
from granian import Granian
from granian.constants import Interfaces

from nestipy.core import NestipyFactory

from app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == '__main__':
    granian = Granian(
        target="main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
    )
    granian.serve()
```
Inside module, we got,

```python
from app_command import AppCommand
from app_controller import AppController
from app_service import AppService

from nestipy.common import Module


@Module(
    controllers=[AppController],
    providers=[AppService, AppCommand]
)
class AppModule: ...

```
For controller, we got something like
```python
from typing import Annotated

from nestipy.common import Controller, Get, Post, Put, Delete
from nestipy.ioc import Inject, Body, Param

from app_service import AppService


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @Get()
    async def get(self) -> str:
        return await self.service.get()

    @Post()
    async def post(self, data: Annotated[dict, Body()]) -> str:
        return await self.service.post(data=data)

    @Put("/{app_id}")
    async def put(
        self, app_id: Annotated[int, Param("app_id")], data: Annotated[dict, Body()]
    ) -> str:
        return await self.service.put(id_=app_id, data=data)

    @Delete("/{app_id}")
    async def delete(self, app_id: Annotated[int, Param("app_id")]) -> None:
        await self.service.delete(id_=app_id)

```
And, for `app_service.py`
```python
from nestipy.common import Injectable


@Injectable()
class AppService:
    @classmethod
    async def get(cls):
        return "test"

    @classmethod
    async def post(cls, data: dict):
        return "test"

    @classmethod
    async def put(cls, id_: int, data: dict):
        return "test"

    @classmethod
    async def delete(cls, id_: int):
        return "test"

```
## Documentation

View full documentation from [here](https://nestipy.vercel.app).

## Support

Nestipy is an MIT-licensed open source project. It can grow thanks to the sponsors and support from the amazing backers.
If you'd like to join them, please [read more here].

## Stay in touch

- Author - [Tsiresy Mila](https://tsiresymila.vercel.app)

## License

Nestipy is [MIT licensed](LICENSE).
