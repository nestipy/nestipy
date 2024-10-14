from __future__ import annotations

import functools
import typing
from typing import Any, ParamSpec

import anyio.to_thread
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

__all__ = ("UploadFile",)

P = ParamSpec("P")
T = typing.TypeVar("T")


async def run_in_thread_pool(
    func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    if kwargs:  # pragma: no cover
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)


class UploadFile(bytes):
    def __new__(
        cls,
        file: typing.BinaryIO,
        *,
        size: int | None = None,
        filename: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        obj = super().__new__(cls, file or b"")
        obj.filename = filename
        obj.size = size
        obj.headers = headers or {}
        obj.file = file
        return obj

    @property
    def content_type(self) -> str | None:
        return self.headers.get("content-type", None)

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

    @property
    def _in_memory(self) -> bool:
        # check for SpooledTemporaryFile._rolled
        rolled_to_disk = getattr(self.file, "_rolled", True)
        return not rolled_to_disk

    async def write(self, data: bytes) -> None:
        if self.size is not None:
            self.size += len(data)
        if self._in_memory:
            self.file.write(data)
        else:
            await run_in_thread_pool(self.file.write, data)

    async def read(self, size: int = -1) -> bytes:
        if self._in_memory:
            return self.file.read(size)
        return await run_in_thread_pool(self.file.read, size)

    async def seek(self, offset: int) -> None:
        if self._in_memory:
            self.file.seek(offset)
        else:
            await run_in_thread_pool(self.file.seek, offset)

    async def close(self) -> None:
        if self._in_memory:
            self.file.close()
        else:
            await run_in_thread_pool(self.file.close)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"filename={self.filename!r}, "
            f"size={self.size!r}, "
            f"headers={self.headers!r})"
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, _handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "binary"}

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        return core_schema.bytes_schema()
