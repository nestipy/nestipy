from nestipy.common import Injectable
from nestipy.web import action, ActionAuth
from datetime import datetime


@Injectable()
class AppActions:
    # Example: permissions + guards in one decorator
    # @ActionAuth("hello:read", guards=[])
    @action()
    async def hello(self, name: str = "Nestipy") -> str:
        return f"Hello, {name} - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!"