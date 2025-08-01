from __future__ import annotations

import json
import typing
from dataclasses import dataclass, field
from enum import Enum
from tempfile import SpooledTemporaryFile
from typing import Union
from urllib.parse import unquote_plus

from .upload_file import UploadFile

try:
    import multipart
    from multipart.multipart import parse_options_header
except ModuleNotFoundError:  # pragma: nocover
    parse_options_header = None
    multipart = None

FormData = dict[str, Union[str | UploadFile]]


class FormMessage(Enum):
    FIELD_START = 1
    FIELD_NAME = 2
    FIELD_DATA = 3
    FIELD_END = 4
    END = 5


@dataclass
class MultipartPart:
    content_disposition: bytes | None = None
    field_name: str = ""
    data: bytes = b""
    file: UploadFile | None = None
    item_headers: list[tuple[bytes, bytes]] = field(default_factory=list)


def _to_form_data(items: list[tuple[str, str | UploadFile]]):
    form_data = {}
    for key, value in items:
        if isinstance(value, str):
            try:
                form_data[key] = json.loads(value)
            except json.JSONDecodeError:
                form_data[key] = value
        else:
            form_data[key] = value

    return form_data


def _user_safe_decode(src: bytes, codec: str) -> str:
    try:
        return src.decode(codec)
    except (UnicodeDecodeError, LookupError):
        return src.decode("latin-1")


class MultiPartException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class FormParser:
    def __init__(
        self, headers: dict[str, typing.Any], stream: typing.AsyncGenerator[bytes, None]
    ) -> None:
        assert multipart is not None, (
            "The `python-multipart` library must be installed to use form parsing."
        )
        self.headers = headers
        self.stream = stream
        self.messages: list[tuple[FormMessage, bytes]] = []

    def on_field_start(self) -> None:
        message = (FormMessage.FIELD_START, b"")
        self.messages.append(message)

    def on_field_name(self, data: bytes, start: int, end: int) -> None:
        message = (FormMessage.FIELD_NAME, data[start:end])
        self.messages.append(message)

    def on_field_data(self, data: bytes, start: int, end: int) -> None:
        message = (FormMessage.FIELD_DATA, data[start:end])
        self.messages.append(message)

    def on_field_end(self) -> None:
        message = (FormMessage.FIELD_END, b"")
        self.messages.append(message)

    def on_end(self) -> None:
        message = (FormMessage.END, b"")
        self.messages.append(message)

    async def parse(self) -> FormData:
        # Callbacks dictionary.
        callbacks = {
            "on_field_start": self.on_field_start,
            "on_field_name": self.on_field_name,
            "on_field_data": self.on_field_data,
            "on_field_end": self.on_field_end,
            "on_end": self.on_end,
        }

        # Create the parser.
        parser = multipart.QuerystringParser(callbacks)
        field_name = b""
        field_value = b""

        items: list[tuple[str, str | UploadFile]] = []

        # Feed the parser with data from the request.
        async for chunk in self.stream:
            if chunk:
                parser.write(chunk)
            else:
                parser.finalize()
            messages = list(self.messages)
            self.messages.clear()
            for message_type, message_bytes in messages:
                if message_type == FormMessage.FIELD_START:
                    field_name = b""
                    field_value = b""
                elif message_type == FormMessage.FIELD_NAME:
                    field_name += message_bytes
                elif message_type == FormMessage.FIELD_DATA:
                    field_value += message_bytes
                elif message_type == FormMessage.FIELD_END:
                    name = unquote_plus(field_name.decode("latin-1"))
                    value = unquote_plus(field_value.decode("latin-1"))
                    items.append((name, value))

        return _to_form_data(items)


