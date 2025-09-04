from typing import Annotated

from nestipy.ioc import Inject

from nestipy.common import Injectable, logger
from nestipy.core import OnInit, OnDestroy


@Injectable()
class UserService(OnInit, OnDestroy):
    tes: Annotated[str, Inject("TEST")]

    async def on_startup(self):
        logger.info("On init user service")

    async def on_shutdown(self):
        logger.info("On shutdown user service")
