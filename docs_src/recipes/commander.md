**Nestipy** provides `nest-commander` alternative for writing command line applications in a structure similar to your
typical Nestipy application.

## Create command

Now, create a provider that extends `BaseCommand` and decorate with `Command`.

```python
from nestipy.commander import Command, BaseCommand


@Command(
    name="my_command",
    desc="This is a test command"
)
class MyCommand(BaseCommand):

    async def run(self):
        print("Hello")
```

Register command provider in Module.

```python

from nestipy.common import Module


@Module(
    providers=[
        MyCommand
    ]
)
class AppModule:
    ...
```

## Running the Command

Similar to how in a Nestipy application we can use the NestipyFactory to create a server for us,
We can import the `CommandFactory` and use the static
method `run` and pass in the root module of your application. This would probably look like below:

```python

from app_module import AppModule

from nestipy.commander import CommandFactory

command = CommandFactory.create(AppModule)

```

To interact with this, put this content in file named `cli.py` in the root of your project.

After of all, we can run the following command and get output :

```bash
$ nestipy run my_command # my_command is the command name declared in `Command` decorator
$ Hello
```

