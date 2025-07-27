from abc import ABC, abstractmethod
from typing import Any, Optional

import click


class BaseCommand(ABC):
    """Abstract base class for Nestipy commands."""

    _args: list = []
    _options: dict[str, Any] = {}

    @abstractmethod
    async def run(self):
        """The method to handle the command logic."""
        raise NotImplemented("Must be implement")

    @classmethod
    def info(
        cls,
        info: Optional[Any] = None,
    ):
        click.secho(info, fg="green")

    @classmethod
    def error(
        cls,
        info: Optional[Any] = None,
    ):
        click.secho(info, fg="red")

    @classmethod
    def warning(
        cls,
        info: Optional[Any] = None,
    ):
        click.secho(info, fg="orange")

    @classmethod
    def success(
        cls,
        info: Optional[Any] = None,
    ):
        click.secho(info, fg="green", bold=True)

    def init(self, context: tuple):
        """Parse the combined context into arguments and options.

        Args:
            context (tuple): Combined arguments and options.

        """
        positional_args = []
        keyword_args = {}
        i = 0
        while i < len(context):
            arg = context[i]
            if arg.startswith("--"):
                if "=" in arg:
                    key, value = arg[2:].split("=", 1)
                    keyword_args[key] = value
                else:
                    key = arg[2:]
                    # lookahead for value
                    if i + 1 < len(context) and not context[i + 1].startswith("-"):
                        keyword_args[key] = context[i + 1]
                        i += 1
                    else:
                        keyword_args[key] = True
            elif arg.startswith("-") and len(arg) == 2:
                key = arg[1:]
                if i + 1 < len(context) and not context[i + 1].startswith("-"):
                    keyword_args[key] = context[i + 1]
                    i += 1
                else:
                    keyword_args[key] = True
            else:
                positional_args.append(arg)
            i += 1

        self._args = positional_args
        self._options = keyword_args

    def get_opt(self, key: str = None, default=None):
        """Retrieve an option from the options dictionary safely."""
        return self._options.get(key, default) if key else self._options

    def get_arg(self, index: int = None, default=None):
        """Retrieve an argument by index from the arguments list safely."""
        try:
            return self._args[index] if index is not None else self._args
        except IndexError:
            return default
