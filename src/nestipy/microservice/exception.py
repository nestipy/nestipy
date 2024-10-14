import dataclasses
from abc import abstractmethod, ABC
from typing import Any, TYPE_CHECKING

import dataclasses_json

from nestipy.common.exception.http import HttpException
from nestipy.common.exception.interface import ExceptionFilter

if TYPE_CHECKING:
    from nestipy.core.context.argument_host import ArgumentHost


class RPCErrorCode:
    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16


class RPCErrorMessage:
    OK = "The operation completed successfully."
    CANCELLED = "The operation was cancelled, typically by the caller."
    UNKNOWN = "An unknown error occurred."
    INVALID_ARGUMENT = "The client specified an invalid argument."
    DEADLINE_EXCEEDED = "The deadline expired before the operation could complete."
    NOT_FOUND = "Some requested entity (e.g., file or directory) was not found."
    ALREADY_EXISTS = "The entity that a client attempted to create already exists."
    PERMISSION_DENIED = (
        "The caller does not have permission to execute the specified operation."
    )
    RESOURCE_EXHAUSTED = (
        "Some resource has been exhausted, perhaps a per-user quota, or perhaps the entire file "
        "system is out of space."
    )
    FAILED_PRECONDITION = (
        "The operation was rejected because the system is not in a state required for the "
        "operation's execution."
    )
    ABORTED = (
        "The operation was aborted, typically due to a concurrency issue such as a sequencer check failure or "
        "transaction abort."
    )
    OUT_OF_RANGE = "The operation was attempted past the valid range."
    UNIMPLEMENTED = (
        "The operation is not implemented or is not supported/enabled in this service."
    )
    INTERNAL = "Internal errors. Means some invariants expected by the underlying system have been broken."
    UNAVAILABLE = "The service is currently unavailable."
    DATA_LOSS = "Unrecoverable data loss or corruption."
    UNAUTHENTICATED = (
        "The request does not have valid authentication credentials for the operation."
    )


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class RpcException(HttpException):
    status_code: int
    message: str

    def __post_init__(self):
        super().__init__(self.status_code, self.message)

    def to_json(self):
        return {"status_code": self.status_code, "message": self.message}

    @classmethod
    def from_json(cls, data: dict):
        return cls(data.get("status_code"), data.get("message"))


class RpcExceptionFilter(ExceptionFilter, ABC):
    @abstractmethod
    async def catch(self, exception: "RpcException", host: "ArgumentHost") -> Any:
        pass
