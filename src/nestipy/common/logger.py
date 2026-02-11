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
    _STATUS_STYLES = {
        "2xx": "green",
        "3xx": "cyan",
        "4xx": "yellow",
        "5xx": "red",
    }

    @classmethod
    def _style_status(cls, status: int) -> str:
        if 200 <= status < 300:
            return cls._STATUS_STYLES["2xx"]
        if 300 <= status < 400:
            return cls._STATUS_STYLES["3xx"]
        if 400 <= status < 500:
            return cls._STATUS_STYLES["4xx"]
        if 500 <= status < 600:
            return cls._STATUS_STYLES["5xx"]
        return "white"

    @classmethod
    def _colorize_status(cls, message: str, status: int) -> str:
        try:
            import re

            style = cls._style_status(status)
            pattern = re.compile(rf"(?<!\d){status}(?!\d)")
            return pattern.sub(f"[{style}]{status}[/{style}]", message, count=1)
        except Exception:
            return message

    @staticmethod
    def _extract_status_from_message(message: str) -> Optional[int]:
        try:
            import re

            primary = re.search(r"\"[^\"]*\"\s+(\d{3})\b", message)
            if primary:
                value = int(primary.group(1))
                if 100 <= value <= 599:
                    return value
            candidates = [
                int(m.group(1))
                for m in re.finditer(r"(?<!\d)(\d{3})(?!\d)", message)
                if 100 <= int(m.group(1)) <= 599
            ]
            if candidates:
                return candidates[-1]
        except Exception:
            return None
        return None

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        record.levelname = f"[green]{original_levelname}[/green]"
        try:
            rendered = super().format(record)
            status = getattr(record, "status", None)
            if status is None:
                status = getattr(record, "status_code", None)
            if isinstance(status, int):
                rendered = self._colorize_status(rendered, status)
            else:
                extracted = self._extract_status_from_message(rendered)
                if extracted is not None:
                    rendered = self._colorize_status(rendered, extracted)
            return f"[green]{rendered}[/green]"
        finally:
            record.levelname = original_levelname


class _NestipyRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        from rich.highlighter import NullHighlighter

        if "highlighter" not in kwargs or kwargs["highlighter"] is None:
            kwargs["highlighter"] = NullHighlighter()
        super().__init__(*args, **kwargs)


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
            highlighter=None,
            show_time=False,
            show_level=False,
            show_path=False,
        )
        # Ensure no Rich default highlighter overrides our status coloring.
        console_handler.highlighter = None
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
    formatter = {
        "()": _NestipyRichFormatter,
        "fmt": fmt,
        "datefmt": datefmt,
    }
    if not use_color:
        formatter = {
            "()": logging.Formatter,
            "fmt": fmt,
            "datefmt": datefmt,
        }
    if use_color:
        handler = {
            "()": _NestipyRichHandler,
            "level": level,
            "formatter": "nestipy",
            "rich_tracebacks": True,
            "markup": True,
            "show_time": False,
            "show_level": False,
            "show_path": False,
        }
    else:
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
