from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .processor import ExceptionFilterHandler

__all__ = ["ExceptionFilterHandler"]


def __getattr__(name: str):
    if name == "ExceptionFilterHandler":
        from .processor import ExceptionFilterHandler

        return ExceptionFilterHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
