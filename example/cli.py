import asyncio
import sys

from nestipy.commander import CommandFactory

from app_module import AppModule

command = CommandFactory.create(AppModule)

if __name__ == "__main__":
    asyncio.run(command.run(sys.argv[1], tuple(sys.argv[2:])))
