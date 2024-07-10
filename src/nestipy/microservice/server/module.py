from typing import Annotated

from nestipy.common import Module
from nestipy.core import DiscoverService
from nestipy.ioc import Inject


@Module()
class MicroserviceServerModule:
    discover: Annotated[DiscoverService, Inject()]
