"""
Logging and console utilities for Nestipy using Python's logging and Rich.
"""
import logging

from rich.console import Console
from rich.style import Style

logger = logging.getLogger("granian")
console = Console(color_system="auto", style=Style(bold=True))
