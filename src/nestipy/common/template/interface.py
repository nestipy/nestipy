from abc import ABC, abstractmethod
from typing import Any


class TemplateEngine(ABC):

    def __init__(self, template_dir: str):
        self.template_dir = template_dir

    @abstractmethod
    def render(self, template: str, context: dict) -> str:
        """
        A specific implementation of rendering content of template file.

        Args:
            template (str): The template string.
            context (dict): The context data to be used in rendering.

        Returns:
            str: The rendered template.
        """
        pass

    @abstractmethod
    def render_str(self, string: str, context: dict) -> str:
        """
        Args:
            string (str): The string to compile.
            context (dict): The context data to be used in rendering.
        Returns:
            str: The rendered string .
        """
        pass

    @abstractmethod
    def get_env(self) -> Any:
        pass
