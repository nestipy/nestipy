from abc import ABC, abstractmethod
from typing import Any


class BaseCommand(ABC):
    """Abstract base class for Nestipy commands."""

    _args: list = []
    _options: dict[str, Any] = {}

    @abstractmethod
    async def run(self):
        """The method to handle the command logic."""
        raise NotImplemented("Must be implement")

    def init(self, context: tuple):
        """Parse the combined context into arguments and options.

        Args:
            context (tuple): Combined arguments and options.

        """
        args = []
        options = {}

        it = iter(context)
        for item in it:
            if item.startswith('--'):
                key = item.lstrip('--')
                value = next(it, True)
                if value.startswith('--'):
                    value = True
                options[key] = value
            else:
                args.append(item)
        self._args = args
        self._options = options

    def get_opt(self, key: str = None, default=None):
        """Retrieve an option from the options dictionary safely."""
        return self._options.get(key, default) if key else self._options

    def get_arg(self, index: int = None, default=None):
        """Retrieve an argument by index from the arguments list safely."""
        try:
            return self._args[index] if index is not None else self._args
        except IndexError:
            return default
