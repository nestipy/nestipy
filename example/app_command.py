from nestipy.commander import BaseCommand, Command


@Command(name='app', desc="Test app command")
class AppCommand(BaseCommand):
    async def run(self, context: dict):
        pass
