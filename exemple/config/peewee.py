import asyncio

from nestipy.plugins.config_module.config_service import ConfigService
from nestipy.plugins.peewee_module.peewee_module import PeeweeDatabaseConfig


async def peewee_mysql_factory(config: ConfigService) -> PeeweeDatabaseConfig:
    await asyncio.sleep(0.4)
    return PeeweeDatabaseConfig(
        driver='mysql',
        database=config.get("DB_DATABASE"),
        host=config.get("DB_HOST"),
        port=int(f'{config.get("DB_PORT")}'),
        user=config.get("DB_USER"),
        password=config.get("DB_PASSWORD") or ''
    )
