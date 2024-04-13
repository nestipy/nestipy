## List of available modules 

### Strawberry module
 Usage: register Strawberry module in `app_module.py` to use it <br/> 
 `app_module.py`

```python
...
from nestipy.plugins.strawberry_module.strawberry_module import StrawberryModule, StrawberryOption

...


@Module(
    imports=[
        ...
        StrawberryModule.for_root(
            resolvers=[UserModule],
            option=StrawberryOption(graphql_ide='graphiql')
        ),
        ...
    ],
)
class AppModule:
    pass
```

In <b>resolvers</b> import all modules that you have defined your **resolvers**.

### Config module
 Usage: register Config module in `app_module.py` to use it <br/>
 `app_module.py`
 
```python
...
from nestipy.plugins.config_module.config_module import ConfigModule
...


@Module(
    imports=[
        ...
        ConfigModule.for_root(),
        ...
    ],

)
class AppModule(NestipyModule):
   pass

```
`ConfigModule.for_root()` can receive a parameter of .env file

`ConfigModule` is a global module, so `ConfigService` can be injected in any Controller, Resolver, or Service.
You can use method `get('key')` of `ConfigService` to get value by key from your `.env` file.

### Peewee module
 Usage: register Peewee module in `app_module.py` to use it <br/> 

`app_module.py`
 
```python
...
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule,PeeweeDatabaseConfig
from nestipy.plugins.config_module.config_module import ConfigModule, ConfigService
...


async def peewee_mysql_factory(config: ConfigService) -> PeeweeDatabaseConfig:
    return PeeweeDatabaseConfig(
        driver='mysql',
        database=config.get("DB_DATABASE"),
        host=config.get("DB_HOST"),
        port=int(f'{config.get("DB_PORT")}'),
        user=config.get("DB_USER"),
        password=config.get("DB_PASSWORD") or ''
    )

@Module(
    imports=[
        ...
        ConfigModule.for_root(),
         PeeweeModule.for_root_async(
            use_factory=peewee_mysql_factory,
            inject=[ConfigService]
        ),
        ...
    ],

)
class AppModule(NestipyModule):
   pass

```
In this example, we show the dependency between module. So , in this case, `ConfigModule` must be registered in top of `PeeweeModule`. 
`ConfigService` is a provider exported by `ConfigModule`

To register a model in peewee, model must decorate with `@Model` from `peewee_module` and must be register by calling `PeeweeModule.for_feature([MyModel])` in imports of Module. 

### Masonite orm module
 Usage: register Masonite orm module in `app_module.py` to use it <br/> 

`app_module.py`

```python 
...
from nestipy.plugins.masonite_orm_module.masonite_orm_module import MasoniteOrmModule, MasoniteDatabaseConfig
...
async def masonite_factory(config: ConfigService):
    await asyncio.sleep(0.4)
    return {
        'default': 'mysql',
        'mysql': MasoniteDatabaseConfig(
            driver='mysql',
            host=config.get("DB_HOST"),
            port=config.get("DB_PORT"),
            user=config.get("DB_USER"),
            password=config.get("DB_PASSWORD") or '',
            database=config.get("DB_DATABASE")
        )
    }
@Module(
    imports=[
        ...,
        ConfigModule.for_root(),
        MasoniteOrmModule.for_root_async(
            factory=masonite_factory,
            inject=[ConfigService]
        ),
        ...
    ]
)
class AppModule:
    pass
```


### Beanie mongo module
 Usage: register Beanie mongo module in `app_module.py` to use it <br/> 

`app_module.py`

```python 
..
from nestipy.plugins.beanie_module.beanie_module import BeanieModule
...

async def beanie_factory(config: ConfigService):
    return config.get('MONGODB_URL')


@Module(
    imports=[
        ...,
        ConfigModule.for_root(),
        BeanieModule.for_root_async(
            use_factory=beanie_factory,
            inject=[ConfigService],
            documents= [
                #Register document here or use BeanieModule.for_feature([MyDocument])
            ]
        ),
        ...
    ]
)
class AppModule:
    pass
```
You must call `BeanieModule.for_feature([MyDocument])` inside module imports to register a document.


