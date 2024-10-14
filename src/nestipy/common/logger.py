import logging

from rich.console import Console
from rich.style import Style

logger = logging.getLogger("uvicorn")
console = Console(color_system="truecolor", style=Style(bold=True, color="green"))
