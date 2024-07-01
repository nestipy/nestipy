from nestipy.common import Injectable
from pyee.asyncio import AsyncIOEventEmitter


@Injectable()
class EventEmitter(AsyncIOEventEmitter):
    pass
