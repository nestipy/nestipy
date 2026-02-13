from nestipy.common import Injectable
from nestipy.web import action, ActionAuth


@Injectable()
class AppActions:
    # Example: permissions + guards in one decorator
    # @ActionAuth("hello:read", guards=[])
    @action()
    async def hello(self, name: str = "Nestipy") -> str:
        return f"Hello, {name}!"