"""
Logging and console utilities for Nestipy using Python's logging and Rich.
"""

from __future__ import annotations

import logging
import logging.config
from typing import Optional, Iterable

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style

DEFAULT_LOG_FORMAT = "[NESTIPY] %(levelname)s %(message)s"

logger = logging.getLogger("nestipy")
console = Console(color_system="auto", style=Style(bold=True))


class _NestipyRichFormatter(logging.Formatter):
    _LEVEL_STYLES = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        style = self._LEVEL_STYLES.get(original_levelname, "white")
        record.levelname = f"[{style}]{original_levelname}[/{style}]"
        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname


def _apply_handlers(
    target_logger: logging.Logger,
    handlers: Iterable[logging.Handler],
    level: int,
    force: bool,
) -> None:
    if force:
        for handler in list(target_logger.handlers):
            target_logger.removeHandler(handler)
    if force or not target_logger.handlers:
        for handler in handlers:
            target_logger.addHandler(handler)
    target_logger.setLevel(level)
    target_logger.propagate = False


def configure_logger(
    level: int = logging.INFO,
    fmt: str = DEFAULT_LOG_FORMAT,
    datefmt: Optional[str] = None,
    use_color: bool = True,
    file: Optional[str] = None,
    file_level: Optional[int] = None,
    file_mode: str = "a",
    attach_granian: bool = True,
    force: bool = False,
) -> logging.Logger:
    """
    Configure Nestipy logger with console (colored) and optional file handlers.
    """
    handlers: list[logging.Handler] = []
    if use_color:
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_level=False,
            show_path=False,
        )
        console_handler.setFormatter(_NestipyRichFormatter(fmt=fmt, datefmt=datefmt))
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    handlers.append(console_handler)

    if file:
        file_handler = logging.FileHandler(file, mode=file_mode)
        file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        if file_level is not None:
            file_handler.setLevel(file_level)
        handlers.append(file_handler)

    _apply_handlers(logger, handlers, level, force)
    if attach_granian:
        granian_logger = logging.getLogger("granian")
        _apply_handlers(granian_logger, handlers, level, force)
    return logger


def build_granian_log_dictconfig(
    level: int = logging.INFO,
    fmt: str = DEFAULT_LOG_FORMAT,
    datefmt: Optional[str] = None,
    use_color: bool = True,
) -> dict:
    """
    Build a logging.dictConfig for Granian so its logs follow Nestipy format.
    """
    if use_color:
        formatter = {
            "()": "nestipy.common.logger._NestipyRichFormatter",
            "fmt": fmt,
            "datefmt": datefmt,
        }
        handler = {
            "()": "rich.logging.RichHandler",
            "level": level,
            "formatter": "nestipy",
            "rich_tracebacks": True,
            "markup": True,
            "show_time": False,
            "show_level": False,
            "show_path": False,
        }
    else:
        formatter = {"format": fmt, "datefmt": datefmt}
        handler = {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "nestipy",
        }
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "nestipy": formatter,
        },
        "handlers": {
            "console": handler,
        },
        "loggers": {
            "granian": {"handlers": ["console"], "level": level, "propagate": False},
            "granian.access": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
        },
        "root": {"handlers": ["console"], "level": level},
    }
