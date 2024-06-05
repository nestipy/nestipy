Currently, Nestipy includes a module designed to facilitate database interactions. This module offers tools and functionalities to manage database connections, perform queries, and handle data efficiently, making it easier for developers to integrate database operations within their applications.
## Peewee Integration

Nestipy provides the `nestipy_peewee` module, which demonstrates how to utilize the `peewee` package effectively.

## Installation
```bash
pip install nestipy_peewee
```

Bellow is a basic example by loading config from `.env` file using `nestipy_config`.
```python
from typing import Annotated

from nestipy.common import Module
from nestipy.ioc import Inject
from nestipy_config import ConfigModule, ConfigOption, ConfigService
from nestipy_peewee import PeeweeConfig, PeeweeModule, Model
from peewee import TextField, IntegerField


@Model()
class User:
    name = TextField()
    city = TextField()
    age = IntegerField()


async def peewee_factory(config: Annotated[ConfigService, Inject()]) -> PeeweeConfig:
    return PeeweeConfig(
        driver='mysql',
        host=config.get('DB_HOST'),
        user=config.get('DB_USER'),
        password=config.get('DB_PASSWORD'),
        port=int(config.get('DB_PORT')),
        database=config.get('DB_DATABASE'),
        models=[User]
    )


@Module(
    imports=[
        ConfigModule.for_root(ConfigOption(), {'is_global': True}),
        # PeeweeModule.for_root(
        #     PeeweeConfig(
        #         driver='mysql',
        #         host='localhost',
        #         user='root',
        #         password='',
        #         port=3306,
        #         database='nestipy',
        #         models=[User]
        #     )
        # ),
        PeeweeModule.for_root_async(
            factory=peewee_factory,
            inject=[ConfigService]
            # we can inject `ConfigService` here because `ConfigModule` is declared as global
        ),
    ],
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...


```
So now, we can use model `User` as same as `Peewee Model`.

```python
from dataclasses import asdict

from nestipy.common import Injectable
from playhouse.shortcuts import model_to_dict

from .dto import CreateUserDto
from .model import User


@Injectable()
class AppService:

    async def list(self):
        return list(User.select().dicts())

    async def create(self, data: CreateUserDto):
        user = User.create(**asdict(data))
        return model_to_dict(user)

    async def update(self, _id: int, data: CreateUserDto):
        User.update(asdict(data), id=_id).execute()
        return True

    async def delete(self, _id: int):
        return User.delete_by_id(_id)

```

We can also register `Peewee Model` by calling `PeeweeModule.for_feature(Model1, Model2, ...)` inside a module imports instead of putting it with `PeeweeConfig`.
For more, take a look at **[Peewee documentation](https://docs.peewee-orm.com)**.

## Beanie Integration

Nestipy provides the `nestipy_beanie` module, which demonstrates how to utilize the `mongo` with it.

## Installation
```bash
pip install nestipy_beanie
```
In the following example, we also use nestipy_config to load the database configuration from a .env file.

```python
from typing import Annotated

from nestipy.common import Module
from nestipy.ioc import Inject
from nestipy_config import ConfigModule, ConfigOption, ConfigService

from app_controller import AppController
from app_service import AppService
from product_document import Product
from nestipy_beanie import BeanieModule, BeanieOption


def beanie_config(config: Annotated[ConfigService, Inject()]) -> BeanieOption:
    return BeanieOption(
        url=f"mongodb://{config.get('DB_USER')}:{config.get('DB_PASSWORD')}@{config.get('DB_HOST')}:{config.get('DB_PORT')}",
        documents=[Product],  # register beanie document here.
        database=config.get("DB_NAME")
    )


@Module(
    imports=[
        BeanieModule.for_root_async(
            factory=beanie_config,
            inject=[ConfigService],
            imports=[ConfigModule.for_root(ConfigOption())]
        ),
        # BeanieModule.for_root(BeanieOption(
        #     url="mongodb://user:pass@host:27017",
        #     database="nestipy",
        #     documents=[Product]
        # ))
    ],
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...

```
For more, take a look at **[Beanie documentation](https://beanie-odm.dev)**.

## Prisma Integration
Nestipy offers the nestipy_prisma module to simplify the configuration and use of prisma.

## Installation
```bash
pip install nestipy_prisma
```
The configiration is simple,

```python
from nestipy.common import Module
from nestipy_prisma import PrismaModule
from app_controller import AppController
from app_service import AppService


@Module(
    imports=[
        PrismaModule.for_root()
    ],
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...

```

Now, we can get instance of `prisma` by injecting `PrismaService`.
```python
from dataclasses import dataclass, asdict
from typing import Annotated

from nestipy.common import Injectable
from nestipy.ioc import Inject
from prisma.types import PostCreateInput, PostUpdateInput

from nestipy_prisma import PrismaService


@dataclass
class PostDto:
    title: str
    published: bool
    desc: str


@Injectable()
class AppService:
    prisma: Annotated[PrismaService, Inject()]

    async def get(self):
        result = await self.prisma.post.find_many()
        return [a.model_dump(mode="json") for a in result]

    async def post(self, data: PostDto):
        return (await self.prisma.post.create(
            PostCreateInput(**asdict(data))
        )).model_dump()

    async def put(self, id_: str, data: PostDto):
        return (await self.prisma.post.update(PostUpdateInput(**asdict(data)), where={
            "id": id_
        })).model_dump(mode="json")

    async def delete(self, id_: str):
        return (await self.prisma.post.delete(where={"id": id_})).model_dump(mode="json")

```

For more, take a look at **[Prisma documentation](https://prisma-client-py.readthedocs.io)**.




