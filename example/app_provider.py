from typing import Annotated

from nestipy.ioc import Inject

from nestipy.common import Injectable


@Injectable()
class AppProvider:
    tes: Annotated[str, Inject("TEST")]
    pass
