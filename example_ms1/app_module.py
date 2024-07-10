from nestipy.common import Module

from app_controller import AppController
from app_service import AppService


@Module(
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...
