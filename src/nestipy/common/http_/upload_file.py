from __future__ import annotations

from tempfile import SpooledTemporaryFile
from typing import Any

from pydantic_core import core_schema

__all__ = ("UploadFile",)


class UploadFile:

    def __init__(
            self,
            content_type: str,
            filename: str,
            file_data: bytes | None = None,
            headers: dict[str, str] | None = None,
            max_spool_size: int = 1024 * 1024,
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self.file = SpooledTemporaryFile(max_size=max_spool_size)
        self.headers = headers or {}

        if file_data:
            self.file.write(file_data)
            self.file.seek(0)

    @property
    def rolled_to_disk(self) -> bool:
        return False

    async def write(self, data: bytes) -> int:
        return self.file.write(data)

    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)

    async def seek(self, offset: int) -> int:
        return self.file.seek(offset)

    async def close(self) -> None:
        return self.file.close()

    def __repr__(self) -> str:
        return f"{self.filename} - {self.content_type}"

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Any,
    ) -> core_schema.CoreSchema:
        return core_schema.bytes_schema()
