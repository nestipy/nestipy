from nestipy.web import action

class DemoActions:
    @action()
    async def hello(self, name: str = "world") -> str:
        return f"Hello, {name}!"
