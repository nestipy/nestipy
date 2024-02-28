import asyncio

from nestipy.plugins.config_module.config_service import ConfigService
from nestipy.plugins.masonite_orm_module.masonite_orm_module import MasoniteDatabaseConfig


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
