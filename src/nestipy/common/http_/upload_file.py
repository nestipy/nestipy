from __future__ import annotations

from tempfile import SpooledTemporaryFile
from typing import Any

from pydantic_core import core_schema

__all__ = ("UploadFile",)


class UploadFile(bytes):
    def __new__(
            cls,
            content_type: str,
            filename: str,
            file_data: bytes | None = None,
            headers: dict[str, str] | None = None,
            max_spool_size: int = 1024 * 1024,
    ) -> bytes:
        obj = super().__new__(cls, file_data or b'')
        obj.filename = filename
        obj.content_type = content_type
        obj.headers = headers or {}
        obj.file = SpooledTemporaryFile(max_size=max_spool_size)
        if file_data:
            obj.file.write(file_data)
            obj.file.seek(0)
        return obj

    def __repr__(self) -> str:
        return f"{self.filename} - {self.content_type}"

    def __len__(self) -> int:
        return len(self.file.read())

    def __getitem__(self, key) -> bytes:
        return self.file.read()[key]

    def __iter__(self) -> iter:
        return iter(self.file.read())

    def __bytes__(self) -> bytes:
        return self.file.read()

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, bytes)

    def __subclasscheck__(self, subclass) -> bool:
        return issubclass(subclass, bytes)

    def __class__(self):
        return bytes

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Any,
    ) -> core_schema.CoreSchema:
        return core_schema.bytes_schema()
