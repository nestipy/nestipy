from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class OpenApiErrorDetail:
    pipe: Optional[str] = None
    error: Optional[Any] = None


@dataclass
class OpenApiErrorResponse:
    status_code: int
    message: str
    details: Optional[OpenApiErrorDetail] = None
