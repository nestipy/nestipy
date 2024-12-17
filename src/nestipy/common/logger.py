import logging

from rich.console import Console
from rich.style import Style

logger = logging.getLogger("uvicorn")
console = Console(color_system="auto", style=Style(bold=True))
