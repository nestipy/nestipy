import importlib.metadata
import os
import platform
from dataclasses import dataclass, field
from typing import List
from typing import Union


@dataclass
class FrameworkTrack:
    """
    Metadata about the environment when an exception occurred.
    """

    python: str
    nestipy: str


@dataclass
class RequestTrack:
    """
    Metadata about the request that triggered the exception.
    """

    method: str
    host: str


@dataclass
class Traceback:
    """
    Detailed information about a single frame in a traceback.
    """

    filename: str
    lineno: int
    name: str
    code: str
    start_line_number: int = field(default=1)
    is_package: bool = field(default=False)


@dataclass
class ExceptionDetail:
    """
    Comprehensive details about an exception, including request info and traceback.
    """

    exception: str
    type: str
    message: str
    root: str
    request: RequestTrack = field(
        default_factory=lambda: RequestTrack("GET", "0.0.0.0:8000")
    )
    traceback: List[Traceback] = field(default_factory=lambda: [])
    framework: FrameworkTrack = field(
        default_factory=lambda: FrameworkTrack(
            platform.python_version(), importlib.metadata.version("nestipy")
        )
    )


class HttpException(Exception):
    """
    Base exception class for all HTTP-related errors in Nestipy.
    Includes status code, message, and detailed traceback information.
    """

    def __init__(
        self,
        status_code: int,
        message: Union[str, None] = None,
        details: Union[dict, str, None] = None,
        track_back: Union[ExceptionDetail, None] = None,
    ):
        """
        Initialize HttpException.
        :param status_code: HTTP status code.
        :param message: Error message.
        :param details: Additional error details.
        :param track_back: Detailed traceback info.
        """
        self.status_code = status_code
        self.message = message
        self.details = details
        self.track_back = track_back or ExceptionDetail(
            "Internal server error",
            "HttpException",
            message,
            os.getcwd(),
        )
        super().__init__(self.message)

    def __str__(self):
        """
        Return a string representation of the exception.
        """
        return f"{self.status_code} - {self.message} {f' - {self.details}' if self.details is not None else ''}"
