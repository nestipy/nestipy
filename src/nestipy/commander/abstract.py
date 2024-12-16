from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base class for CLI commands."""

    @abstractmethod
    async def run(self, context: dict):
        """The method to handle the command logic.

        Args:
            context (dict): Contains options and arguments for the command.
        """
        pass