class MultiPartParser:
    max_file_size = 1024 * 1024

    def __init__(
        self,
        headers: dict[str, typing.Any],
        stream: typing.AsyncGenerator[bytes, None],
        *,
        max_files: int | float = 1000,
        max_fields: int | float = 1000,
    ) -> None:
        assert multipart is not None, (
            "The `python-multipart` library must be installed to use form parsing."
        )
        self.headers = headers
        self.stream = stream
        self.max_files = max_files
        self.max_fields = max_fields
        self.items: list[tuple[str, str | UploadFile]] = []
        self._current_files = 0
        self._current_fields = 0
        self._current_partial_header_name: bytes = b""
        self._current_partial_header_value: bytes = b""
        self._current_part = MultipartPart()
        self._charset = ""
        self._file_parts_to_write: list[tuple[MultipartPart, bytes]] = []
        self._file_parts_to_finish: list[MultipartPart] = []
        self._files_to_close_on_error: list[SpooledTemporaryFile[bytes]] = []

    def on_part_begin(self) -> None:
        self._current_part = MultipartPart()

    def on_part_data(self, data: bytes, start: int, end: int) -> None:
        message_bytes = data[start:end]
        if self._current_part.file is None:
            self._current_part.data += message_bytes
        else:
            self._file_parts_to_write.append((self._current_part, message_bytes))

    def on_part_end(self) -> None:
        if self._current_part.file is None:
            self.items.append(
                (
                    self._current_part.field_name,
                    _user_safe_decode(self._current_part.data, self._charset),
                )
            )
        else:
            self._file_parts_to_finish.append(self._current_part)
            # The file can be added to the items right now even though it's not
            # finished yet, because it will be finished in the `parse()` method, before
            # self.items is used in the return value.
            self.items.append((self._current_part.field_name, self._current_part.file))

    def on_header_field(self, data: bytes, start: int, end: int) -> None:
        self._current_partial_header_name += data[start:end]

    def on_header_value(self, data: bytes, start: int, end: int) -> None:
        self._current_partial_header_value += data[start:end]

    def on_header_end(self) -> None:
        _field = self._current_partial_header_name.lower()
        if _field == b"content-disposition":
            self._current_part.content_disposition = self._current_partial_header_value
        self._current_part.item_headers.append(
            (_field, self._current_partial_header_value)
        )
        self._current_partial_header_name = b""
        self._current_partial_header_value = b""

    def on_headers_finished(self) -> None:
        disposition, options = parse_options_header(
            self._current_part.content_disposition
        )
        try:
            self._current_part.field_name = _user_safe_decode(
                options[b"name"], self._charset
            )
        except KeyError:
            raise MultiPartException(
                'The Content-Disposition header field "name" must be provided.'
            )
        if b"filename" in options:
            self._current_files += 1
            if self._current_files > self.max_files:
                raise MultiPartException(
                    f"Too many files. Maximum number of files is {self.max_files}."
                )
            filename = _user_safe_decode(options[b"filename"], self._charset)
            temp_file = SpooledTemporaryFile(max_size=self.max_file_size)
            self._files_to_close_on_error.append(temp_file)
            self._current_part.file = UploadFile(
                file=temp_file,  # type: ignore[arg-type]
                size=0,
                filename=filename,
                headers={
                    key.decode("utf-8"): value.decode("utf-8")
                    for key, value in self._current_part.item_headers
                },
            )
        else:
            self._current_fields += 1
            if self._current_fields > self.max_fields:
                raise MultiPartException(
                    f"Too many fields. Maximum number of fields is {self.max_fields}."
                )
            self._current_part.file = None

    def on_end(self) -> None:
        pass

    async def parse(self) -> FormData:
        # Parse the Content-Type header to get the multipart boundary.
        _, params = parse_options_header(self.headers.get("content-type"))
        charset = params.get(b"charset", "utf-8")
        if isinstance(charset, bytes):
            charset = charset.decode("latin-1")
        self._charset = charset
        try:
            boundary = params[b"boundary"]
        except KeyError:
            raise MultiPartException("Missing boundary in multipart.")

        # Callbacks dictionary.
        callbacks = {
            "on_part_begin": self.on_part_begin,
            "on_part_data": self.on_part_data,
            "on_part_end": self.on_part_end,
            "on_header_field": self.on_header_field,
            "on_header_value": self.on_header_value,
            "on_header_end": self.on_header_end,
            "on_headers_finished": self.on_headers_finished,
            "on_end": self.on_end,
        }

        # Create the parser.
        parser = multipart.MultipartParser(boundary, callbacks)
        try:
            # Feed the parser with data from the request.
            async for chunk in self.stream:
                parser.write(chunk)
                for part, data in self._file_parts_to_write:
                    # assert part.file  # for type checkers
                    await part.file.write(data)
                for part in self._file_parts_to_finish:
                    # assert part.file  # for type checkers
                    await part.file.seek(0)
                self._file_parts_to_write.clear()
                self._file_parts_to_finish.clear()
        except MultiPartException as exc:
            # Close all the files if there was an error.
            for file in self._files_to_close_on_error:
                file.close()
            raise exc
        parser.finalize()
        return _to_form_data(self.items)
